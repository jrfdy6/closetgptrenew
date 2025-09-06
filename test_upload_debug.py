#!/usr/bin/env python3
"""
Debug script for upload endpoint issues
"""
import requests
import base64
import io
from PIL import Image

def test_image_processing():
    """Test image processing locally"""
    print("🧪 Testing Image Processing Locally")
    print("=" * 50)
    
    # Create a test image
    test_image_data = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==")
    
    try:
        # Test PIL processing
        image = Image.open(io.BytesIO(test_image_data))
        print(f"✅ PIL can open image: {image.size}, {image.mode}")
        
        # Test HEIF support
        try:
            from pillow_heif import register_heif_opener
            register_heif_opener()
            print("✅ HEIF support available")
        except ImportError:
            print("⚠️  HEIF support not available")
            
    except Exception as e:
        print(f"❌ Image processing failed: {e}")

def test_upload_with_different_formats():
    """Test upload with different image formats"""
    print("\n🧪 Testing Upload with Different Formats")
    print("=" * 50)
    
    BACKEND_URL = "https://closetgptrenew-backend-production.up.railway.app"
    
    # Test 1: Very simple PNG
    print("📸 Test 1: Simple PNG")
    test_image_data = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==")
    
    try:
        files = {'file': ('test.png', test_image_data, 'image/png')}
        data = {'category': 'clothing', 'name': 'test-simple'}
        
        response = requests.post(f"{BACKEND_URL}/api/image/upload", files=files, data=data, timeout=30)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: JPEG
    print("\n📸 Test 2: JPEG")
    try:
        # Create a simple JPEG
        img = Image.new('RGB', (10, 10), color='red')
        jpeg_buffer = io.BytesIO()
        img.save(jpeg_buffer, format='JPEG')
        jpeg_data = jpeg_buffer.getvalue()
        
        files = {'file': ('test.jpg', jpeg_data, 'image/jpeg')}
        data = {'category': 'clothing', 'name': 'test-jpeg'}
        
        response = requests.post(f"{BACKEND_URL}/api/image/upload", files=files, data=data, timeout=30)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_image_processing()
    test_upload_with_different_formats()
