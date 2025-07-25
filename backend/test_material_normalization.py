#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.wardrobe_analysis_service import WardrobeAnalysisService
from firebase_admin import firestore
import firebase_admin
from firebase_admin import credentials

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-credentials.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

def test_material_normalization():
    """Test the material normalization function."""
    service = WardrobeAnalysisService()
    
    # Test cases from the debug output
    test_materials = [
        'Cotton', 'Linen', 'Wool', 'Denim', 'Corduroy', 'Light Cotton',
        'Polyester', 'Mesh', 'Synthetic Blends', 'Fleece'
    ]
    
    print("Testing material normalization:")
    for material in test_materials:
        normalized = service._normalize_material(material)
        print(f"  '{material}' -> '{normalized}'")
    
    # Test preprocessing on a sample item
    print("\nTesting preprocessing on sample item...")
    
    # Get a sample item from Firestore
    wardrobe_ref = db.collection('wardrobe')
    docs = wardrobe_ref.limit(1).stream()
    
    for doc in docs:
        item_data = doc.to_dict()
        print(f"Original item data keys: {list(item_data.keys())}")
        
        # Test preprocessing
        processed_data = service._preprocess_item_data(item_data)
        print(f"Processed item data keys: {list(processed_data.keys())}")
        
        # Check if metadata was processed
        if 'metadata' in processed_data:
            metadata = processed_data['metadata']
            if 'visualAttributes' in metadata:
                va = metadata['visualAttributes']
                print(f"Visual attributes keys: {list(va.keys())}")
                
                if 'materialCompatibility' in va:
                    mc = va['materialCompatibility']
                    print(f"Material compatibility keys: {list(mc.keys())}")
                    
                    if 'weatherAppropriate' in mc:
                        wa = mc['weatherAppropriate']
                        print(f"Weather appropriate seasons: {list(wa.keys())}")
                        for season, materials in wa.items():
                            print(f"  {season}: {materials}")

if __name__ == "__main__":
    test_material_normalization() 