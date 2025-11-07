#!/usr/bin/env python3
"""
Worker Service for Background Image Processing
Runs alpha matting on uploaded wardrobe items in the background
"""

import base64
import os
import time
import requests
import numpy as np
from io import BytesIO
from rembg import remove
from PIL import Image, UnidentifiedImageError, ImageFilter, ImageDraw
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


MATERIAL_SHADOWS = {
    "silk": {"blur": 3, "opacity": 0.06},
    "puffer": {"blur": 7, "opacity": 0.18},
    "cotton": {"blur": 5, "opacity": 0.12},
    "denim": {"blur": 6, "opacity": 0.10},
    "knit": {"blur": 5, "opacity": 0.14},
    "wool": {"blur": 6, "opacity": 0.16},
}

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
    "flat_lay_processed": 0,
    "flat_lay_failed": 0,
    "flat_lay_skipped": 0,
}


def _alpha_matting(bytes_data: bytes) -> bytes:
    return remove(
        bytes_data,
        alpha_matting=True,
        alpha_matting_foreground_threshold=240,
        alpha_matting_background_threshold=10,
        alpha_matting_erode_size=10,
    )


def smooth_edges(img: Image.Image, edge_blur_radius: float = 1.5) -> Image.Image:
    r, g, b, a = img.split()
    a = a.filter(ImageFilter.MinFilter(3))
    a = a.filter(ImageFilter.MaxFilter(3))
    a = a.filter(ImageFilter.GaussianBlur(edge_blur_radius))
    a = a.point(lambda p: min(255, int(p * 1.05)))
    return Image.merge("RGBA", (r, g, b, a))


def add_material_shadow(img: Image.Image, material: str = "cotton") -> Image.Image:
    params = MATERIAL_SHADOWS.get(material, MATERIAL_SHADOWS["cotton"])
    alpha = img.split()[3]
    shadow = alpha.filter(ImageFilter.GaussianBlur(params["blur"]))
    shadow_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    shadow_layer.paste((0, 0, 0, int(255 * params["opacity"])), (0, 0), shadow)
    return Image.alpha_composite(shadow_layer, img)


def apply_light_gradient(img: Image.Image) -> Image.Image:
    width, height = img.size
    gradient = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(gradient)
    draw.ellipse((-width * 0.3, -height * 0.3, width * 1.3, height * 1.3), fill=128)
    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
    overlay.putalpha(gradient)
    return Image.alpha_composite(img, overlay)


def generate_thumbnail(img: Image.Image, size: tuple[int, int] = (THUMBNAIL_SIZE, THUMBNAIL_SIZE)) -> Image.Image:
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    img_ratio = img.width / max(1, img.height)
    canvas_ratio = size[0] / max(1, size[1])

    if img_ratio > canvas_ratio:
        new_width = size[0]
        new_height = int(size[0] / img_ratio)
    else:
        new_height = size[1]
        new_width = int(size[1] * img_ratio)

    resized = img.resize((max(1, new_width), max(1, new_height)), Image.LANCZOS)
    x_offset = (size[0] - resized.width) // 2
    y_offset = (size[1] - resized.height) // 2
    canvas.paste(resized, (x_offset, y_offset), resized)
    return canvas


def resolve_material(data: dict) -> str:
    candidates = []
    metadata = data.get("metadata") or {}
    analysis = data.get("analysis") or {}

    candidates.append(metadata.get("material"))
    candidates.append(metadata.get("fabric"))
    visual = metadata.get("visualAttributes") or metadata.get("visual_attributes") or {}
    candidates.append(visual.get("material"))

    analysis_meta = (analysis.get("metadata") or {}).get("visualAttributes") or {}
    candidates.append(analysis_meta.get("material"))

    for candidate in candidates:
        if candidate:
            key = str(candidate).lower()
            if key in MATERIAL_SHADOWS:
                return key
    return "cotton"


# ----------------------------
# Premium Flat Lay Functions
# ----------------------------

def generate_radial_background(size: tuple[int, int] = (1200, 1200), base_color: tuple[int, int, int] = (245, 245, 245), center_brightness: int = 255) -> Image.Image:
    """Soft radial gradient for studio effect"""
    width, height = size
    bg = Image.new("RGBA", size, base_color + (255,))
    draw = ImageDraw.Draw(bg)
    for i in range(width // 2, 0, -1):
        alpha = int((1 - i / (width / 2)) * (255 - center_brightness / 255))
        draw.ellipse(
            (width / 2 - i, height / 2 - i, width / 2 + i, height / 2 + i),
            fill=(255, 255, 255, alpha)
        )
    return bg


def normalize_item_for_flatlay(img: Image.Image, max_dim: int = 400) -> Image.Image:
    """Scale item to max width/height while preserving aspect ratio"""
    w, h = img.size
    scale = min(max_dim / w, max_dim / h, 1.0)
    new_size = (int(w * scale), int(h * scale))
    return img.resize(new_size, Image.Resampling.LANCZOS)


def premium_flatlay(items: list[dict], canvas_size: tuple[int, int] = (1200, 1200)) -> Image.Image:
    """
    Compose multiple items into a polished flat lay.
    
    items: list of dicts with keys:
        - "img": PIL.Image (RGBA)
        - "material": str (optional, defaults to "cotton")
    """
    import math
    import random
    
    canvas = generate_radial_background(size=canvas_size)
    num_items = len(items)
    if num_items == 0:
        return canvas

    # Layout: staggered grid with rotation + overlapping
    margin = 40
    cols = max(1, math.ceil(math.sqrt(num_items)))
    rows = math.ceil(num_items / cols)
    cell_w = (canvas_size[0] - margin * 2) / cols
    cell_h = (canvas_size[1] - margin * 2) / rows
    positions = []
    angles = []

    for idx, item in enumerate(items):
        col = idx % cols
        row = idx // cols
        x = margin + int(col * cell_w)
        y = margin + int(row * cell_h)
        positions.append((x, y))
        angles.append(random.uniform(-5, 5))

    for idx, item in enumerate(items):
        img = normalize_item_for_flatlay(item["img"])
        img = smooth_edges(img)
        img = add_material_shadow(img, material=item.get("material", "cotton"))
        rotated = img.rotate(angles[idx], expand=True)
        x, y = positions[idx]
        paste_x = x + (cell_w - rotated.width) // 2
        paste_y = y + (cell_h - rotated.height) // 2
        canvas.alpha_composite(rotated, (int(paste_x), int(paste_y)))

    return canvas


def create_premium_flatlay(outfit_items: list[dict], outfit_id: str) -> str:
    """
    Create a premium flat lay from outfit items.
    
    outfit_items: list of dicts with keys:
        - 'backgroundRemovedUrl': str (Firebase URL) or 'processed.png' path
        - 'material': str (optional)
        - 'id': str (item ID for fallback lookup)
    
    Returns: Firebase Storage URL of the flat lay image
    """
    processed_images = []
    
    for item in outfit_items:
        # Try backgroundRemovedUrl first, then fallback to processed.png path
        image_url = item.get('backgroundRemovedUrl')
        if not image_url:
            # Fallback: construct path from item ID
            item_id = item.get('id')
            if item_id:
                image_url = f"https://storage.googleapis.com/{FIREBASE_BUCKET_NAME}/items/{item_id}/processed.png"
            else:
                print(f"⚠️  Skipping item in flat lay: no image URL or ID")
                continue
        
        try:
            # Download image
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content)).convert("RGBA")
            
            # Get material type
            material = item.get("material") or resolve_material(item) or "cotton"
            
            processed_images.append({
                "img": img,
                "material": material
            })
        except Exception as e:
            print(f"⚠️  Failed to load item image for flat lay: {e}")
            continue
    
    if not processed_images:
        print(f"❌ No valid images for flat lay {outfit_id}")
        return None
    
    # Generate flat lay canvas
    canvas = premium_flatlay(processed_images)
    
    # Upload to Firebase Storage
    path = f"flat_lays/outfit_{outfit_id}.png"
    buffer = BytesIO()
    canvas.save(buffer, format="PNG")
    buffer.seek(0)
    blob = bucket.blob(path)
    blob.upload_from_file(buffer, content_type="image/png")
    blob.make_public()
    flat_lay_url = blob.public_url
    
    print(f"✅ Created premium flat lay for outfit {outfit_id}: {flat_lay_url}")
    return flat_lay_url


def process_outfit_flat_lay(doc_id: str, data: dict):
    """Generate and store premium flat lay for an outfit document."""
    doc_ref = db.collection('outfits').document(doc_id)
    try:
        items = data.get('items') or []
        if not items:
            doc_ref.update({
                'flat_lay_status': 'failed',
                'flat_lay_error': 'No items available for flat lay',
                'metadata.flat_lay_status': 'failed',
                'metadata.flat_lay_error': 'No items available for flat lay',
                'flat_lay_updated_at': firestore.SERVER_TIMESTAMP,
            })
            metrics['flat_lay_failed'] += 1
            print(f"❌ Outfit {doc_id}: No items available for flat lay")
            return

        flat_lay_url = create_premium_flatlay(items, doc_id)
        if not flat_lay_url:
            raise Exception('Flat lay generation returned no URL')

        doc_ref.update({
            'flat_lay_status': 'done',
            'flat_lay_url': flat_lay_url,
            'flat_lay_error': None,
            'flat_lay_updated_at': firestore.SERVER_TIMESTAMP,
            'metadata.flat_lay_status': 'done',
            'metadata.flat_lay_url': flat_lay_url,
            'metadata.flat_lay_error': None,
        })
        metrics['flat_lay_processed'] += 1
        print(f"🎨 Outfit {doc_id}: Flat lay ready")

    except Exception as exc:
        error_message = str(exc)
        doc_ref.update({
            'flat_lay_status': 'failed',
            'flat_lay_error': error_message,
            'flat_lay_updated_at': firestore.SERVER_TIMESTAMP,
            'metadata.flat_lay_status': 'failed',
            'metadata.flat_lay_error': error_message,
        })
        metrics['flat_lay_failed'] += 1
        print(f"❌ Outfit {doc_id}: Flat lay generation failed - {error_message}")

# ----------------------------
# Wardrobe Item Processing
# ----------------------------

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

        # 3. Check if image already has transparency (skip rembg if it does)
        alpha_channel = np.array(original_image.split()[3])  # Get alpha channel
        has_transparency = np.any(alpha_channel < 255)  # Check if any pixel is not fully opaque

        # 4. Store original image in standard location
        print(f"📤 {doc_id}: Uploading original ({original_size[0]}x{original_size[1]})...")
        original_storage_path = f"items/{doc_id}/original.png"
        original_storage_url = upload_png(original_image, original_storage_path)

        # Determine material for styling
        material_type = resolve_material(data)

        if has_transparency:
            print(f"✨ {doc_id}: Image already has transparency, preserving original")
            output_img = original_image
            processing_mode = "preserved"
        else:
            # Run background removal
            print(f"🎨 {doc_id}: Running alpha matting (timeout {ALPHA_TIMEOUT_SECONDS}s)...")
            original_buffer = BytesIO()
            original_image.save(original_buffer, format="PNG")
            original_bytes_png = original_buffer.getvalue()

            try:
                future = alpha_executor.submit(_alpha_matting, original_bytes_png)
                output_bytes = future.result(timeout=ALPHA_TIMEOUT_SECONDS)
                processing_mode = "alpha"
            except TimeoutError:
                future.cancel()
                print(f"⚠️  {doc_id}: Alpha matting timed out after {ALPHA_TIMEOUT_SECONDS}s, falling back to fast mode")
                output_bytes = remove(original_bytes_png)
                processing_mode = "fast"
            except Exception as alpha_exc:
                print(f"⚠️  {doc_id}: Alpha matting failed ({alpha_exc}), falling back to fast mode")
                output_bytes = remove(original_bytes_png)
                processing_mode = "fast"

            output_img = Image.open(BytesIO(output_bytes)).convert("RGBA")
            print(f"✅ {doc_id}: Background removal complete using {processing_mode} mode")

        # 6. Stylize silhouette for cohesive flatlay aesthetics
        output_img = smooth_edges(output_img)
        output_img = add_material_shadow(output_img, material_type)
        output_img = apply_light_gradient(output_img)

        # 7. Resize processed image if necessary
        if output_img.size[0] > MAX_OUTPUT_WIDTH or output_img.size[1] > MAX_OUTPUT_HEIGHT:
            output_img = resize_image(output_img, MAX_OUTPUT_WIDTH, MAX_OUTPUT_HEIGHT)

        # 8. Generate thumbnail (object-contain)
        thumbnail_img = generate_thumbnail(output_img)

        # 9. Upload processed and thumbnail images
        print(f"📤 {doc_id}: Uploading processed image...")
        processed_storage_path = f"items/{doc_id}/processed.png"
        processed_url = upload_png(output_img, processed_storage_path)

        print(f"📤 {doc_id}: Uploading thumbnail...")
        thumbnail_storage_path = f"items/{doc_id}/thumbnail.png"
        thumbnail_url = upload_png(thumbnail_img, thumbnail_storage_path)

        total_time = time.time() - start_time

        # 10. Update Firestore document with new URLs and status
        doc_ref.update({
            "imageUrl": original_storage_url,
            "backgroundRemovedUrl": processed_url,
            "thumbnailUrl": thumbnail_url,
            "backgroundRemoved": True,
            "processing_status": "done",
            "processing_error": None,
            "processing_retry_count": 0,
            "processing_last_error": None,
            "processing_time": total_time,
            "processing_mode": processing_mode,
            "original_size": f"{original_size[0]}x{original_size[1]}",
            "processed_size": f"{output_img.size[0]}x{output_img.size[1]}"
        })

        metrics["processed"] += 1
        print(f"✅ {doc_id}: Done using {processing_mode} mode ({total_time:.1f}s)")

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
            processed_any = False

            # Wardrobe queue
            wardrobe_pending = list(
                db.collection(FIRESTORE_COLLECTION)
                .where("processing_status", "==", "pending")
                .limit(BATCH_SIZE)
                .stream()
            )

            if wardrobe_pending:
                print(f"🎯 Found {len(wardrobe_pending)} pending wardrobe items")
                for doc in wardrobe_pending:
                    process_item(doc.id, doc.to_dict())
                    processed_any = True
                    time.sleep(1)

            # Outfit queue
            outfit_pending = list(
                db.collection('outfits')
                .where('flat_lay_status', '==', 'pending')
                .limit(1)
                .stream()
            )

            if not outfit_pending:
                outfit_pending = list(
                    db.collection('outfits')
                    .where('flat_lay_status', '==', None)
                    .limit(1)
                    .stream()
                )

            if outfit_pending:
                print(f"🎨 Found {len(outfit_pending)} outfits needing flat lays")
                for doc in outfit_pending:
                    data = doc.to_dict() or {}
                    if data.get('flat_lay_status') is None:
                        doc.reference.update({
                            'flat_lay_status': 'pending',
                            'metadata.flat_lay_status': 'pending'
                        })
                        data['flat_lay_status'] = 'pending'
                    process_outfit_flat_lay(doc.id, data)
                    processed_any = True
                    time.sleep(1)

            if processed_any:
                print(
                    "📊 Metrics: wardrobe_processed={processed} wardrobe_failed={failed} wardrobe_skipped={skipped} "
                    "flatlays_done={flat_lay_processed} flatlays_failed={flat_lay_failed}"
                    .format(**metrics)
                )
            else:
                if loop_count % (300 // POLL_INTERVAL) == 1:
                    print(
                        "💤 No pending tasks. wardrobe_processed={processed}, flatlays_done={flat_lay_processed}"
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

