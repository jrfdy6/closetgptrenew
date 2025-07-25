#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config.firebase import db
from datetime import datetime, timezone

def debug_recent_outfits():
    """Debug why recent outfit data isn't being captured properly."""
    
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    print(f"🔍 Debugging Recent Outfits for User: {user_id}")
    print("=" * 60)
    
    try:
        # Get all outfits for this user
        outfits = db.collection('outfits').where('user_id', '==', user_id).stream()
        
        outfit_list = []
        for outfit in outfits:
            outfit_data = outfit.to_dict()
            created_at = outfit_data.get('createdAt', 0)
            
            # Try different timestamp formats
            if created_at:
                try:
                    # If it's a timestamp in seconds
                    if created_at < 10000000000:  # Before year 2286
                        date_obj = datetime.fromtimestamp(created_at, tz=timezone.utc)
                    else:
                        # If it's a timestamp in milliseconds
                        date_obj = datetime.fromtimestamp(created_at / 1000, tz=timezone.utc)
                except:
                    date_obj = None
            else:
                date_obj = None
            
            outfit_list.append({
                'id': outfit.id,
                'name': outfit_data.get('name', 'Unknown'),
                'occasion': outfit_data.get('occasion', 'Unknown'),
                'style': outfit_data.get('style', 'Unknown'),
                'item_count': len(outfit_data.get('items', [])),
                'created_at_raw': created_at,
                'created_at_parsed': date_obj,
                'success': len(outfit_data.get('items', [])) > 0,
                'feedback': outfit_data.get('feedback', {}),
                'rating': outfit_data.get('rating'),
                'user_rating': outfit_data.get('userRating'),
                'raw_data': outfit_data
            })
        
        # Sort by creation date (newest first)
        outfit_list.sort(key=lambda x: x['created_at_raw'], reverse=True)
        
        print(f"📊 Total Outfits Found: {len(outfit_list)}")
        print()
        
        # Show raw timestamp data for first 10 outfits
        print("🔍 Raw Timestamp Analysis (First 10 Outfits):")
        for i, outfit in enumerate(outfit_list[:10]):
            raw_timestamp = outfit['created_at_raw']
            parsed_date = outfit['created_at_parsed']
            date_str = parsed_date.strftime('%Y-%m-%d %H:%M:%S UTC') if parsed_date else 'Invalid'
            
            print(f"   {i+1}. Raw timestamp: {raw_timestamp}")
            print(f"      Parsed date: {date_str}")
            print(f"      Occasion: {outfit['occasion']}")
            print(f"      Items: {outfit['item_count']}")
            print(f"      Rating: {outfit.get('rating')}")
            print(f"      User Rating: {outfit.get('userRating')}")
            print()
        
        # Check for outfits with ratings
        rated_outfits = [o for o in outfit_list if o.get('rating') or o.get('userRating')]
        print(f"⭐ Outfits with Ratings: {len(rated_outfits)}")
        for outfit in rated_outfits[:5]:
            print(f"   - {outfit['occasion']}: Rating={outfit.get('rating')}, UserRating={outfit.get('userRating')}")
        print()
        
        # Check for recent interview outfits specifically
        interview_outfits = [o for o in outfit_list if 'interview' in o['occasion'].lower()]
        print(f"👔 Interview Outfits Found: {len(interview_outfits)}")
        for outfit in interview_outfits:
            date_str = outfit['created_at_parsed'].strftime('%Y-%m-%d %H:%M:%S UTC') if outfit['created_at_parsed'] else 'Invalid'
            print(f"   - {outfit['occasion']}: {outfit['item_count']} items, {date_str}, Rating={outfit.get('rating')}")
        print()
        
        # Check database collection directly
        print("🔍 Database Collection Info:")
        try:
            # Get collection reference
            collection_ref = db.collection('outfits')
            print(f"   Collection path: {collection_ref.path}")
            
            # Count total documents
            total_docs = len(list(collection_ref.stream()))
            print(f"   Total documents in collection: {total_docs}")
            
            # Check for documents with this user_id
            user_docs = list(collection_ref.where('user_id', '==', user_id).stream())
            print(f"   Documents with user_id {user_id}: {len(user_docs)}")
            
            # Check for documents without user_id
            all_docs = list(collection_ref.stream())
            docs_without_user_id = [doc for doc in all_docs if not doc.to_dict().get('user_id')]
            print(f"   Documents without user_id: {len(docs_without_user_id)}")
            
        except Exception as e:
            print(f"   Error accessing collection: {e}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_recent_outfits() 