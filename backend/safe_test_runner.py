#!/usr/bin/env python3
"""
Safe Test Runner - Basic functionality testing without touching actual data
"""

import asyncio
import time
import json
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class SafeTestResult:
    """Safe test result with basic metrics."""
    test_name: str
    success: bool
    duration_ms: float
    message: str
    details: Dict[str, Any]

class SafeTestRunner:
    """Safe test runner that doesn't touch actual services or data."""
    
    def __init__(self):
        self.test_results = []
    
    async def run_safe_tests(self) -> Dict[str, Any]:
        """Run safe tests that won't break anything."""
        print("🛡️  Running Safe Tests (No Data Touching)")
        print("=" * 50)
        
        start_time = time.time()
        
        # Test 1: Basic Python functionality
        test_result = await self._test_basic_python_functionality()
        self.test_results.append(test_result)
        
        # Test 2: Import validation
        test_result = await self._test_import_validation()
        self.test_results.append(test_result)
        
        # Test 3: Configuration validation
        test_result = await self._test_configuration_validation()
        self.test_results.append(test_result)
        
        # Test 4: File structure validation
        test_result = await self._test_file_structure()
        self.test_results.append(test_result)
        
        # Test 5: Basic data structure validation
        test_result = await self._test_data_structures()
        self.test_results.append(test_result)
        
        total_time = time.time() - start_time
        
        results = {
            'summary': {
                'total_tests': len(self.test_results),
                'passed_tests': sum(1 for r in self.test_results if r.success),
                'failed_tests': sum(1 for r in self.test_results if not r.success),
                'total_duration_ms': total_time * 1000
            },
            'test_results': [vars(r) for r in self.test_results]
        }
        
        self._print_summary(results)
        return results
    
    async def _test_basic_python_functionality(self) -> SafeTestResult:
        """Test basic Python functionality."""
        start_time = time.time()
        
        try:
            # Test basic operations
            assert 2 + 2 == 4
            assert "hello" + " world" == "hello world"
            assert len([1, 2, 3]) == 3
            
            # Test async functionality
            await asyncio.sleep(0.01)
            
            duration = (time.time() - start_time) * 1000
            return SafeTestResult(
                test_name="Basic Python Functionality",
                success=True,
                duration_ms=duration,
                message="✅ Basic Python operations working correctly",
                details={"operations_tested": ["arithmetic", "string_concatenation", "list_length", "async_sleep"]}
            )
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return SafeTestResult(
                test_name="Basic Python Functionality",
                success=False,
                duration_ms=duration,
                message=f"❌ Basic Python test failed: {str(e)}",
                details={"error": str(e)}
            )
    
    async def _test_import_validation(self) -> SafeTestResult:
        """Test that required modules can be imported."""
        start_time = time.time()
        
        try:
            # Test basic imports
            import os
            import sys
            import json
            import asyncio
            from typing import Dict, List, Any
            
            # Test if our custom modules exist (without importing them)
            import importlib.util
            
            # Check if key files exist
            files_to_check = [
                "src/services/outfit_service.py",
                "src/services/outfit_fallback_service.py", 
                "src/custom_types/wardrobe.py",
                "src/custom_types/profile.py"
            ]
            
            existing_files = []
            missing_files = []
            
            for file_path in files_to_check:
                if importlib.util.find_spec(file_path.replace('/', '.').replace('.py', '')) is not None:
                    existing_files.append(file_path)
                else:
                    missing_files.append(file_path)
            
            duration = (time.time() - start_time) * 1000
            return SafeTestResult(
                test_name="Import Validation",
                success=len(missing_files) == 0,
                duration_ms=duration,
                message=f"✅ Found {len(existing_files)} files, missing {len(missing_files)}",
                details={
                    "existing_files": existing_files,
                    "missing_files": missing_files
                }
            )
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return SafeTestResult(
                test_name="Import Validation",
                success=False,
                duration_ms=duration,
                message=f"❌ Import validation failed: {str(e)}",
                details={"error": str(e)}
            )
    
    async def _test_configuration_validation(self) -> SafeTestResult:
        """Test basic configuration validation."""
        start_time = time.time()
        
        try:
            import os
            
            # Check for common environment variables
            env_vars_to_check = [
                "OPENAI_API_KEY",
                "FIREBASE_PROJECT_ID",
                "FIREBASE_PRIVATE_KEY_ID",
                "FIREBASE_PRIVATE_KEY"
            ]
            
            found_vars = []
            missing_vars = []
            
            for var in env_vars_to_check:
                if os.getenv(var):
                    found_vars.append(var)
                else:
                    missing_vars.append(var)
            
            duration = (time.time() - start_time) * 1000
            return SafeTestResult(
                test_name="Configuration Validation",
                success=len(found_vars) > 0,  # At least some config should be present
                duration_ms=duration,
                message=f"✅ Found {len(found_vars)} env vars, missing {len(missing_vars)}",
                details={
                    "found_environment_variables": found_vars,
                    "missing_environment_variables": missing_vars
                }
            )
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return SafeTestResult(
                test_name="Configuration Validation",
                success=False,
                duration_ms=duration,
                message=f"❌ Configuration validation failed: {str(e)}",
                details={"error": str(e)}
            )
    
    async def _test_file_structure(self) -> SafeTestResult:
        """Test that key directories and files exist."""
        start_time = time.time()
        
        try:
            import os
            
            # Check key directories
            dirs_to_check = [
                "src",
                "src/services",
                "src/custom_types",
                "src/routes",
                "tests"
            ]
            
            existing_dirs = []
            missing_dirs = []
            
            for dir_path in dirs_to_check:
                if os.path.exists(dir_path):
                    existing_dirs.append(dir_path)
                else:
                    missing_dirs.append(dir_path)
            
            duration = (time.time() - start_time) * 1000
            return SafeTestResult(
                test_name="File Structure Validation",
                success=len(missing_dirs) == 0,
                duration_ms=duration,
                message=f"✅ Found {len(existing_dirs)} directories, missing {len(missing_dirs)}",
                details={
                    "existing_directories": existing_dirs,
                    "missing_directories": missing_dirs
                }
            )
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return SafeTestResult(
                test_name="File Structure Validation",
                success=False,
                duration_ms=duration,
                message=f"❌ File structure validation failed: {str(e)}",
                details={"error": str(e)}
            )
    
    async def _test_data_structures(self) -> SafeTestResult:
        """Test basic data structure operations."""
        start_time = time.time()
        
        try:
            # Test dictionary operations
            test_dict = {"name": "test", "value": 123}
            assert test_dict["name"] == "test"
            assert test_dict.get("missing", "default") == "default"
            
            # Test list operations
            test_list = [1, 2, 3, 4, 5]
            assert len(test_list) == 5
            assert sum(test_list) == 5
            
            # Test JSON serialization
            json_str = json.dumps(test_dict)
            parsed_dict = json.loads(json_str)
            assert parsed_dict == test_dict
            
            duration = (time.time() - start_time) * 1000
            return SafeTestResult(
                test_name="Data Structure Validation",
                success=True,
                duration_ms=duration,
                message="✅ Data structure operations working correctly",
                details={
                    "operations_tested": ["dictionary_access", "list_operations", "json_serialization"]
                }
            )
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return SafeTestResult(
                test_name="Data Structure Validation",
                success=False,
                duration_ms=duration,
                message=f"❌ Data structure validation failed: {str(e)}",
                details={"error": str(e)}
            )
    
    def _print_summary(self, results: Dict[str, Any]):
        """Print test summary."""
        print(f"\n📊 Test Summary:")
        print(f"   Total Tests: {results['summary']['total_tests']}")
        print(f"   Passed: {results['summary']['passed_tests']}")
        print(f"   Failed: {results['summary']['failed_tests']}")
        print(f"   Duration: {results['summary']['total_duration_ms']:.2f}ms")
        
        print(f"\n📋 Detailed Results:")
        for result in results['test_results']:
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {result['test_name']}: {result['message']}")

async def main():
    """Main function to run safe tests."""
    runner = SafeTestRunner()
    results = await runner.run_safe_tests()
    return results

if __name__ == "__main__":
    asyncio.run(main()) 