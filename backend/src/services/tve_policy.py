"""Shared, I/O-free TVE constants. Existing economics preserved."""
# Category-specific Target Wear Rates (R) - wears per year
# Updated to benchmark against "Efficient Minimalist" standards (weekly active rotation)
# instead of wasteful industry averages ("Hoarder Standard")
TARGET_WEAR_RATES = {
    "tops": 52,        # 1/week - A good shirt is part of your weekly rotation
    "pants": 75,       # 1.5/week - Pants have higher re-wear potential
    "dresses": 25,     # 1/2 weeks - Occasion wear, but still needs frequent use
    "jackets": 50,     # Seasonal daily, averaged to 1/week annual
    "shoes": 100,      # 2/week - Good shoes are worn constantly
    "activewear": 75,  # 1.5/week - Workout gear gets heavy rotation
    "accessories": 45  # ~0.9/week - Core accessories (belt, watch) get regular use
}

# Range midpoints for cost estimation (from old CPW system)
RANGE_MIDPOINTS = {
    "$0-$100": 50,
    "$100-$250": 175,
    "$250-$500": 375,
    "$500-$1,000": 750,
    "$1,000+": 1500,
    "unknown": 100  # Default fallback
}

# Category mappings for wardrobe items to spending categories
CATEGORY_TO_SPENDING_KEY = {
    # Tops
    "shirt": "tops",
    "t-shirt": "tops",
    "blouse": "tops",
    "tank_top": "tops",
    "crop_top": "tops",
    "polo": "tops",
    "dress_shirt": "tops",
    "sweater": "tops",
    "hoodie": "tops",
    "cardigan": "tops",

    # Bottoms
    "pants": "pants",
    "jeans": "pants",
    "chinos": "pants",
    "slacks": "pants",
    "joggers": "pants",
    "sweatpants": "pants",
    "shorts": "pants",
    "skirt": "pants",
    "mini_skirt": "pants",
    "midi_skirt": "pants",
    "maxi_skirt": "pants",
    "pencil_skirt": "pants",

    # Dresses
    "dress": "dresses",
    "sundress": "dresses",
    "cocktail_dress": "dresses",
    "maxi_dress": "dresses",
    "mini_dress": "dresses",

    # Outerwear
    "jacket": "jackets",
    "blazer": "jackets",
    "coat": "jackets",
    "vest": "jackets",

    # Shoes
    "shoes": "shoes",
    "sneakers": "shoes",
    "boots": "shoes",
    "sandals": "shoes",
    "heels": "shoes",
    "flats": "shoes",
    "loafers": "shoes",
    "dress_shoes": "shoes",

    # Accessories
    "hat": "accessories",
    "scarf": "accessories",
    "belt": "accessories",
    "jewelry": "accessories",
    "bag": "accessories",
    "watch": "accessories",
    "accessory": "accessories",
}
