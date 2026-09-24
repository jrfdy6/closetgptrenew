from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from firebase_admin import storage
import uuid
import logging
import tempfile
import os
from PIL import Image
from src.auth.verified_identity import verified_identity, reject_identity_overrides, IDENTITY_KEYS
from src.auth.operator import require_internal_operator
from src.config.firebase import db
from src.services.app_data_privacy import require_app_data_writable, AppDataDeletionError

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

# Lazy import for AVIF support
def get_avif_support():
    try:
        from pillow_avif import register_avif_opener
        register_avif_opener()
        return True
    except ImportError:
        logger.warning("pillow_avif_plugin not available, AVIF support may be limited")
        return False

def process_image_file(contents: bytes, filename: str, content_type: str) -> tuple[bytes, str]:
    """
    Process image file, converting HEIC/AVIF to PNG/JPEG if needed
    Returns: (processed_contents, new_content_type)
    """
    try:
        import io
        
        # Check if it's a HEIC file
        is_heic = (filename.lower().endswith(('.heic', '.heif')) or 
                  content_type in ['image/heic', 'image/heif'])
        
        # Check if it's an AVIF file
        is_avif = (filename.lower().endswith('.avif') or 
                  content_type == 'image/avif')
        
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
                    if 'temp_jpg' in locals():
                        os.unlink(temp_jpg.name)
                except:
                    pass
                    
        elif is_avif:
            logger.info(f"🔄 Converting AVIF to PNG for compatibility: {filename}")
            
            # Register AVIF opener if available
            get_avif_support()
            
            try:
                # Try to open AVIF with PIL (requires pillow-avif-plugin)
                img = Image.open(io.BytesIO(contents))
                logger.info(f"✅ Opened AVIF image: {img.size}, mode: {img.mode}")
                
                # Convert to RGB if needed (AVIF might be RGBA)
                if img.mode in ('RGBA', 'LA'):
                    # Create white background for RGBA
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = rgb_img
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save as PNG to bytes
                png_buffer = io.BytesIO()
                img.save(png_buffer, format='PNG')
                png_contents = png_buffer.getvalue()
                
                logger.info(f"✅ Converted AVIF to PNG: {len(contents)} -> {len(png_contents)} bytes")
                return png_contents, 'image/png'
                
            except Exception as avif_error:
                logger.error(f"❌ Could not convert AVIF: {avif_error}")
                # If PIL can't open AVIF, we need pillow-avif-plugin
                raise HTTPException(
                    status_code=400,
                    detail=f"AVIF conversion failed. PIL cannot open AVIF files without pillow-avif-plugin. Error: {str(avif_error)}"
                )
        else:
            # Not a HEIC/AVIF file, return as-is
            logger.info(f"Processing regular image file: {filename}")
            return contents, content_type
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing image file: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Failed to process image: {str(e)}")

router = APIRouter()

@router.get("/create-firebase-bucket", dependencies=[Depends(require_internal_operator)])
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

@router.get("/test-firebase-upload", dependencies=[Depends(require_internal_operator)])
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

@router.get("/debug-firebase", dependencies=[Depends(require_internal_operator)])
async def debug_firebase():
    """Debug Firebase Storage configuration"""
    try:
        import os
        import firebase_admin
        from firebase_admin import storage
        
        debug_info = {
            "firebase_initialized": len(firebase_admin._apps) > 0,
            "environment_vars": {
                "FIREBASE_PROJECT_ID": bool(os.environ.get("FIREBASE_PROJECT_ID") if environ else None),
                "FIREBASE_PRIVATE_KEY": bool(os.environ.get("FIREBASE_PRIVATE_KEY") if environ else None),
                "FIREBASE_CLIENT_EMAIL": bool(os.environ.get("FIREBASE_CLIENT_EMAIL") if environ else None),
            },
            "project_id": os.environ.get("FIREBASE_PROJECT_ID", "NOT_SET") if environ else "NOT_SET",
            "expected_bucket": f"{os.environ.get('FIREBASE_PROJECT_ID', 'unknown') if environ else 'unknown'}.appspot.com" if os.environ.get("FIREBASE_PROJECT_ID") else "NOT_SET"
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
    request: Request,
    file: UploadFile = File(...),
    claims: dict = Depends(verified_identity),
):
    """Store an original only for a verified, enabled Firebase identity."""
    form = await request.form()
    for key in IDENTITY_KEYS:
        for value in form.getlist(key):
            reject_identity_overrides(claims, {key: value})
    user_id = claims['uid']
    try:
        epoch = require_app_data_writable(db, user_id)
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
        
        # Process image file (convert HEIC/AVIF to JPEG/PNG if needed)
        processed_content_type = file.content_type or "application/octet-stream"
        try:
            processed_contents, processed_content_type = process_image_file(
                contents, file.filename or "unknown", file.content_type or "application/octet-stream"
            )
            logger.info(f"Processed file size: {len(processed_contents)} bytes, type: {processed_content_type}")
            
            # Use processed contents for upload
            contents = processed_contents
            
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
            require_app_data_writable(db, user_id, expected_epoch=epoch)
            blob.upload_from_string(contents, content_type=processed_content_type)
            require_app_data_writable(db, user_id, expected_epoch=epoch)
            logger.info("Successfully uploaded to Firebase Storage")
            
            # Make public and get URL
            logger.info("Making blob public...")
            blob.make_public()
            public_url = blob.public_url
            require_app_data_writable(db, user_id, expected_epoch=epoch)
            
            return JSONResponse(content={
                "success": True, 
                "image_url": public_url,
                "filename": file.filename,
                "size": len(contents)
            }, headers={"Cache-Control": "private, no-store"})
            
        except AppDataDeletionError as error:
            if 'blob' in locals():
                try:
                    blob.delete(if_generation_match=blob.generation)
                except Exception:
                    logger.warning("Interrupted upload cleanup will be retried by data deletion")
            raise HTTPException(error.status_code, error.detail) from error
        except Exception:
            # An upload or visibility failure is not a saved original. Never
            # return a substitute photo that downstream analysis could count.
            logger.warning("Photo storage upload could not be confirmed")
            return JSONResponse(
                status_code=503,
                content={
                    "success": False,
                    "code": "upload_unavailable",
                    "error": "Your photo upload could not be confirmed. Please try again.",
                    "retryable": True,
                },
                headers={"Retry-After": "5", "Cache-Control": "private, no-store"},
            )
            
    except HTTPException:
        raise
    except AppDataDeletionError as error:
        raise HTTPException(error.status_code, error.detail) from error
    except Exception as e:
        logger.error(f"Unexpected error in upload_image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to upload image")
