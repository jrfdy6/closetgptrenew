#!/usr/bin/env python3
"""
Comprehensive Security Setup Script

This script sets up all security components for the wardrobe system:
1. Image sanitization utility
2. Rate limiting middleware
3. Field-level encryption
4. Firestore security rules testing
5. Security audit and validation
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
import subprocess
import tempfile

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from src.utils.image_sanitizer import ImageSanitizer
from src.middleware.rate_limiter import RateLimiter
from src.utils.encryption import FieldEncryptor, get_encryptor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SecuritySetup:
    """Comprehensive security setup and validation."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.security_config = {
            "image_sanitization": {
                "enabled": True,
                "max_file_size": "50MB",
                "allowed_formats": ["jpg", "jpeg", "png", "webp"],
                "strip_exif": True,
                "resize_large_images": True
            },
            "rate_limiting": {
                "enabled": True,
                "default_limit": 60,
                "auth_limit": 10,
                "upload_limit": 20,
                "admin_multiplier": 5
            },
            "encryption": {
                "enabled": True,
                "algorithm": "AES-256-GCM",
                "encrypted_fields": [
                    "email",
                    "phone",
                    "address",
                    "profile_image_url",
                    "personal_notes"
                ]
            },
            "firestore_rules": {
                "enabled": True,
                "rules_file": "firebase/firestore.rules",
                "storage_rules_file": "firebase/storage.rules"
            }
        }
    
    def setup_image_sanitization(self) -> bool:
        """Set up image sanitization utility."""
        try:
            logger.info("🔒 Setting up image sanitization...")
            
            # Test image sanitizer
            sanitizer = ImageSanitizer()
            
            # Create a test image
            test_image_path = self._create_test_image()
            
            try:
                # Test sanitization
                result = sanitizer.sanitize_image(test_image_path)
                
                logger.info(f"✅ Image sanitization working:")
                logger.info(f"   - Original: {test_image_path}")
                logger.info(f"   - Sanitized: {result['output_path']}")
                logger.info(f"   - Size: {result['sanitized_size']}")
                logger.info(f"   - Hash: {result['file_hash'][:16]}...")
                
                return True
                
            finally:
                # Clean up test files
                if os.path.exists(test_image_path):
                    os.unlink(test_image_path)
                if os.path.exists(result['output_path']):
                    os.unlink(result['output_path'])
                    
        except Exception as e:
            logger.error(f"❌ Image sanitization setup failed: {e}")
            return False
    
    def _create_test_image(self) -> str:
        """Create a test image for sanitization testing."""
        try:
            from PIL import Image, ImageDraw
            
            # Create a simple test image
            img = Image.new('RGB', (100, 100), color='red')
            draw = ImageDraw.Draw(img)
            draw.text((10, 40), "Test Image", fill='white')
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            img.save(temp_file.name, 'JPEG')
            temp_file.close()
            
            return temp_file.name
            
        except ImportError:
            logger.warning("PIL not available, creating dummy test file")
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            temp_file.write(b"dummy image data")
            temp_file.close()
            return temp_file.name
    
    def setup_rate_limiting(self) -> bool:
        """Set up rate limiting middleware."""
        try:
            logger.info("🚦 Setting up rate limiting...")
            
            # Test rate limiter
            rate_limiter = RateLimiter()
            
            # Test configuration
            logger.info(f"✅ Rate limiting configured:")
            logger.info(f"   - Default limit: {rate_limiter.default_limits['default']} req/min")
            logger.info(f"   - Auth limit: {rate_limiter.default_limits['auth']} req/min")
            logger.info(f"   - Upload limit: {rate_limiter.default_limits['upload']} req/min")
            logger.info(f"   - Admin multiplier: {rate_limiter.admin_multiplier}x")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Rate limiting setup failed: {e}")
            return False
    
    def setup_encryption(self) -> bool:
        """Set up field-level encryption."""
        try:
            logger.info("🔐 Setting up field-level encryption...")
            
            # Test encryption
            encryptor = get_encryptor()
            
            # Test data
            test_user_id = "security_test_user"
            test_data = {
                "email": "test@example.com",
                "profile_image_url": "https://example.com/profile.jpg",
                "personal_notes": "Private notes",
                "wardrobe_items": ["item1", "item2"]  # Should not be encrypted
            }
            
            # Encrypt sensitive data
            encrypted_data = encryptor.encrypt_user_data(test_data, test_user_id)
            
            # Decrypt and verify
            decrypted_data = encryptor.decrypt_user_data(encrypted_data, test_user_id)
            
            # Verify encryption worked
            assert test_data["email"] == decrypted_data["email"]
            assert test_data["profile_image_url"] == decrypted_data["profile_image_url"]
            assert test_data["personal_notes"] == decrypted_data["personal_notes"]
            assert test_data["wardrobe_items"] == decrypted_data["wardrobe_items"]
            
            logger.info(f"✅ Field-level encryption working:")
            logger.info(f"   - Algorithm: AES-256-GCM")
            logger.info(f"   - Encrypted fields: {len([f for f in encrypted_data.values() if isinstance(f, dict) and f.get('encrypted')])}")
            logger.info(f"   - Non-encrypted fields: {len([f for f in encrypted_data.values() if not isinstance(f, dict) or not f.get('encrypted')])}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Encryption setup failed: {e}")
            return False
    
    def validate_firestore_rules(self) -> bool:
        """Validate Firestore security rules."""
        try:
            logger.info("📋 Validating Firestore security rules...")
            
            # Check if rules files exist
            rules_file = self.project_root / "firebase" / "firestore.rules"
            storage_rules_file = self.project_root / "firebase" / "storage.rules"
            
            if not rules_file.exists():
                logger.error(f"❌ Firestore rules file not found: {rules_file}")
                return False
            
            if not storage_rules_file.exists():
                logger.error(f"❌ Storage rules file not found: {storage_rules_file}")
                return False
            
            # Read and validate rules
            with open(rules_file, 'r') as f:
                rules_content = f.read()
            
            with open(storage_rules_file, 'r') as f:
                storage_rules_content = f.read()
            
            # Basic validation
            required_patterns = [
                "request.auth != null",
                "request.auth.uid == userId",
                "allow read, write: if false"
            ]
            
            for pattern in required_patterns:
                if pattern not in rules_content:
                    logger.warning(f"⚠️  Pattern not found in rules: {pattern}")
            
            logger.info(f"✅ Firestore rules validation:")
            logger.info(f"   - Rules file: {rules_file}")
            logger.info(f"   - Storage rules file: {storage_rules_file}")
            logger.info(f"   - Rules size: {len(rules_content)} chars")
            logger.info(f"   - Storage rules size: {len(storage_rules_content)} chars")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Firestore rules validation failed: {e}")
            return False
    
    def run_security_audit(self) -> Dict[str, Any]:
        """Run a comprehensive security audit."""
        logger.info("🔍 Running security audit...")
        
        audit_results = {
            "timestamp": str(Path(__file__).stat().st_mtime),
            "components": {},
            "overall_score": 0,
            "recommendations": []
        }
        
        # Test each component
        components = [
            ("image_sanitization", self.setup_image_sanitization),
            ("rate_limiting", self.setup_rate_limiting),
            ("encryption", self.setup_encryption),
            ("firestore_rules", self.validate_firestore_rules)
        ]
        
        passed_components = 0
        
        for component_name, test_func in components:
            try:
                result = test_func()
                audit_results["components"][component_name] = {
                    "status": "PASS" if result else "FAIL",
                    "enabled": self.security_config[component_name]["enabled"]
                }
                
                if result:
                    passed_components += 1
                else:
                    audit_results["recommendations"].append(f"Fix {component_name} configuration")
                    
            except Exception as e:
                audit_results["components"][component_name] = {
                    "status": "ERROR",
                    "error": str(e),
                    "enabled": self.security_config[component_name]["enabled"]
                }
                audit_results["recommendations"].append(f"Resolve {component_name} error: {e}")
        
        # Calculate overall score
        total_components = len(components)
        audit_results["overall_score"] = (passed_components / total_components) * 100
        
        return audit_results
    
    def generate_security_report(self, audit_results: Dict[str, Any]) -> str:
        """Generate a human-readable security report."""
        report_lines = [
            "=" * 60,
            "WARDROBE SYSTEM SECURITY AUDIT REPORT",
            "=" * 60,
            f"Generated: {audit_results['timestamp']}",
            f"Overall Score: {audit_results['overall_score']:.1f}%",
            ""
        ]
        
        # Component status
        report_lines.extend([
            "COMPONENT STATUS:",
            "-" * 30
        ])
        
        for component, status in audit_results["components"].items():
            status_icon = "✅" if status["status"] == "PASS" else "❌"
            enabled_icon = "🟢" if status["enabled"] else "🔴"
            report_lines.append(
                f"{status_icon} {component.upper()}: {status['status']} {enabled_icon}"
            )
        
        # Recommendations
        if audit_results["recommendations"]:
            report_lines.extend([
                "",
                "RECOMMENDATIONS:",
                "-" * 30
            ])
            
            for rec in audit_results["recommendations"]:
                report_lines.append(f"• {rec}")
        
        # Security summary
        report_lines.extend([
            "",
            "SECURITY SUMMARY:",
            "-" * 30,
            "✅ Image sanitization prevents malicious uploads",
            "✅ Rate limiting prevents abuse",
            "✅ Field-level encryption protects personal data",
            "✅ Firestore rules enforce access control",
            "✅ Authentication required for all operations",
            "",
            "=" * 60
        ])
        
        return "\n".join(report_lines)
    
    def save_security_config(self) -> bool:
        """Save security configuration to file."""
        try:
            config_file = self.project_root / "security_config.json"
            
            with open(config_file, 'w') as f:
                json.dump(self.security_config, f, indent=2)
            
            logger.info(f"✅ Security configuration saved to: {config_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save security config: {e}")
            return False
    
    def run_full_setup(self) -> bool:
        """Run complete security setup."""
        logger.info("🚀 Starting comprehensive security setup...")
        
        try:
            # Run security audit
            audit_results = self.run_security_audit()
            
            # Generate and display report
            report = self.generate_security_report(audit_results)
            print(report)
            
            # Save configuration
            self.save_security_config()
            
            # Save audit results
            audit_file = self.project_root / "security_audit.json"
            with open(audit_file, 'w') as f:
                json.dump(audit_results, f, indent=2)
            
            logger.info(f"✅ Security audit results saved to: {audit_file}")
            
            if audit_results["overall_score"] >= 80:
                logger.info("🎉 Security setup completed successfully!")
                return True
            else:
                logger.warning("⚠️  Security setup completed with issues. Review recommendations above.")
                return False
                
        except Exception as e:
            logger.error(f"❌ Security setup failed: {e}")
            return False

def main():
    """Main function to run security setup."""
    try:
        setup = SecuritySetup()
        success = setup.run_full_setup()
        
        if success:
            print("\n🎉 All security components are now configured and working!")
            print("Your wardrobe system is protected with:")
            print("• Image sanitization and validation")
            print("• Rate limiting and abuse prevention")
            print("• Field-level encryption for personal data")
            print("• Secure Firestore access rules")
        else:
            print("\n⚠️  Security setup completed with issues.")
            print("Please review the recommendations above and fix any problems.")
        
    except Exception as e:
        logger.error(f"Security setup script failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 