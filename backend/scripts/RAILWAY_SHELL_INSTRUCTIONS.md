# How to Access Railway Shell

## Step-by-Step Instructions

1. **Go to Railway Dashboard**
   - Visit: https://railway.app
   - Log in if needed

2. **Select Your Project**
   - Click on "closetgpt-backend" project (or your project name)

3. **Select the Worker Service**
   - Look for the service named "background-processor"
   - Click on it

4. **Access the Shell**
   - You'll see several tabs: "Deployments", "Metrics", "Settings", etc.
   - Look for a "Shell" or "Connect" button/tab
   - OR click on the latest deployment
   - In the deployment view, look for "Shell" or "Connect" option
   - OR look for a terminal icon (usually in the top right or in a "More" menu)

5. **Alternative: Use Deployments Tab**
   - Click on "Deployments" tab
   - Click on the most recent deployment (the one that just completed)
   - Look for "Shell" or "Connect" button
   - This will open a terminal connected to that deployment

6. **Run the Script**
   Once you're in the shell, type:
   ```bash
   python3 /app/worker/reprocess_all_wardrobe_items.py
   ```

## If You Can't Find Shell Option

Some Railway interfaces don't have a direct shell option. In that case:

1. **Check the Logs Tab**
   - The script might be able to run via the logs interface
   - Or you may need to use Railway CLI (which we already tried)

2. **Use Railway CLI (Alternative)**
   ```bash
   railway shell --service background-processor
   ```
   Then once in the shell:
   ```bash
   python3 /app/worker/reprocess_all_wardrobe_items.py
   ```

## Visual Guide

The Railway interface typically looks like:
```
[Project Name]
  ├── Services
  │   ├── background-processor  ← Click here
  │   │   ├── Deployments tab
  │   │   ├── Metrics tab
  │   │   ├── Logs tab
  │   │   └── Settings tab
  │   └── [other services]
```

Look for:
- A terminal/console icon
- A "Shell" button
- A "Connect" button
- Or in Deployments → Latest deployment → "Shell" or "Connect"

