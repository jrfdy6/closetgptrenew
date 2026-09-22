"""Disposable garment job. No Firestore writes and no paid provider calls.

The coordinator supplies {item_id, attempt_id, image_url, bucket_name?}. All
assets are immutable and scoped to that attempt. An atomic progress manifest
publishes the original reference before background removal. Only the fenced
coordinator decides whether any returned URLs may be written to wardrobe.

Both alpha and fallback inference run in fresh processes. This job imports PIL
but never imports rembg except when explicitly invoked in --infer child mode.
"""
from __future__ import annotations

import argparse
import base64
from io import BytesIO
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time
import warnings

from PIL import Image, ImageOps

try:
    from .process_supervisor import JobProcess, atomic_json
    from .garment_errors import garment_failure_code
except ImportError:
    from process_supervisor import JobProcess, atomic_json
    from garment_errors import garment_failure_code

ALPHA_TIMEOUT_SECONDS = 240
FALLBACK_TIMEOUT_SECONDS = 60
WHOLE_JOB_TIMEOUT_SECONDS = 360
MAX_DOWNLOAD_BYTES = 20 * 1024 * 1024
MAX_SOURCE_PIXELS = 40_000_000
MAX_REFERENCE_IMAGE_PIXELS = 16_777_216
MAX_REFERENCE_IMAGE_BYTES = 50_000_000
STORAGE_TIMEOUT_SECONDS = 20
DOWNLOAD_TIMEOUT_SECONDS = (5, 20)
DEFAULT_BUCKET_NAME = 'closetgptrenew.firebasestorage.app'
_SAFE_ID = re.compile(r'[A-Za-z0-9_-][A-Za-z0-9_.-]{0,127}\Z')


class GarmentJobError(Exception):
    """Stable safe error code; never includes private URLs, credentials or pixels."""


def resize_image(image: Image.Image, max_width: int, max_height: int) -> Image.Image:
    scale = min(max_width / image.width, max_height / image.height, 1.0)
    if scale < 1:
        return image.resize((max(1, int(image.width * scale)), max(1, int(image.height * scale))),
                            Image.Resampling.LANCZOS)
    return image


def png_bytes(image: Image.Image) -> bytes:
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    return buffer.getvalue()


def constrain_original_reference_image(image: Image.Image, *,
                                       max_pixels=MAX_REFERENCE_IMAGE_PIXELS,
                                       max_bytes=MAX_REFERENCE_IMAGE_BYTES) -> Image.Image:
    bounded = image
    if image.width * image.height > max_pixels:
        edge_limit = max(1, int(max_pixels ** 0.5))
        bounded = resize_image(image, edge_limit, edge_limit)
    for _ in range(12):
        if len(png_bytes(bounded)) < max_bytes:
            return bounded
        bounded = resize_image(bounded, max(1, int(bounded.width * .85)),
                               max(1, int(bounded.height * .85)))
    raise GarmentJobError('original_reference_too_large')


def generate_thumbnail(image: Image.Image, size=(512, 512)) -> Image.Image:
    canvas = Image.new('RGBA', size, (0, 0, 0, 0))
    scale = min(size[0] / image.width, size[1] / image.height)
    resized = image.resize((max(1, int(image.width * scale)), max(1, int(image.height * scale))),
                           Image.Resampling.LANCZOS)
    canvas.alpha_composite(resized.convert('RGBA'), ((size[0] - resized.width) // 2,
                                                   (size[1] - resized.height) // 2))
    return canvas


def download_image(url: str) -> bytes:
    if url.startswith('data:image/'):
        try:
            header, encoded = url.split(',', 1)
            if not header.endswith(';base64') or len(encoded) > ((MAX_DOWNLOAD_BYTES + 2) // 3) * 4:
                raise GarmentJobError('source_too_large_or_invalid')
            value = base64.b64decode(encoded, validate=True)
        except (ValueError, TypeError) as exc:
            raise GarmentJobError('source_decode_failed') from exc
    elif url.lower().startswith(('https://', 'http://')):
        import requests
        try:
            with requests.get(url, timeout=DOWNLOAD_TIMEOUT_SECONDS, stream=True) as response:
                response.raise_for_status()
                raw_length = response.headers.get('Content-Length')
                if raw_length and int(raw_length) > MAX_DOWNLOAD_BYTES:
                    raise GarmentJobError('source_too_large')
                chunks, total = [], 0
                for chunk in response.iter_content(chunk_size=64 * 1024):
                    total += len(chunk)
                    if total > MAX_DOWNLOAD_BYTES:
                        raise GarmentJobError('source_too_large')
                    chunks.append(chunk)
                value = b''.join(chunks)
        except GarmentJobError:
            raise
        except Exception as exc:
            raise GarmentJobError('source_download_failed') from exc
    else:
        raise GarmentJobError('unsupported_source')
    if not value or len(value) > MAX_DOWNLOAD_BYTES:
        raise GarmentJobError('source_too_large_or_empty')
    return value


def normalize_source(source_bytes: bytes) -> Image.Image:
    if not isinstance(source_bytes, bytes) or not source_bytes or len(source_bytes) > MAX_DOWNLOAD_BYTES:
        raise GarmentJobError('source_too_large_or_empty')
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(BytesIO(source_bytes)) as opened:
                if opened.width * opened.height > MAX_SOURCE_PIXELS:
                    raise GarmentJobError('source_dimensions_too_large')
                return ImageOps.exif_transpose(opened).convert('RGBA')
    except GarmentJobError:
        raise
    except Exception as exc:
        raise GarmentJobError('source_image_invalid') from exc


def _validate_cutout(output: bytes) -> Image.Image:
    try:
        if not output or len(output) >= MAX_REFERENCE_IMAGE_BYTES:
            raise ValueError('size')
        with Image.open(BytesIO(output)) as opened:
            if opened.width * opened.height > MAX_REFERENCE_IMAGE_PIXELS:
                raise ValueError('dimensions')
            clean = opened.convert('RGBA')
        if clean.getchannel('A').getbbox() is None:
            raise ValueError('empty')
        return clean
    except Exception as exc:
        raise GarmentJobError('background_removal_invalid') from exc


def _run_inference(mode: str, source_path: Path, output_path: Path, timeout: float,
                   *, job_factory=JobProcess) -> bytes:
    child_env = dict(os.environ)
    child_env.pop('OPENAI_API_KEY', None)
    job = job_factory({}, command=[sys.executable, str(Path(__file__).resolve()),
                                  '--infer', mode, str(source_path), str(output_path)],
                      timeout_seconds=timeout, env=child_env)
    try:
        while True:
            summary = job.poll()
            if summary is not None:
                if summary['status'] != 'succeeded' or not output_path.exists():
                    raise GarmentJobError(f'{mode}_inference_failed')
                if output_path.stat().st_size >= MAX_REFERENCE_IMAGE_BYTES:
                    raise GarmentJobError(f'{mode}_inference_output_too_large')
                return output_path.read_bytes()
            time.sleep(.05)
    finally:
        job.close()


def isolated_remove(source: bytes, *, run_inference=_run_inference) -> tuple[bytes, str]:
    with tempfile.TemporaryDirectory(prefix='garment-inference-') as temporary:
        directory = Path(temporary)
        source_path, output_path = directory / 'input.png', directory / 'output.png'
        source_path.write_bytes(source)
        try:
            output = run_inference('alpha', source_path, output_path, ALPHA_TIMEOUT_SECONDS)
            _validate_cutout(output)
            return output, 'alpha'
        except GarmentJobError:
            output_path.unlink(missing_ok=True)
            output = run_inference('fallback', source_path, output_path, FALLBACK_TIMEOUT_SECONDS)
            _validate_cutout(output)
            return output, 'fast'


def process_garment(payload: dict, *, upload, progress=lambda value: None,
                    download=download_image, remove_background=isolated_remove,
                    clock=time.monotonic) -> dict:
    started = clock()
    item_id, attempt_id = payload.get('item_id'), payload.get('attempt_id')
    if not isinstance(item_id, str) or not _SAFE_ID.fullmatch(item_id):
        raise GarmentJobError('invalid_item_id')
    if not isinstance(attempt_id, str) or not _SAFE_ID.fullmatch(attempt_id):
        raise GarmentJobError('invalid_attempt_id')
    source_url = payload.get('image_url')
    if not isinstance(source_url, str) or not source_url:
        raise GarmentJobError('source_missing')
    source_bytes = download(source_url)
    image = normalize_source(source_bytes)
    original_size = image.size
    original = constrain_original_reference_image(image)
    prefix = f'items/{item_id}/attempts/{attempt_id}'
    original_path = f'{prefix}/original.png'
    original_url = upload(original, original_path)
    original_fields = {'originalStoragePath': original_path, 'originalUrl': original_url}
    progress(original_fields)
    working = original
    if len(source_bytes) > 5 * 1024 * 1024 or max(original_size) > 2048:
        working = resize_image(original, 2048, 2048)
    if working.getchannel('A').getextrema()[0] < 255:
        clean, mode = working, 'preserved'
        if clean.getchannel('A').getbbox() is None:
            raise GarmentJobError('background_removal_invalid')
    else:
        output, mode = remove_background(png_bytes(working))
        clean = _validate_cutout(output)
    # Canonical clean evidence receives no crop, shadow, RGB whitening or alpha
    # amplification. processed.png is only the smaller compatibility asset.
    clean_path = f'{prefix}/nobg.png'
    clean_url = upload(clean, clean_path)
    processed = resize_image(clean, 1024, 1024)
    processed_path, thumbnail_path = f'{prefix}/processed.png', f'{prefix}/thumbnail.png'
    processed_url = upload(processed, processed_path)
    thumbnail_url = upload(generate_thumbnail(processed), thumbnail_path)
    return {**original_fields, 'backgroundRemovedStoragePath': clean_path,
            'backgroundRemovedUrl': clean_url, 'processedStoragePath': processed_path,
            'processedUrl': processed_url, 'thumbnailStoragePath': thumbnail_path,
            'thumbnailUrl': thumbnail_url, 'processing_mode': mode,
            'processing_time': max(0, clock() - started),
            'original_size': f'{original_size[0]}x{original_size[1]}',
            'processed_size': f'{processed.width}x{processed.height}'}


def firebase_uploader(bucket_name: str):
    # Initialized inside the disposable job only, never in inference children.
    import firebase_admin
    from firebase_admin import credentials, storage
    try:
        app = firebase_admin.get_app()
    except ValueError:
        credential = {'type': 'service_account',
                      'project_id': os.environ.get('FIREBASE_PROJECT_ID'),
                      'private_key': os.environ.get('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
                      'client_email': os.environ.get('FIREBASE_CLIENT_EMAIL'),
                      'token_uri': 'https://oauth2.googleapis.com/token'}
        if not all(credential.get(key) for key in ('project_id', 'private_key', 'client_email')):
            raise GarmentJobError('storage_configuration_missing')
        app = firebase_admin.initialize_app(credentials.Certificate(credential), {'storageBucket': bucket_name})
    bucket = storage.bucket(bucket_name, app=app)

    def upload(image: Image.Image, path: str) -> str:
        encoded = png_bytes(image)
        if len(encoded) >= MAX_REFERENCE_IMAGE_BYTES:
            raise GarmentJobError('asset_too_large')
        try:
            blob = bucket.blob(path)
            blob.upload_from_string(encoded, content_type='image/png', if_generation_match=0,
                                    timeout=STORAGE_TIMEOUT_SECONDS, retry=None)
            blob.make_public(timeout=STORAGE_TIMEOUT_SECONDS, retry=None)
            return blob.public_url
        except Exception as exc:
            raise GarmentJobError('asset_upload_failed') from exc
    return upload


def infer(mode: str, source_path: str, output_path: str) -> None:
    # The only rembg import in this module. The caller always bounds this child.
    os.environ.setdefault('OMP_NUM_THREADS', '1')
    from rembg import remove
    source = Path(source_path).read_bytes()
    if len(source) >= MAX_REFERENCE_IMAGE_BYTES:
        raise GarmentJobError('inference_input_too_large')
    kwargs = ({'alpha_matting': True, 'alpha_matting_foreground_threshold': 240,
               'alpha_matting_background_threshold': 10, 'alpha_matting_erode_size': 10}
              if mode == 'alpha' else {})
    output = remove(source, **kwargs)
    if not isinstance(output, bytes) or len(output) >= MAX_REFERENCE_IMAGE_BYTES:
        raise GarmentJobError('inference_output_invalid')
    Path(output_path).write_bytes(output)


def main() -> int:
    if len(sys.argv) == 5 and sys.argv[1] == '--infer' and sys.argv[2] in ('alpha', 'fallback'):
        try:
            infer(sys.argv[2], sys.argv[3], sys.argv[4])
            return 0
        except Exception:
            print('garment_inference_failed', file=sys.stderr)
            return 1
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--result', required=True)
    parser.add_argument('--progress', required=True)
    args = parser.parse_args()
    try:
        path = Path(args.manifest)
        if path.stat().st_size > 30 * 1024 * 1024:
            raise GarmentJobError('manifest_too_large')
        payload = json.loads(path.read_text())
        if not isinstance(payload, dict):
            raise GarmentJobError('manifest_invalid')
        result = process_garment(payload, upload=firebase_uploader(payload.get('bucket_name') or DEFAULT_BUCKET_NAME),
                                 progress=lambda value: atomic_json(args.progress, value))
        atomic_json(args.result, result)
        return 0
    except Exception as exc:
        error = garment_failure_code(str(exc) if isinstance(exc, GarmentJobError) else None)
        atomic_json(args.result, {'status': 'failed', 'error_code': error})
        print(error, file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
