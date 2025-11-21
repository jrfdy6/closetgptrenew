# Reprocess All Wardrobe Items

This script reprocesses all wardrobe items with alpha matting to ensure they have processed images (nobg.png, processed.png) for flatlay generation.

## How to Run

### Option 1: Run on Railway (Recommended)

1. SSH into your Railway worker service:
   ```bash
   railway run bash
   ```

2. Navigate to the worker directory:
   ```bash
   cd /app/worker
   ```

3. Run the script:
   ```bash
   python3 ../scripts/reprocess_all_wardrobe_items.py
   ```

### Option 2: Run Locally (if you have all dependencies)

1. Install dependencies:
   ```bash
   pip install numpy pillow rembg firebase-admin requests
   ```

2. Set environment variables:
   ```bash
   export FIREBASE_PROJECT_ID="your-project-id"
   export FIREBASE_PRIVATE_KEY_ID="your-key-id"
   export FIREBASE_PRIVATE_KEY="your-private-key"
   export FIREBASE_CLIENT_EMAIL="your-client-email"
   export FIREBASE_CLIENT_ID="your-client-id"
   export FIREBASE_CLIENT_X509_CERT_URL="your-cert-url"
   ```

3. Run the script:
   ```bash
   cd backend/scripts
   python3 reprocess_all_wardrobe_items.py
   ```

## What It Does

1. Fetches all items from the `wardrobe` Firestore collection
2. Checks if each item has processed images (nobg.png or processed.png)
3. For items missing processed images:
   - Downloads the original image
   - Runs alpha matting for background removal
   - Removes hangers
   - Applies styling (shadows, gradients)
   - Generates thumbnails
   - Uploads processed images to Firebase Storage
   - Updates Firestore with new URLs

## Output

The script will show:
- Total items found
- Items that need processing
- Progress for each item
- Final summary with success/error counts

## Notes

- Items that already have processed images are skipped
- The script processes items sequentially to avoid overwhelming the system
- Each item takes approximately 10-30 seconds depending on image size
- Large batches may take several hours to complete

