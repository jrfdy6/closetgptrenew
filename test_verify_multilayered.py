#!/usr/bin/env python3
"""
Verify that the multi-layered scoring system is actually running
"""

import requests
import json

def test_multilayered_system():
    """Test to confirm multi-layered system is active"""
    
    url = "https://closetgptrenew-backend-production.up.railway.app/api/outfits/generate"
    
    headers = {
        "Authorization": "Bearer test",
        "Content-Type": "application/json"
    }
    
    wardrobe = [
        {
            "id": "shirt1",
            "name": "Coral Wrap Top",
            "type": "shirt",
            "color": "Coral",
            "style": ["classic"],
            "occasion": ["casual"],
            "season": ["spring", "summer", "fall", "winter"],
            "dominantColors": [{"name": "Coral", "hex": "#FF7F50"}],
            "matchingColors": [{"name": "Coral", "hex": "#FF7F50"}],
            "userId": "test-user"
        },
        {
            "id": "pants1",
            "name": "High Waist Straight Pants",
            "type": "pants",
            "color": "Black",
            "style": ["formal"],
            "occasion": ["business"],
            "season": ["spring", "summer", "fall", "winter"],
            "dominantColors": [{"name": "Black", "hex": "#000000"}],
            "matchingColors": [{"name": "Black", "hex": "#000000"}],
            "userId": "test-user"
        },
        {
            "id": "shoes1",
            "name": "Black Heels",
            "type": "shoes",
            "color": "Black",
            "style": ["formal"],
            "occasion": ["business"],
            "season": ["spring", "summer", "fall", "winter"],
            "dominantColors": [{"name": "Black", "hex": "#000000"}],
            "matchingColors": [{"name": "Black", "hex": "#000000"}],
            "userId": "test-user"
        }
    ]
    
    payload = {
        "occasion": "Business",
        "style": "Classic",
        "mood": "Professional",
        "weather": {"temperature": 70, "condition": "clear"},
        "wardrobe": wardrobe,
        "user_profile": {
            "bodyType": "Hourglass",
            "height": "5'4\" - 5'7\"",
            "weight": "120-150 lbs",
            "gender": "Female",
            "skinTone": "Warm"
        }
    }
    
    print("🔍 VERIFICATION TEST: Multi-Layered Scoring System")
    print("=" * 70)
    print("\n📝 What to check in Railway logs:")
    print("   If NEW system is running, you should see:")
    print("   ✅ '🔬 PHASE 1: Multi-Layered Analysis & Scoring'")
    print("   ✅ '🚀 Running 3 analyzers in parallel...'")
    print("   ✅ '👤 BODY TYPE ANALYZER: Scoring...'")
    print("   ✅ '🎭 STYLE PROFILE ANALYZER: Scoring...'")
    print("   ✅ '🎨 COLOR THEORY: Using skin tone...'")
    print("   ✅ '🌤️ WEATHER ANALYZER: Scoring...'")
    print("   ✅ '🧮 Calculating composite scores...'")
    print("   ✅ '🏆 Top 5 scored items:'")
    print("   ✅ '🎨 PHASE 2: Cohesive Composition with Scored Items'")
    print("   ✅ '🌡️ LAYERING ANALYSIS: Temperature=...'")
    print("   ✅ Strategy: 'multi_layered_cohesive_composition'")
    print("\n   If OLD system is running, you'll see:")
    print("   ❌ Strategy: 'cohesive_composition' (no multi-layered prefix)")
    print("   ❌ No analyzer logs")
    print("   ❌ No composite scoring logs")
    print("=" * 70)
    
    try:
        print(f"\n📡 Sending test request...")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            strategy = result.get('metadata', {}).get('generation_strategy', 'unknown')
            items = result.get('items', [])
            
            print(f"\n✅ Request successful!")
            print(f"📋 Strategy returned: '{strategy}'")
            print(f"📋 Items generated: {len(items)}")
            
            print(f"\n" + "=" * 70)
            print("🎯 VERDICT:")
            print("=" * 70)
            
            if strategy == "multi_layered_cohesive_composition":
                print("✅ ✅ ✅ NEW MULTI-LAYERED SYSTEM IS RUNNING! ✅ ✅ ✅")
                print("\n   The system is using:")
                print("   • Body Type Analyzer (body type, height, weight, gender)")
                print("   • Style Profile Analyzer (style + COLOR THEORY with skin tone)")
                print("   • Weather Analyzer (temperature, season, conditions)")
                print("   • Intelligent Layering (weather + occasion + minimalistic)")
                print("   • Composite Scoring (weighted: 30% body, 40% style, 30% weather)")
            elif strategy == "cohesive_composition":
                print("❌ ❌ ❌ OLD SYSTEM STILL RUNNING ❌ ❌ ❌")
                print("\n   The old system does NOT have:")
                print("   ❌ Multi-layered scoring analyzers")
                print("   ❌ Color theory matching with skin tone")
                print("   ❌ Comprehensive body type analysis (height, weight, gender)")
                print("   ❌ Intelligent layering logic")
                print("   ❌ Composite scoring system")
                print("\n   🚨 ACTION REQUIRED: Deploy the new code to Railway!")
            else:
                print(f"⚠️  UNKNOWN STRATEGY: '{strategy}'")
                print("   This is unexpected. Check Railway logs for details.")
            
            print("\n🔍 Check Railway logs NOW to see detailed analyzer output")
            print(f"   Timestamp: ~{__import__('time').strftime('%Y-%m-%d %H:%M:%S')}")
            
            return strategy
            
        else:
            print(f"\n❌ Request failed: HTTP {response.status_code}")
            try:
                error_detail = response.json()
                print(f"Error: {error_detail}")
            except:
                print(f"Raw: {response.text}")
            return None
            
    except Exception as e:
        print(f"\n💥 Exception: {e}")
        return None

if __name__ == "__main__":
    strategy = test_multilayered_system()
    
    print("\n" + "=" * 70)
    print("📝 NEXT STEPS:")
    print("=" * 70)
    
    if strategy == "cohesive_composition":
        print("1. The new multi-layered system code is written but NOT deployed")
        print("2. Railway needs to redeploy with the new code")
        print("3. Once deployed, run this test again to confirm")
        print("\n💡 The code changes are in:")
        print("   backend/src/services/robust_outfit_generation_service.py")
    elif strategy == "multi_layered_cohesive_composition":
        print("✅ System is fully operational!")
        print("   All edge cases and stress tests are using the new system")
    else:
        print("⚠️  Unexpected state - check Railway deployment status")

