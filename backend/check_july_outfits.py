#!/usr/bin/env python3

import requests
import json
from datetime import datetime

# Backend API URL
BACKEND_URL = "https://closetgptrenew-backend-production.up.railway.app"

def get_all_outfits():
    """Get all outfits from the backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/outfits/test", timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting outfits: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error connecting to backend: {e}")
        return []

def find_july_17_outfits(outfits):
    """Find outfits created on July 17, 2025"""
    july_17_outfits = []
    
    for outfit in outfits:
        created_at = outfit.get('createdAt')
        if created_at:
            # Convert timestamp to datetime
            if isinstance(created_at, str):
                try:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                except:
                    continue
            else:
                dt = datetime.fromtimestamp(created_at / 1000)
            
            # Check if it's July 17, 2025
            if dt.year == 2025 and dt.month == 7 and dt.day == 17:
                july_17_outfits.append({
                    'id': outfit.get('id'),
                    'name': outfit.get('name', 'Unknown'),
                    'created_at': dt.strftime('%Y-%m-%d %H:%M:%S'),
                    'data': outfit
                })
    
    return july_17_outfits

def main():
    print("🔍 Checking for outfits from July 17, 2025...")
    
    # Get all outfits
    outfits = get_all_outfits()
    if not outfits:
        print("❌ No outfits found or error connecting to backend")
        return
    
    print(f"📊 Found {len(outfits)} total outfits")
    
    # Find July 17 outfits
    july_17_outfits = find_july_17_outfits(outfits)
    
    if not july_17_outfits:
        print("✅ No outfits found from July 17, 2025")
        print("\n📅 All current outfits are from July 18, 2025")
        return
    
    print(f"\n🗑️  Found {len(july_17_outfits)} outfits from July 17, 2025:")
    for outfit in july_17_outfits:
        print(f"  - {outfit['name']} (ID: {outfit['id']}) - {outfit['created_at']}")

if __name__ == "__main__":
    main() 