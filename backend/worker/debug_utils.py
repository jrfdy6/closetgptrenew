import os
import json
import traceback

# Enable/disable globally via env
DEBUG_FLATLAY = os.getenv("DEBUG_FLATLAY", "1") == "1"


def debug_val(label, value):
    """Print rich debug output with repr + type + safety wrapper."""
    if not DEBUG_FLATLAY:
        return
    try:
        print(f"[flatlay:DEBUG] {label}: {value!r} (type={type(value)})")
    except Exception as e:
        print(f"[flatlay:DEBUG] Print failed for {label}: {e}")


def debug_section(title):
    """Print section header for readability."""
    if DEBUG_FLATLAY:
        print(f"\n===== [flatlay:DEBUG] {title} =====\n")


def debug_exception(context: str, err: Exception):
    """Print a formatted traceback."""
    if not DEBUG_FLATLAY:
        return
    print(f"[flatlay:DEBUG] ERROR in {context}: {err}")
    traceback.print_exc()

