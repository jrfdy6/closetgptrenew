#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config.firebase import db
from datetime import datetime

def count_user_outfits_detailed():
    """Count and analyze outfits for a specific user."""
    
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    print(f"📊 Detailed Outfit Analysis for User: {user_id}")
    print("=" * 60)
    
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
                'style': outfit_data.get('style', 'Unknown'),
                'item_count': len(outfit_data.get('items', [])),
                'created_at': outfit_data.get('createdAt', 0),
                'success': len(outfit_data.get('items', [])) > 0
            })
        
        # Sort by creation date (newest first)
        outfit_list.sort(key=lambda x: x['created_at'], reverse=True)
        
        total_outfits = len(outfit_list)
        successful_outfits = sum(1 for outfit in outfit_list if outfit['success'])
        failed_outfits = total_outfits - successful_outfits
        
        print(f"🎯 Overall Statistics:")
        print(f"   Total Outfits: {total_outfits}")
        print(f"   Successful: {successful_outfits} ({successful_outfits/total_outfits*100:.1f}%)")
        print(f"   Failed: {failed_outfits} ({failed_outfits/total_outfits*100:.1f}%)")
        print()
        
        # Analyze by occasion
        occasion_counts = {}
        for outfit in outfit_list:
            occasion = outfit['occasion']
            if occasion not in occasion_counts:
                occasion_counts[occasion] = {'total': 0, 'successful': 0, 'failed': 0}
            occasion_counts[occasion]['total'] += 1
            if outfit['success']:
                occasion_counts[occasion]['successful'] += 1
            else:
                occasion_counts[occasion]['failed'] += 1
        
        print("📈 Breakdown by Occasion:")
        for occasion, counts in sorted(occasion_counts.items(), key=lambda x: x[1]['total'], reverse=True):
            success_rate = counts['successful'] / counts['total'] * 100 if counts['total'] > 0 else 0
            print(f"   {occasion}: {counts['total']} total ({counts['successful']} successful, {counts['failed']} failed) - {success_rate:.1f}% success rate")
        print()
        
        # Recent activity (last 10 outfits)
        print("🕒 Recent Activity (Last 10 Outfits):")
        for i, outfit in enumerate(outfit_list[:10]):
            date_str = datetime.fromtimestamp(outfit['created_at'] / 1000).strftime('%Y-%m-%d %H:%M') if outfit['created_at'] > 0 else 'Unknown'
            status = "✅" if outfit['success'] else "❌"
            print(f"   {i+1}. {status} {outfit['occasion']} - {outfit['item_count']} items ({date_str})")
        print()
        
        # Success rate over time
        if len(outfit_list) >= 10:
            recent_10 = outfit_list[:10]
            recent_success_rate = sum(1 for outfit in recent_10 if outfit['success']) / len(recent_10) * 100
            print(f"📊 Recent Success Rate (Last 10): {recent_success_rate:.1f}%")
            
            if len(outfit_list) >= 20:
                older_10 = outfit_list[10:20]
                older_success_rate = sum(1 for outfit in older_10 if outfit['success']) / len(older_10) * 100
                print(f"📊 Previous 10 Success Rate: {older_success_rate:.1f}%")
        
        # Item count analysis
        successful_item_counts = [outfit['item_count'] for outfit in outfit_list if outfit['success']]
        if successful_item_counts:
            avg_items = sum(successful_item_counts) / len(successful_item_counts)
            min_items = min(successful_item_counts)
            max_items = max(successful_item_counts)
            print(f"\n👕 Item Count Analysis (Successful Outfits):")
            print(f"   Average items per outfit: {avg_items:.1f}")
            print(f"   Range: {min_items} - {max_items} items")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    count_user_outfits_detailed() 