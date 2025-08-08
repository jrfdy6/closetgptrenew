#!/usr/bin/env python3

import requests
import json
from datetime import datetime

# Backend API URL
BACKEND_URL = "https://closetgptrenew-backend-production.up.railway.app"

def get_actual_outfits():
    """Get actual outfits from test endpoint"""
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

def remove_outfit(outfit_id):
    """Remove an outfit by ID"""
    try:
        response = requests.delete(f"{BACKEND_URL}/api/outfits/{outfit_id}", timeout=30)
        if response.status_code == 200:
            return True
        else:
            print(f"Error removing outfit {outfit_id}: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error removing outfit {outfit_id}: {e}")
        return False

def main():
    print("🔍 Finding outfits from July 17, 2025...")
    
    # Get all outfits
    outfits = get_actual_outfits()
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
    
    # Ask for confirmation
    print(f"\n⚠️  Are you sure you want to delete these {len(july_17_outfits)} outfits?")
    confirm = input("Type 'DELETE' to confirm: ")
    
    if confirm != "DELETE":
        print("❌ Deletion cancelled")
        return
    
    # Remove outfits
    print(f"\n🗑️  Removing {len(july_17_outfits)} outfits...")
    removed_count = 0
    
    for outfit in july_17_outfits:
        print(f"  Removing: {outfit['name']}...")
        if remove_outfit(outfit['id']):
            removed_count += 1
            print(f"    ✅ Removed: {outfit['name']}")
        else:
            print(f"    ❌ Failed to remove: {outfit['name']}")
    
    print(f"\n✅ Successfully removed {removed_count} out of {len(july_17_outfits)} outfits")

if __name__ == "__main__":
    main() 