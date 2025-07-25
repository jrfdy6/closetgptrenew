#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔍 Starting debug_feedback.py script...")

from src.config.firebase import db
from datetime import datetime, timezone

print("✅ Firebase imported successfully")

user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"

print(f"🔍 Debugging Feedback for User: {user_id} (outfit_feedback collection)")
print("=" * 60)

try:
    print("📝 Attempting to connect to outfit_feedback collection...")
    feedback_docs = db.collection('outfit_feedback').where('user_id', '==', user_id).stream()
    
    print("✅ Query executed, processing results...")
    feedback_list = []
    for feedback in feedback_docs:
        print(f"   Found feedback document: {feedback.id}")
        feedback_data = feedback.to_dict()
        feedback_list.append({
            'id': feedback.id,
            'outfit_id': feedback_data.get('outfit_id'),
            'feedback_type': feedback_data.get('feedback_type'),
            'rating': feedback_data.get('rating'),
            'comment': feedback_data.get('comment'),
        })
    
    print(f"   Total feedback entries: {len(feedback_list)}")
    for feedback in feedback_list:
        print(f"   - Outfit ID: {feedback['outfit_id']}")
        print(f"     Feedback Type: {feedback['feedback_type']}")
        print(f"     Rating: {feedback['rating']}")
        print()
    
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
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("✅ Script completed!")
