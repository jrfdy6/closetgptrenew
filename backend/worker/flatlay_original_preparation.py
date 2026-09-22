"""Prepare reserved originals without waiting for garment background removal.

Only an exact, owned object in the configured Firebase bucket can be read. This
runs inside the existing bounded flatlay child, performs no inference/HTTP, and
never edits wardrobe or garment jobs. New PNGs are private, immutable objects
scoped to the reserved flatlay request. A failure returns no partial report.
"""
from hashlib import sha256
from io import BytesIO

from PIL import Image

try:
    from .original_source import DEFAULT_BUCKET_NAME, is_owned_upload_path, request_original_path
    from .garment_job import (MAX_DOWNLOAD_BYTES, normalize_source,
                              constrain_original_reference_image, png_bytes)
    from .flatlay_reference_images import (
        ReferenceImageError, _validated_items, _validate_image_bytes,
        MAX_TOTAL_REFERENCE_BYTES, MAX_TOTAL_REFERENCE_PIXELS, STORAGE_READ_TIMEOUT_SECONDS,
    )
except ImportError:
    from original_source import DEFAULT_BUCKET_NAME, is_owned_upload_path, request_original_path
    from garment_job import (MAX_DOWNLOAD_BYTES, normalize_source,
                             constrain_original_reference_image, png_bytes)
    from flatlay_reference_images import (
        ReferenceImageError, _validated_items, _validate_image_bytes,
        MAX_TOTAL_REFERENCE_BYTES, MAX_TOTAL_REFERENCE_PIXELS, STORAGE_READ_TIMEOUT_SECONDS,
    )

STORAGE_WRITE_TIMEOUT_SECONDS = 20


def _error(code, message):
    return ReferenceImageError(code, message)


def _read_source(bucket, path):
    try:
        blob = bucket.blob(path)
        blob.reload(timeout=STORAGE_READ_TIMEOUT_SECONDS, retry=None)
        size, generation = blob.size, blob.generation
    except Exception:
        raise _error('original_source_unavailable', 'An original item photo could not be loaded. Please try again later.') from None
    if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
        raise _error('invalid_original_image', 'An original item photo is empty or unreadable.')
    if size > MAX_DOWNLOAD_BYTES:
        raise _error('original_image_too_large', 'An original item photo is too large to prepare safely.')
    text_generation = str(generation)
    if (not isinstance(generation, (str, int)) or isinstance(generation, bool)
            or not 1 <= len(text_generation) <= 30 or not text_generation.isascii()
            or not text_generation.isdigit() or int(text_generation) <= 0):
        raise _error('original_source_unavailable', 'An original item photo could not be confirmed. Please try again later.')
    try:
        raw = blob.download_as_bytes(timeout=STORAGE_READ_TIMEOUT_SECONDS, retry=None,
                                     if_generation_match=int(text_generation))
    except Exception:
        raise _error('original_source_unavailable', 'An original item photo changed or could not be loaded. Please try again.') from None
    if not isinstance(raw, bytes) or len(raw) != size:
        raise _error('original_image_changed', 'An original item photo changed while it was being prepared. Please try again.')
    return raw, text_generation


def _normalize(raw):
    try:
        # Do not turn an animated upload into a misleading single-frame source.
        with Image.open(BytesIO(raw)) as source:
            if getattr(source, 'n_frames', 1) != 1:
                raise _error('animated_original_image', 'Use a still original photo for this wardrobe item.')
        image = constrain_original_reference_image(normalize_source(raw))
        encoded = png_bytes(image)
        pixels = _validate_image_bytes(encoded)
        return encoded, pixels
    except ReferenceImageError:
        raise
    except Exception:
        raise _error('invalid_original_image', 'An original item photo is incomplete or unreadable.') from None


def prepare_request_originals(request, bucket) -> list[dict]:
    if not isinstance(request, dict):
        raise _error('invalid_original_preparation', 'The original item photos could not be identified safely.')
    items = _validated_items(request.get('items'))
    descriptors = []
    for identifier, item in items:
        preparation = item.get('originalPreparation')
        if preparation is None:
            continue
        if (not isinstance(preparation, dict) or preparation.get('bucket') != DEFAULT_BUCKET_NAME
                or getattr(bucket, 'name', None) != DEFAULT_BUCKET_NAME
                or not is_owned_upload_path(preparation.get('sourceStoragePath'), request.get('user_id'))):
            raise _error('invalid_original_preparation', 'An original item photo could not be identified safely.')
        try:
            target = request_original_path(identifier, request.get('request_id'))
        except (ValueError, TypeError):
            raise _error('invalid_original_path', 'An original item photo could not be identified safely.') from None
        if item.get('originalStoragePath') != target:
            raise _error('invalid_original_path', 'An original item photo could not be identified safely.')
        descriptors.append((identifier, preparation['sourceStoragePath'], target))

    # Complete validation/normalization for every requested source before writing
    # any output; partial bytes can never become a partial provider input list.
    prepared = []
    total_bytes = total_pixels = 0
    for identifier, source_path, target in descriptors:
        raw, generation = _read_source(bucket, source_path)
        encoded, pixels = _normalize(raw)
        total_bytes += len(encoded)
        total_pixels += pixels
        if total_bytes > MAX_TOTAL_REFERENCE_BYTES:
            raise _error('reference_images_too_large', 'These original photos are too large to prepare together.')
        if total_pixels > MAX_TOTAL_REFERENCE_PIXELS:
            raise _error('reference_images_dimensions_too_large', 'These original photos have too much image detail to prepare together.')
        prepared.append((encoded, {'id': identifier, 'sourceStoragePath': source_path,
                                   'sourceGeneration': generation, 'originalStoragePath': target,
                                   'sha256': sha256(encoded).hexdigest()}))

    for encoded, report in prepared:
        try:
            blob = bucket.blob(report['originalStoragePath'])
            blob.upload_from_string(encoded, content_type='image/png', if_generation_match=0,
                                    predefined_acl='private', timeout=STORAGE_WRITE_TIMEOUT_SECONDS, retry=None)
            # No public ACL: only the server's original-reference loader reads it.
        except Exception:
            raise _error('original_preparation_failed', 'An original item photo could not be prepared. Please try again later.') from None
    return [report for _, report in prepared]
