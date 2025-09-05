from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from PIL import Image
import io
import firebase_admin
from firebase_admin import storage
import os
from typing import Optional
import uuid
import logging

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["image"])

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    category: Optional[str] = "clothing",
    name: Optional[str] = None
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
        filename = f"wardrobe/test-user/{uuid.uuid4()}.{file_extension}"

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
