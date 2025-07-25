#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔍 Starting debug_feedback.py script...")

from src.config.firebase import db
from datetime import datetime, timezone

print("✅ Firebase imported successfully")

def debug_feedback():
    """Debug feedback and ratings data from outfit_feedback collection."""
    
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    print(f"🔍 Debugging Feedback for User: {user_id} (outfit_feedback collection)")
    print("=" * 60)
    
    try:
        print("📝 Attempting to connect to outfit_feedback collection...")
        # Check outfit_feedback collection
        print("📝 Checking outfit_feedback Collection:")
        feedback_docs = db.collection('outfit_feedback').where('user_id', '==', user_id).stream()
        
        print("✅ Query executed, processing results...")
        feedback_list = []
        for feedback in feedback_docs:
            print(f"   Found feedback document: {feedback.id}")
            feedback_data = feedback.to_dict()
            created_at = feedback_data.get('created_at') or feedback_data.get('createdAt')
            if created_at:
                try:
                    if created_at < 10000000000:
                        date_obj = datetime.fromtimestamp(created_at, tz=timezone.utc)
                    else:
                        date_obj = datetime.fromtimestamp(created_at / 1000, tz=timezone.utc)
                except:
                    date_obj = None
            else:
                date_obj = None
            feedback_list.append({
                'id': feedback.id,
                'outfit_id': feedback_data.get('outfit_id'),
                'feedback_type': feedback_data.get('feedback_type'),
                'rating': feedback_data.get('rating'),
                'comment': feedback_data.get('comment'),
                'created_at': created_at,
                'created_at_parsed': date_obj,
                'raw_data': feedback_data
            })
        
        print(f"   Total feedback entries: {len(feedback_list)}")
        for feedback in sorted(feedback_list, key=lambda x: x['created_at'] or 0, reverse=True)[:10]:
            print(f"   - Outfit ID: {feedback['outfit_id']}")
            print(f"     Feedback Type: {feedback['feedback_type']}")
            print(f"     Rating: {feedback['rating']}")
            print(f"     Comment: {feedback['comment']}")
            print(f"     Created: {feedback['created_at_parsed']}")
            print()
        
        # Check if there are any feedback entries without user_id
        print("🔍 Checking for feedback entries without user_id...")
        all_feedback = db.collection('outfit_feedback').stream()
        feedback_without_user = [f for f in all_feedback if not f.to_dict().get('user_id')]
        print(f"   Feedback entries without user_id: {len(feedback_without_user)}")
        
        # Check if there are ANY feedback entries at all
        print("\n🔍 Checking if outfit_feedback collection has ANY entries:")
        all_feedback_docs = list(db.collection('outfit_feedback').stream())
        print(f"   Total documents in outfit_feedback collection: {len(all_feedback_docs)}")
        
        if all_feedback_docs:
            print("   Sample entries:")
            for i, doc in enumerate(all_feedback_docs[:3]):
                data = doc.to_dict()
                print(f"     {i+1}. User ID: {data.get('user_id', 'None')}")
                print(f"        Outfit ID: {data.get('outfit_id', 'None')}")
                print(f"        Feedback Type: {data.get('feedback_type', 'None')}")
                print(f"        Rating: {data.get('rating', 'None')}")
                print()
        else:
            print("   No documents found in outfit_feedback collection!")
        
        # TEST: Try reading from the outfits collection
        print("\n🧪 TEST: Reading from 'outfits' collection...")
        try:
            outfits_docs = list(db.collection('outfits').stream())
            print(f"   Total documents in outfits collection: {len(outfits_docs)}")
            for i, doc in enumerate(outfits_docs[:3]):
                data = doc.to_dict()
                print(f"     {i+1}. Outfit ID: {doc.id}, User ID: {data.get('user_id', 'None')}")
        except Exception as e:
            print(f"❌ Error reading from outfits collection: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Calling debug_feedback() function...")
    debug_feedback()
    print("✅ Script completed!") 