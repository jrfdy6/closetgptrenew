#!/usr/bin/env python3
"""
Test script to check outfit_history collection data
"""
import os
import sys
from datetime import datetime, timezone, timedelta

# Add the backend src to the path
sys.path.append('/Users/johnniefields/Desktop/Cursor/closetgptrenew/backend/src')

try:
    from config.firebase import db
    print("✅ Firebase connection successful")
except Exception as e:
    print(f"❌ Firebase connection failed: {e}")
    sys.exit(1)

def test_outfit_history():
    """Test the outfit_history collection"""
    try:
        # Get current week start (Sunday)
        now = datetime.now(timezone.utc)
        days_since_sunday = (now.weekday() + 1) % 7
        week_start = now - timedelta(days=days_since_sunday)
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        print(f"📅 Current time: {now.isoformat()}")
        print(f"📅 Week start (Sunday): {week_start.isoformat()}")
        
        # Query outfit_history collection
        print("\n🔍 Querying outfit_history collection...")
        history_ref = db.collection('outfit_history')
        docs = list(history_ref.limit(10).stream())
        
        print(f"📊 Found {len(docs)} outfit_history documents (showing first 10)")
        
        worn_this_week = 0
        for i, doc in enumerate(docs):
            data = doc.to_dict()
            user_id = data.get('user_id', 'Unknown')
            date_worn = data.get('date_worn')
            outfit_id = data.get('outfit_id', 'Unknown')
            
            print(f"\n📄 Document {i+1}: {doc.id}")
            print(f"   User ID: {user_id}")
            print(f"   Outfit ID: {outfit_id}")
            print(f"   Date Worn: {date_worn} (type: {type(date_worn)})")
            
            if date_worn:
                # Parse date_worn
                try:
                    if hasattr(date_worn, 'timestamp'):
                        worn_date = datetime.fromtimestamp(date_worn.timestamp(), tz=timezone.utc)
                    elif isinstance(date_worn, str):
                        worn_date = datetime.fromisoformat(date_worn.replace('Z', '+00:00'))
                    else:
                        worn_date = date_worn
                    
                    if worn_date >= week_start:
                        worn_this_week += 1
                        print(f"   ✅ This week: {worn_date.isoformat()}")
                    else:
                        print(f"   ❌ Not this week: {worn_date.isoformat()}")
                        
                except Exception as e:
                    print(f"   ⚠️ Error parsing date: {e}")
            else:
                print(f"   ⚠️ No date_worn field")
        
        print(f"\n📊 Total wear events this week: {worn_this_week}")
        
    except Exception as e:
        print(f"❌ Error testing outfit_history: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_outfit_history()
