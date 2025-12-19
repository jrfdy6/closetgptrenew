from fastapi import APIRouter

router = APIRouter()

@router.get("/debug-tier-filter")
async def debug_tier_filter():
    """Read tier filter debug log"""
    try:
        with open('/tmp/tier_filter_debug.log', 'r') as f:
            content = f.read()
        return {"log": content, "found": True}
    except FileNotFoundError:
        return {"log": "No debug log found yet", "found": False}
    except Exception as e:
        return {"error": str(e), "found": False}
