#!/usr/bin/env python3
"""
Script to add test analytics data for demonstration purposes.
This will create favorite scores for items so they show up in the dashboard.
"""

import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config.firebase import db

# Test user ID - replace with your actual user ID
USER_ID = "dANqjiI0CKgaitxzYtw1bhtvQrG3"

def add_test_analytics():
    """Add test analytics data to demonstrate the favorites feature."""
    print("🎯 Adding test analytics data...")
    
    # Get some items from the user's wardrobe
    wardrobe_ref = db.collection("wardrobe").where("userId", "==", USER_ID)
    wardrobe_docs = wardrobe_ref.limit(5).stream()
    
    items = []
    for doc in wardrobe_docs:
        item_data = doc.to_dict()
        items.append({
            "id": doc.id,
            "name": item_data.get("name", "Unknown Item"),
            "type": item_data.get("type", "unknown")
        })
    
    if not items:
        print("❌ No items found in wardrobe. Please add some items first.")
        return
    
    print(f"📦 Found {len(items)} items in wardrobe:")
    for item in items:
        print(f"  - {item['name']} ({item['type']})")
    
    # Add favorite scores directly to the database
    for i, item in enumerate(items):
        print(f"\n📊 Adding favorite score for {item['type']} (ID: {item['id']})")
        
        # Calculate different scores based on item index
        if i == 0:  # First item - most popular
            total_score = 0.85
            outfit_usage_score = 0.8
            feedback_score = 0.9
            interaction_score = 0.7
            style_preference_score = 0.8
            base_item_score = 0.6
            times_in_outfits = 15
            times_base_item = 3
            total_views = 25
            total_edits = 5
            total_selects = 12
            average_feedback_rating = 4.8
        elif i == 1:  # Second item - good but not great
            total_score = 0.72
            outfit_usage_score = 0.6
            feedback_score = 0.7
            interaction_score = 0.5
            style_preference_score = 0.6
            base_item_score = 0.3
            times_in_outfits = 8
            times_base_item = 1
            total_views = 15
            total_edits = 3
            total_selects = 7
            average_feedback_rating = 4.2
        elif i == 2:  # Third item - moderate usage
            total_score = 0.58
            outfit_usage_score = 0.4
            feedback_score = 0.5
            interaction_score = 0.4
            style_preference_score = 0.5
            base_item_score = 0.2
            times_in_outfits = 6
            times_base_item = 0
            total_views = 10
            total_edits = 2
            total_selects = 4
            average_feedback_rating = 3.5
        else:  # Other items - minimal usage
            total_score = 0.35
            outfit_usage_score = 0.2
            feedback_score = 0.3
            interaction_score = 0.2
            style_preference_score = 0.4
            base_item_score = 0.1
            times_in_outfits = 2
            times_base_item = 0
            total_views = 5
            total_edits = 1
            total_selects = 1
            average_feedback_rating = 3.0
        
        # Create favorite score document
        score_data = {
            "item_id": item['id'],
            "user_id": USER_ID,
            "total_score": total_score,
            "outfit_usage_score": outfit_usage_score,
            "feedback_score": feedback_score,
            "interaction_score": interaction_score,
            "style_preference_score": style_preference_score,
            "base_item_score": base_item_score,
            "times_in_outfits": times_in_outfits,
            "times_base_item": times_base_item,
            "total_views": total_views,
            "total_edits": total_edits,
            "total_selects": total_selects,
            "average_feedback_rating": average_feedback_rating,
            "last_updated": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Save to Firestore
        score_ref = db.collection("item_favorite_scores").document(f"{USER_ID}_{item['id']}")
        score_ref.set(score_data, merge=True)
        
        print(f"✅ Added favorite score for {item['type']}: {total_score:.2f}")
    
    print("\n🎉 Test analytics data added successfully!")
    print("Refresh your dashboard to see the new favorites.")
    print("\n📊 Expected results:")
    print("  - Item 1 should be your #1 favorite (85% score)")
    print("  - Item 2 should be your #2 favorite (72% score)")
    print("  - Item 3 should be your #3 favorite (58% score)")
    print("  - Other items should appear with lower scores")

if __name__ == "__main__":
    add_test_analytics() 