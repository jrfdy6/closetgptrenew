#!/usr/bin/env python3
"""
Direct debug script to check user_stats document in Firestore.
This will show us exactly what's in the database.
"""

import os
import sys
from datetime import datetime, timezone, timedelta

# Add the backend src to Python path
sys.path.append('/Users/johnniefields/Desktop/Cursor/closetgptrenew/backend/src')

try:
    from config.firebase import db, firebase_initialized
    if not firebase_initialized:
        print("❌ Firebase not initialized")
        sys.exit(1)
    print("✅ Firebase initialized successfully")
except ImportError as e:
    print(f"❌ Firebase import failed: {e}")
    sys.exit(1)

def debug_user_stats():
    user_id = 'dANqjiI0CKgaitxzYtw1bhtvQrG3'
    
    print(f"\n🔍 DEBUGGING USER_STATS for user: {user_id}")
    print("=" * 60)
    
    # Get user_stats document
    stats_ref = db.collection('user_stats').document(user_id)
    stats_doc = stats_ref.get()
    
    if not stats_doc.exists:
        print("❌ user_stats document does not exist!")
        return
    
    stats_data = stats_doc.to_dict()
    print("✅ user_stats document exists")
    print(f"📄 Document data: {stats_data}")
    
    # Check specific fields
    worn_this_week = stats_data.get('worn_this_week', 'NOT_FOUND')
    last_updated = stats_data.get('last_updated', 'NOT_FOUND')
    
    print(f"\n📊 FIELD ANALYSIS:")
    print(f"   worn_this_week: {worn_this_week} (type: {type(worn_this_week)})")
    print(f"   last_updated: {last_updated} (type: {type(last_updated)})")
    
    # Calculate current week start
    now = datetime.now(timezone.utc)
    week_start = now - timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    print(f"\n📅 WEEK CALCULATION:")
    print(f"   Current time: {now}")
    print(f"   Week start (Monday): {week_start}")
    print(f"   Days since Monday: {now.weekday()}")
    
    # Test timestamp comparison
    if last_updated and last_updated != 'NOT_FOUND':
        print(f"\n🔍 TIMESTAMP COMPARISON:")
        print(f"   last_updated raw: {last_updated}")
        print(f"   last_updated type: {type(last_updated)}")
        print(f"   isinstance(last_updated, datetime): {isinstance(last_updated, datetime)}")
        print(f"   hasattr(last_updated, 'to_datetime'): {hasattr(last_updated, 'to_datetime')}")
        
        # Try to normalize
        normalized = None
        if isinstance(last_updated, datetime):
            normalized = last_updated
            print(f"   ✅ Already datetime: {normalized}")
        elif hasattr(last_updated, 'to_datetime'):
            try:
                normalized = last_updated.to_datetime()
                print(f"   ✅ Converted from Firestore timestamp: {normalized}")
            except Exception as e:
                print(f"   ❌ Failed to convert Firestore timestamp: {e}")
        
        if normalized:
            comparison_result = normalized >= week_start
            print(f"   📊 Week validation: {normalized} >= {week_start} = {comparison_result}")
        else:
            print(f"   ❌ Could not normalize timestamp for comparison")

if __name__ == "__main__":
    debug_user_stats()
