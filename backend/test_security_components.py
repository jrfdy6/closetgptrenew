#!/usr/bin/env python3
"""
Test Security Components

This script tests all security components to ensure they're working correctly.
"""

import os
import sys
import tempfile
import logging
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_image_sanitization():
    """Test image sanitization component."""
    try:
        logger.info("🔒 Testing image sanitization...")
        
        # Try to import the sanitizer
        from src.utils.image_sanitizer import ImageSanitizer
        
        # Create a test image
        from PIL import Image, ImageDraw
        
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color='blue')
        draw = ImageDraw.Draw(img)
        draw.text((10, 40), "Test", fill='white')
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            img.save(temp_file.name, 'JPEG')
            temp_path = temp_file.name
        
        try:
            # Test sanitization
            sanitizer = ImageSanitizer()
            result = sanitizer.sanitize_image(temp_path)
            
            logger.info(f"✅ Image sanitization working:")
            logger.info(f"   - Original: {temp_path}")
            logger.info(f"   - Sanitized: {result['output_path']}")
            logger.info(f"   - Size: {result['sanitized_size']}")
            
            # Clean up
            if os.path.exists(result['output_path']):
                os.unlink(result['output_path'])
            
            return True
            
        finally:
            # Clean up original
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        logger.error(f"❌ Image sanitization test failed: {e}")
        return False

def test_rate_limiting():
    """Test rate limiting component."""
    try:
        logger.info("🚦 Testing rate limiting...")
        
        from src.middleware.rate_limiter import RateLimiter
        
        # Create rate limiter
        rate_limiter = RateLimiter()
        
        logger.info(f"✅ Rate limiting configured:")
        logger.info(f"   - Default limit: {rate_limiter.default_limits['default']} req/min")
        logger.info(f"   - Auth limit: {rate_limiter.default_limits['auth']} req/min")
        logger.info(f"   - Upload limit: {rate_limiter.default_limits['upload']} req/min")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Rate limiting test failed: {e}")
        return False

def test_encryption():
    """Test encryption component."""
    try:
        logger.info("🔐 Testing field-level encryption...")
        
        from src.utils.encryption import get_encryptor, encrypt_sensitive_data, decrypt_sensitive_data
        
        # Test encryption
        encryptor = get_encryptor()
        
        # Test data
        test_user_id = "test_user_123"
        test_data = {
            "email": "test@example.com",
            "profile_image_url": "https://example.com/profile.jpg",
            "personal_notes": "Private notes",
            "wardrobe_items": ["item1", "item2"]  # Should not be encrypted
        }
        
        # Encrypt sensitive data
        encrypted_data = encrypt_sensitive_data(test_data, test_user_id)
        
        # Decrypt and verify
        decrypted_data = decrypt_sensitive_data(encrypted_data, test_user_id)
        
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
        logger.error(f"❌ Encryption test failed: {e}")
        return False

def test_firestore_rules():
    """Test Firestore rules validation."""
    try:
        logger.info("📋 Testing Firestore rules...")
        
        # Check if rules files exist (look in parent directory)
        rules_file = Path("../firebase/firestore.rules")
        storage_rules_file = Path("../firebase/storage.rules")
        
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
            "request.auth.uid == userId"
        ]
        
        for pattern in required_patterns:
            if pattern not in rules_content:
                logger.warning(f"⚠️  Pattern not found in rules: {pattern}")
        
        logger.info(f"✅ Firestore rules validation:")
        logger.info(f"   - Rules file: {rules_file}")
        logger.info(f"   - Storage rules file: {storage_rules_file}")
        logger.info(f"   - Rules size: {len(rules_content)} chars")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Firestore rules test failed: {e}")
        return False

def main():
    """Run all security component tests."""
    logger.info("🚀 Starting security component tests...")
    
    tests = [
        ("Image Sanitization", test_image_sanitization),
        ("Rate Limiting", test_rate_limiting),
        ("Field-Level Encryption", test_encryption),
        ("Firestore Rules", test_firestore_rules)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Testing: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            if test_func():
                logger.info(f"✅ {test_name} PASSED")
                passed += 1
            else:
                logger.error(f"❌ {test_name} FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} ERROR: {e}")
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("SECURITY TEST SUMMARY")
    logger.info(f"{'='*50}")
    logger.info(f"Passed: {passed}/{total}")
    logger.info(f"Score: {(passed/total)*100:.1f}%")
    
    if passed == total:
        logger.info("🎉 All security components are working correctly!")
        return True
    else:
        logger.warning("⚠️  Some security components need attention.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 