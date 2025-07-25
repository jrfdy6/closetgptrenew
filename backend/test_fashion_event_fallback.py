#!/usr/bin/env python3

def test_fashion_event_fallback_logic():
    """Test the Fashion Event fallback logic directly."""
    
    # Simulate the fallback logic from the outfit service
    def calculate_occasion_appropriateness_enhanced(items, occasion):
        """Simulate the enhanced occasion appropriateness calculation."""
        if not items:
            return 0.8
        
        appropriate_items = 0
        total_items = len(items)
        
        for item in items:
            # Check both regular and enhanced occasion tags
            occasions = item.get('occasion', []) + item.get('metadata', {}).get('enhancedOccasions', [])
            if occasion in occasions:
                appropriate_items += 1
        
        base_score = appropriate_items / total_items
        
        # Fallback logic for low scores
        if base_score == 0.0:
            print(f"DEBUG: Zero occasion score, applying fallback logic for: {occasion}")
            
            # Fashion Event
            if 'fashion' in occasion.lower() or 'event' in occasion.lower():
                print(f"DEBUG: Fashion event detected, applying fashion-specific logic")
                fashion_matches = 0
                for item in items:
                    item_name_lower = item.get('name', '').lower()
                    item_type_lower = item.get('type', '').lower()
                    stylish_keywords = ['stylish', 'fashion', 'trendy', 'modern', 'designer', 'elegant']
                    if any(keyword in item_name_lower for keyword in stylish_keywords):
                        fashion_matches += 1
                    elif any(basic_type in item_type_lower for basic_type in ['shirt', 'pants', 'shoes', 'dress', 'jacket', 'sweater']):
                        fashion_matches += 1
                    elif len(item.get('occasion', [])) > 0:
                        fashion_matches += 1
                    else:
                        fashion_matches += 1
                if fashion_matches > 0:
                    fallback_score = fashion_matches / total_items
                    print(f"DEBUG: Fashion event fallback score: {fallback_score}")
                    return max(fallback_score, 0.5)
            
            # Casual/athletic
            elif occasion.lower() in ['casual', 'athletic', 'gym', 'beach', 'vacation', 'errands']:
                casual_keywords = ['casual', 'comfortable', 'relaxed', 'everyday', 'basic', 'loose', 'slim']
                casual_matches = 0
                for item in items:
                    item_name_lower = item.get('name', '').lower()
                    item_type_lower = item.get('type', '').lower()
                    if any(keyword in item_name_lower or keyword in item_type_lower for keyword in casual_keywords):
                        casual_matches += 1
                    elif any(basic_type in item_type_lower for basic_type in ['t-shirt', 'jeans', 'sneakers', 'shorts', 'pants', 'shoes']):
                        casual_matches += 1
                    elif 'casual' in [occ.lower() for occ in item.get('occasion', [])]:
                        casual_matches += 1
                if casual_matches > 0:
                    fallback_score = casual_matches / total_items
                    print(f"DEBUG: Casual fallback score: {fallback_score}")
                    return max(fallback_score, 0.3)
            
            # Formal
            elif occasion.lower() in ['formal', 'business', 'interview', 'gala', 'wedding']:
                formal_keywords = ['formal', 'business', 'professional', 'dress', 'suit', 'blazer']
                formal_matches = 0
                for item in items:
                    item_name_lower = item.get('name', '').lower()
                    item_type_lower = item.get('type', '').lower()
                    if any(keyword in item_name_lower or keyword in item_type_lower for keyword in formal_keywords):
                        formal_matches += 1
                    elif any(formal_type in item_type_lower for formal_type in ['dress', 'suit', 'blazer', 'shirt', 'pants']):
                        formal_matches += 1
                    elif any('formal' in occ.lower() or 'business' in occ.lower() for occ in item.get('occasion', [])):
                        formal_matches += 1
                if formal_matches > 0:
                    fallback_score = formal_matches / total_items
                    print(f"DEBUG: Formal fallback score: {fallback_score}")
                    return max(fallback_score, 0.4)
            
            # Party/social
            elif occasion.lower() in ['party', 'cocktail', 'night out', 'date night', 'brunch']:
                social_keywords = ['party', 'cocktail', 'dress', 'stylish', 'elegant', 'fashion']
                social_matches = 0
                for item in items:
                    item_name_lower = item.get('name', '').lower()
                    item_type_lower = item.get('type', '').lower()
                    if any(keyword in item_name_lower or keyword in item_type_lower for keyword in social_keywords):
                        social_matches += 1
                    elif any(social_type in item_type_lower for social_type in ['dress', 'shirt', 'pants', 'shoes', 'jacket']):
                        social_matches += 1
                    elif any('party' in occ.lower() or 'cocktail' in occ.lower() for occ in item.get('occasion', [])):
                        social_matches += 1
                if social_matches > 0:
                    fallback_score = social_matches / total_items
                    print(f"DEBUG: Social fallback score: {fallback_score}")
                    return max(fallback_score, 0.4)
            
            # Outdoor/athletic
            elif occasion.lower() in ['athletic', 'gym', 'workout', 'sports', 'outdoor', 'hiking']:
                athletic_keywords = ['athletic', 'sport', 'gym', 'workout', 'active', 'comfortable']
                athletic_matches = 0
                for item in items:
                    item_name_lower = item.get('name', '').lower()
                    item_type_lower = item.get('type', '').lower()
                    if any(keyword in item_name_lower or keyword in item_type_lower for keyword in athletic_keywords):
                        athletic_matches += 1
                    elif any(athletic_type in item_type_lower for athletic_type in ['shorts', 'pants', 'shoes', 'shirt', 't-shirt']):
                        athletic_matches += 1
                    elif any('athletic' in occ.lower() or 'gym' in occ.lower() for occ in item.get('occasion', [])):
                        athletic_matches += 1
                if athletic_matches > 0:
                    fallback_score = athletic_matches / total_items
                    print(f"DEBUG: Athletic fallback score: {fallback_score}")
                    return max(fallback_score, 0.3)
            
            # Travel/vacation
            elif occasion.lower() in ['travel', 'vacation', 'airport', 'beach', 'holiday']:
                travel_keywords = ['comfortable', 'casual', 'relaxed', 'travel', 'vacation', 'beach']
                travel_matches = 0
                for item in items:
                    item_name_lower = item.get('name', '').lower()
                    item_type_lower = item.get('type', '').lower()
                    if any(keyword in item_name_lower or keyword in item_type_lower for keyword in travel_keywords):
                        travel_matches += 1
                    elif any(travel_type in item_type_lower for travel_type in ['shirt', 'pants', 'shoes', 'shorts', 'dress']):
                        travel_matches += 1
                    elif any('travel' in occ.lower() or 'vacation' in occ.lower() for occ in item.get('occasion', [])):
                        travel_matches += 1
                if travel_matches > 0:
                    fallback_score = travel_matches / total_items
                    print(f"DEBUG: Travel fallback score: {fallback_score}")
                    return max(fallback_score, 0.3)
            
            # General fallback
            else:
                print(f"DEBUG: General fallback for occasion: {occasion}")
                basic_items = ['shirt', 'pants', 'shoes', 'dress', 'jacket', 'sweater', 't-shirt', 'jeans']
                basic_count = 0
                for item in items:
                    item_type_lower = item.get('type', '').lower()
                    if any(basic in item_type_lower for basic in basic_items):
                        basic_count += 1
                if basic_count >= 2:
                    fallback_score = basic_count / total_items
                    print(f"DEBUG: General fallback score: {fallback_score}")
                    return max(fallback_score, 0.3)
        
        return base_score
    
    # Create test items with only casual occasions
    test_items = [
        {
            "id": "1",
            "name": "Blue T-Shirt",
            "type": "shirt",
            "color": "blue",
            "style": ["casual"],
            "occasion": ["casual"],  # Only casual, no fashion event
            "season": ["spring", "summer"],
            "tags": ["comfortable", "basic"],
            "metadata": {}
        },
        {
            "id": "2",
            "name": "Black Jeans",
            "type": "pants",
            "color": "black",
            "style": ["casual"],
            "occasion": ["casual"],  # Only casual, no fashion event
            "season": ["all"],
            "tags": ["comfortable", "basic"],
            "metadata": {}
        },
        {
            "id": "3",
            "name": "White Sneakers",
            "type": "shoes",
            "color": "white",
            "style": ["casual"],
            "occasion": ["casual"],  # Only casual, no fashion event
            "season": ["all"],
            "tags": ["comfortable", "basic"],
            "metadata": {}
        }
    ]
    
    # Test Fashion Event occasion appropriateness
    print("Testing Fashion Event fallback logic...")
    print(f"Items: {[item['name'] for item in test_items]}")
    print(f"Items have occasions: {[item['occasion'] for item in test_items]}")
    
    # Test the occasion appropriateness calculation
    score = calculate_occasion_appropriateness_enhanced(test_items, "Fashion Event")
    print(f"Fashion Event appropriateness score: {score}")
    
    # Test other occasions
    occasions_to_test = [
        "Casual",
        "Formal", 
        "Party",
        "Athletic",
        "Travel",
        "Business"
    ]
    
    print("\nTesting other occasions:")
    for occasion in occasions_to_test:
        score = calculate_occasion_appropriateness_enhanced(test_items, occasion)
        print(f"{occasion}: {score}")
    
    print("\nFashion Event fallback logic test completed!")

if __name__ == "__main__":
    test_fashion_event_fallback_logic() 