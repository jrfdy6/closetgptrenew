import firebase_admin
from firebase_admin import credentials, firestore
import os

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {
        'projectId': os.getenv('FIREBASE_PROJECT_ID')
    })
db = firestore.client()

user_id = 'dANqjiI0CKgaitxzYtw1bhtvQrG3'

print(f"🔍 Searching for Michael Kors items in wardrobe for user {user_id}...")

wardrobe_ref = db.collection('wardrobe').where('userId', '==', user_id)
items = wardrobe_ref.stream()

michael_kors_items = []

for item_doc in items:
    item_data = item_doc.to_dict()
    name = (item_data.get('name') or '').lower()
    brand = (item_data.get('brand') or '').lower()
    
    if 'michael kors' in name or 'michael kors' in brand or 'kors' in brand:
        michael_kors_items.append(item_data)

print(f"\n✅ Found {len(michael_kors_items)} Michael Kors items\n")

for i, item_data in enumerate(michael_kors_items):
    print(f"================================================================================")
    print(f"Item {i+1}: {item_data.get('name', 'N/A')}")
    print(f"================================================================================")
    print(f"ID: {item_data.get('id')}")
    print(f"Name: {item_data.get('name')}")
    print(f"Type: {item_data.get('type')}")
    print(f"Color: {item_data.get('color')}")
    print(f"Brand: {item_data.get('brand')}")
    print(f"Occasion: {item_data.get('occasion')}")
    print(f"Style: {item_data.get('style')}")
    print(f"Tags: {item_data.get('tags')}")
    
    metadata = item_data.get('metadata', {})
    visual_attrs = metadata.get('visualAttributes', {}) if metadata else {}
    
    print(f"\n🔍 METADATA - visualAttributes:")
    if visual_attrs:
        for key, value in visual_attrs.items():
            if key in ['neckline', 'pattern', 'fit', 'sleeveLength', 'material', 'formalLevel']:
                print(f"  {key}: {value}")
    else:
        print("  NO VISUAL ATTRIBUTES")
    print("\n")
