"""
Unit Tests for Validation Functions

This module contains comprehensive tests for all modular validation functions
used in the outfit generation pipeline. Tests cover typical cases, edge cases,
and invalid inputs to ensure robust validation.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from typing import List, Dict, Any
from dataclasses import dataclass

# Import validation functions and types
from src.services.validation_orchestrator import ValidationOrchestrator, ValidationResult, ValidationStep
from src.services.outfit_service import OutfitService
from src.custom_types.wardrobe import ClothingItem, ClothingType, Season
from src.custom_types.profile import UserProfile
from src.custom_types.weather import WeatherData
from src.utils.layering import validate_layering_compatibility
from src.custom_types.outfit_rules import validate_outfit_requirements


@dataclass
class MockClothingItem:
    """Mock clothing item for testing."""
    id: str
    name: str
    type: ClothingType
    tags: List[str]
    style: List[str]
    dominantColors: List[Dict[str, Any]]
    matchingColors: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    imageUrl: str = "https://example.com/image.jpg"
    occasion: List[str] = None
    season: List[Season] = None
    
    def __post_init__(self):
        if self.occasion is None:
            self.occasion = ["casual"]
        if self.season is None:
            self.season = [Season.SPRING]


@dataclass
class MockUserProfile:
    """Mock user profile for testing."""
    id: str
    name: str
    email: str
    bodyType: str = "athletic"
    skinTone: str = "medium"
    fitPreference: str = "regular"
    stylePreferences: List[str] = None
    
    def __post_init__(self):
        if self.stylePreferences is None:
            self.stylePreferences = ["casual", "minimalist"]


@dataclass
class MockWeatherData:
    """Mock weather data for testing."""
    temperature: float
    condition: str
    humidity: float = 50.0
    windSpeed: float = 10.0
    location: str = "New York"
    timestamp: int = 1234567890


class TestValidationOrchestrator:
    """Test suite for ValidationOrchestrator functions."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create a ValidationOrchestrator instance for testing."""
        mock_outfit_service = Mock()
        return ValidationOrchestrator(mock_outfit_service)
    
    @pytest.fixture
    def sample_items(self):
        """Create sample clothing items for testing."""
        return [
            MockClothingItem(
                id="1",
                name="Blue T-Shirt",
                type=ClothingType.SHIRT,
                tags=["casual", "cotton"],
                style=["casual", "minimalist"],
                dominantColors=[{"name": "blue", "hex": "#0000FF", "rgb": [0, 0, 255]}],
                matchingColors=[{"name": "navy", "hex": "#000080", "rgb": [0, 0, 128]}],
                metadata={"material": "cotton", "fit": "regular"}
            ),
            MockClothingItem(
                id="2",
                name="Black Jeans",
                type=ClothingType.PANTS,
                tags=["casual", "denim"],
                style=["casual", "minimalist"],
                dominantColors=[{"name": "black", "hex": "#000000", "rgb": [0, 0, 0]}],
                matchingColors=[{"name": "gray", "hex": "#808080", "rgb": [128, 128, 128]}],
                metadata={"material": "denim", "fit": "regular"}
            ),
            MockClothingItem(
                id="3",
                name="White Sneakers",
                type=ClothingType.SHOES,
                tags=["casual", "athletic"],
                style=["casual", "sporty"],
                dominantColors=[{"name": "white", "hex": "#FFFFFF", "rgb": [255, 255, 255]}],
                matchingColors=[{"name": "gray", "hex": "#808080", "rgb": [128, 128, 128]}],
                metadata={"material": "canvas", "fit": "regular"}
            )
        ]
    
    @pytest.fixture
    def sample_context(self):
        """Create sample context for testing."""
        return {
            "occasion": "casual",
            "weather": MockWeatherData(temperature=70.0, condition="sunny"),
            "style": "minimalist",
            "target_counts": {
                "min_items": 3,
                "max_items": 6,
                "required_categories": ["top", "bottom", "shoes"]
            }
        }
    
    @pytest.mark.asyncio
    async def test_validate_occasion_appropriateness_success(self, orchestrator, sample_items, sample_context):
        """Test successful occasion appropriateness validation."""
        result = await orchestrator._validate_occasion_appropriateness(sample_items, sample_context)
        
        assert isinstance(result, ValidationResult)
        assert result.step == ValidationStep.OCCASION_APPROPRIATENESS
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
        assert "occasion" in result.metadata
        assert result.duration > 0
    
    @pytest.mark.asyncio
    async def test_validate_occasion_appropriateness_formal_failure(self, orchestrator, sample_items):
        """Test occasion appropriateness validation for formal occasion with casual items."""
        context = {
            "occasion": "formal",
            "weather": MockWeatherData(temperature=70.0, condition="sunny"),
            "style": "formal"
        }
        
        result = await orchestrator._validate_occasion_appropriateness(sample_items, context)
        
        assert isinstance(result, ValidationResult)
        assert result.step == ValidationStep.OCCASION_APPROPRIATENESS
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("not appropriate for formal" in error for error in result.errors)
    
    @pytest.mark.asyncio
    async def test_validate_layer_count_appropriateness_cold_weather(self, orchestrator, sample_items):
        """Test layer count validation for cold weather."""
        context = {
            "occasion": "casual",
            "weather": MockWeatherData(temperature=30.0, condition="cold"),
            "style": "minimalist"
        }
        
        result = await orchestrator._validate_layer_count_appropriateness(sample_items, context)
        
        assert isinstance(result, ValidationResult)
        assert result.step == ValidationStep.LAYER_COUNT_APPROPRIATENESS
        assert "layer_count" in result.metadata
        assert "temperature" in result.metadata
        assert result.metadata["temperature"] == 30.0
    
    @pytest.mark.asyncio
    async def test_validate_layer_count_appropriateness_hot_weather(self, orchestrator, sample_items):
        """Test layer count validation for hot weather."""
        context = {
            "occasion": "casual",
            "weather": MockWeatherData(temperature=90.0, condition="hot"),
            "style": "minimalist"
        }
        
        result = await orchestrator._validate_layer_count_appropriateness(sample_items, context)
        
        assert isinstance(result, ValidationResult)
        assert result.step == ValidationStep.LAYER_COUNT_APPROPRIATENESS
        # Should have warnings about too many layers for hot weather
        assert len(result.warnings) > 0 or result.is_valid is True
    
    @pytest.mark.asyncio
    async def test_validate_form_completeness_success(self, orchestrator, sample_items, sample_context):
        """Test successful form completeness validation."""
        result = await orchestrator._validate_form_completeness(sample_items, sample_context)
        
        assert isinstance(result, ValidationResult)
        assert result.step == ValidationStep.FORM_COMPLETENESS
        assert result.is_valid is True
        assert "item_count" in result.metadata
        assert "category_counts" in result.metadata
        assert result.metadata["item_count"] == 3
    
    @pytest.mark.asyncio
    async def test_validate_form_completeness_too_few_items(self, orchestrator):
        """Test form completeness validation with too few items."""
        items = [
            MockClothingItem(
                id="1",
                name="Blue T-Shirt",
                type=ClothingType.SHIRT,
                tags=["casual"],
                style=["casual"],
                dominantColors=[{"name": "blue", "hex": "#0000FF", "rgb": [0, 0, 255]}],
                matchingColors=[],
                metadata={}
            )
        ]
        context = {
            "target_counts": {
                "min_items": 3,
                "max_items": 6,
                "required_categories": ["top", "bottom", "shoes"]
            }
        }
        
        result = await orchestrator._validate_form_completeness(items, context)
        
        assert isinstance(result, ValidationResult)
        assert result.step == ValidationStep.FORM_COMPLETENESS
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("minimum 3 required" in error for error in result.errors)
    
    @pytest.mark.asyncio
    async def test_validate_form_completeness_missing_categories(self, orchestrator):
        """Test form completeness validation with missing required categories."""
        items = [
            MockClothingItem(
                id="1",
                name="Blue T-Shirt",
                type=ClothingType.SHIRT,
                tags=["casual"],
                style=["casual"],
                dominantColors=[{"name": "blue", "hex": "#0000FF", "rgb": [0, 0, 255]}],
                matchingColors=[],
                metadata={}
            ),
            MockClothingItem(
                id="2",
                name="Black Jeans",
                type=ClothingType.PANTS,
                tags=["casual"],
                style=["casual"],
                dominantColors=[{"name": "black", "hex": "#000000", "rgb": [0, 0, 0]}],
                matchingColors=[],
                metadata={}
            )
        ]
        context = {
            "target_counts": {
                "min_items": 2,
                "max_items": 6,
                "required_categories": ["top", "bottom", "shoes"]
            }
        }
        
        result = await orchestrator._validate_form_completeness(items, context)
        
        assert isinstance(result, ValidationResult)
        assert result.step == ValidationStep.FORM_COMPLETENESS
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("Missing required category: shoes" in error for error in result.errors)
    
    @pytest.mark.asyncio
    async def test_validate_weather_compatibility_success(self, orchestrator, sample_items, sample_context):
        """Test successful weather compatibility validation."""
        result = await orchestrator._validate_weather_compatibility(sample_items, sample_context)
        
        assert isinstance(result, ValidationResult)
        assert result.step == ValidationStep.WEATHER_COMPATIBILITY
        assert result.duration > 0
    
    @pytest.mark.asyncio
    async def test_validate_style_cohesion_success(self, orchestrator, sample_items, sample_context):
        """Test successful style cohesion validation."""
        result = await orchestrator._validate_style_cohesion(sample_items, sample_context)
        
        assert isinstance(result, ValidationResult)
        assert result.step == ValidationStep.STYLE_COHESION
        assert result.duration > 0
    
    @pytest.mark.asyncio
    async def test_validate_body_type_compatibility_success(self, orchestrator, sample_items, sample_context):
        """Test successful body type compatibility validation."""
        result = await orchestrator._validate_body_type_compatibility(sample_items, sample_context)
        
        assert isinstance(result, ValidationResult)
        assert result.step == ValidationStep.BODY_TYPE_COMPATIBILITY
        assert result.duration > 0
    
    @pytest.mark.asyncio
    async def test_validate_color_harmony_success(self, orchestrator, sample_items, sample_context):
        """Test successful color harmony validation."""
        result = await orchestrator._validate_color_harmony(sample_items, sample_context)
        
        assert isinstance(result, ValidationResult)
        assert result.step == ValidationStep.COLOR_HARMONY
        assert result.duration > 0
    
    @pytest.mark.asyncio
    async def test_validate_deduplication_success(self, orchestrator, sample_items, sample_context):
        """Test successful deduplication validation."""
        result = await orchestrator._validate_deduplication(sample_items, sample_context)
        
        assert isinstance(result, ValidationResult)
        assert result.step == ValidationStep.DEDUPLICATION
        assert result.duration > 0
    
    @pytest.mark.asyncio
    async def test_validate_deduplication_with_duplicates(self, orchestrator, sample_items, sample_context):
        """Test deduplication validation with duplicate items."""
        # Add a duplicate item
        duplicate_item = MockClothingItem(
            id="1",  # Same ID as first item
            name="Blue T-Shirt",
            type=ClothingType.SHIRT,
            tags=["casual", "cotton"],
            style=["casual", "minimalist"],
            dominantColors=[{"name": "blue", "hex": "#0000FF", "rgb": [0, 0, 255]}],
            matchingColors=[{"name": "navy", "hex": "#000080", "rgb": [0, 0, 128]}],
            metadata={"material": "cotton", "fit": "regular"}
        )
        items_with_duplicate = sample_items + [duplicate_item]
        
        result = await orchestrator._validate_deduplication(items_with_duplicate, sample_context)
        
        assert isinstance(result, ValidationResult)
        assert result.step == ValidationStep.DEDUPLICATION
        # Should detect duplicates
        assert result.is_valid is False or len(result.warnings) > 0
    
    @pytest.mark.asyncio
    async def test_validate_layering_compliance_success(self, orchestrator, sample_items, sample_context):
        """Test successful layering compliance validation."""
        result = await orchestrator._validate_layering_compliance(sample_items, sample_context)
        
        assert isinstance(result, ValidationResult)
        assert result.step == ValidationStep.LAYERING_COMPLIANCE
        assert result.duration > 0
    
    @pytest.mark.asyncio
    async def test_run_validation_pipeline_success(self, orchestrator, sample_items, sample_context):
        """Test successful validation pipeline execution."""
        result = await orchestrator.run_validation_pipeline(sample_items, sample_context)
        
        assert isinstance(result, dict)
        assert "is_valid" in result
        assert "errors" in result
        assert "warnings" in result
        assert "step_results" in result
        assert "step_summary" in result
        assert "total_duration" in result
        assert "steps_executed" in result
        assert "success_rate" in result
        assert result["total_duration"] > 0
        assert result["steps_executed"] > 0
        assert 0 <= result["success_rate"] <= 1


class TestOutfitServiceValidation:
    """Test suite for OutfitService validation functions."""
    
    @pytest.fixture
    def outfit_service(self):
        """Create an OutfitService instance for testing."""
        return OutfitService()
    
    @pytest.fixture
    def sample_items(self):
        """Create sample clothing items for testing."""
        return [
            MockClothingItem(
                id="1",
                name="Blue T-Shirt",
                type=ClothingType.SHIRT,
                tags=["casual", "cotton"],
                style=["casual", "minimalist"],
                dominantColors=[{"name": "blue", "hex": "#0000FF", "rgb": [0, 0, 255]}],
                matchingColors=[{"name": "navy", "hex": "#000080", "rgb": [0, 0, 128]}],
                metadata={"material": "cotton", "fit": "regular"}
            ),
            MockClothingItem(
                id="2",
                name="Black Jeans",
                type=ClothingType.PANTS,
                tags=["casual", "denim"],
                style=["casual", "minimalist"],
                dominantColors=[{"name": "black", "hex": "#000000", "rgb": [0, 0, 0]}],
                matchingColors=[{"name": "gray", "hex": "#808080", "rgb": [128, 128, 128]}],
                metadata={"material": "denim", "fit": "regular"}
            )
        ]
    
    def test_validate_occasion_rules_success(self, outfit_service, sample_items):
        """Test successful occasion rules validation."""
        result = outfit_service._validate_occasion_rules(sample_items, "casual")
        
        assert isinstance(result, dict)
        assert "is_valid" in result
        assert "errors" in result
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0
    
    def test_validate_occasion_rules_gym_failure(self, outfit_service, sample_items):
        """Test occasion rules validation for gym with inappropriate items."""
        result = outfit_service._validate_occasion_rules(sample_items, "gym")
        
        assert isinstance(result, dict)
        assert "is_valid" in result
        assert "errors" in result
        # Should have errors for non-athletic items in gym
        assert result["is_valid"] is False or len(result["errors"]) > 0
    
    def test_validate_weather_appropriateness_success(self, outfit_service, sample_items):
        """Test successful weather appropriateness validation."""
        weather = MockWeatherData(temperature=70.0, condition="sunny")
        result = outfit_service._validate_weather_appropriateness(sample_items, weather)
        
        assert isinstance(result, dict)
        assert "is_valid" in result
        assert "errors" in result
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0
    
    def test_validate_weather_appropriateness_extreme_cold(self, outfit_service, sample_items):
        """Test weather appropriateness validation for extreme cold."""
        weather = MockWeatherData(temperature=10.0, condition="cold")
        result = outfit_service._validate_weather_appropriateness(sample_items, weather)
        
        assert isinstance(result, dict)
        assert "is_valid" in result
        assert "errors" in result
        # Should have errors for inappropriate items in extreme cold
        assert result["is_valid"] is False or len(result["errors"]) > 0
    
    def test_validate_style_cohesion_success(self, outfit_service, sample_items):
        """Test successful style cohesion validation."""
        result = outfit_service._validate_style_cohesion(sample_items, "minimalist")
        
        assert isinstance(result, dict)
        assert "is_valid" in result
        assert "warnings" in result
        assert result["is_valid"] is True
    
    def test_validate_style_cohesion_conflict(self, outfit_service, sample_items):
        """Test style cohesion validation with conflicting styles."""
        # Add an item with conflicting style
        conflicting_item = MockClothingItem(
            id="3",
            name="Formal Blazer",
            type=ClothingType.JACKET,
            tags=["formal", "business"],
            style=["formal", "business"],
            dominantColors=[{"name": "navy", "hex": "#000080", "rgb": [0, 0, 128]}],
            matchingColors=[],
            metadata={}
        )
        items_with_conflict = sample_items + [conflicting_item]
        
        result = outfit_service._validate_style_cohesion(items_with_conflict, "minimalist")
        
        assert isinstance(result, dict)
        assert "is_valid" in result
        assert "warnings" in result
        # Should have warnings about style conflicts
        assert len(result["warnings"]) > 0
    
    def test_validate_visual_harmony_success(self, outfit_service, sample_items):
        """Test successful visual harmony validation."""
        result = outfit_service._validate_visual_harmony(sample_items)
        
        assert isinstance(result, dict)
        assert "is_valid" in result
        assert "warnings" in result
    
    def test_validate_visual_harmony_color_clash(self, outfit_service):
        """Test visual harmony validation with color clash."""
        items_with_clash = [
            MockClothingItem(
                id="1",
                name="Red Shirt",
                type=ClothingType.SHIRT,
                tags=["casual"],
                style=["casual"],
                dominantColors=[{"name": "red", "hex": "#FF0000", "rgb": [255, 0, 0]}],
                matchingColors=[],
                metadata={}
            ),
            MockClothingItem(
                id="2",
                name="Green Pants",
                type=ClothingType.PANTS,
                tags=["casual"],
                style=["casual"],
                dominantColors=[{"name": "green", "hex": "#00FF00", "rgb": [0, 255, 0]}],
                matchingColors=[],
                metadata={}
            )
        ]
        
        result = outfit_service._validate_visual_harmony(items_with_clash)
        
        assert isinstance(result, dict)
        assert "is_valid" in result
        assert "warnings" in result
        # Should have warnings about color clash
        assert len(result["warnings"]) > 0
    
    def test_final_outfit_validation_success(self, outfit_service, sample_items):
        """Test successful final outfit validation."""
        context = {
            "occasion": "casual",
            "weather": MockWeatherData(temperature=70.0, condition="sunny"),
            "style": "minimalist",
            "target_counts": {
                "min_items": 2,
                "max_items": 6,
                "required_categories": ["top", "bottom"]
            }
        }
        
        result = outfit_service._final_outfit_validation(sample_items, context)
        
        assert isinstance(result, dict)
        assert "is_valid" in result
        assert "errors" in result
        assert "warnings" in result
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0
    
    def test_final_outfit_validation_duplicates(self, outfit_service, sample_items):
        """Test final outfit validation with duplicate items."""
        # Add a duplicate item
        duplicate_item = MockClothingItem(
            id="1",  # Same ID as first item
            name="Blue T-Shirt",
            type=ClothingType.SHIRT,
            tags=["casual", "cotton"],
            style=["casual", "minimalist"],
            dominantColors=[{"name": "blue", "hex": "#0000FF", "rgb": [0, 0, 255]}],
            matchingColors=[{"name": "navy", "hex": "#000080", "rgb": [0, 0, 128]}],
            metadata={"material": "cotton", "fit": "regular"}
        )
        items_with_duplicate = sample_items + [duplicate_item]
        
        context = {
            "occasion": "casual",
            "weather": MockWeatherData(temperature=70.0, condition="sunny"),
            "style": "minimalist",
            "target_counts": {
                "min_items": 2,
                "max_items": 6,
                "required_categories": ["top", "bottom"]
            }
        }
        
        result = outfit_service._final_outfit_validation(items_with_duplicate, context)
        
        assert isinstance(result, dict)
        assert "is_valid" in result
        assert "errors" in result
        assert "warnings" in result
        # Should detect duplicates
        assert result["is_valid"] is False or len(result["errors"]) > 0


class TestLayeringValidation:
    """Test suite for layering validation functions."""
    
    def test_validate_layering_compatibility_success(self):
        """Test successful layering compatibility validation."""
        items = [
            {"type": "shirt", "layerLevel": "base", "warmthFactor": "medium"},
            {"type": "jacket", "layerLevel": "outer", "warmthFactor": "heavy"},
            {"type": "pants", "layerLevel": "base", "warmthFactor": "medium"}
        ]
        
        result = validate_layering_compatibility(items, 50.0)
        
        assert isinstance(result, dict)
        assert "errors" in result
        assert "warnings" in result
        assert "is_valid" in result
        assert result["is_valid"] is True
    
    def test_validate_layering_compatibility_insufficient_layers(self):
        """Test layering compatibility validation with insufficient layers."""
        items = [
            {"type": "shirt", "layerLevel": "base", "warmthFactor": "medium"}
        ]
        
        result = validate_layering_compatibility(items, 30.0)
        
        assert isinstance(result, dict)
        assert "errors" in result
        assert "warnings" in result
        assert "is_valid" in result
        # Should have errors for insufficient layering in cold weather
        assert result["is_valid"] is False or len(result["errors"]) > 0
    
    def test_validate_layering_compatibility_too_many_layers(self):
        """Test layering compatibility validation with too many layers."""
        items = [
            {"type": "shirt", "layerLevel": "base", "warmthFactor": "medium"},
            {"type": "sweater", "layerLevel": "middle", "warmthFactor": "heavy"},
            {"type": "jacket", "layerLevel": "outer", "warmthFactor": "heavy"},
            {"type": "coat", "layerLevel": "outer", "warmthFactor": "heavy"},
            {"type": "pants", "layerLevel": "base", "warmthFactor": "medium"}
        ]
        
        result = validate_layering_compatibility(items, 80.0)
        
        assert isinstance(result, dict)
        assert "errors" in result
        assert "warnings" in result
        assert "is_valid" in result
        # Should have warnings for too many layers in hot weather
        assert len(result["warnings"]) > 0


class TestOutfitRequirementsValidation:
    """Test suite for outfit requirements validation."""
    
    def test_validate_outfit_requirements_success(self):
        """Test successful outfit requirements validation."""
        outfit_items = [
            {"type": "shirt", "color": "blue"},
            {"type": "pants", "color": "black"},
            {"type": "shoes", "color": "white"}
        ]
        
        result = validate_outfit_requirements(outfit_items, 70.0, "casual", "confident")
        
        assert isinstance(result, dict)
        assert "is_valid" in result
        assert "warnings" in result
        assert "suggestions" in result
        assert result["is_valid"] is True
    
    def test_validate_outfit_requirements_insufficient_layering(self):
        """Test outfit requirements validation with insufficient layering."""
        outfit_items = [
            {"type": "shirt", "color": "blue"},
            {"type": "pants", "color": "black"}
        ]
        
        result = validate_outfit_requirements(outfit_items, 30.0, "casual", "confident")
        
        assert isinstance(result, dict)
        assert "is_valid" in result
        assert "warnings" in result
        assert "suggestions" in result
        # Should have warnings for insufficient layering in cold weather
        assert result["is_valid"] is False or len(result["warnings"]) > 0
    
    def test_validate_outfit_requirements_missing_required_items(self):
        """Test outfit requirements validation with missing required items."""
        outfit_items = [
            {"type": "shirt", "color": "blue"},
            {"type": "shoes", "color": "white"}
        ]
        
        result = validate_outfit_requirements(outfit_items, 70.0, "formal", "confident")
        
        assert isinstance(result, dict)
        assert "is_valid" in result
        assert "warnings" in result
        assert "suggestions" in result
        # Should have warnings for missing required items in formal occasion
        assert result["is_valid"] is False or len(result["warnings"]) > 0


class TestUtilsValidation:
    """Test suite for utility validation functions."""
    
    @pytest.fixture
    def sample_items(self):
        """Create sample clothing items for testing."""
        return [
            MockClothingItem(
                id="1",
                name="Blue T-Shirt",
                type=ClothingType.SHIRT,
                tags=["casual", "cotton"],
                style=["casual", "minimalist"],
                dominantColors=[{"name": "blue", "hex": "#0000FF", "rgb": [0, 0, 255]}],
                matchingColors=[{"name": "navy", "hex": "#000080", "rgb": [0, 0, 128]}],
                metadata={"material": "cotton", "fit": "regular"}
            ),
            MockClothingItem(
                id="2",
                name="Black Jeans",
                type=ClothingType.PANTS,
                tags=["casual", "denim"],
                style=["casual", "minimalist"],
                dominantColors=[{"name": "black", "hex": "#000000", "rgb": [0, 0, 0]}],
                matchingColors=[{"name": "gray", "hex": "#808080", "rgb": [128, 128, 128]}],
                metadata={"material": "denim", "fit": "regular"}
            )
        ]
    
    @pytest.fixture
    def sample_user_profile(self):
        """Create sample user profile for testing."""
        return MockUserProfile(
            id="user1",
            name="Test User",
            email="test@example.com",
            bodyType="athletic",
            skinTone="medium",
            fitPreference="regular",
            stylePreferences=["casual", "minimalist"]
        )
    
    def test_validate_material_compatibility_success(self, sample_items):
        """Test successful material compatibility validation."""
        from src.utils.outfit_validation import validate_material_compatibility
        
        result = validate_material_compatibility(sample_items)
        
        assert isinstance(result, ValidationResult)
        assert hasattr(result, "is_valid")
        assert hasattr(result, "warnings")
        assert result.is_valid is True
    
    def test_validate_weather_appropriateness_success(self, sample_items):
        """Test successful weather appropriateness validation."""
        from src.utils.outfit_validation import validate_weather_appropriateness
        
        result = validate_weather_appropriateness(sample_items, Season.SPRING)
        
        assert isinstance(result, ValidationResult)
        assert hasattr(result, "is_valid")
        assert hasattr(result, "warnings")
        assert result.is_valid is True
    
    def test_validate_skin_tone_compatibility_success(self, sample_items, sample_user_profile):
        """Test successful skin tone compatibility validation."""
        from src.utils.outfit_validation import validate_skin_tone_compatibility
        
        result = validate_skin_tone_compatibility(sample_items, sample_user_profile)
        
        assert isinstance(result, ValidationResult)
        assert hasattr(result, "is_valid")
        assert hasattr(result, "warnings")
        assert result.is_valid is True
    
    def test_validate_body_type_fit_success(self, sample_items, sample_user_profile):
        """Test successful body type fit validation."""
        from src.utils.outfit_validation import validate_body_type_fit
        
        result = validate_body_type_fit(sample_items, sample_user_profile)
        
        assert isinstance(result, ValidationResult)
        assert hasattr(result, "is_valid")
        assert hasattr(result, "warnings")
        assert result.is_valid is True
    
    def test_validate_gender_appropriateness_success(self, sample_items, sample_user_profile):
        """Test successful gender appropriateness validation."""
        from src.utils.outfit_validation import validate_gender_appropriateness
        
        result = validate_gender_appropriateness(sample_items, sample_user_profile)
        
        assert isinstance(result, ValidationResult)
        assert hasattr(result, "is_valid")
        assert hasattr(result, "warnings")
        assert result.is_valid is True
    
    def test_validate_outfit_compatibility_success(self, sample_items, sample_user_profile):
        """Test successful outfit compatibility validation."""
        from src.utils.outfit_validation import validate_outfit_compatibility
        
        result = validate_outfit_compatibility(sample_items, sample_user_profile, Season.SPRING)
        
        assert isinstance(result, ValidationResult)
        assert hasattr(result, "is_valid")
        assert hasattr(result, "warnings")
        assert result.is_valid is True


class TestEdgeCases:
    """Test suite for edge cases and invalid inputs."""
    
    def test_validation_with_empty_items_list(self):
        """Test validation with empty items list."""
        from src.services.validation_orchestrator import ValidationOrchestrator
        
        orchestrator = ValidationOrchestrator(Mock())
        context = {
            "occasion": "casual",
            "weather": MockWeatherData(temperature=70.0, condition="sunny"),
            "style": "minimalist",
            "target_counts": {
                "min_items": 3,
                "max_items": 6,
                "required_categories": ["top", "bottom", "shoes"]
            }
        }
        
        # Test that validation handles empty list gracefully
        result = asyncio.run(orchestrator._validate_form_completeness([], context))
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("minimum" in error.lower() for error in result.errors)
    
    def test_validation_with_none_context(self):
        """Test validation with None context."""
        from src.services.validation_orchestrator import ValidationOrchestrator
        
        orchestrator = ValidationOrchestrator(Mock())
        
        # Test that validation handles None context gracefully
        result = asyncio.run(orchestrator._validate_occasion_appropriateness([], None))
        
        assert isinstance(result, ValidationResult)
        assert result.step == ValidationStep.OCCASION_APPROPRIATENESS
        assert result.duration > 0
    
    def test_validation_with_invalid_item_types(self):
        """Test validation with invalid item types."""
        from src.services.validation_orchestrator import ValidationOrchestrator
        
        orchestrator = ValidationOrchestrator(Mock())
        
        # Create items with invalid types
        invalid_items = [
            MockClothingItem(
                id="1",
                name="Invalid Item",
                type="invalid_type",  # Invalid type
                tags=["casual"],
                style=["casual"],
                dominantColors=[],
                matchingColors=[],
                metadata={}
            )
        ]
        
        context = {
            "occasion": "casual",
            "weather": MockWeatherData(temperature=70.0, condition="sunny"),
            "style": "minimalist"
        }
        
        # Test that validation handles invalid types gracefully
        result = asyncio.run(orchestrator._validate_occasion_appropriateness(invalid_items, context))
        
        assert isinstance(result, ValidationResult)
        assert result.step == ValidationStep.OCCASION_APPROPRIATENESS
        assert result.duration > 0
    
    def test_validation_with_extreme_temperatures(self):
        """Test validation with extreme temperature values."""
        from src.services.validation_orchestrator import ValidationOrchestrator
        
        orchestrator = ValidationOrchestrator(Mock())
        
        sample_items = [
            MockClothingItem(
                id="1",
                name="Test Item",
                type=ClothingType.SHIRT,
                tags=["casual"],
                style=["casual"],
                dominantColors=[],
                matchingColors=[],
                metadata={}
            )
        ]
        
        # Test extreme cold
        context_cold = {
            "weather": MockWeatherData(temperature=-50.0, condition="extreme_cold"),
            "occasion": "casual"
        }
        
        result_cold = asyncio.run(orchestrator._validate_layer_count_appropriateness(sample_items, context_cold))
        
        assert isinstance(result_cold, ValidationResult)
        assert result_cold.step == ValidationStep.LAYER_COUNT_APPROPRIATENESS
        
        # Test extreme heat
        context_hot = {
            "weather": MockWeatherData(temperature=120.0, condition="extreme_heat"),
            "occasion": "casual"
        }
        
        result_hot = asyncio.run(orchestrator._validate_layer_count_appropriateness(sample_items, context_hot))
        
        assert isinstance(result_hot, ValidationResult)
        assert result_hot.step == ValidationStep.LAYER_COUNT_APPROPRIATENESS


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"]) 