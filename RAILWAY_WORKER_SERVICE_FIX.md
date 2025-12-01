# Railway Background-Processor Service Fix

## Problem
The `background-processor` service was failing because Railway builds with `backend/worker` as the root directory, preventing Python from accessing `backend/src/` for imports like `src.services.subscription_utils`.

## Solution ✅ IMPLEMENTED
**Option 1: Dynamic sys.path manipulation + NIXPACKS builder** - Modified `worker/main.py` to add `backend/src/` to Python's import path at runtime, and switched to NIXPACKS builder (instead of Dockerfile) to avoid build context restrictions.

**Why NIXPACKS:**
- Dockerfile builder restricts build context to `backend/worker/` only
- Cannot access `../src/` from parent directories
- NIXPACKS doesn't have this restriction and allows `sys.path` to resolve `../src/` at runtime

**Constraint:** Railway root directory and start command cannot be changed.

---

## Implementation Details

### Code Changes in `backend/worker/main.py`

The worker now uses robust `sys.path` manipulation to access `backend/src/`:

```python
# Calculate paths relative to worker directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # backend/worker
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))  # backend/
SRC_DIR = os.path.join(BACKEND_DIR, "src")  # backend/src/

# Add backend/src to sys.path if it exists
if os.path.exists(SRC_DIR) and SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
    # Now we can import: from services.subscription_utils import ...
```

### Key Changes:
1. **Uses `os.path` instead of `Path`** for more reliable path resolution
2. **Explicitly calculates `backend/src`** relative to worker directory
3. **Adds to `sys.path` before any imports** from `src/`
4. **Multiple fallback paths** for different deployment scenarios
5. **Comprehensive logging** to debug import resolution
6. **Imports use `services.subscription_utils`** (without `src.` prefix) once path is set

### Why This Works

1. **No Railway Dashboard Changes Required**
   - Root directory stays as `backend/worker`
   - Start command stays as `python main.py`
   - Works within Railway's constraints

2. **Runtime Path Resolution**
   - Worker calculates `backend/src/` path at runtime
   - Adds it to `sys.path` before importing
   - Python can now find modules in `backend/src/`

3. **Robust Fallbacks**
   - Tries multiple path locations
   - Handles different deployment scenarios
   - Provides clear error messages if paths aren't found

---

## Verification After Deploy

### ✅ Success Indicators

1. **Build Logs:**
   - Should show NIXPACKS detecting Python
   - Should install dependencies from `worker/requirements.txt`
   - No import errors during build

2. **Runtime Logs:**
   - Look for: `✅ Worker script starting...`
   - Look for: `✅ Added [path]/src to sys.path` (confirms path resolution)
   - Look for: `✅ Successfully imported from services.subscription_utils` (confirms import works)
   - Look for: `✅ OpenAI client initialized for flat lay generation` (if API key is set)

3. **Flat Lay Generation:**
   - When generating outfits, look for `[flatlay:DEBUG]` messages in logs
   - Flat lay status should update in Firestore
   - No `ModuleNotFoundError` for `src.services.*` imports

### ❌ Failure Indicators

- `ModuleNotFoundError: No module named 'services'`
- `ModuleNotFoundError: No module named 'services.subscription_utils'`
- `⚠️ Warning: Could not find src/ directory` in logs
- Build fails with "Cannot find requirements.txt" (wrong root directory)

---

## Current Configuration Files

### `backend/worker/railway.toml`
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "python main.py"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

**Note:** The Railway dashboard should have:
- **Root Directory:** `backend/worker` (unchanged)
- **Start Command:** `python main.py` (unchanged)
- **Builder:** `NIXPACKS` (set in railway.toml, or manually set in dashboard)

**Why not Dockerfile:**
- Dockerfile build context is restricted to `backend/worker/` only
- Cannot access `../src/` from parent directories
- NIXPACKS allows `sys.path` to resolve `../src/` at runtime

The fix is implemented in code (sys.path manipulation) + builder choice (NIXPACKS).

---

## Related Files

- **Worker Script:** `backend/worker/main.py`
- **Worker Requirements:** `backend/worker/requirements.txt`
- **Subscription Utils:** `backend/src/services/subscription_utils.py` (imported by worker)
- **Main App Config:** `railway.toml` (root - for main app service, not worker)

---

## Quick Reference

**Copy-paste for Railway Dashboard:**

```
Root Directory: backend
Start Command: python worker/main.py
Builder: NIXPACKS
```

---

## Troubleshooting

### If imports still fail after fix:

1. **Check Logs for Path Resolution:**
   - Look for `✅ Added [path]/src to sys.path` message
   - If you see `⚠️ Warning: Could not find src/ directory`, check the paths being tried
   - Verify the calculated `SRC_DIR` path is correct

2. **Verify Directory Structure:**
   - Railway should have `backend/worker/` as root
   - The worker code should be able to navigate to `../src/` from `backend/worker/`
   - Check that `backend/src/services/subscription_utils.py` exists in the build

3. **Check Import Statements:**
   - After `sys.path` is set, imports should use `from services.subscription_utils import ...`
   - Not `from src.services.subscription_utils import ...` (that's the fallback)

4. **Verify Requirements:**
   - `backend/worker/requirements.txt` should be detected by NIXPACKS
   - All dependencies should install successfully

5. **Test Locally:**
   - Run from `backend/worker/` directory: `python main.py`
   - Should see path resolution messages in logs
   - Should successfully import `services.subscription_utils`

---

**Last Updated:** November 30, 2025
**Status:** ✅ Fix implemented in code - no Railway dashboard changes needed

