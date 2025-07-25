#!/usr/bin/env python3
"""
Comprehensive Data & Models Audit
Audits the current environment for data quality and migration completeness.
"""

import firebase_admin
from firebase_admin import firestore, initialize_app
from collections import Counter
import numpy as np
import time

# Initialize Firebase
if not firebase_admin._apps:
    initialize_app()
db = firestore.client()

def comprehensive_audit():
    """Run a comprehensive audit of the current environment."""
    print("🔍 Comprehensive Data & Models Audit")
    print("=" * 60)
    
    # Get project info from service account
    try:
        with open('service-account-key.json', 'r') as f:
            import json
            service_account = json.load(f)
            project_id = service_account.get('project_id', 'unknown')
    except:
        project_id = 'unknown'
    
    print(f"📊 Project: {project_id}")
    print(f"🕒 Audit Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    collections = ['wardrobe', 'outfits', 'users', 'analytics_events', 'style_profiles']
    
    print(f"\n📁 Collection Analysis:")
    print("=" * 40)
    
    total_docs = 0
    collection_stats = {}
    
    for collection in collections:
        try:
            docs = list(db.collection(collection).stream())
            count = len(docs)
            total_docs += count
            
            if count > 0:
                # Sample analysis
                sample = docs[:min(50, count)]
                schema_versions = Counter()
                missing_schema = 0
                
                for doc in sample:
                    data = doc.to_dict()
                    schema_ver = data.get('schema_version', 'missing')
                    schema_versions[schema_ver] += 1
                    if schema_ver == 'missing':
                        missing_schema += 1
                
                collection_stats[collection] = {
                    'total': count,
                    'sample_size': len(sample),
                    'schema_versions': dict(schema_versions),
                    'missing_schema_pct': (missing_schema / len(sample) * 100) if sample else 0
                }
                
                print(f"✅ {collection}: {count:,} documents")
                print(f"   Schema versions: {dict(schema_versions)}")
                if missing_schema > 0:
                    print(f"   ⚠️  {missing_schema} docs missing schema version")
            else:
                print(f"ℹ️  {collection}: 0 documents")
                
        except Exception as e:
            print(f"❌ {collection}: Error - {e}")
    
    print(f"\n📊 Overall Statistics:")
    print("=" * 40)
    print(f"Total documents: {total_docs:,}")
    print(f"Collections with data: {len([c for c in collection_stats.values() if c['total'] > 0])}")
    
    # Detailed analysis for main collections
    if 'wardrobe' in collection_stats and collection_stats['wardrobe']['total'] > 0:
        analyze_wardrobe_data()
    
    if 'outfits' in collection_stats and collection_stats['outfits']['total'] > 0:
        analyze_outfits_data()
    
    print(f"\n🎯 Migration Completeness Assessment:")
    print("=" * 50)
    assess_migration_completeness(collection_stats)
    
    print(f"\n✅ Audit Complete!")

def analyze_wardrobe_data():
    """Detailed analysis of wardrobe collection."""
    print(f"\n👕 Wardrobe Collection Analysis:")
    print("-" * 40)
    
    docs = list(db.collection('wardrobe').stream())
    sample = docs[:min(20, len(docs))]
    
    metadata_complete = 0
    has_embeddings = 0
    has_images = 0
    test_items = 0
    
    for doc in sample:
        data = doc.to_dict()
        
        # Check metadata completeness
        if data.get('metadata') and data['metadata'].get('visualAttributes'):
            metadata_complete += 1
        
        # Check embeddings
        if data.get('clipEmbedding') or data.get('embedding'):
            has_embeddings += 1
        
        # Check images
        if data.get('imageUrl'):
            has_images += 1
        
        # Check for test items
        name = data.get('name', '').lower()
        if any(keyword in name for keyword in ['test', 'demo', 'sample']):
            test_items += 1
    
    total = len(sample)
    print(f"   Sample size: {total}")
    print(f"   Metadata complete: {metadata_complete}/{total} ({metadata_complete/total*100:.1f}%)")
    print(f"   Has embeddings: {has_embeddings}/{total} ({has_embeddings/total*100:.1f}%)")
    print(f"   Has images: {has_images}/{total} ({has_images/total*100:.1f}%)")
    print(f"   Test items: {test_items}/{total} ({test_items/total*100:.1f}%)")

def analyze_outfits_data():
    """Detailed analysis of outfits collection."""
    print(f"\n👔 Outfits Collection Analysis:")
    print("-" * 40)
    
    docs = list(db.collection('outfits').stream())
    sample = docs[:min(20, len(docs))]
    
    has_items = 0
    has_mood = 0
    has_style = 0
    valid_structure = 0
    
    for doc in sample:
        data = doc.to_dict()
        
        # Check if outfit has items
        if data.get('items') and len(data['items']) > 0:
            has_items += 1
        
        # Check for mood field
        if data.get('mood'):
            has_mood += 1
        
        # Check for style field
        if data.get('style'):
            has_style += 1
        
        # Check for valid structure
        if data.get('items') and data.get('occasion'):
            valid_structure += 1
    
    total = len(sample)
    print(f"   Sample size: {total}")
    print(f"   Has items: {has_items}/{total} ({has_items/total*100:.1f}%)")
    print(f"   Has mood: {has_mood}/{total} ({has_mood/total*100:.1f}%)")
    print(f"   Has style: {has_style}/{total} ({has_style/total*100:.1f}%)")
    print(f"   Valid structure: {valid_structure}/{total} ({valid_structure/total*100:.1f}%)")

def assess_migration_completeness(collection_stats):
    """Assess the overall migration completeness."""
    print(f"\n📋 Migration Completeness Checklist:")
    print("-" * 40)
    
    checks = []
    
    # Schema versioning
    all_have_schema = True
    for collection, stats in collection_stats.items():
        if stats['missing_schema_pct'] > 0:
            all_have_schema = False
            break
    
    checks.append(("✅ Schema versioning", all_have_schema))
    
    # Data presence
    has_wardrobe = collection_stats.get('wardrobe', {}).get('total', 0) > 0
    checks.append(("✅ Wardrobe data present", has_wardrobe))
    
    has_outfits = collection_stats.get('outfits', {}).get('total', 0) > 0
    checks.append(("✅ Outfits data present", has_outfits))
    
    # Overall assessment
    passed_checks = sum(1 for _, passed in checks if passed)
    total_checks = len(checks)
    
    print(f"   Schema versioning: {'✅' if all_have_schema else '❌'}")
    print(f"   Wardrobe data: {'✅' if has_wardrobe else '❌'}")
    print(f"   Outfits data: {'✅' if has_outfits else '❌'}")
    
    print(f"\n🎯 Overall Score: {passed_checks}/{total_checks} ({passed_checks/total_checks*100:.1f}%)")
    
    if passed_checks == total_checks:
        print("🎉 Migration appears complete!")
    else:
        print("⚠️  Some migration steps may be needed.")

if __name__ == "__main__":
    comprehensive_audit() 