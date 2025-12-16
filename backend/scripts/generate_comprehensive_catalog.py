#!/usr/bin/env python3
"""
Generate a comprehensive style inspiration catalog that fills all gaps
Covers all gender, style preference, and persona combinations
"""

import json
import random
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# All style personas mapped to catalog style names
PERSONA_TO_STYLE = {
    "architect": ["Minimalist", "Classic"],
    "strategist": ["Urban Street", "Classic", "Preppy"],
    "innovator": ["Avant-Garde", "Y2K", "Urban Street"],
    "classic": ["Classic", "Old Money", "Preppy"],
    "wanderer": ["Boho", "Classic"],
    "rebel": ["Urban Street", "Avant-Garde", "Y2K"],
    "connoisseur": ["Old Money", "Classic", "Preppy"],
    "modernist": ["Minimalist", "Avant-Garde", "Urban Street"]
}

# Style personas with their characteristics (enhanced)
STYLE_PERSONAS = {
    "Old Money": {
        "keywords": ["luxury", "heritage", "timeless", "refined", "polished", "classic", "elegant"],
        "materials": ["cashmere", "wool", "silk", "leather", "cotton", "linen"],
        "colors": ["camel", "navy", "grey", "cream", "burgundy", "forest green", "tan"],
        "price_multiplier": 2.5,
        "genders": ["male", "female", "unisex"]
    },
    "Urban Street": {
        "keywords": ["streetwear", "casual", "edgy", "modern", "utility", "relaxed", "cool"],
        "materials": ["cotton", "nylon", "polyester", "denim", "canvas"],
        "colors": ["black", "white", "olive", "grey", "charcoal", "khaki"],
        "price_multiplier": 1.2,
        "genders": ["male", "female", "unisex"]
    },
    "Minimalist": {
        "keywords": ["clean", "simple", "sleek", "modern", "understated", "versatile"],
        "materials": ["cotton", "wool", "linen", "jersey", "silk"],
        "colors": ["black", "white", "grey", "beige", "navy", "cream"],
        "price_multiplier": 1.5,
        "genders": ["male", "female", "unisex"]
    },
    "Preppy": {
        "keywords": ["collegiate", "classic", "polished", "crisp", "traditional"],
        "materials": ["cotton", "wool", "oxford cloth", "chino"],
        "colors": ["navy", "white", "burgundy", "kelly green", "khaki", "pink"],
        "price_multiplier": 1.8,
        "genders": ["male", "female", "unisex"]
    },
    "Boho": {
        "keywords": ["bohemian", "relaxed", "artistic", "free-spirited", "earthy", "flowing"],
        "materials": ["cotton", "linen", "rayon", "silk", "crochet"],
        "colors": ["rust", "mustard", "terracotta", "olive", "cream", "burnt orange"],
        "price_multiplier": 1.3,
        "genders": ["male", "female", "unisex"]
    },
    "Y2K": {
        "keywords": ["retro", "playful", "bold", "nostalgic", "trendy", "statement"],
        "materials": ["polyester", "nylon", "vinyl", "mesh", "metallic"],
        "colors": ["pink", "purple", "silver", "neon", "bright blue", "lime"],
        "price_multiplier": 1.0,
        "genders": ["male", "female", "unisex"]
    },
    "Avant-Garde": {
        "keywords": ["experimental", "architectural", "artistic", "unconventional", "bold"],
        "materials": ["wool", "leather", "technical fabrics", "structured cotton"],
        "colors": ["black", "white", "charcoal", "deep red", "midnight blue"],
        "price_multiplier": 3.0,
        "genders": ["male", "female", "unisex"]
    },
    "Classic": {
        "keywords": ["timeless", "traditional", "versatile", "refined", "essential"],
        "materials": ["cotton", "wool", "silk", "leather", "denim"],
        "colors": ["navy", "white", "black", "grey", "tan", "brown"],
        "price_multiplier": 1.6,
        "genders": ["male", "female", "unisex"]
    }
}

# Item categories with gender-specific types
ITEM_CATEGORIES = {
    "tops": {
        "types": {
            "male": ["T-Shirt", "Polo Shirt", "Button-Down Shirt", "Sweater", "Cardigan", 
                    "Hoodie", "Sweatshirt", "Turtleneck", "Henley", "Tank Top"],
            "female": ["T-Shirt", "Tank Top", "Blouse", "Sweater", "Cardigan", 
                      "Crop Top", "Tube Top", "Camisole", "Halter Top", "Turtleneck"],
            "unisex": ["T-Shirt", "Hoodie", "Sweatshirt", "Sweater", "Cardigan"]
        },
        "base_price": 35,
        "silhouettes": ["fitted", "relaxed", "oversized", "slim", "regular"],
        "temp_range": (15, 28)
    },
    "bottoms": {
        "types": {
            "male": ["Jeans", "Chinos", "Trousers", "Shorts", "Cargo Pants", 
                    "Wide-Leg Pants", "Joggers"],
            "female": ["Jeans", "Chinos", "Trousers", "Shorts", "Wide-Leg Pants", 
                      "Leggings", "Culottes", "Palazzo Pants", "Skirt", "Midi Skirt", 
                      "Mini Skirt", "Pencil Skirt", "A-Line Skirt"],
            "unisex": ["Jeans", "Shorts", "Joggers", "Wide-Leg Pants"]
        },
        "base_price": 60,
        "silhouettes": ["slim", "regular", "wide", "tapered", "relaxed"],
        "temp_range": (10, 30)
    },
    "outerwear": {
        "types": {
            "male": ["Coat", "Trench Coat", "Peacoat", "Parka", "Blazer",
                    "Leather Jacket", "Denim Jacket", "Bomber Jacket", "Varsity Jacket",
                    "Puffer Jacket", "Cardigan", "Sweater Coat"],
            "female": ["Coat", "Trench Coat", "Peacoat", "Parka", "Blazer",
                      "Leather Jacket", "Denim Jacket", "Bomber Jacket", "Puffer Jacket",
                      "Cardigan", "Cape", "Kimono"],
            "unisex": ["Coat", "Parka", "Denim Jacket", "Bomber Jacket", "Puffer Jacket"]
        },
        "base_price": 120,
        "silhouettes": ["fitted", "oversized", "structured", "relaxed"],
        "temp_range": (-10, 20)
    },
    "footwear": {
        "types": {
            "male": ["Sneakers", "Loafers", "Boots", "Chelsea Boots", "Combat Boots",
                    "Oxfords", "Slides", "Ankle Boots"],
            "female": ["Sneakers", "Boots", "Chelsea Boots", "Combat Boots",
                      "Sandals", "Heels", "Flats", "Mules", "Platforms", "Wedges",
                      "Ankle Boots", "Knee-High Boots"],
            "unisex": ["Sneakers", "Boots", "Chelsea Boots", "Slides"]
        },
        "base_price": 80,
        "silhouettes": ["sleek", "chunky", "minimalist", "statement"],
        "temp_range": (5, 35)
    },
    "dresses": {
        "types": {
            "female": ["Midi Dress", "Maxi Dress", "Mini Dress", "Shift Dress", "Wrap Dress",
                      "Shirt Dress", "Slip Dress", "A-Line Dress", "Bodycon Dress",
                      "T-Shirt Dress", "Sweater Dress", "Cocktail Dress"],
            "unisex": ["T-Shirt Dress", "Shirt Dress"]  # Minimal unisex dress options
        },
        "base_price": 90,
        "silhouettes": ["fitted", "flowy", "structured", "relaxed"],
        "temp_range": (15, 30)
    },
    "accessories": {
        "types": {
            "male": ["Belt", "Scarf", "Hat", "Beanie", "Baseball Cap",
                    "Sunglasses", "Watch", "Bag", "Backpack", "Tote", "Crossbody"],
            "female": ["Belt", "Scarf", "Hat", "Beanie", "Baseball Cap",
                      "Sunglasses", "Watch", "Necklace", "Earrings", "Bracelet",
                      "Bag", "Backpack", "Tote", "Crossbody", "Clutch"],
            "unisex": ["Belt", "Scarf", "Hat", "Beanie", "Baseball Cap",
                      "Sunglasses", "Watch", "Bag", "Backpack", "Tote"]
        },
        "base_price": 40,
        "silhouettes": ["minimalist", "statement", "classic", "bold"],
        "temp_range": (-10, 40)
    }
}

BRANDS = {
    "luxury": ["Loro Piana", "Brunello Cucinelli", "The Row", "Max Mara", "Saint Laurent"],
    "premium": ["Theory", "Equipment", "APC", "Acne Studios", "Common Projects"],
    "mid": ["COS", "Everlane", "Madewell", "J.Crew", "Banana Republic"],
    "accessible": ["Uniqlo", "H&M", "Zara", "Gap", "Old Navy"]
}

SEASONS = ["spring", "summer", "fall", "winter"]
GENDERS = ["male", "female", "unisex"]

def generate_style_vector(primary_style: str, secondary_styles: List[str] = None) -> Dict[str, float]:
    """Generate a style vector with primary and optional secondary styles"""
    vector = {style: 0.0 for style in STYLE_PERSONAS.keys()}
    
    # Primary style gets high score
    vector[primary_style] = random.uniform(0.75, 0.95)
    
    # Secondary styles get medium scores
    if secondary_styles:
        for style in secondary_styles:
            if style in vector:
                vector[style] = random.uniform(0.35, 0.65)
    
    # Add small random values to other styles
    for style in vector.keys():
        if style != primary_style and style not in (secondary_styles or []):
            vector[style] = random.uniform(0.05, 0.25)
    
    return vector

def calculate_weather_properties(category: str, materials: List[str], season: List[str]) -> Dict[str, Any]:
    """Calculate weather-related properties based on materials and season"""
    
    thermal_map = {
        "wool": 0.85, "cashmere": 0.90, "down": 0.95, "fleece": 0.80,
        "cotton": 0.50, "linen": 0.20, "silk": 0.40, "polyester": 0.55,
        "nylon": 0.60, "leather": 0.70, "denim": 0.60
    }
    
    water_map = {
        "leather": 0.5, "nylon": 0.7, "polyester": 0.6, "wool": 0.3,
        "cotton": 0.2, "down": 0.8, "wax": 0.9
    }
    
    thermal_scores = [thermal_map.get(mat.lower(), 0.5) for mat in materials]
    thermal_score = sum(thermal_scores) / len(thermal_scores) if thermal_scores else 0.5
    
    water_scores = [water_map.get(mat.lower(), 0.1) for mat in materials]
    water_resistance = sum(water_scores) / len(water_scores) if water_scores else 0.1
    
    wind_resistance = 0.7 if category == "outerwear" else 0.3
    
    if "winter" in season:
        temp_min, temp_max = -10, 15
    elif "fall" in season or "spring" in season:
        temp_min, temp_max = 5, 22
    elif "summer" in season:
        temp_min, temp_max = 18, 35
    else:
        temp_min, temp_max = 0, 30
    
    weather_tags = []
    if thermal_score > 0.7:
        weather_tags.append("insulating")
    if water_resistance > 0.5:
        weather_tags.append("water_resistant")
    if wind_resistance > 0.5:
        weather_tags.append("wind_resistant")
    if thermal_score < 0.3:
        weather_tags.append("breathable")
    
    return {
        "material_thermal_score": round(thermal_score, 2),
        "water_resistance": round(water_resistance, 2),
        "wind_resistance": round(wind_resistance, 2),
        "temp_min_c": temp_min,
        "temp_max_c": temp_max,
        "weather_tags": weather_tags
    }

def generate_item(item_id: int, primary_style: str, category: str, gender: str) -> Dict[str, Any]:
    """Generate a single catalog item with gender specification"""
    
    style_info = STYLE_PERSONAS[primary_style]
    category_info = ITEM_CATEGORIES[category]
    
    # Get gender-specific item types
    if gender not in category_info["types"]:
        # Fallback to unisex if gender-specific types don't exist
        gender = "unisex"
    
    available_types = category_info["types"].get(gender, category_info["types"].get("unisex", []))
    if not available_types:
        # Skip categories that don't have types for this gender (e.g., dresses for male)
        return None
    
    # Select secondary styles (sometimes)
    secondary_styles = []
    if random.random() > 0.6:
        available = [s for s in STYLE_PERSONAS.keys() if s != primary_style]
        secondary_styles = random.sample(available, random.randint(1, 2))
    
    # Item type
    item_type = random.choice(available_types)
    
    # Materials (1-2 from style persona)
    materials = random.sample(style_info["materials"], min(random.randint(1, 2), len(style_info["materials"])))
    
    # Color
    color = random.choice(style_info["colors"])
    
    # Silhouette
    silhouette = random.choice(category_info["silhouettes"])
    
    # Season (1-2 seasons)
    seasons = random.sample(SEASONS, random.randint(1, 2))
    
    # Price tier and brand
    rand = random.random()
    if rand > 0.9:
        price_tier = "luxury"
    elif rand > 0.6:
        price_tier = "premium"
    elif rand > 0.3:
        price_tier = "mid"
    else:
        price_tier = "accessible"
    
    brand = random.choice(BRANDS[price_tier])
    
    # Calculate price
    base_price = category_info["base_price"]
    tier_multiplier = {"luxury": 5.0, "premium": 2.5, "mid": 1.0, "accessible": 0.5}[price_tier]
    style_multiplier = style_info["price_multiplier"]
    final_price = int(base_price * tier_multiplier * style_multiplier * random.uniform(0.8, 1.2))
    
    # Tags from style keywords
    tags = random.sample(style_info["keywords"], min(random.randint(2, 4), len(style_info["keywords"])))
    
    # Weather properties
    weather_props = calculate_weather_properties(category, materials, seasons)
    
    # Trend score
    trend_score = 0.2 if "timeless" in tags or "classic" in tags else random.uniform(0.4, 0.8)
    
    # Generate style vector
    style_vector = generate_style_vector(primary_style, secondary_styles)
    
    # Image URL (using pollinations.ai with relevant search terms)
    image_search = f"{item_type.lower().replace(' ', '-')}-{color.replace(' ', '-')}-{gender}"
    image_url = f"https://image.pollinations.ai/prompt/professional%20product%20photo%2C%20{color.title()}%20{item_type}%2C%20{',%20'.join(materials)}%20material%2C%20{primary_style.lower()}%20style%2C%20white%20background%2C%20studio%20lighting%2C%20centered%2C%20high%20quality?width=400&height=600&seed={random.randint(1000000000, 2000000000)}&nologo=true"
    
    # Gender-specific categories/tags
    gender_tags = []
    if gender == "male":
        gender_tags = ["menswear", "masculine"]
    elif gender == "female":
        gender_tags = ["womenswear", "feminine"]
    else:
        gender_tags = ["unisex", "gender-neutral"]
    
    return {
        "id": f"item_{item_id:05d}",
        "title": f"{color.title()} {item_type}",
        "brand": brand,
        "price_cents": final_price * 100,
        "currency": "USD",
        "image_url": image_url,
        "categories": [category, item_type.lower().replace(" ", "_"), silhouette] + gender_tags,
        "materials": materials,
        "silhouettes": [silhouette],
        "tags": tags + gender_tags,
        "gender": gender,  # Explicit gender field
        "seasonality": seasons,
        "trend_score": round(trend_score, 2),
        **weather_props,
        "style_vector": style_vector,
        "ai_generated": True,
        "ai_service": "pollinations"
    }

def generate_comprehensive_catalog(
    items_per_combination: int = 15,
    ensure_coverage: bool = True
) -> Dict[str, Any]:
    """
    Generate a comprehensive catalog ensuring coverage for all combinations
    
    Args:
        items_per_combination: Number of items per style/gender/category combination
        ensure_coverage: If True, ensures at least one item for each valid combination
    """
    
    print(f"Generating comprehensive catalog...")
    print(f"Target: {items_per_combination} items per style/gender/category combination")
    
    items = []
    # Start with a high ID to avoid conflicts with existing catalogs
    item_id = 100000
    
    styles = list(STYLE_PERSONAS.keys())
    categories = list(ITEM_CATEGORIES.keys())
    
    # Generate items for each combination
    for style in styles:
        print(f"  Generating {style} items...")
        for category in categories:
            for gender in GENDERS:
                # Check if this combination is valid (e.g., dresses for male)
                if gender not in ITEM_CATEGORIES[category]["types"]:
                    continue
                if not ITEM_CATEGORIES[category]["types"][gender]:
                    continue
                
                # Generate items for this combination
                for _ in range(items_per_combination):
                    item = generate_item(item_id, style, category, gender)
                    if item:  # Skip None items (invalid combinations)
                        items.append(item)
                        item_id += 1
    
    # Ensure minimum coverage: at least 1 item per valid combination
    if ensure_coverage:
        print("\n  Ensuring minimum coverage for all combinations...")
        for style in styles:
            for category in categories:
                for gender in GENDERS:
                    if gender not in ITEM_CATEGORIES[category]["types"]:
                        continue
                    if not ITEM_CATEGORIES[category]["types"][gender]:
                        continue
                    
                    # Check if we have at least one item for this combination
                    existing = [i for i in items if 
                               i.get("style_vector", {}).get(style, 0) > 0.7 and
                               category in i.get("categories", []) and
                               i.get("gender") == gender]
                    
                    if not existing:
                        # Generate at least one item
                        item = generate_item(item_id, style, category, gender)
                        if item:
                            items.append(item)
                            item_id += 1
                            print(f"    Added missing: {style} {category} {gender}")
    
    # Shuffle for variety
    random.shuffle(items)
    
    catalog = {
        "catalog_version": "4.0",
        "last_updated": datetime.now().isoformat(),
        "total_items": len(items),
        "styles_covered": styles,
        "categories_covered": categories,
        "genders_covered": GENDERS,
        "items_per_combination": items_per_combination,
        "price_range": {
            "min_cents": min(item["price_cents"] for item in items) if items else 0,
            "max_cents": max(item["price_cents"] for item in items) if items else 0
        },
        "items": items
    }
    
    return catalog

def print_catalog_stats(catalog: Dict[str, Any]):
    """Print comprehensive statistics about the generated catalog"""
    items = catalog["items"]
    
    print("\n" + "="*70)
    print("COMPREHENSIVE CATALOG STATISTICS")
    print("="*70)
    print(f"Total Items: {len(items)}")
    print(f"Price Range: ${catalog['price_range']['min_cents']/100:.2f} - ${catalog['price_range']['max_cents']/100:.2f}")
    
    # Style distribution
    print("\n📊 Style Distribution:")
    style_counts = {}
    for item in items:
        for style, score in item.get("style_vector", {}).items():
            if score > 0.7:  # Primary style
                style_counts[style] = style_counts.get(style, 0) + 1
    for style, count in sorted(style_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {style}: {count} items")
    
    # Gender distribution
    print("\n👥 Gender Distribution:")
    gender_counts = {}
    for item in items:
        gender = item.get("gender", "unknown")
        gender_counts[gender] = gender_counts.get(gender, 0) + 1
    for gender, count in sorted(gender_counts.items()):
        print(f"  {gender}: {count} items")
    
    # Category distribution
    print("\n🏷️  Category Distribution:")
    category_counts = {}
    for item in items:
        cat = item.get("categories", [""])[0] if item.get("categories") else "unknown"
        category_counts[cat] = category_counts.get(cat, 0) + 1
    for cat, count in sorted(category_counts.items()):
        print(f"  {cat}: {count} items")
    
    # Style x Gender matrix
    print("\n🎯 Style x Gender Coverage:")
    for style in catalog["styles_covered"]:
        style_items = [i for i in items if i.get("style_vector", {}).get(style, 0) > 0.7]
        male_count = len([i for i in style_items if i.get("gender") == "male"])
        female_count = len([i for i in style_items if i.get("gender") == "female"])
        unisex_count = len([i for i in style_items if i.get("gender") == "unisex"])
        print(f"  {style:15s} | Male: {male_count:3d} | Female: {female_count:3d} | Unisex: {unisex_count:3d}")
    
    # Price tier distribution
    print("\n💰 Price Tier Distribution:")
    budget = len([i for i in items if i["price_cents"] < 5000])
    mid = len([i for i in items if 5000 <= i["price_cents"] < 15000])
    premium = len([i for i in items if 15000 <= i["price_cents"] < 30000])
    luxury = len([i for i in items if i["price_cents"] >= 30000])
    print(f"  Budget (<$50): {budget} items")
    print(f"  Mid ($50-$150): {mid} items")
    print(f"  Premium ($150-$300): {premium} items")
    print(f"  Luxury ($300+): {luxury} items")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate comprehensive style inspiration catalog")
    parser.add_argument("--items-per-combo", type=int, default=15, 
                       help="Number of items per style/gender/category combination")
    parser.add_argument("--output", type=str, 
                       default="../src/data/style_inspiration_catalog.json", 
                       help="Output file path")
    parser.add_argument("--append", action="store_true",
                       help="Append to existing catalog instead of replacing")
    parser.add_argument("--input", type=str,
                       help="Input catalog path (required if using --append)")
    parser.add_argument("--no-coverage-check", action="store_true",
                       help="Skip minimum coverage check (faster but may have gaps)")
    args = parser.parse_args()
    
    # Generate new catalog
    new_catalog = generate_comprehensive_catalog(
        items_per_combination=args.items_per_combo,
        ensure_coverage=not args.no_coverage_check
    )
    
    # If appending, merge with existing catalog
    if args.append:
        if not args.input:
            print("❌ Error: --input required when using --append")
            exit(1)
        
        input_path = Path(__file__).parent / args.input
        if not input_path.exists():
            print(f"❌ Error: Input catalog not found: {input_path}")
            exit(1)
        
        print(f"\n📖 Loading existing catalog from: {input_path}")
        with open(input_path, 'r') as f:
            existing_catalog = json.load(f)
        
        existing_items = existing_catalog.get("items", [])
        existing_ids = {item.get("id") for item in existing_items}
        
        # Filter out duplicates and get new items
        new_items = [item for item in new_catalog["items"] 
                    if item.get("id") not in existing_ids]
        
        # Merge catalogs
        merged_items = existing_items + new_items
        
        # Preserve existing metadata but update key fields
        merged_catalog = {
            **existing_catalog,  # Preserve existing metadata
            "catalog_version": "4.0",
            "last_updated": datetime.now().isoformat(),
            "total_items": len(merged_items),
            "items": merged_items,
            "appended_items": len(new_items),
            "original_items": len(existing_items)
        }
        
        # Ensure required fields exist
        if "styles_covered" not in merged_catalog:
            merged_catalog["styles_covered"] = new_catalog.get("styles_covered", [])
        if "categories_covered" not in merged_catalog:
            merged_catalog["categories_covered"] = new_catalog.get("categories_covered", [])
        if "genders_covered" not in merged_catalog:
            merged_catalog["genders_covered"] = new_catalog.get("genders_covered", GENDERS)
        
        print(f"✅ Merged catalogs:")
        print(f"   Existing items: {len(existing_items)}")
        print(f"   New items: {len(new_items)}")
        print(f"   Total items: {len(merged_items)}")
        
        catalog = merged_catalog
    else:
        catalog = new_catalog
        print(f"\n📝 Generating NEW catalog (will replace existing)")
    
    # Print stats
    print_catalog_stats(catalog)
    
    # Save to file
    output_path = Path(__file__).parent / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(catalog, f, indent=2)
    
    print(f"✅ Catalog saved to: {output_path}")
    print(f"📦 File size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
    print(f"\n🎉 Catalog generation complete!")
    print(f"   Total items: {len(catalog['items'])}")
    print(f"   Styles: {len(catalog.get('styles_covered', []))}")
    print(f"   Categories: {len(catalog.get('categories_covered', []))}")
    print(f"   Genders: {len(catalog.get('genders_covered', []))}")
    if args.append:
        print(f"   ✨ Appended {catalog.get('appended_items', 0)} new items to existing catalog")

