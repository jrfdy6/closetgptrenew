#!/usr/bin/env python3
"""
Dual Environment Audit Script
Compares dev and prod environments to verify migration completeness.
"""

import firebase_admin
from firebase_admin import firestore, initialize_app, credentials
import os
from typing import Dict, Any, List
from collections import Counter

# === CONFIGURATION ===
# Set these to your actual project IDs and service account paths
DEV_PROJECT_ID = "your-dev-project-id"
PROD_PROJECT_ID = "your-prod-project-id"
DEV_SERVICE_ACCOUNT_PATH = "path/to/dev-service-account.json"
PROD_SERVICE_ACCOUNT_PATH = "path/to/prod-service-account.json"

# Set to True when you have the service account files configured
ENABLED = False

def initialize_firebase_app(project_id: str, service_account_path: str):
    """Initialize Firebase app for a specific project."""
    try:
        cred = credentials.Certificate(service_account_path)
        app = initialize_app(cred, name=project_id)
        return firestore.client(app=app)
    except Exception as e:
        print(f"❌ Failed to initialize {project_id}: {e}")
        return None

def get_collection_stats(db, collection_name: str) -> Dict[str, Any]:
    """Get statistics for a collection."""
    try:
        docs = list(db.collection(collection_name).stream())
        total = len(docs)
        
        # Sample analysis (first 50 docs)
        sample = docs[:50]
        schema_versions = Counter()
        has_metadata = 0
        has_embeddings = 0
        
        for doc in sample:
            data = doc.to_dict()
            schema_versions[data.get('schema_version', 'missing')] += 1
            
            if collection_name == 'wardrobe':
                if data.get('metadata'):
                    has_metadata += 1
                if data.get('clipEmbedding') or data.get('embedding'):
                    has_embeddings += 1
        
        return {
            'total': total,
            'sample_size': len(sample),
            'schema_versions': dict(schema_versions),
            'has_metadata_pct': (has_metadata / len(sample) * 100) if sample else 0,
            'has_embeddings_pct': (has_embeddings / len(sample) * 100) if sample else 0
        }
    except Exception as e:
        print(f"❌ Error analyzing {collection_name}: {e}")
        return {'error': str(e)}

def compare_environments():
    """Compare dev and prod environments."""
    if not ENABLED:
        print("⚠️  Dual environment audit is disabled.")
        print("To enable:")
        print("1. Set your project IDs in DEV_PROJECT_ID and PROD_PROJECT_ID")
        print("2. Set your service account paths in DEV_SERVICE_ACCOUNT_PATH and PROD_SERVICE_ACCOUNT_PATH")
        print("3. Set ENABLED = True")
        print("\nExample configuration:")
        print("DEV_PROJECT_ID = 'closetgpt-dev'")
        print("PROD_PROJECT_ID = 'closetgpt-prod'")
        print("DEV_SERVICE_ACCOUNT_PATH = './service-accounts/dev-key.json'")
        print("PROD_SERVICE_ACCOUNT_PATH = './service-accounts/prod-key.json'")
        return
    
    print("🔍 Dual Environment Migration Audit")
    print("=" * 50)
    
    # Initialize both environments
    dev_db = initialize_firebase_app(DEV_PROJECT_ID, DEV_SERVICE_ACCOUNT_PATH)
    prod_db = initialize_firebase_app(PROD_PROJECT_ID, PROD_SERVICE_ACCOUNT_PATH)
    
    if not dev_db or not prod_db:
        print("❌ Failed to initialize one or both environments")
        return
    
    collections = ['wardrobe', 'outfits', 'users', 'analytics_events']
    
    print(f"\n📊 Comparing {DEV_PROJECT_ID} (dev) vs {PROD_PROJECT_ID} (prod)")
    print("-" * 50)
    
    for collection in collections:
        print(f"\n📁 {collection.upper()} Collection:")
        print("-" * 30)
        
        dev_stats = get_collection_stats(dev_db, collection)
        prod_stats = get_collection_stats(prod_db, collection)
        
        if 'error' in dev_stats or 'error' in prod_stats:
            print(f"❌ Error analyzing {collection}")
            continue
        
        # Compare totals
        dev_total = dev_stats['total']
        prod_total = prod_stats['total']
        
        print(f"   Dev:  {dev_total:,} documents")
        print(f"   Prod: {prod_total:,} documents")
        
        if dev_total == prod_total:
            print(f"   ✅ Document counts match")
        else:
            diff = prod_total - dev_total
            print(f"   ⚠️  Document count difference: {diff:+d}")
        
        # Compare schema versions
        dev_schema = dev_stats['schema_versions']
        prod_schema = prod_stats['schema_versions']
        
        print(f"   Dev schema versions:  {dev_schema}")
        print(f"   Prod schema versions: {prod_schema}")
        
        if dev_schema == prod_schema:
            print(f"   ✅ Schema versions match")
        else:
            print(f"   ⚠️  Schema version differences detected")
        
        # Compare metadata completeness (for wardrobe)
        if collection == 'wardrobe':
            dev_meta = dev_stats['has_metadata_pct']
            prod_meta = prod_stats['has_metadata_pct']
            dev_emb = dev_stats['has_embeddings_pct']
            prod_emb = prod_stats['has_embeddings_pct']
            
            print(f"   Dev metadata:  {dev_meta:.1f}% complete")
            print(f"   Prod metadata: {prod_meta:.1f}% complete")
            print(f"   Dev embeddings:  {dev_emb:.1f}% complete")
            print(f"   Prod embeddings: {prod_emb:.1f}% complete")
            
            if abs(dev_meta - prod_meta) < 5 and abs(dev_emb - prod_emb) < 5:
                print(f"   ✅ Metadata and embedding completeness match")
            else:
                print(f"   ⚠️  Metadata/embedding completeness differences detected")
    
    print(f"\n🎯 Migration Completeness Summary:")
    print("=" * 50)
    print("✅ Document counts should be similar or prod > dev")
    print("✅ Schema versions should match")
    print("✅ Metadata completeness should be similar")
    print("✅ Embedding completeness should be similar")
    print("\n⚠️  If differences are found, manual review may be needed.")

def manual_comparison_guide():
    """Provide manual comparison instructions."""
    print("\n📋 Manual Comparison Guide")
    print("=" * 50)
    print("If you can't use the automated script, here's how to compare manually:")
    print("\n1. **Document Counts**:")
    print("   - Go to Firebase Console > Firestore")
    print("   - Switch between dev and prod projects")
    print("   - Count documents in each collection")
    print("   - Compare: wardrobe, outfits, users, analytics_events")
    
    print("\n2. **Schema Versioning**:")
    print("   - Sample 10-20 documents from each collection")
    print("   - Check for 'schema_version' field")
    print("   - Verify version is '1.0.0' or current")
    
    print("\n3. **Metadata Completeness**:")
    print("   - Check wardrobe items have 'metadata' field")
    print("   - Verify 'clipEmbedding' or 'embedding' fields exist")
    print("   - Ensure 'visualAttributes' and other fields are present")
    
    print("\n4. **Data Quality**:")
    print("   - Look for test/demo items (should be none in prod)")
    print("   - Check for missing required fields")
    print("   - Verify image URLs are accessible")

if __name__ == "__main__":
    if ENABLED:
        compare_environments()
    else:
        manual_comparison_guide() 