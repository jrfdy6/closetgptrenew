#!/usr/bin/env python3
"""
Firebase Outfit Search Utility
This script helps you search for outfits in your Firestore database with various filters.
"""

import os
import sys
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

# Add the backend src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

try:
    from config.firebase import db, firebase_initialized, initialize_firebase
    from custom_types.outfit import OutfitGeneratedOutfit
    from custom_types.profile import UserProfile
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

class OutfitSearcher:
    """Utility class for searching outfits in Firebase"""
    
    def __init__(self):
        if not firebase_initialized:
            print("🔥 Initializing Firebase...")
            if not initialize_firebase():
                print("❌ Failed to initialize Firebase")
                sys.exit(1)
        
        self.db = db
        self.outfits_collection = self.db.collection('outfits')
        self.wardrobe_collection = self.db.collection('wardrobe')
        self.users_collection = self.db.collection('users')
    
    def search_outfits_by_user(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search for outfits by user ID"""
        print(f"🔍 Searching for outfits for user: {user_id}")
        
        try:
            # Method 1: Direct user_id field query
            outfits = self.outfits_collection.where('user_id', '==', user_id).limit(limit).stream()
            outfit_list = []
            
            for doc in outfits:
                outfit_data = doc.to_dict()
                outfit_data['id'] = doc.id
                outfit_list.append(outfit_data)
            
            if outfit_list:
                print(f"✅ Found {len(outfit_list)} outfits with direct user_id field")
                return outfit_list
            
            # Method 2: Search through items' userId if no direct matches
            print("🔍 No direct matches, searching through outfit items...")
            all_outfits = self.outfits_collection.limit(1000).stream()
            
            for doc in all_outfits:
                outfit_data = doc.to_dict()
                items = outfit_data.get('items', [])
                
                # Check if any item belongs to the user
                for item in items:
                    if isinstance(item, dict) and item.get('userId') == user_id:
                        outfit_data['id'] = doc.id
                        outfit_list.append(outfit_data)
                        break
                    elif isinstance(item, str):
                        # Item is an ID, check wardrobe collection
                        try:
                            item_doc = self.wardrobe_collection.document(item).get()
                            if item_doc.exists:
                                item_data = item_doc.to_dict()
                                if item_data.get('userId') == user_id:
                                    outfit_data['id'] = doc.id
                                    outfit_list.append(outfit_data)
                                    break
                        except Exception as e:
                            continue
            
            print(f"✅ Found {len(outfit_list)} outfits through item search")
            return outfit_list
            
        except Exception as e:
            print(f"❌ Error searching outfits: {e}")
            return []
    
    def search_outfits_by_occasion(self, occasion: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search for outfits by occasion"""
        print(f"🔍 Searching for outfits with occasion: {occasion}")
        
        try:
            outfits = self.outfits_collection.where('occasion', '==', occasion).limit(limit).stream()
            outfit_list = []
            
            for doc in outfits:
                outfit_data = doc.to_dict()
                outfit_data['id'] = doc.id
                outfit_list.append(outfit_data)
            
            print(f"✅ Found {len(outfit_list)} outfits with occasion: {occasion}")
            return outfit_list
            
        except Exception as e:
            print(f"❌ Error searching outfits by occasion: {e}")
            return []
    
    def search_outfits_by_style(self, style: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search for outfits by style"""
        print(f"🔍 Searching for outfits with style: {style}")
        
        try:
            outfits = self.outfits_collection.where('style', '==', style).limit(limit).stream()
            outfit_list = []
            
            for doc in outfits:
                outfit_data = doc.to_dict()
                outfit_data['id'] = doc.id
                outfit_list.append(outfit_data)
            
            print(f"✅ Found {len(outfit_list)} outfits with style: {style}")
            return outfit_list
            
        except Exception as e:
            print(f"❌ Error searching outfits by style: {e}")
            return []
    
    def search_outfits_by_date_range(self, start_date: str, end_date: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search for outfits by date range"""
        print(f"🔍 Searching for outfits between {start_date} and {end_date}")
        
        try:
            # Convert string dates to datetime objects
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
            
            outfits = self.outfits_collection.where('created_at', '>=', start_dt).where('created_at', '<=', end_dt).limit(limit).stream()
            outfit_list = []
            
            for doc in outfits:
                outfit_data = doc.to_dict()
                outfit_data['id'] = doc.id
                outfit_list.append(outfit_data)
            
            print(f"✅ Found {len(outfit_list)} outfits in date range")
            return outfit_list
            
        except Exception as e:
            print(f"❌ Error searching outfits by date range: {e}")
            return []
    
    def search_outfits_by_weather(self, temperature: float, weather_condition: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Search for outfits by weather conditions"""
        print(f"🔍 Searching for outfits suitable for {temperature}°F weather")
        
        try:
            # Determine season based on temperature
            if temperature < 50:
                season = "winter"
            elif temperature < 70:
                season = "spring/fall"
            else:
                season = "summer"
            
            print(f"🌡️  Determined season: {season}")
            
            # Search for outfits with matching seasonality
            outfits = self.outfits_collection.where('seasonality', 'array_contains', season).limit(limit).stream()
            outfit_list = []
            
            for doc in outfits:
                outfit_data = doc.to_dict()
                outfit_data['id'] = doc.id
                outfit_list.append(outfit_data)
            
            print(f"✅ Found {len(outfit_list)} outfits suitable for {season}")
            return outfit_list
            
        except Exception as e:
            print(f"❌ Error searching outfits by weather: {e}")
            return []
    
    def get_all_outfits(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all outfits (useful for debugging)"""
        print(f"🔍 Getting all outfits (limit: {limit})")
        
        try:
            outfits = self.outfits_collection.limit(limit).stream()
            outfit_list = []
            
            for doc in outfits:
                outfit_data = doc.to_dict()
                outfit_data['id'] = doc.id
                outfit_list.append(outfit_data)
            
            print(f"✅ Found {len(outfit_list)} total outfits")
            return outfit_list
            
        except Exception as e:
            print(f"❌ Error getting all outfits: {e}")
            return []
    
    def display_outfit_summary(self, outfit: Dict[str, Any]) -> None:
        """Display a summary of an outfit"""
        print(f"\n👕 Outfit: {outfit.get('name', 'Unnamed')} (ID: {outfit.get('id', 'N/A')})")
        print(f"   Occasion: {outfit.get('occasion', 'N/A')}")
        print(f"   Style: {outfit.get('style', 'N/A')}")
        print(f"   Items: {len(outfit.get('items', []))}")
        print(f"   Created: {outfit.get('created_at', 'N/A')}")
        print(f"   User ID: {outfit.get('user_id', 'N/A')}")
        
        # Show items if available
        items = outfit.get('items', [])
        if items:
            print("   Items:")
            for i, item in enumerate(items[:5]):  # Show first 5 items
                if isinstance(item, dict):
                    print(f"     {i+1}. {item.get('category', 'Unknown')} - {item.get('name', 'Unnamed')}")
                else:
                    print(f"     {i+1}. Item ID: {item}")
            if len(items) > 5:
                print(f"     ... and {len(items) - 5} more items")

def main():
    """Main function to demonstrate outfit searching"""
    print("🔥 Firebase Outfit Search Utility")
    print("=" * 50)
    
    # Initialize searcher
    searcher = OutfitSearcher()
    
    while True:
        print("\n🔍 Choose a search option:")
        print("1. Search outfits by user ID")
        print("2. Search outfits by occasion")
        print("3. Search outfits by style")
        print("4. Search outfits by date range")
        print("5. Search outfits by weather")
        print("6. Get all outfits")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == "1":
            user_id = input("Enter user ID: ").strip()
            if user_id:
                outfits = searcher.search_outfits_by_user(user_id)
                if outfits:
                    print(f"\n📋 Found {len(outfits)} outfits:")
                    for outfit in outfits[:10]:  # Show first 10
                        searcher.display_outfit_summary(outfit)
                    if len(outfits) > 10:
                        print(f"\n... and {len(outfits) - 10} more outfits")
                else:
                    print("❌ No outfits found for this user")
        
        elif choice == "2":
            occasion = input("Enter occasion (e.g., casual, formal, business): ").strip()
            if occasion:
                outfits = searcher.search_outfits_by_occasion(occasion)
                if outfits:
                    print(f"\n📋 Found {len(outfits)} outfits:")
                    for outfit in outfits[:10]:
                        searcher.display_outfit_summary(outfit)
                else:
                    print("❌ No outfits found for this occasion")
        
        elif choice == "3":
            style = input("Enter style (e.g., bohemian, classic, streetwear): ").strip()
            if style:
                outfits = searcher.search_outfits_by_style(style)
                if outfits:
                    print(f"\n📋 Found {len(outfits)} outfits:")
                    for outfit in outfits[:10]:
                        searcher.display_outfit_summary(outfit)
                else:
                    print("❌ No outfits found for this style")
        
        elif choice == "4":
            start_date = input("Enter start date (YYYY-MM-DD): ").strip()
            end_date = input("Enter end date (YYYY-MM-DD): ").strip()
            if start_date and end_date:
                outfits = searcher.search_outfits_by_date_range(start_date, end_date)
                if outfits:
                    print(f"\n📋 Found {len(outfits)} outfits:")
                    for outfit in outfits[:10]:
                        searcher.display_outfit_summary(outfit)
                else:
                    print("❌ No outfits found in this date range")
        
        elif choice == "5":
            try:
                temp = float(input("Enter temperature (°F): ").strip())
                outfits = searcher.search_outfits_by_weather(temp)
                if outfits:
                    print(f"\n📋 Found {len(outfits)} outfits:")
                    for outfit in outfits[:10]:
                        searcher.display_outfit_summary(outfit)
                else:
                    print("❌ No outfits found for this weather")
            except ValueError:
                print("❌ Please enter a valid temperature")
        
        elif choice == "6":
            outfits = searcher.get_all_outfits()
            if outfits:
                print(f"\n📋 Found {len(outfits)} total outfits:")
                for outfit in outfits[:10]:
                    searcher.display_outfit_summary(outfit)
                if len(outfits) > 10:
                    print(f"\n... and {len(outfits) - 10} more outfits")
            else:
                print("❌ No outfits found in database")
        
        elif choice == "7":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please enter a number between 1-7.")

if __name__ == "__main__":
    main()
