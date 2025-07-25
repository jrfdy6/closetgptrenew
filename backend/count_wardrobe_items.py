#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config.firebase import db

def count_wardrobe_items():
    """Count wardrobe items for each user."""
    try:
        print("Counting wardrobe items per user...")
        
        # Get all wardrobe items
        wardrobe_items = db.collection('wardrobe').stream()
        
        user_counts = {}
        for item in wardrobe_items:
            item_data = item.to_dict()
            user_id = item_data.get('userId')
            if user_id:
                if user_id not in user_counts:
                    user_counts[user_id] = 0
                user_counts[user_id] += 1
        
        print(f"Wardrobe item counts by user:")
        for user_id, count in sorted(user_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  User {user_id}: {count} items")
        
        # Get user names for the top users
        if user_counts:
            print("\nTop users with wardrobe items:")
            for user_id, count in sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
                user_doc = db.collection('users').document(user_id).get()
                if user_doc.exists:
                    user_data = user_doc.to_dict()
                    user_name = user_data.get('name', 'Unknown')
                    user_email = user_data.get('email', 'No email')
                    print(f"  {user_name} ({user_email}) - ID: {user_id} - {count} items")
                else:
                    print(f"  Unknown user - ID: {user_id} - {count} items")
        
        return user_counts
        
    except Exception as e:
        print(f"Error counting wardrobe items: {e}")
        return {}

if __name__ == "__main__":
    count_wardrobe_items() 