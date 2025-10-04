from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
from .style_engine import StyleAttributes, Material
from .wardrobe import ClothingType

class Accessory(str, Enum):
    WATCH = "watch"
    TIE = "tie"
    BELT = "belt"
    CUFFLINKS = "cufflinks"
    NECKLACE = "necklace"
    BRACELET = "bracelet"
    EARRINGS = "earrings"
    SCARF = "scarf"
    GLOVES = "gloves"
    UMBRELLA = "umbrella"
    SPORTS_WATCH = "sports_watch"
    SUNGLASSES = "sunglasses"
    HAT = "hat"
    BAG = "bag"
    WALLET = "wallet"

class WeatherCondition(str, Enum):
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    SNOWY = "snowy"
    WINDY = "windy"
    HUMID = "humid"
    DRY = "dry"

class TemperatureRange(str, Enum):
    FREEZING = "freezing"  # < 32°F
    COLD = "cold"         # 32-50°F
    CHILLY = "chilly"     # 50-65°F
    MILD = "mild"         # 65-75°F
    WARM = "warm"         # 75-85°F
    HOT = "hot"           # > 85°F

class Mood(str, Enum):
    CONFIDENT = "confident"
    RELAXED = "relaxed"
    PROFESSIONAL = "professional"
    PLAYFUL = "playful"
    ELEGANT = "elegant"
    BOLD = "bold"
    MINIMAL = "minimal"
    CREATIVE = "creative"
    COMFORTABLE = "comfortable"
    SOPHISTICATED = "sophisticated"
    ENERGETIC = "energetic"

class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"      # Office work, meetings
    LIGHT = "light"             # Walking, shopping
    MODERATE = "moderate"       # Light exercise, casual activities
    ACTIVE = "active"           # Sports, dancing
    INTENSE = "intense"         # Heavy exercise, outdoor activities

class OccasionType(str, Enum):
    # Professional
    BUSINESS_FORMAL = "Business Formal"
    BUSINESS_CASUAL = "Business Casual"
    WORK = "Work"
    INTERVIEW = "Interview"
    
    # Social
    CASUAL = "Casual"
    FORMAL = "Formal"
    GALA = "Gala"
    PARTY = "Party"
    DATE_NIGHT = "Date Night"
    FIRST_DATE = "First Date"
    BRUNCH = "Brunch"
    WEDDING_GUEST = "Wedding Guest"
    COCKTAIL = "Cocktail"
    NIGHT_OUT = "Night Out"
    
    # Travel & Leisure
    TRAVEL = "Travel"
    AIRPORT = "Airport"
    LOUNGEWEAR = "Loungewear"
    BEACH = "Beach"
    VACATION = "Vacation"
    FESTIVAL = "Festival"
    
    # Weather Specific
    RAINY_DAY = "Rainy Day"
    SNOW_DAY = "Snow Day"
    HOT_WEATHER = "Hot Weather"
    COLD_WEATHER = "Cold Weather"
    CHILLY_EVENING = "Chilly Evening"
    
    # Activities
    ATHLETIC = "Athletic / Gym"
    SCHOOL = "School"
    HOLIDAY = "Holiday"
    CONCERT = "Concert"
    ERRANDS = "Errands"
    MUSEUM = "Museum / Gallery"
    FASHION_EVENT = "Fashion Event"
    OUTDOOR_GATHERING = "Outdoor Gathering"
    
    # Special Occasions
    FUNERAL = "Funeral / Memorial"

class LayeringRule(BaseModel):
    min_temperature: float
    max_temperature: float
    required_layers: int
    layer_types: List[ClothingType]
    material_preferences: List[Material]
    notes: str

class OccasionRule(BaseModel):
    occasion: OccasionType
    required_items: List[ClothingType]
    forbidden_items: List[ClothingType]
    style_preferences: List[str]
    material_preferences: List[Material]
    accessory_requirements: List[Accessory]
    notes: str

class MoodRule(BaseModel):
    mood: Mood
    color_palette: List[str]
    style_preferences: List[str]
    material_preferences: List[Material]
    accessory_preferences: List[Accessory]
    notes: str

# Define layering rules
LAYERING_RULES = {
    "freezing": LayeringRule(
        min_temperature=-float('inf'),
        max_temperature=32,
        required_layers=3,
        layer_types=[ClothingType.SHIRT, ClothingType.SWEATER, ClothingType.JACKET],
        material_preferences=[Material.WOOL, Material.CASHMERE, Material.DOWN],
        notes="Heavy layering required with thermal base layer"
    ),
    "cold": LayeringRule(
        min_temperature=32,
        max_temperature=50,
        required_layers=2,
        layer_types=[ClothingType.SHIRT, ClothingType.SWEATER],
        material_preferences=[Material.WOOL, Material.CASHMERE, Material.FLEECE],
        notes="Medium layering with warm materials"
    ),
    "chilly": LayeringRule(
        min_temperature=50,
        max_temperature=65,
        required_layers=1,
        layer_types=[ClothingType.SHIRT],
        material_preferences=[Material.COTTON, Material.LINEN, Material.WOOL_BLEND],
        notes="Light layering with breathable materials"
    ),
    "mild": LayeringRule(
        min_temperature=65,
        max_temperature=75,
        required_layers=1,
        layer_types=[ClothingType.SHIRT],
        material_preferences=[Material.COTTON, Material.LINEN],
        notes="Single layer with light materials"
    ),
    "warm": LayeringRule(
        min_temperature=75,
        max_temperature=85,
        required_layers=1,
        layer_types=[ClothingType.SHIRT],
        material_preferences=[Material.COTTON, Material.LINEN],
        notes="Light, breathable single layer"
    ),
    "hot": LayeringRule(
        min_temperature=85,
        max_temperature=float('inf'),
        required_layers=1,
        layer_types=[ClothingType.SHIRT],
        material_preferences=[Material.COTTON, Material.LINEN],
        notes="Minimal, breathable clothing"
    )
}

# Define occasion rules
OCCASION_RULES = {
    # Professional
    "business_formal": OccasionRule(
        occasion=OccasionType.BUSINESS_FORMAL,
        required_items=[ClothingType.SHIRT, ClothingType.PANTS, ClothingType.DRESS_SHOES],
        forbidden_items=[ClothingType.SHORTS, ClothingType.SNEAKERS, ClothingType.SWEATER],
        style_preferences=["tailored", "structured", "classic", "professional", "sophisticated"],
        material_preferences=[Material.WOOL, Material.SILK, Material.TWILL],
        accessory_requirements=[Accessory.WATCH, Accessory.TIE, Accessory.BELT],
        notes="Professional and formal attire required"
    ),
    "business_casual": OccasionRule(
        occasion=OccasionType.BUSINESS_CASUAL,
        required_items=[ClothingType.SHIRT, ClothingType.PANTS, ClothingType.SHOES],
        forbidden_items=[ClothingType.SHORTS, ClothingType.SNEAKERS],
        style_preferences=["smart_casual", "refined", "polished", "contemporary", "professional"],
        material_preferences=[Material.COTTON, Material.WOOL, Material.TWILL],
        accessory_requirements=[Accessory.WATCH, Accessory.BELT],
        notes="Professional yet relaxed, no sneakers unless fashion-forward"
    ),
    "work": OccasionRule(
        occasion=OccasionType.WORK,
        required_items=[ClothingType.SHIRT, ClothingType.PANTS, ClothingType.SHOES],
        forbidden_items=[ClothingType.SHORTS, ClothingType.SNEAKERS],
        style_preferences=["professional", "practical", "neat", "business", "work_appropriate"],
        material_preferences=[Material.COTTON, Material.WOOL, Material.TWILL],
        accessory_requirements=[Accessory.WATCH],
        notes="Professional work attire"
    ),
    "interview": OccasionRule(
        occasion=OccasionType.INTERVIEW,
        required_items=[ClothingType.SHIRT, ClothingType.PANTS, ClothingType.DRESS_SHOES],
        forbidden_items=[ClothingType.SHORTS, ClothingType.SNEAKERS, ClothingType.SWEATER],
        style_preferences=["conservative", "professional", "polished", "traditional", "confident"],
        material_preferences=[Material.WOOL, Material.SILK, Material.TWILL],
        accessory_requirements=[Accessory.WATCH, Accessory.TIE],
        notes="Professional and formal interview attire"
    ),
    
    # Social
    "casual": OccasionRule(
        occasion=OccasionType.CASUAL,
        required_items=[ClothingType.SHIRT, ClothingType.PANTS],
        forbidden_items=[],
        style_preferences=["relaxed", "comfortable", "everyday", "effortless", "laid_back"],
        material_preferences=[Material.COTTON, Material.DENIM, Material.LINEN],
        accessory_requirements=[],
        notes="Relaxed and comfortable casual wear"
    ),
    "formal": OccasionRule(
        occasion=OccasionType.FORMAL,
        required_items=[ClothingType.SHIRT, ClothingType.PANTS, ClothingType.DRESS_SHOES],
        forbidden_items=[ClothingType.SHORTS, ClothingType.SNEAKERS],
        style_preferences=["elegant", "sophisticated", "refined", "luxurious", "classic"],
        material_preferences=[Material.WOOL, Material.SILK, Material.TWILL],
        accessory_requirements=[Accessory.WATCH, Accessory.TIE],
        notes="Formal attire required"
    ),
    "gala": OccasionRule(
        occasion=OccasionType.GALA,
        required_items=[ClothingType.SHIRT, ClothingType.PANTS, ClothingType.DRESS_SHOES],
        forbidden_items=[ClothingType.SHORTS, ClothingType.SNEAKERS],
        style_preferences=["luxurious", "elegant", "sophisticated", "high_end", "glamorous"],
        material_preferences=[Material.SILK, Material.WOOL, Material.SATIN],
        accessory_requirements=[Accessory.WATCH, Accessory.TIE, Accessory.CUFFLINKS],
        notes="Black tie or formal gala attire"
    ),
    "party": OccasionRule(
        occasion=OccasionType.PARTY,
        required_items=[ClothingType.SHIRT, ClothingType.PANTS, ClothingType.SHOES],
        forbidden_items=[],
        style_preferences=["bold", "trendy", "fashion_forward", "statement", "playful"],
        material_preferences=[Material.SILK, Material.SATIN, Material.LEATHER],
        accessory_requirements=[Accessory.WATCH, Accessory.NECKLACE],
        notes="Allow asymmetry, metallics, and statement pieces"
    ),
    "date_night": OccasionRule(
        occasion=OccasionType.DATE_NIGHT,
        required_items=[ClothingType.SHIRT, ClothingType.PANTS, ClothingType.SHOES],
        forbidden_items=[],
        style_preferences=["romantic", "elegant", "sophisticated", "stylish", "attractive"],
        material_preferences=[Material.SILK, Material.COTTON, Material.WOOL],
        accessory_requirements=[Accessory.WATCH],
        notes="Balanced between comfort and style"
    ),
    "first_date": OccasionRule(
        occasion=OccasionType.FIRST_DATE,
        required_items=[ClothingType.SHIRT, ClothingType.PANTS, ClothingType.SHOES],
        forbidden_items=[],
        style_preferences=["approachable", "stylish", "confident", "authentic", "memorable"],
        material_preferences=[Material.SILK, Material.COTTON, Material.WOOL],
        accessory_requirements=[Accessory.WATCH],
        notes="Balanced between comfort and style"
    ),
    "brunch": OccasionRule(
        occasion=OccasionType.BRUNCH,
        required_items=[ClothingType.SHIRT, ClothingType.PANTS],
        forbidden_items=[],
        style_preferences=["effortless", "elegant", "relaxed", "sophisticated", "casual_chic"],
        material_preferences=[Material.COTTON, Material.LINEN, Material.SILK],
        accessory_requirements=[Accessory.WATCH],
        notes="Casual yet put-together brunch attire"
    ),
    "wedding_guest": OccasionRule(
        occasion=OccasionType.WEDDING_GUEST,
        required_items=[ClothingType.SHIRT, ClothingType.PANTS, ClothingType.DRESS_SHOES],
        forbidden_items=[ClothingType.SHORTS, ClothingType.SNEAKERS],
        style_preferences=["elegant", "sophisticated", "festive", "refined", "celebratory"],
        material_preferences=[Material.WOOL, Material.SILK, Material.TWILL],
        accessory_requirements=[Accessory.WATCH, Accessory.TIE],
        notes="Formal wedding guest attire"
    ),
    "cocktail": OccasionRule(
        occasion=OccasionType.COCKTAIL,
        required_items=[ClothingType.SHIRT, ClothingType.PANTS, ClothingType.SHOES],
        forbidden_items=[ClothingType.SHORTS, ClothingType.SNEAKERS],
        style_preferences=["sophisticated", "elegant", "refined", "stylish", "upscale"],
        material_preferences=[Material.SILK, Material.WOOL, Material.SATIN],
        accessory_requirements=[Accessory.WATCH, Accessory.TIE],
        notes="Cocktail attire - elegant and sophisticated"
    ),
    "night_out": OccasionRule(
        occasion=OccasionType.NIGHT_OUT,
        required_items=[ClothingType.SHIRT, ClothingType.PANTS, ClothingType.SHOES],
        forbidden_items=[],
        style_preferences=["bold", "trendy", "stylish", "fashion_forward", "confident"],
        material_preferences=[Material.SILK, Material.SATIN, Material.LEATHER],
        accessory_requirements=[Accessory.WATCH, Accessory.NECKLACE],
        notes="Allow asymmetry, metallics, and statement pieces"
    ),
    
    # Travel & Leisure
    "travel": OccasionRule(
        occasion=OccasionType.TRAVEL,
        required_items=[ClothingType.SHIRT, ClothingType.PANTS],
        forbidden_items=[],
        style_preferences=["practical", "comfortable", "versatile", "functional", "travel_ready"],
        material_preferences=[Material.COTTON, Material.LINEN, Material.WOOL],
        accessory_requirements=[Accessory.WATCH],
        notes="Comfortable and practical travel wear"
    ),
    "airport": OccasionRule(
        occasion=OccasionType.AIRPORT,
        required_items=[ClothingType.SHIRT, ClothingType.PANTS],
        forbidden_items=[],
        style_preferences=["comfortable", "practical", "easy_movement", "travel_friendly", "layered"],
        material_preferences=[Material.COTTON, Material.LINEN, Material.WOOL],
        accessory_requirements=[Accessory.WATCH],
        notes="Comfortable and practical airport wear"
    ),
    "loungewear": OccasionRule(
        occasion=OccasionType.LOUNGEWEAR,
        required_items=[ClothingType.SHIRT, ClothingType.PANTS],
        forbidden_items=[],
        style_preferences=["cozy", "relaxed", "comfortable", "soft", "casual"],
        material_preferences=[Material.COTTON, Material.LINEN, Material.FLEECE],
        accessory_requirements=[],
        notes="Comfortable and relaxed loungewear"
    ),
    "beach": OccasionRule(
        occasion=OccasionType.BEACH,
        required_items=[ClothingType.SHIRT, ClothingType.SHORTS],
        forbidden_items=[ClothingType.DRESS_SHOES, ClothingType.DRESS_SHIRT],
        style_preferences=["beach_ready", "casual", "summer", "relaxed", "vacation"],
        material_preferences=[Material.COTTON, Material.LINEN],
        accessory_requirements=[],
        notes="Light and comfortable beach wear"
    ),
    "vacation": OccasionRule(
        occasion=OccasionType.VACATION,
        required_items=[],
        forbidden_items=[ClothingType.DRESS_SHOES, ClothingType.DRESS_SHIRT],
        style_preferences=["resort", "vacation", "relaxed", "comfortable", "holiday"],
        material_preferences=[Material.COTTON, Material.LINEN, Material.WOOL, Material.SILK],
        accessory_requirements=[Accessory.WATCH, Accessory.SUNGLASSES],
        notes="Comfortable and relaxed vacation wear. Can include dresses, shorts, swimwear, and resort wear."
    ),
    "festival": OccasionRule(
        occasion=OccasionType.FESTIVAL,
        required_items=[ClothingType.SHIRT, ClothingType.PANTS],
        forbidden_items=[ClothingType.DRESS_SHOES, ClothingType.DRESS_SHIRT],
        style_preferences=["festival", "bohemian", "trendy", "creative", "expressive"],
        material_preferences=[Material.COTTON, Material.DENIM],
        accessory_requirements=[],
        notes="Comfortable and trendy festival wear"
    ),
    
    # Weather Specific
    "rainy_day": OccasionRule(
        occasion=OccasionType.RAINY_DAY,
        required_items=[ClothingType.SHIRT, ClothingType.PANTS, ClothingType.JACKET],
        forbidden_items=[],
        style_preferences=["practical", "waterproof", "functional", "weather_appropriate", "protective"],
        material_preferences=[Material.WATERPROOF, Material.RUBBER],
        accessory_requirements=[Accessory.UMBRELLA],
        notes="Waterproof and practical rainy day wear"
    ),
    "snow_day": OccasionRule(
        occasion=OccasionType.SNOW_DAY,
        required_items=[ClothingType.SHIRT, ClothingType.PANTS, ClothingType.JACKET],
        forbidden_items=[],
        style_preferences=["warm", "protective", "insulated", "winter_ready", "cozy"],
        material_preferences=[Material.WOOL, Material.DOWN, Material.THERMAL],
        accessory_requirements=[Accessory.GLOVES, Accessory.SCARF],
        notes="Warm and practical snow day wear"
    ),
    "hot_weather": OccasionRule(
        occasion=OccasionType.HOT_WEATHER,
        required_items=[ClothingType.SHIRT, ClothingType.PANTS],
        forbidden_items=[ClothingType.JACKET, ClothingType.SWEATER],
        style_preferences=["breathable", "light", "summer", "cool", "airy"],
        material_preferences=[Material.COTTON, Material.LINEN],
        accessory_requirements=[],
        notes="Light and breathable hot weather wear"
    ),
    "cold_weather": OccasionRule(
        occasion=OccasionType.COLD_WEATHER,
        required_items=[ClothingType.SHIRT, ClothingType.PANTS, ClothingType.JACKET],
        forbidden_items=[],
        style_preferences=["warm", "insulated", "protective", "winter", "cozy"],
        material_preferences=[Material.WOOL, Material.DOWN, Material.THERMAL],
        accessory_requirements=[Accessory.GLOVES, Accessory.SCARF],
        notes="Warm and practical cold weather wear"
    ),
    "chilly_evening": OccasionRule(
        occasion=OccasionType.CHILLY_EVENING,
        required_items=[ClothingType.SHIRT, ClothingType.PANTS, ClothingType.JACKET],
        forbidden_items=[],
        style_preferences=["elegant", "layered", "sophisticated", "evening_appropriate", "refined"],
        material_preferences=[Material.WOOL, Material.CASHMERE],
        accessory_requirements=[Accessory.SCARF],
        notes="Warm and elegant chilly evening wear"
    ),
    
    # Activities
    "athletic": OccasionRule(
        occasion=OccasionType.ATHLETIC,
        required_items=[ClothingType.SHIRT, ClothingType.SHORTS, ClothingType.SNEAKERS],
        forbidden_items=[ClothingType.DRESS_SHIRT, ClothingType.LOAFERS, ClothingType.DRESS_SHOES, ClothingType.SWEATER],
        style_preferences=["athletic", "sporty", "performance", "active", "dynamic"],
        material_preferences=[Material.COTTON, Material.POLYESTER, Material.SPANDEX],
        accessory_requirements=[Accessory.SPORTS_WATCH],
        notes="Athletic and comfortable gym wear"
    ),
    "school": OccasionRule(
        occasion=OccasionType.SCHOOL,
        required_items=[ClothingType.SHIRT, ClothingType.PANTS],
        forbidden_items=[ClothingType.DRESS_SHOES],
        style_preferences=["neat", "appropriate", "practical", "comfortable", "academic"],
        material_preferences=[Material.COTTON, Material.DENIM],
        accessory_requirements=[],
        notes="Comfortable and practical school wear"
    ),
    "holiday": OccasionRule(
        occasion=OccasionType.HOLIDAY,
        required_items=[ClothingType.SHIRT, ClothingType.PANTS],
        forbidden_items=[],
        style_preferences=["festive", "celebratory", "traditional", "elegant", "seasonal"],
        material_preferences=[Material.WOOL, Material.COTTON, Material.SILK],
        accessory_requirements=[Accessory.WATCH],
        notes="Festive and elegant holiday wear"
    ),
    "concert": OccasionRule(
        occasion=OccasionType.CONCERT,
        required_items=[ClothingType.SHIRT, ClothingType.PANTS],
        forbidden_items=[ClothingType.DRESS_SHOES],
        style_preferences=["trendy", "music_inspired", "expressive", "stylish", "concert_ready"],
        material_preferences=[Material.COTTON, Material.DENIM],
        accessory_requirements=[],
        notes="Comfortable and trendy concert wear"
    ),
    "errands": OccasionRule(
        occasion=OccasionType.ERRANDS,
        required_items=[ClothingType.SHIRT, ClothingType.PANTS],
        forbidden_items=[],
        style_preferences=["practical", "comfortable", "easy_movement", "casual", "functional"],
        material_preferences=[Material.COTTON, Material.DENIM],
        accessory_requirements=[],
        notes="Comfortable and practical errand wear"
    ),
    "museum": OccasionRule(
        occasion=OccasionType.MUSEUM,
        required_items=[ClothingType.SHIRT, ClothingType.PANTS],
        forbidden_items=[],
        style_preferences=["cultured", "elegant", "refined", "sophisticated", "artistic"],
        material_preferences=[Material.COTTON, Material.WOOL],
        accessory_requirements=[Accessory.WATCH],
        notes="Comfortable and elegant museum wear"
    ),
    "fashion_event": OccasionRule(
        occasion=OccasionType.FASHION_EVENT,
        required_items=[ClothingType.SHIRT, ClothingType.PANTS, ClothingType.SHOES],
        forbidden_items=[],
        style_preferences=["fashion_forward", "trendy", "sophisticated", "stylish", "avant_garde"],
        material_preferences=[Material.SILK, Material.WOOL, Material.LEATHER],
        accessory_requirements=[Accessory.WATCH, Accessory.NECKLACE],
        notes="Fashion-forward and elegant event wear"
    ),
    "outdoor_gathering": OccasionRule(
        occasion=OccasionType.OUTDOOR_GATHERING,
        required_items=[ClothingType.SHIRT, ClothingType.PANTS],
        forbidden_items=[],
        style_preferences=["outdoor_ready", "casual", "practical", "weather_appropriate", "social"],
        material_preferences=[Material.COTTON, Material.DENIM, Material.WOOL],
        accessory_requirements=[Accessory.WATCH],
        notes="Comfortable and practical outdoor gathering wear"
    ),
    
    # Special Occasions
    "funeral": OccasionRule(
        occasion=OccasionType.FUNERAL,
        required_items=[ClothingType.SHIRT, ClothingType.PANTS, ClothingType.DRESS_SHOES],
        forbidden_items=[ClothingType.SHORTS, ClothingType.SNEAKERS],
        style_preferences=["respectful", "somber", "traditional", "formal", "dignified"],
        material_preferences=[Material.WOOL, Material.SILK, Material.TWILL],
        accessory_requirements=[Accessory.WATCH, Accessory.TIE],
        notes="Formal and somber funeral attire"
    )
}

# Define mood rules
MOOD_RULES = {
    "confident": MoodRule(
        mood=Mood.CONFIDENT,
        color_palette=["red", "black", "navy", "emerald"],
        style_preferences=["bold", "elegant", "sophisticated"],
        material_preferences=[Material.SILK, Material.LEATHER, Material.WOOL],
        accessory_preferences=[Accessory.WATCH, Accessory.NECKLACE],
        notes="Strong colors and structured pieces"
    ),
    "relaxed": MoodRule(
        mood=Mood.RELAXED,
        color_palette=["beige", "gray", "navy", "white"],
        style_preferences=["casual", "comfortable", "minimal"],
        material_preferences=[Material.COTTON, Material.LINEN, Material.CASHMERE],
        accessory_preferences=[Accessory.WATCH],
        notes="Soft colors and comfortable materials"
    ),
    "professional": MoodRule(
        mood=Mood.PROFESSIONAL,
        color_palette=["navy", "gray", "white", "black"],
        style_preferences=["business", "classic", "smart_casual"],
        material_preferences=[Material.WOOL, Material.COTTON, Material.TWILL],
        accessory_preferences=[Accessory.WATCH, Accessory.TIE],
        notes="Clean lines and professional colors"
    ),
    "playful": MoodRule(
        mood=Mood.PLAYFUL,
        color_palette=["yellow", "pink", "blue", "green"],
        style_preferences=["casual", "trendy", "colorful"],
        material_preferences=[Material.COTTON, Material.DENIM],
        accessory_preferences=[Accessory.BRACELET, Accessory.NECKLACE],
        notes="Bright colors and fun patterns"
    ),
    "comfortable": MoodRule(
        mood=Mood.COMFORTABLE,
        color_palette=["beige", "gray", "navy", "white", "brown"],
        style_preferences=["casual", "comfortable", "relaxed"],
        material_preferences=[Material.COTTON, Material.LINEN, Material.CASHMERE],
        accessory_preferences=[Accessory.WATCH],
        notes="Soft colors and comfortable materials"
    ),
    "energetic": MoodRule(
        mood=Mood.ENERGETIC,
        color_palette=["orange", "yellow", "bright_blue", "green", "red"],
        style_preferences=["athletic", "sporty", "dynamic"],
        material_preferences=[Material.COTTON, Material.POLYESTER, Material.SPANDEX],
        accessory_preferences=[Accessory.SPORTS_WATCH, Accessory.BRACELET],
        notes="Bright colors and active materials"
    )
}

def get_weather_rule(temperature: float) -> LayeringRule:
    """Get the appropriate layering rule based on temperature."""
    if temperature < 32:
        return LAYERING_RULES["freezing"]
    elif temperature < 50:
        return LAYERING_RULES["cold"]
    elif temperature < 65:
        return LAYERING_RULES["chilly"]
    elif temperature < 75:
        return LAYERING_RULES["mild"]
    elif temperature < 85:
        return LAYERING_RULES["warm"]
    else:
        return LAYERING_RULES["hot"]

def get_occasion_rule(occasion: str) -> Optional[OccasionRule]:
    """Get the rule for a specific occasion."""
    occasion_lower = occasion.lower()
    
    # First try exact match
    if occasion_lower in OCCASION_RULES:
        return OCCASION_RULES[occasion_lower]
    
    # Try partial matches for common variations
    for key, rule in OCCASION_RULES.items():
        # Check if the key is contained in the occasion string
        if key in occasion_lower:
            return rule
        # Check if the occasion string is contained in the key
        if occasion_lower in key:
            return rule
    
    # Try matching by common patterns
    if "athletic" in occasion_lower or "gym" in occasion_lower:
        return (OCCASION_RULES.get("athletic") if OCCASION_RULES else None)
    elif "business" in occasion_lower:
        if "formal" in occasion_lower:
            return (OCCASION_RULES.get("business_formal") if OCCASION_RULES else None)
        else:
            return (OCCASION_RULES.get("business_casual") if OCCASION_RULES else None)
    elif "casual" in occasion_lower:
        return (OCCASION_RULES.get("casual") if OCCASION_RULES else None)
    elif "formal" in occasion_lower:
        return (OCCASION_RULES.get("formal") if OCCASION_RULES else None)
    elif "interview" in occasion_lower:
        return (OCCASION_RULES.get("interview") if OCCASION_RULES else None)
    elif "beach" in occasion_lower:
        return (OCCASION_RULES.get("beach") if OCCASION_RULES else None)
    elif "travel" in occasion_lower:
        return (OCCASION_RULES.get("travel") if OCCASION_RULES else None)
    elif "party" in occasion_lower:
        return (OCCASION_RULES.get("party") if OCCASION_RULES else None)
    elif "date" in occasion_lower:
        return (OCCASION_RULES.get("date_night") if OCCASION_RULES else None)
    
    return None

def get_mood_rule(mood: str) -> Optional[MoodRule]:
    """Get the rule for a specific mood."""
    return (MOOD_RULES.get(mood.lower() if MOOD_RULES else None))

def validate_outfit_requirements(
    outfit_items: List[Dict[str, Any]],
    temperature: float,
    occasion: str,
    mood: Optional[str] = None
) -> Dict[str, Any]:
    """Validate if an outfit meets the requirements for the given conditions."""
    validation = {
        "is_valid": True,
        "warnings": [],
        "suggestions": []
    }

    # Check layering requirements
    layering_rule = get_weather_rule(temperature)
    current_layers = len([item for item in outfit_items if item["type"] in layering_rule.layer_types])
    
    if current_layers < layering_rule.required_layers:
        validation["is_valid"] = False
        validation["warnings"].append(
            f"Insufficient layering for {temperature}°F weather. Need {layering_rule.required_layers} layers."
        )

    # Check occasion requirements
    occasion_rule = get_occasion_rule(occasion)
    if occasion_rule:
        # Check required items
        for required_type in occasion_rule.required_items:
            if not any(item["type"] == required_type for item in outfit_items):
                validation["is_valid"] = False
                validation["warnings"].append(f"Missing required item type: {required_type}")

        # Check forbidden items
        for forbidden_type in occasion_rule.forbidden_items:
            if any(item["type"] == forbidden_type for item in outfit_items):
                validation["is_valid"] = False
                validation["warnings"].append(f"Forbidden item type present: {forbidden_type}")

    # Check mood requirements if specified
    if mood:
        mood_rule = get_mood_rule(mood)
        if mood_rule:
            # Check color palette
            outfit_colors = [item["color"] for item in outfit_items]
            if not any(color in mood_rule.color_palette for color in outfit_colors):
                validation["suggestions"].append(
                    f"Consider incorporating colors from the {mood} mood palette: {', '.join(mood_rule.color_palette)}"
                )

    return validation 