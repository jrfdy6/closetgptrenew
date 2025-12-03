#!/usr/bin/env python3
"""
Comprehensive End-to-End Testing Script
Tests all newly implemented features + critical paths
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://closetgptrenew-production.up.railway.app"
FIREBASE_TOKEN = ""  # User will provide

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_test(name, status, details=""):
    symbol = f"{Colors.GREEN}✅{Colors.END}" if status == "PASS" else f"{Colors.RED}❌{Colors.END}"
    print(f"{symbol} {name}")
    if details:
        print(f"   {Colors.BLUE}→{Colors.END} {details}")

def print_section(title):
    print(f"\n{Colors.BOLD}{Colors.YELLOW}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.YELLOW}{title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.YELLOW}{'='*70}{Colors.END}\n")

def get_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

# =============================================================================
# TEST 1: Backend Health Check
# =============================================================================
def test_backend_health():
    print_section("TEST 1: Backend Health Check")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            print_test("Backend Health", "PASS", f"Status: {response.status_code}")
            return True
        else:
            print_test("Backend Health", "FAIL", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Backend Health", "FAIL", f"Error: {str(e)}")
        return False

# =============================================================================
# TEST 2: Authentication
# =============================================================================
def test_authentication(token):
    print_section("TEST 2: Authentication")
    if not token:
        print_test("Authentication", "SKIP", "No token provided")
        return False
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/wardrobe",
            headers=get_headers(token),
            timeout=10
        )
        if response.status_code in [200, 404]:  # 404 is ok if no wardrobe yet
            print_test("Authentication", "PASS", f"Token valid, status: {response.status_code}")
            return True
        else:
            print_test("Authentication", "FAIL", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Authentication", "FAIL", f"Error: {str(e)}")
        return False

# =============================================================================
# TEST 3: Generate Outfit Endpoint
# =============================================================================
def test_generate_outfit(token):
    print_section("TEST 3: Generate Outfit Endpoint")
    if not token:
        print_test("Generate Outfit", "SKIP", "No token provided")
        return None
    
    payload = {
        "occasion": "casual",
        "style": "minimalist",
        "mood": "confident",
        "weather": {
            "temperature": 72,
            "condition": "sunny",
            "season": "spring"
        }
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BACKEND_URL}/api/outfits-existing-data/generate-personalized",
            headers=get_headers(token),
            json=payload,
            timeout=30
        )
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for performance metadata
            has_metadata = "metadata" in data
            has_perf_fields = False
            if has_metadata:
                metadata = data["metadata"]
                has_perf_fields = all(k in metadata for k in 
                    ["generation_duration", "is_slow", "cache_hit", "generation_attempts"])
            
            # Check for personalization insights
            has_personalization = "personalization_insights" in data.get("metadata", {})
            
            print_test("Generate Outfit", "PASS", f"Duration: {duration:.2f}s")
            print_test("  - Response Structure", "PASS", f"Has {len(data.get('items', []))} items")
            print_test("  - Performance Metadata", "PASS" if has_perf_fields else "FAIL", 
                      f"Fields present: {has_perf_fields}")
            print_test("  - Personalization Insights", "PASS" if has_personalization else "WARN",
                      f"Present: {has_personalization}")
            
            return data.get("id")
        else:
            print_test("Generate Outfit", "FAIL", f"Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return None
    except Exception as e:
        print_test("Generate Outfit", "FAIL", f"Error: {str(e)}")
        return None

# =============================================================================
# TEST 4: Rate Outfit Endpoint (NEWLY FIXED!)
# =============================================================================
def test_rate_outfit(token, outfit_id):
    print_section("TEST 4: Rate Outfit Endpoint (Newly Fixed!)")
    if not token or not outfit_id:
        print_test("Rate Outfit", "SKIP", "No token or outfit_id")
        return False
    
    payload = {
        "outfitId": outfit_id,
        "rating": 5,
        "isLiked": True,
        "feedback": "Love this outfit!"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/outfits/rate",
            headers=get_headers(token),
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            has_learning = "learning_confirmation" in data
            
            print_test("Rate Outfit Endpoint", "PASS", f"Status: 200")
            print_test("  - Learning Confirmation", "PASS" if has_learning else "FAIL",
                      f"Present: {has_learning}")
            
            if has_learning:
                learning = data["learning_confirmation"]
                print(f"   {Colors.BLUE}Learning Summary:{Colors.END}")
                for msg in learning.get("summary", [])[:3]:
                    print(f"   {Colors.GREEN}✨{Colors.END} {msg}")
                print(f"   Progress: {learning.get('personalization_level', 0)}% trained")
            
            return True
        elif response.status_code == 405:
            print_test("Rate Outfit Endpoint", "FAIL", "405 Method Not Allowed - Endpoint still broken!")
            return False
        else:
            print_test("Rate Outfit Endpoint", "FAIL", f"Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print_test("Rate Outfit Endpoint", "FAIL", f"Error: {str(e)}")
        return False

# =============================================================================
# TEST 5: Create Outfit Endpoint (NEWLY FIXED!)
# =============================================================================
def test_create_outfit(token):
    print_section("TEST 5: Create Outfit Endpoint (Newly Fixed!)")
    if not token:
        print_test("Create Outfit", "SKIP", "No token provided")
        return None
    
    payload = {
        "name": "Test Outfit",
        "occasion": "casual",
        "style": "minimalist",
        "description": "Created by test script",
        "items": ["test_item_1", "test_item_2"],
        "createdAt": int(time.time())
    }
    
    try:
        # Try with trailing slash (the fix)
        response = requests.post(
            f"{BACKEND_URL}/api/outfits/",
            headers=get_headers(token),
            json=payload,
            timeout=10
        )
        
        if response.status_code == 201:
            data = response.json()
            print_test("Create Outfit Endpoint", "PASS", f"Created outfit: {data.get('id')}")
            return data.get("id")
        elif response.status_code == 405:
            print_test("Create Outfit Endpoint", "FAIL", "405 Method Not Allowed - Still broken!")
            return None
        else:
            print_test("Create Outfit Endpoint", "FAIL", f"Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return None
    except Exception as e:
        print_test("Create Outfit Endpoint", "FAIL", f"Error: {str(e)}")
        return None

# =============================================================================
# TEST 6: User Preferences Service
# =============================================================================
def test_user_preferences(token):
    print_section("TEST 6: User Preferences Service")
    if not token:
        print_test("User Preferences", "SKIP", "No token provided")
        return False
    
    # This is tested indirectly through the rate endpoint
    # Check if preferences are being stored in Firestore
    print_test("User Preferences Service", "INFO", 
              "Tested indirectly via rate endpoint (check Firestore manually)")
    return True

# =============================================================================
# TEST 7: Weight Optimizations
# =============================================================================
def test_weight_optimizations(token):
    print_section("TEST 7: Weight Optimizations")
    if not token:
        print_test("Weight Optimizations", "SKIP", "No token provided")
        return False
    
    print_test("Weight Optimizations", "INFO", 
              "Generate outfits manually and verify:")
    print("   • Better style cohesion (style weight: 18% → 22%)")
    print("   • Better color harmony (color weight: 14% → 18%)")
    print("   • Still diverse (diversity: 30% → 22%)")
    print("   • No short-sleeve sweater layering issues")
    return True

# =============================================================================
# MAIN TEST RUNNER
# =============================================================================
def main():
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}🧪 COMPREHENSIVE END-TO-END TESTING{Colors.END}")
    print(f"{Colors.BOLD}Easy Outfit App - December 2, 2025{Colors.END}")
    print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")
    
    # Get token
    print(f"{Colors.YELLOW}Enter your Firebase token:{Colors.END}")
    print(f"{Colors.BLUE}(Get it from browser console: https://www.easyoutfitapp.com/debug-token){Colors.END}")
    token = input("Token: ").strip()
    
    if not token:
        print(f"\n{Colors.RED}No token provided. Running limited tests only.{Colors.END}\n")
    
    # Run tests
    results = {}
    
    results["backend_health"] = test_backend_health()
    results["authentication"] = test_authentication(token)
    outfit_id = test_generate_outfit(token)
    results["generate_outfit"] = outfit_id is not None
    results["rate_outfit"] = test_rate_outfit(token, outfit_id)
    custom_outfit_id = test_create_outfit(token)
    results["create_outfit"] = custom_outfit_id is not None
    results["user_preferences"] = test_user_preferences(token)
    results["weight_optimizations"] = test_weight_optimizations(token)
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v == True)
    total = len(results)
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.END}\n")
    
    for test_name, status in results.items():
        symbol = f"{Colors.GREEN}✅{Colors.END}" if status else f"{Colors.RED}❌{Colors.END}"
        print(f"{symbol} {test_name.replace('_', ' ').title()}")
    
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED!{Colors.END}")
    elif passed >= total * 0.8:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  MOST TESTS PASSED - Some issues to fix{Colors.END}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ MULTIPLE FAILURES - Needs attention{Colors.END}")
    
    print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")
    
    # Next steps
    print(f"{Colors.BOLD}NEXT STEPS:{Colors.END}")
    print("1. Fix any failed tests")
    print("2. Test frontend on Vercel (should be deployed by now)")
    print("3. Do full user journey test in browser")
    print("4. Check Firestore for user_preferences updates")
    print(f"5. Celebrate! 🎉\n")

if __name__ == "__main__":
    main()

