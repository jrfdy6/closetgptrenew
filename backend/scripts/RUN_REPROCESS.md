# How to Run the Reprocess Script on Railway

## Option 1: Using Railway CLI (Recommended)

1. **Install Railway CLI** (if not already installed):
   ```bash
   npm i -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Link to your project**:
   ```bash
   railway link
   ```

4. **Run the script in the worker service**:
   ```bash
   railway run --service background-processor python3 /app/scripts/reprocess_all_wardrobe_items.py
   ```

## Option 2: Using Railway Dashboard

1. Go to your Railway dashboard
2. Select the `background-processor` service
3. Click on "Deployments" → "View Logs" or "Connect" → "Shell"
4. Once in the shell, run:
   ```bash
   cd /app
   python3 scripts/reprocess_all_wardrobe_items.py
   ```

## Option 3: SSH into Railway (if available)

```bash
railway shell --service background-processor
cd /app
python3 scripts/reprocess_all_wardrobe_items.py
```

## What to Expect

The script will:
- Show total items found
- List items that need processing (those without `processing_mode == "alpha"`)
- Process each item sequentially
- Show progress for each item
- Display a summary at the end

**Note:** Processing can take a while (10-30 seconds per item). For large wardrobes, this may take several hours.


