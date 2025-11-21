#!/usr/bin/env python3
"""
Script to reprocess all wardrobe items with alpha matting for background removal.
This ensures all items have processed images (nobg.png, processed.png) for flatlay generation.
"""

import os
import sys
import time
import requests
import multiprocessing
from io import BytesIO
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, TimeoutError
from rembg import remove
from PIL import Image, UnidentifiedImageError
import firebase_admin
from firebase_admin import credentials, firestore, storage

# Try to import numpy, fallback to PIL-only method
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Add parent directories to path
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(BACKEND_DIR / "src"))

# Import worker functions
sys.path.insert(0, str(BACKEND_DIR / "worker"))
from main import (
    _alpha_matting,
    remove_hangers,
    smooth_edges,
    add_material_shadow,
    apply_light_gradient,
    resize_image,
    generate_thumbnail,
    upload_png,
    resolve_material,
    MAX_OUTPUT_WIDTH,
    MAX_OUTPUT_HEIGHT,
    THUMBNAIL_SIZE,
    MAX_IMAGE_BYTES,
    ALPHA_TIMEOUT_SECONDS,
    MATERIAL_SHADOWS,
)

# Configuration
FIRESTORE_COLLECTION = "wardrobe"
FIREBASE_BUCKET_NAME = "closetgptrenew.firebasestorage.app"

# Initialize Firebase
if not firebase_admin._apps:
    firebase_creds = {
        "type": "service_account",
        "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
        "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID"),
        "private_key": os.environ.get("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n"),
        "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
        "client_id": os.environ.get("FIREBASE_CLIENT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.environ.get("FIREBASE_CLIENT_X509_CERT_URL")
    }
    cred = credentials.Certificate(firebase_creds)
    firebase_admin.initialize_app(cred, {
        "storageBucket": FIREBASE_BUCKET_NAME
    })

db = firestore.client()
bucket = storage.bucket()

# Alpha matting executor
os.environ.setdefault("OMP_NUM_THREADS", "1")
alpha_executor = ProcessPoolExecutor(
    max_workers=1,
    mp_context=multiprocessing.get_context("spawn")
)


def check_item_needs_processing(item_id: str, item_data: dict) -> bool:
    """Check if item needs processing with alpha matting.
    Only skip if it was already processed with alpha matting."""
    # Check if item was processed with alpha matting
    processing_mode = item_data.get("processing_mode")
    if processing_mode == "alpha":
        # Already processed with alpha matting, skip
        return False
    
    # If processing_mode is not "alpha" (could be "fast", "preserved", missing, etc.),
    # or if the item doesn't have processed images, it needs reprocessing
    return True


def process_item(item_id: str, item_data: dict) -> dict:
    """Process a single wardrobe item with alpha matting."""
    result = {
        "item_id": item_id,
        "status": "unknown",
        "error": None,
        "time": 0
    }
    
    start_time = time.time()
    
    try:
        # Get original image URL
        original_url = item_data.get("imageUrl") or item_data.get("image_url")
        if not original_url:
            result["status"] = "skipped"
            result["error"] = "No imageUrl"
            return result
        
        # Download original image
        if original_url.startswith("data:"):
            import base64
            encoded = original_url.split(",")[1]
            original_bytes = base64.b64decode(encoded)
        else:
            if not original_url.lower().startswith(("http://", "https://")):
                result["status"] = "skipped"
                result["error"] = "Invalid URL format"
                return result
            response = requests.get(original_url, timeout=30)
            response.raise_for_status()
            original_bytes = response.content
        
        if len(original_bytes) > MAX_IMAGE_BYTES:
            result["status"] = "skipped"
            result["error"] = "Image too large"
            return result
        
        # Open and convert to RGBA
        try:
            original_image = Image.open(BytesIO(original_bytes)).convert("RGBA")
        except UnidentifiedImageError:
            result["status"] = "skipped"
            result["error"] = "Unrecognized image format"
            return result
        
        original_size = original_image.size
        
        # Check if already has transparency
        if HAS_NUMPY:
            alpha_channel = np.array(original_image.split()[3])
            has_transparency = np.any(alpha_channel < 255)
        else:
            # Fallback: check alpha channel extrema
            alpha_channel = original_image.split()[3]
            has_transparency = alpha_channel.getextrema() != (255, 255)
        
        # Upload original if not already uploaded (keep original, don't overwrite)
        original_storage_path = f"items/{item_id}/original.png"
        original_blob = bucket.blob(original_storage_path)
        if not original_blob.exists():
            print(f"📤 {item_id}: Uploading original...")
            upload_png(original_image, original_storage_path)
        else:
            print(f"ℹ️  {item_id}: Original already exists, keeping it")
        
        # Determine material
        material_type = resolve_material(item_data)
        
        if has_transparency:
            print(f"✨ {item_id}: Already has transparency, reprocessing with hanger removal...")
            output_img = original_image
            processing_mode = "preserved"
        else:
            # Run alpha matting
            print(f"🎨 {item_id}: Running alpha matting...")
            original_buffer = BytesIO()
            original_image.save(original_buffer, format="PNG")
            original_bytes_png = original_buffer.getvalue()
            
            try:
                future = alpha_executor.submit(_alpha_matting, original_bytes_png)
                output_bytes = future.result(timeout=ALPHA_TIMEOUT_SECONDS)
                processing_mode = "alpha"
            except TimeoutError:
                future.cancel()
                print(f"⚠️  {item_id}: Alpha matting timed out, using fast mode")
                output_bytes = remove(original_bytes_png)
                processing_mode = "fast"
            except Exception as alpha_exc:
                print(f"⚠️  {item_id}: Alpha matting failed, using fast mode: {alpha_exc}")
                output_bytes = remove(original_bytes_png)
                processing_mode = "fast"
            
            output_img = Image.open(BytesIO(output_bytes)).convert("RGBA")
            print(f"✅ {item_id}: Background removal complete ({processing_mode})")
        
        # Remove hangers
        output_img = remove_hangers(output_img)
        print(f"✅ {item_id}: Hanger removal applied")
        
        # Stylize
        output_img = smooth_edges(output_img)
        output_img = add_material_shadow(output_img, material_type)
        output_img = apply_light_gradient(output_img)
        
        # Resize if necessary
        if output_img.size[0] > MAX_OUTPUT_WIDTH or output_img.size[1] > MAX_OUTPUT_HEIGHT:
            output_img = resize_image(output_img, MAX_OUTPUT_WIDTH, MAX_OUTPUT_HEIGHT)
        
        # Generate thumbnail
        thumbnail_img = generate_thumbnail(output_img)
        
        # Upload processed images (overwriting existing ones with same filenames)
        print(f"📤 {item_id}: Uploading processed images (replacing old ones)...")
        nobg_path = f"items/{item_id}/nobg.png"
        processed_path = f"items/{item_id}/processed.png"
        thumbnail_path = f"items/{item_id}/thumbnail.png"
        
        # Overwrite existing images with new alpha-matted versions
        upload_png(output_img, nobg_path)
        upload_png(output_img, processed_path)
        upload_png(thumbnail_img, thumbnail_path)
        
        print(f"✅ {item_id}: Replaced old processed images with alpha-matted versions")
        
        # Update Firestore with new URLs (same filenames, but updated URLs)
        doc_ref = db.collection(FIRESTORE_COLLECTION).document(item_id)
        nobg_url = bucket.blob(nobg_path).public_url
        processed_url = bucket.blob(processed_path).public_url
        thumbnail_url = bucket.blob(thumbnail_path).public_url
        
        doc_ref.update({
            "backgroundRemovedUrl": processed_url,
            "background_removed_url": processed_url,
            "thumbnailUrl": thumbnail_url,
            "backgroundRemoved": True,
            "processing_status": "done",
            "processing_mode": "alpha",  # Always mark as alpha since we're using alpha matting
        })
        
        total_time = time.time() - start_time
        result["status"] = "success"
        result["time"] = total_time
        print(f"✅ {item_id}: Done in {total_time:.1f}s")
        
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        print(f"❌ {item_id}: Error - {e}")
        import traceback
        traceback.print_exc()
    
    return result


def main():
    """Reprocess all wardrobe items."""
    print("🚀 Starting wardrobe item reprocessing...")
    print("=" * 60)
    
    # Get all wardrobe items
    print("📋 Fetching all wardrobe items...")
    items_ref = db.collection(FIRESTORE_COLLECTION)
    all_items = list(items_ref.stream())
    
    print(f"📊 Found {len(all_items)} total items")
    
    # Filter items that need processing
    items_to_process = []
    for doc in all_items:
        item_id = doc.id
        item_data = doc.to_dict()
        
        if check_item_needs_processing(item_id, item_data):
            items_to_process.append((item_id, item_data))
        else:
            processing_mode = item_data.get("processing_mode", "unknown")
            print(f"⏭️  {item_id}: Already processed with alpha matting (mode: {processing_mode}), skipping")
    
    print(f"🎯 {len(items_to_process)} items need processing")
    print("=" * 60)
    
    if not items_to_process:
        print("✅ All items are already processed!")
        return
    
    # Process items
    results = {
        "success": 0,
        "skipped": 0,
        "error": 0,
        "total_time": 0
    }
    
    start_time = time.time()
    
    for i, (item_id, item_data) in enumerate(items_to_process, 1):
        print(f"\n[{i}/{len(items_to_process)}] Processing {item_id}...")
        result = process_item(item_id, item_data)
        
        results[result["status"]] = results.get(result["status"], 0) + 1
        results["total_time"] += result.get("time", 0)
        
        # Small delay to avoid overwhelming the system
        time.sleep(0.5)
    
    total_time = time.time() - start_time
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 REPROCESSING SUMMARY")
    print("=" * 60)
    print(f"✅ Success: {results['success']}")
    print(f"⏭️  Skipped: {results.get('skipped', 0)}")
    print(f"❌ Errors: {results.get('error', 0)}")
    print(f"⏱️  Total time: {total_time:.1f}s")
    print(f"⏱️  Average per item: {total_time / len(items_to_process):.1f}s")
    print("=" * 60)


if __name__ == "__main__":
    main()

