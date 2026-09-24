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
    from .garment_errors import garment_failure_code, safe_diagnostics, exception_diagnostic, exception_diagnostics
    from .garment_errors import process_exit_category, inference_progress_stage
except ImportError:
    from process_supervisor import JobProcess, atomic_json
    from garment_errors import garment_failure_code, safe_diagnostics, exception_diagnostic, exception_diagnostics
    from garment_errors import process_exit_category, inference_progress_stage

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

    def __init__(self, code, *, diagnostics=()):
        super().__init__(code)
        self.diagnostics = safe_diagnostics(diagnostics)


def _stage(stage, action):
    try:
        return action()
    except Exception as exc:
        existing = exception_diagnostics(exc)
        code = str(exc) if isinstance(exc, GarmentJobError) else 'processing_failed'
        raise GarmentJobError(code, diagnostics=existing or [exception_diagnostic(stage, exc)]) from exc


def _inference_manifest(path, value):
    # Diagnostics are best effort: a manifest I/O error must neither change a
    # successful cutout nor print a traceback containing a prior private cause.
    try:
        atomic_json(path, value)
    except Exception:
        pass


def _memory_events():
    """Best-effort fixed cgroup-v2 counters; never expose file contents or paths."""
    try:
        with open('/sys/fs/cgroup/memory.events', 'rb') as stream:
            raw = stream.read(4097)
        if len(raw) > 4096:
            return None
        counters = {}
        for line in raw.splitlines():
            fields = line.split()
            if not fields or fields[0] not in (b'oom', b'oom_kill'):
                continue
            if (len(fields) != 2 or fields[0] in counters or len(fields[1]) > 19 or
                    not fields[1].isdigit() or int(fields[1]) > 2**63 - 1):
                return None
            counters[fields[0]] = int(fields[1])
        return counters if set(counters) == {b'oom', b'oom_kill'} else None
    except Exception:
        return None


def _memory_event_deltas(before, after):
    # These counters belong to the container. A delta overlaps the inference
    # interval but does not prove this child caused or suffered an OOM event.
    try:
        if not isinstance(before, dict) or not isinstance(after, dict):
            return {}
        result = {}
        for key, field in ((b'oom', 'container_oom_delta'), (b'oom_kill', 'container_oom_kill_delta')):
            first, last = before.get(key), after.get(key)
            if any(type(value) is not int or not 0 <= value <= 2**63 - 1 for value in (first, last)):
                return {}
            delta = last - first
            if not 0 <= delta <= 2**31 - 1:
                return {}
            result[field] = delta
        return result
    except Exception:
        return {}


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
    memory_before = _memory_events()
    job = job_factory({}, command=[sys.executable, str(Path(__file__).resolve()),
                                  '--infer', mode, str(source_path), str(output_path), '{result}', '{progress}'],
                      timeout_seconds=timeout, env=child_env)
    try:
        while True:
            summary = job.poll()
            if summary is not None:
                memory_deltas = _memory_event_deltas(memory_before, _memory_events())
                if summary['status'] != 'succeeded' or not output_path.exists():
                    result = summary.get('result')
                    result = result if isinstance(result, dict) else {}
                    diagnostics = safe_diagnostics(result.get('diagnostics'))
                    code = summary.get('returncode')
                    category = ('process_timeout' if summary['status'] == 'timed_out' else
                                process_exit_category(code) if type(code) is not int or code != 0 else
                                'process_no_result' if not result else
                                'output_missing' if summary['status'] == 'succeeded' else 'process_failed')
                    diagnostics = diagnostics or [
                        {'stage': inference_progress_stage(mode, summary.get('progress')), 'category': category}]
                    diagnostics[-1] = {**diagnostics[-1], **memory_deltas}
                    raise GarmentJobError(f'{mode}_inference_failed', diagnostics=diagnostics)
                if output_path.stat().st_size >= MAX_REFERENCE_IMAGE_BYTES:
                    raise GarmentJobError(f'{mode}_inference_output_too_large', diagnostics=[
                        {'stage': f'{mode}_output', 'category': 'validation_failed'}])
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
        except GarmentJobError as alpha_error:
            output_path.unlink(missing_ok=True)
            try:
                output = run_inference('fallback', source_path, output_path, FALLBACK_TIMEOUT_SECONDS)
                _stage('fallback_output', lambda: _validate_cutout(output))
                return output, 'fast'
            except GarmentJobError as fallback_error:
                alpha = exception_diagnostics(alpha_error) or [exception_diagnostic('alpha_output', alpha_error)]
                fallback = exception_diagnostics(fallback_error) or [exception_diagnostic('fallback_output', fallback_error)]
                raise GarmentJobError(str(fallback_error), diagnostics=[alpha[-1], fallback[-1]]) from fallback_error


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
    source_bytes = _stage('source_download', lambda: download(source_url))
    image = _stage('source_normalization', lambda: normalize_source(source_bytes))
    original_size = image.size
    original = _stage('original_prepare', lambda: constrain_original_reference_image(image))
    prefix = f'items/{item_id}/attempts/{attempt_id}'
    original_path = f'{prefix}/original.png'
    original_url = _stage('original_upload', lambda: upload(original, original_path))
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
        output, mode = _stage('background_removal', lambda: remove_background(png_bytes(working)))
        clean = _stage('cutout_validation', lambda: _validate_cutout(output))
    # Canonical clean evidence receives no crop, shadow, RGB whitening or alpha
    # amplification. processed.png is only the smaller compatibility asset.
    clean_path = f'{prefix}/nobg.png'
    clean_url = _stage('cutout_upload', lambda: upload(clean, clean_path))
    processed = resize_image(clean, 1024, 1024)
    processed_path, thumbnail_path = f'{prefix}/processed.png', f'{prefix}/thumbnail.png'
    processed_url = _stage('processed_upload', lambda: upload(processed, processed_path))
    thumbnail_url = _stage('thumbnail_upload', lambda: upload(generate_thumbnail(processed), thumbnail_path))
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


def infer(mode: str, source_path: str, output_path: str, *, progress_path=None) -> None:
    # The only rembg import in this module. The caller always bounds this child.
    os.environ.setdefault('OMP_NUM_THREADS', '1')
    def load_rembg():
        from rembg import new_session, remove
        return new_session, remove
    if progress_path is not None:
        _inference_manifest(progress_path, {'stage': f'{mode}_import'})
    new_session, remove = _stage(f'{mode}_import', load_rembg)
    if progress_path is not None:
        _inference_manifest(progress_path, {'stage': f'{mode}_input'})
    source = _stage(f'{mode}_input', lambda: Path(source_path).read_bytes())
    if len(source) >= MAX_REFERENCE_IMAGE_BYTES:
        raise GarmentJobError('inference_input_too_large', diagnostics=[
            {'stage': f'{mode}_input', 'category': 'validation_failed'}])
    if progress_path is not None:
        _inference_manifest(progress_path, {'stage': f'{mode}_session'})
    session = _stage(f'{mode}_session', lambda: new_session('u2net'))
    kwargs = ({'alpha_matting': True, 'alpha_matting_foreground_threshold': 240,
               'alpha_matting_background_threshold': 10, 'alpha_matting_erode_size': 10}
              if mode == 'alpha' else {})
    if progress_path is not None:
        _inference_manifest(progress_path, {'stage': f'{mode}_removal'})
    output = _stage(f'{mode}_removal', lambda: remove(source, session=session, **kwargs))
    if progress_path is not None:
        _inference_manifest(progress_path, {'stage': f'{mode}_output'})
    if not isinstance(output, bytes) or len(output) >= MAX_REFERENCE_IMAGE_BYTES:
        raise GarmentJobError('inference_output_invalid', diagnostics=[
            {'stage': f'{mode}_output', 'category': 'validation_failed'}])
    _stage(f'{mode}_output', lambda: Path(output_path).write_bytes(output))


def main() -> int:
    if len(sys.argv) in (5, 6, 7) and sys.argv[1] == '--infer' and sys.argv[2] in ('alpha', 'fallback'):
        try:
            infer(sys.argv[2], sys.argv[3], sys.argv[4], progress_path=sys.argv[6] if len(sys.argv) == 7 else None)
            if len(sys.argv) >= 6:
                _inference_manifest(sys.argv[5], {'status': 'succeeded'})
            return 0
        except Exception as exc:
            if len(sys.argv) >= 6:
                diagnostics = exception_diagnostics(exc) or [
                    exception_diagnostic(f'{sys.argv[2]}_process', exc)]
                _inference_manifest(sys.argv[5], {'status': 'failed', 'diagnostics': diagnostics})
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
        uploader = _stage('storage_setup', lambda: firebase_uploader(payload.get('bucket_name') or DEFAULT_BUCKET_NAME))
        result = process_garment(payload, upload=uploader,
                                 progress=lambda value: atomic_json(args.progress, value))
        atomic_json(args.result, result)
        return 0
    except Exception as exc:
        error = garment_failure_code(str(exc) if isinstance(exc, GarmentJobError) else None)
        diagnostics = exception_diagnostics(exc) or [exception_diagnostic('job', exc)]
        atomic_json(args.result, {'status': 'failed', 'error_code': error, 'diagnostics': diagnostics})
        print(error, file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
