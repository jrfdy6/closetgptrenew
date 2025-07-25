from fastapi import APIRouter, UploadFile, File, HTTPException
from rembg import remove
from PIL import Image
import io
import firebase_admin
from firebase_admin import storage
import os
from typing import Optional
import logging
from ..config.firebase import firebase_admin  # Import Firebase configuration

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/image", tags=["image"])

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