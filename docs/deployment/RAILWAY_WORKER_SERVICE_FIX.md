# Railway Background-Processor Service Fix

## Problem

The `background-processor` service runs with `backend/worker` as its root directory. That means the worker should not depend on importing `backend/src` at runtime. The previous startup path tried to probe for `src/`, logged noisy warnings, and had a broken fallback import.

## Current Fix

The worker now imports a worker-local helper directly:

- `backend/worker/subscription_utils.py`

This keeps startup deterministic inside the actual Railway worker container layout.

## Why This Is Better

- `backend/worker` remains the Railway root directory
- `python main.py` remains the start command
- No runtime `sys.path` probing
- No misleading `Could not find src/ directory` warning
- No dependency on parent-directory imports

## Current Configuration

### `backend/worker/railway.toml`

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "python main.py"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

### Railway Dashboard

```text
Root Directory: backend/worker
Start Command: python main.py
Builder: NIXPACKS
```

## Verification

Healthy startup should show:

```text
Starting Container
✅ Loaded worker-local subscription_utils
🔍 Worker script starting...
```

The service status should be `SUCCESS` in Railway.

## Sync Rule

The worker-local helper is intentionally duplicated. If subscription quota logic changes in:

- `backend/src/services/subscription_utils.py`

mirror the same change in:

- `backend/worker/subscription_utils.py`

## Related Files

- `backend/worker/main.py`
- `backend/worker/subscription_utils.py`
- `backend/worker/requirements.txt`
- `backend/worker/railway.toml`

## Status

As of April 27, 2026:

- `background-processor` deploys from `main`
- Railway root directory is `backend/worker`
- The worker no longer depends on `backend/src` at startup
