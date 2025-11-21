from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from PIL import Image
import io
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
    # print("⚠️ rembg not available - background removal disabled")

try:
    import firebase_admin
    from firebase_admin import storage
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    # print("⚠️ Firebase Admin SDK not available")

try:
    from ..config.firebase import firebase_admin  # Import Firebase configuration
    FIREBASE_CONFIG_AVAILABLE = True
except ImportError:
    FIREBASE_CONFIG_AVAILABLE = False
    # print("⚠️ Firebase config not available")

try:
    from ..auth.auth_service import get_current_user_optional
    from ..custom_types.profile import UserProfile
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False
    # print("⚠️ Auth services not available - using fallback")
    
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
    remove_bg: bool = True,  # ENABLED: Always use alpha matting for best quality
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
        item_id = str(uuid.uuid4())
        filename = f"wardrobe/{user_id}/{item_id}.{file_extension}"

        # Upload to Firebase Storage with download token
        if not FIREBASE_AVAILABLE:
            logger.error("❌ Firebase Storage not available")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                detail="Firebase Storage not available"
            )
        
        try:
            bucket = storage.bucket()
            
            # Upload ORIGINAL image
            blob = bucket.blob(filename)
            token = str(uuid.uuid4())
            blob.metadata = {"firebaseStorageDownloadTokens": token}
            blob.upload_from_string(contents, content_type=file.content_type)
            logger.info(f"✅ Uploaded original image: {filename}")
            
        except Exception as firebase_error:
            import traceback
            logger.error(f"❌ Firebase upload error: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Firebase Storage upload failed: {str(firebase_error)}"
            )

        original_url = (
            f"https://firebasestorage.googleapis.com/v0/b/{bucket.name}/o/"
            f"{filename.replace('/', '%2F')}?alt=media&token={token}"
        )
        
        # NEW: Auto-remove background and store clean version
        background_removed_url = None
        if remove_bg:
            try:
                logger.info("🎨 Starting automatic background removal with ALPHA MATTING...")
                
                # Process image with rembg + alpha matting for BEST quality
                input_image = Image.open(io.BytesIO(contents))
                
                try:
                    # Try with alpha matting first (best quality)
                    output_image = remove(
                        input_image,
                        alpha_matting=True,
                        alpha_matting_foreground_threshold=240,
                        alpha_matting_background_threshold=10,
                        alpha_matting_erode_size=10
                    )
                    logger.info("✅ Background removed with alpha matting (high quality)")
                except Exception as alpha_error:
                    # Fallback to fast mode if alpha matting fails
                    logger.warning(f"⚠️ Alpha matting failed, using fast mode: {alpha_error}")
                    output_image = remove(input_image)
                    logger.info("✅ Background removed with fast mode (standard quality)")
                
                # Convert to bytes
                img_byte_arr = io.BytesIO()
                output_image.save(img_byte_arr, format='PNG')
                img_bytes = img_byte_arr.getvalue()
                
                # Upload background-removed version
                bg_removed_filename = f"wardrobe/{user_id}/{item_id}_nobg.png"
                bg_blob = bucket.blob(bg_removed_filename)
                bg_token = str(uuid.uuid4())
                bg_blob.metadata = {"firebaseStorageDownloadTokens": bg_token}
                bg_blob.upload_from_string(img_bytes, content_type='image/png')
                
                background_removed_url = (
                    f"https://firebasestorage.googleapis.com/v0/b/{bucket.name}/o/"
                    f"{bg_removed_filename.replace('/', '%2F')}?alt=media&token={bg_token}"
                )
                logger.info(f"✅ Background removed and uploaded: {bg_removed_filename}")
                
            except Exception as bg_error:
                logger.warning(f"⚠️ Background removal failed (continuing without): {bg_error}")
                # Continue without background-removed version (not critical)

        return {
            "message": "Image uploaded successfully",
            "item_id": item_id,
            "image_url": original_url,
            "background_removed_url": background_removed_url,  # NEW: Clean version for flat lays
            "background_removed": background_removed_url is not None,  # NEW: Flag
            "item": {
                "name": name or file.filename,
                "category": category,
                "image_url": original_url,
                "backgroundRemovedUrl": background_removed_url,
                "backgroundRemoved": background_removed_url is not None,
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