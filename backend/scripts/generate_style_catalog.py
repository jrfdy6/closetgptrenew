#!/usr/bin/env python3
"""
Generate a comprehensive style inspiration catalog with 2000+ items
Covers all style personas, categories, price ranges, and weather conditions
"""

import json
import random
from typing import List, Dict, Any
from datetime import datetime

# Style personas with their characteristics
STYLE_PERSONAS = {
    "Old Money": {
        "keywords": ["luxury", "heritage", "timeless", "refined", "polished", "classic", "elegant"],
        "materials": ["cashmere", "wool", "silk", "leather", "cotton", "linen"],
        "colors": ["camel", "navy", "grey", "cream", "burgundy", "forest green", "tan"],
        "price_multiplier": 2.5
    },
    "Urban Street": {
        "keywords": ["streetwear", "casual", "edgy", "modern", "utility", "relaxed", "cool"],
        "materials": ["cotton", "nylon", "polyester", "denim", "canvas"],
        "colors": ["black", "white", "olive", "grey", "charcoal", "khaki"],
        "price_multiplier": 1.2
    },
    "Minimalist": {
        "keywords": ["clean", "simple", "sleek", "modern", "understated", "versatile"],
        "materials": ["cotton", "wool", "linen", "jersey", "silk"],
        "colors": ["black", "white", "grey", "beige", "navy", "cream"],
        "price_multiplier": 1.5
    },
    "Preppy": {
        "keywords": ["collegiate", "classic", "polished", "crisp", "traditional"],
        "materials": ["cotton", "wool", "oxford cloth", "chino"],
        "colors": ["navy", "white", "burgundy", "kelly green", "khaki", "pink"],
        "price_multiplier": 1.8
    },
    "Boho": {
        "keywords": ["bohemian", "relaxed", "artistic", "free-spirited", "earthy", "flowing"],
        "materials": ["cotton", "linen", "rayon", "silk", "crochet"],
        "colors": ["rust", "mustard", "terracotta", "olive", "cream", "burnt orange"],
        "price_multiplier": 1.3
    },
    "Y2K": {
        "keywords": ["retro", "playful", "bold", "nostalgic", "trendy", "statement"],
        "materials": ["polyester", "nylon", "vinyl", "mesh", "metallic"],
        "colors": ["pink", "purple", "silver", "neon", "bright blue", "lime"],
        "price_multiplier": 1.0
    },
    "Avant-Garde": {
        "keywords": ["experimental", "architectural", "artistic", "unconventional", "bold"],
        "materials": ["wool", "leather", "technical fabrics", "structured cotton"],
        "colors": ["black", "white", "charcoal", "deep red", "midnight blue"],
        "price_multiplier": 3.0
    },
    "Classic": {
        "keywords": ["timeless", "traditional", "versatile", "refined", "essential"],
        "materials": ["cotton", "wool", "silk", "leather", "denim"],
        "colors": ["navy", "white", "black", "grey", "tan", "brown"],
        "price_multiplier": 1.6
    }
}

# Item categories with their properties
ITEM_CATEGORIES = {
    "tops": {
        "types": [
            "T-Shirt", "Tank Top", "Polo Shirt", "Button-Down Shirt", "Blouse",
            "Sweater", "Cardigan", "Hoodie", "Sweatshirt", "Turtleneck",
            "Henley", "Crop Top", "Tube Top", "Camisole", "Halter Top"
        ],
        "base_price": 35,
        "silhouettes": ["fitted", "relaxed", "oversized", "slim", "regular"],
        "temp_range": (15, 28)
    },
    "bottoms": {
        "types": [
            "Jeans", "Chinos", "Trousers", "Shorts", "Cargo Pants",
            "Wide-Leg Pants", "Leggings", "Joggers", "Culottes", "Palazzo Pants",
            "Skirt", "Midi Skirt", "Mini Skirt", "Pencil Skirt", "A-Line Skirt"
        ],
        "base_price": 60,
        "silhouettes": ["slim", "regular", "wide", "tapered", "relaxed"],
        "temp_range": (10, 30)
    },
    "outerwear": {
        "types": [
            "Coat", "Trench Coat", "Peacoat", "Parka", "Blazer",
            "Leather Jacket", "Denim Jacket", "Bomber Jacket", "Varsity Jacket",
            "Puffer Jacket", "Cardigan", "Sweater Coat", "Cape", "Kimono"
        ],
        "base_price": 120,
        "silhouettes": ["fitted", "oversized", "structured", "relaxed"],
        "temp_range": (-10, 20)
    },
    "footwear": {
        "types": [
            "Sneakers", "Loafers", "Boots", "Chelsea Boots", "Combat Boots",
            "Sandals", "Heels", "Flats", "Oxfords", "Mules",
            "Slides", "Platforms", "Wedges", "Ankle Boots", "Knee-High Boots"
        ],
        "base_price": 80,
        "silhouettes": ["sleek", "chunky", "minimalist", "statement"],
        "temp_range": (5, 35)
    },
    "dresses": {
        "types": [
            "Midi Dress", "Maxi Dress", "Mini Dress", "Shift Dress", "Wrap Dress",
            "Shirt Dress", "Slip Dress", "A-Line Dress", "Bodycon Dress",
            "T-Shirt Dress", "Sweater Dress", "Cocktail Dress"
        ],
        "base_price": 90,
        "silhouettes": ["fitted", "flowy", "structured", "relaxed"],
        "temp_range": (15, 30)
    },
    "accessories": {
        "types": [
            "Belt", "Scarf", "Hat", "Beanie", "Baseball Cap",
            "Sunglasses", "Watch", "Necklace", "Earrings", "Bracelet",
            "Bag", "Backpack", "Tote", "Crossbody", "Clutch"
        ],
        "base_price": 40,
        "silhouettes": ["minimalist", "statement", "classic", "bold"],
        "temp_range": (-10, 40)
    }
}

# Brands by price tier
BRANDS = {
    "luxury": ["Loro Piana", "Brunello Cucinelli", "The Row", "Max Mara", "Saint Laurent"],
    "premium": ["Theory", "Equipment", "APC", "Acne Studios", "Common Projects"],
    "mid": ["COS", "Everlane", "Madewell", "J.Crew", "Banana Republic"],
    "accessible": ["Uniqlo", "H&M", "Zara", "Gap", "Old Navy"]
}

SEASONS = ["spring", "summer", "fall", "winter"]

def generate_style_vector(primary_style: str, secondary_styles: List[str] = None) -> Dict[str, float]:
    """Generate a style vector with primary and optional secondary styles"""
    vector = {style: 0.0 for style in STYLE_PERSONAS.keys()}
    
    # Primary style gets high score
    vector[primary_style] = random.uniform(0.75, 0.95)
    
    # Secondary styles get medium scores
    if secondary_styles:
        for style in secondary_styles:
            vector[style] = random.uniform(0.35, 0.65)
    
    # Add small random values to other styles
    for style in vector.keys():
        if style != primary_style and style not in (secondary_styles or []):
            vector[style] = random.uniform(0.05, 0.25)
    
    return vector

def calculate_weather_properties(category: str, materials: List[str], season: List[str]) -> Dict[str, Any]:
    """Calculate weather-related properties based on materials and season"""
    
    # Material thermal scores
    thermal_map = {
        "wool": 0.85, "cashmere": 0.90, "down": 0.95, "fleece": 0.80,
        "cotton": 0.50, "linen": 0.20, "silk": 0.40, "polyester": 0.55,
        "nylon": 0.60, "leather": 0.70, "denim": 0.60
    }
    
    # Water resistance by material
    water_map = {
        "leather": 0.5, "nylon": 0.7, "polyester": 0.6, "wool": 0.3,
        "cotton": 0.2, "down": 0.8, "wax": 0.9
    }
    
    # Calculate thermal score
    thermal_scores = [thermal_map.get(mat.lower(), 0.5) for mat in materials]
    thermal_score = sum(thermal_scores) / len(thermal_scores) if thermal_scores else 0.5
    
    # Calculate water resistance
    water_scores = [water_map.get(mat.lower(), 0.1) for mat in materials]
    water_resistance = sum(water_scores) / len(water_scores) if water_scores else 0.1
    
    # Wind resistance (outerwear higher)
    wind_resistance = 0.7 if category == "outerwear" else 0.3
    
    # Temperature ranges by season
    if "winter" in season:
        temp_min, temp_max = -10, 15
    elif "fall" in season or "spring" in season:
        temp_min, temp_max = 5, 22
    elif "summer" in season:
        temp_min, temp_max = 18, 35
    else:
        temp_min, temp_max = 0, 30
    
    # Weather tags
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

def generate_item(item_id: int, primary_style: str, category: str) -> Dict[str, Any]:
    """Generate a single catalog item"""
    
    style_info = STYLE_PERSONAS[primary_style]
    category_info = ITEM_CATEGORIES[category]
    
    # Select secondary styles (sometimes)
    secondary_styles = []
    if random.random() > 0.6:
        available = [s for s in STYLE_PERSONAS.keys() if s != primary_style]
        secondary_styles = random.sample(available, random.randint(1, 2))
    
    # Item type
    item_type = random.choice(category_info["types"])
    
    # Materials (1-2 from style persona)
    materials = random.sample(style_info["materials"], random.randint(1, 2))
    
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
    tags = random.sample(style_info["keywords"], random.randint(2, 4))
    
    # Weather properties
    weather_props = calculate_weather_properties(category, materials, seasons)
    
    # Trend score (inverse of "timeless" tags)
    trend_score = 0.2 if "timeless" in tags or "classic" in tags else random.uniform(0.4, 0.8)
    
    # Generate style vector
    style_vector = generate_style_vector(primary_style, secondary_styles)
    
    # Image URL (using Unsplash with relevant search terms)
    image_search = f"{item_type.lower().replace(' ', '-')}-{color.replace(' ', '-')}"
    image_url = f"https://images.unsplash.com/photo-{random.randint(1500000000, 1700000000)}?w=400&q={image_search}"
    
    return {
        "id": f"item_{item_id:05d}",
        "title": f"{color.title()} {item_type}",
        "brand": brand,
        "price_cents": final_price * 100,
        "currency": "USD",
        "image_url": image_url,
        "categories": [category, item_type.lower().replace(" ", "_"), silhouette],
        "materials": materials,
        "silhouettes": [silhouette],
        "tags": tags,
        "seasonality": seasons,
        "trend_score": round(trend_score, 2),
        **weather_props,
        "style_vector": style_vector
    }

def generate_catalog(num_items: int = 2000) -> Dict[str, Any]:
    """Generate the full catalog with balanced distribution"""
    
    print(f"Generating catalog with {num_items} items...")
    
    items = []
    item_id = 1
    
    # Calculate items per style (balanced distribution)
    styles = list(STYLE_PERSONAS.keys())
    categories = list(ITEM_CATEGORIES.keys())
    
    items_per_style = num_items // len(styles)
    items_per_category = items_per_style // len(categories)
    
    print(f"Target: ~{items_per_style} items per style, ~{items_per_category} per category")
    
    for style in styles:
        print(f"  Generating {style} items...")
        for category in categories:
            for _ in range(items_per_category):
                item = generate_item(item_id, style, category)
                items.append(item)
                item_id += 1
    
    # Fill remaining slots with random distribution
    remaining = num_items - len(items)
    if remaining > 0:
        print(f"  Generating {remaining} additional items for balance...")
        for _ in range(remaining):
            style = random.choice(styles)
            category = random.choice(categories)
            item = generate_item(item_id, style, category)
            items.append(item)
            item_id += 1
    
    # Shuffle for variety
    random.shuffle(items)
    
    catalog = {
        "catalog_version": "2.0",
        "last_updated": datetime.now().isoformat(),
        "total_items": len(items),
        "styles_covered": styles,
        "categories_covered": categories,
        "price_range": {
            "min_cents": min(item["price_cents"] for item in items),
            "max_cents": max(item["price_cents"] for item in items)
        },
        "items": items
    }
    
    return catalog

def print_catalog_stats(catalog: Dict[str, Any]):
    """Print statistics about the generated catalog"""
    items = catalog["items"]
    
    print("\n" + "="*60)
    print("CATALOG STATISTICS")
    print("="*60)
    print(f"Total Items: {len(items)}")
    print(f"Price Range: ${catalog['price_range']['min_cents']/100:.2f} - ${catalog['price_range']['max_cents']/100:.2f}")
    
    # Style distribution
    print("\n📊 Style Distribution:")
    style_counts = {}
    for item in items:
        for style, score in item["style_vector"].items():
            if score > 0.7:  # Primary style
                style_counts[style] = style_counts.get(style, 0) + 1
    for style, count in sorted(style_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {style}: {count} items")
    
    # Category distribution
    print("\n🏷️  Category Distribution:")
    category_counts = {}
    for item in items:
        cat = item["categories"][0]
        category_counts[cat] = category_counts.get(cat, 0) + 1
    for cat, count in sorted(category_counts.items()):
        print(f"  {cat}: {count} items")
    
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
    
    # Season distribution
    print("\n🌦️  Season Coverage:")
    season_counts = {}
    for item in items:
        for season in item["seasonality"]:
            season_counts[season] = season_counts.get(season, 0) + 1
    for season, count in sorted(season_counts.items()):
        print(f"  {season}: {count} items")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate style inspiration catalog")
    parser.add_argument("--items", type=int, default=2000, help="Number of items to generate")
    parser.add_argument("--output", type=str, default="../src/data/style_inspiration_catalog.json", help="Output file path")
    args = parser.parse_args()
    
    # Generate catalog
    catalog = generate_catalog(args.items)
    
    # Print stats
    print_catalog_stats(catalog)
    
    # Save to file
    import os
    output_path = os.path.join(os.path.dirname(__file__), args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(catalog, f, indent=2)
    
    print(f"✅ Catalog saved to: {output_path}")
    print(f"📦 File size: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")

