#!/usr/bin/env python3
"""
Worker Service for Background Image Processing
Runs alpha matting on uploaded wardrobe items in the background
"""

import time
import requests
import tempfile
import os
import json
from io import BytesIO
from rembg import remove
from PIL import Image
import firebase_admin
from firebase_admin import credentials, firestore, storage

# ----------------------------
# Configuration
# ----------------------------
FIRESTORE_COLLECTION = "wardrobe"  # Using 'wardrobe' collection (not 'closet')
FIREBASE_BUCKET_NAME = "closetgptrenew.firebasestorage.app"

# Initialize Firebase Admin SDK
print("🔥 Initializing Firebase Admin SDK...")

# Build credentials from environment variables
firebase_creds = {
    "type": "service_account",
    "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
    "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.environ.get("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n"),
    "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.environ.get("FIREBASE_CLIENT_ID"),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.environ.get("FIREBASE_CLIENT_X509_CERT_URL")
}

# Initialize Firebase
cred = credentials.Certificate(firebase_creds)
firebase_admin.initialize_app(cred, {
    "storageBucket": FIREBASE_BUCKET_NAME
})

# Get Firebase clients
db = firestore.client()
bucket = storage.bucket()

print(f"✅ Connected to Firestore collection: {FIRESTORE_COLLECTION}")
print(f"✅ Connected to Storage bucket: {bucket.name}")


# ----------------------------
# Image Processing Function
# ----------------------------
def process_item(doc_id, data):
    """Process a single wardrobe item with alpha matting"""
    print(f"📸 Processing {doc_id}...")
    
    original_url = data.get("imageUrl") or data.get("image_url")
    if not original_url:
        print(f"  ⚠️  No original image found for {doc_id}")
        return
    
    try:
        # 1. Download image
        print(f"  📥 Downloading image from {original_url[:50]}...")
        response = requests.get(original_url, timeout=30)
        response.raise_for_status()
        input_img = Image.open(BytesIO(response.content)).convert("RGBA")
        print(f"  ✅ Downloaded image: {input_img.size}")
        
        # 2. Alpha matting (the heavy part - takes 5-10 seconds)
        print(f"  🎨 Running alpha matting...")
        output_img = remove(
            input_img,
            alpha_matting=True,
            alpha_matting_foreground_threshold=240,
            alpha_matting_background_threshold=10,
            alpha_matting_erode_size=10
        )
        print(f"  ✅ Background removed with alpha matting")
        
        # 3. Save locally
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            output_img.save(tmp.name, "PNG")
            tmp_path = tmp.name
        
        try:
            # 4. Upload to Firebase Storage
            print(f"  📤 Uploading processed image...")
            blob_path = f"wardrobe/processed/{doc_id}_clean.png"
            blob = bucket.blob(blob_path)
            blob.upload_from_filename(tmp_path)
            blob.make_public()
            processed_url = blob.public_url
            print(f"  ✅ Uploaded to: {processed_url[:50]}...")
            
            # 5. Update Firestore silently (user's UI auto-updates)
            db.collection(FIRESTORE_COLLECTION).document(doc_id).update({
                "backgroundRemovedUrl": processed_url,
                "backgroundRemoved": True,
                "processing_status": "done"
            })
            print(f"✅ COMPLETE: {doc_id} - Image auto-upgraded in UI")
            
        finally:
            # Cleanup temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except Exception as e:
        print(f"❌ Error processing {doc_id}: {e}")
        # Mark as failed so we don't retry forever
        try:
            db.collection(FIRESTORE_COLLECTION).document(doc_id).update({
                "processing_status": "failed",
                "processing_error": str(e)
            })
        except:
            pass


# ----------------------------
# Worker Loop
# ----------------------------
def run_worker():
    """Main worker loop - checks for pending items and processes them"""
    print("🔥 Worker started. Listening for new images...")
    print(f"📊 Monitoring collection: {FIRESTORE_COLLECTION}")
    print(f"🔍 Query: processing_status == 'pending'")
    print()
    
    loop_count = 0
    
    while True:
        try:
            loop_count += 1
            
            # Query items still pending processing
            pending = (
                db.collection(FIRESTORE_COLLECTION)
                .where("processing_status", "==", "pending")
                .limit(3)  # Process 3 at a time to avoid overwhelming
                .stream()
            )
            
            pending_list = list(pending)
            
            if pending_list:
                print(f"🎯 Loop #{loop_count}: Found {len(pending_list)} pending items")
                
                for doc in pending_list:
                    process_item(doc.id, doc.to_dict())
                    time.sleep(1)  # Small delay between items
                
                print()
            else:
                # No items to process
                if loop_count % 12 == 1:  # Log every minute
                    print(f"💤 Loop #{loop_count}: No pending items. Waiting...")
                time.sleep(5)
        
        except Exception as e:
            print(f"⚠️  Worker encountered error in loop: {e}")
            time.sleep(5)


# ----------------------------
# Entry Point
# ----------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 ClosetGPT Background Image Processor")
    print("=" * 60)
    print()
    run_worker()

