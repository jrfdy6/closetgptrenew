"""Parse owned raw-upload references without fetching a URL or trusting its host.

Only the two URL formats produced by the wardrobe upload routes are admitted.
The caller supplies the verified user ID and configured bucket; the returned
object name is read through that bucket's SDK, never through HTTP redirects.
"""
import re
from urllib.parse import parse_qsl, unquote, urlsplit


DEFAULT_BUCKET_NAME = "closetgptrenew.firebasestorage.app"
_ITEM_ID = re.compile(r"[A-Za-z0-9_-][A-Za-z0-9_.-]{0,127}\Z")
_REQUEST_ID = re.compile(r"[A-Za-z0-9_-]{1,128}\Z")
_BUCKET_NAME = re.compile(r"[a-z0-9][a-z0-9._-]{1,220}[a-z0-9]\Z")
_BAD_ESCAPE = re.compile(r"%(?![0-9A-Fa-f]{2})")


def _has_control(value):
    return any(ord(character) < 32 or ord(character) == 127 for character in value)


def is_owned_upload_path(path, user_id) -> bool:
    """Validate an already-decoded descriptor; never decode it a second time."""
    if (not isinstance(path, str) or not isinstance(user_id, str)
            or not 1 <= len(user_id) <= 128 or user_id.strip() != user_id
            or user_id in {".", ".."}
            or any(character in user_id for character in "/\\%")
            or _has_control(user_id) or _has_control(path)
            or "%" in path or "\\" in path):
        return False
    parts = path.split("/")
    return (len(parts) == 3 and parts[0] == "wardrobe" and parts[1] == user_id
            and bool(parts[2].strip()) and parts[2] not in {".", ".."})


def _firebase_query_allowed(query):
    if not query:
        return True
    if _BAD_ESCAPE.search(query):
        return False
    try:
        pairs = parse_qsl(query, keep_blank_values=True, strict_parsing=True,
                          encoding="utf-8", errors="strict", max_num_fields=2)
    except (ValueError, UnicodeError):
        return False
    keys = [key for key, _ in pairs]
    if len(set(keys)) != len(keys) or any(key not in {"alt", "token"} for key in keys):
        return False
    return all(value == "media" if key == "alt" else bool(value) and not _has_control(value)
               for key, value in pairs)


def owned_upload_source(source_url, user_id, bucket_name=DEFAULT_BUCKET_NAME) -> dict | None:
    """Return the exact owned raw object, or None for an untrusted reference.

    Decode the object name once. Residual percent escapes, traversal, nested
    leaves, foreign user prefixes and all other bucket/host combinations fail
    closed. Firebase download tokens are syntax only, never access authority.
    """
    if (not isinstance(source_url, str) or not source_url or len(source_url) > 8192
            or _has_control(source_url) or source_url.strip() != source_url
            or " " in source_url or "\\" in source_url
            or not isinstance(bucket_name, str) or not _BUCKET_NAME.fullmatch(bucket_name)):
        return None
    try:
        parsed = urlsplit(source_url)
    except ValueError:
        return None
    if parsed.scheme != "https" or parsed.fragment or "#" in source_url:
        return None

    # Exact netloc rejects userinfo, explicit ports, suffix lookalikes and dots.
    if parsed.netloc == "storage.googleapis.com":
        prefix = f"/{bucket_name}/"
        if not parsed.path.startswith(prefix) or parsed.query or "?" in source_url:
            return None
    elif parsed.netloc == "firebasestorage.googleapis.com":
        prefix = f"/v0/b/{bucket_name}/o/"
        if not parsed.path.startswith(prefix) or not _firebase_query_allowed(parsed.query):
            return None
    else:
        return None

    encoded_path = parsed.path[len(prefix):]
    if _BAD_ESCAPE.search(encoded_path):
        return None
    try:
        object_path = unquote(encoded_path, encoding="utf-8", errors="strict")
    except UnicodeError:
        return None
    if not is_owned_upload_path(object_path, user_id):
        return None
    return {"bucket": bucket_name, "sourceStoragePath": object_path}


def request_original_path(item_id, request_id) -> str:
    """Build a request-specific immutable original location from safe IDs."""
    if (not isinstance(item_id, str) or not _ITEM_ID.fullmatch(item_id)
            or not isinstance(request_id, str) or not _REQUEST_ID.fullmatch(request_id)):
        raise ValueError("Invalid original reference identifiers")
    return f"items/{item_id}/flatlay-requests/{request_id}/original.png"
