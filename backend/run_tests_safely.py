#!/usr/bin/env python3
"""
Safe Test Runner - Runs comprehensive tests with proper environment setup
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Any

def check_environment():
    """Check if we're in a safe environment to run tests."""
    print("🔍 Checking Environment Safety")
    print("=" * 40)
    
    warnings = []
    
    # Check if we're in a git repository
    if not Path(".git").exists():
        warnings.append("Not in a git repository - no version control backup")
    
    # Check for environment variables
    env_vars = ["OPENAI_API_KEY", "FIREBASE_PROJECT_ID"]
    missing_vars = []
    
    for var in env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        warnings.append(f"Missing environment variables: {missing_vars}")
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        warnings.append("Not in a virtual environment")
    
    if warnings:
        print("⚠️  Warnings found:")
        for warning in warnings:
            print(f"   - {warning}")
        
        response = input("\n🤔 Continue anyway? (y/n): ")
        if response.lower() not in ['y', 'yes']:
            print("❌ Test execution cancelled")
            return False
    
    print("✅ Environment check completed")
    return True

def setup_test_environment():
    """Set up a safe test environment."""
    print("\n🔧 Setting up Test Environment")
    print("=" * 40)
    
    # Create test directories
    test_dirs = ["test_output", "test_logs", "test_data"]
    for dir_name in test_dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"   📁 Created: {dir_name}")
    
    # Create test configuration
    test_config = {
        "test_mode": True,
        "mock_services": True,
        "log_level": "DEBUG",
        "output_dir": "test_output"
    }
    
    with open("test_config.json", "w") as f:
        json.dump(test_config, f, indent=2)
    
    print("   ⚙️  Created: test_config.json")
    print("✅ Test environment ready")

def run_safe_tests():
    """Run the safe test suite first."""
    print("\n🛡️  Running Safe Tests")
    print("=" * 40)
    
    try:
        result = subprocess.run([sys.executable, "safe_test_runner.py"], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Safe tests passed")
            return True
        else:
            print(f"❌ Safe tests failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Safe tests timed out")
        return False
    except Exception as e:
        print(f"❌ Safe tests error: {str(e)}")
        return False

def run_comprehensive_tests():
    """Run the comprehensive test suite."""
    print("\n🧪 Running Comprehensive Tests")
    print("=" * 40)
    
    try:
        # Set test environment variables
        env = os.environ.copy()
        env["TEST_MODE"] = "true"
        env["LOG_LEVEL"] = "DEBUG"
        
        result = subprocess.run([sys.executable, "tests/comprehensive_outfit_testing_framework.py"], 
                              env=env, capture_output=True, text=True, timeout=300)
        
        # Save test output
        with open("test_output/comprehensive_test_results.txt", "w") as f:
            f.write(f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}")
        
        if result.returncode == 0:
            print("✅ Comprehensive tests completed")
            print(f"   📄 Results saved to: test_output/comprehensive_test_results.txt")
            return True
        else:
            print(f"❌ Comprehensive tests failed")
            print(f"   📄 Error details saved to: test_output/comprehensive_test_results.txt")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Comprehensive tests timed out (5 minutes)")
        return False
    except Exception as e:
        print(f"❌ Comprehensive tests error: {str(e)}")
        return False

def cleanup_test_environment():
    """Clean up test environment."""
    print("\n🧹 Cleaning up Test Environment")
    print("=" * 40)
    
    # Remove test configuration
    if Path("test_config.json").exists():
        Path("test_config.json").unlink()
        print("   🗑️  Removed: test_config.json")
    
    # Keep test output for review
    print("   📁 Test output preserved in: test_output/")
    print("✅ Cleanup completed")

def main():
    """Main function to run tests safely."""
    print("🚀 Safe Test Runner for Outfit Generation System")
    print("=" * 60)
    
    # Step 1: Environment check
    if not check_environment():
        return
    
    # Step 2: Setup test environment
    setup_test_environment()
    
    # Step 3: Run safe tests first
    if not run_safe_tests():
        print("\n❌ Safe tests failed - stopping execution")
        cleanup_test_environment()
        return
    
    # Step 4: Ask for confirmation before comprehensive tests
    print("\n⚠️  About to run comprehensive tests that may interact with services")
    response = input("🤔 Continue with comprehensive tests? (y/n): ")
    
    if response.lower() not in ['y', 'yes']:
        print("❌ Comprehensive tests skipped")
        cleanup_test_environment()
        return
    
    # Step 5: Run comprehensive tests
    success = run_comprehensive_tests()
    
    # Step 6: Cleanup
    cleanup_test_environment()
    
    # Step 7: Final summary
    print("\n📊 Test Execution Summary")
    print("=" * 40)
    if success:
        print("✅ All tests completed successfully!")
        print("   📄 Check test_output/ for detailed results")
    else:
        print("❌ Some tests failed")
        print("   📄 Check test_output/ for error details")
    
    print("\n🎯 Next Steps:")
    print("   1. Review test results in test_output/")
    print("   2. Address any failures or warnings")
    print("   3. Run specific test categories if needed")

if __name__ == "__main__":
    main() 