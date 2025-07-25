"""
Setup Firestore Indexes for Wardrobe Collection
==============================================

This script helps set up the required Firestore indexes for the wardrobe collection
to enable fast, scalable queries for outfit generation and fallback strategies.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.wardrobe_indexing_service import WardrobeIndexingService
import asyncio

async def setup_indexes():
    """Set up Firestore indexes for the wardrobe collection."""
    
    print("🔧 Setting up Firestore Indexes for Wardrobe Collection")
    print("=" * 60)
    
    indexing_service = WardrobeIndexingService()
    
    # Get required indexes
    required_indexes = indexing_service.get_required_firestore_indexes()
    
    print(f"📋 Found {len(required_indexes)} required indexes")
    print("\n🔧 Required Firestore Indexes (to be created manually in Firebase Console):")
    print("-" * 60)
    
    for i, index in enumerate(required_indexes, 1):
        print(f"{i:2d}. Collection: {index['collection']}")
        print(f"    Fields: {', '.join(index['fields'])}")
        print(f"    Scope: {index['queryScope']}")
        print()
    
    print("📋 Instructions for creating indexes in Firebase Console:")
    print("1. Go to Firebase Console > Firestore Database")
    print("2. Click on 'Indexes' tab")
    print("3. Click 'Create Index'")
    print("4. For each index above:")
    print("   - Collection ID: wardrobe")
    print("   - Fields: Add each field with appropriate type")
    print("   - Query scope: Collection")
    print("5. Click 'Create'")
    print()
    
    print("⚡ Index Creation Priority:")
    print("High Priority (for basic queries):")
    high_priority = [
        ['userId', 'category', 'seasonality'],
        ['userId', 'category', 'occasions'],
        ['userId', 'category', 'formality'],
        ['userId', 'category', 'quality_score'],
        ['userId', 'category', 'pairability_score']
    ]
    
    for i, fields in enumerate(high_priority, 1):
        print(f"   {i}. {', '.join(fields)}")
    
    print("\nMedium Priority (for advanced queries):")
    medium_priority = [
        ['userId', 'category', 'seasonality', 'formality'],
        ['userId', 'category', 'occasions', 'style_tags'],
        ['userId', 'category', 'temperature_range', 'material'],
        ['userId', 'category', 'body_type_compatibility', 'skin_tone_compatibility']
    ]
    
    for i, fields in enumerate(medium_priority, 1):
        print(f"   {i}. {', '.join(fields)}")
    
    print("\nLow Priority (for complex queries):")
    low_priority = [
        ['userId', 'category', 'seasonality', 'occasions', 'formality'],
        ['userId', 'category', 'temperature_range', 'material', 'style_tags'],
        ['userId', 'category', 'quality_score', 'pairability_score', 'favorite']
    ]
    
    for i, fields in enumerate(low_priority, 1):
        print(f"   {i}. {', '.join(fields)}")
    
    print("\n✅ Index setup instructions complete!")
    print("💡 Note: Index creation may take several minutes to complete.")

if __name__ == "__main__":
    asyncio.run(setup_indexes()) 