#!/bin/bash
# Test the debug filter endpoint to see actual metadata

curl -X POST "https://closetgptrenew-backend-production.up.railway.app/api/outfits/debug-filter" \
  -H "Content-Type: application/json" \
  -d '{
    "occasion": "Athletic",
    "style": "Classic",
    "mood": "Bold",
    "weather": {
      "temperature": 72,
      "condition": "Clear"
    },
    "wardrobe": [],
    "user_profile": {
      "bodyType": "Oval",
      "height": "5'\''8\" - 5'\''11\"",
      "weight": "201-250 lbs",
      "gender": "Male"
    },
    "semantic": true
  }' | python3 -m json.tool

