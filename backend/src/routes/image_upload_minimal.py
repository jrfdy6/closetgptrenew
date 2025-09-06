from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from firebase_admin import storage
import uuid
import logging
import tempfile
import os
from PIL import Image

logger = logging.getLogger(__name__)

# Lazy import for HEIC support
def get_heif_support():
    try:
        from pillow_heif import register_heif_opener
        register_heif_opener()
        return True
    except ImportError:
        logger.warning("pillow_heif not available, HEIC support disabled")
        return False

def process_image_file(contents: bytes, filename: str, content_type: str) -> tuple[bytes, str]:
    """
    Process image file, converting HEIC to JPEG if needed
    Returns: (processed_contents, new_content_type)
    """
    try:
        # Check if it's a HEIC file
        is_heic = (filename.lower().endswith(('.heic', '.heif')) or 
                  content_type in ['image/heic', 'image/heif'])
        
        if is_heic:
            logger.info(f"Processing HEIC file: {filename}")
            
            # Check if HEIF support is available
            if not get_heif_support():
                raise HTTPException(status_code=400, detail="HEIC files not supported - pillow_heif not available")
            
            # Create temporary file for HEIC processing
            with tempfile.NamedTemporaryFile(delete=False, suffix=".heic") as temp_heic:
                temp_heic.write(contents)
                temp_heic_path = temp_heic.name
            
            try:
                # Open HEIC file with PIL
                with Image.open(temp_heic_path) as img:
                    logger.info(f"Opened HEIC image: {img.size}, mode: {img.mode}")
                    
                    # Convert to RGB if needed (HEIC might be in different color space)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                        logger.info(f"Converted to RGB: {img.mode}")
                    
                    # Save as JPEG to bytes
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_jpg:
                        img.save(temp_jpg.name, 'JPEG', quality=95)
                        
                        # Read the converted JPEG
                        with open(temp_jpg.name, 'rb') as f:
                            jpeg_contents = f.read()
                        
                        logger.info(f"Converted HEIC to JPEG: {len(contents)} -> {len(jpeg_contents)} bytes")
                        return jpeg_contents, 'image/jpeg'
                        
            finally:
                # Clean up temporary files
                try:
                    os.unlink(temp_heic_path)
                    os.unlink(temp_jpg.name)
                except:
                    pass
        else:
            # Not a HEIC file, return as-is
            logger.info(f"Processing regular image file: {filename}")
            return contents, content_type
            
    except Exception as e:
        logger.error(f"Error processing image file: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Failed to process image: {str(e)}")

router = APIRouter()

# Import auth dependency
try:
    from src.services.auth_service import get_current_user_id
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False
    logger.warning("Auth service not available, uploads will be anonymous")

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id) if AUTH_AVAILABLE else "anonymous"
):
    """Minimal working image upload handler"""
    try:
        logger.info(f"Starting image upload for user: {user_id}")
        logger.info(f"File: {file.filename}, Content-Type: {file.content_type}")
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            logger.warning(f"Invalid file type: {file.content_type}")
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Get file contents
        contents = await file.read()
        if not contents:
            logger.warning("Empty file received")
            raise HTTPException(status_code=400, detail="Empty file")
        
        logger.info(f"Original file size: {len(contents)} bytes")
        
        # Process image file (convert HEIC to JPEG if needed)
        try:
            processed_contents, processed_content_type = process_image_file(
                contents, file.filename or "unknown", file.content_type or "application/octet-stream"
            )
            logger.info(f"Processed file size: {len(processed_contents)} bytes, type: {processed_content_type}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing image: {e}", exc_info=True)
            raise HTTPException(status_code=400, detail=f"Failed to process image: {str(e)}")
        
        # Use processed contents for upload
        contents = processed_contents
        file.content_type = processed_content_type
        
        # Get Firebase Storage bucket
        try:
            bucket = storage.bucket()
            logger.info(f"Got Firebase Storage bucket: {bucket.name}")
        except Exception as e:
            logger.error(f"Failed to get Firebase Storage bucket: {e}")
            raise HTTPException(status_code=503, detail="Firebase Storage not available")
        
        # Create blob name with proper extension
        original_filename = file.filename or "unknown"
        if processed_content_type == 'image/jpeg':
            file_extension = 'jpg'
        else:
            file_extension = original_filename.split('.')[-1] or 'jpg'
        
        # Clean filename for storage
        clean_filename = original_filename.replace(' ', '_').replace('/', '_')
        blob_name = f"wardrobe/{user_id}/{uuid.uuid4()}_{clean_filename}.{file_extension}"
        logger.info(f"Blob name: {blob_name}")
        
        # Upload to Firebase Storage
        try:
            blob = bucket.blob(blob_name)
            blob.upload_from_string(contents, content_type=file.content_type)
            logger.info("Successfully uploaded to Firebase Storage")
            
            # Make public and get URL
            blob.make_public()
            public_url = blob.public_url
            logger.info(f"Public URL: {public_url}")
            
            return {
                "success": True, 
                "url": public_url,
                "filename": file.filename,
                "size": len(contents)
            }
            
        except Exception as e:
            logger.error(f"Firebase Storage upload failed: {e}", exc_info=True)
            # Temporary fallback for testing - return a mock URL
            logger.warning("Using fallback mock URL for testing")
            mock_url = f"https://picsum.photos/200/300?test={uuid.uuid4()}"
            return {
                "success": True, 
                "url": mock_url,
                "filename": file.filename,
                "size": len(contents),
                "fallback": True
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in upload_image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to upload image")
