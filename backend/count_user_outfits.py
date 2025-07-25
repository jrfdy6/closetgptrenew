#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config.firebase import db

def count_user_outfits():
    """Count outfits saved by a specific user."""
    
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    print(f"Counting outfits for user: {user_id}")
    print("=" * 50)
    
    try:
        # Get all outfits for this user
        outfits = db.collection('outfits').where('user_id', '==', user_id).stream()
        
        outfit_list = []
        for outfit in outfits:
            outfit_data = outfit.to_dict()
            outfit_list.append({
                'id': outfit.id,
                'name': outfit_data.get('name', 'Unknown'),
                'occasion': outfit_data.get('occasion', 'Unknown'),
                'wasSuccessful': outfit_data.get('wasSuccessful', False),
                'createdAt': outfit_data.get('createdAt', 0),
                'items_count': len(outfit_data.get('items', []))
            })
        
        print(f"Total outfits found: {len(outfit_list)}")
        print()
        
        # Show breakdown by success status
        successful_outfits = [o for o in outfit_list if o['wasSuccessful']]
        failed_outfits = [o for o in outfit_list if not o['wasSuccessful']]
        
        print(f"Successful outfits: {len(successful_outfits)}")
        print(f"Failed outfits: {len(failed_outfits)}")
        print()
        
        # Show breakdown by occasion
        occasion_counts = {}
        for outfit in outfit_list:
            occasion = outfit['occasion']
            if occasion not in occasion_counts:
                occasion_counts[occasion] = {'total': 0, 'successful': 0, 'failed': 0}
            occasion_counts[occasion]['total'] += 1
            if outfit['wasSuccessful']:
                occasion_counts[occasion]['successful'] += 1
            else:
                occasion_counts[occasion]['failed'] += 1
        
        print("Breakdown by occasion:")
        for occasion, counts in sorted(occasion_counts.items()):
            print(f"  {occasion}: {counts['total']} total ({counts['successful']} successful, {counts['failed']} failed)")
        
        print()
        
        # Show recent outfits
        print("Recent outfits (last 10):")
        sorted_outfits = sorted(outfit_list, key=lambda x: x['createdAt'], reverse=True)
        for i, outfit in enumerate(sorted_outfits[:10], 1):
            status = "✅" if outfit['wasSuccessful'] else "❌"
            print(f"  {i}. {status} {outfit['name']} ({outfit['occasion']}) - {outfit['items_count']} items")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    count_user_outfits() 