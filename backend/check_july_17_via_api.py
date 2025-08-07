#!/usr/bin/env python3

import requests
import json
from datetime import datetime, timezone

def check_july_17_outfits():
    """Check for outfits created on July 17, 2024 using the API."""
    
    # Backend URL
    backend_url = "https://closetgptrenew-backend-production.up.railway.app"
    
    print("🔍 Checking for outfits created on July 17, 2024")
    print("=" * 50)
    
    # Define July 17, 2024 date range (in milliseconds)
    july_17_start = datetime(2024, 7, 17, 0, 0, 0, tzinfo=timezone.utc).timestamp() * 1000
    july_17_end = datetime(2024, 7, 17, 23, 59, 59, tzinfo=timezone.utc).timestamp() * 1000
    
    print(f"🔍 Looking for outfits created between:")
    print(f"   Start: {datetime.fromtimestamp(july_17_start / 1000).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   End: {datetime.fromtimestamp(july_17_end / 1000).strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Get all outfits from the API
        response = requests.get(f"{backend_url}/api/outfits/test", timeout=30)
        print(f"🔍 API response status: {response.status_code}")
        
        if response.status_code == 200:
            outfits = response.json()
            print(f"🔍 Number of outfits returned: {len(outfits)}")
            
            july_17_outfits = []
            
            for outfit in outfits:
                created_at = outfit.get('createdAt')
                
                # Convert createdAt to timestamp if it's a string
                if isinstance(created_at, str):
                    try:
                        created_at = float(created_at)
                    except ValueError:
                        continue
                
                # Check if outfit was created on July 17, 2024
                if isinstance(created_at, (int, float)):
                    if july_17_start <= created_at <= july_17_end:
                        outfit_info = {
                            'id': outfit.get('id'),
                            'name': outfit.get('name', 'Unknown'),
                            'createdAt': created_at,
                            'createdAt_formatted': datetime.fromtimestamp(created_at / 1000).strftime('%Y-%m-%d %H:%M:%S')
                        }
                        july_17_outfits.append(outfit_info)
                        print(f"🗑️  Found July 17 outfit: {outfit_info['name']} (ID: {outfit_info['id']})")
                        print(f"    Created: {outfit_info['createdAt_formatted']}")
            
            print("\n" + "=" * 50)
            print(f"📊 SUMMARY:")
            print(f"Total outfits checked: {len(outfits)}")
            print(f"Outfits created on July 17, 2024: {len(july_17_outfits)}")
            
            if not july_17_outfits:
                print("✅ No outfits found from July 17, 2024")
                return
            
            print("\n" + "=" * 50)
            print("🗑️  JULY 17 OUTFITS:")
            for outfit in july_17_outfits:
                print(f"  • {outfit['name']} (ID: {outfit['id']})")
                print(f"    Created: {outfit['createdAt_formatted']}")
            
            # Ask for confirmation
            print("\n" + "=" * 50)
            response = input(f"❓ Do you want to delete these {len(july_17_outfits)} outfits? (yes/no): ")
            
            if response.lower() != 'yes':
                print("❌ Deletion cancelled")
                return
            
            # Delete the outfits using the API
            print("\n🗑️  DELETING OUTFITS...")
            deleted_count = 0
            
            for outfit in july_17_outfits:
                try:
                    # Call the delete endpoint
                    delete_response = requests.delete(f"{backend_url}/api/outfits/{outfit['id']}", timeout=30)
                    if delete_response.status_code == 200:
                        print(f"✅ Deleted: {outfit['name']} (ID: {outfit['id']})")
                        deleted_count += 1
                    else:
                        print(f"❌ Failed to delete {outfit['name']} (ID: {outfit['id']}): {delete_response.status_code}")
                except Exception as e:
                    print(f"❌ Error deleting {outfit['name']} (ID: {outfit['id']}): {e}")
            
            print("\n" + "=" * 50)
            print(f"✅ DELETION COMPLETE:")
            print(f"Successfully deleted: {deleted_count}/{len(july_17_outfits)} outfits")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_july_17_outfits() 