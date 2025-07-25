#!/usr/bin/env python3
"""
Script to set up Firestore indexes for the favorite scores collection.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.firebase import db

def setup_favorite_indexes():
    """Set up the required indexes for favorite scores queries."""
    print("🔧 Setting up Firestore indexes for favorite scores...")
    
    # The indexes we need:
    # 1. item_favorite_scores collection: user_id (ascending) + total_score (descending)
    # 2. analytics_events collection: user_id (ascending) + item_id (ascending) + timestamp (descending)
    
    print("📋 Required indexes:")
    print("1. Collection: item_favorite_scores")
    print("   Fields: user_id (Ascending), total_score (Descending)")
    print("   Purpose: Query favorites by user, ordered by score")
    print()
    print("2. Collection: analytics_events") 
    print("   Fields: user_id (Ascending), item_id (Ascending), timestamp (Descending)")
    print("   Purpose: Query item analytics for favorite score calculation")
    print()
    
    print("⚠️  Note: Firestore indexes must be created manually in the Firebase Console")
    print("   Go to: https://console.firebase.google.com/project/closetgptrenew/firestore/indexes")
    print()
    print("   Or use the Firebase CLI:")
    print("   firebase deploy --only firestore:indexes")
    print()
    
    # Check if indexes exist by trying a simple query
    print("🧪 Testing current index status...")
    
    try:
        # Test the favorite scores query
        query = db.collection("item_favorite_scores").where("user_id", "==", "test").order_by("total_score", direction="DESCENDING").limit(1)
        docs = list(query.stream())
        print("✅ item_favorite_scores index appears to be working")
    except Exception as e:
        if "requires an index" in str(e):
            print("❌ item_favorite_scores index is missing")
            print(f"   Error: {e}")
        else:
            print(f"⚠️  Unexpected error testing index: {e}")
    
    try:
        # Test the analytics events query
        query = db.collection("analytics_events").where("user_id", "==", "test").where("item_id", "==", "test").order_by("timestamp", direction="DESCENDING").limit(1)
        docs = list(query.stream())
        print("✅ analytics_events index appears to be working")
    except Exception as e:
        if "requires an index" in str(e):
            print("❌ analytics_events index is missing")
            print(f"   Error: {e}")
        else:
            print(f"⚠️  Unexpected error testing index: {e}")

def create_firestore_indexes_config():
    """Create a firestore.indexes.json configuration file."""
    config = {
        "indexes": [
            {
                "collectionGroup": "item_favorite_scores",
                "queryScope": "COLLECTION",
                "fields": [
                    {
                        "fieldPath": "user_id",
                        "order": "ASCENDING"
                    },
                    {
                        "fieldPath": "total_score", 
                        "order": "DESCENDING"
                    }
                ]
            },
            {
                "collectionGroup": "analytics_events",
                "queryScope": "COLLECTION", 
                "fields": [
                    {
                        "fieldPath": "user_id",
                        "order": "ASCENDING"
                    },
                    {
                        "fieldPath": "item_id",
                        "order": "ASCENDING"
                    },
                    {
                        "fieldPath": "timestamp",
                        "order": "DESCENDING"
                    }
                ]
            }
        ],
        "fieldOverrides": []
    }
    
    import json
    config_path = os.path.join(os.path.dirname(__file__), '..', 'firestore.indexes.json')
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Created firestore.indexes.json at {config_path}")
    print("   You can now deploy indexes with: firebase deploy --only firestore:indexes")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Set up Firestore indexes for favorite scores')
    parser.add_argument('--create-config', action='store_true', help='Create firestore.indexes.json config file')
    
    args = parser.parse_args()
    
    if args.create_config:
        create_firestore_indexes_config()
    else:
        setup_favorite_indexes() 