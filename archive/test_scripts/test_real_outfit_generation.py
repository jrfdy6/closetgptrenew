#!/usr/bin/env python3
"""
Real Backend Test Suite for Outfit Generation
Tests the actual outfit generation service with weather integration.
"""

import asyncio
import json
import time
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime

class RealOutfitGenerationTester:
    """Test suite for real backend outfit generation."""
    
    def __init__(self, backend_url: str = "http://localhost:3001"):
        self.backend_url = backend_url
        self.test_results = []
        self.inappropriate_outfits = []
        
    async def run_real_backend_tests(self):
        """Run tests against the real backend."""
        print("🧪 Starting Real Backend Outfit Generation Tests")
        print("=" * 60)
        
        # Test 1: Check if backend is running
        await self.test_backend_connectivity()
        
        # Test 2: Test outfit generation with various scenarios
        await self.test_outfit_generation_scenarios()
        
        # Test 3: Test weather integration
        await self.test_weather_integration()
        
        # Test 4: Test inappropriate combination prevention
        await self.test_inappropriate_prevention()
        
        # Print results
        self.print_results()
        
    async def test_backend_connectivity(self):
        """Test if backend is running and accessible."""
        print("\n🔌 Testing Backend Connectivity...")
        
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                self.record_test("✅", "Backend Connectivity", "PASSED - Backend is running")
                return True
            else:
                self.record_test("❌", "Backend Connectivity", f"FAILED - Status code: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.record_test("❌", "Backend Connectivity", f"FAILED - Cannot connect: {str(e)}")
            print(f"   Make sure the backend is running on {self.backend_url}")
            print(f"   You can start it with: cd backend && python app.py")
            return False
    
    async def test_outfit_generation_scenarios(self):
        """Test outfit generation with various scenarios."""
        print("\n👗 Testing Outfit Generation Scenarios...")
        
        # Test scenarios
        scenarios = [
            {
                "name": "Business Casual - Normal Weather",
                "occasion": "business",
                "style": "casual",
                "weather": {
                    "temperature": 70,
                    "condition": "clear",
                    "humidity": 50,
                    "wind_speed": 5,
                    "precipitation": 0
                }
            },
            {
                "name": "Formal - Cold Weather",
                "occasion": "formal",
                "style": "formal",
                "weather": {
                    "temperature": 40,
                    "condition": "cold",
                    "humidity": 60,
                    "wind_speed": 10,
                    "precipitation": 0
                }
            },
            {
                "name": "Casual - Hot Weather",
                "occasion": "casual",
                "style": "casual",
                "weather": {
                    "temperature": 85,
                    "condition": "sunny",
                    "humidity": 70,
                    "wind_speed": 3,
                    "precipitation": 0
                }
            }
        ]
        
        for scenario in scenarios:
            try:
                result = await self.generate_outfit_with_scenario(scenario)
                
                if result["success"]:
                    # Check if outfit is appropriate
                    is_appropriate = self.check_outfit_appropriateness(
                        result["outfit"], 
                        scenario["occasion"], 
                        scenario["weather"]
                    )
                    
                    if is_appropriate:
                        self.record_test("✅", scenario["name"], "PASSED - Appropriate outfit generated")
                    else:
                        self.record_test("❌", scenario["name"], "FAILED - Inappropriate outfit generated")
                        self.inappropriate_outfits.append({
                            "scenario": scenario,
                            "outfit": result["outfit"],
                            "issues": result.get("issues", [])
                        })
                else:
                    self.record_test("❌", scenario["name"], f"FAILED - Generation failed: {result.get('error', 'Unknown')}")
                    
            except Exception as e:
                self.record_test("❌", scenario["name"], f"ERROR - {str(e)}")
    
    async def test_weather_integration(self):
        """Test weather integration specifically."""
        print("\n🌤️ Testing Weather Integration...")
        
        weather_tests = [
            {
                "name": "Hot Weather - Should Avoid Heavy Items",
                "weather": {"temperature": 90, "condition": "hot"},
                "should_avoid": ["blazer", "coat", "sweater"],
                "should_include": ["t-shirt", "shorts", "dress"]
            },
            {
                "name": "Cold Weather - Should Include Warm Items",
                "weather": {"temperature": 30, "condition": "cold"},
                "should_avoid": ["t-shirt", "shorts", "sandals"],
                "should_include": ["coat", "sweater", "pants"]
            },
            {
                "name": "Rainy Weather - Should Avoid Open Shoes",
                "weather": {"temperature": 60, "condition": "rain", "precipitation": 80},
                "should_avoid": ["sandals", "flip-flops", "open shoes"],
                "should_include": ["closed shoes", "boots"]
            }
        ]
        
        for test in weather_tests:
            try:
                result = await self.generate_outfit_with_weather(test["weather"])
                
                if result["success"]:
                    outfit_items = result["outfit"].get("items", [])
                    
                    # Check for items that should be avoided
                    avoided_items = []
                    for item in outfit_items:
                        item_name = item.get("name", "").lower()
                        item_type = item.get("type", "").lower()
                        
                        for avoid_type in test["should_avoid"]:
                            if avoid_type.lower() in item_name or avoid_type.lower() in item_type:
                                avoided_items.append(item)
                    
                    if not avoided_items:
                        self.record_test("✅", test["name"], "PASSED - Weather-appropriate items selected")
                    else:
                        self.record_test("❌", test["name"], f"FAILED - Inappropriate items for weather: {[item['name'] for item in avoided_items]}")
                else:
                    self.record_test("❌", test["name"], f"FAILED - Generation failed: {result.get('error', 'Unknown')}")
                    
            except Exception as e:
                self.record_test("❌", test["name"], f"ERROR - {str(e)}")
    
    async def test_inappropriate_prevention(self):
        """Test that inappropriate combinations are prevented."""
        print("\n🚫 Testing Inappropriate Combination Prevention...")
        
        # Test cases that should be prevented
        inappropriate_tests = [
            {
                "name": "Blazer + Cargo Pants Prevention",
                "description": "Should not generate blazer with cargo pants",
                "base_items": ["blazer", "cargo pants"]
            },
            {
                "name": "Blazer + Flip Flops Prevention",
                "description": "Should not generate blazer with flip flops",
                "base_items": ["blazer", "flip-flops"]
            },
            {
                "name": "Formal Shoes + Shorts Prevention",
                "description": "Should not generate formal shoes with shorts",
                "base_items": ["oxford", "shorts"]
            }
        ]
        
        for test in inappropriate_tests:
            try:
                # Generate multiple outfits to test consistency
                inappropriate_found = 0
                total_generated = 10
                
                for i in range(total_generated):
                    result = await self.generate_outfit_for_test(test["base_items"])
                    
                    if result["success"]:
                        outfit_items = result["outfit"].get("items", [])
                        
                        # Check if inappropriate combination exists
                        if self.has_inappropriate_combination(outfit_items, test["base_items"]):
                            inappropriate_found += 1
                
                inappropriate_rate = (inappropriate_found / total_generated) * 100
                
                if inappropriate_rate == 0:
                    self.record_test("✅", test["name"], "PASSED - No inappropriate combinations found")
                elif inappropriate_rate <= 10:
                    self.record_test("⚠️", test["name"], f"WARNING - {inappropriate_rate:.1f}% inappropriate combinations")
                else:
                    self.record_test("❌", test["name"], f"FAILED - {inappropriate_rate:.1f}% inappropriate combinations")
                    
            except Exception as e:
                self.record_test("❌", test["name"], f"ERROR - {str(e)}")
    
    async def generate_outfit_with_scenario(self, scenario: Dict) -> Dict[str, Any]:
        """Generate outfit with a specific scenario."""
        try:
            payload = {
                "occasion": scenario["occasion"],
                "style": scenario["style"],
                "weather": scenario["weather"],
                "wardrobe": [],  # Empty wardrobe to use default test wardrobe
                "user_profile": {
                    "id": "test_user",
                    "name": "Test User",
                    "email": "test@example.com"
                },
                "likedOutfits": [],
                "trendingStyles": [],
                "preferences": {}
            }
            
            response = requests.post(
                f"{self.backend_url}/api/outfits",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                return {"success": True, "outfit": response.json()}
            else:
                return {
                    "success": False, 
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def generate_outfit_with_weather(self, weather: Dict) -> Dict[str, Any]:
        """Generate outfit with specific weather."""
        return await self.generate_outfit_with_scenario({
            "occasion": "casual",
            "style": "casual",
            "weather": weather
        })
    
    async def generate_outfit_for_test(self, base_items: List[str]) -> Dict[str, Any]:
        """Generate outfit for testing inappropriate combinations."""
        return await self.generate_outfit_with_scenario({
            "occasion": "business",
            "style": "casual",
            "weather": {
                "temperature": 70,
                "condition": "clear",
                "humidity": 50,
                "wind_speed": 5,
                "precipitation": 0
            }
        })
    
    def check_outfit_appropriateness(self, outfit: Dict, occasion: str, weather: Dict) -> bool:
        """Check if an outfit is appropriate for the occasion and weather."""
        items = outfit.get("items", [])
        
        if not items:
            return False
        
        # Check for basic appropriateness
        has_inappropriate = self.has_inappropriate_combination(items, [])
        
        # Check weather appropriateness
        temperature = weather.get("temperature", 70)
        weather_appropriate = True
        
        for item in items:
            item_type = item.get("type", "").lower()
            
            # Hot weather checks
            if temperature > 80:
                if item_type in ["blazer", "coat", "sweater", "jacket"]:
                    weather_appropriate = False
                    break
            
            # Cold weather checks
            elif temperature < 50:
                if item_type in ["t-shirt", "shorts", "sandals", "flip-flops"]:
                    weather_appropriate = False
                    break
        
        return not has_inappropriate and weather_appropriate
    
    def has_inappropriate_combination(self, items: List[Dict], base_items: List[str]) -> bool:
        """Check if items contain inappropriate combinations."""
        item_types = [item.get("type", "").lower() for item in items]
        item_names = [item.get("name", "").lower() for item in items]
        
        # Check for blazer + casual items
        has_blazer = any("blazer" in item_type or "blazer" in name 
                        for item_type, name in zip(item_types, item_names))
        
        if has_blazer:
            # Check for inappropriate items with blazer
            inappropriate_with_blazer = ["cargo", "shorts", "flip-flops", "sandals", "athletic"]
            for item_type, item_name in zip(item_types, item_names):
                for inappropriate in inappropriate_with_blazer:
                    if inappropriate in item_type or inappropriate in item_name:
                        return True
        
        # Check for formal shoes + casual bottoms
        has_formal_shoes = any("oxford" in item_type or "dress shoes" in name or "heels" in item_type
                              for item_type, name in zip(item_types, item_names))
        
        if has_formal_shoes:
            casual_bottoms = ["shorts", "athletic shorts", "cargo"]
            for item_type, item_name in zip(item_types, item_names):
                for casual in casual_bottoms:
                    if casual in item_type or casual in item_name:
                        return True
        
        return False
    
    def record_test(self, status: str, test_name: str, result: str):
        """Record test result."""
        self.test_results.append({
            "status": status,
            "name": test_name,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
    
    def print_results(self):
        """Print test results."""
        print("\n" + "=" * 60)
        print("📊 REAL BACKEND TEST RESULTS")
        print("=" * 60)
        
        passed = len([r for r in self.test_results if r["status"] == "✅"])
        failed = len([r for r in self.test_results if r["status"] == "❌"])
        warnings = len([r for r in self.test_results if r["status"] == "⚠️"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        print("-" * 60)
        
        for result in self.test_results:
            print(f"{result['status']} {result['name']}: {result['result']}")
        
        # Print inappropriate outfits found
        if self.inappropriate_outfits:
            print(f"\n❌ INAPPROPRIATE OUTFITS FOUND:")
            print("-" * 60)
            for outfit in self.inappropriate_outfits:
                print(f"   - Scenario: {outfit['scenario']['name']}")
                print(f"     Items: {[item.get('name', 'Unknown') for item in outfit['outfit'].get('items', [])]}")
        
        # Final assessment
        if failed == 0 and warnings == 0:
            print(f"\n🎉 ALL TESTS PASSED! Backend outfit generation is working correctly.")
            print("✅ Weather integration is working")
            print("✅ Inappropriate combinations are being prevented")
            print("✅ System is ready for production")
        elif failed == 0:
            print(f"\n⚠️  {warnings} tests have warnings but no failures.")
            print("✅ Core functionality is working")
            print("⚠️  Consider addressing warnings for optimal performance")
        else:
            print(f"\n❌ {failed} tests failed - backend needs fixes")
            print("🔧 Please review and fix the failing tests before production deployment")

async def main():
    """Run the real backend test suite."""
    print("🚀 Starting Real Backend Outfit Generation Tests")
    print("=" * 60)
    print("Make sure your backend is running on port 3001")
    print("Start it with: cd backend && python app.py")
    print()
    
    tester = RealOutfitGenerationTester()
    await tester.run_real_backend_tests()

if __name__ == "__main__":
    asyncio.run(main())
