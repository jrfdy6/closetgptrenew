#!/usr/bin/env python3
"""
Fix Teal Shirt Metadata Structure
Quick script to properly structure the teal shirt's metadata
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from google.cloud import firestore

db = firestore.Client()

# Find and fix the teal shirt
docs = db.collection('wardrobe').where('userId', '==', 'dANqjiI0CKgaitxzYtw1bhtvQrG3').stream()

print("Searching for teal shirt...")

for doc in docs:
    item = doc.to_dict()
    if 'Teal' in item.get('name', '') and 't-shirt' in item.get('name', '').lower():
        print(f"\n✅ Found: {item.get('name')}")
        print(f"   ID: {doc.id}")
        
        # Check if it has analysis but no visualAttributes
        analysis = item.get('analysis', {})
        metadata = item.get('metadata', {})
        
        if analysis and not metadata.get('visualAttributes'):
            print("   ⚠️  Has analysis but no visualAttributes - FIXING...")
            
            # Extract from analysis and properly structure
            update_data = {
                'metadata': {
                    'visualAttributes': {
                        'material': analysis.get('material', 'Cotton'),
                        'pattern': analysis.get('pattern', 'solid'),
                        'fit': analysis.get('fit', 'regular'),
                        'formalLevel': analysis.get('formalLevel', 'Casual'),
                        'sleeveLength': analysis.get('sleeveLength', 'Short'),
                        'fabricWeight': 'medium',
                        'silhouette': 'regular',
                        'genderTarget': analysis.get('gender', 'Unisex'),
                        'wearLayer': 'Inner',
                        'textureStyle': 'smooth',
                        'length': 'regular',
                        'neckline': 'crew',
                        'transparency': 'opaque',
                        'collarType': 'none',
                        'embellishments': 'none',
                        'printSpecificity': 'none',
                        'rise': 'none',
                        'legOpening': 'none',
                        'heelHeight': 'none',
                        'statementLevel': 3,
                        'waistbandType': 'none',
                        'backgroundRemoved': False,
                        'hangerPresent': False
                    },
                    'naturalDescription': f"A {analysis.get('fit', 'regular').lower()} {analysis.get('material', 'cotton').lower()} t-shirt in {item.get('color', 'teal').lower()}",
                    'colorAnalysis': metadata.get('colorAnalysis', {}),
                    'analysisTimestamp': metadata.get('analysisTimestamp', 0)
                }
            }
            
            # Update Firestore
            db.collection('wardrobe').document(doc.id).update(update_data)
            
            print("   ✅ Fixed! Now has properly structured metadata.visualAttributes")
            print(f"      material: {analysis.get('material', 'Cotton')}")
            print(f"      description: A {analysis.get('fit', 'regular').lower()} {analysis.get('material', 'cotton').lower()} t-shirt")
            print(f"      fit: {analysis.get('fit', 'regular')}")
            print(f"      sleeveLength: {analysis.get('sleeveLength', 'Short')}")
        else:
            print("   ✅ Already has proper metadata structure")

print("\n✅ Done!")

