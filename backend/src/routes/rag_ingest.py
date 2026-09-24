"""
Enhanced RAG Ingestion Route - Chunks, embeds, and stores in Firestore
This extends the basic ingest_drive functionality with proper chunking and embedding
"""
import logging
import os
import time
from uuid import uuid4
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from src.auth.operator import require_operator
from src.services.app_data_privacy import require_app_data_writable, write_app_record, AppDataDeletionError
from src.auth.verified_identity import reject_identity_overrides

logger = logging.getLogger(__name__)

router = APIRouter()

# Try to import dependencies
try:
    from src.config.firebase import db, firebase_initialized
except ImportError:
    try:
        from config.firebase import db, firebase_initialized
    except ImportError:
        db = None
        firebase_initialized = False
        logger.warning("Firebase not available for RAG ingestion")

from ..services.ai_runtime.embedding_runtime import generate_text_embedding

# Import Google Drive functions
# We'll implement these directly since the ingest_drive module is in a different location
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    import io
    from PyPDF2 import PdfReader
    google_drive_ready = True
    
    def _build_drive_service():
        """Build Google Drive service from credentials"""
        creds_path = os.getenv("GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not creds_path or not os.path.isabs(creds_path) or not os.path.exists(creds_path):
            raise RuntimeError(
                "Google Drive service account file not found. "
                "Set GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE (recommended) or GOOGLE_APPLICATION_CREDENTIALS to an absolute path."
            )
        scopes = ["https://www.googleapis.com/auth/drive.readonly"]
        credentials = service_account.Credentials.from_service_account_file(creds_path, scopes=scopes)
        return build("drive", "v3", credentials=credentials, cache_discovery=False)
    
    def _fallback_list_files_in_folder(drive_service, folder_id: str, max_files: int):
        """List files in a Google Drive folder"""
        query = f"'{folder_id}' in parents and trashed=false"
        resp = drive_service.files().list(q=query, fields="files(id, name, mimeType)", pageSize=max_files).execute()
        return resp.get("files", [])
    
    def _fallback_extract_text(drive_service, file_id: str, mime_type: str) -> str:
        """Extract text from a Google Drive file"""
        if mime_type == "application/pdf":
            request = drive_service.files().get_media(fileId=file_id)
            fh = io.BytesIO(request.execute())
            reader = PdfReader(fh)
            text = ""
            for page in reader.pages:
                try:
                    text += page.extract_text() or ""
                except Exception:
                    continue
            return text
        elif mime_type in ["application/vnd.google-apps.document", "application/vnd.google-apps.presentation"]:
            exported = drive_service.files().export(fileId=file_id, mimeType="text/plain").execute()
            if isinstance(exported, bytes):
                return exported.decode("utf-8", errors="ignore")
            return str(exported)
        return ""
except ImportError:
    google_drive_ready = False
    logger.warning("Google Drive libraries not available")
    
    def _build_drive_service():
        raise RuntimeError("Google Drive client not available")
    
    def _fallback_list_files_in_folder(*args, **kwargs):
        return []
    
    def _fallback_extract_text(*args, **kwargs):
        return ""


class IngestDriveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: Optional[str] = None
    folder_id: str = Field(min_length=1, pattern=r"^[A-Za-z0-9_-]+$")
    max_files: int = Field(default=10, ge=1, le=100)


def _chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks for better retrieval"""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start = end - overlap
        if start >= len(text):
            break
    return chunks


async def _generate_embedding(text: str) -> Optional[List[float]]:
    """Generate embedding for text using the centralized embedding runtime."""
    embedding = await generate_text_embedding(text, max_input_chars=8000)
    if embedding is None:
        logger.warning("Embedding runtime unavailable, skipping embedding generation")
    return embedding


async def _process_and_store_chunks(
    user_id: str,
    file_id: str,
    file_name: str,
    folder_id: str,
    text: str,
    mime_type: str,
    app_data_epoch: Optional[int] = None,
) -> int:
    """Chunk text, generate embeddings, and store in Firestore"""
    if not db or not firebase_initialized:
        logger.warning("Firestore not available, skipping chunk storage")
        return 0
    
    try:
        epoch = require_app_data_writable(db, user_id, expected_epoch=app_data_epoch)
        # Chunk the text
        chunks = _chunk_text(text, chunk_size=1000, overlap=200)
        stored_count = 0
        
        for idx, chunk_text in enumerate(chunks):
            # Generate embedding
            embedding = await _generate_embedding(chunk_text)
            
            # Create chunk document
            chunk_doc = {
                "user_id": user_id,
                "file_id": file_id,
                "file_name": file_name,
                "folder_id": folder_id,
                "text": chunk_text,
                "chunk_index": idx,
                "mime_type": mime_type,
                "metadata": {
                    "total_chunks": len(chunks),
                    "chunk_size": len(chunk_text),
                    "file_name": file_name
                },
                "created_at": time.time(),
                "updated_at": time.time()
            }
            
            # Add embedding if available
            if embedding:
                chunk_doc["embedding"] = embedding
            
            # Store in Firestore
            chunk_ref = db.collection("knowledge_chunks").document(uuid4().hex)
            write_app_record(db, user_id, chunk_ref, chunk_doc, expected_epoch=epoch)
            stored_count += 1
        
        logger.info(f"Stored {stored_count} chunks for file {file_name}")
        return stored_count
    
    except Exception as e:
        logger.exception(f"Error processing chunks for {file_name}: {e}")
        return 0


async def _ingest_drive_background_rag(
    user_id: str,
    folder_id: str,
    max_files: int,
    app_data_epoch: Optional[int] = None,
) -> None:
    """Enhanced background ingestion with chunking and embedding"""
    try:
        epoch = require_app_data_writable(db, user_id, expected_epoch=app_data_epoch)
        if not google_drive_ready:
            raise RuntimeError("Google Drive client not available")
        
        # Build drive service
        drive_service = _build_drive_service()
        
        # List files
        files = _fallback_list_files_in_folder(drive_service, folder_id, max_files)
        files = files[:max_files]
        
        logger.info(f"[RAG ingest] Found {len(files)} files in folder={folder_id}")
        
        processed = 0
        skipped = 0
        errors: List[str] = []
        total_chunks = 0
        
        for f in files:
            file_id = f.get("id")
            name = f.get("name")
            mime_type = f.get("mimeType")
            
            try:
                # Extract text
                text = _fallback_extract_text(drive_service, file_id, mime_type)
                
                if not text or len(text.strip()) < 50:  # Skip very short files
                    skipped += 1
                    logger.info(f"[RAG ingest] Skipped empty file: {name} ({mime_type})")
                    continue
                
                # Process and store chunks with embeddings
                chunks_stored = await _process_and_store_chunks(
                    user_id, file_id, name, folder_id, text, mime_type, epoch
                )
                
                if chunks_stored > 0:
                    total_chunks += chunks_stored
                    processed += 1
                    logger.info(f"[RAG ingest] Processed: {name} -> {chunks_stored} chunks")
                else:
                    skipped += 1
            
            except Exception as e:
                error_msg = f"{name}:{str(e)}"
                errors.append(error_msg)
                logger.exception(f"[RAG ingest] Error processing {name}: {e}")
        
        # Log completion
        logger.info(
            f"[RAG ingest] Completed. processed={processed} skipped={skipped} "
            f"chunks={total_chunks} errors={len(errors)}"
        )
        
        # Store job status
        if db and firebase_initialized:
            try:
                write_app_record(db, user_id, db.collection("ingest_jobs").document(uuid4().hex), {
                    "user_id": user_id,
                    "folder_id": folder_id,
                    "status": "completed",
                    "details": {
                        "processed": processed,
                        "skipped": skipped,
                        "total_chunks": total_chunks,
                        "errors": errors
                    },
                    "ts": time.time()
                }, expected_epoch=epoch)
            except Exception as e:
                logger.warning(f"Failed to log ingest job: {e}")
    
    except Exception as e:
        logger.exception(f"[RAG ingest] Fatal error: {e}")
        if db and firebase_initialized:
            try:
                write_app_record(db, user_id, db.collection("ingest_jobs").document(uuid4().hex), {
                    "user_id": user_id,
                    "folder_id": folder_id,
                    "status": "failed",
                    "details": {"error": str(e)},
                    "ts": time.time()
                }, expected_epoch=epoch)
            except Exception:
                pass


@router.post("/ingest_drive")
async def ingest_drive_rag(
    req: IngestDriveRequest,
    background_tasks: BackgroundTasks,
    claims: dict = Depends(require_operator),
):
    """
    Ingest a Google Drive folder with full RAG pipeline:
    - Downloads files from Google Drive
    - Extracts text
    - Chunks text into manageable pieces
    - Generates embeddings
    - Stores in Firestore for retrieval
    
    Returns 202 immediately, processing happens in background.
    """
    reject_identity_overrides(claims, req.model_dump(exclude_unset=True))
    user_id = claims["uid"]
    logger.info(
        f"[RAG ingest] Triggered for user={user_id} "
        f"folder={req.folder_id} max_files={req.max_files}"
    )
    
    try:
        epoch = require_app_data_writable(db, user_id)
    except AppDataDeletionError as error:
        raise HTTPException(error.status_code, error.detail) from error
    background_tasks.add_task(
        _ingest_drive_background_rag,
        user_id,
        req.folder_id,
        int(req.max_files or 10),
        epoch,
    )
    
    return {
        "accepted": True,
        "message": "Ingestion started in background. Files will be chunked, embedded, and stored.",
        "user_id": user_id,
        "folder_id": req.folder_id,
        "max_files": req.max_files or 10,
        "status": "pending"
    }
