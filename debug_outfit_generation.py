#!/usr/bin/env python3
"""
Comprehensive Outfit Generation Debug Test Script

This script systematically tests the outfit generation function to identify
issues with user profile setup and outfit generation pipeline.
"""

import asyncio
import json
import sys
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the backend directory to the path
backend_path = os.path.join(os.path.dirname(__file__), 'backend', 'src')
sys.path.insert(0, backend_path)

try:
    from services.outfit_service import OutfitService
    from types.wardrobe import ClothingItem, ClothingType, Season, StyleTag, Color
    from types.weather import WeatherData
    from types.profile import UserProfile
    from types.outfit import OutfitGeneratedOutfit
except ImportError as e:
    print(f"❌ Import error: {e}")
    print(f"Backend path: {backend_path}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

class OutfitGenerationDebugger:
    def __init__(self):
        self.outfit_service = OutfitService()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = "", data: Any = None):
        """Log test results"""
        result = {
            "test_name": test_name,
            "success": success,
            "details": details,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if data and not success:
            print(f"   Data: {json.dumps(data, indent=2, default=str)}")
        print()

    def create_test_wardrobe(self) -> List[ClothingItem]:
        """Create a test wardrobe with basic items"""
        return [
            ClothingItem(
                id="test-shirt-1",
                name="Blue T-Shirt",
                type=ClothingType.SHIRT,
                color="blue",
                season=[Season.SPRING, Season.SUMMER],
                style=[StyleTag.CASUAL],
                imageUrl="",
                tags=[],
                dominantColors=["#0000FF"],
                matchingColors=[],
                occasion=["casual"],
                createdAt=int(datetime.now().timestamp()),
                updatedAt=int(datetime.now().timestamp()),
                userId="test-user"
            ),
            ClothingItem(
                id="test-pants-1",
                name="Black Jeans",
                type=ClothingType.PANTS,
                color="black",
                season=[Season.SPRING, Season.SUMMER, Season.FALL, Season.WINTER],
                style=[StyleTag.CASUAL],
                imageUrl="",
                tags=[],
                dominantColors=["#000000"],
                matchingColors=[],
                occasion=["casual"],
                createdAt=int(datetime.now().timestamp()),
                updatedAt=int(datetime.now().timestamp()),
                userId="test-user"
            ),
            ClothingItem(
                id="test-shoes-1",
                name="White Sneakers",
                type=ClothingType.SHOES,
                color="white",
                season=[Season.SPRING, Season.SUMMER, Season.FALL],
                style=[StyleTag.CASUAL],
                imageUrl="",
                tags=[],
                dominantColors=["#FFFFFF"],
                matchingColors=[],
                occasion=["casual"],
                createdAt=int(datetime.now().timestamp()),
                updatedAt=int(datetime.now().timestamp()),
                userId="test-user"
            )
        ]

    def create_test_user_profile(self, profile_type: str = "complete") -> UserProfile:
        """Create test user profiles with different completeness levels"""
        
        base_profile = {
            "id": "test-user-123",
            "name": "Test User",
            "email": "test@example.com",
            "createdAt": int(datetime.now().timestamp()),
            "updatedAt": int(datetime.now().timestamp())
        }
        
        if profile_type == "complete":
            return UserProfile(
                **base_profile,
                gender="male",
                preferences={
                    "style": ["casual", "minimalist"],
                    "colors": ["blue", "black", "white"],
                    "occasions": ["casual", "work"],
                    "formality": "casual",
                    "budget": "medium",
                    "preferredBrands": ["Nike", "Adidas"],
                    "fitPreferences": ["fitted", "relaxed"]
                },
                measurements={
                    "height": 175,
                    "weight": 70,
                    "bodyType": "athletic",
                    "skinTone": "medium",
                    "heightFeetInches": "5'9\"",
                    "topSize": "M",
                    "bottomSize": "32",
                    "shoeSize": "10",
                    "dressSize": "",
                    "jeanWaist": "32",
                    "braSize": "",
                    "inseam": "32",
                    "waist": "32",
                    "chest": "40"
                },
                stylePreferences=["casual", "minimalist", "athletic"],
                bodyType="athletic",
                skinTone="medium",
                fitPreference="fitted",
                budget="medium",
                preferredBrands=["Nike", "Adidas"],
                fitPreferences=["fitted", "relaxed"],
                quizResponses=[],
                colorPalette={
                    "primary": ["blue", "black"],
                    "secondary": ["white", "gray"],
                    "accent": ["red"],
                    "neutral": ["beige", "brown"],
                    "avoid": ["pink", "purple"]
                },
                hybridStyleName="Athletic Minimalist",
                alignmentScore=0.85,
                selfieUrl="",
                onboardingCompleted=True
            )
        
        elif profile_type == "minimal":
            return UserProfile(
                **base_profile,
                gender="male",
                preferences={
                    "style": ["casual"],
                    "colors": ["blue", "black"],
                    "occasions": ["casual"]
                },
                measurements={
                    "height": 175,
                    "weight": 70,
                    "bodyType": "athletic",
                    "skinTone": "medium"
                },
                stylePreferences=["casual"],
                bodyType="athletic",
                skinTone="medium",
                onboardingCompleted=False
            )
        
        elif profile_type == "incomplete":
            return UserProfile(
                **base_profile,
                gender=None,
                preferences={
                    "style": [],
                    "colors": [],
                    "occasions": []
                },
                measurements={
                    "height": 0,
                    "weight": 0,
                    "bodyType": None,
                    "skinTone": None
                },
                stylePreferences=[],
                bodyType=None,
                skinTone=None,
                onboardingCompleted=False
            )
        
        else:
            raise ValueError(f"Unknown profile type: {profile_type}")

    def create_test_weather(self) -> WeatherData:
        """Create test weather data"""
        return WeatherData(
            temperature=75.0,
            condition="sunny",
            location="test-location",
            humidity=50.0,
            wind_speed=5.0,
            precipitation=0.0
        )

    async def test_1_user_profile_validation(self):
        """Test 1: Validate user profile structure and completeness"""
        print("🧪 Test 1: User Profile Validation")
        print("=" * 50)
        
        # Test complete profile
        try:
            complete_profile = self.create_test_user_profile("complete")
            self.log_test(
                "Complete Profile Creation",
                True,
                f"Profile created with {len(complete_profile.stylePreferences)} style preferences"
            )
        except Exception as e:
            self.log_test(
                "Complete Profile Creation",
                False,
                f"Failed to create complete profile: {str(e)}"
            )
        
        # Test minimal profile
        try:
            minimal_profile = self.create_test_user_profile("minimal")
            self.log_test(
                "Minimal Profile Creation",
                True,
                f"Minimal profile created with basic info"
            )
        except Exception as e:
            self.log_test(
                "Minimal Profile Creation",
                False,
                f"Failed to create minimal profile: {str(e)}"
            )
        
        # Test incomplete profile
        try:
            incomplete_profile = self.create_test_user_profile("incomplete")
            self.log_test(
                "Incomplete Profile Creation",
                True,
                f"Incomplete profile created (expected for testing)"
            )
        except Exception as e:
            self.log_test(
                "Incomplete Profile Creation",
                False,
                f"Failed to create incomplete profile: {str(e)}"
            )

    async def test_2_wardrobe_validation(self):
        """Test 2: Validate wardrobe structure and item compatibility"""
        print("🧪 Test 2: Wardrobe Validation")
        print("=" * 50)
        
        try:
            wardrobe = self.create_test_wardrobe()
            self.log_test(
                "Wardrobe Creation",
                True,
                f"Created wardrobe with {len(wardrobe)} items"
            )
            
            # Check item types
            item_types = [item.type for item in wardrobe]
            self.log_test(
                "Item Type Diversity",
                len(set(item_types)) >= 3,
                f"Found item types: {item_types}"
            )
            
            # Check color diversity
            colors = [item.color for item in wardrobe]
            self.log_test(
                "Color Diversity",
                len(set(colors)) >= 2,
                f"Found colors: {colors}"
            )
            
        except Exception as e:
            self.log_test(
                "Wardrobe Creation",
                False,
                f"Failed to create wardrobe: {str(e)}"
            )

    async def test_3_weather_data_validation(self):
        """Test 3: Validate weather data structure"""
        print("🧪 Test 3: Weather Data Validation")
        print("=" * 50)
        
        try:
            weather = self.create_test_weather()
            self.log_test(
                "Weather Data Creation",
                True,
                f"Weather: {weather.temperature}°F, {weather.condition}"
            )
            
            # Validate temperature range
            temp_valid = 0 <= weather.temperature <= 120
            self.log_test(
                "Temperature Range",
                temp_valid,
                f"Temperature {weather.temperature}°F is {'valid' if temp_valid else 'invalid'}"
            )
            
        except Exception as e:
            self.log_test(
                "Weather Data Creation",
                False,
                f"Failed to create weather data: {str(e)}"
            )

    async def test_4_outfit_generation_with_complete_profile(self):
        """Test 4: Generate outfit with complete user profile"""
        print("🧪 Test 4: Outfit Generation with Complete Profile")
        print("=" * 50)
        
        try:
            profile = self.create_test_user_profile("complete")
            wardrobe = self.create_test_wardrobe()
            weather = self.create_test_weather()
            
            outfit = await self.outfit_service.generate_outfit(
                occasion="casual",
                weather=weather,
                wardrobe=wardrobe,
                user_profile=profile,
                likedOutfits=[],
                trendingStyles=[],
                style="casual",
                mood="relaxed"
            )
            
            self.log_test(
                "Complete Profile Outfit Generation",
                True,
                f"Generated outfit with {len(outfit.items)} items"
            )
            
            # Validate outfit structure
            has_items = len(outfit.items) > 0
            self.log_test(
                "Outfit Has Items",
                has_items,
                f"Outfit contains {len(outfit.items)} items"
            )
            
            # Check outfit metadata
            has_metadata = hasattr(outfit, 'metadata') and outfit.metadata
            self.log_test(
                "Outfit Has Metadata",
                has_metadata,
                "Outfit includes generation metadata"
            )
            
        except Exception as e:
            self.log_test(
                "Complete Profile Outfit Generation",
                False,
                f"Failed to generate outfit: {str(e)}",
                {"error": str(e), "traceback": str(sys.exc_info())}
            )

    async def test_5_outfit_generation_with_minimal_profile(self):
        """Test 5: Generate outfit with minimal user profile"""
        print("🧪 Test 5: Outfit Generation with Minimal Profile")
        print("=" * 50)
        
        try:
            profile = self.create_test_user_profile("minimal")
            wardrobe = self.create_test_wardrobe()
            weather = self.create_test_weather()
            
            outfit = await self.outfit_service.generate_outfit(
                occasion="casual",
                weather=weather,
                wardrobe=wardrobe,
                user_profile=profile,
                likedOutfits=[],
                trendingStyles=[],
                style="casual"
            )
            
            self.log_test(
                "Minimal Profile Outfit Generation",
                True,
                f"Generated outfit with {len(outfit.items)} items"
            )
            
        except Exception as e:
            self.log_test(
                "Minimal Profile Outfit Generation",
                False,
                f"Failed to generate outfit: {str(e)}",
                {"error": str(e), "traceback": str(sys.exc_info())}
            )

    async def test_6_outfit_generation_with_incomplete_profile(self):
        """Test 6: Generate outfit with incomplete user profile"""
        print("🧪 Test 6: Outfit Generation with Incomplete Profile")
        print("=" * 50)
        
        try:
            profile = self.create_test_user_profile("incomplete")
            wardrobe = self.create_test_wardrobe()
            weather = self.create_test_weather()
            
            outfit = await self.outfit_service.generate_outfit(
                occasion="casual",
                weather=weather,
                wardrobe=wardrobe,
                user_profile=profile,
                likedOutfits=[],
                trendingStyles=[]
            )
            
            self.log_test(
                "Incomplete Profile Outfit Generation",
                True,
                f"Generated outfit with {len(outfit.items)} items (should use fallbacks)"
            )
            
        except Exception as e:
            self.log_test(
                "Incomplete Profile Outfit Generation",
                False,
                f"Failed to generate outfit: {str(e)}",
                {"error": str(e), "traceback": str(sys.exc_info())}
            )

    async def test_7_profile_field_analysis(self):
        """Test 7: Analyze which profile fields are causing issues"""
        print("🧪 Test 7: Profile Field Analysis")
        print("=" * 50)
        
        # Test different profile configurations
        test_configs = [
            ("missing_gender", {"gender": None}),
            ("missing_preferences", {"preferences": {"style": [], "colors": [], "occasions": []}}),
            ("missing_measurements", {"measurements": {"height": 0, "weight": 0, "bodyType": None, "skinTone": None}}),
            ("missing_style_preferences", {"stylePreferences": []}),
            ("missing_body_type", {"bodyType": None}),
            ("missing_skin_tone", {"skinTone": None})
        ]
        
        for config_name, override_fields in test_configs:
            try:
                # Create base profile
                base_profile = self.create_test_user_profile("complete")
                
                # Override specific fields
                profile_dict = base_profile.dict()
                profile_dict.update(override_fields)
                
                # Create modified profile
                modified_profile = UserProfile(**profile_dict)
                wardrobe = self.create_test_wardrobe()
                weather = self.create_test_weather()
                
                outfit = await self.outfit_service.generate_outfit(
                    occasion="casual",
                    weather=weather,
                    wardrobe=wardrobe,
                    user_profile=modified_profile,
                    likedOutfits=[],
                    trendingStyles=[]
                )
                
                self.log_test(
                    f"Profile with {config_name}",
                    True,
                    f"Generated outfit successfully despite missing {config_name}"
                )
                
            except Exception as e:
                self.log_test(
                    f"Profile with {config_name}",
                    False,
                    f"Failed with missing {config_name}: {str(e)}"
                )

    async def test_8_outfit_generation_edge_cases(self):
        """Test 8: Test edge cases in outfit generation"""
        print("🧪 Test 8: Outfit Generation Edge Cases")
        print("=" * 50)
        
        # Test with empty wardrobe
        try:
            profile = self.create_test_user_profile("complete")
            weather = self.create_test_weather()
            
            outfit = await self.outfit_service.generate_outfit(
                occasion="casual",
                weather=weather,
                wardrobe=[],
                user_profile=profile,
                likedOutfits=[],
                trendingStyles=[]
            )
            
            self.log_test(
                "Empty Wardrobe",
                True,
                "Generated outfit with empty wardrobe (should use fallback)"
            )
            
        except Exception as e:
            self.log_test(
                "Empty Wardrobe",
                False,
                f"Failed with empty wardrobe: {str(e)}"
            )
        
        # Test with extreme weather
        try:
            profile = self.create_test_user_profile("complete")
            wardrobe = self.create_test_wardrobe()
            extreme_weather = WeatherData(
                temperature=100.0,
                condition="hot",
                location="test-location",
                humidity=80.0,
                wind_speed=0.0,
                precipitation=0.0
            )
            
            outfit = await self.outfit_service.generate_outfit(
                occasion="casual",
                weather=extreme_weather,
                wardrobe=wardrobe,
                user_profile=profile,
                likedOutfits=[],
                trendingStyles=[]
            )
            
            self.log_test(
                "Extreme Weather",
                True,
                f"Generated outfit for {extreme_weather.temperature}°F weather"
            )
            
        except Exception as e:
            self.log_test(
                "Extreme Weather",
                False,
                f"Failed with extreme weather: {str(e)}"
            )

    async def test_9_user_profile_data_consistency(self):
        """Test 9: Check for data consistency issues in user profiles"""
        print("🧪 Test 9: User Profile Data Consistency")
        print("=" * 50)
        
        # Test profile with conflicting data
        try:
            profile = self.create_test_user_profile("complete")
            profile_dict = profile.dict()
            
            # Add conflicting data
            profile_dict["measurements"]["height"] = 0  # Invalid height
            profile_dict["preferences"]["style"] = []   # Empty style preferences
            
            conflicting_profile = UserProfile(**profile_dict)
            wardrobe = self.create_test_wardrobe()
            weather = self.create_test_weather()
            
            outfit = await self.outfit_service.generate_outfit(
                occasion="casual",
                weather=weather,
                wardrobe=wardrobe,
                user_profile=conflicting_profile,
                likedOutfits=[],
                trendingStyles=[]
            )
            
            self.log_test(
                "Conflicting Profile Data",
                True,
                "Generated outfit despite conflicting profile data"
            )
            
        except Exception as e:
            self.log_test(
                "Conflicting Profile Data",
                False,
                f"Failed with conflicting data: {str(e)}"
            )

    async def test_10_outfit_generation_performance(self):
        """Test 10: Performance and timing analysis"""
        print("🧪 Test 10: Performance Analysis")
        print("=" * 50)
        
        import time
        
        profile = self.create_test_user_profile("complete")
        wardrobe = self.create_test_wardrobe()
        weather = self.create_test_weather()
        
        start_time = time.time()
        
        try:
            outfit = await self.outfit_service.generate_outfit(
                occasion="casual",
                weather=weather,
                wardrobe=wardrobe,
                user_profile=profile,
                likedOutfits=[],
                trendingStyles=[]
            )
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            self.log_test(
                "Generation Performance",
                generation_time < 30.0,  # Should complete within 30 seconds
                f"Generated outfit in {generation_time:.2f} seconds"
            )
            
        except Exception as e:
            end_time = time.time()
            generation_time = end_time - start_time
            
            self.log_test(
                "Generation Performance",
                False,
                f"Failed after {generation_time:.2f} seconds: {str(e)}"
            )

    def generate_report(self):
        """Generate a comprehensive test report"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test_name']}: {result['details']}")
        
        print("\n🔍 RECOMMENDATIONS:")
        if failed_tests == 0:
            print("  ✅ All tests passed! The outfit generation system appears to be working correctly.")
        else:
            print("  ⚠️  Some tests failed. Check the failed test details above for specific issues.")
            print("  🔧 Focus on fixing the user profile setup issues identified in the failed tests.")
        
        # Save detailed report to file
        report_file = "outfit_generation_debug_report.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: {report_file}")

    async def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Comprehensive Outfit Generation Debug Tests")
        print("=" * 80)
        
        tests = [
            self.test_1_user_profile_validation,
            self.test_2_wardrobe_validation,
            self.test_3_weather_data_validation,
            self.test_4_outfit_generation_with_complete_profile,
            self.test_5_outfit_generation_with_minimal_profile,
            self.test_6_outfit_generation_with_incomplete_profile,
            self.test_7_profile_field_analysis,
            self.test_8_outfit_generation_edge_cases,
            self.test_9_user_profile_data_consistency,
            self.test_10_outfit_generation_performance
        ]
        
        for test in tests:
            try:
                await test()
            except Exception as e:
                print(f"❌ Test {test.__name__} crashed: {str(e)}")
                import traceback
                traceback.print_exc()
        
        self.generate_report()

async def main():
    """Main function to run the debug tests"""
    debugger = OutfitGenerationDebugger()
    await debugger.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 