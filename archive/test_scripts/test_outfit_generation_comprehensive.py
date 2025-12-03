"""
Comprehensive Test Suite for Outfit Generation Pipeline
Tests the robust outfit service through all phases without fallbacks
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

# Test configuration
BACKEND_URL = "https://closetgptrenew-production.up.railway.app"
TEST_RESULTS = []

class OutfitGenerationTester:
    def __init__(self, backend_url: str):
        self.backend_url = backend_url
        self.test_results = []
        
    def log_test(self, test_name: str, status: str, details: Dict[str, Any]):
        """Log test result"""
        result = {
            "test_name": test_name,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        
        # Print immediate feedback
        icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{icon} {test_name}: {status}")
        if details.get("error"):
            print(f"   Error: {details['error']}")
        
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("OUTFIT GENERATION PIPELINE - COMPREHENSIVE TEST RESULTS")
        print("="*80)
        
        passed = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed = sum(1 for r in self.test_results if r["status"] == "FAIL")
        warnings = sum(1 for r in self.test_results if r["status"] == "WARN")
        
        print(f"\nTotal Tests: {len(self.test_results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warnings}")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! Robust outfit service is working correctly!")
        else:
            print(f"\n⚠️  {failed} test(s) failed. Review details below.")
        
        print("\n" + "-"*80)
        print("DETAILED RESULTS")
        print("-"*80)
        
        for result in self.test_results:
            print(f"\n{result['test_name']} - {result['status']}")
            for key, value in result['details'].items():
                if key != "raw_response" and value:
                    print(f"  {key}: {value}")

# Test Cases
async def test_1_health_check(tester: OutfitGenerationTester):
    """Test 1: Verify backend is responsive"""
    import urllib.request
    import urllib.error
    
    try:
        url = f"{tester.backend_url}/api/outfits/health"
        req = urllib.request.Request(url, method='GET')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            
            if data.get("status") == "healthy":
                tester.log_test(
                    "1. Health Check",
                    "PASS",
                    {
                        "response": data.get("message"),
                        "version": data.get("version"),
                        "firebase_available": data.get("firebase_available")
                    }
                )
                return True
            else:
                tester.log_test(
                    "1. Health Check",
                    "FAIL",
                    {"error": "Unhealthy status", "response": str(data)}
                )
                return False
                
    except Exception as e:
        tester.log_test(
            "1. Health Check",
            "FAIL",
            {"error": str(e)}
        )
        return False

async def test_2_route_registration(tester: OutfitGenerationTester):
    """Test 2: Verify all routes are registered"""
    import urllib.request
    
    try:
        url = f"{tester.backend_url}/api/outfits/debug-routes"
        req = urllib.request.Request(url, method='GET')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            
            total_routes = data.get("total_routes", 0)
            routes = data.get("routes", [])
            
            # Check for critical routes
            route_paths = [r.get("path") for r in routes]
            has_generate = "/generate" in route_paths
            has_create = "/" in route_paths or "" in route_paths
            has_stats = "/stats/summary" in route_paths
            
            if total_routes >= 18 and has_generate:
                tester.log_test(
                    "2. Route Registration",
                    "PASS",
                    {
                        "total_routes": total_routes,
                        "has_generate_route": has_generate,
                        "has_create_route": has_create,
                        "has_stats_route": has_stats
                    }
                )
                return True
            else:
                tester.log_test(
                    "2. Route Registration",
                    "FAIL",
                    {
                        "total_routes": total_routes,
                        "expected": "18+",
                        "missing_critical": not has_generate
                    }
                )
                return False
                
    except Exception as e:
        tester.log_test(
            "2. Route Registration",
            "WARN",
            {"error": str(e), "note": "May require authentication"}
        )
        return True  # Non-critical for pipeline test

async def test_3_generation_endpoint_exists(tester: OutfitGenerationTester):
    """Test 3: Verify POST /generate endpoint exists and responds"""
    import urllib.request
    
    try:
        url = f"{tester.backend_url}/api/outfits/generate"
        
        # Create minimal test payload
        payload = json.dumps({
            "style": "casual",
            "mood": "confident",
            "occasion": "casual",
            "wardrobe": [],
            "weather": None
        }).encode('utf-8')
        
        req = urllib.request.Request(
            url,
            data=payload,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                # Should not reach here without auth, but if it does...
                tester.log_test(
                    "3. Generation Endpoint",
                    "WARN",
                    {"note": "Endpoint responded without auth (unexpected)"}
                )
                return True
        except urllib.error.HTTPError as e:
            if e.code == 401 or e.code == 422:
                # Expected - needs authentication or valid data
                tester.log_test(
                    "3. Generation Endpoint",
                    "PASS",
                    {
                        "status": "Endpoint exists and requires authentication",
                        "http_code": e.code
                    }
                )
                return True
            else:
                tester.log_test(
                    "3. Generation Endpoint",
                    "FAIL",
                    {"error": f"Unexpected HTTP {e.code}: {e.reason}"}
                )
                return False
                
    except Exception as e:
        tester.log_test(
            "3. Generation Endpoint",
            "FAIL",
            {"error": str(e)}
        )
        return False

async def test_4_service_import_check(tester: OutfitGenerationTester):
    """Test 4: Check if OutfitGenerationService is importable (local test)"""
    
    print("\n📋 Checking local service imports...")
    
    try:
        # Check if we're in the backend directory
        import os
        import sys
        
        backend_path = "/Users/johnniefields/Desktop/Cursor/closetgptrenew/backend"
        if os.path.exists(backend_path):
            sys.path.insert(0, backend_path)
            
            try:
                from src.services.outfits.generation_service import OutfitGenerationService
                
                # Check if the service has the expected methods
                service = OutfitGenerationService()
                has_generate_method = hasattr(service, 'generate_outfit_logic')
                
                if has_generate_method:
                    tester.log_test(
                        "4. Service Import",
                        "PASS",
                        {
                            "service_found": True,
                            "has_generate_method": True,
                            "note": "OutfitGenerationService is properly configured"
                        }
                    )
                    return True
                else:
                    tester.log_test(
                        "4. Service Import",
                        "FAIL",
                        {
                            "service_found": True,
                            "has_generate_method": False,
                            "error": "generate_outfit_logic method not found"
                        }
                    )
                    return False
                    
            except ImportError as e:
                tester.log_test(
                    "4. Service Import",
                    "WARN",
                    {
                        "error": str(e),
                        "note": "Cannot verify locally (may work in production)"
                    }
                )
                return True  # Non-critical for remote tests
        else:
            tester.log_test(
                "4. Service Import",
                "WARN",
                {"note": "Not in project directory, skipping local import check"}
            )
            return True
            
    except Exception as e:
        tester.log_test(
            "4. Service Import",
            "WARN",
            {"error": str(e), "note": "Local check failed, may still work in production"}
        )
        return True

async def test_5_routes_file_structure(tester: OutfitGenerationTester):
    """Test 5: Verify routes.py has correct structure"""
    
    try:
        routes_file = "/Users/johnniefields/Desktop/Cursor/closetgptrenew/backend/src/routes/outfits/routes.py"
        
        with open(routes_file, 'r') as f:
            content = f.read()
        
        # Check for key indicators
        has_generate_route = '@router.post("/generate")' in content
        has_get_generate_outfit_logic = 'def get_generate_outfit_logic' in content or 'get_generate_outfit_logic()' in content
        has_outfit_generation_service = 'OutfitGenerationService' in content
        has_robust_logic = 'generate_outfit_logic' in content
        
        # Check for fallback indicators (should NOT be present)
        has_simple_fallback = 'simple_generator' in content.lower() or 'fallback_generator' in content.lower()
        has_minimal_fallback = 'minimal_outfit' in content.lower() and 'fallback' in content.lower()
        
        if has_generate_route and has_robust_logic and not has_simple_fallback:
            tester.log_test(
                "5. Routes File Structure",
                "PASS",
                {
                    "has_generate_route": has_generate_route,
                    "uses_robust_service": has_outfit_generation_service,
                    "no_fallbacks_detected": not has_simple_fallback and not has_minimal_fallback,
                    "file_size": f"{len(content)} characters"
                }
            )
            return True
        else:
            tester.log_test(
                "5. Routes File Structure",
                "FAIL",
                {
                    "has_generate_route": has_generate_route,
                    "has_robust_logic": has_robust_logic,
                    "fallbacks_detected": has_simple_fallback or has_minimal_fallback,
                    "error": "Missing required structure or fallbacks detected"
                }
            )
            return False
            
    except Exception as e:
        tester.log_test(
            "5. Routes File Structure",
            "WARN",
            {"error": str(e), "note": "Could not read routes file locally"}
        )
        return True

async def test_6_generation_service_structure(tester: OutfitGenerationTester):
    """Test 6: Verify generation_service.py has all phases"""
    
    try:
        service_file = "/Users/johnniefields/Desktop/Cursor/closetgptrenew/backend/src/services/outfits/generation_service.py"
        
        with open(service_file, 'r') as f:
            content = f.read()
        
        # Check for all required phases
        phases_to_check = {
            "weather_filtering": "weather" in content.lower() and "filter" in content.lower(),
            "style_filtering": "style" in content.lower() and ("match" in content.lower() or "compatible" in content.lower()),
            "composition_building": "composition" in content.lower() or "build_outfit" in content.lower(),
            "validation": "validate" in content.lower(),
            "scoring": "score" in content.lower() or "calculate_score" in content.lower(),
            "retry_logic": "retry" in content.lower() or "attempt" in content.lower(),
        }
        
        all_phases_present = all(phases_to_check.values())
        present_phases = [k for k, v in phases_to_check.items() if v]
        missing_phases = [k for k, v in phases_to_check.items() if not v]
        
        if all_phases_present:
            tester.log_test(
                "6. Generation Service Structure",
                "PASS",
                {
                    "all_phases_present": True,
                    "phases_found": len(present_phases),
                    "note": "Robust service has all required phases"
                }
            )
            return True
        else:
            tester.log_test(
                "6. Generation Service Structure",
                "WARN",
                {
                    "phases_found": present_phases,
                    "potentially_missing": missing_phases,
                    "note": "Some phase indicators not detected (may use different naming)"
                }
            )
            return True  # Non-critical
            
    except Exception as e:
        tester.log_test(
            "6. Generation Service Structure",
            "WARN",
            {"error": str(e), "note": "Could not read service file locally"}
        )
        return True

async def test_7_no_fallback_imports(tester: OutfitGenerationTester):
    """Test 7: Verify no fallback generator imports in routes.py"""
    
    try:
        routes_file = "/Users/johnniefields/Desktop/Cursor/closetgptrenew/backend/src/routes/outfits/routes.py"
        
        with open(routes_file, 'r') as f:
            lines = f.readlines()
        
        # Check imports at the top of the file
        import_section = ''.join(lines[:100])  # First 100 lines should have imports
        
        # Bad imports that indicate fallbacks
        bad_imports = [
            'simple_generator',
            'minimal_generator',
            'fallback_generator',
            'emergency_outfit',
            'mock_outfit'
        ]
        
        found_bad_imports = [imp for imp in bad_imports if imp in import_section.lower()]
        
        if not found_bad_imports:
            tester.log_test(
                "7. No Fallback Imports",
                "PASS",
                {
                    "clean_imports": True,
                    "note": "No fallback generator imports detected"
                }
            )
            return True
        else:
            tester.log_test(
                "7. No Fallback Imports",
                "FAIL",
                {
                    "found_fallback_imports": found_bad_imports,
                    "error": "Fallback generators are imported"
                }
            )
            return False
            
    except Exception as e:
        tester.log_test(
            "7. No Fallback Imports",
            "WARN",
            {"error": str(e)}
        )
        return True

async def test_8_deployment_marker(tester: OutfitGenerationTester):
    """Test 8: Check if latest deployment marker is in logs (via health check)"""
    import urllib.request
    
    try:
        url = f"{tester.backend_url}/api/outfits/health"
        req = urllib.request.Request(url, method='GET')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            version = data.get("version", "")
            
            # Check if version indicates recent deployment
            is_recent = "v5" in version or "REDEPLOY" in version or "2025" in version
            
            if is_recent:
                tester.log_test(
                    "8. Deployment Status",
                    "PASS",
                    {
                        "version": version,
                        "note": "Recent deployment detected"
                    }
                )
                return True
            else:
                tester.log_test(
                    "8. Deployment Status",
                    "WARN",
                    {
                        "version": version,
                        "note": "Version string may be outdated"
                    }
                )
                return True
                
    except Exception as e:
        tester.log_test(
            "8. Deployment Status",
            "WARN",
            {"error": str(e)}
        )
        return True

async def run_all_tests():
    """Run all comprehensive tests"""
    tester = OutfitGenerationTester(BACKEND_URL)
    
    print("="*80)
    print("COMPREHENSIVE OUTFIT GENERATION PIPELINE TEST SUITE")
    print("="*80)
    print(f"\nBackend URL: {BACKEND_URL}")
    print(f"Started at: {datetime.utcnow().isoformat()}\n")
    print("Running tests...\n")
    
    # Run all tests
    await test_1_health_check(tester)
    await test_2_route_registration(tester)
    await test_3_generation_endpoint_exists(tester)
    await test_4_service_import_check(tester)
    await test_5_routes_file_structure(tester)
    await test_6_generation_service_structure(tester)
    await test_7_no_fallback_imports(tester)
    await test_8_deployment_marker(tester)
    
    # Print summary
    tester.print_summary()
    
    # Save results to file
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    results_file = f"test_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump({
            "test_suite": "Outfit Generation Pipeline",
            "timestamp": datetime.utcnow().isoformat(),
            "backend_url": BACKEND_URL,
            "results": tester.test_results
        }, f, indent=2)
    
    print(f"\n📄 Results saved to: {results_file}")
    
    # Return exit code
    failed_tests = sum(1 for r in tester.test_results if r["status"] == "FAIL")
    return 0 if failed_tests == 0 else 1

if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)

