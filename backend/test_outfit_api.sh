#!/bin/bash

# Test script for outfit generation and retrieval
# This script fetches wardrobe items and tests the complete flow

BASE_URL="http://localhost:3001"
USER_ID="dANqjiI0CKgaitxzYtw1bhtvQrG3"

echo "🚀 Starting outfit generation and retrieval test"
echo "============================================================"

# Step 1: Try to fetch wardrobe items (if endpoint exists)
echo "🔍 Attempting to fetch wardrobe items..."
WARDROBE_RESPONSE=$(curl -s -X GET "$BASE_URL/api/wardrobe?userId=$USER_ID" 2>/dev/null)

if [ $? -eq 0 ] && [ "$WARDROBE_RESPONSE" != "" ]; then
    echo "✅ Found wardrobe endpoint, using real data"
    WARDROBE_DATA="$WARDROBE_RESPONSE"
else
    echo "⚠️  No wardrobe endpoint found, using sample data"
    # Create sample wardrobe items
    WARDROBE_DATA='[
        {
            "id": "sample-shirt-1",
            "name": "Blue Casual Shirt",
            "type": "shirt",
            "color": "blue",
            "season": ["spring", "summer"],
            "style": ["casual"],
            "occasion": ["casual"],
            "imageUrl": "https://example.com/shirt1.jpg",
            "tags": [],
            "dominantColors": [],
            "matchingColors": [],
            "createdAt": 1750531295,
            "updatedAt": 1750531295,
            "userId": "'$USER_ID'",
            "metadata": {}
        },
        {
            "id": "sample-pants-1",
            "name": "Black Casual Pants",
            "type": "pants",
            "color": "black",
            "season": ["fall", "winter"],
            "style": ["classic"],
            "occasion": ["casual"],
            "imageUrl": "https://example.com/pants1.jpg",
            "tags": [],
            "dominantColors": [],
            "matchingColors": [],
            "createdAt": 1750531295,
            "updatedAt": 1750531295,
            "userId": "'$USER_ID'",
            "metadata": {}
        },
        {
            "id": "sample-shoes-1",
            "name": "White Sneakers",
            "type": "shoes",
            "color": "white",
            "season": ["spring", "summer", "fall"],
            "style": ["casual"],
            "occasion": ["casual"],
            "imageUrl": "https://example.com/shoes1.jpg",
            "tags": [],
            "dominantColors": [],
            "matchingColors": [],
            "createdAt": 1750531295,
            "updatedAt": 1750531295,
            "userId": "'$USER_ID'",
            "metadata": {}
        }
    ]'
fi

echo "📦 Using wardrobe items:"
echo "$WARDROBE_DATA" | jq -r '.[] | "  - \(.name) (\(.type))"'

# Step 2: Generate outfit
echo ""
echo "🎨 Generating outfit..."
echo "============================================================"

GENERATION_PAYLOAD='{
    "occasion": "Casual",
    "weather": {
        "temperature": 70.0,
        "condition": "sunny",
        "humidity": 50
    },
    "wardrobe": '"$WARDROBE_DATA"',
    "user_profile": {
        "id": "'$USER_ID'",
        "name": "Test User",
        "email": "test@example.com",
        "gender": "male",
        "bodyType": "athletic",
        "skinTone": "medium",
        "stylePreferences": ["casual", "classic"],
        "budget": "medium",
        "favoriteBrands": ["Nike", "Adidas"],
        "createdAt": 1750531295,
        "updatedAt": 1750531295
    },
    "likedOutfits": [],
    "trendingStyles": [],
    "style": "Casual",
    "mood": "relaxed"
}'

GENERATION_RESPONSE=$(curl -s -X POST "$BASE_URL/api/outfit/generate" \
    -H "Content-Type: application/json" \
    -d "$GENERATION_PAYLOAD")

if [ $? -eq 0 ]; then
    echo "✅ Outfit generation request sent successfully"
    
    # Extract outfit ID
    OUTFIT_ID=$(echo "$GENERATION_RESPONSE" | jq -r '.id // empty')
    
    if [ "$OUTFIT_ID" != "" ] && [ "$OUTFIT_ID" != "null" ]; then
        echo "📋 Generated outfit details:"
        echo "$GENERATION_RESPONSE" | jq -r '
            "  ID: \(.id // "N/A")",
            "  Name: \(.name // "N/A")",
            "  Items count: \(.items | length)",
            "  Was successful: \(.wasSuccessful // "N/A")",
            "  Validation errors: \(.validationErrors // [])"
        '
        
        # Step 3: Test retrieval
        echo ""
        echo "🔍 Testing outfit retrieval..."
        echo "============================================================"
        
        # Wait a moment for the outfit to be saved
        sleep 2
        
        RETRIEVAL_RESPONSE=$(curl -s -X GET "$BASE_URL/api/outfit/$OUTFIT_ID")
        
        if [ $? -eq 0 ]; then
            if echo "$RETRIEVAL_RESPONSE" | jq -e '.id' >/dev/null 2>&1; then
                echo "✅ Outfit retrieved successfully!"
                echo "📋 Retrieved outfit details:"
                echo "$RETRIEVAL_RESPONSE" | jq -r '
                    "  ID: \(.id // "N/A")",
                    "  Name: \(.name // "N/A")",
                    "  Items count: \(.items | length)",
                    "  Was successful: \(.wasSuccessful // "N/A")"
                '
                
                echo ""
                echo "🎉 SUCCESS: Outfit generation and retrieval works!"
                echo "============================================================"
            else
                echo "❌ Outfit retrieval failed - outfit not found or invalid response"
                echo "Response: $RETRIEVAL_RESPONSE"
                echo ""
                echo "❌ FAILED: Outfit retrieval failed"
                echo "============================================================"
            fi
        else
            echo "❌ Error during outfit retrieval"
            echo ""
            echo "❌ FAILED: Outfit retrieval failed"
            echo "============================================================"
        fi
    else
        echo "❌ No outfit ID returned from generation"
        echo "Response: $GENERATION_RESPONSE"
        echo ""
        echo "❌ FAILED: Outfit generation failed"
        echo "============================================================"
    fi
else
    echo "❌ Error during outfit generation"
    echo ""
    echo "❌ FAILED: Outfit generation failed"
    echo "============================================================"
fi

echo ""
echo "🏁 Test completed!"
echo "============================================================" 