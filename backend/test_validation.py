#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.types.wardrobe import ClothingItem
from pydantic import ValidationError

def test_clothing_item_validation():
    """Test ClothingItem validation with sample data."""
    
    # Sample data that should work
    sample_data = {
        'id': 'test123',
        'name': 'Test Shirt',
        'type': 'shirt',
        'color': 'Blue',
        'season': ['spring', 'summer'],
        'imageUrl': 'https://example.com/image.jpg',
        'tags': ['casual'],
        'style': ['Casual'],
        'userId': 'testuser',
        'dominantColors': [{'name': 'Blue', 'hex': '#0000FF', 'rgb': [0, 0, 255]}],
        'matchingColors': [{'name': 'White', 'hex': '#FFFFFF', 'rgb': [255, 255, 255]}],
        'occasion': ['Casual'],
        'createdAt': 1234567890,
        'updatedAt': 1234567890
    }
    
    try:
        item = ClothingItem(**sample_data)
        print("✓ Sample data validation successful")
        print(f"  Item type: {item.type}")
        print(f"  Item color: {item.color}")
    except ValidationError as e:
        print("✗ Sample data validation failed:")
        print(e)
    
    # Test with minimal data
    minimal_data = {
        'id': 'test123',
        'name': 'Test Item',
        'type': 'other',
        'color': 'Unknown',
        'season': ['all'],
        'imageUrl': '',
        'tags': [],
        'style': ['Casual'],
        'userId': 'testuser',
        'dominantColors': [],
        'matchingColors': [],
        'occasion': ['Casual'],
        'createdAt': 0,
        'updatedAt': 0
    }
    
    try:
        item = ClothingItem(**minimal_data)
        print("✓ Minimal data validation successful")
    except ValidationError as e:
        print("✗ Minimal data validation failed:")
        print(e)

if __name__ == "__main__":
    test_clothing_item_validation() 