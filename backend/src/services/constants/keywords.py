#!/usr/bin/env python3
"""
Occasion and Style Keywords
============================

Comprehensive keyword definitions for matching clothing items to occasions and styles.
Extracted from robust_outfit_generation_service.py for better maintainability.
"""

# ═══════════════════════════════════════════════════════════════════════
# OCCASION KEYWORDS
# ═══════════════════════════════════════════════════════════════════════

OCCASION_KEYWORDS = {
    # Formal occasions
    "formal": ["formal", "gala", "black-tie", "white-tie", "evening", "elegant"],
    "business": ["business", "professional", "corporate", "office", "work"],
    "interview": ["interview", "job interview", "professional meeting"],
    "wedding": ["wedding", "ceremony", "reception", "formal event"],
    
    # Semi-formal
    "cocktail": ["cocktail", "cocktail party", "semi-formal", "dressy"],
    "date": ["date", "date night", "romantic", "dinner date"],
    "dinner": ["dinner", "restaurant", "fine dining", "dinner party"],
    
    # Casual
    "casual": ["casual", "everyday", "relaxed", "comfortable"],
    "brunch": ["brunch", "lunch", "daytime", "weekend"],
    "party": ["party", "celebration", "social", "gathering"],
    
    # Active
    "gym": ["gym", "workout", "exercise", "fitness", "training"],
    "athletic": ["athletic", "sport", "sports", "active", "running"],
    "outdoor": ["outdoor", "hiking", "camping", "nature", "adventure"],
    
    # Relaxed
    "loungewear": ["loungewear", "lounge", "home", "relaxing", "cozy"],
    "sleep": ["sleep", "pajamas", "nightwear", "bedtime"],
    "beach": ["beach", "pool", "swim", "resort", "vacation"],
}

# ═══════════════════════════════════════════════════════════════════════
# STYLE KEYWORDS
# ═══════════════════════════════════════════════════════════════════════

STYLE_KEYWORDS = {
    # Classic styles
    "classic": ["classic", "timeless", "traditional", "elegant", "refined"],
    "preppy": ["preppy", "ivy-league", "collegiate", "nautical", "polished"],
    "minimalist": ["minimalist", "minimal", "simple", "clean", "modern"],
    
    # Trendy styles
    "streetwear": ["streetwear", "urban", "hip-hop", "contemporary", "edgy"],
    "bohemian": ["bohemian", "boho", "free-spirit", "artistic", "eclectic"],
    "romantic": ["romantic", "feminine", "soft", "delicate", "dreamy"],
    
    # Professional styles
    "business_casual": ["business casual", "smart casual", "professional", "polished"],
    "corporate": ["corporate", "executive", "formal", "business", "professional"],
    
    # Casual styles
    "athleisure": ["athleisure", "sporty", "athletic", "active", "comfortable"],
    "casual_chic": ["casual chic", "effortless", "relaxed", "stylish"],
    
    # Alternative styles
    "gothic": ["gothic", "goth", "dark", "alternative", "edgy"],
    "punk": ["punk", "rock", "rebellious", "alternative", "edgy"],
    "vintage": ["vintage", "retro", "classic", "nostalgic", "timeless"],
    
    # Academia styles
    "dark_academia": ["dark academia", "scholarly", "intellectual", "vintage", "classic"],
    "light_academia": ["light academia", "scholarly", "soft", "romantic", "vintage"],
    
    # Modern styles
    "modern": ["modern", "contemporary", "current", "trendy", "fashionable"],
    "scandinavian": ["scandinavian", "nordic", "minimalist", "clean", "functional"],
    
    # Luxury styles
    "old_money": ["old money", "luxury", "refined", "elegant", "classic"],
    "quiet_luxury": ["quiet luxury", "understated", "refined", "quality", "timeless"],
}

# ═══════════════════════════════════════════════════════════════════════
# ITEM TYPE KEYWORDS
# ═══════════════════════════════════════════════════════════════════════

ITEM_TYPE_KEYWORDS = {
    # Tops
    "shirt": ["shirt", "blouse", "top", "tee", "t-shirt", "button-up", "button-down"],
    "sweater": ["sweater", "pullover", "cardigan", "knit", "jumper"],
    "jacket": ["jacket", "blazer", "coat", "outerwear"],
    
    # Bottoms
    "pants": ["pants", "trousers", "jeans", "slacks", "chinos"],
    "shorts": ["shorts", "bermuda", "cargo shorts"],
    "skirt": ["skirt", "mini skirt", "midi skirt", "maxi skirt"],
    
    # Dresses
    "dress": ["dress", "gown", "frock", "sundress", "maxi dress"],
    
    # Shoes
    "sneakers": ["sneakers", "trainers", "athletic shoes", "running shoes"],
    "boots": ["boots", "ankle boots", "knee boots", "chelsea boots"],
    "heels": ["heels", "pumps", "stilettos", "high heels"],
    "flats": ["flats", "ballet flats", "loafers", "oxfords"],
    "sandals": ["sandals", "slides", "flip-flops", "espadrilles"],
    
    # Accessories
    "bag": ["bag", "purse", "handbag", "tote", "clutch", "backpack"],
    "hat": ["hat", "cap", "beanie", "fedora", "beret"],
    "scarf": ["scarf", "shawl", "wrap", "pashmina"],
    "jewelry": ["jewelry", "necklace", "bracelet", "earrings", "ring"],
}

# ═══════════════════════════════════════════════════════════════════════
# FORMALITY KEYWORDS
# ═══════════════════════════════════════════════════════════════════════

FORMALITY_KEYWORDS = {
    "very_formal": [
        "tuxedo", "evening gown", "black-tie", "white-tie", "formal dress",
        "dress shoes", "patent leather", "bow tie", "cufflinks"
    ],
    "formal": [
        "suit", "blazer", "dress pants", "dress shirt", "dress shoes",
        "heels", "tie", "formal skirt", "cocktail dress"
    ],
    "business_casual": [
        "button-up", "chinos", "loafers", "polo", "sweater",
        "dress pants", "ankle boots", "blazer casual"
    ],
    "smart_casual": [
        "dark jeans", "nice top", "leather shoes", "cardigan",
        "midi dress", "chelsea boots", "smart sneakers"
    ],
    "casual": [
        "jeans", "t-shirt", "sneakers", "hoodie", "casual dress",
        "sandals", "shorts", "tank top"
    ],
    "athletic": [
        "athletic wear", "gym clothes", "running shoes", "workout gear",
        "sports bra", "leggings", "track pants", "training shoes"
    ],
}

# ═══════════════════════════════════════════════════════════════════════
# WEATHER KEYWORDS
# ═══════════════════════════════════════════════════════════════════════

WEATHER_KEYWORDS = {
    "cold": [
        "coat", "jacket", "sweater", "boots", "scarf", "gloves",
        "warm", "insulated", "wool", "fleece", "puffer"
    ],
    "cool": [
        "light jacket", "cardigan", "long sleeves", "jeans",
        "closed-toe shoes", "layering pieces"
    ],
    "mild": [
        "light layers", "versatile", "transitional", "adaptable"
    ],
    "warm": [
        "short sleeves", "light fabrics", "breathable", "cotton",
        "linen", "open-toe shoes"
    ],
    "hot": [
        "shorts", "tank top", "sundress", "sandals", "breathable",
        "lightweight", "minimal layers", "sleeveless"
    ],
    "rainy": [
        "waterproof", "rain jacket", "boots", "water-resistant",
        "covered shoes", "umbrella-friendly"
    ],
}

# ═══════════════════════════════════════════════════════════════════════
# COLOR KEYWORDS
# ═══════════════════════════════════════════════════════════════════════

COLOR_FAMILIES = {
    "neutral": ["black", "white", "gray", "grey", "beige", "tan", "cream", "ivory", "brown"],
    "earth_tones": ["brown", "tan", "olive", "khaki", "camel", "terracotta", "rust"],
    "jewel_tones": ["emerald", "sapphire", "ruby", "amethyst", "topaz"],
    "pastels": ["pink", "lavender", "mint", "peach", "baby blue", "powder blue"],
    "brights": ["red", "orange", "yellow", "green", "blue", "purple"],
    "metallics": ["gold", "silver", "bronze", "copper", "metallic"],
}

# ═══════════════════════════════════════════════════════════════════════
# PATTERN KEYWORDS
# ═══════════════════════════════════════════════════════════════════════

PATTERN_KEYWORDS = {
    "solid": ["solid", "plain", "single-color", "monochrome"],
    "stripes": ["striped", "stripes", "pinstripe", "horizontal stripes", "vertical stripes"],
    "plaid": ["plaid", "check", "checkered", "gingham", "tartan"],
    "floral": ["floral", "flower", "botanical", "rose", "daisy"],
    "geometric": ["geometric", "abstract", "shapes", "triangles", "circles"],
    "animal_print": ["leopard", "zebra", "snake", "animal print", "cheetah"],
    "polka_dot": ["polka dot", "dots", "spotted"],
}

# ═══════════════════════════════════════════════════════════════════════
# MATERIAL KEYWORDS
# ═══════════════════════════════════════════════════════════════════════

MATERIAL_KEYWORDS = {
    "natural": ["cotton", "linen", "wool", "silk", "leather", "suede"],
    "synthetic": ["polyester", "nylon", "spandex", "acrylic", "rayon"],
    "luxury": ["cashmere", "silk", "velvet", "satin", "leather", "suede"],
    "performance": ["moisture-wicking", "breathable", "stretchy", "quick-dry"],
    "sustainable": ["organic cotton", "recycled", "eco-friendly", "sustainable"],
}

# ═══════════════════════════════════════════════════════════════════════
# SEASON KEYWORDS
# ═══════════════════════════════════════════════════════════════════════

SEASON_KEYWORDS = {
    "spring": ["spring", "transitional", "light layers", "fresh"],
    "summer": ["summer", "lightweight", "breathable", "warm weather"],
    "fall": ["fall", "autumn", "layering", "cozy", "transitional"],
    "winter": ["winter", "warm", "insulated", "cold weather", "heavy"],
}

