#!/usr/bin/env python3
"""
Backfill script using Railway environment variables
This avoids the local service account JWT issues
"""
import os
import sys

print("🚀 Railway Environment Backfill Script")
print("=" * 60)

# Set Railway environment variables manually
print("\n📋 You need to set these environment variables from Railway:")
print("   1. Go to Railway → Your Backend Service → Variables")
print("   2. Copy the Firebase credentials")
print("   3. Set them in your terminal:")
print()
print("export FIREBASE_PROJECT_ID='your-project-id'")
print("export FIREBASE_PRIVATE_KEY='your-private-key'")
print("export FIREBASE_CLIENT_EMAIL='your-client-email'")
print("export FIREBASE_CLIENT_ID='your-client-id'")
print("export FIREBASE_CLIENT_X509_CERT_URL='your-cert-url'")
print()

# Check if environment variables are set
required_vars = [
    "FIREBASE_PROJECT_ID",
    "FIREBASE_PRIVATE_KEY",
    "FIREBASE_CLIENT_EMAIL",
    "FIREBASE_CLIENT_ID",
    "FIREBASE_CLIENT_X509_CERT_URL"
]

missing_vars = [var for var in required_vars if not os.environ.get(var)]

if missing_vars:
    print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
    print("\nPlease set them and run this script again.")
    sys.exit(1)

print("✅ All environment variables found")
print("=" * 60)
print()

# Now initialize Firebase using environment variables
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

try:
    if not firebase_admin._apps:
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
            "private_key": os.environ.get("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n"),
            "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.environ.get("FIREBASE_CLIENT_ID"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.environ.get("FIREBASE_CLIENT_X509_CERT_URL"),
        })
        firebase_admin.initialize_app(cred)
        print("✅ Firebase initialized with Railway credentials")
except Exception as e:
    print(f"❌ Firebase initialization failed: {e}")
    sys.exit(1)

db = firestore.client()

# Import normalization
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
import importlib.util
norm_path = os.path.join(backend_dir, 'src', 'utils', 'semantic_normalization.py')
spec = importlib.util.spec_from_file_location("semantic_normalization", norm_path)
norm_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(norm_module)
normalize_item_metadata = norm_module.normalize_item_metadata
print("✅ Normalization module loaded")

print("=" * 60)
print()

# Ask for mode
print("Choose mode:")
print("  1. DRY RUN (test with 10 items)")
print("  2. PRODUCTION (update all items)")
print()

choice = input("Enter choice (1-2): ").strip()

if choice == "1":
    dry_run = True
    max_items = 10
    print("\n🔍 Mode: DRY RUN with 10 items")
elif choice == "2":
    dry_run = False
    max_items = None
    confirm = input("\n⚠️  WARNING: This will modify production database. Type 'YES' to continue: ")
    if confirm != 'YES':
        print("❌ Cancelled")
        sys.exit(0)
    print("\n🚀 Mode: PRODUCTION - will update database")
else:
    print("❌ Invalid choice")
    sys.exit(1)

print("=" * 60)
print()

# Run backfill
stats = {'processed': 0, 'updated': 0, 'skipped': 0, 'errors': 0}

try:
    query = db.collection('wardrobe')
    if max_items:
        query = query.limit(max_items)
    
    items = query.stream()
    
    for doc in items:
        item = doc.to_dict()
        stats['processed'] += 1
        
        if 'normalized' in item:
            stats['skipped'] += 1
            print(f"⏭️  [{stats['processed']}] Skipped {doc.id}")
            continue
        
        try:
            normalized = normalize_item_metadata(item)
            normalized_fields = {
                'style': normalized.get('style', []),
                'occasion': normalized.get('occasion', []),
                'mood': normalized.get('mood', []),
                'season': normalized.get('season', []),
                'normalized_at': datetime.utcnow().isoformat(),
                'normalized_version': '1.0'
            }
            
            if dry_run:
                print(f"🔍 [{stats['processed']}] DRY RUN: Would update {doc.id}")
                stats['updated'] += 1
            else:
                db.collection('wardrobe').document(doc.id).update({
                    'normalized': normalized_fields
                })
                print(f"✅ [{stats['processed']}] Updated {doc.id}")
                stats['updated'] += 1
                
        except Exception as e:
            print(f"❌ [{stats['processed']}] Error: {e}")
            stats['errors'] += 1
    
    print()
    print("=" * 60)
    print("📊 RESULTS:")
    print(f"   Processed: {stats['processed']}")
    print(f"   Updated: {stats['updated']}")
    print(f"   Skipped: {stats['skipped']}")
    print(f"   Errors: {stats['errors']}")
    
    if stats['processed'] > 0:
        success_rate = (stats['updated'] / stats['processed']) * 100
        print(f"   Success Rate: {success_rate:.1f}%")
    
    print("=" * 60)
    print("\n✅ Done!")
    
except Exception as e:
    print(f"\n❌ Backfill failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

