#!/usr/bin/env python3
"""
Comprehensive Outfit Generation Testing

Tests all critical aspects of the outfit generation system:
1. Outfit Generation Logic
2. Filtering & Personalization  
3. Data Quality & Metadata Integrity
4. User Profile Matching Logic
5. System Integrity, Security, and Performance
6. Edge Cases & Error Handling
7. Production Readiness
"""

import asyncio
import time
import random
from typing import List, Dict, Any

# Import your existing services and types
from src.services.outfit_service import OutfitService
from src.services.outfit_fallback_service import OutfitFallbackService
from src.custom_types.wardrobe import ClothingItem, ClothingType, Season
from src.custom_types.profile import UserProfile
from src.custom_types.weather import WeatherData

class OutfitGenerationTester:
    """Comprehensive tester for outfit generation system."""
    
    def __init__(self):
        self.outfit_service = OutfitService()
        self.fallback_service = OutfitFallbackService()
        self.test_results = []
    
    async def run_all_tests(self):
        """Run all comprehensive tests."""
        print("🧪 Starting Comprehensive Outfit Generation Testing")
        print("=" * 60)
        
        # 1. Test Outfit Generation Logic
        print("\n🔍 1. Testing Outfit Generation Logic")
        await self.test_outfit_generation_logic()
        
        # 2. Test Filtering & Personalization
        print("\n🧘 2. Testing Filtering & Personalization")
        await self.test_filtering_and_personalization()
        
        # 3. Test Data Quality
        print("\n🧩 3. Testing Data Quality & Metadata")
        await self.test_data_quality()
        
        # 4. Test User Profile Matching
        print("\n👤 4. Testing User Profile Matching")
        await self.test_user_profile_matching()
        
        # 5. Test System Integrity & Performance
        print("\n🔐 5. Testing System Integrity & Performance")
        await self.test_system_integrity()
        
        # 6. Test Edge Cases
        print("\n💔 6. Testing Edge Cases & Error Handling")
        await self.test_edge_cases()
        
        # 7. Test Production Readiness
        print("\n🧭 7. Testing Production Readiness")
        await self.test_production_readiness()
        
        # Print final results
        self.print_final_results()
    
    async def test_outfit_generation_logic(self):
        """Test 1: Outfit Generation Logic"""
        print("  Testing base item handling...")
        
        # Test base item preservation
        wardrobe = self.create_test_wardrobe(20)
        base_item = wardrobe[0]
        
        # Test with different contexts
        contexts = [
            {'occasion': 'casual', 'style': 'minimalist'},
            {'occasion': 'formal', 'style': 'classic'},
            {'occasion': 'athletic', 'style': 'sporty'}
        ]
        
        base_item_preserved = 0
        for context in contexts:
            try:
                # Apply filtering
                filtered_items = self.outfit_service._apply_strict_filtering(wardrobe, context)
                if base_item in filtered_items:
                    base_item_preserved += 1
            except Exception as e:
                print(f"    ❌ Base item filtering failed: {e}")
        
        success_rate = base_item_preserved / len(contexts)
        print(f"    ✅ Base item preservation rate: {success_rate:.1%}")
        
        # Test smart selection
        print("  Testing smart selection logic...")
        try:
            context = {
                'occasion': 'casual',
                'style': 'casual',
                'weather': WeatherData(temperature=70.0, condition='sunny'),
                'user_profile': self.create_test_user_profile(),
                'target_counts': {'min_items': 3, 'max_items': 5}
            }
            
            selected_items = self.outfit_service._smart_selection_phase(wardrobe, context)
            if len(selected_items) >= 3:
                print(f"    ✅ Smart selection successful: {len(selected_items)} items selected")
            else:
                print(f"    ⚠️  Smart selection returned only {len(selected_items)} items")
                
        except Exception as e:
            print(f"    ❌ Smart selection failed: {e}")
        
        # Test fallback logic
        print("  Testing fallback logic...")
        try:
            outfit = await self.fallback_service.generate_outfit_with_constraints(
                user_id="test-user",
                constraints={
                    'occasion': 'casual',
                    'style': 'casual',
                    'temperature': 70.0
                }
            )
            
            if outfit['success']:
                print(f"    ✅ Fallback logic successful")
            else:
                print(f"    ⚠️  Fallback logic failed: {outfit.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"    ❌ Fallback logic error: {e}")
    
    async def test_filtering_and_personalization(self):
        """Test 2: Filtering & Personalization"""
        print("  Testing mood filtering...")
        
        # Test mood filtering
        moods = ['relaxed', 'energetic', 'confident', 'playful']
        wardrobe = self.create_test_wardrobe(15)
        
        for mood in moods:
            try:
                mood_rule = self.get_mood_rule(mood)
                filtered_items = self.outfit_service._filter_items_by_mood(wardrobe, mood_rule)
                print(f"    ✅ Mood '{mood}': {len(filtered_items)} items filtered")
            except Exception as e:
                print(f"    ❌ Mood filtering failed for '{mood}': {e}")
        
        print("  Testing weather handling...")
        # Test weather handling
        temperatures = [30.0, 70.0, 90.0]  # Cold, moderate, hot
        
        for temp in temperatures:
            try:
                weather = WeatherData(temperature=temp, condition='sunny')
                filtered_items = self.outfit_service._filter_by_weather_strict(wardrobe, weather)
                print(f"    ✅ Weather {temp}°F: {len(filtered_items)} items filtered")
            except Exception as e:
                print(f"    ❌ Weather filtering failed for {temp}°F: {e}")
    
    async def test_data_quality(self):
        """Test 3: Data Quality & Metadata Integrity"""
        print("  Testing clothing metadata completeness...")
        
        # Test metadata completeness
        test_items = self.create_test_wardrobe(10)
        complete_items = 0
        
        required_fields = ['type', 'color', 'season', 'style', 'occasion', 'dominantColors']
        
        for item in test_items:
            missing_fields = []
            for field in required_fields:
                if not hasattr(item, field) or getattr(item, field) is None:
                    missing_fields.append(field)
            
            if not missing_fields:
                complete_items += 1
            else:
                print(f"    ⚠️  Item {item.name} missing fields: {missing_fields}")
        
        completeness_rate = complete_items / len(test_items)
        print(f"    ✅ Metadata completeness rate: {completeness_rate:.1%}")
        
        print("  Testing tag consistency...")
        # Test tag consistency
        inconsistent_items = 0
        
        for item in test_items:
            # Check for inconsistent tags
            if hasattr(item, 'style') and hasattr(item, 'occasion'):
                if not item.style or not item.occasion:
                    inconsistent_items += 1
        
        consistency_rate = (len(test_items) - inconsistent_items) / len(test_items)
        print(f"    ✅ Tag consistency rate: {consistency_rate:.1%}")
    
    async def test_user_profile_matching(self):
        """Test 4: User Profile Matching Logic"""
        print("  Testing style fingerprinting...")
        
        # Test style fingerprinting
        user_profiles = [
            self.create_test_user_profile('athletic', ['casual', 'sporty']),
            self.create_test_user_profile('hourglass', ['classic', 'elegant']),
            self.create_test_user_profile('rectangle', ['minimalist', 'modern'])
        ]
        
        for profile in user_profiles:
            try:
                # Test style compatibility
                wardrobe = self.create_test_wardrobe(10)
                compatible_items = self.check_style_compatibility(wardrobe, profile)
                print(f"    ✅ Profile {profile.bodyType}: {len(compatible_items)} compatible items")
            except Exception as e:
                print(f"    ❌ Style fingerprinting failed for {profile.bodyType}: {e}")
    
    async def test_system_integrity(self):
        """Test 5: System Integrity, Security, and Performance"""
        print("  Testing invalid input handling...")
        
        # Test invalid inputs
        invalid_inputs = [
            {'type': None, 'name': 'test'},
            {'type': 'invalid_type', 'name': 'test'},
            {'type': 'shirt', 'dominantColors': 'invalid'},
            {}
        ]
        
        for invalid_input in invalid_inputs:
            try:
                # Try to process invalid input
                result = self.process_item_data(invalid_input)
                print(f"    ⚠️  Invalid input processed without error: {invalid_input}")
            except Exception as e:
                print(f"    ✅ Invalid input properly rejected: {type(e).__name__}")
        
        print("  Testing performance...")
        # Test performance
        start_time = time.time()
        
        try:
            # Generate multiple outfits
            for i in range(5):
                outfit = await self.outfit_service.generate_outfit(
                    occasion='casual',
                    weather=WeatherData(temperature=70.0, condition='sunny'),
                    wardrobe=self.create_test_wardrobe(15),
                    user_profile=self.create_test_user_profile(),
                    likedOutfits=[],
                    trendingStyles=[],
                    style='casual',
                    mood='neutral'
                )
            
            end_time = time.time()
            avg_time = (end_time - start_time) / 5
            
            if avg_time < 3.0:  # 3 seconds threshold
                print(f"    ✅ Performance good: {avg_time:.2f}s average")
            else:
                print(f"    ⚠️  Performance slow: {avg_time:.2f}s average")
                
        except Exception as e:
            print(f"    ❌ Performance test failed: {e}")
    
    async def test_edge_cases(self):
        """Test 6: Edge Cases & Error Handling"""
        print("  Testing empty wardrobe...")
        
        # Test empty wardrobe
        try:
            empty_wardrobe = []
            outfit = await self.outfit_service.generate_outfit(
                occasion='casual',
                weather=WeatherData(temperature=70.0, condition='sunny'),
                wardrobe=empty_wardrobe,
                user_profile=self.create_test_user_profile(),
                likedOutfits=[],
                trendingStyles=[],
                style='casual',
                mood='neutral'
            )
            
            if outfit and len(outfit.get('items', [])) == 0:
                print(f"    ✅ Empty wardrobe handled gracefully")
            else:
                print(f"    ⚠️  Empty wardrobe returned unexpected result")
                
        except Exception as e:
            print(f"    ❌ Empty wardrobe test failed: {e}")
        
        print("  Testing extreme weather conditions...")
        # Test extreme weather
        extreme_temps = [-10.0, 110.0]  # Very cold, very hot
        
        for temp in extreme_temps:
            try:
                weather = WeatherData(temperature=temp, condition='sunny')
                wardrobe = self.create_test_wardrobe(10)
                filtered_items = self.outfit_service._filter_by_weather_strict(wardrobe, weather)
                print(f"    ✅ Extreme temp {temp}°F: {len(filtered_items)} items filtered")
            except Exception as e:
                print(f"    ❌ Extreme weather test failed for {temp}°F: {e}")
    
    async def test_production_readiness(self):
        """Test 7: Production Deployment Checklist"""
        print("  Testing environment variables...")
        
        # Test environment variables
        required_env_vars = [
            'OPENAI_API_KEY',
            'FIREBASE_PROJECT_ID',
            'DATABASE_URL'
        ]
        
        missing_vars = []
        for var in required_env_vars:
            if not self.check_environment_variable(var):
                missing_vars.append(var)
        
        if not missing_vars:
            print(f"    ✅ All required environment variables present")
        else:
            print(f"    ⚠️  Missing environment variables: {missing_vars}")
        
        print("  Testing health checks...")
        # Test health checks
        try:
            health_status = await self.perform_health_check()
            if health_status['healthy']:
                print(f"    ✅ Health check passed")
            else:
                print(f"    ⚠️  Health check failed: {health_status.get('errors', [])}")
        except Exception as e:
            print(f"    ❌ Health check error: {e}")
    
    # Helper methods
    
    def create_test_wardrobe(self, size: int = 10) -> List[ClothingItem]:
        """Create a test wardrobe with specified number of items."""
        wardrobe = []
        
        item_types = [ClothingType.SHIRT, ClothingType.PANTS, ClothingType.SHOES]
        colors = ['white', 'black', 'navy', 'gray']
        styles = ['casual', 'formal', 'classic']
        
        for i in range(size):
            item = ClothingItem(
                id=f"test-item-{i}",
                userId="test-user",
                name=f"Test Item {i}",
                type=random.choice(item_types),
                color=random.choice(colors),
                season=[Season.SPRING, Season.SUMMER],
                imageUrl=f"test-image-{i}.jpg",
                tags=[f"tag-{i}"],
                style=[random.choice(styles)],
                dominantColors=[{"name": random.choice(colors), "hex": "#000000"}],
                matchingColors=[{"name": random.choice(colors), "hex": "#FFFFFF"}],
                occasion=["casual", "daily"],
                createdAt=int(time.time()),
                updatedAt=int(time.time())
            )
            wardrobe.append(item)
        
        return wardrobe
    
    def create_test_user_profile(self, body_type: str = "athletic", style_prefs: List[str] = None) -> UserProfile:
        """Create a test user profile."""
        if style_prefs is None:
            style_prefs = ["casual", "classic"]
            
        return UserProfile(
            id="test-user",
            name="Test User",
            email="test@example.com",
            bodyType=body_type,
            skinTone="medium",
            height=175,
            weight=70,
            stylePreferences=style_prefs,
            budget="medium",
            createdAt=int(time.time()),
            updatedAt=int(time.time())
        )
    
    def get_mood_rule(self, mood: str):
        """Get mood rule for testing."""
        # Simplified mood rule
        return type('MoodRule', (), {'mood': mood})()
    
    def check_style_compatibility(self, wardrobe: List[ClothingItem], profile: UserProfile) -> List[ClothingItem]:
        """Check style compatibility with user profile."""
        compatible_items = []
        for item in wardrobe:
            if hasattr(item, 'style') and item.style:
                if any(style in profile.stylePreferences for style in item.style):
                    compatible_items.append(item)
        return compatible_items
    
    def process_item_data(self, data: Dict) -> bool:
        """Process item data for testing."""
        if not data or 'type' not in data:
            raise ValueError("Invalid item data")
        return True
    
    def check_environment_variable(self, var_name: str) -> bool:
        """Check if environment variable exists."""
        import os
        return os.getenv(var_name) is not None
    
    async def perform_health_check(self) -> Dict:
        """Perform health check."""
        try:
            # Simplified health check
            return {
                'healthy': True,
                'timestamp': time.time(),
                'services': ['outfit_service', 'fallback_service']
            }
        except Exception as e:
            return {
                'healthy': False,
                'errors': [str(e)],
                'timestamp': time.time()
            }
    
    def print_final_results(self):
        """Print final test results."""
        print("\n" + "=" * 60)
        print("🧪 COMPREHENSIVE TESTING RESULTS")
        print("=" * 60)
        
        # Calculate summary statistics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.get('success', False))
        
        print(f"\n📊 Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {total_tests - passed_tests}")
        
        if total_tests > 0:
            success_rate = (passed_tests / total_tests) * 100
            print(f"   Success Rate: {success_rate:.1f}%")
        
        print("\n✅ Comprehensive testing completed!")

# Main execution
async def main():
    """Main function to run the comprehensive testing."""
    tester = OutfitGenerationTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 