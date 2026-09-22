#!/usr/bin/env python3
"""
Worker Service for Background Image Processing
Runs alpha matting on uploaded wardrobe items in the background
"""

# Early startup logging
import sys
import os
print("🔍 Worker script starting...", file=sys.stderr, flush=True)
print("🔍 Python version:", sys.version, file=sys.stderr, flush=True)
print("🔍 Using railway.worker.toml config with NIXPACKS builder (root railway.toml removed)", file=sys.stderr, flush=True)

from flatlay_lifecycle import (
    REQUESTS_COLLECTION,
    claim_request,
    admit_provider_request,
    finish_request,
)
from flatlay_original_preparation import prepare_request_originals
from flatlay_reference_images import (
    prepare_original_references,
    build_reference_edit_payload,
    ReferenceImageError,
    MAX_IMAGE_BYTES as MAX_REFERENCE_IMAGE_BYTES,
    MAX_IMAGE_PIXELS as MAX_REFERENCE_IMAGE_PIXELS,
)

# Continue with other imports
import base64
import json
import signal
import time
import requests
from datetime import datetime, timezone
from pathlib import Path
from io import BytesIO
from urllib.parse import urlparse, unquote
from PIL import Image, UnidentifiedImageError, ImageFilter, ImageDraw, ImageOps
from uuid import uuid4
from openai import OpenAI
import firebase_admin
from firebase_admin import credentials, firestore, storage
from google.cloud.firestore_v1 import FieldFilter
from debug_utils import debug_val, debug_section, debug_exception

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


def _read_positive_float_env(name: str, default: float) -> float:
    raw = (os.environ.get(name) or "").strip()
    if raw:
        try:
            value = float(raw)
            if value > 0:
                return value
        except ValueError:
            pass
    return default


OPENAI_TIMEOUT_SECONDS = _read_positive_float_env("EASYOUTFIT_OPENAI_TIMEOUT_SECONDS", 45.0)
OPENAI_IMAGE_EDIT_TIMEOUT_SECONDS = _read_positive_float_env(
    "EASYOUTFIT_OPENAI_IMAGE_EDIT_TIMEOUT_SECONDS",
    120.0,
)
OPENAI_IMAGE_EDIT_MODEL = (os.environ.get("EASYOUTFIT_OPENAI_IMAGE_EDIT_MODEL") or "gpt-image-1").strip() or "gpt-image-1"
OPENAI_IMAGE_EDIT_API_URL = "https://api.openai.com/v1/images/edits"

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if OPENAI_API_KEY:
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY, timeout=OPENAI_TIMEOUT_SECONDS)
        print(f"✅ OpenAI client initialized for flat lay generation ({OPENAI_IMAGE_EDIT_MODEL})")
    except Exception as openai_init_error:
        print(f"⚠️  Failed to initialize OpenAI client: {openai_init_error}")
        openai_client = None
else:
    print("ℹ️  OPENAI_API_KEY not provided; OpenAI flat lay generation disabled")
    openai_client = None

# Initialize Firebase Admin SDK
print("🔍 Initializing Firebase Admin SDK...", flush=True)

try:
    # Check if Firebase is already initialized
    try:
        firebase_admin.get_app()
        print("ℹ️  Firebase already initialized, reusing existing app", flush=True)
    except ValueError:
        # Not initialized, proceed with initialization
        print("🔍 Building Firebase credentials...", flush=True)
        
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
        
        # Validate required fields
        required_fields = ["project_id", "private_key", "client_email"]
        missing_fields = [field for field in required_fields if not firebase_creds.get(field)]
        if missing_fields:
            raise ValueError(f"Missing Firebase credentials: {', '.join(missing_fields)}")
        
        print("🔍 Creating Firebase credentials object...", flush=True)
        cred = credentials.Certificate(firebase_creds)
        
        print("🔍 Initializing Firebase app...", flush=True)
        firebase_admin.initialize_app(cred, {
            "storageBucket": FIREBASE_BUCKET_NAME
        })
        print("✅ Firebase app initialized", flush=True)
    
    # Get Firebase clients
    print("🔍 Getting Firestore client...", flush=True)
    db = firestore.client()
    print("🔍 Getting Storage bucket...", flush=True)
    bucket = storage.bucket()
    
    print(f"✅ Connected to Firestore collection: {FIRESTORE_COLLECTION}", flush=True)
    print(f"✅ Connected to Storage bucket: {bucket.name}", flush=True)
    
except Exception as e:
    print(f"❌ Firebase initialization failed: {type(e).__name__}: {e}", flush=True)
    import traceback
    traceback.print_exc()
    raise


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


def constrain_original_reference_image(image: Image.Image, *,
                                       max_pixels: int = MAX_REFERENCE_IMAGE_PIXELS,
                                       max_bytes: int = MAX_REFERENCE_IMAGE_BYTES) -> Image.Image:
    """Keep original pixels when within bounds; otherwise resize without styling."""
    bounded = image
    if bounded.width * bounded.height > max_pixels:
        edge_limit = max(1, int(max_pixels ** 0.5))
        bounded = resize_image(bounded, edge_limit, edge_limit)
    # PNG can be larger than the original JPEG. Bound the actual stored encoding,
    # matching the reference loader, rather than trusting incoming file size.
    for _ in range(12):
        buffer = BytesIO()
        bounded.save(buffer, format="PNG")
        if buffer.tell() < max_bytes:
            return bounded
        bounded = resize_image(bounded, max(1, int(bounded.width * 0.85)),
                               max(1, int(bounded.height * 0.85)))
    raise ValueError("Original photo exceeds the supported reference size")


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


def get_openai_image_edit_runtime_config() -> dict[str, str | float | None]:
    """
    Mirror the backend AI runtime image-edit config locally.

    Railway deploys the worker with `backend/worker` as the root directory, so this
    service cannot import `backend/src/services/ai_runtime` at runtime.
    """
    quality = (os.environ.get("EASYOUTFIT_OPENAI_IMAGE_EDIT_QUALITY") or "").strip().lower() or None
    if quality is not None and quality not in {"low", "medium", "high", "auto"}:
        raise ReferenceImageError("invalid_quality", "The preview image quality setting is invalid. Please contact support.")
    return {
        "api_url": OPENAI_IMAGE_EDIT_API_URL,
        "model": OPENAI_IMAGE_EDIT_MODEL,
        "timeout_seconds": OPENAI_IMAGE_EDIT_TIMEOUT_SECONDS,
        "quality": quality,
    }


def _build_openai_image_edit_headers() -> dict[str, str]:
    if openai_client is None or not getattr(openai_client, "api_key", None):
        raise RuntimeError("openai_client_unavailable")
    return {"Authorization": f"Bearer {openai_client.api_key}"}


def _load_image_from_openai_image_response(response_data: dict, debug_prefix: str) -> Image.Image | None:
    enhanced_url = None
    enhanced_b64 = None

    if response_data.get("data") and len(response_data["data"]) > 0:
        first_item = response_data["data"][0]
        if isinstance(first_item, dict):
            enhanced_url = first_item.get("url")
            enhanced_b64 = first_item.get("b64_json")
        print(f"{debug_prefix}: Found data array response")
    elif "url" in response_data:
        enhanced_url = response_data.get("url")
        print(f"{debug_prefix}: Found top-level URL response")
    elif "b64_json" in response_data:
        enhanced_b64 = response_data.get("b64_json")
        print(f"{debug_prefix}: Found top-level base64 response")
    elif "output_images" in response_data:
        output_images = response_data.get("output_images", [])
        if output_images:
            first_output = output_images[0]
            if isinstance(first_output, dict):
                enhanced_url = first_output.get("url")
                enhanced_b64 = first_output.get("b64_json")
        print(f"{debug_prefix}: Found output_images response")

    if enhanced_url:
        print(f"{debug_prefix}: Downloading generated image from URL...")
        enhanced_response = requests.get(enhanced_url, timeout=30)
        enhanced_response.raise_for_status()
        return Image.open(BytesIO(enhanced_response.content)).convert("RGBA")

    if enhanced_b64:
        print(f"{debug_prefix}: Decoding generated image from base64...")
        enhanced_bytes = base64.b64decode(enhanced_b64)
        return Image.open(BytesIO(enhanced_bytes)).convert("RGBA")

    return None


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

    runtime_config = get_openai_image_edit_runtime_config()
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
                    # Continue to next blob_path on error
                    pass
        
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
        print(f"   Model: {runtime_config['model']}")
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
        api_url = str(runtime_config["api_url"])
        headers = _build_openai_image_edit_headers()
        
        # Prepare multipart form data
        files = {
            'image': (image_files[0][1][0], image_files[0][1][1], image_files[0][1][2]),
            'model': (None, str(runtime_config["model"])),
            'prompt': (None, prompt),
            'size': (None, '1024x1024'),
            'n': (None, '1'),
        }
        
        # If there are multiple images, try to include them
        # Note: This may not work if API only accepts one image
        if len(image_files) > 1:
            print(f"⚠️  Multiple images detected, but edits endpoint may only accept one base image")
            print(f"⚠️  Using first image as base, others may be ignored by API")
        
        api_response = requests.post(
            api_url,
            headers=headers,
            files=files,
            timeout=float(runtime_config["timeout_seconds"]),
        )
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
        
        image = _load_image_from_openai_image_response(response_data, "✅ gpt-image-1")
        if image is None:
            print(f"⚠️  gpt-image-1 response has no usable image data")
            return None, "no_image_data"

        TARGET_SIZE = 1024
        if image.width < TARGET_SIZE or image.height < TARGET_SIZE:
            image = image.resize((TARGET_SIZE, TARGET_SIZE), Image.Resampling.LANCZOS)

        print(f"✅ OpenAI flat lay generated for outfit {outfit_id} (user {user_id})")
        return image, None

    except Exception as openai_error:
        print(f"⚠️  OpenAI flat lay generation failed for outfit {outfit_id}: {openai_error}")
        return None, str(openai_error)


def upload_flatlay_image(image: Image.Image, outfit_id: str, renderer_tag: str = "compositor_v1", request_id: str | None = None) -> str | None:
    if image is None:
        return None

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    path = f"flat_lays/outfit_{outfit_id}/{request_id}.png" if request_id else f"flat_lays/outfit_{outfit_id}.png"
    blob = bucket.blob(path)
    blob.upload_from_file(buffer, content_type="image/png")
    blob.make_public()
    url = blob.public_url
    print(f"✅ Uploaded {renderer_tag} flat lay for outfit {outfit_id}: {url}")
    return url



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
    canvas.alpha_composite(resized.convert("RGBA"), (x_offset, y_offset))
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
    debug_section("NORMALIZE ITEM")
    debug_val("img.size BEFORE validation", getattr(img, "size", None))
    debug_val("item metadata", {"max_dim": max_dim, "category": category})
    
    # Note: Hanger removal is skipped during flatlay processing for performance
    # Hangers should already be removed during initial item processing
    
    # Get image size - ensure it's a tuple
    size = img.size
    if not isinstance(size, (tuple, list)) or len(size) < 2:
        print(f"⚠️  Invalid image size: {size}, returning original")
        return img
    
    w, h = int(size[0]), int(size[1])
    if not w or not h or w <= 0 or h <= 0:
        print(f"⚠️  Invalid dimensions: {w}x{h}, returning original")
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
    
    new_w = int(w * scale)
    new_h = int(h * scale)
    new_size = (new_w, new_h)
    
    debug_val("new_size BEFORE resize", new_size)
    
    # Ensure minimum size for visibility
    if new_w < 50 or new_h < 50:
        min_scale = 50 / min(w, h) if min(w, h) > 0 else 1.0
        scale = max(scale, min_scale)
        new_w = int(w * scale)
        new_h = int(h * scale)
        new_size = (new_w, new_h)
        debug_val("new_size AFTER min size adjustment", new_size)
    
    # Ensure new_size is valid
    if new_w <= 0 or new_h <= 0:
        print(f"⚠️  Calculated invalid size: {new_size}, using original")
        return img
    
    return img.resize(new_size, Image.Resampling.LANCZOS)


def remove_hangers(img: Image.Image) -> Image.Image:
    """Remove hangers from clothing items by detecting and cropping out top horizontal hanger bars."""
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    
    w, h = img.size
    alpha = img.split()[3]  # This is a single-channel (L mode) image
    
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
        # For single-channel (L mode) images, getdata() returns integers, not tuples
        row_data = list(row.getdata())
        # row_data is a list of integers (alpha values), not tuples
        opaque_count = sum(1 for pixel_alpha in row_data if pixel_alpha >= min_opaque_threshold)
        
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
    debug_section("LAYOUT ENGINE")
    debug_val("canvas_size BEFORE unpack", canvas_size)
    debug_val("items passed to layout", items)
    
    # Ensure canvas_size is a tuple
    if not isinstance(canvas_size, (tuple, list)) or len(canvas_size) < 2:
        print(f"⚠️  Invalid canvas_size in smart_grid_layout: {canvas_size}, using default")
        canvas_size = (1024, 1024)
    width, height = int(canvas_size[0]), int(canvas_size[1])
    center_x = float(width) / 2
    center_y = float(height) / 2

    # Add random variation to slot positions for variety
    variation = 0.08  # 8% variation
    def vary_pos(base_x, base_y):
        x_var = random.uniform(-variation, variation) * width
        y_var = random.uniform(-variation, variation) * height
        result = (float(base_x + x_var), float(base_y + y_var))
        return result

    slots = {
        "top_left": vary_pos(width * 0.28, height * 0.28),
        "top_right": vary_pos(width * 0.72, height * 0.28),
        "bottom_left": vary_pos(width * 0.28, height * 0.72),
        "bottom_right": vary_pos(width * 0.72, height * 0.72),
        "bottom_center": vary_pos(center_x, height * 0.82),
        "top_center": vary_pos(center_x, height * 0.22),
        "center": vary_pos(center_x, center_y),
    }
    
    # Ensure all slots are tuples
    for slot_name, slot_pos in slots.items():
        if not isinstance(slot_pos, (tuple, list)) or len(slot_pos) < 2:
            print(f"⚠️  Invalid slot position for {slot_name}: {slot_pos}, using center")
            slots[slot_name] = (float(center_x), float(center_y))
    
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
        slot_pos = slots.get(slot_name, (float(center_x), float(center_y)))
        # Ensure slot_pos is a valid tuple
        if not isinstance(slot_pos, (tuple, list)) or len(slot_pos) < 2:
            print(f"⚠️  Invalid slot_pos for {slot_name}, using center")
            slot_pos = (float(center_x), float(center_y))
        positioned.append({**item, "slot": slot_name, "slot_pos": slot_pos})

    return positioned


def premium_flatlay(items: list[dict], canvas_size: tuple[int, int] = (1024, 1024)) -> Image.Image:
    """Compose multiple items into a polished flat lay."""
    debug_section("PREMIUM FLATLAY START")
    debug_val("canvas_size RAW", canvas_size)
    
    # Ensure canvas_size is a tuple
    if not isinstance(canvas_size, (tuple, list)) or len(canvas_size) < 2:
        print(f"⚠️  Invalid canvas_size: {canvas_size}, using default (1024, 1024)")
        canvas_size = (1024, 1024)
    canvas_size = (int(canvas_size[0]), int(canvas_size[1]))
    
    canvas = generate_radial_background(size=canvas_size)
    if not items:
        return canvas

    positioned = smart_grid_layout(items, canvas_size)

    for item in positioned:
        debug_val("slot_pos RAW", item.get("slot_pos"))
        
        category = item.get("category")
        img = normalize_item_for_flatlay(item["img"], max_dim=420, category=category)
        img = smooth_edges(img)
        img = add_material_shadow(img, material=item.get("material", "cotton"))

        # Get slot position - ensure it's a tuple
        slot_pos = item.get("slot_pos")
        debug_val("slot_pos BEFORE UNPACK", slot_pos)
        
        if not isinstance(slot_pos, (tuple, list)) or len(slot_pos) < 2:
            print(f"⚠️  Invalid slot_pos for item {item.get('id')}: {slot_pos}, using center")
            slot_pos = (float(canvas_size[0]) / 2, float(canvas_size[1]) / 2)
        
        x_center, y_center = float(slot_pos[0]), float(slot_pos[1])
        x = int(x_center - img.width / 2)
        y = int(y_center - img.height / 2)
        canvas_w, canvas_h = int(canvas_size[0]), int(canvas_size[1])
        x = max(0, min(x, canvas_w - img.width))
        y = max(0, min(y, canvas_h - img.height))

        debug_val("paste position", (x, y))
        debug_val("item image size", getattr(img, "size", None))

        canvas.alpha_composite(img, (x, y))

    return canvas


def prepare_flatlay_assets(outfit_items: list[dict], outfit_id: str) -> list[dict]:
    """Download, normalize, and enrich outfit items for flat lay composition."""
    debug_section(f"FIREBASE RAW ITEM DATA - Outfit {outfit_id}")
    processed_images = []
    
    for item in outfit_items:
        debug_section(f"FIREBASE RAW ITEM DATA - Item {item.get('id')}")
        debug_val("Raw Firestore Item", item)
        debug_val("Item metadata", item.get("metadata"))
        debug_val("Item slot_pos pre-compositor", item.get("slot_pos"))
        
        item_id = item.get('id') or item.get('itemId') or item.get('item_id')
        source = item.get('source') or {}
        
        # Try to get image URL from various sources (prefer background-removed, fallback to original)
        image_url = (
            item.get('backgroundRemovedUrl') or 
            item.get('background_removed_url') or
            source.get('backgroundRemovedUrl') or
            source.get('background_removed_url') or
            item.get('imageUrl') or
            item.get('image_url') or
            source.get('imageUrl') or
            source.get('image_url')
        )

        # Prioritize processed images (nobg.png is fastest, then processed.png, thumbnail as last resort)
        blob_candidates: list[str] = []
        if item_id:
            # Prefer nobg.png (background removed, ready for flatlay)
            # Then processed.png (fully processed with shadows/styling)
            # Thumbnail only as fallback
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

        # Only add processed image paths to candidates, skip original.png
        # (original.png doesn't have transparency and will be skipped anyway)
        if image_url:
            blob_path = blob_from_url(image_url)
            if blob_path and not blob_path.endswith('/original.png'):
                # Only add if it's a processed image, not original
                blob_candidates.insert(0, blob_path)

        debug_section(f"IMAGE LOAD - Item {item_id}")
        debug_val("candidate paths", blob_candidates)

        image_bytes = None
        last_error = None
        chosen_path = None
        for blob_path in blob_candidates:
            # Skip original.png - it doesn't have transparency and will be rejected anyway
            if blob_path.endswith('/original.png'):
                print(f"{debug_prefix} ⏭️  skipping original.png (no transparency)")
                continue
            try:
                blob = bucket.blob(blob_path)
                if blob.exists():
                    candidate_bytes = blob.download_as_bytes()
                    if candidate_bytes:
                        image_bytes = candidate_bytes
                        chosen_path = blob_path
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
        
        debug_val("chosen asset path", chosen_path)
        debug_val("image bytes length", len(image_bytes) if image_bytes else None)
        debug_val("fallback image_url available", bool(image_url))

        # Fallback to original imageUrl if no storage blobs found (for legacy items)
        if image_bytes is None and image_url:
            try:
                print(f"{debug_prefix} 🔄 Falling back to original imageUrl (legacy item): {image_url[:80]}...")
                response = requests.get(image_url, timeout=30)
                response.raise_for_status()
                image_bytes = response.content
                print(f"{debug_prefix} ✅ fetched via HTTP fallback {image_url} ({len(image_bytes)} bytes)")
            except Exception as e:
                last_error = e
                print(f"{debug_prefix} ⚠️ HTTP fetch failed {image_url}: {e}")

        if not image_bytes:
            print(f"⚠️  Failed to load item image for flat lay: {last_error or 'no image bytes'}")
            print(f"{debug_prefix} ❌ Item will be skipped - no image available from blobs or imageUrl")
            continue

        try:
            source_bytes = image_bytes
            img = Image.open(BytesIO(source_bytes)).convert("RGBA")
        except Exception as e:
            print(f"⚠️  Failed to decode image for flat lay: {e}")
            continue

        # Check if image has transparency (items should already be processed)
        alpha_channel = img.split()[3]
        has_transparency = alpha_channel.getextrema() != (255, 255)
        if alpha_channel.getbbox() is None:
            print(f"{debug_prefix} Empty garment image; request will fail asset validation")
            continue
        
        # Skip background removal during flatlay for performance - items should already be processed
        # If no transparency, skip this item and log a warning (don't block flatlay generation)
        if not has_transparency:
            print(f"{debug_prefix} ⚠️  Item missing transparency - skipping (should be processed first)")
            print(f"{debug_prefix} ℹ️  Item will be processed by worker, then flatlay can be regenerated")
            continue

        # Always crop to the garment silhouette to keep layout math accurate
        img = crop_to_alpha(img)

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


class FlatlayGenerationError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def generate_original_reference_flatlay(references, outfit_id):
    """Send every original garment reference in one paid image-edit request."""
    runtime = get_openai_image_edit_runtime_config()
    files = build_reference_edit_payload(references, str(runtime["model"]), quality=runtime.get("quality"))
    response = requests.post(
        str(runtime["api_url"]), headers=_build_openai_image_edit_headers(), files=files,
        timeout=float(runtime["timeout_seconds"]),
    )
    if not response.ok:
        raise FlatlayGenerationError("provider_failed", "The image service could not finish this preview.")
    image = _load_image_from_openai_image_response(response.json(), f"flatlay:{outfit_id}")
    if image is None or image.width < 512 or image.height < 512 or image.getbbox() is None:
        raise FlatlayGenerationError("empty_provider_result", "The image service returned an incomplete preview.")
    return image


def process_outfit_flat_lay(doc_id: str, data: dict | None = None):
    """Claim the private request, then perform at most one provider attempt."""
    request = claim_request(db, doc_id)
    if request is None:
        metrics['flat_lay_skipped'] += 1
        return
    request_id = request['request_id']
    try:
        if request.get('preflight_error'):
            raise FlatlayGenerationError(request['preflight_error'], "The preview could not start. Please request it again.")
        if openai_client is None:
            raise FlatlayGenerationError("provider_unavailable", "The image service is unavailable. Please try again later.")
        items = request.get('items') or []
        expected_ids = {item.get('id') for item in items}
        if not items or None in expected_ids or len(expected_ids) != len(items):
            raise FlatlayGenerationError("invalid_items", "The outfit items could not be prepared.")
        prepared_originals = prepare_request_originals(request, bucket)
        references = prepare_original_references(items, bucket, request_id=request_id)
        actual_ids = {reference.get('id') for reference in references}
        if actual_ids != expected_ids or len(references) != len(items):
            raise FlatlayGenerationError("missing_original_references", "Some original item photos are unavailable. Please check your wardrobe items.")
        if int(time.time()) >= request['expires_at']:
            raise FlatlayGenerationError("preparation_timeout", "Preparing the item photos took too long. Please try again.")
        if not admit_provider_request(db, doc_id, request_id, prepared_originals):
            raise FlatlayGenerationError("request_changed", "The outfit or its photos changed while preparing the preview. Please request it again.")
        image = generate_original_reference_flatlay(references, doc_id)
        # Each attempt gets a unique object; a late image cannot replace pixels
        # belonging to a newer request. No compositor or automatic retry is used.
        final_url = upload_flatlay_image(image, doc_id, renderer_tag="original_refs_v1", request_id=request_id)
        if not final_url:
            raise FlatlayGenerationError("upload_failed", "The preview could not be saved. Please try again.")
        if finish_request(db, doc_id, request_id, url=final_url, retryable=False):
            metrics['flat_lay_processed'] += 1
            metrics['flat_lay_openai'] += 1
    except Exception as exc:
        # Persist only safe customer-facing errors, never provider payloads/URLs.
        code = exc.code if isinstance(exc, (FlatlayGenerationError, ReferenceImageError)) else "generation_failed"
        message = str(exc) if isinstance(exc, (FlatlayGenerationError, ReferenceImageError)) else "The preview could not be completed. Please try again."
        # A request timeout can mean the provider completed but the response was
        # lost. Return the product credit, but hold another paid attempt for review.
        ambiguous = isinstance(exc, (requests.Timeout, requests.ConnectionError))
        if ambiguous:
            code = "provider_outcome_unknown"
            message = "The image service did not confirm the result. This preview needs review before another request."
        if finish_request(db, doc_id, request_id, error=message, error_code=code, retryable=not ambiguous):
            metrics['flat_lay_failed'] += 1
            metrics['flat_lay_openai_failed'] += 1
        print(f"Flat lay {doc_id} failed ({code}); no automatic provider retry.")


def expire_stale_flatlay_requests():
    """Settle the oldest expired jobs before new work, without paid retries.

    The coordinator runs this independently from garment and flatlay children.
    Storage availability and the polling interval still bound observed recovery.
    Numeric range queries exclude the null expiry on completed requests and use
    a single-field index, so active jobs cannot hide expired jobs in the batch.
    """
    now = int(time.time())
    expired_requests = (
        db.collection(REQUESTS_COLLECTION)
        .where(filter=FieldFilter('expires_at', '>=', 0))
        .where(filter=FieldFilter('expires_at', '<=', now))
        .order_by('expires_at').limit(20).stream(timeout=10, retry=None)
    )
    for doc in expired_requests:
        request = doc.to_dict() or {}
        status = request.get('status')
        if status not in ('pending', 'processing'):
            continue
        pending = status == 'pending'
        finish_request(
            db, doc.id, request.get('request_id'), now=now, expired_only=True,
            error=("The preview could not start in time. Please request it again." if pending else
                   "The image service did not confirm the result. This preview needs review before another request."),
            error_code="queue_timeout" if pending else "worker_outcome_unknown", retryable=pending,
        )


# ----------------------------
# Lightweight coordinator
# ----------------------------
def run_worker():
    from coordinator import WorkerCoordinator
    from process_supervisor import JobProcess
    from garment_lifecycle import (
        claim_garment, finish_garment, publish_original, recover_expired_garments,
        LEASE_SECONDS,
    )
    from flatlay_lifecycle import PROCESSING_TIMEOUT_SECONDS

    worker_id = uuid4().hex
    pending_cursor = None

    def wardrobe_candidates():
        nonlocal pending_cursor
        now = int(time.time())
        # Private due work remains schedulable even if an older client has
        # replaced the public wardrobe status projection.
        due = list(db.collection("garment_processing_jobs")
                   .where(filter=FieldFilter("next_attempt_at", ">=", 0))
                   .where(filter=FieldFilter("next_attempt_at", "<=", now))
                   .order_by("next_attempt_at").limit(25).stream(timeout=10, retry=None))
        query = (db.collection(FIRESTORE_COLLECTION)
                 .where(filter=FieldFilter("processing_status", "==", "pending"))
                 .order_by("__name__").limit(25))
        if pending_cursor is not None:
            query = query.start_after(pending_cursor)
        rows = list(query.stream(timeout=10, retry=None))
        pending_cursor = rows[-1] if rows else None
        return list(dict.fromkeys([doc.id for doc in due] + [doc.id for doc in rows]))

    def flatlay_candidates():
        rows = (db.collection(REQUESTS_COLLECTION)
                .where(filter=FieldFilter("queued_at", ">=", 0))
                .order_by("queued_at").limit(1).stream(timeout=10, retry=None))
        return [doc.id for doc in rows]

    def reconcile_legacy():
        rows = (db.collection("outfits")
                .where(filter=FieldFilter("flat_lay_status", "==", "pending"))
                .limit(20).stream(timeout=10, retry=None))
        for doc in rows:
            # Projection repair must never claim a paid job in the coordinator.
            claim_request(db, doc.id, allow_claim=False)

    def start_garment(claim):
        environment = {key: value for key, value in os.environ.items()
                       if not key.startswith("OPENAI_")}
        remaining = min(LEASE_SECONDS, claim["expires_at"] - time.time())
        if remaining <= 0:
            raise TimeoutError("Garment lease expired before dispatch")
        return JobProcess({"item_id": claim["garment_id"], "attempt_id": claim["attempt_id"],
                           "image_url": claim["source_url"], "bucket_name": FIREBASE_BUCKET_NAME},
                          timeout_seconds=remaining, env=environment)

    def start_flatlay(outfit_id):
        return JobProcess({}, command=[sys.executable, str(Path(__file__).resolve()),
                                       "--flatlay-job", outfit_id],
                          timeout_seconds=PROCESSING_TIMEOUT_SECONDS)

    coordinator = WorkerCoordinator(
        expire_flatlays=expire_stale_flatlay_requests,
        recover_garments=lambda: recover_expired_garments(db),
        garment_candidates=wardrobe_candidates,
        claim_garment=lambda item_id: claim_garment(db, item_id, worker_id),
        start_garment=start_garment,
        publish_original=lambda item_id, attempt_id, original: publish_original(db, item_id, attempt_id, original),
        finish_garment=lambda item_id, attempt_id, **outcome: finish_garment(db, item_id, attempt_id, **outcome),
        flatlay_candidates=flatlay_candidates,
        start_flatlay=start_flatlay,
        legacy_reconcile=reconcile_legacy,
        report=lambda event, fields: print(json.dumps({"schema_version": 1, "event": event, **fields}), flush=True),
    )
    print("Worker coordinator started: independent garment and flatlay slots", flush=True)
    try:
        while True:
            coordinator.tick()
            time.sleep(POLL_INTERVAL)
    finally:
        coordinator.close()


def _shutdown(_signal, _frame):
    raise KeyboardInterrupt


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, _shutdown)
    try:
        if len(sys.argv) == 3 and sys.argv[1] == "--flatlay-job":
            process_outfit_flat_lay(sys.argv[2])
        elif len(sys.argv) == 1:
            run_worker()
        else:
            raise SystemExit("Unsupported worker command")
    except KeyboardInterrupt:
        print("Worker stopped", flush=True)
