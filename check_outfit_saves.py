"""
Quick script to check if outfits are being saved to Firestore
"""
import os
import sys
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from src.config.firebase import db

# Your user ID
user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"

print("🔍 Checking outfits collection for recent saves...\n")

# Check outfits from the last hour
one_hour_ago = int((datetime.now() - timedelta(hours=1)).timestamp() * 1000)

try:
    # Query outfits collection
    outfits_ref = db.collection('outfits')\
        .where('user_id', '==', user_id)\
        .where('createdAt', '>', one_hour_ago)\
        .order_by('createdAt', direction='DESCENDING')\
        .limit(10)
    
    outfits = list(outfits_ref.stream())
    
    print(f"📊 Found {len(outfits)} outfits in the last hour\n")
    
    if len(outfits) == 0:
        print("❌ No outfits found in the last hour!")
        print("\nPossible reasons:")
        print("1. No outfits generated yet")
        print("2. Save logic not being executed")
        print("3. 405 error preventing outfit generation")
        print("\nNext steps:")
        print("- Generate an outfit on the personalization demo")
        print("- Check Railway logs for: '✅ Saved outfit'")
    else:
        print("✅ Outfits ARE being saved!\n")
        
        for outfit_doc in outfits:
            outfit = outfit_doc.to_dict()
            created_time = datetime.fromtimestamp(outfit.get('createdAt', 0) / 1000)
            
            print(f"🎯 Outfit: {outfit.get('name', 'Unnamed')}")
            print(f"   ID: {outfit_doc.id}")
            print(f"   Occasion: {outfit.get('occasion', 'N/A')}")
            print(f"   Style: {outfit.get('style', 'N/A')}")
            print(f"   Mood: {outfit.get('mood', 'N/A')}")
            print(f"   Items: {len(outfit.get('items', []))} items")
            print(f"   Created: {created_time.strftime('%I:%M:%S %p')}")
            print(f"   Generation: {outfit.get('generation_strategy', 'unknown')}")
            print()
        
        print(f"📈 Summary:")
        print(f"   Total outfits in last hour: {len(outfits)}")
        print(f"   User ID: {user_id}")
        print(f"   Collection: outfits (not users/{user_id}/outfits)")
        print(f"\n✅ Diversity system should now have history to work with!")

except Exception as e:
    print(f"❌ Error checking Firestore: {e}")
    print("\nMake sure you have:")
    print("1. Firebase credentials configured")
    print("2. Firestore permissions for the user")

