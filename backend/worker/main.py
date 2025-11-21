#!/usr/bin/env python3
"""
Worker Service for Background Image Processing
Runs alpha matting on uploaded wardrobe items in the background
"""

# Early startup logging
import sys
print("🔍 Worker script starting...", file=sys.stderr, flush=True)
print("🔍 Python version:", sys.version, file=sys.stderr, flush=True)

import base64
import os
import time
import sys
import requests
import numpy as np
import multiprocessing
from datetime import datetime, timezone
from pathlib import Path
from io import BytesIO
from urllib.parse import urlparse, unquote
from rembg import remove
from PIL import Image, UnidentifiedImageError, ImageFilter, ImageDraw
from concurrent.futures import ProcessPoolExecutor, TimeoutError
from uuid import uuid4
from openai import OpenAI
import firebase_admin
from firebase_admin import credentials, firestore, storage
from google.cloud.firestore_v1 import FieldFilter

# Ensure backend/src is importable when worker runs standalone
CURRENT_DIR = Path(__file__).resolve().parent

def _ensure_path(path: Path):
    if path and path.exists():
        path_str = str(path)
        if path_str not in sys.path:
            sys.path.append(path_str)

_ensure_path(CURRENT_DIR)
for ancestor in [CURRENT_DIR.parent, CURRENT_DIR.parent.parent, CURRENT_DIR.parent.parent.parent]:
    if ancestor and ancestor != ancestor.parent:
        _ensure_path(ancestor)
        _ensure_path(ancestor / "src")
_ensure_path(CURRENT_DIR / "src")
try:
    from src.services.subscription_utils import (
        DEFAULT_SUBSCRIPTION_TIER,
        TIER_LIMITS,
        WEEKLY_ALLOWANCE_SECONDS,
        parse_iso8601,
        format_iso8601,
        subscription_defaults,
    )
except ModuleNotFoundError:
    from subscription_utils import (
        DEFAULT_SUBSCRIPTION_TIER,
        TIER_LIMITS,
        WEEKLY_ALLOWANCE_SECONDS,
        parse_iso8601,
        format_iso8601,
        subscription_defaults,
    )

# ----------------------------
# Configuration
# ----------------------------
FIRESTORE_COLLECTION = "wardrobe"  # Using 'wardrobe' collection (not 'closet')
FIREBASE_BUCKET_NAME = "closetgptrenew.firebasestorage.app"

# Worker tuning parameters
MAX_RETRIES = 3  # Retry failed items up to 3 times
BATCH_SIZE = 1   # Sequential processing to manage memory usage
POLL_INTERVAL = 5  # Check for new items every 5 seconds
MAX_OUTPUT_WIDTH = 1024  # Resize large images to save bandwidth (standardized to match flatlay output)
MAX_OUTPUT_HEIGHT = 1024
THUMBNAIL_SIZE = 512  # Generate thumbnails for fast loading with good detail
MAX_IMAGE_SIZE_MB = 5
MAX_IMAGE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024
ALPHA_TIMEOUT_SECONDS = 240

# Ensure deterministic OpenMP threading inside worker processes
os.environ.setdefault("OMP_NUM_THREADS", "1")

alpha_executor = ProcessPoolExecutor(
    max_workers=1,
    mp_context=multiprocessing.get_context("spawn")
)


MATERIAL_SHADOWS = {
    "silk": {"blur": 3, "opacity": 0.06},
    "puffer": {"blur": 7, "opacity": 0.18},
    "cotton": {"blur": 5, "opacity": 0.12},
    "denim": {"blur": 6, "opacity": 0.10},
    "knit": {"blur": 5, "opacity": 0.14},
    "wool": {"blur": 6, "opacity": 0.16},
}

CATEGORY_ALIASES = {
    "outerwear": [
        "blazer", "jacket", "coat", "overcoat", "trench", "outerwear", "suit jacket",
        "sport coat", "puffer coat", "peacoat", "cardigan", "topcoat"
    ],
    "top": [
        "shirt", "t-shirt", "tee", "sweater", "hoodie", "top", "polo", "jersey",
        "blouse", "crewneck", "knit top"
    ],
    "bottom": [
        "pants", "trousers", "jeans", "shorts", "bottoms", "chinos", "slacks",
        "skirt", "joggers"
    ],
    "shoes": [
        "shoe", "shoes", "sneaker", "sneakers", "boot", "boots", "loafer",
        "loafers", "heel", "heels", "sandals"
    ],
}

CATEGORY_SHADOW_OVERRIDES = {
    "outerwear": {"blur": 14, "opacity": 0.22},
    "top": {"blur": 10, "opacity": 0.12},
    "bottom": {"blur": 11, "opacity": 0.18},
    "shoes": {"blur": 8, "opacity": 0.26},
}

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if OPENAI_API_KEY:
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        print("✅ OpenAI client initialized for flat lay generation")
    except Exception as openai_init_error:
        print(f"⚠️  Failed to initialize OpenAI client: {openai_init_error}")
        openai_client = None
else:
    print("ℹ️  OPENAI_API_KEY not provided; OpenAI flat lay generation disabled")
    openai_client = None

# Initialize Firebase Admin SDK
print("🔍 Initializing Firebase Admin SDK...", flush=True)

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
    "flat_lay_openai": 0,
    "flat_lay_openai_failed": 0,
    "flat_lay_renderer_fallbacks": 0,
}


def _encode_image_to_base64(image: Image.Image) -> str:
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def _extract_image_bytes_from_openai_response(response) -> bytes | None:
    """Handle multiple possible OpenAI response formats for image data."""
    try:
        output = getattr(response, "output", None)
        if output:
            for item in output:
                contents = getattr(item, "content", None) or []
                for content in contents:
                    content_type = getattr(content, "type", None)
                    if content_type in {"output_image", "image"}:
                        image_obj = getattr(content, "image", None) or {}
                        b64_data = getattr(image_obj, "base64", None) or getattr(image_obj, "b64_json", None)
                        if not b64_data and isinstance(image_obj, dict):
                            b64_data = image_obj.get("base64") or image_obj.get("b64_json")
                        if b64_data:
                            return base64.b64decode(b64_data)
    except Exception as parse_error:
        print(f"⚠️  Error parsing OpenAI response output: {parse_error}")

    try:
        data = getattr(response, "data", None)
        if data:
            first = data[0]
            if isinstance(first, dict):
                b64_data = first.get("b64_json") or first.get("base64")
            else:
                b64_data = getattr(first, "b64_json", None) or getattr(first, "base64", None)
            if b64_data:
                return base64.b64decode(b64_data)
    except Exception as fallback_error:
        print(f"⚠️  Error parsing OpenAI legacy response: {fallback_error}")

    return None


def reserve_openai_flatlay_slot(user_id: str | None) -> dict:
    """Attempt to reserve an OpenAI flat lay usage for the user."""
    result = {
        "allowed": False,
        "tier": DEFAULT_SUBSCRIPTION_TIER,
        "limit": TIER_LIMITS.get(DEFAULT_SUBSCRIPTION_TIER),
        "used": 0,
        "week_start": None,
        "reservation_active": False,
        "reason": None,
    }

    if not user_id:
        result["reason"] = "missing_user_id"
        return result

    doc_ref = db.collection("users").document(user_id)
    transaction = db.transaction()

    @firestore.transactional
    def _reserve(txn):
        snapshot = doc_ref.get(transaction=txn)
        now = datetime.now(timezone.utc)

        if snapshot.exists:
            data = snapshot.to_dict() or {}
        else:
            data = {}

        subscription = data.get("subscription") or {}
        tier = subscription.get("tier") or DEFAULT_SUBSCRIPTION_TIER
        limit = TIER_LIMITS.get(tier, 0)

        used_raw = subscription.get("openai_flatlays_used", 0) or 0
        try:
            used = int(used_raw)
        except (TypeError, ValueError):
            used = 0

        week_start = parse_iso8601(subscription.get("flatlay_week_start"))
        if not week_start or (now - week_start).total_seconds() >= WEEKLY_ALLOWANCE_SECONDS:
            used = 0
            week_start = now

        allowed = (limit is None) or (used < limit)
        new_used = used + 1 if allowed else used

        update_payload = {
            "subscription.tier": tier,
            "subscription.flatlay_week_start": format_iso8601(week_start),
            "subscription.openai_flatlays_used": new_used if allowed else used,
            "subscription.last_updated": firestore.SERVER_TIMESTAMP,
        }

        if snapshot.exists:
            txn.update(doc_ref, update_payload)
        else:
            subscription_payload = subscription_defaults(tier=tier, now=week_start)
            subscription_payload["openai_flatlays_used"] = new_used if allowed else used
            subscription_payload["last_updated"] = firestore.SERVER_TIMESTAMP
            txn.set(doc_ref, {"subscription": subscription_payload}, merge=True)

        return {
            "allowed": allowed,
            "tier": tier,
            "limit": limit,
            "used": new_used if allowed else used,
            "week_start": week_start,
            "reservation_active": allowed,
            "reason": None if allowed else "limit_reached",
        }

    try:
        reserve_result = _reserve(transaction)
        result.update(reserve_result)
    except Exception as reservation_error:
        print(f"⚠️  Failed to reserve OpenAI flat lay slot: {reservation_error}")
        result["reason"] = "reservation_error"

    return result


def release_openai_flatlay_slot(user_id: str | None):
    """Release a previously reserved OpenAI flat lay slot (e.g., after fallback)."""
    if not user_id:
        return

    doc_ref = db.collection("users").document(user_id)
    transaction = db.transaction()

    @firestore.transactional
    def _release(txn):
        snapshot = doc_ref.get(transaction=txn)
        if not snapshot.exists:
            return

        data = snapshot.to_dict() or {}
        subscription = data.get("subscription") or {}
        used_raw = subscription.get("openai_flatlays_used", 0) or 0

        try:
            used = int(used_raw)
        except (TypeError, ValueError):
            used = 0

        if used <= 0:
            return

        txn.update(doc_ref, {"subscription.openai_flatlays_used": used - 1})

    try:
        _release(transaction)
    except Exception as release_error:
        print(f"⚠️  Failed to release OpenAI flat lay slot: {release_error}")


def get_outfit_user_id(data: dict | None) -> str | None:
    if not data:
        return None
    return (
        data.get("userId")
        or data.get("user_id")
        or data.get("userID")
        or (data.get("metadata") or {}).get("userId")
        or (data.get("metadata") or {}).get("user_id")
    )


def build_flatlay_prompt(processed_images: list[dict], outfit_data: dict | None) -> str:
    lines = [
        "Create a cohesive, photorealistic fashion flat lay shot on a soft neutral studio background.",
        "Arrange all pieces tastefully with natural shadows, crisp lighting, and realistic proportions.",
    ]

    if outfit_data:
        style_tags = outfit_data.get("style") or outfit_data.get("styleTags")
        occasion = outfit_data.get("occasion") or outfit_data.get("occasions")
        season = outfit_data.get("season") or outfit_data.get("seasons")

        context_parts = []
        if style_tags:
            if isinstance(style_tags, list):
                context_parts.append(f"Style focus: {', '.join(style_tags[:3])}")
            else:
                context_parts.append(f"Style focus: {style_tags}")
        if occasion:
            if isinstance(occasion, list):
                context_parts.append(f"Occasions: {', '.join(occasion[:3])}")
            else:
                context_parts.append(f"Occasion: {occasion}")
        if season:
            if isinstance(season, list):
                context_parts.append(f"Season: {', '.join(season[:3])}")
            else:
                context_parts.append(f"Season: {season}")
        if context_parts:
            lines.append("Context: " + " | ".join(context_parts))

    lines.append("Garment details:")
    for idx, item in enumerate(processed_images, 1):
        source = item.get("source") or {}
        name = source.get("name") or source.get("title") or f"item {idx}"
        category = item.get("category") or source.get("category") or source.get("type") or "garment"
        material = item.get("material") or source.get("material")

        colors = []
        dominant_colors = source.get("dominantColors") or source.get("dominant_colors")
        if isinstance(dominant_colors, list) and dominant_colors:
            first_color = dominant_colors[0]
            if isinstance(first_color, dict):
                color_name = first_color.get("name")
                if color_name:
                    colors.append(color_name)
            elif isinstance(first_color, str):
                colors.append(first_color)

        if isinstance(source.get("color"), str):
            colors.append(source["color"])

        descriptors = [category]
        if colors:
            descriptors.append(", ".join(dict.fromkeys(colors)))
        if material:
            descriptors.append(material)

        lines.append(f"- {name}: {' | '.join(descriptors)}")

    lines.append("Ensure the composition feels editorial and premium, with balanced spacing and a single consistent light direction.")
    return "\n".join(lines)


def generate_openai_flatlay_image(
    processed_images: list[dict],
    outfit_id: str,
    outfit_data: dict | None,
    user_id: str | None,
) -> tuple[Image.Image | None, str | None]:
    if openai_client is None:
        return None, "openai_client_unavailable"

    prompt = build_flatlay_prompt(processed_images, outfit_data)

    # Collect image URLs for gpt-image-1
    # Use gpt-image-1 with images.generate API - this is the correct API for combining multiple images
    image_urls = []
    for item in processed_images:
        item_id = item.get("id")
        source = item.get("source") or {}
        
        # Try to get public URL from source item
        image_url = (
            source.get('backgroundRemovedUrl') or 
            source.get('background_removed_url') or
            source.get('imageUrl') or
            source.get('image_url')
        )
        
        # If no URL in source, construct from Firebase Storage blob path
        if not image_url and item_id:
            # Try common blob paths and get public URL
            blob_paths = [
                f"items/{item_id}/nobg.png",
                f"items/{item_id}/processed.png",
                f"items/{item_id}/thumbnail.png",
            ]
            for blob_path in blob_paths:
                try:
                    blob = bucket.blob(blob_path)
                    if blob.exists():
                        # Make sure blob is public and get URL
                        blob.make_public()
                        image_url = blob.public_url
                        break
                except Exception as blob_error:
                    continue
        
        if image_url:
            image_urls.append(image_url)
            print(f"✅ Added image URL for item {item_id}: {image_url[:60]}...")
        else:
            print(f"⚠️  No public URL available for item {item_id}, skipping")

    if not image_urls:
        print(f"⚠️  No image URLs available for gpt-image-1; cannot generate flatlay for outfit {outfit_id}")
        return None, "no_images_available"
    
    try:
        
        if not image_urls:
            print(f"⚠️  No image URLs available for gpt-image-1")
            return None, "no_image_urls"
        
        prompt = (
            "Create a high-quality flatlay of these clothing items. "
            "Use the images exactly as provided (they already have transparent backgrounds). "
            "Arrange them neatly like an outfit: top above pants, shoes at bottom, accessories around. "
            "Lighting soft and consistent. White background. "
            "Photorealistic fashion flat lay, 1024x1024 pixels."
        )
        
        print(f"🎨 Using gpt-image-1 for flatlay generation")
        print(f"   Model: gpt-image-1")
        print(f"   Image URLs: {len(image_urls)}")
        print(f"   Prompt: {prompt[:80]}...")
        
        # Use images.edits() for combining multiple images (not images.generate())
        # .generate() = text → image
        # .edits() = image(s) → new image (this is what we need for flatlay)
        
        # Format input images as array of input_image objects
        input_images = [
                {
                    "type": "input_image",
                "url": url
            }
            for url in image_urls
        ]
        
        print(f"🎨 Using images.edits() for flatlay generation (combining {len(input_images)} images)")
        
        # Use multipart/form-data for /v1/images/edits endpoint
        # This endpoint requires file uploads, not JSON
        print(f"⚠️  images.edits() requires multipart/form-data, implementing file upload approach")
        
        # Download all images to send as files
        if not image_urls:
            return None, "no_images_available"
        
        # Download images
        image_files = []
        for i, url in enumerate(image_urls):
            try:
                img_response = requests.get(url, timeout=30)
                img_response.raise_for_status()
                image_files.append(('image', (f'image_{i}.png', img_response.content, 'image/png')))
                print(f"✅ Downloaded image {i+1}/{len(image_urls)}")
            except Exception as download_error:
                print(f"⚠️  Failed to download image {i+1}: {download_error}")
                continue
        
        if not image_files:
            return None, "failed_to_download_images"
        
        # Use first image as base, others as additional inputs
        # Note: edits endpoint typically takes one base image
        # For multiple images, we may need to use a different approach
        api_url = "https://api.openai.com/v1/images/edits"
        headers = {
            "Authorization": f"Bearer {openai_client.api_key}",
        }
        
        # Prepare multipart form data
        files = {
            'image': (image_files[0][1][0], image_files[0][1][1], image_files[0][1][2]),
            'model': (None, 'gpt-image-1'),
            'prompt': (None, prompt),
            'size': (None, '1024x1024'),
            'n': (None, '1'),
        }
        
        # If there are multiple images, try to include them
        # Note: This may not work if API only accepts one image
        if len(image_files) > 1:
            print(f"⚠️  Multiple images detected, but edits endpoint may only accept one base image")
            print(f"⚠️  Using first image as base, others may be ignored by API")
        
        api_response = requests.post(api_url, headers=headers, files=files, timeout=120)
        if not api_response.ok:
            error_text = api_response.text
            print(f"⚠️  API error response: {api_response.status_code} - {error_text[:500]}")
            try:
                error_json = api_response.json()
                print(f"⚠️  Error details: {error_json}")
            except:
                pass
            api_response.raise_for_status()
        
        response_data = api_response.json()
        
        # Convert to SDK-like response object
        class ImageData:
            def __init__(self, data):
                self.url = data.get("url")
                self.b64_json = data.get("b64_json")
        
        class ImageResponse:
            def __init__(self, data):
                self.data = [ImageData(item) for item in data.get("data", [])]
        
        response = ImageResponse(response_data)
        
        # Extract image from response
        if not hasattr(response, "data") or not response.data:
            print(f"⚠️  gpt-image-1 response has no data")
            return None, "no_image_returned"

        # Check for b64_json (base64 encoded image)
        image_data = response.data[0]
        if hasattr(image_data, "b64_json") and image_data.b64_json:
            image_bytes = base64.b64decode(image_data.b64_json)
        elif hasattr(image_data, "url") and image_data.url:
            # Download from URL if b64_json not available
            print(f"✅ gpt-image-1 generated image URL: {image_data.url[:80]}...")
            img_response = requests.get(image_data.url, timeout=30)
            img_response.raise_for_status()
            image_bytes = img_response.content
        else:
            print(f"⚠️  gpt-image-1 response has no image data")
            return None, "no_image_data"
        
        image = Image.open(BytesIO(image_bytes)).convert("RGBA")

        TARGET_SIZE = 1024
        if image.width < TARGET_SIZE or image.height < TARGET_SIZE:
            image = image.resize((TARGET_SIZE, TARGET_SIZE), Image.Resampling.LANCZOS)

        print(f"✅ OpenAI flat lay generated for outfit {outfit_id} (user {user_id})")
        return image, None

    except Exception as openai_error:
        print(f"⚠️  OpenAI flat lay generation failed for outfit {outfit_id}: {openai_error}")
        return None, str(openai_error)


def upload_flatlay_image(image: Image.Image, outfit_id: str, renderer_tag: str = "compositor_v1") -> str | None:
    if image is None:
        return None

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    path = f"flat_lays/outfit_{outfit_id}.png"
    blob = bucket.blob(path)
    blob.upload_from_file(buffer, content_type="image/png")
    blob.make_public()
    url = blob.public_url
    print(f"✅ Uploaded {renderer_tag} flat lay for outfit {outfit_id}: {url}")
    return url


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


def add_material_shadow(img: Image.Image, material: str = "cotton", override: dict | None = None) -> Image.Image:
    params = MATERIAL_SHADOWS.get(material, MATERIAL_SHADOWS["cotton"]).copy()
    if override:
        if "blur" in override:
            params["blur"] = override["blur"]
        if "opacity" in override:
            params["opacity"] = override["opacity"]
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

def generate_radial_background(
    size: tuple[int, int] = (1024, 1024),
    base_color: tuple[int, int, int] = (245, 245, 245),
    center_brightness: int = 255
) -> Image.Image:
    """Return a solid color background for consistent studio look."""
    return Image.new("RGBA", size, base_color + (255,))


CATEGORY_SIZE_SCALE = {
    "outerwear": 1.0,   # Jackets, coats - largest
    "top": 0.85,        # Shirts, sweaters - medium-large
    "bottom": 0.80,     # Pants, shorts - medium-large
    "shoes": 0.50,      # Shoes - smaller
    "accessory": 0.40,  # Accessories - smallest
}

# Base sizes for different categories (in pixels on 1024x1024 canvas)
CATEGORY_BASE_SIZES = {
    "outerwear": 450,   # Jackets/coats
    "top": 380,         # Shirts/sweaters
    "bottom": 360,      # Pants/shorts
    "shoes": 220,       # Shoes
    "accessory": 180,   # Accessories
}


def normalize_item_for_flatlay(img: Image.Image, max_dim: int = 400, category: str | None = None) -> Image.Image:
    """Scale item to proper size for flatlay while preserving aspect ratio.
    Uses category-based sizing for realistic proportions.
    Also removes hangers if detected."""
    # Remove hangers - detect vertical lines at top of image (common hanger pattern)
    img = remove_hangers(img)
    
    w, h = img.size
    if not w or not h:
        return img
    
    # Use category-specific base size for more realistic proportions
    if category and category in CATEGORY_BASE_SIZES:
        target_size = CATEGORY_BASE_SIZES[category]
    else:
        # Default size based on category scale
        target_size = max_dim
        if category and category in CATEGORY_SIZE_SCALE:
            target_size = max_dim * CATEGORY_SIZE_SCALE[category]
    
    # Scale to fit within target size while preserving aspect ratio
    # Use the larger dimension to determine scale
    max_item_dim = max(w, h)
    if max_item_dim > 0:
        scale = target_size / max_item_dim
        # Don't upscale small items too much (max 2x)
        scale = min(scale, 2.0)
        # Don't downscale too aggressively (min 0.3x)
        scale = max(scale, 0.3)
    else:
        scale = 1.0
    
    new_size = (int(w * scale), int(h * scale))
    # Ensure minimum size for visibility
    if new_size[0] < 50 or new_size[1] < 50:
        min_scale = 50 / min(w, h) if min(w, h) > 0 else 1.0
        scale = max(scale, min_scale)
        new_size = (int(w * scale), int(h * scale))
    
    return img.resize(new_size, Image.Resampling.LANCZOS)


def remove_hangers(img: Image.Image) -> Image.Image:
    """Remove hangers from clothing items by detecting and cropping out top horizontal hanger bars."""
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    
    w, h = img.size
    alpha = img.split()[3]
    
    # Check top 15% of image for hanger patterns
    # Look for horizontal lines of opaque pixels (hanger bars)
    top_region_height = int(h * 0.15)
    top_region = alpha.crop((0, 0, w, top_region_height))
    
    # Find the lowest row with significant opaque content (likely the top of the garment)
    # Skip rows that are mostly transparent (hanger area)
    min_opaque_threshold = 50  # Minimum alpha value to consider opaque
    min_opaque_pixels = w * 0.3  # At least 30% of width should be opaque
    
    garment_top = 0
    for y in range(top_region_height):
        row = top_region.crop((0, y, w, y + 1))
        row_data = list(row.getdata())
        opaque_count = sum(1 for pixel in row_data if pixel[3] >= min_opaque_threshold)
        
        if opaque_count >= min_opaque_pixels:
            garment_top = y
            break
    
    # If we found a garment top below the very top, crop out the hanger area
    if garment_top > 0:
        # Crop from garment_top, keeping a small margin
        margin = max(2, int(garment_top * 0.1))
        crop_top = max(0, garment_top - margin)
        img = img.crop((0, crop_top, w, h))
    
    return img


def crop_to_alpha(img: Image.Image) -> Image.Image:
    """Trim transparent borders so layout math uses only the garment silhouette."""
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    alpha = img.split()[3]
    bbox = alpha.getbbox()
    if bbox:
        return img.crop(bbox)
    return img


def categorize_item_type(source_item: dict) -> str:
    """
    Map raw wardrobe metadata into canonical categories:
    outerwear, top, bottom, shoes, accessory.
    """
    potential_fields = [
        source_item.get("category"),
        source_item.get("type"),
        source_item.get("subType"),
        source_item.get("subtype"),
        source_item.get("metadata", {}).get("category"),
        source_item.get("metadata", {}).get("type"),
        source_item.get("metadata", {}).get("originalType"),
        source_item.get("metadata", {}).get("basicMetadata", {}).get("category")
        if isinstance(source_item.get("metadata"), dict)
        else None,
    ]

    for field in potential_fields:
        if not field:
            continue
        value = str(field).lower()
        for canonical, aliases in CATEGORY_ALIASES.items():
            if any(alias in value for alias in aliases):
                return canonical
        if "accessor" in value or "bag" in value or "watch" in value:
            return "accessory"

    # Fallback heuristics based on keywords
    value = str(source_item.get("name", "")).lower()
    for canonical, aliases in CATEGORY_ALIASES.items():
        if any(alias in value for alias in aliases):
            return canonical
    if "bag" in value or "belt" in value or "hat" in value or "glasses" in value:
        return "accessory"

    # Default to top if unsure, keeps layout stable
    return "top"


def smart_grid_layout(items: list[dict], canvas_size: tuple[int, int]) -> list[dict]:
    """Assign adaptive positions based on item categories and count with variety."""
    import random
    width, height = canvas_size
    center_x = width / 2
    center_y = height / 2

    # Add random variation to slot positions for variety
    variation = 0.08  # 8% variation
    def vary_pos(base_x, base_y):
        x_var = random.uniform(-variation, variation) * width
        y_var = random.uniform(-variation, variation) * height
        return (base_x + x_var, base_y + y_var)

    slots = {
        "top_left": vary_pos(width * 0.28, height * 0.28),
        "top_right": vary_pos(width * 0.72, height * 0.28),
        "bottom_left": vary_pos(width * 0.28, height * 0.72),
        "bottom_right": vary_pos(width * 0.72, height * 0.72),
        "bottom_center": vary_pos(center_x, height * 0.82),
        "top_center": vary_pos(center_x, height * 0.22),
        "center": vary_pos(center_x, center_y),
    }
    
    # Shuffle slot assignment order for variety
    slot_names = list(slots.keys())
    random.shuffle(slot_names)

    categorized = {"outerwear": [], "top": [], "bottom": [], "shoes": [], "accessory": []}
    for item in items:
        cat = item.get("category") or "top"
        categorized.setdefault(cat, []).append(item)

    assignments: dict = {}
    used_slots: set[str] = set()

    def claim(slot_name: str):
        if slot_name in used_slots:
            return None
        used_slots.add(slot_name)
        return slot_name

    for category in ["outerwear", "top"]:
        for item in categorized.get(category, []):
            slot = claim("top_left") or claim("top_center") or claim("top_right") or claim("center")
            if slot:
                assignments[item["id"]] = slot

    for item in categorized.get("bottom", []):
        slot = claim("top_right") or claim("bottom_left") or claim("center")
        if slot:
            assignments[item["id"]] = slot

    shoe_items = categorized.get("shoes", [])
    if shoe_items:
        if len(shoe_items) == 1:
            slot = claim("bottom_center") or claim("bottom_left") or claim("bottom_right")
            if slot:
                assignments[shoe_items[0]["id"]] = slot
        else:
            left_slot = claim("bottom_left") or claim("bottom_center")
            right_slot = claim("bottom_right") or claim("bottom_center")
            if left_slot and len(shoe_items) > 0:
                assignments[shoe_items[0]["id"]] = left_slot
            if right_slot and len(shoe_items) > 1:
                assignments[shoe_items[1]["id"]] = right_slot
            for idx in range(2, len(shoe_items)):
                slot = claim("bottom_center") or claim("center") or claim("top_center")
                if slot:
                    assignments[shoe_items[idx]["id"]] = slot

    for item in categorized.get("accessory", []):
        slot = claim("center") or claim("top_center") or claim("bottom_center")
        if slot:
            assignments[item["id"]] = slot

    for item in items:
        if item["id"] not in assignments:
            slot = claim("center") or claim("top_center") or claim("bottom_center")
            if slot:
                assignments[item["id"]] = slot

    positioned: list[dict] = []
    for item in items:
        slot_name = assignments.get(item["id"], "center")
        slot_pos = slots.get(slot_name, (center_x, center_y))
        positioned.append({**item, "slot": slot_name, "slot_pos": slot_pos})

    return positioned


def premium_flatlay(items: list[dict], canvas_size: tuple[int, int] = (1024, 1024)) -> Image.Image:
    """Compose multiple items into a polished flat lay."""
    canvas = generate_radial_background(size=canvas_size)
    if not items:
        return canvas

    positioned = smart_grid_layout(items, canvas_size)

    for item in positioned:
        category = item.get("category")
        img = normalize_item_for_flatlay(item["img"], max_dim=420, category=category)
        img = smooth_edges(img)
        img = add_material_shadow(img, material=item.get("material", "cotton"))

        x_center, y_center = item["slot_pos"]
        x = int(x_center - img.width / 2)
        y = int(y_center - img.height / 2)
        x = max(0, min(x, canvas_size[0] - img.width))
        y = max(0, min(y, canvas_size[1] - img.height))

        canvas.alpha_composite(img, (x, y))

    return canvas


def prepare_flatlay_assets(outfit_items: list[dict], outfit_id: str) -> list[dict]:
    """Download, normalize, and enrich outfit items for flat lay composition."""
    processed_images = []
    
    for item in outfit_items:
        item_id = item.get('id') or item.get('itemId') or item.get('item_id')
        image_url = item.get('backgroundRemovedUrl') or item.get('background_removed_url')

        blob_candidates: list[str] = []
        if item_id:
            blob_candidates.extend([
                f"items/{item_id}/nobg.png",
                f"items/{item_id}/processed.png",
                f"items/{item_id}/thumbnail.png",
            ])
        debug_prefix = f"[flatlay:{outfit_id}] item={item_id or 'unknown'}"
        print(f"{debug_prefix} category_hint={item.get('category') or item.get('type')} candidates={blob_candidates}")

        def blob_from_url(url: str) -> str | None:
            parsed = urlparse(url)
            if 'storage.googleapis.com' not in parsed.netloc:
                return None
            path = parsed.path.lstrip('/')
            if path.startswith(FIREBASE_BUCKET_NAME + '/'):
                return path[len(FIREBASE_BUCKET_NAME)+1:]
            # Handle download/storage/v1/b/<bucket>/o/<object>
            segments = path.split('/')
            if len(segments) >= 5 and segments[0] == 'download' and segments[1] == 'storage' and segments[2].startswith('v1') and segments[3] == 'b':
                bucket_in_url = segments[4]
                if bucket_in_url == FIREBASE_BUCKET_NAME:
                    idx = path.find('/o/')
                    if idx != -1:
                        encoded = path[idx+3:]
                        if encoded:
                            return unquote(encoded)
            return None

        if image_url:
            blob_path = blob_from_url(image_url)
            if blob_path:
                blob_candidates.insert(0, blob_path)

        image_bytes = None
        last_error = None
        for blob_path in blob_candidates:
            try:
                blob = bucket.blob(blob_path)
                if blob.exists():
                    candidate_bytes = blob.download_as_bytes()
                    if candidate_bytes:
                        image_bytes = candidate_bytes
                        print(f"{debug_prefix} ✅ loaded {blob_path} ({len(candidate_bytes)} bytes)")
                        break
                    else:
                        print(f"{debug_prefix} ⚠️ blob {blob_path} returned empty bytes")
                else:
                    print(f"{debug_prefix} ⚠️ blob missing: {blob_path}")
            except Exception as e:
                last_error = e
                print(f"{debug_prefix} ⚠️ error downloading {blob_path}: {e}")
                continue

        if image_bytes is None and image_url:
            try:
                response = requests.get(image_url, timeout=30)
                response.raise_for_status()
                image_bytes = response.content
                print(f"{debug_prefix} ✅ fetched via HTTP {image_url} ({len(image_bytes)} bytes)")
            except Exception as e:
                last_error = e
                print(f"{debug_prefix} ⚠️ HTTP fetch failed {image_url}: {e}")

        if not image_bytes:
            print(f"⚠️  Failed to load item image for flat lay: {last_error or 'no image bytes'}")
            continue

        try:
            source_bytes = image_bytes
            img = Image.open(BytesIO(source_bytes)).convert("RGBA")
        except Exception as e:
            print(f"⚠️  Failed to decode image for flat lay: {e}")
            continue

        # Ensure the image actually has transparency. If not, run background removal now.
        alpha_channel = img.split()[3]
        has_transparency = alpha_channel.getextrema() != (255, 255)
        reprocessed = False
        if not has_transparency:
            try:
                processed_bytes = remove(source_bytes)
                img = Image.open(BytesIO(processed_bytes)).convert("RGBA")
                reprocessed = True
            except Exception as remove_error:
                print(f"⚠️  Failed to reprocess background removal for {item_id}: {remove_error}")
                continue

        # Always crop to the garment silhouette to keep layout math accurate
        img = crop_to_alpha(img)

        # If we regenerated transparency, persist it so future runs skip this work
        if reprocessed and item_id:
            try:
                nobg_path = f"items/{item_id}/nobg.png"
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                buffer.seek(0)
                blob = bucket.blob(nobg_path)
                blob.upload_from_file(buffer, content_type="image/png")
                blob.make_public()
            except Exception as upload_error:
                print(f"⚠️  Failed to upload regenerated nobg.png for {item_id}: {upload_error}")

        material = item.get("material") or resolve_material(item) or "cotton"

        category = categorize_item_type(item)

        item_unique_id = item_id or item.get("id") or str(uuid4())

        processed_images.append({
            "id": item_unique_id,
            "img": img,
            "material": material,
            "category": category,
            "source": item,
        })
    
    if not processed_images:
        print(f"❌ No valid images for flat lay {outfit_id}")
    
    return processed_images


def compose_flatlay_image(processed_images: list[dict]) -> Image.Image | None:
    if not processed_images:
        return None
    return premium_flatlay(processed_images)
    

def create_premium_flatlay(outfit_items: list[dict], outfit_id: str) -> str | None:
    """
    Legacy helper to create and upload a premium flat lay from outfit items.
    """
    processed_images = prepare_flatlay_assets(outfit_items, outfit_id)
    if not processed_images:
        return None
    
    canvas = compose_flatlay_image(processed_images)
    if canvas is None:
        print(f"❌ Failed to compose flat lay canvas for outfit {outfit_id}")
        return None

    return upload_flatlay_image(canvas, outfit_id, renderer_tag="compositor_v1")


def process_outfit_flat_lay(doc_id: str, data: dict):
    """Generate and store premium flat lay for an outfit document."""
    doc_ref = db.collection('outfits').document(doc_id)
    try:
        items = data.get('items') or []
        if not items:
            doc_ref.update({
                'flat_lay_status': 'failed',
                'flatLayStatus': 'failed',
                'flat_lay_error': 'No items available for flat lay',
                'flatLayError': 'No items available for flat lay',
                'metadata.flat_lay_status': 'failed',
                'metadata.flatLayStatus': 'failed',
                'metadata.flat_lay_error': 'No items available for flat lay',
                'metadata.flatLayError': 'No items available for flat lay',
                'flat_lay_updated_at': firestore.SERVER_TIMESTAMP,
            })
            metrics['flat_lay_failed'] += 1
            print(f"❌ Outfit {doc_id}: No items available for flat lay")
            return

        user_id = get_outfit_user_id(data)
        processed_images = prepare_flatlay_assets(items, doc_id)
        if not processed_images:
            failure_reason = 'No valid images available for flat lay composition'
            doc_ref.update({
                'flat_lay_status': 'failed',
                'flatLayStatus': 'failed',
                'flat_lay_error': failure_reason,
                'flatLayError': failure_reason,
                'metadata.flat_lay_status': 'failed',
                'metadata.flatLayStatus': 'failed',
                'metadata.flat_lay_error': failure_reason,
                'metadata.flatLayError': failure_reason,
                'flat_lay_updated_at': firestore.SERVER_TIMESTAMP,
            })
            metrics['flat_lay_failed'] += 1
            print(f"❌ Outfit {doc_id}: {failure_reason}")
            return

        flat_lay_url: str | None = None
        openai_note: str | None = None
        openai_used = False
        reservation = None

        # Check OpenAI availability (but skip direct multi-image approach)
        # TEMPORARY: Limit check disabled for testing
        if openai_client and user_id:
            # Bypass limit check - allow all requests for testing
            reservation = {"allowed": True, "reason": "limit_disabled_for_testing", "bypassed": True}
            print(f"🧪 Limit check disabled for testing - allowing OpenAI flatlay for outfit {doc_id}")
        else:
            if not openai_client:
                openai_note = "openai_client_unavailable"
            elif not user_id:
                openai_note = "missing_user_id"
            if openai_note:
                print(f"ℹ️  Skipping OpenAI for outfit {doc_id}: {openai_note}")

        # Generate compositor flatlay first, then enhance with OpenAI
        renderer_note = openai_note or 'openai_unavailable'
        print(f"🎨 Outfit {doc_id}: Generating compositor flatlay first...")
        
        compositor_canvas = None
        try:
            compositor_canvas = compose_flatlay_image(processed_images)
            if compositor_canvas is None:
                print(f"⚠️  Outfit {doc_id}: Compositor failed to generate canvas")
                raise Exception("compositor_failed")
            print(f"✅ Outfit {doc_id}: Compositor flatlay generated, enhancing with OpenAI...")
        except Exception as compositor_error:
            print(f"⚠️  Outfit {doc_id}: Compositor error: {compositor_error}")
            compositor_canvas = None
        
        # If we have a compositor image and OpenAI is available, enhance it
        if compositor_canvas and openai_client and user_id:
            print(f"🎨 Outfit {doc_id}: Enhancing compositor image with OpenAI...")
            
            # Convert compositor image directly to bytes (no storage needed)
            compositor_buffer = BytesIO()
            compositor_canvas.save(compositor_buffer, format="PNG")
            compositor_buffer.seek(0)
            compositor_bytes = compositor_buffer.read()
            
            # Use OpenAI to enhance the compositor image
            try:
                # Use images.edits to enhance the compositor flatlay
                api_url = "https://api.openai.com/v1/images/edits"
                headers = {
                    "Authorization": f"Bearer {openai_client.api_key}",
                }
                
                enhance_prompt = (
                    "Enhance ONLY the existing items in this fashion flatlay image. "
                    "CRITICAL: DO NOT show any hangers, hooks, or hanging hardware. Remove any hangers if present. "
                    "DO NOT add any new items. DO NOT add accessories, jewelry, or any clothing items that are not already in the image. "
                    "PRESERVE the exact appearance of each item - keep colors, patterns, textures, and details exactly as they appear in the original. "
                    "Do not change the style, design, or visual characteristics of any item. "
                    "Improve lighting, shadows, and composition. Make it look more professional and photorealistic. "
                    "Keep all existing items clearly visible and maintain their exact same arrangement. "
                    "Only refine the visual quality - better lighting, natural shadows, improved colors and contrast. "
                    "The output must contain exactly the same items as the input image, nothing more, nothing less. "
                    "Items should appear as if laid flat on a surface, never hanging."
                )
                
                files = {
                    'image': ('compositor.png', compositor_bytes, 'image/png'),
                    'model': (None, 'gpt-image-1'),
                    'prompt': (None, enhance_prompt),
                    'size': (None, '1024x1024'),
                    'n': (None, '1'),
                }
                
                api_response = requests.post(api_url, headers=headers, files=files, timeout=120)
                
                if not api_response.ok:
                    # Log detailed error information
                    error_text = api_response.text
                    try:
                        error_json = api_response.json()
                        error_msg = f"Status {api_response.status_code}: {error_json}"
                    except:
                        error_msg = f"Status {api_response.status_code}: {error_text[:500]}"
                    print(f"⚠️  Outfit {doc_id}: OpenAI enhancement API error: {error_msg}")
                    if reservation and not reservation.get("bypassed"):
                        release_openai_flatlay_slot(user_id)
                    metrics['flat_lay_openai_failed'] += 1
                else:
                    try:
                        response_data = api_response.json()
                        print(f"🔍 Outfit {doc_id}: OpenAI response structure: {list(response_data.keys())}")
                        
                        # Check for different response formats
                        enhanced_url = None
                        enhanced_b64 = None
                        
                        # Format 1: Standard images API response with data array
                        if response_data.get("data") and len(response_data["data"]) > 0:
                            first_item = response_data["data"][0]
                            enhanced_url = first_item.get("url")
                            enhanced_b64 = first_item.get("b64_json")
                            print(f"🔍 Outfit {doc_id}: Found data array, first item keys: {list(first_item.keys()) if isinstance(first_item, dict) else 'not a dict'}")
                        
                        # Format 2: Direct URL or b64_json at top level
                        elif "url" in response_data:
                            enhanced_url = response_data.get("url")
                            print(f"🔍 Outfit {doc_id}: Found URL at top level")
                        elif "b64_json" in response_data:
                            enhanced_b64 = response_data.get("b64_json")
                            print(f"🔍 Outfit {doc_id}: Found b64_json at top level")
                        
                        # Format 3: Check for output_images (Responses API format)
                        elif "output_images" in response_data:
                            output_images = response_data.get("output_images", [])
                            if output_images and len(output_images) > 0:
                                first_output = output_images[0]
                                if isinstance(first_output, dict):
                                    enhanced_url = first_output.get("url")
                                    enhanced_b64 = first_output.get("b64_json")
                                print(f"🔍 Outfit {doc_id}: Found output_images array")
                        
                        if enhanced_url:
                            # Download enhanced image from URL
                            print(f"🔍 Outfit {doc_id}: Downloading enhanced image from URL...")
                            enhanced_response = requests.get(enhanced_url, timeout=30)
                            enhanced_response.raise_for_status()
                            enhanced_bytes = enhanced_response.content
                            enhanced_image = Image.open(BytesIO(enhanced_bytes)).convert("RGBA")
                        elif enhanced_b64:
                            # Decode base64 image
                            print(f"🔍 Outfit {doc_id}: Decoding base64 enhanced image...")
                            import base64
                            enhanced_bytes = base64.b64decode(enhanced_b64)
                            enhanced_image = Image.open(BytesIO(enhanced_bytes)).convert("RGBA")
                        else:
                            print(f"⚠️  Outfit {doc_id}: OpenAI response missing URL or b64_json")
                            print(f"⚠️  Full response structure: {response_data}")
                            if reservation and not reservation.get("bypassed"):
                                release_openai_flatlay_slot(user_id)
                            metrics['flat_lay_openai_failed'] += 1
                            return  # Skip to compositor fallback
                        
                        # Upload final enhanced image
                        final_url = upload_flatlay_image(enhanced_image, doc_id, renderer_tag="openai_enhanced_compositor")
                        if final_url:
                            update_payload = {
                                'flat_lay_status': 'done',
                                'flatLayStatus': 'done',
                                'flat_lay_url': final_url,
                                'flatLayUrl': final_url,
                                'flat_lay_error': None,
                                'flatLayError': None,
                                'flat_lay_updated_at': firestore.SERVER_TIMESTAMP,
                                'flat_lay_renderer': 'openai_enhanced_compositor',
                                'flatLayRenderer': 'openai_enhanced_compositor',
                                'metadata.flat_lay_status': 'done',
                                'metadata.flatLayStatus': 'done',
                                'metadata.flat_lay_url': final_url,
                                'metadata.flatLayUrl': final_url,
                                'metadata.flat_lay_error': None,
                                'metadata.flatLayError': None,
                                'metadata.flat_lay_renderer': 'openai_enhanced_compositor',
                                'metadata.flatLayRenderer': 'openai_enhanced_compositor',
                            }
                            doc_ref.update(update_payload)
                            metrics['flat_lay_processed'] += 1
                            metrics['flat_lay_openai'] += 1
                            if reservation and not reservation.get("bypassed"):
                                release_openai_flatlay_slot(user_id)
                            print(f"✅ Outfit {doc_id}: OpenAI-enhanced flatlay ready ({final_url})")
                            return
                    except Exception as parse_error:
                        print(f"⚠️  Outfit {doc_id}: Error parsing OpenAI response: {parse_error}")
                        print(f"⚠️  Response status: {api_response.status_code}, text: {api_response.text[:500]}")
                        if reservation and not reservation.get("bypassed"):
                            release_openai_flatlay_slot(user_id)
                        metrics['flat_lay_openai_failed'] += 1
            except Exception as enhance_error:
                import traceback
                error_trace = traceback.format_exc()
                print(f"⚠️  Outfit {doc_id}: OpenAI enhancement exception: {enhance_error}")
                print(f"⚠️  Traceback: {error_trace[:500]}")
                if reservation and not reservation.get("bypassed"):
                    release_openai_flatlay_slot(user_id)
                metrics['flat_lay_openai_failed'] += 1
        
        # Fallback: Use compositor image directly
        if compositor_canvas:
            compositor_url = upload_flatlay_image(compositor_canvas, doc_id, renderer_tag="compositor_v1")
            if compositor_url:
        update_payload = {
                    'flat_lay_status': 'done',
                    'flatLayStatus': 'done',
                    'flat_lay_url': compositor_url,
                    'flatLayUrl': compositor_url,
                    'flat_lay_error': None,
                    'flatLayError': None,
            'flat_lay_updated_at': firestore.SERVER_TIMESTAMP,
                    'flat_lay_renderer': 'compositor_v1',
                    'flatLayRenderer': 'compositor_v1',
                    'metadata.flat_lay_status': 'done',
                    'metadata.flatLayStatus': 'done',
                    'metadata.flat_lay_url': compositor_url,
                    'metadata.flatLayUrl': compositor_url,
                    'metadata.flat_lay_error': None,
                    'metadata.flatLayError': None,
                    'metadata.flat_lay_renderer': 'compositor_v1',
                    'metadata.flatLayRenderer': 'compositor_v1',
                    'metadata.flat_lay_renderer_note': f'openai_enhancement_failed: {renderer_note}',
                    'flat_lay_renderer_note': f'openai_enhancement_failed: {renderer_note}',
                    'flatLayRendererNote': f'openai_enhancement_failed: {renderer_note}',
                }
                doc_ref.update(update_payload)
                metrics['flat_lay_processed'] += 1
                metrics['flat_lay_renderer_fallbacks'] += 1
                print(f"✅ Outfit {doc_id}: Compositor flatlay ready ({compositor_url})")
                return
        
        # Compositor also failed - mark as failed
        message = f'OpenAI unavailable ({renderer_note}), compositor also failed'
        update_payload = {
                'flat_lay_status': 'failed',
                'flatLayStatus': 'failed',
            'flat_lay_url': None,
            'flatLayUrl': None,
                'flat_lay_error': message,
                'flatLayError': message,
            'flat_lay_updated_at': firestore.SERVER_TIMESTAMP,
            'flat_lay_renderer': 'none',
            'flatLayRenderer': 'none',
                'metadata.flat_lay_status': 'failed',
                'metadata.flatLayStatus': 'failed',
            'metadata.flat_lay_url': None,
            'metadata.flatLayUrl': None,
                'metadata.flat_lay_error': message,
                'metadata.flatLayError': message,
            'metadata.flat_lay_renderer': 'none',
            'metadata.flatLayRenderer': 'none',
            'metadata.flat_lay_renderer_note': renderer_note,
            'flat_lay_renderer_note': renderer_note,
            'flatLayRendererNote': renderer_note,
        }
        doc_ref.update(update_payload)
        metrics['flat_lay_failed'] += 1
        print(f"❌ Outfit {doc_id}: Both OpenAI and compositor failed - {message}")
        return

    except Exception as exc:
        error_message = str(exc)
        doc_ref.update({
            'flat_lay_status': 'failed',
            'flatLayStatus': 'failed',
            'flat_lay_error': error_message,
            'flatLayError': error_message,
            'flat_lay_updated_at': firestore.SERVER_TIMESTAMP,
            'metadata.flat_lay_status': 'failed',
            'metadata.flatLayStatus': 'failed',
            'metadata.flat_lay_error': error_message,
            'metadata.flatLayError': error_message,
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
                .where(filter=FieldFilter("processing_status", "==", "pending"))
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
                .where(filter=FieldFilter('flat_lay_status', "==", 'pending'))
                .limit(1)
                .stream()
            )

            if not outfit_pending:
                outfit_pending = list(
                    db.collection('outfits')
                    .where(filter=FieldFilter('flat_lay_status', "==", None))
                    .limit(1)
                    .stream()
                )

            if not outfit_pending:
                outfit_pending = list(
                    db.collection('outfits')
                    .where(filter=FieldFilter('metadata.flat_lay_status', "==", 'pending'))
                    .limit(1)
                    .stream()
                )

            if not outfit_pending:
                outfit_pending = list(
                    db.collection('outfits')
                    .where(filter=FieldFilter('flatLayStatus', "==", 'pending'))
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
                            'flatLayStatus': 'pending',
                            'metadata.flat_lay_status': 'pending',
                            'metadata.flatLayStatus': 'pending'
                        })
                        data['flat_lay_status'] = 'pending'
                        data['flatLayStatus'] = 'pending'
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
    try:
    print("=" * 60)
    print("🚀 Easy Outfit Background Image Processor")
    print("=" * 60)
    print()
    run_worker()
    except KeyboardInterrupt:
        print("\n👋 Worker stopped by user")
    except Exception as e:
        import traceback
        print(f"❌ Fatal error during worker startup:")
        print(f"   {str(e)}")
        print(f"   Traceback:")
        traceback.print_exc()
        raise

