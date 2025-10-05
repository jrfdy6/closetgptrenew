#!/usr/bin/env python3
"""
Test the new metadata-first filtering approach
"""

import requests
import json
import time

def test_metadata_filtering():
    """Test the new metadata-first filtering approach"""
    
    print("🧪 TESTING METADATA-FIRST FILTERING APPROACH")
    print("=" * 70)
    print()
    
    # Test wardrobe items with rich metadata
    test_wardrobe = [
        {
            "id": "test_athletic_shirt",
            "name": "Blue Cotton Shirt",
            "type": "shirt",
            "color": "Blue",
            "brand": "Nike",
            "occasion": ["athletic", "casual"],
            "style": ["athletic", "sporty"],
            "season": ["spring", "summer"],
            "imageUrl": "https://example.com/shirt.jpg",
            "userId": "test_user"
        },
        {
            "id": "test_business_shirt", 
            "name": "White Button-Down Shirt",
            "type": "shirt",
            "color": "White",
            "brand": "Brooks Brothers",
            "occasion": ["business", "formal"],
            "style": ["formal", "professional"],
            "season": ["spring", "summer", "fall", "winter"],
            "imageUrl": "https://example.com/business_shirt.jpg",
            "userId": "test_user"
        },
        {
            "id": "test_casual_shirt",
            "name": "Red T-Shirt",
            "type": "shirt", 
            "color": "Red",
            "brand": "Gap",
            "occasion": ["casual"],
            "style": ["casual", "relaxed"],
            "season": ["spring", "summer"],
            "imageUrl": "https://example.com/tshirt.jpg",
            "userId": "test_user"
        },
        {
            "id": "test_athletic_pants",
            "name": "Black Athletic Pants",
            "type": "pants",
            "color": "Black",
            "brand": "Adidas",
            "occasion": ["athletic", "gym"],
            "style": ["athletic", "sporty"],
            "season": ["spring", "fall", "winter"],
            "imageUrl": "https://example.com/athletic_pants.jpg",
            "userId": "test_user"
        },
        {
            "id": "test_business_pants",
            "name": "Gray Dress Pants",
            "type": "pants",
            "color": "Gray",
            "brand": "Hugo Boss",
            "occasion": ["business", "formal"],
            "style": ["formal", "professional"],
            "season": ["spring", "fall", "winter"],
            "imageUrl": "https://example.com/dress_pants.jpg",
            "userId": "test_user"
        },
        {
            "id": "test_athletic_shoes",
            "name": "White Running Shoes",
            "type": "sneakers",
            "color": "White",
            "brand": "Nike",
            "occasion": ["athletic", "casual"],
            "style": ["athletic", "sporty"],
            "season": ["spring", "summer", "fall", "winter"],
            "imageUrl": "https://example.com/sneakers.jpg",
            "userId": "test_user"
        },
        {
            "id": "test_business_shoes",
            "name": "Brown Oxford Shoes",
            "type": "shoes",
            "color": "Brown",
            "brand": "Allen Edmonds",
            "occasion": ["business", "formal"],
            "style": ["formal", "professional"],
            "season": ["spring", "fall", "winter"],
            "imageUrl": "https://example.com/oxford.jpg",
            "userId": "test_user"
        }
    ]
    
    # Test cases
    test_cases = [
        {
            "name": "Athletic Occasion Test",
            "occasion": "athletic",
            "style": "athletic",
            "mood": "energetic",
            "expected_items": ["Blue Cotton Shirt", "Black Athletic Pants", "White Running Shoes"],
            "description": "Should use occasion=['athletic'] and brand='Nike/Adidas' as primary filters"
        },
        {
            "name": "Business Occasion Test", 
            "occasion": "business",
            "style": "formal",
            "mood": "professional",
            "expected_items": ["White Button-Down Shirt", "Gray Dress Pants", "Brown Oxford Shoes"],
            "description": "Should use occasion=['business'] and brand='Brooks Brothers/Hugo Boss' as primary filters"
        },
        {
            "name": "Casual Occasion Test",
            "occasion": "casual", 
            "style": "casual",
            "mood": "relaxed",
            "expected_items": ["Red T-Shirt", "Blue Cotton Shirt", "White Running Shoes"],
            "description": "Should use occasion=['casual'] as primary filter"
        }
    ]
    
    base_url = "https://closetgptrenew-backend-production.up.railway.app"
    
    print("🎯 TEST CASES:")
    print("-" * 50)
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['name']}")
        print(f"   Occasion: {test_case['occasion']}")
        print(f"   Expected Items: {', '.join(test_case['expected_items'])}")
        print(f"   Description: {test_case['description']}")
        print()
    
    print("🚀 RUNNING TESTS...")
    print("-" * 50)
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 TEST {i}: {test_case['name']}")
        print("=" * 50)
        
        # Prepare request
        request_data = {
            "occasion": test_case["occasion"],
            "style": test_case["style"], 
            "mood": test_case["mood"],
            "wardrobe": test_wardrobe,
            "weather": {
                "temperature": 72,
                "condition": "clear",
                "humidity": 50
            },
            "userProfile": {
                "id": "test_user",
                "bodyType": "Average",
                "height": "Average",
                "weight": "Average",
                "stylePreferences": {
                    "favoriteColors": ["blue", "black", "white"],
                    "preferredBrands": ["Nike", "Adidas", "Brooks Brothers"]
                }
            }
        }
        
        try:
            print(f"📤 Request: {test_case['occasion']} + {test_case['style']} + {test_case['mood']}")
            print(f"📦 Wardrobe: {len(test_wardrobe)} items with rich metadata")
            
            # Make API call
            response = requests.post(
                f"{base_url}/api/outfits/generate",
                json=request_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer test"
                },
                timeout=30
            )
            
            print(f"📥 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if "items" in data and data["items"]:
                    generated_items = [item.get("name", "Unknown") for item in data["items"]]
                    print(f"✅ SUCCESS: Generated {len(data['items'])} items")
                    print(f"🎯 Generated Items: {', '.join(generated_items)}")
                    print(f"📋 Expected Items: {', '.join(test_case['expected_items'])}")
                    
                    # Check if expected items were included
                    included_expected = [item for item in test_case['expected_items'] if item in generated_items]
                    print(f"✅ Expected Items Included: {len(included_expected)}/{len(test_case['expected_items'])}")
                    
                    if len(included_expected) >= 2:  # At least 2/3 expected items
                        print("🎉 TEST PASSED: Metadata-first filtering working!")
                        results.append({"test": test_case['name'], "status": "PASSED", "items": generated_items})
                    else:
                        print("⚠️ TEST PARTIAL: Some expected items missing")
                        results.append({"test": test_case['name'], "status": "PARTIAL", "items": generated_items})
                else:
                    print("❌ TEST FAILED: No items generated")
                    print(f"📄 Response: {data}")
                    results.append({"test": test_case['name'], "status": "FAILED", "items": []})
            else:
                print(f"❌ TEST FAILED: HTTP {response.status_code}")
                print(f"📄 Response: {response.text}")
                results.append({"test": test_case['name'], "status": "FAILED", "items": []})
                
        except Exception as e:
            print(f"❌ TEST ERROR: {e}")
            results.append({"test": test_case['name'], "status": "ERROR", "items": []})
        
        print(f"⏱️ Waiting 2 seconds before next test...")
        time.sleep(2)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for r in results if r["status"] == "PASSED")
    partial = sum(1 for r in results if r["status"] == "PARTIAL")
    failed = sum(1 for r in results if r["status"] in ["FAILED", "ERROR"])
    
    print(f"✅ PASSED: {passed}/{len(results)} tests")
    print(f"⚠️ PARTIAL: {partial}/{len(results)} tests")
    print(f"❌ FAILED: {failed}/{len(results)} tests")
    print()
    
    for result in results:
        status_emoji = {"PASSED": "✅", "PARTIAL": "⚠️", "FAILED": "❌", "ERROR": "❌"}
        print(f"{status_emoji[result['status']]} {result['test']}: {result['status']}")
        if result['items']:
            print(f"   Generated: {', '.join(result['items'])}")
    
    print()
    if passed >= 2:
        print("🎉 METADATA-FIRST FILTERING IS WORKING!")
        print("✅ The new approach is successfully using metadata as primary filters")
        print("✅ Items are no longer rejected based on arbitrary name patterns")
    elif partial >= 2:
        print("⚠️ METADATA-FIRST FILTERING IS PARTIALLY WORKING")
        print("✅ Some improvements seen, but may need fine-tuning")
    else:
        print("❌ METADATA-FIRST FILTERING NEEDS MORE WORK")
        print("🔧 May need to debug the filtering logic further")
    
    print(f"\n📝 Test completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_metadata_filtering()

