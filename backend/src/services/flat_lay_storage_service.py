#!/usr/bin/env python3
"""
Flat Lay Storage Service
Handles uploading and storing flat lay images to Firebase Storage
"""

import logging
import io
import uuid
from typing import Optional, Dict, Any
from PIL import Image
from firebase_admin import storage
from datetime import datetime

logger = logging.getLogger(__name__)


class FlatLayStorageService:
    """Service for storing flat lay images in Firebase Storage"""
    
    def __init__(self, bucket_name: Optional[str] = None):
        """
        Initialize storage service
        
        Args:
            bucket_name: Firebase Storage bucket name (optional)
        """
        try:
            self.bucket = storage.bucket(bucket_name)
            logger.info(f"✅ Flat lay storage service initialized with bucket: {self.bucket.name}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize storage bucket: {e}")
            self.bucket = None
    
    async def upload_flat_lay(
        self,
        image: Image.Image,
        outfit_id: str,
        user_id: str,
        format: str = "PNG"
    ) -> Optional[str]:
        """
        Upload a flat lay image to Firebase Storage
        
        Args:
            image: PIL Image to upload
            outfit_id: Unique outfit identifier
            user_id: User identifier
            format: Image format (PNG or JPEG)
            
        Returns:
            Public URL of uploaded image, or None on error
        """
        try:
            if not self.bucket:
                logger.error("Storage bucket not initialized")
                return None
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"flat_lays/{user_id}/{outfit_id}_{timestamp}.{format.lower()}"
            
            # Convert image to bytes
            buffer = io.BytesIO()
            if format.upper() == "JPEG":
                # Convert to RGB for JPEG
                rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'RGBA':
                    rgb_image.paste(image, mask=image.split()[3])
                else:
                    rgb_image = image.convert('RGB')
                rgb_image.save(buffer, format=format, quality=95)
            else:
                image.save(buffer, format=format, quality=95)
            
            buffer.seek(0)
            
            # Upload to Firebase Storage
            blob = self.bucket.blob(filename)
            blob.upload_from_file(
                buffer,
                content_type=f'image/{format.lower()}'
            )
            
            # Make the blob publicly accessible
            blob.make_public()
            
            # Get public URL
            public_url = blob.public_url
            
            logger.info(f"✅ Uploaded flat lay for outfit {outfit_id}: {public_url}")
            
            return public_url
            
        except Exception as e:
            logger.error(f"❌ Error uploading flat lay: {e}", exc_info=True)
            return None
    
    async def delete_flat_lay(
        self,
        outfit_id: str,
        user_id: str
    ) -> bool:
        """
        Delete flat lay image(s) for an outfit
        
        Args:
            outfit_id: Outfit identifier
            user_id: User identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.bucket:
                logger.error("Storage bucket not initialized")
                return False
            
            # List all blobs matching the outfit_id pattern
            prefix = f"flat_lays/{user_id}/{outfit_id}"
            blobs = self.bucket.list_blobs(prefix=prefix)
            
            deleted_count = 0
            for blob in blobs:
                blob.delete()
                deleted_count += 1
            
            logger.info(f"✅ Deleted {deleted_count} flat lay image(s) for outfit {outfit_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting flat lay: {e}")
            return False
    
    async def get_flat_lay_url(
        self,
        outfit_id: str,
        user_id: str
    ) -> Optional[str]:
        """
        Get the URL of an existing flat lay image
        
        Args:
            outfit_id: Outfit identifier
            user_id: User identifier
            
        Returns:
            Public URL of the flat lay, or None if not found
        """
        try:
            if not self.bucket:
                logger.error("Storage bucket not initialized")
                return None
            
            # List blobs matching the outfit_id
            prefix = f"flat_lays/{user_id}/{outfit_id}"
            blobs = list(self.bucket.list_blobs(prefix=prefix, max_results=1))
            
            if blobs:
                return blobs[0].public_url
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting flat lay URL: {e}")
            return None

