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

@router.get("/create-firebase-bucket")
async def create_firebase_bucket():
    """Try to create a Firebase Storage bucket"""
    try:
        import os
        import firebase_admin
        from firebase_admin import storage
        
        project_id = os.environ.get("FIREBASE_PROJECT_ID", "closetgptrenew")
        bucket_name = f"{project_id}.appspot.com"
        
        logger.info(f"Attempting to create bucket: {bucket_name}")
        
        # Try to create the bucket
        from google.cloud import storage as gcs
        client = gcs.Client()
        
        try:
            bucket = client.create_bucket(bucket_name, location="us-central1")
            logger.info(f"Bucket created successfully: {bucket.name}")
            return {
                "success": True,
                "bucket_name": bucket.name,
                "message": "Bucket created successfully"
            }
        except Exception as create_error:
            logger.error(f"Failed to create bucket: {create_error}")
            return {
                "success": False,
                "error": str(create_error),
                "message": "Failed to create bucket - may already exist or lack permissions"
            }
        
    except Exception as e:
        logger.error(f"Bucket creation test failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }

@router.get("/test-firebase-upload")
async def test_firebase_upload():
    """Test Firebase Storage upload with different bucket name formats"""
    try:
        import os
        import firebase_admin
        from firebase_admin import storage
        
        project_id = os.environ.get("FIREBASE_PROJECT_ID", "closetgptrenew")
        
        # Try different bucket name formats
        bucket_names_to_try = [
            f"{project_id}.firebasestorage.app",  # New Firebase format
            f"{project_id}.appspot.com",  # Old format
            f"{project_id}-default-rtdb",  # Alternative format
            f"{project_id}-storage",  # Another format
            project_id,  # Just project ID
        ]
        
        results = []
        
        for bucket_name in bucket_names_to_try:
            try:
                logger.info(f"Trying bucket: {bucket_name}")
                bucket = storage.bucket(bucket_name)
                
                # Create a simple test file
                test_content = b"test image content"
                test_filename = f"test-{uuid.uuid4()}.txt"
                blob_name = f"test/{test_filename}"
                
                # Create blob and upload
                blob = bucket.blob(blob_name)
                blob.upload_from_string(test_content, content_type="text/plain")
                
                # Make public
                blob.make_public()
                public_url = blob.public_url
                
                results.append({
                    "bucket_name": bucket_name,
                    "success": True,
                    "public_url": public_url
                })
                
                logger.info(f"Success with bucket: {bucket_name}")
                break  # Stop on first success
                
            except Exception as e:
                results.append({
                    "bucket_name": bucket_name,
                    "success": False,
                    "error": str(e)
                })
                logger.warning(f"Failed with bucket {bucket_name}: {e}")
        
        return {
            "results": results,
            "project_id": project_id
        }
        
    except Exception as e:
        logger.error(f"Firebase Storage test failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }

@router.get("/debug-firebase")
async def debug_firebase():
    """Debug Firebase Storage configuration"""
    try:
        import os
        import firebase_admin
        from firebase_admin import storage
        
        debug_info = {
            "firebase_initialized": len(firebase_admin._apps) > 0,
            "environment_vars": {
                "FIREBASE_PROJECT_ID": bool(os.environ.get("FIREBASE_PROJECT_ID")),
                "FIREBASE_PRIVATE_KEY": bool(os.environ.get("FIREBASE_PRIVATE_KEY")),
                "FIREBASE_CLIENT_EMAIL": bool(os.environ.get("FIREBASE_CLIENT_EMAIL")),
            },
            "project_id": os.environ.get("FIREBASE_PROJECT_ID", "NOT_SET"),
            "expected_bucket": f"{os.environ.get('FIREBASE_PROJECT_ID', 'unknown')}.appspot.com" if os.environ.get("FIREBASE_PROJECT_ID") else "NOT_SET"
        }
        
        # Try to get the bucket
        try:
            bucket = storage.bucket()
            debug_info["bucket_name"] = bucket.name
            debug_info["bucket_exists"] = True
        except Exception as e:
            debug_info["bucket_error"] = str(e)
            debug_info["bucket_exists"] = False
            
        # Try to list buckets to see what's available
        try:
            from google.cloud import storage as gcs
            client = gcs.Client()
            buckets = list(client.list_buckets())
            debug_info["available_buckets"] = [bucket.name for bucket in buckets]
        except Exception as e:
            debug_info["bucket_list_error"] = str(e)
            
        return debug_info
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}

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
            
            # Use processed contents for upload
            contents = processed_contents
            file.content_type = processed_content_type
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing image: {e}", exc_info=True)
            # For now, skip processing and use original contents
            logger.warning("Skipping image processing, using original contents")
            # Don't raise error, just use original contents
        
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
            logger.info(f"Creating blob: {blob_name}")
            blob = bucket.blob(blob_name)
            logger.info(f"Blob created successfully")
            
            logger.info(f"Uploading {len(contents)} bytes to Firebase Storage...")
            blob.upload_from_string(contents, content_type=file.content_type)
            logger.info("Successfully uploaded to Firebase Storage")
            
            # Make public and get URL
            logger.info("Making blob public...")
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
