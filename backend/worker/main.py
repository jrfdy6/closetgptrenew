#!/usr/bin/env python3
"""
Worker Service for Background Image Processing
Runs alpha matting on uploaded wardrobe items in the background
"""

import time
import requests
import tempfile
import os
import json
from io import BytesIO
from rembg import remove
from PIL import Image
import firebase_admin
from firebase_admin import credentials, firestore, storage

# ----------------------------
# Configuration
# ----------------------------
FIRESTORE_COLLECTION = "wardrobe"  # Using 'wardrobe' collection (not 'closet')
FIREBASE_BUCKET_NAME = "closetgptrenew.firebasestorage.app"

# Worker tuning parameters
MAX_RETRIES = 3  # Retry failed items up to 3 times
BATCH_SIZE = 2   # Process 2 items at a time (balances speed vs memory)
POLL_INTERVAL = 5  # Check for new items every 5 seconds
MAX_OUTPUT_WIDTH = 1200  # Resize large images to save bandwidth
MAX_OUTPUT_HEIGHT = 1200
THUMBNAIL_SIZE = 300  # Generate thumbnails for fast loading

# Initialize Firebase Admin SDK
print("🔥 Initializing Firebase Admin SDK...")

# Build credentials from environment variables
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

# Initialize Firebase
cred = credentials.Certificate(firebase_creds)
firebase_admin.initialize_app(cred, {
    "storageBucket": FIREBASE_BUCKET_NAME
})

# Get Firebase clients
db = firestore.client()
bucket = storage.bucket()

print(f"✅ Connected to Firestore collection: {FIRESTORE_COLLECTION}")
print(f"✅ Connected to Storage bucket: {bucket.name}")


# ----------------------------
# Image Processing Function
# ----------------------------
def resize_image(img: Image.Image, max_width: int, max_height: int) -> Image.Image:
    """Resize image while maintaining aspect ratio"""
    width, height = img.size
    
    # Calculate scaling factor
    scale = min(max_width / width, max_height / height, 1.0)
    
    if scale < 1.0:
        new_width = int(width * scale)
        new_height = int(height * scale)
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    return img


def create_thumbnail(img: Image.Image, size: int) -> Image.Image:
    """Create square thumbnail"""
    img.thumbnail((size, size), Image.Resampling.LANCZOS)
    return img


def process_item(doc_id, data):
    """Process a single wardrobe item with alpha matting, retry logic, and optimizations"""
    print(f"📸 Processing {doc_id}...")
    
    original_url = data.get("imageUrl") or data.get("image_url")
    if not original_url:
        print(f"  ⚠️  No original image found for {doc_id}")
        return
    
    # Check retry count
    retry_count = data.get("processing_retry_count", 0)
    if retry_count >= MAX_RETRIES:
        print(f"  ⛔ Max retries ({MAX_RETRIES}) reached for {doc_id}, skipping")
        return
    
    try:
        # 1. Download image with retry
        print(f"  📥 Downloading image (retry #{retry_count})...")
        response = requests.get(original_url, timeout=30)
        response.raise_for_status()
        input_img = Image.open(BytesIO(response.content)).convert("RGBA")
        original_size = input_img.size
        print(f"  ✅ Downloaded image: {original_size}")
        
        # 2. Alpha matting (the heavy part - takes 5-10 seconds)
        print(f"  🎨 Running alpha matting...")
        start_time = time.time()
        output_img = remove(
            input_img,
            alpha_matting=True,
            alpha_matting_foreground_threshold=240,
            alpha_matting_background_threshold=10,
            alpha_matting_erode_size=10
        )
        processing_time = time.time() - start_time
        print(f"  ✅ Background removed in {processing_time:.1f}s")
        
        # 3. Resize if too large (save bandwidth & storage)
        if output_img.size[0] > MAX_OUTPUT_WIDTH or output_img.size[1] > MAX_OUTPUT_HEIGHT:
            print(f"  🔧 Resizing from {output_img.size} to fit {MAX_OUTPUT_WIDTH}x{MAX_OUTPUT_HEIGHT}")
            output_img = resize_image(output_img, MAX_OUTPUT_WIDTH, MAX_OUTPUT_HEIGHT)
            print(f"  ✅ Resized to {output_img.size}")
        
        # 4. Generate thumbnail for fast loading
        thumbnail_img = output_img.copy()
        thumbnail_img.thumbnail((THUMBNAIL_SIZE, THUMBNAIL_SIZE), Image.Resampling.LANCZOS)
        
        # 5. Save both full and thumbnail
        tmp_files = []
        try:
            # Save full image
            tmp_full = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            output_img.save(tmp_full.name, "PNG", optimize=True)
            tmp_files.append(tmp_full.name)
            
            # Save thumbnail
            tmp_thumb = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            thumbnail_img.save(tmp_thumb.name, "PNG", optimize=True)
            tmp_files.append(tmp_thumb.name)
            
            # 6. Upload full image to Firebase Storage
            print(f"  📤 Uploading processed image ({output_img.size})...")
            blob_path = f"wardrobe/processed/{doc_id}_clean.png"
            blob = bucket.blob(blob_path)
            blob.upload_from_filename(tmp_full.name)
            blob.make_public()
            processed_url = blob.public_url
            print(f"  ✅ Uploaded full image")
            
            # 7. Upload thumbnail
            print(f"  📤 Uploading thumbnail ({thumbnail_img.size})...")
            thumb_path = f"wardrobe/thumbnails/{doc_id}_thumb.png"
            thumb_blob = bucket.blob(thumb_path)
            thumb_blob.upload_from_filename(tmp_thumb.name)
            thumb_blob.make_public()
            thumbnail_url = thumb_blob.public_url
            print(f"  ✅ Uploaded thumbnail")
            
            # 8. Update Firestore silently (user's UI auto-updates)
            print(f"  💾 Updating Firestore document: {FIRESTORE_COLLECTION}/{doc_id}")
            update_data = {
                "backgroundRemovedUrl": processed_url,
                "thumbnailUrl": thumbnail_url,
                "backgroundRemoved": True,
                "processing_status": "done",
                "processing_time": processing_time,
                "original_size": f"{original_size[0]}x{original_size[1]}",
                "processed_size": f"{output_img.size[0]}x{output_img.size[1]}"
            }
            print(f"  📝 Update payload: {update_data}")
            
            # Perform the update with explicit error handling
            try:
                doc_ref = db.collection(FIRESTORE_COLLECTION).document(doc_id)
                doc_ref.update(update_data)
                print(f"  ✅ Firestore update call completed")
                
                # VERIFY the update worked by reading back
                print(f"  🔍 Verifying Firestore update...")
                updated_doc = doc_ref.get()
                if updated_doc.exists:
                    updated_data = updated_doc.to_dict()
                    print(f"  ✅ Verified: processing_status = {updated_data.get('processing_status')}")
                    print(f"  ✅ Verified: backgroundRemovedUrl = {updated_data.get('backgroundRemovedUrl')[:80] if updated_data.get('backgroundRemovedUrl') else 'None'}...")
                else:
                    print(f"  ⚠️  WARNING: Document {doc_id} does not exist after update!")
                    raise Exception(f"Document {doc_id} not found in Firestore")
                    
            except Exception as firestore_error:
                print(f"  ❌ FIRESTORE UPDATE FAILED: {firestore_error}")
                import traceback
                print(f"  📋 Traceback: {traceback.format_exc()}")
                raise  # Re-raise to trigger retry logic
            
            print(f"✅ COMPLETE: {doc_id} - Image auto-upgraded in UI ({processing_time:.1f}s)")
            
        finally:
            # Cleanup temp files
            for tmp_file in tmp_files:
                if os.path.exists(tmp_file):
                    os.unlink(tmp_file)
    
    except requests.RequestException as e:
        # Network error - retry
        print(f"⚠️  Network error for {doc_id}: {e}")
        db.collection(FIRESTORE_COLLECTION).document(doc_id).update({
            "processing_retry_count": retry_count + 1,
            "processing_last_error": f"Network: {str(e)}"
        })
    except Exception as e:
        # Other error - log and retry
        print(f"❌ Error processing {doc_id}: {e}")
        import traceback
        error_trace = traceback.format_exc()
        print(f"   Stack trace: {error_trace[:200]}...")
        
        # Update with retry count or mark as failed
        if retry_count + 1 >= MAX_RETRIES:
            db.collection(FIRESTORE_COLLECTION).document(doc_id).update({
                "processing_status": "failed",
                "processing_error": str(e),
                "processing_retry_count": retry_count + 1
            })
            print(f"  ⛔ Max retries reached, marked as failed")
        else:
            db.collection(FIRESTORE_COLLECTION).document(doc_id).update({
                "processing_retry_count": retry_count + 1,
                "processing_last_error": str(e)
            })
            print(f"  🔄 Will retry (attempt {retry_count + 2}/{MAX_RETRIES})")


# ----------------------------
# Worker Loop
# ----------------------------
def run_worker():
    """Main worker loop - checks for pending items and processes them"""
    print("🔥 Worker started. Listening for new images...")
    print(f"📊 Configuration:")
    print(f"   Collection: {FIRESTORE_COLLECTION}")
    print(f"   Batch size: {BATCH_SIZE} items")
    print(f"   Poll interval: {POLL_INTERVAL}s")
    print(f"   Max retries: {MAX_RETRIES}")
    print(f"   Max output size: {MAX_OUTPUT_WIDTH}x{MAX_OUTPUT_HEIGHT}")
    print(f"   Thumbnail size: {THUMBNAIL_SIZE}x{THUMBNAIL_SIZE}")
    print()
    
    loop_count = 0
    total_processed = 0
    total_failed = 0
    
    while True:
        try:
            loop_count += 1
            
            # Query items still pending processing (using configurable batch size)
            pending = (
                db.collection(FIRESTORE_COLLECTION)
                .where("processing_status", "==", "pending")
                .limit(BATCH_SIZE)
                .stream()
            )
            
            pending_list = list(pending)
            
            if pending_list:
                print(f"🎯 Loop #{loop_count}: Found {len(pending_list)} pending items")
                
                for doc in pending_list:
                    process_item(doc.id, doc.to_dict())
                    total_processed += 1
                    time.sleep(1)  # Small delay between items to reduce memory spikes
                
                print(f"📊 Stats: {total_processed} processed, {total_failed} failed")
                print()
            else:
                # No items to process - log periodically
                if loop_count % (60 // POLL_INTERVAL) == 1:  # Log every minute
                    print(f"💤 Loop #{loop_count}: No pending items. Waiting... (Processed: {total_processed}, Failed: {total_failed})")
                time.sleep(POLL_INTERVAL)
        
        except Exception as e:
            print(f"⚠️  Worker encountered error in loop: {e}")
            import traceback
            print(f"   {traceback.format_exc()[:300]}...")
            total_failed += 1
            time.sleep(POLL_INTERVAL)


# ----------------------------
# Entry Point
# ----------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 ClosetGPT Background Image Processor")
    print("=" * 60)
    print()
    run_worker()

