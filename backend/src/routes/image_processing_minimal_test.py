from fastapi import APIRouter, UploadFile, File, HTTPException, status
import uuid
import logging

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["image-test"])

@router.post("/upload-test")
async def upload_image_test(
    file: UploadFile = File(...),
    category: str = "clothing",
    name: str = None
):
    """
    Minimal test endpoint for image upload
    """
    try:
        print(f"🔍 Test endpoint called with file: {file.filename}")
        
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be an image")

        # Read contents
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")

        print(f"✅ File read successfully: {len(contents)} bytes")
        
        # Return a simple response without Firebase
        return {
            "message": "Test upload successful",
            "item_id": str(uuid.uuid4()),
            "image_url": "test-url",
            "item": {
                "name": name or file.filename,
                "category": category,
                "image_url": "test-url",
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Test upload error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Test upload failed")
