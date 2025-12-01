# Railway Background-Processor Service Fix

## Problem
The `background-processor` service was failing because Railway was building with `backend/worker` as the root directory, preventing Python from accessing `backend/src/` for imports like `src.services.subscription_utils`.

## Solution
Change the Railway service configuration to use `backend/` as the root directory instead of `backend/worker/`.

---

## Exact Railway Dashboard Settings

### Service: `background-processor`

**Navigate to:** Settings → Build & Deploy

#### Root Directory
```
backend
```
*(Change from: `backend/worker`)*

#### Start Command
```
python worker/main.py
```
*(Change from: `python main.py`)*

#### Builder
```
NIXPACKS
```
*(Should already be set, or use "Auto-detect")*

#### Restart Policy
- **Type:** `ON_FAILURE`
- **Max Retries:** `10`

---

## Why This Works

1. **Root Directory = `backend/`**
   - Exposes both `worker/` and `src/` directories
   - Python can now import from `src.services.subscription_utils` and other modules
   - NIXPACKS can find `requirements.txt` in the worker directory

2. **Start Command = `python worker/main.py`**
   - Runs the worker script from the correct path
   - Worker's `sys.path` modifications can now find parent directories
   - All imports resolve correctly

---

## Verification After Deploy

### ✅ Success Indicators

1. **Build Logs:**
   - Should show NIXPACKS detecting Python
   - Should install dependencies from `worker/requirements.txt`
   - No import errors during build

2. **Runtime Logs:**
   - Look for: `✅ Worker script starting...`
   - Look for: `✅ OpenAI client initialized for flat lay generation` (if API key is set)
   - Should see: `Successfully imported subscription_utils` or similar

3. **Flat Lay Generation:**
   - When generating outfits, look for `[flatlay:DEBUG]` messages in logs
   - Flat lay status should update in Firestore
   - No `ModuleNotFoundError` for `src.services.*` imports

### ❌ Failure Indicators

- `ModuleNotFoundError: No module named 'src'`
- `ModuleNotFoundError: No module named 'src.services.subscription_utils'`
- Build fails with "Cannot find requirements.txt" (wrong root directory)

---

## Current Configuration Files

### `backend/worker/railway.toml`
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "python worker/main.py"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

**Note:** The `railway.toml` file documents the correct settings, but Railway dashboard settings take precedence. Make sure to update the dashboard settings as specified above.

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

1. **Check Root Directory:**
   - Verify it's exactly `backend` (not `backend/` with trailing slash)
   - Railway should show both `worker/` and `src/` in file explorer

2. **Check Start Command:**
   - Must be `python worker/main.py` (not `python main.py`)
   - The `worker/` prefix is required because root is now `backend/`

3. **Check Python Path:**
   - Worker's `sys.path` modifications should find `backend/src/`
   - Look for path resolution logs in worker startup

4. **Verify Requirements:**
   - `backend/worker/requirements.txt` should be detected by NIXPACKS
   - All dependencies should install successfully

---

**Last Updated:** November 30, 2025
**Status:** ✅ Fix documented, awaiting Railway dashboard update

