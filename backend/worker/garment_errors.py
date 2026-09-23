"""Finite garment failure contract shared by child and coordinator (stdlib only).

Worker exceptions and provider/network messages never cross this boundary.
Values are existing lifecycle codes; a missing envelope is handled separately
as worker_crashed, while an unrecognized supplied code is processing_failed.
"""
SAFE_FAILURE_CODES = frozenset({
    'processing_failed', 'worker_timeout', 'worker_crashed', 'invalid_image',
    'invalid_identifier', 'invalid_result', 'source_changed', 'item_changed',
    'garment_unavailable', 'retry_exhausted',
})

PHOTO_FAILURES = frozenset({
    'unsupported_source', 'source_missing', 'source_decode_failed',
    'source_too_large_or_invalid', 'source_too_large', 'source_too_large_or_empty',
    'source_dimensions_too_large', 'source_image_invalid', 'original_reference_too_large',
})
STORAGE_FAILURES = frozenset({'asset_upload_failed', 'asset_too_large'})


def garment_failure_code(value) -> str:
    if not isinstance(value, str):
        return 'processing_failed'
    if value in SAFE_FAILURE_CODES:
        return value
    if value in PHOTO_FAILURES:
        return 'invalid_image'
    if value == 'invalid_item_id':
        return 'invalid_identifier'
    if value in STORAGE_FAILURES:
        return 'invalid_result'
    # Transient download/inference/configuration failures share a safe retry
    # message. Unknown strings (including exception text/URLs) use it too.
    return 'processing_failed'


# Operational diagnostics never become lifecycle fields or user-facing errors.
# The child, its parent and the coordinator each project through this allowlist.
DIAGNOSTIC_STAGES = frozenset({
    'manifest', 'storage_setup', 'source_download', 'source_normalization',
    'original_prepare', 'original_upload', 'background_removal', 'cutout_validation',
    'cutout_upload', 'processed_upload', 'thumbnail_upload', 'job',
    *[f'{mode}_{stage}' for mode in ('alpha', 'fallback')
      for stage in ('import', 'input', 'removal', 'model_download', 'output', 'process')],
})
DIAGNOSTIC_CATEGORIES = frozenset({
    'dependency_missing', 'import_error', 'network_timeout', 'connection_error',
    'tls_error', 'http_error', 'image_invalid', 'invalid_value', 'memory_error',
    'permission_denied', 'filesystem_error', 'runtime_error', 'model_runtime_error',
    'validation_failed', 'unknown', 'process_timeout', 'process_crashed',
    'process_no_result', 'process_failed', 'output_missing',
})
_EXCEPTION_CATEGORIES = {
    'ModuleNotFoundError': 'dependency_missing', 'ImportError': 'import_error',
    'Timeout': 'network_timeout', 'TimeoutError': 'network_timeout',
    'ConnectTimeout': 'network_timeout', 'ReadTimeout': 'network_timeout',
    'ConnectionError': 'connection_error', 'URLError': 'connection_error',
    'SSLError': 'tls_error', 'SSLCertVerificationError': 'tls_error',
    'HTTPError': 'http_error', 'UnidentifiedImageError': 'image_invalid',
    'ValueError': 'invalid_value', 'TypeError': 'invalid_value',
    'MemoryError': 'memory_error', 'PermissionError': 'permission_denied',
    'FileNotFoundError': 'filesystem_error', 'OSError': 'filesystem_error',
    'RuntimeError': 'runtime_error', 'GarmentJobError': 'validation_failed',
    'Fail': 'model_runtime_error', 'InvalidArgument': 'model_runtime_error',
    'RuntimeException': 'model_runtime_error', 'InvalidProtobuf': 'model_runtime_error',
    'NoSuchFile': 'model_runtime_error', 'EPFail': 'model_runtime_error',
}
_MODEL_DOWNLOAD_FRAMES = frozenset({
    ('pooch.core', 'retrieve'), ('pooch.core', 'stream_download'),
    ('pooch.downloaders', '__call__'),
    ('rembg.sessions.u2net', 'download_models'),
    ('rembg.sessions.u2netp', 'download_models'),
})


def _project_diagnostics(value) -> list[dict]:
    if not isinstance(value, (list, tuple)):
        return []
    result = []
    for entry in value[:2]:
        if not isinstance(entry, dict):
            continue
        stage, category = entry.get('stage'), entry.get('category')
        if not isinstance(stage, str) or stage not in DIAGNOSTIC_STAGES:
            continue
        if not isinstance(category, str) or category not in DIAGNOSTIC_CATEGORIES:
            continue
        safe = {'stage': stage, 'category': category}
        status = entry.get('http_status')
        if type(status) is int and 400 <= status <= 599:
            safe['http_status'] = status
        result.append(safe)
    return result


def safe_diagnostics(value) -> list[dict]:
    try:
        return _project_diagnostics(value)
    except Exception:
        return []


def _optional_attribute(value, name):
    try:
        return getattr(value, name, None)
    except Exception:
        return None


def exception_diagnostics(error) -> list[dict]:
    return safe_diagnostics(_optional_attribute(error, 'diagnostics'))


def exception_diagnostic(stage: str, error: Exception) -> dict:
    # SDK/custom exception properties are not guaranteed to be readable. An
    # instrumentation failure must never replace the original safe job failure.
    try:
        return _exception_diagnostic(stage, error)
    except Exception:
        return {'stage': 'job', 'category': 'unknown'}


def _exception_diagnostic(stage: str, error: Exception) -> dict:
    """Inspect at most four causes/24 frames each; never copy messages or locals."""
    category, http_status, model_download = 'unknown', None, False
    seen = set()
    for _ in range(4):
        if error is None or id(error) in seen:
            break
        seen.add(id(error))
        known = _EXCEPTION_CATEGORIES.get(type(error).__name__)
        if known:
            category = known
        if known == 'http_error':
            response = _optional_attribute(error, 'response')
            for candidate in (_optional_attribute(response, 'status_code'),
                              _optional_attribute(error, 'status_code'), _optional_attribute(error, 'code')):
                if type(candidate) is int and 400 <= candidate <= 599:
                    http_status = candidate
                    break
        traceback = error.__traceback__
        for _ in range(24):
            if traceback is None:
                break
            frame = traceback.tb_frame
            if (frame.f_globals.get('__name__'), frame.f_code.co_name) in _MODEL_DOWNLOAD_FRAMES:
                model_download = True
            traceback = traceback.tb_next
        error = error.__cause__ or error.__context__
    if model_download and stage in ('alpha_removal', 'fallback_removal'):
        stage = stage.replace('_removal', '_model_download')
    values = {'stage': stage, 'category': category}
    if http_status is not None:
        values['http_status'] = http_status
    projected = safe_diagnostics([values])
    return projected[0] if projected else {'stage': 'job', 'category': 'unknown'}
