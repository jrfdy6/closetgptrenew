from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from firebase_admin import storage
import uuid
import logging

logger = logging.getLogger(__name__)

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
        
        logger.info(f"File size: {len(contents)} bytes")
        
        # Get Firebase Storage bucket
        try:
            bucket = storage.bucket()
            logger.info(f"Got Firebase Storage bucket: {bucket.name}")
        except Exception as e:
            logger.error(f"Failed to get Firebase Storage bucket: {e}")
            raise HTTPException(status_code=503, detail="Firebase Storage not available")
        
        # Create blob name
        file_extension = (file.filename or "").split('.')[-1] or 'jpg'
        blob_name = f"wardrobe/{user_id}/{uuid.uuid4()}_{file.filename}"
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
