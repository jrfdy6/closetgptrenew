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
    # ========== DAILY ENGAGEMENT CHALLENGES ==========
    "daily_logger": Challenge(
        id="daily_logger",
        type=ChallengeType.STREAK_MAINTENANCE,
        title="Daily Logger",
        description="Log an outfit every day for 7 days",
        rules={"streak_days": 7},
        rewards={"xp": 100, "tokens": 100, "badge": "daily_logger"},
        cadence="weekly",
        featured=True,
        icon="Calendar"
    ),
    "week_warrior": Challenge(
        id="week_warrior",
        type=ChallengeType.STREAK_MAINTENANCE,
        title="Week Warrior",
        description="Log outfits 7 days in a row",
        rules={"streak_days": 7},
        rewards={"xp": 150, "tokens": 150, "badge": "week_warrior"},
        cadence="weekly",
        featured=False,
        icon="Flame"
    ),
    "monthly_marathon": Challenge(
        id="monthly_marathon",
        type=ChallengeType.STREAK_MAINTENANCE,
        title="Monthly Marathon",
        description="Maintain a 30-day streak",
        rules={"streak_days": 30},
        rewards={"xp": 500, "tokens": 500, "badge": "monthly_marathon"},
        cadence="monthly",
        featured=True,
        icon="Trophy"
    ),
    "first_log_bonus": Challenge(
        id="first_log_bonus",
        type=ChallengeType.STREAK_MAINTENANCE,
        title="Early Bird",
        description="Log your first outfit of the day",
        rules={"first_log_today": True},
        rewards={"xp": 25, "tokens": 25},
        cadence="daily",
        featured=False,
        icon="Sunrise"
    ),
    # ========== WEEKLY VARIETY CHALLENGES ==========
    "outfit_variety_week": Challenge(
        id="outfit_variety_week",
        type=ChallengeType.CONTEXT,
        title="Variety Week",
        description="Log 5 different outfits this week",
        rules={"outfits_required": 5, "unique_outfits": True},
        rewards={"xp": 150, "tokens": 150, "badge": "variety_seeker"},
        cadence="weekly",
        featured=True,
        icon="Shuffle"
    ),
    "occasion_explorer": Challenge(
        id="occasion_explorer",
        type=ChallengeType.CONTEXT,
        title="Occasion Explorer",
        description="Log outfits for 3 different occasions this week",
        rules={"occasions_required": 3},
        rewards={"xp": 120, "tokens": 120, "badge": "occasion_explorer"},
        cadence="weekly",
        featured=False,
        icon="Map"
    ),
    "weather_adaptation": Challenge(
        id="weather_adaptation",
        type=ChallengeType.CONTEXT,
        title="Weather Adaptation",
        description="Log outfits for 3 different weather conditions",
        rules={"weather_conditions_required": 3},
        rewards={"xp": 100, "tokens": 100, "badge": BadgeType.WEATHER_WARRIOR.value},
        cadence="weekly",
        featured=False,
        icon="Cloud"
    ),
    "mood_swing": Challenge(
        id="mood_swing",
        type=ChallengeType.CONTEXT,
        title="Mood Swing",
        description="Log outfits with 4 different moods this week",
        rules={"moods_required": 4},
        rewards={"xp": 110, "tokens": 110, "badge": "mood_swing"},
        cadence="weekly",
        featured=False,
        icon="Heart"
    ),
    # ========== COLOR CHALLENGES ==========
    "monochrome_week": Challenge(
        id="monochrome_week",
        type=ChallengeType.COLOR_PALETTE,
        title="Monochrome Week",
        description="Create 3 monochrome outfits this week",
        rules={"outfits_required": 3, "color_rule": "monochrome"},
        rewards={"xp": 130, "tokens": 130, "badge": BadgeType.MONOCHROME_MAVEN.value},
        cadence="weekly",
        featured=True,
        icon="Palette"
    ),
    "color_explorer": Challenge(
        id="color_explorer",
        type=ChallengeType.COLOR_EXPLORER,
        title="Color Explorer",
        description="Use 5 different colors in your outfits this week",
        rules={"unique_colors_required": 5},
        rewards={"xp": 140, "tokens": 140, "badge": "color_explorer"},
        cadence="weekly",
        featured=False,
        icon="Rainbow"
    ),
    "bold_colors": Challenge(
        id="bold_colors",
        type=ChallengeType.COLOR_EXPLORER,
        title="Bold Colors",
        description="Create 2 outfits with bold/vibrant colors",
        rules={"outfits_required": 2, "color_intensity": "bold"},
        rewards={"xp": 100, "tokens": 100, "badge": "bold_stylist"},
        cadence="weekly",
        featured=False,
        icon="Sparkles"
    ),
    "neutral_master": Challenge(
        id="neutral_master",
        type=ChallengeType.COLOR_PALETTE,
        title="Neutral Master",
        description="Create 4 outfits using only neutral colors",
        rules={"outfits_required": 4, "color_rule": "neutral"},
        rewards={"xp": 120, "tokens": 120, "badge": "neutral_master"},
        cadence="weekly",
        featured=False,
        icon="Circle"
    ),
    # ========== ITEM EXPLORATION CHALLENGES ==========
    "new_item_explorer": Challenge(
        id="new_item_explorer",
        type=ChallengeType.FORGOTTEN_GEMS,
        title="New Item Explorer",
        description="Wear 3 items you've never worn before",
        rules={"items_required": 3, "never_worn": True},
        rewards={"xp": 150, "tokens": 150, "badge": "new_item_explorer"},
        cadence="weekly",
        featured=True,
        icon="Star"
    ),
    "dormant_revival": Challenge(
        id="dormant_revival",
        type=ChallengeType.FORGOTTEN_GEMS,
        title="Dormant Revival",
        description="Wear 5 items you haven't worn in 30+ days",
        rules={"days_dormant_min": 30, "items_required": 5},
        rewards={"xp": 200, "tokens": 200, "badge": "dormant_revival"},
        cadence="monthly",
        featured=True,
        icon="Revive"
    ),
    "category_rover": Challenge(
        id="category_rover",
        type=ChallengeType.CONTEXT,
        title="Category Rover",
        description="Wear items from 5 different categories this week",
        rules={"categories_required": 5},
        rewards={"xp": 130, "tokens": 130, "badge": "category_rover"},
        cadence="weekly",
        featured=False,
        icon="Grid"
    ),
    "favorite_rotation": Challenge(
        id="favorite_rotation",
        type=ChallengeType.FORGOTTEN_GEMS,
        title="Favorite Rotation",
        description="Wear 3 of your favorite items this week",
        rules={"items_required": 3, "favorite_only": True},
        rewards={"xp": 80, "tokens": 80, "badge": "favorite_rotation"},
        cadence="weekly",
        featured=False,
        icon="Heart"
    ),
    # ========== SUSTAINABILITY CHALLENGES ==========
    "sustainability_starter": Challenge(
        id="sustainability_starter",
        type=ChallengeType.SUSTAINABILITY_CHAMPION,
        title="Sustainability Starter",
        description="Wear any item 10 times",
        rules={"target_wears": 10},
        rewards={"xp": 75, "tokens": 75, "badge": "sustainability_starter"},
        cadence="always",
        featured=False,
        icon="Leaf"
    ),
    "sustainability_champion": Challenge(
        id="sustainability_champion",
        type=ChallengeType.SUSTAINABILITY_CHAMPION,
        title="Sustainability Champion",
        description="Wear 3 different items 20 times each",
        rules={"items_required": 3, "target_wears": 20},
        rewards={"xp": 300, "tokens": 300, "badge": "sustainability_champion"},
        cadence="monthly",
        featured=True,
        icon="Award"
    ),
    "cpw_optimizer": Challenge(
        id="cpw_optimizer",
        type=ChallengeType.CPW_OPTIMIZER,
        title="CPW Optimizer",
        description="Achieve CPW under $5 for 3 items",
        rules={"items_required": 3, "max_cpw": 5.0},
        rewards={"xp": 200, "tokens": 200, "badge": "cpw_optimizer"},
        cadence="monthly",
        featured=True,
        icon="TrendingDown"
    ),
    "value_maximizer": Challenge(
        id="value_maximizer",
        type=ChallengeType.CPW_OPTIMIZER,
        title="Value Maximizer",
        description="Get 5 items to $3 CPW or less",
        rules={"items_required": 5, "max_cpw": 3.0},
        rewards={"xp": 400, "tokens": 400, "badge": "value_maximizer"},
        cadence="monthly",
        featured=False,
        icon="DollarSign"
    ),
    # ========== PATTERN & STYLE CHALLENGES ==========
    "pattern_master": Challenge(
        id="pattern_master",
        type=ChallengeType.PATTERN_MASTER,
        title="Pattern Master",
        description="Create 3 outfits with pattern mixing",
        rules={"outfits_required": 3, "pattern_mixing": True},
        rewards={"xp": 180, "tokens": 180, "badge": "pattern_master"},
        cadence="weekly",
        featured=True,
        icon="Layers"
    ),
    "solid_stylist": Challenge(
        id="solid_stylist",
        type=ChallengeType.PATTERN_MASTER,
        title="Solid Stylist",
        description="Create 4 outfits using only solid colors (no patterns)",
        rules={"outfits_required": 4, "no_patterns": True},
        rewards={"xp": 120, "tokens": 120, "badge": "solid_stylist"},
        cadence="weekly",
        featured=False,
        icon="Square"
    ),
    "texture_explorer": Challenge(
        id="texture_explorer",
        type=ChallengeType.PATTERN_MASTER,
        title="Texture Explorer",
        description="Create 3 outfits mixing different textures",
        rules={"outfits_required": 3, "texture_mixing": True},
        rewards={"xp": 150, "tokens": 150, "badge": "texture_explorer"},
        cadence="weekly",
        featured=False,
        icon="Texture"
    ),
    # ========== FEEDBACK & AI CHALLENGES ==========
    "feedback_contributor": Challenge(
        id="feedback_contributor",
        type=ChallengeType.CONTEXT,
        title="Feedback Contributor",
        description="Rate 10 outfit suggestions this week",
        rules={"ratings_required": 10},
        rewards={"xp": 100, "tokens": 100, "badge": BadgeType.STYLE_CONTRIBUTOR.value},
        cadence="weekly",
        featured=True,
        icon="MessageSquare"
    ),
    "ai_trainer_weekly": Challenge(
        id="ai_trainer_weekly",
        type=ChallengeType.CONTEXT,
        title="AI Trainer",
        description="Rate 25 outfit suggestions",
        rules={"ratings_required": 25},
        rewards={"xp": 250, "tokens": 250, "badge": BadgeType.AI_TRAINER.value},
        cadence="monthly",
        featured=False,
        icon="Brain"
    ),
    "feedback_streak": Challenge(
        id="feedback_streak",
        type=ChallengeType.STREAK_MAINTENANCE,
        title="Feedback Streak",
        description="Rate outfits 5 days in a row",
        rules={"ratings_days": 5},
        rewards={"xp": 120, "tokens": 120, "badge": "feedback_streak"},
        cadence="weekly",
        featured=False,
        icon="TrendingUp"
    ),
    # ========== UPLOAD & CATALOG CHALLENGES ==========
    "wardrobe_builder": Challenge(
        id="wardrobe_builder",
        type=ChallengeType.COLD_START,
        title="Wardrobe Builder",
        description="Upload 25 items to your wardrobe",
        rules={"items_required": 25},
        rewards={"xp": 150, "tokens": 150, "badge": "wardrobe_builder"},
        cadence="always",
        featured=False,
        icon="Package"
    ),
    "wardrobe_expander": Challenge(
        id="wardrobe_expander",
        type=ChallengeType.COLD_START,
        title="Wardrobe Expander",
        description="Upload 100 items to your wardrobe",
        rules={"items_required": 100},
        rewards={"xp": 500, "tokens": 500, "badge": "wardrobe_expander"},
        cadence="always",
        featured=True,
        icon="Archive"
    ),
    "complete_catalog": Challenge(
        id="complete_catalog",
        type=ChallengeType.COLD_START,
        title="Complete Catalog",
        description="Upload items from all 8 categories",
        rules={"categories_required": 8},
        rewards={"xp": 200, "tokens": 200, "badge": "complete_catalog"},
        cadence="always",
        featured=False,
        icon="CheckCircle"
    ),
    "new_upload_week": Challenge(
        id="new_upload_week",
        type=ChallengeType.COLD_START,
        title="New Upload Week",
        description="Upload 5 new items this week",
        rules={"items_required": 5},
        rewards={"xp": 100, "tokens": 100, "badge": "new_upload_week"},
        cadence="weekly",
        featured=False,
        icon="Plus"
    ),
    # ========== GACHA & TOKEN CHALLENGES ==========
    "first_gacha_pull": Challenge(
        id="first_gacha_pull",
        type=ChallengeType.GACHA_PULL,
        title="First Pull",
        description="Perform your first gacha pull",
        rules={"pulls_required": 1},
        rewards={"xp": 50, "tokens": 0, "badge": "first_pull"},
        cadence="always",
        featured=True,
        icon="Gift"
    ),
    "gacha_collector": Challenge(
        id="gacha_collector",
        type=ChallengeType.GACHA_PULL,
        title="Gacha Collector",
        description="Perform 5 gacha pulls",
        rules={"pulls_required": 5},
        rewards={"xp": 300, "tokens": 0, "badge": "gacha_collector"},
        cadence="monthly",
        featured=False,
        icon="Collection"
    ),
    "token_saver": Challenge(
        id="token_saver",
        type=ChallengeType.GACHA_PULL,
        title="Token Saver",
        description="Accumulate 1000 tokens",
        rules={"token_balance_required": 1000},
        rewards={"xp": 200, "tokens": 0, "badge": "token_saver"},
        cadence="always",
        featured=False,
        icon="PiggyBank"
    ),
    "legendary_hunter": Challenge(
        id="legendary_hunter",
        type=ChallengeType.GACHA_PULL,
        title="Legendary Hunter",
        description="Pull a legendary reward from gacha",
        rules={"rarity_required": "legendary"},
        rewards={"xp": 500, "tokens": 0, "badge": "legendary_hunter"},
        cadence="always",
        featured=True,
        icon="Crown"
    ),
    # ========== ROLE & STATUS CHALLENGES ==========
    "role_promotion": Challenge(
        id="role_promotion",
        type=ChallengeType.ROLE_DEFENSE,
        title="Role Promotion",
        description="Reach Explorer role",
        rules={"target_role": "explorer"},
        rewards={"xp": 150, "tokens": 150, "badge": "role_promotion"},
        cadence="always",
        featured=True,
        icon="ArrowUp"
    ),
    "role_master": Challenge(
        id="role_master",
        type=ChallengeType.ROLE_DEFENSE,
        title="Role Master",
        description="Reach Master role",
        rules={"target_role": "master"},
        rewards={"xp": 1000, "tokens": 1000, "badge": "role_master"},
        cadence="always",
        featured=True,
        icon="Star"
    ),
    "role_defender": Challenge(
        id="role_defender",
        type=ChallengeType.ROLE_DEFENSE,
        title="Role Defender",
        description="Maintain Master role for 4 weeks",
        rules={"role": "master", "weeks_required": 4},
        rewards={"xp": 400, "tokens": 400, "badge": "role_defender"},
        cadence="monthly",
        featured=False,
        icon="Shield"
    ),
    # ========== SEASONAL & THEMED CHALLENGES ==========
    "seasonal_stylist": Challenge(
        id="seasonal_stylist",
        type=ChallengeType.THEMED_EVENT,
        title="Seasonal Stylist",
        description="Log 5 outfits appropriate for current season",
        rules={"outfits_required": 5, "seasonal": True},
        rewards={"xp": 150, "tokens": 150, "badge": "seasonal_stylist"},
        cadence="monthly",
        featured=True,
        icon="Sun"
    ),
    "holiday_special": Challenge(
        id="holiday_special",
        type=ChallengeType.THEMED_EVENT,
        title="Holiday Special",
        description="Create 3 outfits for a holiday/event",
        rules={"outfits_required": 3, "themed": True},
        rewards={"xp": 180, "tokens": 180, "badge": "holiday_special"},
        cadence="monthly",
        featured=False,
        icon="Party"
    ),
    "weekend_warrior": Challenge(
        id="weekend_warrior",
        type=ChallengeType.THEMED_EVENT,
        title="Weekend Warrior",
        description="Log outfits on both weekend days",
        rules={"weekend_days": 2},
        rewards={"xp": 80, "tokens": 80, "badge": "weekend_warrior"},
        cadence="weekly",
        featured=False,
        icon="Calendar"
    ),
    # ========== CONSISTENCY CHALLENGES ==========
    "weekly_consistency": Challenge(
        id="weekly_consistency",
        type=ChallengeType.STREAK_MAINTENANCE,
        title="Weekly Consistency",
        description="Log at least 5 outfits this week",
        rules={"outfits_required": 5},
        rewards={"xp": 120, "tokens": 120, "badge": "weekly_consistency"},
        cadence="weekly",
        featured=True,
        icon="Check"
    ),
    "monthly_consistency": Challenge(
        id="monthly_consistency",
        type=ChallengeType.STREAK_MAINTENANCE,
        title="Monthly Consistency",
        description="Log at least 20 outfits this month",
        rules={"outfits_required": 20},
        rewards={"xp": 400, "tokens": 400, "badge": "monthly_consistency"},
        cadence="monthly",
        featured=True,
        icon="Calendar"
    ),
    "quarterly_consistency": Challenge(
        id="quarterly_consistency",
        type=ChallengeType.STREAK_MAINTENANCE,
        title="Quarterly Consistency",
        description="Log at least 60 outfits in 3 months",
        rules={"outfits_required": 60, "months": 3},
        rewards={"xp": 1000, "tokens": 1000, "badge": "quarterly_consistency"},
        cadence="quarterly",
        featured=True,
        icon="Trophy"
    ),
    # ========== EXPLORATION CHALLENGES ==========
    "style_explorer": Challenge(
        id="style_explorer",
        type=ChallengeType.CONTEXT,
        title="Style Explorer",
        description="Try 3 different style categories this week",
        rules={"styles_required": 3},
        rewards={"xp": 130, "tokens": 130, "badge": "style_explorer"},
        cadence="weekly",
        featured=False,
        icon="Compass"
    ),
    "formality_range": Challenge(
        id="formality_range",
        type=ChallengeType.CONTEXT,
        title="Formality Range",
        description="Log outfits across all formality levels",
        rules={"formality_levels_required": 4},
        rewards={"xp": 140, "tokens": 140, "badge": "formality_range"},
        cadence="weekly",
        featured=False,
        icon="Sliders"
    ),
    "versatile_pro": Challenge(
        id="versatile_pro",
        type=ChallengeType.CONTEXT,
        title="Versatile Pro",
        description="Create outfits for 5 different contexts",
        rules={"contexts_required": 5},
        rewards={"xp": 200, "tokens": 200, "badge": BadgeType.VERSATILE_PRO.value},
        cadence="monthly",
        featured=True,
        icon="Zap"
    ),
    # ========== MILESTONE CHALLENGES ==========
    "first_10_outfits": Challenge(
        id="first_10_outfits",
        type=ChallengeType.COLD_START,
        title="First 10",
        description="Log your first 10 outfits",
        rules={"outfits_required": 10},
        rewards={"xp": 100, "tokens": 100, "badge": "first_10"},
        cadence="always",
        featured=True,
        icon="Target"
    ),
    "century_club": Challenge(
        id="century_club",
        type=ChallengeType.COLD_START,
        title="Century Club",
        description="Log 100 outfits total",
        rules={"outfits_required": 100},
        rewards={"xp": 500, "tokens": 500, "badge": "century_club"},
        cadence="always",
        featured=True,
        icon="Award"
    ),
    "five_hundred_club": Challenge(
        id="five_hundred_club",
        type=ChallengeType.COLD_START,
        title="500 Club",
        description="Log 500 outfits total",
        rules={"outfits_required": 500},
        rewards={"xp": 2000, "tokens": 2000, "badge": "five_hundred_club"},
        cadence="always",
        featured=True,
        icon="Star"
    ),
    # ========== LIMITED TIME / SCARCITY CHALLENGES ==========
    "flash_challenge": Challenge(
        id="flash_challenge",
        type=ChallengeType.SCARCITY_EVENT,
        title="Flash Challenge",
        description="Log 3 outfits in 24 hours",
        rules={"outfits_required": 3, "time_limit_hours": 24},
        rewards={"xp": 150, "tokens": 150, "badge": "flash_challenge"},
        cadence="weekly",
        featured=True,
        icon="Clock"
    ),
    "weekend_sprint": Challenge(
        id="weekend_sprint",
        type=ChallengeType.SCARCITY_EVENT,
        title="Weekend Sprint",
        description="Log 4 outfits over the weekend",
        rules={"outfits_required": 4, "weekend_only": True},
        rewards={"xp": 120, "tokens": 120, "badge": "weekend_sprint"},
        cadence="weekly",
        featured=False,
        icon="Zap"
    ),
    # ========== SPECIAL ACHIEVEMENTS ==========
    "perfect_week": Challenge(
        id="perfect_week",
        type=ChallengeType.STREAK_MAINTENANCE,
        title="Perfect Week",
        description="Log an outfit every single day for 7 days",
        rules={"days_required": 7, "consecutive": True},
        rewards={"xp": 200, "tokens": 200, "badge": "perfect_week"},
        cadence="weekly",
        featured=True,
        icon="CheckCircle"
    ),
    "level_up_achiever": Challenge(
        id="level_up_achiever",
        type=ChallengeType.COLD_START,
        title="Level Up Achiever",
        description="Reach level 5",
        rules={"target_level": 5},
        rewards={"xp": 300, "tokens": 300, "badge": "level_up_achiever"},
        cadence="always",
        featured=True,
        icon="TrendingUp"
    ),
    "badge_collector": Challenge(
        id="badge_collector",
        type=ChallengeType.COLD_START,
        title="Badge Collector",
        description="Earn 10 different badges",
        rules={"badges_required": 10},
        rewards={"xp": 400, "tokens": 400, "badge": "badge_collector"},
        cadence="always",
        featured=True,
        icon="Award"
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

