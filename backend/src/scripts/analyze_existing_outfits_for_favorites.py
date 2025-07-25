#!/usr/bin/env python3
"""
Script to analyze existing outfit data and calculate initial favorite scores for users.
This uses the existing outfits collection to determine which items are most used and liked.
"""

import sys
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import math

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config.firebase import db
from services.analytics_service import (
    update_item_favorite_score_async,
    get_user_favorites,
    FAVORITE_SCORES_COLLECTION
)
from models.analytics_event import ItemInteractionType
from types.wardrobe import ClothingItem
from types.profile import UserProfile

def analyze_existing_outfits_for_user(user_id: str) -> Dict[str, Any]:
    """
    Analyze existing outfits for a user and calculate favorite scores.
    
    Returns:
        Dict with analysis results and favorite items
    """
    print(f"🔍 Analyzing outfits for user: {user_id}")
    
    # Get all outfits for this user
    outfits_ref = db.collection('outfits')
    outfits_query = outfits_ref.where('user_id', '==', user_id).stream()
    
    outfits = []
    for doc in outfits_query:
        outfit_data = doc.to_dict()
        outfit_data['outfit_id'] = doc.id
        outfits.append(outfit_data)
    
    print(f"📊 Found {len(outfits)} outfits for user {user_id}")
    
    if not outfits:
        return {
            "user_id": user_id,
            "total_outfits": 0,
            "favorite_items": {},
            "analysis_summary": "No outfits found"
        }
    
    # Analyze outfit data
    item_usage = {}  # item_id -> usage count
    item_feedback = {}  # item_id -> list of ratings
    base_item_usage = {}  # item_id -> base item usage count
    successful_outfits = 0
    total_outfits = len(outfits)
    
    for outfit in outfits:
        # Check if outfit was successful
        was_successful = outfit.get('wasSuccessful', True)
        if was_successful:
            successful_outfits += 1
        
        # Get items from outfit
        items = outfit.get('items', [])
        if not items:
            continue
        
        # Track item usage
        for item in items:
            if isinstance(item, dict):
                item_id = item.get('id')
            else:
                item_id = str(item)
            
            if item_id:
                item_usage[item_id] = item_usage.get(item_id, 0) + 1
                
                # Check if this was a base item
                base_item_id = outfit.get('baseItemId')
                if base_item_id == item_id:
                    base_item_usage[item_id] = base_item_usage.get(item_id, 0) + 1
        
        # Track feedback
        user_feedback = outfit.get('userFeedback')
        if user_feedback:
            rating = user_feedback.get('rating', 0)
            if rating > 0:
                for item in items:
                    if isinstance(item, dict):
                        item_id = item.get('id')
                    else:
                        item_id = str(item)
                    
                    if item_id:
                        if item_id not in item_feedback:
                            item_feedback[item_id] = []
                        item_feedback[item_id].append(rating)
    
    # Calculate favorite scores for each item
    favorite_items = {}
    
    for item_id, usage_count in item_usage.items():
        # Get item details from wardrobe
        item_ref = db.collection('wardrobe').document(item_id)
        item_doc = item_ref.get()
        
        if not item_doc.exists:
            print(f"⚠️ Item {item_id} not found in wardrobe, skipping")
            continue
        
        item_data = item_doc.to_dict()
        
        # Calculate component scores
        outfit_usage_score = min(math.log(1 + usage_count) / math.log(51), 1.0)
        
        # Feedback score
        feedback_score = 0.0
        if item_id in item_feedback:
            ratings = item_feedback[item_id]
            if ratings:
                avg_rating = sum(ratings) / len(ratings)
                feedback_score = (avg_rating - 1) / 4  # Convert 1-5 to 0-1
        
        # Base item score
        base_item_score = 0.0
        if item_id in base_item_usage:
            base_count = base_item_usage[item_id]
            base_item_score = min(base_count / 10.0, 1.0)
        
        # Style preference score (default to neutral)
        style_preference_score = 0.5
        
        # Interaction score (default to low since we don't have interaction data)
        interaction_score = 0.1 if usage_count > 0 else 0.0
        
        # Calculate total score
        total_score = (
            outfit_usage_score * 0.4 +  # Higher weight for usage since that's what we have
            feedback_score * 0.3 +
            interaction_score * 0.15 +
            style_preference_score * 0.1 +
            base_item_score * 0.05
        )
        
        # Create favorite score data
        score_data = {
            "item_id": item_id,
            "user_id": user_id,
            "total_score": total_score,
            "outfit_usage_score": outfit_usage_score,
            "feedback_score": feedback_score,
            "interaction_score": interaction_score,
            "style_preference_score": style_preference_score,
            "base_item_score": base_item_score,
            "last_updated": datetime.utcnow().isoformat(),
            "times_in_outfits": usage_count,
            "times_base_item": base_item_usage.get(item_id, 0),
            "total_views": 0,  # No view data from outfits
            "total_edits": 0,  # No edit data from outfits
            "total_selects": 0,  # No select data from outfits
            "average_feedback_rating": sum(item_feedback.get(item_id, [0])) / len(item_feedback.get(item_id, [1])) if item_id in item_feedback else 0.0
        }
        
        # Save to Firestore
        score_ref = db.collection(FAVORITE_SCORES_COLLECTION).document(f"{user_id}_{item_id}")
        score_ref.set(score_data, merge=True)
        
        # Add to favorite items dict
        favorite_items[item_id] = {
            "item_name": item_data.get('name', 'Unknown'),
            "item_type": item_data.get('type', 'unknown'),
            "image_url": item_data.get('imageUrl', ''),
            "favorite_score": total_score,
            "outfit_appearances": usage_count,
            "base_item_uses": base_item_usage.get(item_id, 0),
            "average_rating": score_data["average_feedback_rating"]
        }
        
        print(f"✅ Calculated score for {item_data.get('name', 'Unknown')}: {total_score:.3f}")
    
    # Get top favorites by type
    top_favorites = {}
    for item_type in ['shirt', 'pants', 'shoes']:
        type_favorites = [
            (item_id, data) for item_id, data in favorite_items.items()
            if data['item_type'] == item_type
        ]
        if type_favorites:
            # Sort by favorite score
            type_favorites.sort(key=lambda x: x[1]['favorite_score'], reverse=True)
            top_favorites[item_type] = type_favorites[0][1]  # Get the top one
    
    return {
        "user_id": user_id,
        "total_outfits": total_outfits,
        "successful_outfits": successful_outfits,
        "total_items_analyzed": len(favorite_items),
        "favorite_items": favorite_items,
        "top_favorites": top_favorites,
        "analysis_summary": f"Analyzed {total_outfits} outfits, found {len(favorite_items)} unique items"
    }

def analyze_all_users():
    """Analyze outfits for all users in the system."""
    print("🚀 Starting analysis of existing outfits for all users...")
    
    # Get all users
    users_ref = db.collection('users')
    users = list(users_ref.stream())
    
    print(f"👥 Found {len(users)} users to analyze")
    
    results = {}
    for i, user_doc in enumerate(users, 1):
        user_id = user_doc.id
        print(f"\n📊 Processing user {i}/{len(users)}: {user_id}")
        
        try:
            result = analyze_existing_outfits_for_user(user_id)
            results[user_id] = result
            print(f"✅ Completed analysis for user {user_id}")
        except Exception as e:
            print(f"❌ Error analyzing user {user_id}: {e}")
            results[user_id] = {
                "user_id": user_id,
                "error": str(e)
            }
    
    # Print summary
    print("\n" + "="*50)
    print("📈 ANALYSIS SUMMARY")
    print("="*50)
    
    total_users = len(results)
    successful_users = sum(1 for r in results.values() if 'error' not in r)
    total_outfits = sum(r.get('total_outfits', 0) for r in results.values() if 'error' not in r)
    total_items = sum(r.get('total_items_analyzed', 0) for r in results.values() if 'error' not in r)
    
    print(f"Total users processed: {total_users}")
    print(f"Successful analyses: {successful_users}")
    print(f"Total outfits analyzed: {total_outfits}")
    print(f"Total items scored: {total_items}")
    
    # Show top favorites for each user
    print("\n🏆 TOP FAVORITES BY USER:")
    for user_id, result in results.items():
        if 'error' not in result and result.get('top_favorites'):
            print(f"\n👤 {user_id}:")
            for item_type, favorite in result['top_favorites'].items():
                print(f"  {item_type.capitalize()}: {favorite['item_name']} (Score: {favorite['favorite_score']:.3f})")
    
    return results

def test_favorite_retrieval(user_id: str):
    """Test the favorite retrieval functions for a user."""
    print(f"\n🧪 Testing favorite retrieval for user: {user_id}")
    
    # Test getting favorites by type
    for item_type in ['shirt', 'pants', 'shoes']:
        try:
            favorites = get_user_favorites(user_id, item_type, limit=3)
            print(f"📋 Top {item_type} favorites:")
            for i, favorite in enumerate(favorites, 1):
                print(f"  {i}. {favorite['item_name']} (Score: {favorite['favorite_score']:.3f})")
        except Exception as e:
            print(f"❌ Error getting {item_type} favorites: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze existing outfits for favorite items')
    parser.add_argument('--user-id', help='Analyze specific user ID')
    parser.add_argument('--all-users', action='store_true', help='Analyze all users')
    parser.add_argument('--test', help='Test favorite retrieval for specific user ID')
    
    args = parser.parse_args()
    
    if args.test:
        test_favorite_retrieval(args.test)
    elif args.user_id:
        result = analyze_existing_outfits_for_user(args.user_id)
        print(f"\n📊 Analysis result for {args.user_id}:")
        print(f"Total outfits: {result['total_outfits']}")
        print(f"Items analyzed: {result['total_items_analyzed']}")
        if result.get('top_favorites'):
            print("\n🏆 Top favorites:")
            for item_type, favorite in result['top_favorites'].items():
                print(f"  {item_type.capitalize()}: {favorite['item_name']} (Score: {favorite['favorite_score']:.3f})")
    elif args.all_users:
        analyze_all_users()
    else:
        print("Please specify --user-id, --all-users, or --test")
        print("Example: python analyze_existing_outfits_for_favorites.py --user-id user123")
        print("Example: python analyze_existing_outfits_for_favorites.py --all-users")
        print("Example: python analyze_existing_outfits_for_favorites.py --test user123") 