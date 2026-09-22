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
