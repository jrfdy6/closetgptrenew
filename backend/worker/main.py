#!/usr/bin/env python3
"""
Worker Service for Background Image Processing
Runs alpha matting on uploaded wardrobe items in the background
"""

import base64
import os
import time
import requests
from io import BytesIO
from rembg import remove
from PIL import Image, UnidentifiedImageError
from concurrent.futures import ProcessPoolExecutor, TimeoutError
import firebase_admin
from firebase_admin import credentials, firestore, storage

# ----------------------------
# Configuration
# ----------------------------
FIRESTORE_COLLECTION = "wardrobe"  # Using 'wardrobe' collection (not 'closet')
FIREBASE_BUCKET_NAME = "closetgptrenew.firebasestorage.app"

# Worker tuning parameters
MAX_RETRIES = 3  # Retry failed items up to 3 times
BATCH_SIZE = 1   # Sequential processing to manage memory usage
POLL_INTERVAL = 5  # Check for new items every 5 seconds
MAX_OUTPUT_WIDTH = 1200  # Resize large images to save bandwidth
MAX_OUTPUT_HEIGHT = 1200
THUMBNAIL_SIZE = 512  # Generate thumbnails for fast loading with good detail
MAX_IMAGE_SIZE_MB = 5
MAX_IMAGE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024
ALPHA_TIMEOUT_SECONDS = 240

alpha_executor = ProcessPoolExecutor(max_workers=1)

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


def decode_data_uri(data_uri: str) -> bytes:
    if not data_uri.startswith("data:image/"):
        raise ValueError("Unsupported data URI")
    try:
        header, encoded = data_uri.split(",", 1)
    except ValueError as exc:
        raise ValueError("Malformed data URI") from exc
    return base64.b64decode(encoded)


def upload_png(image: Image.Image, blob_path: str) -> str:
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    blob = bucket.blob(blob_path)
    blob.upload_from_file(buffer, content_type="image/png")
    blob.make_public()
    return blob.public_url


def mark_failure(doc_id: str, status: str, error: str, retry_count=None):
    update_payload = {
        "processing_status": status,
        "processing_error": error,
    }
    if retry_count is not None:
        update_payload["processing_retry_count"] = retry_count
    db.collection(FIRESTORE_COLLECTION).document(doc_id).update(update_payload)
    print(f"❌ {doc_id}: {error}")


metrics = {
    "processed": 0,
    "failed": 0,
    "skipped": 0,
}


def _alpha_matting(bytes_data: bytes) -> bytes:
    return remove(
        bytes_data,
        alpha_matting=True,
        alpha_matting_foreground_threshold=240,
        alpha_matting_background_threshold=10,
        alpha_matting_erode_size=10,
    )


def process_item(doc_id, data):
    """Process a single wardrobe item with alpha matting, retry logic, and optimizations"""
    original_url = data.get("imageUrl") or data.get("image_url")
    if not original_url:
        return
    
    retry_count = data.get("processing_retry_count", 0)
    if retry_count >= MAX_RETRIES:
        print(f"⛔ {doc_id}: Max retries reached, skipping")
        return

    doc_ref = db.collection(FIRESTORE_COLLECTION).document(doc_id)

    try:
        start_time = time.time()

        # 1. Fetch or decode the original image bytes
        if original_url.startswith("data:"):
            original_bytes = decode_data_uri(original_url)
            if len(original_bytes) > MAX_IMAGE_BYTES:
                mark_failure(doc_id, "skipped_large_data_uri", "Data URI exceeds 5MB limit", retry_count)
                metrics["skipped"] += 1
                return
        else:
            if not original_url.lower().startswith(("http://", "https://")):
                mark_failure(doc_id, "failed", "Unsupported image URL format", retry_count)
                metrics["failed"] += 1
                return
            response = requests.get(original_url, timeout=30)
            response.raise_for_status()
            original_bytes = response.content
            if len(original_bytes) > MAX_IMAGE_BYTES:
                mark_failure(doc_id, "failed", "Original image exceeds 5MB limit", retry_count)
                metrics["failed"] += 1
                return

        # 2. Open image and normalize to RGBA
        try:
            original_image = Image.open(BytesIO(original_bytes)).convert("RGBA")
        except UnidentifiedImageError:
            mark_failure(doc_id, "failed", "Unrecognized image format", retry_count)
            metrics["failed"] += 1
            return

        original_size = original_image.size

        # 3. Store original image in standard location
        print(f"📤 {doc_id}: Uploading original ({original_size[0]}x{original_size[1]})...")
        original_storage_path = f"items/{doc_id}/original.png"
        original_storage_url = upload_png(original_image, original_storage_path)

        # 4. Run background removal
        print(f"🎨 {doc_id}: Running alpha matting (timeout {ALPHA_TIMEOUT_SECONDS}s)...")
        original_buffer = BytesIO()
        original_image.save(original_buffer, format="PNG")
        original_bytes_png = original_buffer.getvalue()

        try:
            future = alpha_executor.submit(_alpha_matting, original_bytes_png)
            output_bytes = future.result(timeout=ALPHA_TIMEOUT_SECONDS)
            alpha_mode = "alpha"
        except TimeoutError:
            future.cancel()
            print(f"⚠️  {doc_id}: Alpha matting timed out after {ALPHA_TIMEOUT_SECONDS}s, falling back to fast mode")
            output_bytes = remove(original_bytes_png)
            alpha_mode = "fast"
        except Exception as alpha_exc:
            print(f"⚠️  {doc_id}: Alpha matting failed ({alpha_exc}), falling back to fast mode")
            output_bytes = remove(original_bytes_png)
            alpha_mode = "fast"

        output_img = Image.open(BytesIO(output_bytes)).convert("RGBA")
        processing_time = time.time() - start_time
        print(f"✅ {doc_id}: Background removal complete using {alpha_mode} mode ({processing_time:.1f}s)")

        # 5. Resize processed image if necessary
        if output_img.size[0] > MAX_OUTPUT_WIDTH or output_img.size[1] > MAX_OUTPUT_HEIGHT:
            output_img = resize_image(output_img, MAX_OUTPUT_WIDTH, MAX_OUTPUT_HEIGHT)

        # 6. Generate thumbnail (object-contain)
        thumbnail_img = output_img.copy()
        thumbnail_img.thumbnail((THUMBNAIL_SIZE, THUMBNAIL_SIZE), Image.Resampling.LANCZOS)

        # 7. Upload processed and thumbnail images
        print(f"📤 {doc_id}: Uploading processed image...")
        processed_storage_path = f"items/{doc_id}/nobg.png"
        processed_url = upload_png(output_img, processed_storage_path)

        print(f"📤 {doc_id}: Uploading thumbnail...")
        thumbnail_storage_path = f"items/{doc_id}/thumb.png"
        thumbnail_url = upload_png(thumbnail_img, thumbnail_storage_path)

        # 8. Update Firestore document with new URLs and status
        doc_ref.update({
            "imageUrl": original_storage_url,
            "backgroundRemovedUrl": processed_url,
            "thumbnailUrl": thumbnail_url,
            "backgroundRemoved": True,
            "processing_status": "done",
            "processing_error": None,
            "processing_retry_count": 0,
            "processing_last_error": None,
            "processing_time": processing_time,
            "original_size": f"{original_size[0]}x{original_size[1]}",
            "processed_size": f"{output_img.size[0]}x{output_img.size[1]}"
        })

        metrics["processed"] += 1
        print(f"✅ {doc_id}: Done ({processing_time:.1f}s)")

    except requests.RequestException as exc:
        doc_ref.update({
            "processing_retry_count": retry_count + 1,
            "processing_last_error": f"Network: {str(exc)}"
        })
        print(f"⚠️  {doc_id}: Network error - {str(exc)[:80]}")
    except Exception as exc:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ {doc_id}: Error - {str(exc)[:100]}")
        print(f"   Traceback: {error_details[:200]}...")
        mark_failure(doc_id, "failed", str(exc), retry_count + 1)
        metrics["failed"] += 1


# ----------------------------
# Worker Loop
# ----------------------------
def run_worker():
    """Main worker loop - checks for pending items and processes them"""
    print("🔥 Worker started. Listening for new images...")
    print(f"📊 Configuration:")
    print(f"   Firebase Project: {firebase_creds.get('project_id')}")
    print(f"   Collection: {FIRESTORE_COLLECTION}")
    print(f"   Batch size: {BATCH_SIZE} items")
    print(f"   Poll interval: {POLL_INTERVAL}s")
    print(f"   Max retries: {MAX_RETRIES}")
    print(f"   Max output size: {MAX_OUTPUT_WIDTH}x{MAX_OUTPUT_HEIGHT}")
    print(f"   Thumbnail size: {THUMBNAIL_SIZE}x{THUMBNAIL_SIZE}")
    print()
    
    loop_count = 0
    
    while True:
        try:
            loop_count += 1
            
            # Query items still pending processing
            pending = (
                db.collection(FIRESTORE_COLLECTION)
                .where("processing_status", "==", "pending")
                .limit(BATCH_SIZE)
                .stream()
            )
            
            pending_list = list(pending)
            
            if pending_list:
                print(f"🎯 Found {len(pending_list)} pending items")
                
                for doc in pending_list:
                    process_item(doc.id, doc.to_dict())
                    time.sleep(1)  # Small delay between items to reduce memory spikes
                
                print(
                    "📊 Metrics: processed={processed} failed={failed} skipped={skipped}"
                    .format(**metrics)
                )
            else:
                # No items to process - log every 5 minutes
                if loop_count % (300 // POLL_INTERVAL) == 1:  # Log every 5 minutes
                    print(
                        "💤 No pending items. (processed={processed}, failed={failed}, skipped={skipped})"
                        .format(**metrics)
                    )
                time.sleep(POLL_INTERVAL)
        
        except Exception as e:
            print(f"⚠️  Worker loop error: {str(e)[:100]}")
            metrics["failed"] += 1
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

