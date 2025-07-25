#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.types.outfit_rules import get_occasion_rule, OCCASION_RULES

def debug_occasion_rule():
    """Debug the get_occasion_rule function."""
    
    print("Testing get_occasion_rule function...")
    print(f"Available occasion rules: {list(OCCASION_RULES.keys())}")
    
    # Test with "interview"
    result = get_occasion_rule("interview")
    print(f"\nResult for 'interview': {result}")
    
    if result:
        print(f"  - Occasion: {result.occasion}")
        print(f"  - Required items: {result.required_items}")
        print(f"  - Forbidden items: {result.forbidden_items}")
        print(f"  - Style preferences: {result.style_preferences}")
    else:
        print("  - No rule found!")
    
    # Test with "Interview" (capitalized)
    result2 = get_occasion_rule("Interview")
    print(f"\nResult for 'Interview': {result2}")
    
    # Test with "formal" for comparison
    result3 = get_occasion_rule("formal")
    print(f"\nResult for 'formal': {result3}")

if __name__ == "__main__":
    debug_occasion_rule() 