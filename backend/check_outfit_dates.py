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

def check_outfit_dates(outfits):
    """Check the dates of all outfits"""
    print("📅 Outfit dates:")
    print("-" * 50)
    
    for i, outfit in enumerate(outfits, 1):
        created_at = outfit.get('createdAt')
        name = outfit.get('name', 'Unknown')
        outfit_id = outfit.get('id', 'Unknown')
        
        if created_at:
            # Convert timestamp to datetime
            if isinstance(created_at, str):
                try:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                except:
                    dt_str = "Invalid date format"
                    dt = None
            else:
                dt = datetime.fromtimestamp(created_at / 1000)
            
            if dt:
                dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                day_name = dt.strftime('%A')
                print(f"{i:2d}. {name}")
                print(f"     ID: {outfit_id}")
                print(f"     Date: {dt_str} ({day_name})")
                print()
            else:
                print(f"{i:2d}. {name} - {dt_str}")
                print()
        else:
            print(f"{i:2d}. {name} - No date found")
            print()

def main():
    print("🔍 Checking outfit dates...")
    
    # Get all outfits
    outfits = get_all_outfits()
    if not outfits:
        print("❌ No outfits found or error connecting to backend")
        return
    
    print(f"📊 Found {len(outfits)} total outfits")
    print()
    
    # Check dates
    check_outfit_dates(outfits)

if __name__ == "__main__":
    main() 