#!/usr/bin/env python3
"""
Test runner for the modular pipeline components.
"""

import pytest
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def run_all_tests():
    """Run all modular pipeline tests."""
    print("🧪 Running modular pipeline tests...")
    
    test_files = [
        "tests/test_initial_filter.py",
        "tests/test_smart_selector.py", 
        "tests/test_validation_orchestrator.py",
        "tests/test_fallback_handler.py",
        "tests/test_e2e_pipeline.py"
    ]
    
    results = []
    
    for test_file in test_files:
        print(f"\n📋 Running {test_file}...")
        try:
            result = pytest.main([test_file, "-v"])
            results.append((test_file, result == 0))
            status = "✅ PASSED" if result == 0 else "❌ FAILED"
            print(f"   {status}")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results.append((test_file, False))
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_file, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} {test_file}")
    
    print(f"\n🎯 Results: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All modular pipeline tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 