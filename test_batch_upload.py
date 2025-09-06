#!/usr/bin/env python3
"""
Test script for batch upload functionality
"""
import requests
import json
import time

# Configuration
BACKEND_URL = "https://closetgptrenew-backend-production.up.railway.app"
TEST_IMAGES = [
    "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400&h=600&fit=crop",
    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=600&fit=crop",
    "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400&h=600&fit=crop"
]

def test_analysis_endpoint():
    """Test the analysis endpoint with real images"""
    print("🧪 Testing Image Analysis Endpoint")
    print("=" * 50)
    
    for i, image_url in enumerate(TEST_IMAGES, 1):
        print(f"\n📸 Testing Image {i}: {image_url[:50]}...")
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/analyze-image",
                headers={"Content-Type": "application/json"},
                json={"url": image_url},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                analysis = data.get("analysis", {})
                
                print(f"✅ Analysis successful!")
                print(f"   Type: {analysis.get('type', 'unknown')}")
                print(f"   Style: {analysis.get('style', 'unknown')}")
                print(f"   Material: {analysis.get('material', 'unknown')}")
                print(f"   Method: {analysis.get('analysisMethod', 'unknown')}")
                print(f"   Confidence: {analysis.get('confidence', 0)}")
                
                if analysis.get('analysisMethod') == 'fallback':
                    print(f"⚠️  Using fallback analysis - AI may have failed")
                    if 'error' in analysis:
                        print(f"   Error: {analysis['error']}")
                
            else:
                print(f"❌ Analysis failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        time.sleep(2)  # Rate limiting

def test_upload_endpoint():
    """Test the upload endpoint with a small image"""
    print("\n🧪 Testing Image Upload Endpoint")
    print("=" * 50)
    
    # Create a small test image
    import base64
    test_image_data = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==")
    
    try:
        files = {
            'file': ('test.png', test_image_data, 'image/png')
        }
        data = {
            'category': 'clothing',
            'name': 'test-upload'
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/image/upload",
            files=files,
            data=data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Upload successful!")
            print(f"   URL: {data.get('url', 'unknown')}")
            print(f"   Size: {data.get('size', 0)} bytes")
            print(f"   Fallback: {data.get('fallback', False)}")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Upload request failed: {e}")

def test_full_batch_flow():
    """Test the full batch upload flow"""
    print("\n🧪 Testing Full Batch Upload Flow")
    print("=" * 50)
    
    # Simulate the frontend batch upload process
    for i, image_url in enumerate(TEST_IMAGES, 1):
        print(f"\n📦 Processing Item {i}/{len(TEST_IMAGES)}")
        
        # Step 1: Upload image (simulate with public URL)
        print(f"   1️⃣ Using public URL: {image_url[:50]}...")
        
        # Step 2: Analyze image
        print(f"   2️⃣ Analyzing image...")
        try:
            response = requests.post(
                f"{BACKEND_URL}/analyze-image",
                headers={"Content-Type": "application/json"},
                json={"url": image_url},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                analysis = data.get("analysis", {})
                
                print(f"   ✅ Analysis complete!")
                print(f"      Type: {analysis.get('type', 'unknown')}")
                print(f"      Style: {analysis.get('style', 'unknown')}")
                print(f"      Material: {analysis.get('material', 'unknown')}")
                print(f"      Colors: {[c.get('name', 'unknown') for c in analysis.get('dominantColors', [])]}")
                
                # Step 3: Simulate saving to wardrobe
                print(f"   3️⃣ Would save to wardrobe with AI analysis")
                
            else:
                print(f"   ❌ Analysis failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Analysis request failed: {e}")
        
        time.sleep(2)

if __name__ == "__main__":
    print("🚀 Starting Batch Upload Test Suite")
    print("=" * 60)
    
    # Test individual endpoints
    test_analysis_endpoint()
    test_upload_endpoint()
    
    # Test full flow
    test_full_batch_flow()
    
    print("\n🎉 Test suite completed!")
