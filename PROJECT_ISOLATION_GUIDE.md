# Project Isolation Guide

## Current Situation

You have multiple projects in `/Users/johnniefields/Desktop/Cursor/`:
- **closetgptrenew** (Easy Outfit App) - Currently active workspace
- **aiclone** - Separate AI Clone project

## The Problem

When you see "Easy Outfit" headers in your aiclone webpage, it's because:
1. You're viewing `localhost:3000` which is running the **closetgptrenew** frontend
2. The **aiclone** frontend is not running
3. Cursor shows "closetgptrenew" in the left panel because that's the current workspace

## Solution: Proper Project Isolation

### 1. Always Check Your Current Workspace

**In Cursor:**
- Look at the left panel - it shows the workspace name
- The workspace name should match the project you want to work on
- To switch workspaces: `File > Open Folder` and select the correct project folder

### 2. Use Different Ports for Each Project

**closetgptrenew (Easy Outfit):**
- Frontend: Port 3000 (default)
- Backend: Port 3001

**aiclone:**
- Frontend: Should use a different port (e.g., 3002)
- Backend: Port 8080 (already configured)

### 3. Before Starting Work

**Checklist:**
- [ ] Verify you're in the correct workspace (check left panel in Cursor)
- [ ] Check what's running: `lsof -i :3000 -i :3001 -i :3002 -i :8080`
- [ ] Stop any servers from the wrong project
- [ ] Start servers for the correct project
- [ ] Verify the correct URL in browser (check port number)

### 4. Starting aiclone Frontend

```bash
# Navigate to aiclone project
cd /Users/johnniefields/Desktop/Cursor/aiclone/frontend

# Install dependencies (if needed)
npm install

# Start on a different port (3002 to avoid conflict)
npm run dev -- -p 3002
```

Then visit: `http://localhost:3002` (NOT 3000!)

### 5. Starting closetgptrenew (Easy Outfit)

```bash
# Navigate to closetgptrenew project
cd /Users/johnniefields/Desktop/Cursor/closetgptrenew/frontend

# Start on default port 3000
npm run dev
```

Then visit: `http://localhost:3000`

## Quick Reference: Port Assignments

| Project | Frontend Port | Backend Port | URL |
|---------|--------------|--------------|-----|
| closetgptrenew (Easy Outfit) | 3000 | 3001 | http://localhost:3000 |
| aiclone | 3002 | 8080 | http://localhost:3002 |

## Common Mistakes to Avoid

1. **Wrong Workspace Open**: Always check the left panel shows the project you want
2. **Wrong Port**: Visiting localhost:3000 when you want aiclone (should be 3002)
3. **Multiple Servers Running**: Both projects running simultaneously can cause confusion
4. **Browser Cache**: Clear cache or use incognito if you see wrong content
5. **Environment Variables**: Each project has its own `.env` files - don't mix them up

## Verification Steps

Before coding, always verify:

```bash
# 1. Check which workspace you're in
pwd
# Should show: /Users/johnniefields/Desktop/Cursor/[project-name]

# 2. Check what's running
lsof -i :3000 -i :3001 -i :3002 -i :8080

# 3. Check the package.json name
cat frontend/package.json | grep '"name"'
# closetgptrenew should show: "easyoutfitapp-frontend"
# aiclone should show: "aiclone-frontend"
```

## Emergency: Stop All Servers

If you're confused about what's running:

```bash
# Kill all Node/Next.js processes
pkill -f "next dev"

# Kill all Python/uvicorn processes
pkill -f "uvicorn"

# Or more specifically:
lsof -ti :3000 | xargs kill -9  # Kill port 3000
lsof -ti :3001 | xargs kill -9  # Kill port 3001
lsof -ti :3002 | xargs kill -9  # Kill port 3002
lsof -ti :8080 | xargs kill -9  # Kill port 8080
```

## Best Practice: One Project at a Time

For maximum clarity:
1. Work on one project at a time
2. Close/stop servers from other projects
3. Use different browser windows/tabs for each project
4. Bookmark the correct URLs:
   - Easy Outfit: http://localhost:3000
   - AI Clone: http://localhost:3002



