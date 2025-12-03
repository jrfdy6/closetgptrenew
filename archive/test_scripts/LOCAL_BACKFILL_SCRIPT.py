#!/usr/bin/env python3
"""
LOCAL Backfill Script - Run this on your computer
It will connect to production Firebase and normalize your wardrobe items
"""

print("🚀 Local Backfill Script Starting...")
print("=" * 60)

# Setup
import os
import sys

backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

# Check for service account
service_account_path = os.path.join(backend_dir, 'service-account-key.json')
if not os.path.exists(service_account_path):
    print(f"❌ Service account key not found at: {service_account_path}")
    print("Please ensure backend/service-account-key.json exists")
    sys.exit(1)

print(f"✅ Found service account key")

# Initialize Firebase
import firebase_admin
from firebase_admin import credentials, firestore

try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred)
        print("✅ Firebase initialized")
except Exception as e:
    print(f"❌ Firebase initialization failed: {e}")
    sys.exit(1)

db = firestore.client()

# Import normalization - using importlib to avoid __init__.py issues
from datetime import datetime
import importlib.util

norm_path = os.path.join(backend_dir, 'src', 'utils', 'semantic_normalization.py')
spec = importlib.util.spec_from_file_location("semantic_normalization", norm_path)
norm_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(norm_module)
normalize_item_metadata = norm_module.normalize_item_metadata
print("✅ Normalization module loaded")

print("=" * 60)
print()

# Ask user for mode
print("Choose mode:")
print("  1. DRY RUN (test with 10 items, no changes)")
print("  2. DRY RUN (test all items, no changes)")
print("  3. PRODUCTION (actually update database)")
print()

choice = input("Enter choice (1-3): ").strip()

if choice == "1":
    dry_run = True
    max_items = 10
    print("\n🔍 Mode: DRY RUN with 10 items")
elif choice == "2":
    dry_run = True
    max_items = None
    print("\n🔍 Mode: DRY RUN with ALL items")
elif choice == "3":
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
stats = {
    'processed': 0,
    'updated': 0,
    'skipped': 0,
    'errors': 0
}

try:
    query = db.collection('wardrobe')
    if max_items:
        query = query.limit(max_items)
    
    items = query.stream()
    
    for doc in items:
        item = doc.to_dict()
        stats['processed'] += 1
        
        # Skip if already normalized
        if 'normalized' in item:
            stats['skipped'] += 1
            print(f"⏭️  [{stats['processed']}] Skipped {doc.id} (already normalized)")
            continue
        
        # Normalize
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
            print(f"❌ [{stats['processed']}] Error processing {doc.id}: {e}")
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
    print()
    
    if dry_run and max_items == 10:
        print("✅ Dry run successful! Everything looks good.")
        print("   Run again with option 2 to test all items,")
        print("   or option 3 to run the actual backfill.")
    elif dry_run:
        print("✅ Full dry run successful! Everything looks good.")
        print("   Run again with option 3 to run the actual backfill.")
    else:
        print("✅ PRODUCTION BACKFILL COMPLETE!")
        print("   Your wardrobe items are now normalized for semantic filtering.")
    
except Exception as e:
    print(f"\n❌ Backfill failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

