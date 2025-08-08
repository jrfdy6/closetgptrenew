#!/usr/bin/env python3
"""
Comprehensive search for missing outfits across all possible field names and structures.
This will help us find where your 138 outfits are actually stored.
"""

import firebase_admin
from firebase_admin import firestore
import json

def find_outfits_comprehensive():
    """Search for outfits using all possible field names and structures."""
    print("🔍 Comprehensive Outfit Search")
    print("=" * 80)
    
    try:
        # Initialize Firebase if not already initialized
        if not firebase_admin._apps:
            print("🔍 Initializing Firebase...")
            firebase_admin.initialize_app()
        
        db = firestore.client()
        print("✅ Firestore client created successfully")
        
        # Your user ID
        target_user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
        print(f"🎯 Searching for outfits belonging to: {target_user_id}")
        print()
        
        # Test 1: Direct query with user_id (snake_case)
        print("🧪 Test 1: Querying with user_id (snake_case)")
        try:
            query1 = db.collection('outfits').where('user_id', '==', target_user_id)
            results1 = list(query1.stream())
            print(f"   ✅ Found {len(results1)} outfits with user_id field")
            if results1:
                sample = results1[0].to_dict()
                print(f"   📄 Sample field keys: {list(sample.keys())}")
        except Exception as e:
            print(f"   ❌ Error with user_id query: {e}")
        
        # Test 2: Direct query with userId (camelCase)
        print("\n🧪 Test 2: Querying with userId (camelCase)")
        try:
            query2 = db.collection('outfits').where('userId', '==', target_user_id)
            results2 = list(query2.stream())
            print(f"   ✅ Found {len(results2)} outfits with userId field")
            if results2:
                sample = results2[0].to_dict()
                print(f"   📄 Sample field keys: {list(sample.keys())}")
        except Exception as e:
            print(f"   ❌ Error with userId query: {e}")
        
        # Test 3: Get all outfits and analyze structure
        print("\n🧪 Test 3: Analyzing all outfit documents (limited to 50)")
        try:
            all_outfits = list(db.collection('outfits').limit(50).stream())
            print(f"   📊 Total outfits sampled: {len(all_outfits)}")
            
            user_id_variants = {}
            field_analysis = {}
            user_matches = []
            
            for i, doc in enumerate(all_outfits):
                data = doc.to_dict()
                doc_fields = list(data.keys())
                
                # Count field frequency
                for field in doc_fields:
                    field_analysis[field] = field_analysis.get(field, 0) + 1
                
                # Look for user-related fields
                user_fields = {}
                for field in doc_fields:
                    if 'user' in field.lower():
                        value = data.get(field)
                        user_fields[field] = value
                        
                        # Track user ID variants
                        if value:
                            user_id_variants[field] = user_id_variants.get(field, set())
                            user_id_variants[field].add(str(value))
                
                # Check if this outfit belongs to our user
                if any(str(data.get(field)) == target_user_id for field in user_fields.keys()):
                    user_matches.append({
                        'id': doc.id,
                        'user_fields': user_fields,
                        'items_count': len(data.get('items', []))
                    })
                
                # Print first few samples
                if i < 3:
                    print(f"   📄 Sample {i+1} - ID: {doc.id}")
                    print(f"      Fields: {doc_fields}")
                    if user_fields:
                        print(f"      User fields: {user_fields}")
                    print()
            
            print(f"   🎯 Found {len(user_matches)} outfits belonging to target user")
            print(f"   📊 Most common fields across all outfits:")
            for field, count in sorted(field_analysis.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"      {field}: {count} documents")
            
            print(f"\n   👥 User ID field variants found:")
            for field, values in user_id_variants.items():
                print(f"      {field}: {len(values)} unique values")
                if len(values) <= 5:
                    print(f"         Values: {list(values)}")
        
        except Exception as e:
            print(f"   ❌ Error analyzing documents: {e}")
        
        # Test 4: Check items for userId (complex filtering)
        print("\n🧪 Test 4: Searching by item-level userId")
        try:
            all_outfits_for_items = list(db.collection('outfits').limit(100).stream())
            item_matches = []
            
            for doc in all_outfits_for_items:
                data = doc.to_dict()
                items = data.get('items', [])
                
                for item in items:
                    if isinstance(item, dict):
                        item_userId = item.get('userId')
                        if item_userId == target_user_id:
                            item_matches.append({
                                'outfit_id': doc.id,
                                'outfit_user_id': data.get('user_id'),
                                'outfit_userId': data.get('userId'),
                                'items_count': len(items)
                            })
                            break
                    elif isinstance(item, str):
                        # Check wardrobe collection
                        try:
                            item_doc = db.collection('wardrobe').document(item).get()
                            if item_doc.exists:
                                item_data = item_doc.to_dict()
                                if item_data.get('userId') == target_user_id:
                                    item_matches.append({
                                        'outfit_id': doc.id,
                                        'outfit_user_id': data.get('user_id'),
                                        'outfit_userId': data.get('userId'),
                                        'items_count': len(items)
                                    })
                                    break
                        except:
                            continue
            
            print(f"   ✅ Found {len(item_matches)} outfits with matching item userId")
            
        except Exception as e:
            print(f"   ❌ Error with item-level search: {e}")
        
        # Test 5: Check for other collection names
        print("\n🧪 Test 5: Checking other possible collections")
        possible_collections = ['user_outfits', 'outfits_v2', 'generated_outfits', 'my_outfits']
        
        for collection_name in possible_collections:
            try:
                test_docs = list(db.collection(collection_name).limit(5).stream())
                if test_docs:
                    print(f"   📁 Found collection '{collection_name}' with {len(test_docs)} documents")
                    sample = test_docs[0].to_dict()
                    print(f"      Sample keys: {list(sample.keys())}")
            except Exception as e:
                print(f"   ⚠️ Collection '{collection_name}' not accessible: {e}")
        
        # Test 6: Get total count of outfits collection
        print("\n🧪 Test 6: Getting total outfit collection size")
        try:
            # Get a larger sample to estimate total size
            large_sample = list(db.collection('outfits').limit(1000).stream())
            print(f"   📊 Sample of {len(large_sample)} outfits from collection")
            
            # Count how many belong to our user
            our_outfits = 0
            for doc in large_sample:
                data = doc.to_dict()
                # Check all possible user fields
                if (data.get('user_id') == target_user_id or 
                    data.get('userId') == target_user_id):
                    our_outfits += 1
            
            print(f"   🎯 {our_outfits} outfits belong to target user in this sample")
            
        except Exception as e:
            print(f"   ❌ Error getting collection size: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def analyze_wardrobe_collection():
    """Also check wardrobe collection structure."""
    print("\n" + "=" * 80)
    print("🧪 Analyzing Wardrobe Collection")
    print("=" * 80)
    
    try:
        db = firestore.client()
        target_user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
        
        # Get wardrobe items for our user
        wardrobe_items = list(db.collection('wardrobe').where('userId', '==', target_user_id).limit(20).stream())
        print(f"📦 Found {len(wardrobe_items)} wardrobe items for user")
        
        if wardrobe_items:
            sample = wardrobe_items[0].to_dict()
            print(f"📄 Sample wardrobe item keys: {list(sample.keys())}")
            print(f"   Item ID: {wardrobe_items[0].id}")
            print(f"   User ID: {sample.get('userId')}")
            print(f"   Type: {sample.get('type')}")
            print(f"   Name: {sample.get('name')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing wardrobe: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Comprehensive Outfit Search")
    print("This will search all possible locations for your 138 outfits")
    print()
    
    # Search for outfits
    outfits_success = find_outfits_comprehensive()
    
    # Analyze wardrobe
    wardrobe_success = analyze_wardrobe_collection()
    
    print("\n" + "=" * 80)
    if outfits_success and wardrobe_success:
        print("✅ Comprehensive search completed!")
        print("\n📝 Next steps:")
        print("1. Review the results above to see where your outfits are stored")
        print("2. Note which field name contains your user ID")
        print("3. Check if the backend is querying the right field")
        print("4. Look for any field name mismatches or data structure issues")
    else:
        print("❌ Some searches failed. Check the errors above.")
    
    print("\n🔍 Key questions to answer:")
    print("- Which test found the most outfits for your user?")
    print("- What field name actually contains your user ID?")
    print("- Are the outfits in the 'outfits' collection or elsewhere?")
    print("- Do the outfit documents have the expected structure?")