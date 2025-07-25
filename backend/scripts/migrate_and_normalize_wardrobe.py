import os
import sys
import time
import firebase_admin
from firebase_admin import firestore, initialize_app
import numpy as np
from typing import Dict, Any
from PIL import Image
import requests

# Initialize Firebase
if not firebase_admin._apps:
    initialize_app()
db = firestore.client()

# Import enhancement and embedding utilities
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.services.metadata_enhancement_service import MetadataEnhancementService
from src.utils.clip_embedding import embedder

SCHEMA_VERSION = 2
TEST_USER_IDS = [
    'testuser', 'demo', 'test', 'dev', 'sample', 'dummy', 'test@example.com'
]
TEST_ITEM_KEYWORDS = [
    'test', 'demo', 'sample', 'dummy', 'blue shirt', 'test item'
]

metadata_service = MetadataEnhancementService()

def is_test_item(item: Dict[str, Any]) -> bool:
    name = item.get('name', '').lower()
    user_id = item.get('userId', '').lower()
    if any(uid in user_id for uid in TEST_USER_IDS):
        return True
    if any(kw in name for kw in TEST_ITEM_KEYWORDS):
        return True
    return False

def get_clip_embedding_from_url(image_url: str):
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content)).convert('RGB')
        embedding = embedder.get_embedding(image)
        return embedding
    except Exception as e:
        print(f"[ERROR] Failed to get embedding for {image_url}: {e}")
        return None

def migrate_and_normalize():
    wardrobe_ref = db.collection('wardrobe')
    docs = list(wardrobe_ref.stream())
    total = len(docs)
    removed = 0
    updated = 0
    enhanced_count = 0
    normalized = 0
    errors = 0

    print(f"Found {total} wardrobe items.")
    for doc in docs:
        item = doc.to_dict()
        item_id = doc.id
        try:
            # Remove test/demo items
            if is_test_item(item):
                doc.reference.delete()
                removed += 1
                print(f"[REMOVED] {item.get('name', '')} ({item_id})")
                continue

            update_data = {}
            # Add/update schemaVersion
            if item.get('schemaVersion') != SCHEMA_VERSION:
                update_data['schemaVersion'] = SCHEMA_VERSION

            # Enhance metadata
            enhanced = False
            if metadata_service._needs_enhancement(item):
                enhanced_data = metadata_service._enhance_item_metadata(item)
                if enhanced_data:
                    update_data.update(enhanced_data)
                    enhanced = True
                    enhanced_count += 1

            # Normalize/store CLIP embedding
            embedding = item.get('clipEmbedding')
            if embedding is not None:
                arr = np.array(embedding, dtype=np.float32)
                norm = np.linalg.norm(arr)
                if not np.isclose(norm, 1.0):
                    arr = arr / (norm if norm > 0 else 1)
                    update_data['clipEmbedding'] = arr.tolist()
                    normalized += 1
            else:
                # Compute embedding if missing (requires imageUrl)
                image_url = item.get('imageUrl')
                if image_url:
                    from io import BytesIO
                    emb = get_clip_embedding_from_url(image_url)
                    if emb is not None:
                        update_data['clipEmbedding'] = emb
                        normalized += 1

            if update_data:
                doc.reference.update(update_data)
                updated += 1
                print(f"[UPDATED] {item.get('name', '')} ({item_id}) | Enhanced: {enhanced}")
        except Exception as e:
            print(f"[ERROR] {item_id}: {e}")
            errors += 1

    print("\n--- Migration Summary ---")
    print(f"Total items: {total}")
    print(f"Removed test/demo: {removed}")
    print(f"Updated: {updated}")
    print(f"Enhanced metadata: {enhanced_count}")
    print(f"Normalized embeddings: {normalized}")
    print(f"Errors: {errors}")

if __name__ == "__main__":
    migrate_and_normalize() 