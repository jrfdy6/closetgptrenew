from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import logging
import time

# Best-effort imports of existing services if present in the codebase.
# The goal is to avoid hard crashes if a module name differs; we log and continue.
try:
    from app.services.firestore_client import db  # type: ignore
except Exception as e:  # pragma: no cover
    db = None  # noqa: N816
    logging.warning("Firestore client not available: %s", e)

try:
    # If you already have a Drive client wrapper, prefer it.
    from app.services.drive_client import list_files_in_folder, extract_text  # type: ignore
except Exception as e:  # pragma: no cover
    list_files_in_folder = None
    extract_text = None
    logging.warning("Drive client wrapper not available: %s", e)

# If no wrapper exists, fall back to direct Google API usage.
google_drive_ready = False
try:
    from google.oauth2 import service_account  # type: ignore
    from googleapiclient.discovery import build  # type: ignore
    import io  # type: ignore
    from PyPDF2 import PdfReader  # type: ignore
    google_drive_ready = True
except Exception as e:  # pragma: no cover
    logging.warning("Google client libraries not fully available: %s", e)

router = APIRouter()


class IngestDriveRequest(BaseModel):
    user_id: str
    folder_id: str
    max_files: Optional[int] = 25


def _build_drive_service() -> Any:
    # Prefer explicit GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE; else try GOOGLE_APPLICATION_CREDENTIALS.
    creds_path = os.getenv("GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE") or os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS"
    )
    if not creds_path or not os.path.isabs(creds_path) or not os.path.exists(creds_path):
        raise RuntimeError(
            "Google Drive service account file not found. "
            "Set GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE (recommended) or GOOGLE_APPLICATION_CREDENTIALS to an absolute path."
        )
    scopes = ["https://www.googleapis.com/auth/drive.readonly"]
    credentials = service_account.Credentials.from_service_account_file(
        creds_path, scopes=scopes
    )
    return build("drive", "v3", credentials=credentials, cache_discovery=False)


def _fallback_list_files_in_folder(drive_service: Any, folder_id: str, max_files: int) -> List[Dict[str, Any]]:
    query = f"'{folder_id}' in parents and trashed=false"
    resp = (
        drive_service.files()
        .list(q=query, fields="files(id, name, mimeType)", pageSize=max_files)
        .execute()
    )
    return resp.get("files", [])


def _fallback_extract_text(drive_service: Any, file_id: str, mime_type: str) -> str:
    # Minimal extraction: PDFs via PyPDF2, Google Docs/Slides via export text/plain.
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
    elif mime_type in [
        "application/vnd.google-apps.document",
        "application/vnd.google-apps.presentation",
    ]:
        exported = (
            drive_service.files()
            .export(fileId=file_id, mimeType="text/plain")
            .execute()
        )
        if isinstance(exported, bytes):
            return exported.decode("utf-8", errors="ignore")
        return str(exported)
    # Unsupported types are skipped for now.
    return ""


def _log_ingest_job(user_id: str, folder_id: str, status: str, details: Dict[str, Any]) -> None:
    if db is None:
        logging.info("[ingest_job] %s | user=%s folder=%s details=%s", status, user_id, folder_id, details)
        return
    try:
        db.collection("ingest_jobs").add(
            {
                "user_id": user_id,
                "folder_id": folder_id,
                "status": status,
                "details": details,
                "ts": time.time(),
            }
        )
    except Exception as e:
        logging.warning("Failed to log ingest job to Firestore: %s", e)


def _ingest_drive_background(user_id: str, folder_id: str, max_files: int) -> None:
    _log_ingest_job(user_id, folder_id, "started", {"max_files": max_files})
    try:
        # Choose list/extract implementations
        if list_files_in_folder and extract_text:
            files = list_files_in_folder(folder_id)  # type: ignore
            if isinstance(files, dict) and "files" in files:
                files = files["files"]
        else:
            if not google_drive_ready:
                raise RuntimeError("Google Drive client not available and no wrapper present.")
            drive_service = _build_drive_service()
            files = _fallback_list_files_in_folder(drive_service, folder_id, max_files)

        files = files[:max_files]
        logging.info("[ingest_drive] Found %d files in folder=%s", len(files), folder_id)

        processed = 0
        skipped = 0
        errors: List[str] = []

        # Per-file extraction (chunking/embeddings intentionally omitted here to keep job non-blocking and robust).
        for f in files:
            file_id = f.get("id")
            name = f.get("name")
            mime_type = f.get("mimeType")
            try:
                if extract_text:
                    text = extract_text(file_id, mime_type)  # type: ignore
                else:
                    drive_service = _build_drive_service()
                    text = _fallback_extract_text(drive_service, file_id, mime_type)
                if not text:
                    skipped += 1
                    logging.info("[ingest_drive] Skipped empty/unsupported file: %s (%s)", name, mime_type)
                    continue
                # Optionally, save a lightweight record to Firestore to confirm visibility.
                if db is not None:
                    db.collection("users").document(user_id).collection("ingested_files").document(file_id).set(
                        {
                            "file_id": file_id,
                            "name": name,
                            "mime_type": mime_type,
                            "folder_id": folder_id,
                            "text_preview": text[:1000],
                            "ts": time.time(),
                        }
                    )
                processed += 1
                logging.info("[ingest_drive] Processed: %s (%s)", name, mime_type)
            except Exception as e:
                errors.append(f"{name}:{e}")
                logging.exception("[ingest_drive] Error processing file %s: %s", name, e)

        _log_ingest_job(
            user_id,
            folder_id,
            "completed",
            {"processed": processed, "skipped": skipped, "errors": errors},
        )
        logging.info("[ingest_drive] Completed. processed=%d skipped=%d errors=%d", processed, skipped, len(errors))
    except Exception as e:
        _log_ingest_job(user_id, folder_id, "failed", {"error": str(e)})
        logging.exception("[ingest_drive] Fatal error: %s", e)


@router.post("/ingest_drive")
def ingest_drive(req: IngestDriveRequest, background_tasks: BackgroundTasks):
    """
    Non-blocking Google Drive ingestion trigger.
    - Returns 202 immediately with a job descriptor.
    - Background task lists files and stores lightweight records in Firestore (if available).
    - Robust logging for each step to diagnose issues quickly.
    """
    logging.info("[ingest_drive] Triggered for user=%s folder=%s max_files=%s", req.user_id, req.folder_id, req.max_files)
    background_tasks.add_task(_ingest_drive_background, req.user_id, req.folder_id, int(req.max_files or 25))
    return {
        "accepted": True,
        "message": "Ingestion started in background.",
        "user_id": req.user_id,
        "folder_id": req.folder_id,
        "max_files": req.max_files or 25,
        "status": "pending",
    }



