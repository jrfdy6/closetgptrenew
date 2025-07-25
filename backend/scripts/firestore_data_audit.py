#!/usr/bin/env python3
"""
Firestore Data & Model Audit Script
Checks:
- Schema versioning
- Migration completeness (dev vs prod)
- Test/demo data presence
- Metadata completeness
- CLIP embedding normalization
"""

import firebase_admin
from firebase_admin import firestore
from collections import Counter
import numpy as np

# === CONFIG ===
# Set to True to check prod, False for dev
IS_PROD = True
# Path to your service account key (if needed)
# firebase_admin.initialize_app(firebase_admin.credentials.Certificate('path/to/serviceAccount.json'))
if not firebase_admin._apps:
    firebase_admin.initialize_app()

db = firestore.client()

# === SETTINGS ===
COLLECTIONS = ["wardrobe", "outfits", "outfit_feedback", "analytics_events"]
REQUIRED_WARDROBE_METADATA = ["fit", "silhouette", "style", "color_harmony", "pattern", "material", "visualAttributes"]
EMBEDDING_FIELD = "clip_embedding"
SCHEMA_VERSION = "1.0.0"

# === AUDIT FUNCTIONS ===
def check_schema_versioning():
    print("\n[1] Checking schema versioning...")
    missing = []
    for col in COLLECTIONS:
        docs = db.collection(col).limit(10).stream()
        for doc in docs:
            data = doc.to_dict()
            if "schema_version" not in data:
                missing.append((col, doc.id))
    if not missing:
        print("✅ All sampled documents have schema_version field.")
        return True
    else:
        print(f"❌ Missing schema_version in: {missing}")
        return False

def check_test_demo_data():
    print("\n[2] Checking for test/demo wardrobe items...")
    test_items = []
    docs = db.collection("wardrobe").limit(500).stream()
    for doc in docs:
        data = doc.to_dict()
        name = data.get("name", "").lower()
        user = data.get("user_id", "").lower()
        if any(x in name for x in ["test", "demo"]) or any(x in user for x in ["test", "demo"]):
            test_items.append(doc.id)
    if not test_items:
        print("✅ No test/demo wardrobe items found in sample.")
        return True
    else:
        print(f"❌ Found {len(test_items)} test/demo items: {test_items[:5]}{'...' if len(test_items)>5 else ''}")
        return False

def check_metadata_completeness():
    print("\n[3] Checking wardrobe metadata completeness...")
    incomplete = []
    docs = db.collection("wardrobe").limit(200).stream()
    for doc in docs:
        data = doc.to_dict()
        meta = data.get("metadata", {})
        for field in REQUIRED_WARDROBE_METADATA:
            if field not in meta or not meta[field]:
                incomplete.append(doc.id)
                break
    if not incomplete:
        print("✅ All sampled wardrobe items have complete metadata.")
        return True
    else:
        print(f"❌ {len(incomplete)} items missing metadata: {incomplete[:5]}{'...' if len(incomplete)>5 else ''}")
        return False

def check_clip_embedding_normalization():
    print("\n[4] Checking CLIP embedding normalization...")
    unnormalized = []
    missing = []
    docs = db.collection("wardrobe").limit(200).stream()
    for doc in docs:
        data = doc.to_dict()
        emb = data.get(EMBEDDING_FIELD)
        if emb is None:
            missing.append(doc.id)
        elif isinstance(emb, list):
            norm = np.linalg.norm(emb)
            if not (0.99 < norm < 1.01):
                unnormalized.append(doc.id)
    if not missing and not unnormalized:
        print("✅ All sampled wardrobe items have normalized CLIP embeddings.")
        return True
    else:
        if missing:
            print(f"❌ {len(missing)} items missing embeddings: {missing[:5]}{'...' if len(missing)>5 else ''}")
        if unnormalized:
            print(f"❌ {len(unnormalized)} items with unnormalized embeddings: {unnormalized[:5]}{'...' if len(unnormalized)>5 else ''}")
        return False

def check_migration_completeness():
    print("\n[5] Checking migration completeness (dev vs prod)...")
    # This check is only meaningful if you have both dev and prod projects accessible.
    print("ℹ️  Skipping automated migration check (requires both dev and prod access in script). Please compare manually or request a dual-project script.")
    return None

def main():
    print("\n=== Firestore Data & Model Audit ===")
    results = {}
    results['schema_versioning'] = check_schema_versioning()
    results['test_demo_data'] = check_test_demo_data()
    results['metadata_completeness'] = check_metadata_completeness()
    results['clip_embedding_normalization'] = check_clip_embedding_normalization()
    results['migration_completeness'] = check_migration_completeness()
    print("\n=== Audit Summary ===")
    for k, v in results.items():
        if v is True:
            print(f"✅ {k.replace('_',' ').title()}")
        elif v is False:
            print(f"❌ {k.replace('_',' ').title()} (see above)")
        else:
            print(f"ℹ️  {k.replace('_',' ').title()} (manual check or skipped)")
    print("\nDone.")

if __name__ == "__main__":
    main() 