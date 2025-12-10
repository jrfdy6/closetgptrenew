"""
Pydantic models for gamification system
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ChallengeType(str, Enum):
    """Types of challenges available in the system"""
    FORGOTTEN_GEMS = "forgotten_gems"
    COLOR_PALETTE = "color_palette"
    THIRTY_WEARS = "30_wears"
    CONTEXT = "context"
    COLD_START = "cold_start"
    # New Ecosystem Engineering challenge types
    STREAK_MAINTENANCE = "streak_maintenance"
    GACHA_PULL = "gacha_pull"
    ROLE_DEFENSE = "role_defense"
    SCARCITY_EVENT = "scarcity_event"
    CPW_OPTIMIZER = "cpw_optimizer"
    COLOR_EXPLORER = "color_explorer"
    THEMED_EVENT = "themed_event"
    SUSTAINABILITY_CHAMPION = "sustainability_champion"
    PATTERN_MASTER = "pattern_master"
    ANNUAL = "annual"


class ChallengeStatus(str, Enum):
    """Status of a user's challenge"""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"
    FAILED = "failed"


class BadgeType(str, Enum):
    """Types of badges that can be earned"""
    # Onboarding badges
    STARTER_CLOSET = "starter_closet"
    CLOSET_CATALOGER = "closet_cataloger"
    
    # Usage badges
    HIDDEN_GEM_HUNTER = "hidden_gem_hunter"
    TREASURE_HUNTER = "treasure_hunter"
    
    # Wear count badges
    SUSTAINABLE_STYLE_BRONZE = "sustainable_style_bronze"
    SUSTAINABLE_STYLE_SILVER = "sustainable_style_silver"
    SUSTAINABLE_STYLE_GOLD = "sustainable_style_gold"
    
    # Color challenges
    COLOR_MASTER = "color_master"
    MONOCHROME_MAVEN = "monochrome_maven"
    
    # Context challenges
    WEATHER_WARRIOR = "weather_warrior"
    TRANSIT_STYLIST = "transit_stylist"
    VERSATILE_PRO = "versatile_pro"
    
    # Feedback badges
    STYLE_CONTRIBUTOR = "style_contributor"
    AI_TRAINER = "ai_trainer"


class LevelTier(str, Enum):
    """Level tier names"""
    NOVICE = "Novice"
    STYLIST = "Stylist"
    CURATOR = "Curator"
    CONNOISSEUR = "Connoisseur"


class UserRole(str, Enum):
    """Internal Status Roles - Power User Tiers"""
    STARTER = "starter"            # Level 1 - Basic access
    EXPLORER = "explorer"          # Level 2 - Early access, token bonuses
    STYLIST = "stylist"            # Level 3 - Enhanced perks
    CURATOR = "curator"            # Level 4 - Premium features
    MASTER = "master"              # Level 5 - Top tier, exclusive features


class GachaRarity(str, Enum):
    """Gacha pull rarity tiers"""
    COMMON = "COMMON"
    RARE = "RARE"
    LEGENDARY = "LEGENDARY"


class Challenge(BaseModel):
    """Global challenge definition"""
    id: str
    type: ChallengeType
    title: str
    description: str
    rules: Dict[str, Any]
    rewards: Dict[str, Any]  # Contains xp and optional badge
    cadence: Optional[str] = None  # "weekly", "monthly", "always"
    featured: bool = False
    icon: Optional[str] = None
    
    class Config:
        use_enum_values = True


class UserChallenge(BaseModel):
    """A user's active or completed challenge"""
    challenge_id: str
    user_id: str
    started_at: datetime
    expires_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: int = 0
    target: int
    status: ChallengeStatus = ChallengeStatus.IN_PROGRESS
    items: List[str] = Field(default_factory=list)  # Item IDs involved in challenge
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True


class Badge(BaseModel):
    """Badge metadata"""
    id: BadgeType
    name: str
    description: str
    icon: str  # Lucide icon name
    unlock_condition: str
    rarity: str = "common"  # common, rare, epic, legendary
    
    class Config:
        use_enum_values = True


class GamificationEvent(BaseModel):
    """Event for analytics tracking"""
    event_type: str  # xp_earned, level_up, badge_unlocked, challenge_started, etc.
    user_id: str
    timestamp: datetime
    xp_amount: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class XPReward(BaseModel):
    """XP reward information"""
    amount: int
    reason: str
    source: str  # outfit_logged, feedback_given, challenge_completed, etc.
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LevelInfo(BaseModel):
    """Level information"""
    level: int
    tier: LevelTier
    current_xp: int
    xp_for_next_level: int
    progress_percentage: float
    
    class Config:
        use_enum_values = True


class GamificationState(BaseModel):
    """Complete gamification state for a user"""
    user_id: str
    xp: int
    level: int
    level_info: LevelInfo
    ai_fit_score: float
    badges: List[str]
    active_challenges: List[UserChallenge]
    completed_challenges_count: int
    
    class Config:
        use_enum_values = True


class StreakData(BaseModel):
    """User streak information"""
    current_streak: int = 0
    longest_streak: int = 0
    last_log_date: Optional[str] = None
    streak_multiplier: float = 1.0


class StyleTokens(BaseModel):
    """Style Token balance and statistics"""
    balance: int = 0
    total_earned: int = 0
    total_spent: int = 0
    last_earned_at: Optional[str] = None


class UserRoleData(BaseModel):
    """User role and privilege information"""
    current_role: str = "starter"
    role_earned_at: Optional[str] = None
    role_decay_checks_remaining: int = 0
    privileges: Dict[str, Any] = Field(default_factory=dict)


class GachaPull(BaseModel):
    """Gacha pull result"""
    rarity: GachaRarity
    reward_type: str
    reward_data: Dict[str, Any]
    visual_effect: str
    pulled_at: datetime
    cost: int




# Predefined challenges catalog
CHALLENGE_CATALOG = {
    "forgotten_gems_weekly": Challenge(
        id="forgotten_gems_weekly",
        type=ChallengeType.FORGOTTEN_GEMS,
        title="Hidden Gem Hunter",
        description="Wear 2 items you haven't worn in 60+ days",
        rules={
            "days_dormant_min": 60,
            "items_required": 2
        },
        rewards={
            "xp": 75,
            "tokens": 75,
            "badge": BadgeType.HIDDEN_GEM_HUNTER.value
        },
        cadence="weekly",
        featured=True,
        icon="Sparkles"
    ),
    "30_wears_challenge": Challenge(
        id="30_wears_challenge",
        type=ChallengeType.THIRTY_WEARS,
        title="30 Wears Challenge",
        description="Wear any item 30 times to unlock sustainable style badge",
        rules={
            "target_wears": 30
        },
        rewards={
            "xp": 100,
            "tokens": 100,
            "badge": BadgeType.SUSTAINABLE_STYLE_BRONZE.value
        },
        cadence="always",
        featured=False,
        icon="Target"
    ),
    "color_harmony": Challenge(
        id="color_harmony",
        type=ChallengeType.COLOR_PALETTE,
        title="Color Harmony Week",
        description="Create 3 outfits using complementary colors",
        rules={
            "outfits_required": 3,
            "color_rule": "complementary"
        },
        rewards={
            "xp": 120,
            "tokens": 120,
            "badge": BadgeType.COLOR_MASTER.value
        },
        cadence="weekly",
        featured=True,
        icon="Palette"
    ),
    "cold_start_quest": Challenge(
        id="cold_start_quest",
        type=ChallengeType.COLD_START,
        title="Closet Cataloger",
        description="Upload your first 50 items to your wardrobe",
        rules={
            "items_required": 50
        },
        rewards={
            "xp": 200,
            "tokens": 200,
            "badge": BadgeType.CLOSET_CATALOGER.value
        },
        cadence="always",
        featured=False,
        icon="Upload"
    ),
    "annual_wardrobe_master": Challenge(
        id="annual_wardrobe_master",
        type=ChallengeType.ANNUAL,
        title="Wardrobe Master",
        description="Log 5 outfits per week for 52 weeks (260 total)",
        rules={
            "outfits_per_week": 5,
            "weeks_required": 52,
            "total_outfits": 260
        },
        rewards={
            "xp": 5000,
            "tokens": 5000,
            "badge": "annual_master_cycle_1"  # Cycle number will be appended dynamically
        },
        cadence="annual",
        featured=True,
        icon="Crown"
    ),
}


# Badge definitions
BADGE_DEFINITIONS = {
    BadgeType.STARTER_CLOSET: Badge(
        id=BadgeType.STARTER_CLOSET,
        name="Starter Closet",
        description="Uploaded your first 10 items",
        icon="Shirt",
        unlock_condition="Upload 10 items",
        rarity="common"
    ),
    BadgeType.CLOSET_CATALOGER: Badge(
        id=BadgeType.CLOSET_CATALOGER,
        name="Closet Cataloger",
        description="Uploaded 50 items to your wardrobe",
        icon="Archive",
        unlock_condition="Upload 50 items",
        rarity="rare"
    ),
    BadgeType.HIDDEN_GEM_HUNTER: Badge(
        id=BadgeType.HIDDEN_GEM_HUNTER,
        name="Hidden Gem Hunter",
        description="Revived a forgotten wardrobe item",
        icon="Gem",
        unlock_condition="Complete Forgotten Gems challenge",
        rarity="common"
    ),
    BadgeType.TREASURE_HUNTER: Badge(
        id=BadgeType.TREASURE_HUNTER,
        name="Treasure Hunter",
        description="Completed 5 Forgotten Gems challenges",
        icon="TreasureChest",
        unlock_condition="Complete 5 Forgotten Gems challenges",
        rarity="epic"
    ),
    BadgeType.SUSTAINABLE_STYLE_BRONZE: Badge(
        id=BadgeType.SUSTAINABLE_STYLE_BRONZE,
        name="Sustainable Style (Bronze)",
        description="Wore an item 30 times",
        icon="Award",
        unlock_condition="Wear any item 30 times",
        rarity="common"
    ),
    BadgeType.SUSTAINABLE_STYLE_SILVER: Badge(
        id=BadgeType.SUSTAINABLE_STYLE_SILVER,
        name="Sustainable Style (Silver)",
        description="Wore an item 60 times",
        icon="Medal",
        unlock_condition="Wear any item 60 times",
        rarity="rare"
    ),
    BadgeType.SUSTAINABLE_STYLE_GOLD: Badge(
        id=BadgeType.SUSTAINABLE_STYLE_GOLD,
        name="Sustainable Style (Gold)",
        description="Wore an item 100 times",
        icon="Trophy",
        unlock_condition="Wear any item 100 times",
        rarity="legendary"
    ),
    BadgeType.COLOR_MASTER: Badge(
        id=BadgeType.COLOR_MASTER,
        name="Color Master",
        description="Completed color palette challenges",
        icon="Palette",
        unlock_condition="Complete color harmony challenge",
        rarity="rare"
    ),
    BadgeType.WEATHER_WARRIOR: Badge(
        id=BadgeType.WEATHER_WARRIOR,
        name="Weather Warrior",
        description="Mastered dressing for extreme weather",
        icon="Cloud",
        unlock_condition="Complete weather context challenge",
        rarity="rare"
    ),
    BadgeType.STYLE_CONTRIBUTOR: Badge(
        id=BadgeType.STYLE_CONTRIBUTOR,
        name="Style Contributor",
        description="Provided 25 outfit ratings",
        icon="Star",
        unlock_condition="Rate 25 outfits",
        rarity="common"
    ),
    BadgeType.AI_TRAINER: Badge(
        id=BadgeType.AI_TRAINER,
        name="AI Trainer",
        description="Provided 100 outfit ratings",
        icon="Brain",
        unlock_condition="Rate 100 outfits",
        rarity="epic"
    ),
}


# Level tier configuration
LEVEL_TIERS = [
    {"min_xp": 0, "max_xp": 2999, "tier": LevelTier.NOVICE, "levels": [1, 2, 3, 4]},
    {"min_xp": 3000, "max_xp": 6999, "tier": LevelTier.STYLIST, "levels": [5, 6, 7, 8, 9]},
    {"min_xp": 7000, "max_xp": 11999, "tier": LevelTier.CURATOR, "levels": [10, 11, 12, 13, 14]},
    {"min_xp": 12000, "max_xp": float('inf'), "tier": LevelTier.CONNOISSEUR, "levels": range(15, 100)},
]


# XP thresholds for each level
XP_PER_LEVEL = [
    0,      # Level 1
    250,    # Level 2
    600,    # Level 3
    1000,   # Level 4
    1500,   # Level 5
    2100,   # Level 6
    2800,   # Level 7
    3600,   # Level 8
    4500,   # Level 9
    5500,   # Level 10
    6600,   # Level 11
    7800,   # Level 12
    9100,   # Level 13
    10500,  # Level 14
    12000,  # Level 15
]

# After level 15, each level requires 2000 more XP
def get_xp_for_level(level: int) -> int:
    """Get XP required to reach a specific level"""
    if level <= len(XP_PER_LEVEL):
        return XP_PER_LEVEL[level - 1]
    else:
        # After level 15, each level requires 2000 more XP than the previous
        return XP_PER_LEVEL[-1] + (level - 15) * 2000


# Export all types
__all__ = [
    'ChallengeType',
    'ChallengeStatus',
    'BadgeType',
    'LevelTier',
    'UserRole',
    'GachaRarity',
    'Challenge',
    'UserChallenge',
    'Badge',
    'GamificationEvent',
    'XPReward',
    'LevelInfo',
    'GamificationState',
    'StreakData',
    'StyleTokens',
    'UserRoleData',
    'GachaPull',
    'CHALLENGE_CATALOG',
    'BADGE_DEFINITIONS',
    'LEVEL_TIERS',
    'XP_PER_LEVEL',
    'get_xp_for_level',
]

