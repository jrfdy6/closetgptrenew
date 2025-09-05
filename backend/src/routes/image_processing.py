from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from PIL import Image
import io
import firebase_admin
from firebase_admin import storage
import os
from typing import Optional
import uuid
import logging

# Optional imports with fallbacks
try:
    from rembg import remove
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False
    print("⚠️ rembg not available - background removal disabled")

try:
    from ..config.firebase import firebase_admin  # Import Firebase configuration
    FIREBASE_CONFIG_AVAILABLE = True
except ImportError:
    FIREBASE_CONFIG_AVAILABLE = False
    print("⚠️ Firebase config not available")

try:
    from ..auth.auth_service import get_current_user_optional
    from ..custom_types.profile import UserProfile
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False
    print("⚠️ Auth services not available - using fallback")
    
    # Fallback for when auth is not available
    def get_current_user_optional():
        return None
    
    class UserProfile:
        def __init__(self, id="anonymous"):
            self.id = id

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["image"])

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    category: Optional[str] = "clothing",
    name: Optional[str] = None,
    current_user: Optional[UserProfile] = Depends(get_current_user_optional) if AUTH_AVAILABLE else None
):
    try:
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be an image")

        # Read contents
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")

        # Build filename
        file_extension = (file.filename or "").split('.')[-1] or 'jpg'
        user_id = current_user.id if current_user else "anonymous"
        filename = f"wardrobe/{user_id}/{uuid.uuid4()}.{file_extension}"

        # Upload to Firebase Storage with download token
        bucket = storage.bucket()
        blob = bucket.blob(filename)
        token = str(uuid.uuid4())
        blob.metadata = {"firebaseStorageDownloadTokens": token}
        blob.upload_from_string(contents, content_type=file.content_type)

        download_url = (
            f"https://firebasestorage.googleapis.com/v0/b/{bucket.name}/o/"
            f"{filename.replace('/', '%2F')}?alt=media&token={token}"
        )

        return {
            "message": "Image uploaded successfully",
            "item_id": str(uuid.uuid4()),
            "image_url": download_url,
            "item": {
                "name": name or file.filename,
                "category": category,
                "image_url": download_url,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload image")

@router.post("/remove-background")
async def remove_background(
    file: UploadFile = File(...),
    item_id: Optional[str] = None
):
    try:
        logger.info(f"Starting background removal for file: {file.filename}")
        
        # Read the uploaded image
        contents = await file.read()
        logger.info(f"Successfully read file of size: {len(contents)} bytes")
        
        try:
            input_image = Image.open(io.BytesIO(contents))
            logger.info(f"Successfully opened image with size: {input_image.size}")
        except Exception as e:
            logger.error(f"Failed to open image: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")
        
        try:
            # Remove background
            logger.info("Starting background removal with rembg")
            output_image = remove(input_image)
            logger.info("Background removal completed successfully")
        except Exception as e:
            logger.error(f"Background removal failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Background removal failed: {str(e)}")
        
        try:
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            output_image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            logger.info(f"Successfully converted image to bytes: {len(img_byte_arr)} bytes")
        except Exception as e:
            logger.error(f"Failed to convert image to bytes: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Image conversion failed: {str(e)}")
        
        try:
            # Upload to Firebase Storage
            bucket = storage.bucket()
            filename = f"background_removed/{item_id if item_id else 'temp'}.png"
            blob = bucket.blob(filename)
            logger.info(f"Preparing to upload to Firebase Storage: {filename}")
            
            # Upload the image
            blob.upload_from_string(
                img_byte_arr,
                content_type='image/png'
            )
            logger.info("Successfully uploaded to Firebase Storage")
            
            # Make the image publicly accessible
            blob.make_public()
            logger.info(f"Image made public. URL: {blob.public_url}")
            
            return {
                "success": True,
                "message": "Background removed successfully",
                "image_url": blob.public_url
            }
        except Exception as e:
            logger.error(f"Firebase Storage operation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Storage operation failed: {str(e)}")
        
    except Exception as e:
        logger.error(f"Unexpected error in remove_background: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        ) 