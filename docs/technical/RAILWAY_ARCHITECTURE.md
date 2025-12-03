# 🏗️ Railway Project Architecture

## Your Railway Project: `closetgptrenew`

### Two Services in One Project

```
Railway Project: closetgptrenew
├── Service 1: closetgptrenew-production (Main App)
│   ├── URL: https://closetgptrenew-production.up.railway.app
│   ├── Code: /backend (main FastAPI app)
│   ├── Start: python run.py
│   └── Database: Firebase/Firestore
│
└── Service 2: closetgptrenewopenaisdk (MCP Server) ← NEW
    ├── URL: https://closetgptrenewopenaisdk-xxxxx.up.railway.app
    ├── Code: /backend (MCP server only)
    ├── Start: bash start_mcp.sh
    └── Connects to: Service 1 API
```

## How They Communicate

```
ChatGPT User
    ↓ (MCP Protocol)
Service 2: MCP Server (closetgptrenewopenaisdk)
    ↓ (HTTP with API_KEY)
Service 1: Main API (closetgptrenew-production)
    ↓
Firebase/Firestore
```

## Benefits of This Setup

### Same Project ✅
- **Unified billing** - One Railway project
- **Organized** - Related services together
- **Easy management** - View both in one dashboard
- **Shared resources** - Can share databases if needed

### Separate Services ✅
- **Independent deployments** - Update MCP without touching main app
- **Independent scaling** - Scale each based on usage
- **Isolated failures** - MCP crash won't break main app
- **Separate logs** - Debug each independently
- **Different configs** - Different environment variables

## Deployment

### Service 1: Main App (Existing - No Changes)
Already deployed at `closetgptrenew-production.up.railway.app`

### Service 2: MCP Server (New)
Deploy with:
```bash
./deploy-mcp-service-same-project.sh
```

## Environment Variables

### Service 1: Main App
- `OPENAI_API_KEY`
- `FIREBASE_CREDENTIALS_JSON`
- `PORT=3001`
- (all your existing vars)

### Service 2: MCP Server
- `MAIN_API_URL=https://closetgptrenew-production.up.railway.app`
- `API_KEY=dqvNQIiCRXmUSsEHFpVvWhotNkwAspNGS4nH3u2r844`
- `PORT=3002`

**Note:** Each service has its own environment variables. They don't interfere.

## Viewing in Railway Dashboard

In your Railway dashboard, you'll see:

```
Project: closetgptrenew
├─ Service: closetgptrenew-production
│  └─ Status: ✅ Running
│
└─ Service: closetgptrenewopenaisdk
   └─ Status: ✅ Running
```

Click each service to see its logs, metrics, and settings independently.

## Cost

Same Railway project = same billing.
But you have:
- Better organization
- Independent services
- Easier debugging

## URLs

Both services get their own public URLs:
- Main App: `https://closetgptrenew-production.up.railway.app`
- MCP Server: `https://closetgptrenewopenaisdk-production.up.railway.app`

(Railway auto-generates the full domain)

## Summary

✅ Same project = organized
✅ Separate services = safe & independent
✅ Clean architecture = easy to maintain

