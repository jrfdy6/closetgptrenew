#!/usr/bin/env python3
"""
Firestore Index Creation Helper Script

This script helps create the required Firestore indexes for the outfit generation system.
It provides both interactive and automated options for index creation.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

# Required indexes configuration
REQUIRED_INDEXES = {
    "wardrobe": [
        {
            "name": "User + Category + Seasonality",
            "fields": [
                {"fieldPath": "userId", "order": "ASCENDING"},
                {"fieldPath": "category", "order": "ASCENDING"},
                {"fieldPath": "seasonality", "arrayConfig": "CONTAINS"}
            ],
            "description": "Filter items by user, category, and season"
        },
        {
            "name": "User + Category + Formality",
            "fields": [
                {"fieldPath": "userId", "order": "ASCENDING"},
                {"fieldPath": "category", "order": "ASCENDING"},
                {"fieldPath": "formality", "order": "ASCENDING"}
            ],
            "description": "Filter items by user, category, and formality level"
        },
        {
            "name": "User + Category + Quality Score",
            "fields": [
                {"fieldPath": "userId", "order": "ASCENDING"},
                {"fieldPath": "category", "order": "ASCENDING"},
                {"fieldPath": "quality_score", "order": "DESCENDING"}
            ],
            "description": "Get high-quality items by category"
        },
        {
            "name": "User + Category + Pairability Score",
            "fields": [
                {"fieldPath": "userId", "order": "ASCENDING"},
                {"fieldPath": "category", "order": "ASCENDING"},
                {"fieldPath": "pairability_score", "order": "DESCENDING"}
            ],
            "description": "Get highly pairable items by category"
        },
        {
            "name": "User + Favorite Items",
            "fields": [
                {"fieldPath": "userId", "order": "ASCENDING"},
                {"fieldPath": "favorite", "order": "ASCENDING"}
            ],
            "description": "Get user's favorite items"
        },
        {
            "name": "User + Category + Wear Count",
            "fields": [
                {"fieldPath": "userId", "order": "ASCENDING"},
                {"fieldPath": "category", "order": "ASCENDING"},
                {"fieldPath": "wear_count", "order": "ASCENDING"}
            ],
            "description": "Get underutilized items"
        },
        {
            "name": "User + Style Tags",
            "fields": [
                {"fieldPath": "userId", "order": "ASCENDING"},
                {"fieldPath": "style_tags", "arrayConfig": "CONTAINS_ANY"}
            ],
            "description": "Filter items by style compatibility"
        },
        {
            "name": "User + Material + Seasonality",
            "fields": [
                {"fieldPath": "userId", "order": "ASCENDING"},
                {"fieldPath": "material", "order": "ASCENDING"},
                {"fieldPath": "seasonality", "arrayConfig": "CONTAINS"}
            ],
            "description": "Weather-appropriate material filtering"
        }
    ],
    "outfits": [
        {
            "name": "User + Creation Date Range",
            "fields": [
                {"fieldPath": "user_id", "order": "ASCENDING"},
                {"fieldPath": "createdAt", "order": "ASCENDING"}
            ],
            "description": "Get outfits within date range"
        },
        {
            "name": "User + Success Status",
            "fields": [
                {"fieldPath": "user_id", "order": "ASCENDING"},
                {"fieldPath": "wasSuccessful", "order": "ASCENDING"}
            ],
            "description": "Filter successful vs failed outfits"
        }
    ]
}

def check_firebase_cli():
    """Check if Firebase CLI is installed and accessible."""
    try:
        result = subprocess.run(['firebase', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Firebase CLI found: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Firebase CLI not found")
        return False

def check_firebase_login():
    """Check if user is logged into Firebase."""
    try:
        result = subprocess.run(['firebase', 'projects:list'], 
                              capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def create_firestore_indexes_json():
    """Create the firestore.indexes.json file."""
    indexes_config = {
        "indexes": [],
        "fieldOverrides": []
    }
    
    for collection, indexes in REQUIRED_INDEXES.items():
        for index in indexes:
            indexes_config["indexes"].append({
                "collectionGroup": collection,
                "queryScope": "COLLECTION",
                "fields": index["fields"]
            })
    
    # Write to file
    with open('firestore.indexes.json', 'w') as f:
        json.dump(indexes_config, f, indent=2)
    
    print("✅ Created firestore.indexes.json")
    return indexes_config

def deploy_indexes():
    """Deploy the indexes using Firebase CLI."""
    try:
        print("🚀 Deploying Firestore indexes...")
        result = subprocess.run(['firebase', 'deploy', '--only', 'firestore:indexes'], 
                              capture_output=True, text=True, check=True)
        print("✅ Indexes deployed successfully!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Failed to deploy indexes:")
        print(e.stderr)
        return False

def print_index_summary():
    """Print a summary of required indexes."""
    print("\n📋 Required Firestore Indexes Summary:")
    print("=" * 50)
    
    total_indexes = 0
    for collection, indexes in REQUIRED_INDEXES.items():
        print(f"\n📁 Collection: {collection}")
        print("-" * 30)
        for i, index in enumerate(indexes, 1):
            print(f"{i}. {index['name']}")
            print(f"   Purpose: {index['description']}")
            fields = []
            for field in index['fields']:
                if 'arrayConfig' in field:
                    fields.append(f"{field['fieldPath']} (Array {field['arrayConfig']})")
                else:
                    fields.append(f"{field['fieldPath']} ({field['order']})")
            print(f"   Fields: {', '.join(fields)}")
            total_indexes += 1
    
    print(f"\n📊 Total indexes to create: {total_indexes}")

def interactive_setup():
    """Interactive setup process."""
    print("🔥 Firestore Index Creation Helper")
    print("=" * 40)
    
    # Check Firebase CLI
    if not check_firebase_cli():
        print("\n📦 Installing Firebase CLI...")
        print("Please run: npm install -g firebase-tools")
        print("Then run this script again.")
        return False
    
    # Check login
    if not check_firebase_login():
        print("\n🔐 Please login to Firebase:")
        print("Run: firebase login")
        print("Then run this script again.")
        return False
    
    # Print summary
    print_index_summary()
    
    # Ask for confirmation
    response = input("\n🤔 Do you want to create these indexes? (y/N): ").lower()
    if response != 'y':
        print("❌ Index creation cancelled.")
        return False
    
    # Create configuration file
    create_firestore_indexes_json()
    
    # Deploy indexes
    if deploy_indexes():
        print("\n🎉 All indexes created successfully!")
        print("\n⏳ Note: Index building may take 1-60 minutes depending on collection size.")
        print("   Check the Firebase Console to monitor progress.")
        return True
    else:
        print("\n❌ Index creation failed. Please check the error messages above.")
        return False

def generate_manual_instructions():
    """Generate manual instructions for index creation."""
    print("\n📝 Manual Index Creation Instructions:")
    print("=" * 50)
    print("\n1. Open Firebase Console:")
    print("   https://console.firebase.google.com")
    print("\n2. Select your project")
    print("\n3. Go to Firestore Database > Indexes")
    print("\n4. Click 'Create Index' for each index below:")
    
    for collection, indexes in REQUIRED_INDEXES.items():
        print(f"\n📁 Collection: {collection}")
        for i, index in enumerate(indexes, 1):
            print(f"\n   {i}. {index['name']}")
            print(f"      Collection: {collection}")
            print(f"      Query scope: Collection")
            print(f"      Fields:")
            for field in index['fields']:
                if 'arrayConfig' in field:
                    print(f"        - {field['fieldPath']} (Array {field['arrayConfig']})")
                else:
                    print(f"        - {field['fieldPath']} ({field['order']})")
            print(f"      Purpose: {index['description']}")

def main():
    """Main function."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--manual":
            generate_manual_instructions()
            return
        elif sys.argv[1] == "--summary":
            print_index_summary()
            return
        elif sys.argv[1] == "--config":
            create_firestore_indexes_json()
            return
    
    # Default interactive mode
    success = interactive_setup()
    
    if not success:
        print("\n💡 Alternative options:")
        print("  --manual   : Show manual creation instructions")
        print("  --summary  : Show index summary")
        print("  --config   : Generate firestore.indexes.json only")

if __name__ == "__main__":
    main() 