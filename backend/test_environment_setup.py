#!/usr/bin/env python3
"""
Test Environment Setup Script

This script safely configures the environment for running comprehensive tests
without affecting production data or services.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess
import sys

class TestEnvironmentSetup:
    """Manages test environment setup and teardown."""
    
    def __init__(self):
        self.test_config = {
            'test_mode': True,
            'use_mock_services': True,
            'test_database': 'test_closetgpt',
            'test_storage': 'test_storage',
            'backup_existing': True,
            'cleanup_after_tests': True
        }
        
        self.backup_paths = []
        self.test_data_path = Path("test_data")
        self.config_backup_path = Path("config_backup")
        
    def setup_test_environment(self) -> Dict[str, Any]:
        """Set up the test environment safely."""
        print("🔧 Setting up Test Environment")
        print("=" * 50)
        
        results = {
            'success': True,
            'steps_completed': [],
            'warnings': [],
            'errors': []
        }
        
        try:
            # Step 1: Create test directories
            self._create_test_directories(results)
            
            # Step 2: Backup existing configs
            self._backup_existing_configs(results)
            
            # Step 3: Set up test configuration
            self._setup_test_configuration(results)
            
            # Step 4: Validate environment variables
            self._validate_environment_variables(results)
            
            # Step 5: Create test data
            self._create_test_data(results)
            
            # Step 6: Set up mock services
            self._setup_mock_services(results)
            
            print(f"\n✅ Test environment setup completed!")
            print(f"   Steps completed: {len(results['steps_completed'])}")
            print(f"   Warnings: {len(results['warnings'])}")
            print(f"   Errors: {len(results['errors'])}")
            
        except Exception as e:
            results['success'] = False
            results['errors'].append(f"Setup failed: {str(e)}")
            print(f"\n❌ Test environment setup failed: {str(e)}")
        
        return results
    
    def _create_test_directories(self, results: Dict[str, Any]):
        """Create necessary test directories."""
        try:
            directories = [
                self.test_data_path,
                self.config_backup_path,
                Path("test_logs"),
                Path("test_output"),
                Path("test_cache")
            ]
            
            for directory in directories:
                directory.mkdir(exist_ok=True)
                print(f"   📁 Created directory: {directory}")
            
            results['steps_completed'].append("Created test directories")
            
        except Exception as e:
            results['errors'].append(f"Failed to create directories: {str(e)}")
    
    def _backup_existing_configs(self, results: Dict[str, Any]):
        """Backup existing configuration files."""
        try:
            config_files = [
                "config.py",
                "src/core/config.py",
                ".env",
                "firebase/firestore.rules"
            ]
            
            for config_file in config_files:
                if Path(config_file).exists():
                    backup_path = self.config_backup_path / f"{config_file}.backup"
                    shutil.copy2(config_file, backup_path)
                    self.backup_paths.append(backup_path)
                    print(f"   💾 Backed up: {config_file}")
            
            results['steps_completed'].append("Backed up existing configurations")
            
        except Exception as e:
            results['warnings'].append(f"Backup warning: {str(e)}")
    
    def _setup_test_configuration(self, results: Dict[str, Any]):
        """Set up test-specific configuration."""
        try:
            # Create test environment file
            test_env_content = f"""
# Test Environment Configuration
TEST_MODE=true
USE_MOCK_SERVICES=true
TEST_DATABASE={self.test_config['test_database']}
TEST_STORAGE={self.test_config['test_storage']}

# Mock API keys for testing
OPENAI_API_KEY=sk-test-mock-key-for-testing-only
FIREBASE_PROJECT_ID=test-project-id
FIREBASE_PRIVATE_KEY_ID=test-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\\nMOCK_KEY_FOR_TESTING\\n-----END PRIVATE KEY-----"

# Test-specific settings
LOG_LEVEL=DEBUG
ENABLE_ANALYTICS=false
ENABLE_CACHING=false
"""
            
            with open(".env.test", "w") as f:
                f.write(test_env_content.strip())
            
            print(f"   ⚙️  Created test environment file: .env.test")
            results['steps_completed'].append("Created test configuration")
            
        except Exception as e:
            results['errors'].append(f"Failed to create test config: {str(e)}")
    
    def _validate_environment_variables(self, results: Dict[str, Any]):
        """Validate that required environment variables are set for testing."""
        try:
            required_vars = [
                "OPENAI_API_KEY",
                "FIREBASE_PROJECT_ID"
            ]
            
            missing_vars = []
            for var in required_vars:
                if not os.getenv(var):
                    missing_vars.append(var)
            
            if missing_vars:
                results['warnings'].append(f"Missing environment variables: {missing_vars}")
                print(f"   ⚠️  Warning: Missing env vars: {missing_vars}")
            else:
                print(f"   ✅ Environment variables validated")
            
            results['steps_completed'].append("Validated environment variables")
            
        except Exception as e:
            results['errors'].append(f"Environment validation failed: {str(e)}")
    
    def _create_test_data(self, results: Dict[str, Any]):
        """Create test data for the comprehensive test suite."""
        try:
            # Create test wardrobe data
            test_wardrobe = {
                "items": [
                    {
                        "id": "test-shirt-1",
                        "name": "Test Blue Shirt",
                        "type": "shirt",
                        "color": "blue",
                        "season": ["spring", "summer"],
                        "style": ["casual", "business"],
                        "tags": ["cotton", "comfortable"]
                    },
                    {
                        "id": "test-pants-1", 
                        "name": "Test Black Pants",
                        "type": "pants",
                        "color": "black",
                        "season": ["all"],
                        "style": ["business", "formal"],
                        "tags": ["wool", "professional"]
                    }
                ]
            }
            
            with open(self.test_data_path / "test_wardrobe.json", "w") as f:
                json.dump(test_wardrobe, f, indent=2)
            
            # Create test user profile
            test_profile = {
                "user_id": "test-user-123",
                "style_preferences": ["business", "casual"],
                "color_preferences": ["blue", "black", "white"],
                "body_type": "athletic",
                "budget_range": "medium"
            }
            
            with open(self.test_data_path / "test_profile.json", "w") as f:
                json.dump(test_profile, f, indent=2)
            
            print(f"   📊 Created test data files")
            results['steps_completed'].append("Created test data")
            
        except Exception as e:
            results['errors'].append(f"Failed to create test data: {str(e)}")
    
    def _setup_mock_services(self, results: Dict[str, Any]):
        """Set up mock services for testing."""
        try:
            # Create mock service configuration
            mock_config = {
                "services": {
                    "outfit_service": {
                        "mock_mode": True,
                        "response_delay_ms": 100
                    },
                    "analytics_service": {
                        "mock_mode": True,
                        "log_to_file": True
                    },
                    "weather_service": {
                        "mock_mode": True,
                        "default_weather": "sunny"
                    }
                }
            }
            
            with open(self.test_data_path / "mock_services.json", "w") as f:
                json.dump(mock_config, f, indent=2)
            
            print(f"   🎭 Created mock service configuration")
            results['steps_completed'].append("Set up mock services")
            
        except Exception as e:
            results['errors'].append(f"Failed to set up mock services: {str(e)}")
    
    def teardown_test_environment(self) -> Dict[str, Any]:
        """Clean up test environment and restore original configs."""
        print("\n🧹 Cleaning up Test Environment")
        print("=" * 50)
        
        results = {
            'success': True,
            'steps_completed': [],
            'warnings': [],
            'errors': []
        }
        
        try:
            # Restore original configurations
            self._restore_configurations(results)
            
            # Clean up test files
            self._cleanup_test_files(results)
            
            # Remove test directories (optional)
            if self.test_config['cleanup_after_tests']:
                self._remove_test_directories(results)
            
            print(f"\n✅ Test environment cleanup completed!")
            print(f"   Steps completed: {len(results['steps_completed'])}")
            
        except Exception as e:
            results['success'] = False
            results['errors'].append(f"Cleanup failed: {str(e)}")
            print(f"\n❌ Test environment cleanup failed: {str(e)}")
        
        return results
    
    def _restore_configurations(self, results: Dict[str, Any]):
        """Restore original configuration files from backup."""
        try:
            for backup_path in self.backup_paths:
                if backup_path.exists():
                    original_path = backup_path.parent / backup_path.stem
                    shutil.copy2(backup_path, original_path)
                    print(f"   🔄 Restored: {original_path}")
            
            # Remove test environment file
            if Path(".env.test").exists():
                Path(".env.test").unlink()
                print(f"   🗑️  Removed: .env.test")
            
            results['steps_completed'].append("Restored original configurations")
            
        except Exception as e:
            results['warnings'].append(f"Restore warning: {str(e)}")
    
    def _cleanup_test_files(self, results: Dict[str, Any]):
        """Clean up test-generated files."""
        try:
            test_files = [
                "test_logs",
                "test_output", 
                "test_cache"
            ]
            
            for file_path in test_files:
                if Path(file_path).exists():
                    if Path(file_path).is_dir():
                        shutil.rmtree(file_path)
                    else:
                        Path(file_path).unlink()
                    print(f"   🗑️  Cleaned up: {file_path}")
            
            results['steps_completed'].append("Cleaned up test files")
            
        except Exception as e:
            results['warnings'].append(f"Cleanup warning: {str(e)}")
    
    def _remove_test_directories(self, results: Dict[str, Any]):
        """Remove test directories."""
        try:
            directories = [
                self.test_data_path,
                self.config_backup_path
            ]
            
            for directory in directories:
                if directory.exists():
                    shutil.rmtree(directory)
                    print(f"   🗑️  Removed directory: {directory}")
            
            results['steps_completed'].append("Removed test directories")
            
        except Exception as e:
            results['warnings'].append(f"Directory removal warning: {str(e)}")

def main():
    """Main function to run test environment setup."""
    setup = TestEnvironmentSetup()
    
    # Set up test environment
    setup_results = setup.setup_test_environment()
    
    if setup_results['success']:
        print(f"\n🎯 Test environment is ready!")
        print(f"   You can now run your comprehensive test suite safely.")
        print(f"   Use: python tests/comprehensive_outfit_testing_framework.py")
        
        # Ask if user wants to run tests now
        response = input(f"\n🤔 Would you like to run the comprehensive tests now? (y/n): ")
        if response.lower() in ['y', 'yes']:
            print(f"\n🚀 Running comprehensive tests...")
            try:
                # Import and run the test framework
                from tests.comprehensive_outfit_testing_framework import ComprehensiveOutfitTestingFramework
                import asyncio
                
                async def run_tests():
                    framework = ComprehensiveOutfitTestingFramework()
                    return await framework.run_comprehensive_tests()
                
                test_results = asyncio.run(run_tests())
                print(f"\n✅ Tests completed!")
                
            except Exception as e:
                print(f"\n❌ Test execution failed: {str(e)}")
        
        # Clean up
        response = input(f"\n🧹 Would you like to clean up the test environment? (y/n): ")
        if response.lower() in ['y', 'yes']:
            cleanup_results = setup.teardown_test_environment()
            if cleanup_results['success']:
                print(f"\n✅ Environment cleaned up successfully!")
            else:
                print(f"\n⚠️  Cleanup had some issues: {cleanup_results['warnings']}")
    else:
        print(f"\n❌ Test environment setup failed!")
        print(f"   Errors: {setup_results['errors']}")

if __name__ == "__main__":
    main() 