#!/usr/bin/env python3
"""
Simple test to check filtering logic for Fashion Event
"""

def test_occasion_filtering():
    """Test the occasion filtering logic manually."""
    print("🔍 Testing Fashion Event filtering logic")
    print("=" * 50)
    
    # Simulate the filtering logic from _filter_by_occasion_strict
    occasion = "Fashion Event"
    occasion_lower = occasion.lower()
    
    print(f"Occasion: {occasion}")
    print(f"Occasion (lower): {occasion_lower}")
    
    # Check if "fashion_event" is in the occasion rules
    occasion_rules = {
        "gym": ["dress shoes", "dress shirt", "formal", "heels", "dress pants", "slacks"],
        "beach": ["closed leather shoes", "blazer", "tight jeans", "formal"],
        "work": ["tank top", "flip-flops", "swimwear", "athletic"],
        "party": ["athletic", "gym", "workout", "casual shorts", "athletic shorts", "sweatpants"],
        "formal": ["athletic", "casual", "beach", "gym", "tank top", "polo", "t-shirt", "jeans", "shorts", "sneakers", "toe shoes", "slides", "flip flops", "sandals", "running shoes", "athletic shoes", "sport shoes"],
        "gala": ["athletic", "casual", "beach", "gym", "tank top", "polo", "t-shirt", "jeans", "shorts", "sneakers", "toe shoes", "slides", "flip flops", "sandals", "running shoes", "athletic shoes", "sport shoes", "short sleeve", "short-sleeve"]
    }
    
    print(f"\nAvailable occasion rules: {list(occasion_rules.keys())}")
    
    # Check if "fashion_event" matches any rules
    forbidden_types = []
    for key, forbidden in occasion_rules.items():
        if key in occasion_lower:
            forbidden_types.extend(forbidden)
            print(f"✓ Matched rule '{key}' - forbidden types: {forbidden}")
    
    if not forbidden_types:
        print("❌ No specific rules found for 'fashion_event'")
        print("   This means the filtering will be very lenient")
    
    # Check if it would be treated as formal
    if "formal" in occasion_lower or "gala" in occasion_lower or "interview" in occasion_lower:
        print("✓ Would be treated as formal occasion")
    else:
        print("❌ Not treated as formal occasion")
    
    # Check if it would be treated as athletic
    if "athletic" in occasion_lower or "gym" in occasion_lower:
        print("✓ Would be treated as athletic occasion")
    else:
        print("❌ Not treated as athletic occasion")
    
    print(f"\n🎯 Conclusion:")
    print(f"   - 'Fashion Event' has no specific filtering rules")
    print(f"   - It will use very lenient filtering")
    print(f"   - This means bottoms should NOT be filtered out")
    print(f"   - The issue is likely in style filtering or item selection")

def test_style_filtering():
    """Test the style filtering logic for Business Casual."""
    print(f"\n👔 Testing Business Casual style filtering")
    print("=" * 50)
    
    # Simulate the style compatibility matrix
    style = "Business Casual"
    
    # This is what the style matrix would contain for Business Casual
    style_matrix = {
        "approved_items": ["shirt", "polo", "pants", "jeans", "dress shoes", "loafers", "belt", "watch"],
        "banned_items": ["tank top", "shorts", "sneakers", "flip flops", "athletic"]
    }
    
    print(f"Style: {style}")
    print(f"Approved items: {style_matrix['approved_items']}")
    print(f"Banned items: {style_matrix['banned_items']}")
    
    # Test some items
    test_items = [
        {"name": "Slim Fit Chinos", "type": "pants"},
        {"name": "Tailored Trousers", "type": "pants"},
        {"name": "Dark Wash Jeans", "type": "jeans"},
        {"name": "A solid, smooth toe shoes by SUICOKE", "type": "shoes"},
        {"name": "Leather Oxfords", "type": "dress shoes"}
    ]
    
    print(f"\nTesting items:")
    for item in test_items:
        item_type = item["type"].lower()
        item_name = item["name"].lower()
        
        # Check if banned
        has_banned = any(banned in item_type or banned in item_name for banned in style_matrix["banned_items"])
        
        # Check if approved
        has_approved = any(approved in item_type or approved in item_name for approved in style_matrix["approved_items"])
        
        # Check if neutral (not banned)
        is_neutral = not has_banned
        
        status = "❌ BANNED" if has_banned else ("✅ APPROVED" if has_approved else "⚠️  NEUTRAL")
        
        print(f"   {item['name']} ({item['type']}) - {status}")
        if has_banned:
            banned_reasons = [banned for banned in style_matrix["banned_items"] if banned in item_type or banned in item_name]
            print(f"     Banned because: {banned_reasons}")
    
    print(f"\n🎯 Conclusion:")
    print(f"   - Pants and jeans should be APPROVED")
    print(f"   - SUICOKE shoes might be filtered out if they contain 'sneakers' or 'athletic'")
    print(f"   - The issue might be that SUICOKE shoes are being filtered out")

if __name__ == "__main__":
    test_occasion_filtering()
    test_style_filtering() 