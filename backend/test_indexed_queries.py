"""
Test Indexed Firestore Queries
==============================

This script tests the performance and accuracy of indexed Firestore queries
for outfit generation and fallback strategies.
"""

import asyncio
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.outfit_fallback_service import OutfitFallbackService
from src.services.wardrobe_indexing_service import WardrobeIndexingService
from src.types.wardrobe import ClothingItem
from src.types.weather import WeatherData
from src.types.profile import UserProfile
import time

async def test_indexed_queries():
    """Test the performance of indexed Firestore queries."""
    
    print("🧪 Testing Indexed Firestore Queries")
    print("=" * 60)
    
    # Initialize services
    fallback_service = OutfitFallbackService()
    indexing_service = WardrobeIndexingService()
    
    # Create test context
    context = {
        'occasion': 'casual',
        'weather': WeatherData(
            temperature=75.0,
            condition='sunny',
            humidity=60.0,
            wind_speed=5.0
        ),
        'user_profile': UserProfile(
            id='test-user-123',
            name='Test User',
            email='test@example.com',
            gender='male',
            bodyType='athletic',
            skinTone='medium',
            stylePreferences=['casual', 'minimalist'],
            colorPreferences=['blue', 'gray', 'white'],
            occasionPreferences=['casual', 'workout'],
            measurements={
                'height': 180,
                'weight': 75,
                'chest': 100,
                'waist': 80,
                'hips': 95
            }
        ),
        'style': 'casual',
        'mood': 'relaxed'
    }
    
    # Test 1: Category-based queries
    print("\n🔍 Test 1: Category-based Queries")
    print("-" * 40)
    
    start_time = time.time()
    top_items = await fallback_service._query_category_with_indexes(
        'test-user-123', 'top', context, 5
    )
    query_time = time.time() - start_time
    
    print(f"✅ Query time: {query_time:.3f} seconds")
    print(f"✅ Items found: {len(top_items)}")
    for item in top_items:
        print(f"   - {item.name} ({item.type})")
    
    # Test 2: Weather-appropriate queries
    print("\n🔍 Test 2: Weather-appropriate Queries")
    print("-" * 40)
    
    test_item = ClothingItem(
        id='test-item',
        name='Test Item',
        type='shirt',
        color='blue',
        season=['spring', 'summer'],
        style=['casual'],
        occasion=['casual'],
        imageUrl='https://example.com/test.jpg',
        tags=['cotton'],
        dominantColors=[{'name': 'blue', 'hex': '#0000FF'}],
        matchingColors=[{'name': 'white', 'hex': '#FFFFFF'}],
        createdAt=int(time.time()),
        updatedAt=int(time.time()),
        userId='test-user-123'
    )
    
    start_time = time.time()
    weather_replacement = await fallback_service._find_weather_appropriate_replacement(
        test_item, 75.0, 'summer', context
    )
    query_time = time.time() - start_time
    
    print(f"✅ Query time: {query_time:.3f} seconds")
    if weather_replacement:
        print(f"✅ Found replacement: {weather_replacement.name}")
    else:
        print("❌ No replacement found")
    
    # Test 3: Style-compatible queries
    print("\n🔍 Test 3: Style-compatible Queries")
    print("-" * 40)
    
    start_time = time.time()
    style_replacement = await fallback_service._find_style_compatible_replacement(
        test_item, 'casual', context
    )
    query_time = time.time() - start_time
    
    print(f"✅ Query time: {query_time:.3f} seconds")
    if style_replacement:
        print(f"✅ Found replacement: {style_replacement.name}")
    else:
        print("❌ No replacement found")
    
    # Test 4: Better alternative queries
    print("\n🔍 Test 4: Better Alternative Queries")
    print("-" * 40)
    
    start_time = time.time()
    better_alternative = await fallback_service._find_better_alternative(
        test_item, context
    )
    query_time = time.time() - start_time
    
    print(f"✅ Query time: {query_time:.3f} seconds")
    if better_alternative:
        print(f"✅ Found better alternative: {better_alternative.name}")
    else:
        print("❌ No better alternative found")
    
    # Test 5: Scratch generation with indexes
    print("\n🔍 Test 5: Scratch Generation with Indexes")
    print("-" * 40)
    
    start_time = time.time()
    scratch_outfit = await fallback_service._generate_from_scratch_with_indexes(context)
    query_time = time.time() - start_time
    
    print(f"✅ Query time: {query_time:.3f} seconds")
    if scratch_outfit:
        print(f"✅ Generated outfit with {len(scratch_outfit)} items:")
        for item in scratch_outfit:
            print(f"   - {item.name} ({item.type})")
    else:
        print("❌ Failed to generate outfit")
    
    # Test 6: Indexing service performance
    print("\n🔍 Test 6: Indexing Service Performance")
    print("-" * 40)
    
    # Test indexing a sample item
    sample_item = ClothingItem(
        id='sample-item',
        name='Sample Item',
        type='t-shirt',
        color='white',
        season=['spring', 'summer'],
        style=['casual', 'minimalist'],
        occasion=['casual'],
        imageUrl='https://example.com/sample.jpg',
        tags=['cotton', 'comfortable'],
        dominantColors=[{'name': 'white', 'hex': '#FFFFFF'}],
        matchingColors=[{'name': 'black', 'hex': '#000000'}],
        createdAt=int(time.time()),
        updatedAt=int(time.time()),
        userId='test-user-123'
    )
    
    start_time = time.time()
    indexed_data = await indexing_service.create_indexes_for_wardrobe_item(sample_item)
    indexing_time = time.time() - start_time
    
    print(f"✅ Indexing time: {indexing_time:.3f} seconds")
    print(f"✅ Indexed fields: {list(indexed_data.keys())}")
    print(f"✅ Category: {indexed_data.get('category')}")
    print(f"✅ Material: {indexed_data.get('material')}")
    print(f"✅ Formality: {indexed_data.get('formality')}")
    print(f"✅ Quality score: {indexed_data.get('quality_score')}")
    
    # Test 7: Wardrobe statistics
    print("\n🔍 Test 7: Wardrobe Statistics")
    print("-" * 40)
    
    start_time = time.time()
    stats = await indexing_service.get_indexed_wardrobe_stats('test-user-123')
    stats_time = time.time() - start_time
    
    print(f"✅ Stats query time: {stats_time:.3f} seconds")
    print(f"✅ Total items: {stats.get('total_items', 0)}")
    print(f"✅ Indexed items: {stats.get('indexed_items', 0)}")
    print(f"✅ Non-indexed items: {stats.get('non_indexed_items', 0)}")
    
    if stats.get('categories'):
        print("✅ Categories found:")
        for category, count in stats['categories'].items():
            print(f"   - {category}: {count}")
    
    print("\n🎉 Indexed Query Testing Complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_indexed_queries()) 