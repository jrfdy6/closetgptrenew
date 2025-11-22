#!/usr/bin/env python3
"""
Cleanup script to remove legacy subscription fields from all users.
Removes:
- subscription.tier (use subscription.role instead)
- subscription.openai_flatlays_used (use quotas.flatlaysRemaining instead)
- subscription.flatlay_week_start (use quotas.lastRefillAt instead)
"""

import os
import sys
from pathlib import Path

# Add backend to path
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(BACKEND_DIR / "src"))

from datetime import datetime, timezone
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import DELETE_FIELD

# Initialize Firebase
try:
    cred = credentials.Certificate(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
    firebase_admin.initialize_app(cred)
except:
    # Try default credentials
    try:
        firebase_admin.initialize_app()
    except Exception as e:
        print(f"❌ Firebase init error: {e}")
        sys.exit(1)

db = firestore.client()


def cleanup_user_legacy_fields(user_id: str, dry_run: bool = True) -> bool:
    """Remove legacy subscription fields from a user"""
    print(f"\n🔍 Cleaning up legacy fields for user: {user_id}")
    
    try:
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            print(f"❌ User {user_id} not found")
            return False
        
        user_data = user_doc.to_dict() or {}
        subscription = user_data.get('subscription', {})
        
        # Check which legacy fields exist
        legacy_fields = []
        if 'tier' in subscription:
            legacy_fields.append('tier')
        if 'openai_flatlays_used' in subscription:
            legacy_fields.append('openai_flatlays_used')
        if 'flatlay_week_start' in subscription:
            legacy_fields.append('flatlay_week_start')
        
        if not legacy_fields:
            print(f"✅ No legacy fields found for user {user_id}")
            return True
        
        print(f"📋 Found legacy fields: {', '.join(legacy_fields)}")
        
        if dry_run:
            print(f"🔍 DRY RUN: Would remove legacy fields: {', '.join(legacy_fields)}")
            return True
        else:
            # Remove legacy fields
            updates = {}
            for field in legacy_fields:
                updates[f'subscription.{field}'] = DELETE_FIELD
            
            user_ref.update(updates)
            print(f"✅ Removed legacy fields: {', '.join(legacy_fields)}")
            return True
            
    except Exception as e:
        print(f"❌ Error cleaning up user {user_id}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Cleanup legacy subscription fields')
    parser.add_argument('--user-id', type=str, help='Specific user ID to clean up')
    parser.add_argument('--all', action='store_true', help='Clean up all users')
    parser.add_argument('--dry-run', action='store_true', default=True, help='Dry run (default: True)')
    parser.add_argument('--execute', action='store_true', help='Actually execute cleanup (overrides --dry-run)')
    
    args = parser.parse_args()
    
    dry_run = not args.execute
    
    if args.user_id:
        # Clean up specific user
        cleanup_user_legacy_fields(args.user_id, dry_run=dry_run)
    elif args.all:
        # Find all users with legacy fields
        print("🔍 Finding all users with legacy subscription fields...")
        users_ref = db.collection('users')
        users = users_ref.stream()
        
        cleaned_count = 0
        skipped_count = 0
        error_count = 0
        
        for user_doc in users:
            user_data = user_doc.to_dict() or {}
            subscription = user_data.get('subscription', {})
            
            # Check if user has legacy fields
            has_legacy = (
                'tier' in subscription or
                'openai_flatlays_used' in subscription or
                'flatlay_week_start' in subscription
            )
            
            if has_legacy:
                if cleanup_user_legacy_fields(user_doc.id, dry_run=dry_run):
                    cleaned_count += 1
                else:
                    error_count += 1
            else:
                skipped_count += 1
        
        print(f"\n📊 Summary:")
        print(f"   Cleaned: {cleaned_count}")
        print(f"   Skipped (no legacy fields): {skipped_count}")
        print(f"   Errors: {error_count}")
    else:
        parser.print_help()
        print("\n💡 Example usage:")
        print("   # Dry run for specific user:")
        print("   python cleanup_legacy_subscription_fields.py --user-id dANqjiI0CKgaitxzYtw1bhtvQrG3")
        print("\n   # Actually clean up specific user:")
        print("   python cleanup_legacy_subscription_fields.py --user-id dANqjiI0CKgaitxzYtw1bhtvQrG3 --execute")
        print("\n   # Dry run for all users:")
        print("   python cleanup_legacy_subscription_fields.py --all")
        print("\n   # Clean up all users:")
        print("   python cleanup_legacy_subscription_fields.py --all --execute")


if __name__ == '__main__':
    main()

