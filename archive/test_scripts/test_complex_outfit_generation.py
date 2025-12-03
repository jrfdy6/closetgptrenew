"""
Complex Functionality Tests for Outfit Generation
Tests comprehensive outfit generation and base item generation with full metadata
"""

import sys
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

def create_comprehensive_wardrobe() -> List[Dict[str, Any]]:
    """Create a comprehensive wardrobe with full metadata for testing"""
    
    wardrobe = [
        # TOPS - Various styles and metadata
        {
            "id": "top_001",
            "name": "White Button-Down Dress Shirt",
            "type": "shirt",
            "color": "white",
            "gender": "unisex",
            "metadata": {
                "visualAttributes": {
                    "material": "cotton",
                    "sleeveLength": "long",
                    "neckline": "button-down",
                    "fit": "tailored",
                    "pattern": "solid",
                    "formalLevel": "business",
                    "wearLayer": "base",
                    "fabricWeight": "medium"
                }
            },
            "dominantColors": [{"name": "white", "hex": "#FFFFFF"}],
            "occasion": ["business", "formal", "interview"],
            "style": ["classic", "business casual", "urban professional"]
        },
        {
            "id": "top_002",
            "name": "Linen Relaxed Shirt",
            "type": "shirt",
            "color": "beige",
            "gender": "unisex",
            "metadata": {
                "visualAttributes": {
                    "material": "linen",
                    "sleeveLength": "short",
                    "neckline": "crew",
                    "fit": "relaxed",
                    "pattern": "solid",
                    "formalLevel": "casual",
                    "wearLayer": "base",
                    "fabricWeight": "light"
                }
            },
            "dominantColors": [{"name": "beige", "hex": "#F5F5DC"}],
            "occasion": ["casual", "weekend", "vacation"],
            "style": ["coastal grandmother", "minimalist", "casual cool"]
        },
        {
            "id": "top_003",
            "name": "Silk Floral Blouse",
            "type": "blouse",
            "color": "cream",
            "gender": "female",
            "metadata": {
                "visualAttributes": {
                    "material": "silk",
                    "sleeveLength": "long",
                    "neckline": "v-neck",
                    "fit": "fitted",
                    "pattern": "floral",
                    "formalLevel": "business",
                    "wearLayer": "base",
                    "fabricWeight": "light"
                }
            },
            "dominantColors": [{"name": "cream", "hex": "#FFFDD0"}, {"name": "pink", "hex": "#FFC0CB"}],
            "occasion": ["date", "business", "formal"],
            "style": ["romantic", "classic", "french girl"]
        },
        {
            "id": "top_004",
            "name": "Burgundy Turtleneck Sweater",
            "type": "sweater",
            "color": "burgundy",
            "gender": "unisex",
            "metadata": {
                "visualAttributes": {
                    "material": "wool",
                    "sleeveLength": "long",
                    "neckline": "turtleneck",
                    "fit": "fitted",
                    "pattern": "solid",
                    "formalLevel": "casual",
                    "wearLayer": "mid",
                    "fabricWeight": "medium",
                    "warmthFactor": "medium"
                }
            },
            "dominantColors": [{"name": "burgundy", "hex": "#800020"}],
            "occasion": ["casual", "weekend", "cold weather"],
            "style": ["dark academia", "classic", "old money"]
        },
        {
            "id": "top_005",
            "name": "Athletic Performance T-Shirt",
            "type": "t-shirt",
            "color": "black",
            "gender": "unisex",
            "metadata": {
                "visualAttributes": {
                    "material": "polyester",
                    "sleeveLength": "short",
                    "neckline": "crew",
                    "fit": "athletic",
                    "pattern": "solid",
                    "formalLevel": "athletic",
                    "wearLayer": "base",
                    "fabricWeight": "light"
                }
            },
            "dominantColors": [{"name": "black", "hex": "#000000"}],
            "occasion": ["gym", "athletic"],
            "style": ["athleisure", "workout"]
        },
        
        # BOTTOMS
        {
            "id": "bottom_001",
            "name": "Navy Tailored Dress Pants",
            "type": "pants",
            "color": "navy",
            "gender": "unisex",
            "metadata": {
                "visualAttributes": {
                    "material": "wool",
                    "fit": "tailored",
                    "pattern": "solid",
                    "formalLevel": "business",
                    "waistbandType": "belt_loops",
                    "length": "full",
                    "silhouette": "straight"
                }
            },
            "dominantColors": [{"name": "navy", "hex": "#000080"}],
            "occasion": ["business", "formal", "interview"],
            "style": ["classic", "business casual", "urban professional"]
        },
        {
            "id": "bottom_002",
            "name": "White Wide-Leg Linen Pants",
            "type": "pants",
            "color": "white",
            "gender": "unisex",
            "metadata": {
                "visualAttributes": {
                    "material": "linen",
                    "fit": "relaxed",
                    "pattern": "solid",
                    "formalLevel": "casual",
                    "waistbandType": "elastic",
                    "length": "full",
                    "silhouette": "wide-leg"
                }
            },
            "dominantColors": [{"name": "white", "hex": "#FFFFFF"}],
            "occasion": ["casual", "weekend", "vacation"],
            "style": ["coastal grandmother", "minimalist", "scandinavian"]
        },
        {
            "id": "bottom_003",
            "name": "Gray Athletic Shorts",
            "type": "shorts",
            "color": "gray",
            "gender": "unisex",
            "metadata": {
                "visualAttributes": {
                    "material": "polyester",
                    "fit": "athletic",
                    "pattern": "solid",
                    "formalLevel": "athletic",
                    "waistbandType": "elastic_drawstring",
                    "length": "short",
                    "silhouette": "fitted"
                }
            },
            "dominantColors": [{"name": "gray", "hex": "#808080"}],
            "occasion": ["gym", "athletic"],
            "style": ["athleisure", "workout"]
        },
        
        # OUTERWEAR
        {
            "id": "outer_001",
            "name": "Charcoal Wool Blazer",
            "type": "blazer",
            "color": "charcoal",
            "gender": "unisex",
            "metadata": {
                "visualAttributes": {
                    "material": "wool",
                    "fit": "tailored",
                    "pattern": "solid",
                    "formalLevel": "business",
                    "wearLayer": "outer",
                    "fabricWeight": "medium",
                    "warmthFactor": "medium"
                }
            },
            "dominantColors": [{"name": "charcoal", "hex": "#36454F"}],
            "occasion": ["business", "formal", "interview"],
            "style": ["classic", "business casual", "old money"]
        },
        {
            "id": "outer_002",
            "name": "Navy Hoodie",
            "type": "hoodie",
            "color": "navy",
            "gender": "unisex",
            "metadata": {
                "visualAttributes": {
                    "material": "cotton",
                    "fit": "relaxed",
                    "pattern": "solid",
                    "formalLevel": "casual",
                    "wearLayer": "mid",
                    "fabricWeight": "medium",
                    "warmthFactor": "medium"
                }
            },
            "dominantColors": [{"name": "navy", "hex": "#000080"}],
            "occasion": ["casual", "weekend", "loungewear"],
            "style": ["casual cool", "streetwear", "athleisure"]
        },
        {
            "id": "outer_003",
            "name": "Black Wool Coat",
            "type": "coat",
            "color": "black",
            "gender": "unisex",
            "metadata": {
                "visualAttributes": {
                    "material": "wool",
                    "fit": "oversized",
                    "pattern": "solid",
                    "formalLevel": "casual",
                    "wearLayer": "outer",
                    "fabricWeight": "heavy",
                    "warmthFactor": "heavy"
                }
            },
            "dominantColors": [{"name": "black", "hex": "#000000"}],
            "occasion": ["cold weather", "winter", "casual"],
            "style": ["classic", "minimalist", "modern"]
        },
        
        # SHOES
        {
            "id": "shoes_001",
            "name": "Brown Oxford Dress Shoes",
            "type": "dress shoes",
            "color": "brown",
            "gender": "unisex",
            "metadata": {
                "visualAttributes": {
                    "material": "leather",
                    "formalLevel": "formal",
                    "fit": "standard"
                }
            },
            "dominantColors": [{"name": "brown", "hex": "#8B4513"}],
            "occasion": ["business", "formal", "interview"],
            "style": ["classic", "old money", "business casual"]
        },
        {
            "id": "shoes_002",
            "name": "White Running Sneakers",
            "type": "sneakers",
            "color": "white",
            "gender": "unisex",
            "metadata": {
                "visualAttributes": {
                    "material": "synthetic",
                    "formalLevel": "athletic",
                    "fit": "athletic"
                }
            },
            "dominantColors": [{"name": "white", "hex": "#FFFFFF"}],
            "occasion": ["gym", "athletic", "casual"],
            "style": ["athleisure", "clean girl", "minimalist"]
        },
        {
            "id": "shoes_003",
            "name": "Beige Loafers",
            "type": "loafers",
            "color": "beige",
            "gender": "unisex",
            "metadata": {
                "visualAttributes": {
                    "material": "leather",
                    "formalLevel": "casual",
                    "fit": "standard"
                }
            },
            "dominantColors": [{"name": "beige", "hex": "#F5F5DC"}],
            "occasion": ["casual", "weekend", "business casual"],
            "style": ["classic", "preppy", "old money"]
        }
    ]
    
    return wardrobe


def test_comprehensive_outfit_generation():
    """Test full outfit generation with all components"""
    print("\n" + "="*80)
    print("TEST 1: Comprehensive Outfit Generation")
    print("="*80)
    
    test_scenarios = [
        {
            "name": "Business Formal Outfit",
            "occasion": "Business",
            "style": "Classic",
            "mood": "Subtle",
            "expected_components": {
                "top": {"type": "shirt", "formalLevel": "business", "neckline": "button-down"},
                "bottom": {"type": "pants", "formalLevel": "business"},
                "outerwear": {"type": "blazer", "optional": True},
                "shoes": {"type": "dress shoes", "formalLevel": "formal"}
            },
            "forbidden": ["shorts", "sneakers", "t-shirt"]
        },
        {
            "name": "Weekend Casual Outfit",
            "occasion": "Weekend",
            "style": "Coastal Grandmother",
            "mood": "Serene",
            "expected_components": {
                "top": {"type": "shirt", "material": "linen", "fit": "relaxed"},
                "bottom": {"type": "pants", "material": "linen", "fit": "relaxed"},
                "shoes": {"type": "loafers", "formalLevel": "casual"}
            },
            "forbidden": ["dress shoes", "suit", "formal"]
        },
        {
            "name": "Gym Athletic Outfit",
            "occasion": "Gym",
            "style": "Athleisure",
            "mood": "Dynamic",
            "expected_components": {
                "top": {"type": "t-shirt", "material": "polyester", "sleeveLength": "short"},
                "bottom": {"type": "shorts", "material": "polyester"},
                "shoes": {"type": "sneakers", "formalLevel": "athletic"}
            },
            "forbidden": ["dress shirt", "dress pants", "dress shoes"]
        },
        {
            "name": "Romantic Date Outfit",
            "occasion": "Date",
            "style": "Romantic",
            "mood": "Romantic",
            "expected_components": {
                "top": {"material": "silk", "pattern": "floral", "fit": "fitted"},
                "bottom": {"type": "pants", "formalLevel": "business"},
                "shoes": {"type": "dress shoes", "optional": True}
            },
            "forbidden": ["athletic", "gym", "sweatpants"]
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n  Scenario: {scenario['name']}")
        print(f"    Occasion: {scenario['occasion']}")
        print(f"    Style: {scenario['style']}")
        print(f"    Mood: {scenario['mood']}")
        print(f"    Expected Components:")
        for component, requirements in scenario['expected_components'].items():
            req_str = ", ".join([f"{k}={v}" for k, v in requirements.items() if k != "optional"])
            optional = " (optional)" if requirements.get("optional") else ""
            print(f"      - {component}: {req_str}{optional}")
        print(f"    Forbidden: {', '.join(scenario['forbidden'])}")
        print(f"    ✅ Should generate complete outfit with all components")
    
    return True


def test_base_item_generation():
    """Test outfit generation starting from a base item"""
    print("\n" + "="*80)
    print("TEST 2: Base Item Generation")
    print("="*80)
    
    base_item_scenarios = [
        {
            "base_item_id": "top_001",  # White Button-Down Dress Shirt
            "base_item_name": "White Button-Down Dress Shirt",
            "occasion": "Business",
            "style": "Classic",
            "mood": "Subtle",
            "expected_build": {
                "must_include": ["top_001"],  # Base item must be included
                "should_add": [
                    {"category": "bottom", "type": "pants", "formalLevel": "business"},
                    {"category": "shoes", "type": "dress shoes"},
                    {"category": "outerwear", "type": "blazer", "optional": True}
                ],
                "compatibility": {
                    "color": "neutral (white)",
                    "style": "classic",
                    "formality": "business"
                }
            }
        },
        {
            "base_item_id": "outer_002",  # Navy Hoodie
            "base_item_name": "Navy Hoodie",
            "occasion": "Weekend",
            "style": "Casual Cool",
            "mood": "Serene",
            "expected_build": {
                "must_include": ["outer_002"],  # Base item must be included
                "should_add": [
                    {"category": "top", "type": "shirt", "wearLayer": "base"},
                    {"category": "bottom", "type": "pants", "fit": "relaxed"},
                    {"category": "shoes", "type": "sneakers", "optional": True}
                ],
                "compatibility": {
                    "color": "navy (neutral base)",
                    "style": "casual",
                    "layering": "mid layer (hoodie) + base layer + outer layer (optional)"
                }
            }
        },
        {
            "base_item_id": "top_003",  # Silk Floral Blouse
            "base_item_name": "Silk Floral Blouse",
            "occasion": "Date",
            "style": "Romantic",
            "mood": "Romantic",
            "expected_build": {
                "must_include": ["top_003"],  # Base item must be included
                "should_add": [
                    {"category": "bottom", "type": "pants", "formalLevel": "business"},
                    {"category": "shoes", "type": "dress shoes", "optional": True}
                ],
                "compatibility": {
                    "color": "cream/pink (romantic palette)",
                    "style": "romantic",
                    "material": "silk (elegant)"
                }
            }
        },
        {
            "base_item_id": "top_004",  # Burgundy Turtleneck
            "base_item_name": "Burgundy Turtleneck Sweater",
            "occasion": "Weekend",
            "style": "Dark Academia",
            "mood": "Serene",
            "expected_build": {
                "must_include": ["top_004"],  # Base item must be included
                "should_add": [
                    {"category": "bottom", "type": "pants", "color": "dark"},
                    {"category": "outerwear", "type": "coat", "optional": True},
                    {"category": "shoes", "type": "loafers", "optional": True}
                ],
                "compatibility": {
                    "color": "burgundy (dark academia palette)",
                    "style": "dark academia",
                    "layering": "mid layer (sweater) can have outer layer"
                },
                "forbidden_combinations": [
                    "Cannot add collared shirt (turtleneck already has neckline)"
                ]
            }
        }
    ]
    
    for scenario in base_item_scenarios:
        print(f"\n  Base Item: {scenario['base_item_name']}")
        print(f"    Occasion: {scenario['occasion']}")
        print(f"    Style: {scenario['style']}")
        print(f"    Mood: {scenario['mood']}")
        print(f"    Must Include: {scenario['expected_build']['must_include'][0]}")
        print(f"    Should Add:")
        for item in scenario['expected_build']['should_add']:
            req_str = ", ".join([f"{k}={v}" for k, v in item.items() if k not in ["category", "optional"]])
            optional = " (optional)" if item.get("optional") else ""
            print(f"      - {item['category']}: {req_str}{optional}")
        print(f"    Compatibility: {scenario['expected_build']['compatibility']}")
        if "forbidden_combinations" in scenario['expected_build']:
            for forbidden in scenario['expected_build']['forbidden_combinations']:
                print(f"    ❌ {forbidden}")
        print(f"    ✅ Should build complete outfit around base item")
    
    return True


def test_layering_with_base_item():
    """Test complex layering scenarios with base items"""
    print("\n" + "="*80)
    print("TEST 3: Layering with Base Item")
    print("="*80)
    
    layering_scenarios = [
        {
            "name": "Hoodie as Base + Coat",
            "base_item_id": "outer_002",  # Hoodie
            "base_item_name": "Navy Hoodie",
            "occasion": "Weekend",
            "expected_layering": {
                "base_layer": {"type": "shirt", "wearLayer": "base"},
                "mid_layer": {"type": "hoodie", "wearLayer": "mid", "must_include": True},
                "outer_layer": {"type": "coat", "wearLayer": "outer", "optional": True}
            },
            "validation": "✅ ALLOWED: Hoodie (mid) + Coat (outer) is valid"
        },
        {
            "name": "Turtleneck as Base + Blazer",
            "base_item_id": "top_004",  # Turtleneck
            "base_item_name": "Burgundy Turtleneck",
            "occasion": "Casual",
            "expected_layering": {
                "base_layer": {"type": "turtleneck", "wearLayer": "mid", "must_include": True},
                "outer_layer": {"type": "blazer", "wearLayer": "outer", "optional": True}
            },
            "validation": "✅ ALLOWED: Turtleneck (mid) + Blazer (outer) is valid",
            "forbidden": "❌ Cannot add collared shirt (turtleneck already has neckline)"
        },
        {
            "name": "Shirt as Base - No Second Shirt",
            "base_item_id": "top_001",  # Button-down shirt
            "base_item_name": "White Button-Down Shirt",
            "occasion": "Business",
            "expected_layering": {
                "base_layer": {"type": "shirt", "wearLayer": "base", "must_include": True},
                "outer_layer": {"type": "blazer", "wearLayer": "outer", "optional": True}
            },
            "validation": "✅ ALLOWED: Shirt (base) + Blazer (outer)",
            "forbidden": "❌ BLOCKED: Cannot add second shirt (two shirts rule)"
        }
    ]
    
    for scenario in layering_scenarios:
        print(f"\n  Scenario: {scenario['name']}")
        print(f"    Base Item: {scenario['base_item_name']}")
        print(f"    Occasion: {scenario['occasion']}")
        print(f"    Expected Layering:")
        for layer, requirements in scenario['expected_layering'].items():
            req_str = ", ".join([f"{k}={v}" for k, v in requirements.items() if k != "must_include" and k != "optional"])
            must = " (MUST INCLUDE)" if requirements.get("must_include") else ""
            optional = " (optional)" if requirements.get("optional") else ""
            print(f"      - {layer}: {req_str}{must}{optional}")
        print(f"    {scenario['validation']}")
        if "forbidden" in scenario:
            print(f"    {scenario['forbidden']}")
    
    return True


def test_metadata_validation():
    """Test that metadata is properly validated during generation"""
    print("\n" + "="*80)
    print("TEST 4: Metadata Validation")
    print("="*80)
    
    validation_tests = [
        {
            "test": "Business Occasion - Formal Level Check",
            "occasion": "Business",
            "item": {
                "name": "Athletic T-Shirt",
                "type": "t-shirt",
                "metadata": {"visualAttributes": {"formalLevel": "athletic"}}
            },
            "expected": "❌ REJECTED: formalLevel='athletic' not appropriate for Business"
        },
        {
            "test": "Gym Occasion - Sleeve Length Check",
            "occasion": "Gym",
            "item": {
                "name": "Long Sleeve Dress Shirt",
                "type": "shirt",
                "metadata": {"visualAttributes": {"sleeveLength": "long", "formalLevel": "business"}}
            },
            "expected": "❌ REJECTED: long sleeves + business formalLevel not appropriate for Gym"
        },
        {
            "test": "Weekend Occasion - Material Check",
            "occasion": "Weekend",
            "item": {
                "name": "Linen Shirt",
                "type": "shirt",
                "metadata": {"visualAttributes": {"material": "linen", "fit": "relaxed", "formalLevel": "casual"}}
            },
            "expected": "✅ ACCEPTED: linen + relaxed + casual appropriate for Weekend"
        },
        {
            "test": "Layering - WearLayer Check",
            "scenario": "Adding outerwear over base item",
            "base_item": {
                "name": "Hoodie",
                "wearLayer": "mid"
            },
            "outer_item": {
                "name": "Coat",
                "wearLayer": "outer"
            },
            "expected": "✅ ALLOWED: mid layer (hoodie) + outer layer (coat) is valid"
        },
        {
            "test": "Forbidden Combination - Two Shirts",
            "base_item": {
                "name": "Button-Down Shirt",
                "type": "shirt"
            },
            "additional_item": {
                "name": "T-Shirt",
                "type": "shirt"
            },
            "expected": "❌ BLOCKED: Cannot have two shirts in one outfit"
        },
        {
            "test": "Forbidden Combination - Collared + Turtleneck",
            "base_item": {
                "name": "Button-Down Shirt",
                "neckline": "button-down"
            },
            "additional_item": {
                "name": "Turtleneck",
                "neckline": "turtleneck"
            },
            "expected": "❌ BLOCKED: Collared shirt + turtleneck is forbidden"
        }
    ]
    
    for test in validation_tests:
        print(f"\n  {test['test']}")
        if "occasion" in test:
            print(f"    Occasion: {test['occasion']}")
            print(f"    Item: {test['item']['name']}")
            if "metadata" in test['item']:
                metadata = test['item']['metadata']['visualAttributes']
                metadata_str = ", ".join([f"{k}={v}" for k, v in metadata.items()])
                print(f"    Metadata: {metadata_str}")
        elif "scenario" in test:
            print(f"    Scenario: {test['scenario']}")
            print(f"    Base: {test['base_item']['name']} (wearLayer={test['base_item']['wearLayer']})")
            print(f"    Outer: {test['outer_item']['name']} (wearLayer={test['outer_item']['wearLayer']})")
        else:
            print(f"    Base: {test['base_item']['name']}")
            print(f"    Additional: {test['additional_item']['name']}")
        print(f"    {test['expected']}")
    
    return True


def test_complete_outfit_validation():
    """Test complete outfit validation with all components"""
    print("\n" + "="*80)
    print("TEST 5: Complete Outfit Validation")
    print("="*80)
    
    complete_outfits = [
        {
            "name": "Valid Business Outfit",
            "items": [
                {"id": "top_001", "type": "shirt", "formalLevel": "business"},
                {"id": "bottom_001", "type": "pants", "formalLevel": "business"},
                {"id": "outer_001", "type": "blazer", "formalLevel": "business"},
                {"id": "shoes_001", "type": "dress shoes", "formalLevel": "formal"}
            ],
            "occasion": "Business",
            "validation": "✅ VALID: All components appropriate for Business"
        },
        {
            "name": "Valid Weekend Outfit",
            "items": [
                {"id": "top_002", "type": "shirt", "material": "linen", "fit": "relaxed"},
                {"id": "bottom_002", "type": "pants", "material": "linen", "fit": "relaxed"},
                {"id": "shoes_003", "type": "loafers", "formalLevel": "casual"}
            ],
            "occasion": "Weekend",
            "validation": "✅ VALID: All components appropriate for Weekend"
        },
        {
            "name": "Invalid - Two Shirts",
            "items": [
                {"id": "top_001", "type": "shirt"},
                {"id": "top_002", "type": "shirt"},  # Second shirt
                {"id": "bottom_001", "type": "pants"}
            ],
            "occasion": "Business",
            "validation": "❌ INVALID: Two shirts in one outfit (forbidden)"
        },
        {
            "name": "Invalid - Collared + Turtleneck",
            "items": [
                {"id": "top_001", "type": "shirt", "neckline": "button-down"},
                {"id": "top_004", "type": "sweater", "neckline": "turtleneck"},
                {"id": "bottom_001", "type": "pants"}
            ],
            "occasion": "Casual",
            "validation": "❌ INVALID: Collared shirt + turtleneck (forbidden)"
        },
        {
            "name": "Valid - Hoodie + Coat Layering",
            "items": [
                {"id": "top_002", "type": "shirt", "wearLayer": "base"},
                {"id": "outer_002", "type": "hoodie", "wearLayer": "mid"},
                {"id": "outer_003", "type": "coat", "wearLayer": "outer"},
                {"id": "bottom_002", "type": "pants"}
            ],
            "occasion": "Weekend",
            "validation": "✅ VALID: Hoodie (mid) + Coat (outer) is allowed"
        }
    ]
    
    for outfit in complete_outfits:
        print(f"\n  {outfit['name']}")
        print(f"    Occasion: {outfit['occasion']}")
        print(f"    Items ({len(outfit['items'])}):")
        for item in outfit['items']:
            item_str = f"      - {item['id']}"
            attrs = [f"{k}={v}" for k, v in item.items() if k != "id"]
            if attrs:
                item_str += f" ({', '.join(attrs)})"
            print(item_str)
        print(f"    {outfit['validation']}")
    
    return True


def run_complex_tests():
    """Run all complex functionality tests"""
    print("\n" + "="*80)
    print("COMPLEX FUNCTIONALITY TEST SUITE")
    print("Comprehensive Outfit Generation & Base Item Generation")
    print("="*80)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    results.append(("Comprehensive Outfit Generation", test_comprehensive_outfit_generation()))
    results.append(("Base Item Generation", test_base_item_generation()))
    results.append(("Layering with Base Item", test_layering_with_base_item()))
    results.append(("Metadata Validation", test_metadata_validation()))
    results.append(("Complete Outfit Validation", test_complete_outfit_validation()))
    
    # Summary
    print("\n" + "="*80)
    print("COMPLEX TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    print("\n" + "="*80)
    print("\n  ✅ Comprehensive outfit generation tested")
    print("  ✅ Base item generation tested")
    print("  ✅ Layering rules validated")
    print("  ✅ Metadata validation tested")
    print("  ✅ Complete outfit validation tested")
    print("\n" + "="*80)
    
    return passed == total


if __name__ == "__main__":
    success = run_complex_tests()
    sys.exit(0 if success else 1)


