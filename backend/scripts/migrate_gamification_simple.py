"""
Simple migration script to add gamification fields to existing users
Uses service account key directly
"""

import firebase_admin
from firebase_admin import credentials, firestore
import sys
from pathlib import Path

# Initialize Firebase with service account
cred = credentials.Certificate('service-account-key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

def migrate_users():
    """Add gamification fields to existing users"""
    print("🚀 Starting user migration...")
    
    users = db.collection('users').stream()
    updated_count = 0
    skipped_count = 0
    
    for user_doc in users:
        user_data = user_doc.to_dict()
        user_id = user_doc.id
        
        updates = {}
        
        if 'xp' not in user_data:
            updates['xp'] = 0
        if 'level' not in user_data:
            updates['level'] = 1
        if 'ai_fit_score' not in user_data:
            updates['ai_fit_score'] = 0.0
        if 'badges' not in user_data:
            updates['badges'] = []
        if 'current_challenges' not in user_data:
            updates['current_challenges'] = {}
        if 'spending_ranges' not in user_data:
            updates['spending_ranges'] = {
                "annual_total": "unknown",
                "shoes": "unknown",
                "jackets": "unknown",
                "pants": "unknown",
                "tops": "unknown",
                "dresses": "unknown",
                "activewear": "unknown",
                "accessories": "unknown"
            }
        
        if updates:
            user_doc.reference.update(updates)
            updated_count += 1
            print(f"✅ Updated user {user_id}")
        else:
            skipped_count += 1
    
    print(f"\n{'='*60}")
    print(f"✅ USER MIGRATION COMPLETE")
    print(f"{'='*60}")
    print(f"Users updated: {updated_count}")
    print(f"Users skipped: {skipped_count}")
    print(f"Total users: {updated_count + skipped_count}")
    
    return updated_count

def migrate_wardrobe():
    """Add cpw and target_wears to wardrobe items"""
    print("\n🚀 Starting wardrobe migration...")
    
    items = db.collection('wardrobe').stream()
    updated_count = 0
    
    for item_doc in items:
        item_data = item_doc.to_dict()
        
        updates = {}
        
        if 'cpw' not in item_data:
            updates['cpw'] = None
        if 'target_wears' not in item_data:
            updates['target_wears'] = 30
        
        if updates:
            item_doc.reference.update(updates)
            updated_count += 1
            
            if updated_count % 50 == 0:
                print(f"Processed {updated_count} items...")
    
    print(f"\n✅ WARDROBE MIGRATION COMPLETE")
    print(f"Items updated: {updated_count}")
    
    return updated_count

if __name__ == "__main__":
    print("="*60)
    print("🎮 GAMIFICATION MIGRATION SCRIPT")
    print("="*60)
    
    try:
        # Migrate users
        user_count = migrate_users()
        
        # Migrate wardrobe
        wardrobe_count = migrate_wardrobe()
        
        print("\n" + "="*60)
        print("✅ ALL MIGRATIONS COMPLETE!")
        print(f"Users initialized: {user_count}")
        print(f"Wardrobe items updated: {wardrobe_count}")
        print("="*60)
        print("\n🎉 Your gamification system is ready to use!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

