#!/usr/bin/env python3
"""
Production API Testing Suite for ClosetGPT Backend
Tests all core endpoints, error handling, and edge cases
"""

import requests
import json
import time
import os
import sys
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TestResult:
    test_name: str
    status: str  # 'PASS', 'FAIL', 'ERROR'
    duration: float
    error_message: str = ""
    response_data: Dict[str, Any] = None

class ProductionAPITester:
    def __init__(self, base_url: str = "http://localhost:3001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results: List[TestResult] = []
        self.test_user_id = None
        self.test_wardrobe_items = []
        
    def log_test(self, test_name: str, status: str, duration: float, error_message: str = "", response_data: Dict[str, Any] = None):
        """Log test result"""
        result = TestResult(
            test_name=test_name,
            status=status,
            duration=duration,
            error_message=error_message,
            response_data=response_data
        )
        self.test_results.append(result)
        print(f"[{status}] {test_name} ({duration:.2f}s)")
        if error_message:
            print(f"  Error: {error_message}")
    
    def test_health_check(self) -> bool:
        """Test basic health check endpoint"""
        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}/health")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.log_test("Health Check", "PASS", duration, response_data=response.json())
                return True
            else:
                self.log_test("Health Check", "FAIL", duration, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Health Check", "ERROR", duration, str(e))
            return False
    
    def test_authentication_flow(self) -> bool:
        """Test user authentication flow"""
        start_time = time.time()
        try:
            # Test user registration
            register_data = {
                "email": "test@example.com",
                "password": "securePassword123",
                "name": "Test User"
            }
            
            response = self.session.post(f"{self.base_url}/api/auth/register", json=register_data)
            duration = time.time() - start_time
            
            if response.status_code in [200, 201, 409]:  # 409 = user already exists
                self.log_test("User Registration", "PASS", duration, response_data=response.json())
                
                # Test login
                login_data = {
                    "email": "test@example.com",
                    "password": "securePassword123"
                }
                
                login_response = self.session.post(f"{self.base_url}/api/auth/login", json=login_data)
                if login_response.status_code == 200:
                    login_data = login_response.json()
                    self.test_user_id = login_data.get("user_id")
                    self.session.headers.update({"Authorization": f"Bearer {login_data.get('token')}"})
                    self.log_test("User Login", "PASS", time.time() - start_time, response_data=login_data)
                    return True
                else:
                    self.log_test("User Login", "FAIL", time.time() - start_time, f"Status code: {login_response.status_code}")
                    return False
            else:
                self.log_test("User Registration", "FAIL", duration, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Authentication Flow", "ERROR", duration, str(e))
            return False
    
    def test_wardrobe_management(self) -> bool:
        """Test wardrobe item management"""
        if not self.test_user_id:
            self.log_test("Wardrobe Management", "FAIL", 0, "No authenticated user")
            return False
            
        start_time = time.time()
        try:
            # Test adding wardrobe item
            item_data = {
                "name": "Test Blue Shirt",
                "type": "shirt",
                "color": "blue",
                "style": ["casual"],
                "occasion": ["daily"],
                "season": ["spring", "summer"],
                "imageUrl": "https://example.com/test-shirt.jpg"
            }
            
            response = self.session.post(f"{self.base_url}/api/wardrobe/add", json=item_data)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                item_id = response.json().get("id")
                self.test_wardrobe_items.append(item_id)
                self.log_test("Add Wardrobe Item", "PASS", duration, response_data=response.json())
                
                # Test getting wardrobe items
                get_response = self.session.get(f"{self.base_url}/api/wardrobe/")
                if get_response.status_code == 200:
                    response_data = get_response.json()
                    # Handle both list and object responses
                    if isinstance(response_data, list):
                        items = response_data
                    else:
                        items = response_data.get("items", [])
                    
                    if len(items) > 0:
                        self.log_test("Get Wardrobe Items", "PASS", time.time() - start_time, response_data={"items": items, "count": len(items)})
                        return True
                    else:
                        self.log_test("Get Wardrobe Items", "FAIL", time.time() - start_time, "No items returned")
                        return False
                else:
                    self.log_test("Get Wardrobe Items", "FAIL", time.time() - start_time, f"Status code: {get_response.status_code}")
                    return False
            else:
                self.log_test("Add Wardrobe Item", "FAIL", duration, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Wardrobe Management", "ERROR", duration, str(e))
            return False
    
    def test_outfit_generation(self) -> bool:
        """Test outfit generation functionality"""
        if not self.test_user_id or not self.test_wardrobe_items:
            self.log_test("Outfit Generation", "FAIL", 0, "No wardrobe items available")
            return False
            
        start_time = time.time()
        try:
            # Get user's wardrobe items first
            wardrobe_response = self.session.get(f"{self.base_url}/api/wardrobe/")
            if wardrobe_response.status_code != 200:
                self.log_test("Outfit Generation", "FAIL", time.time() - start_time, "Could not fetch wardrobe items")
                return False
            
            wardrobe_data = wardrobe_response.json()
            if isinstance(wardrobe_data, list):
                wardrobe_items = wardrobe_data
            else:
                wardrobe_items = wardrobe_data.get("items", [])
            
            if len(wardrobe_items) == 0:
                self.log_test("Outfit Generation", "FAIL", time.time() - start_time, "No wardrobe items available")
                return False
            
            # Create user profile data
            user_profile = {
                "id": self.test_user_id,
                "bodyType": "rectangle",
                "skinTone": "neutral",
                "stylePreferences": ["casual", "minimalist"],
                "colorPreferences": ["blue", "gray", "white"]
            }
            
            generation_data = {
                "occasion": "casual",
                "weather": {
                    "temperature": 72,
                    "condition": "sunny"
                },
                "wardrobe": wardrobe_items[:5],  # Use first 5 items
                "user_profile": user_profile,
                "likedOutfits": [],
                "trendingStyles": ["casual", "minimalist"],
                "preferences": ["comfortable", "minimalist"]
            }
            
            response = self.session.post(f"{self.base_url}/api/outfit/generate", json=generation_data)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                outfit = response.json()
                if "items" in outfit and len(outfit["items"]) > 0:
                    self.log_test("Outfit Generation", "PASS", duration, response_data=outfit)
                    return True
                else:
                    self.log_test("Outfit Generation", "FAIL", duration, "No outfit items generated")
                    return False
            else:
                self.log_test("Outfit Generation", "FAIL", duration, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Outfit Generation", "ERROR", duration, str(e))
            return False
    
    def test_image_analysis(self) -> bool:
        """Test AI image analysis functionality"""
        start_time = time.time()
        try:
            # Test with a sample image URL
            analysis_data = {
                "image_url": "https://example.com/test-shirt.jpg"
            }
            
            response = self.session.post(f"{self.base_url}/api/analyze-image", json=analysis_data)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                analysis = response.json()
                if "type" in analysis and "color" in analysis:
                    self.log_test("Image Analysis", "PASS", duration, response_data=analysis)
                    return True
                else:
                    self.log_test("Image Analysis", "FAIL", duration, "Missing analysis data")
                    return False
            else:
                self.log_test("Image Analysis", "FAIL", duration, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Image Analysis", "ERROR", duration, str(e))
            return False
    
    def test_weather_integration(self) -> bool:
        """Test weather API integration"""
        start_time = time.time()
        try:
            weather_data = {
                "location": "New York"
            }
            
            response = self.session.post(f"{self.base_url}/api/weather", json=weather_data)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                weather = response.json()
                if "temperature" in weather and "condition" in weather:
                    self.log_test("Weather Integration", "PASS", duration, response_data=weather)
                    return True
                else:
                    self.log_test("Weather Integration", "FAIL", duration, "Missing weather data")
                    return False
            else:
                self.log_test("Weather Integration", "FAIL", duration, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Weather Integration", "ERROR", duration, str(e))
            return False
    
    def test_trends_integration(self) -> bool:
        """Test fashion trends integration"""
        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}/api/wardrobe/trending-styles")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                trends = response.json()
                if isinstance(trends, list) and len(trends) > 0:
                    self.log_test("Trends Integration", "PASS", duration, response_data=trends)
                    return True
                else:
                    self.log_test("Trends Integration", "FAIL", duration, "No trends data returned")
                    return False
            else:
                self.log_test("Trends Integration", "FAIL", duration, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Trends Integration", "ERROR", duration, str(e))
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling for invalid requests"""
        start_time = time.time()
        try:
            # Test invalid endpoint
            response = self.session.get(f"{self.base_url}/api/invalid-endpoint")
            duration = time.time() - start_time
            
            if response.status_code == 404:
                self.log_test("404 Error Handling", "PASS", duration)
            else:
                self.log_test("404 Error Handling", "FAIL", duration, f"Expected 404, got {response.status_code}")
            
            # Test invalid JSON
            response = self.session.post(f"{self.base_url}/api/wardrobe/add", data="invalid json")
            duration = time.time() - start_time
            
            if response.status_code == 400:
                self.log_test("Invalid JSON Handling", "PASS", duration)
                return True
            else:
                self.log_test("Invalid JSON Handling", "FAIL", duration, f"Expected 400, got {response.status_code}")
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Error Handling", "ERROR", duration, str(e))
            return False
    
    def test_performance(self) -> bool:
        """Test API performance under load"""
        start_time = time.time()
        try:
            # Test multiple concurrent requests
            import concurrent.futures
            
            def make_request():
                return self.session.get(f"{self.base_url}/api/wardrobe")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request) for _ in range(10)]
                responses = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            duration = time.time() - start_time
            
            # Check all responses were successful
            successful_responses = [r for r in responses if r.status_code == 200]
            if len(successful_responses) == len(responses):
                self.log_test("Performance Test", "PASS", duration, f"All {len(responses)} requests successful")
                return True
            else:
                self.log_test("Performance Test", "FAIL", duration, f"{len(successful_responses)}/{len(responses)} requests successful")
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Performance Test", "ERROR", duration, str(e))
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all production tests"""
        print("🚀 Starting ClosetGPT Production API Testing Suite")
        print("=" * 60)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Authentication Flow", self.test_authentication_flow),
            ("Wardrobe Management", self.test_wardrobe_management),
            ("Outfit Generation", self.test_outfit_generation),
            ("Image Analysis", self.test_image_analysis),
            ("Weather Integration", self.test_weather_integration),
            ("Trends Integration", self.test_trends_integration),
            ("Error Handling", self.test_error_handling),
            ("Performance Test", self.test_performance)
        ]
        
        passed = 0
        failed = 0
        errors = 0
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                errors += 1
                self.log_test(test_name, "ERROR", 0, str(e))
        
        # Generate summary
        total_tests = len(tests)
        summary = {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "success_rate": (passed / total_tests) * 100 if total_tests > 0 else 0,
            "test_results": self.test_results,
            "timestamp": datetime.now().isoformat()
        }
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Errors: {errors}")
        print(f"📈 Success Rate: {summary['success_rate']:.1f}%")
        
        if failed > 0 or errors > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if result.status in ["FAIL", "ERROR"]:
                    print(f"  - {result.test_name}: {result.error_message}")
        
        return summary

def main():
    """Main function to run the production test suite"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ClosetGPT Production API Testing Suite")
    parser.add_argument("--base-url", default="http://localhost:3001", help="Base URL for the API")
    parser.add_argument("--output", help="Output file for test results (JSON)")
    
    args = parser.parse_args()
    
    tester = ProductionAPITester(args.base_url)
    results = tester.run_all_tests()
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n📄 Test results saved to: {args.output}")
    
    # Exit with appropriate code
    if results["failed"] > 0 or results["errors"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main() 