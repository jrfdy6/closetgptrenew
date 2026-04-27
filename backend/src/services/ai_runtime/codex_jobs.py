from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from firebase_admin import firestore

try:
    from src.config.firebase import db, firebase_initialized
except ImportError:  # pragma: no cover
    try:
        from config.firebase import db, firebase_initialized
    except ImportError:  # pragma: no cover
        db = None
        firebase_initialized = False

logger = logging.getLogger(__name__)

CODEX_JOBS_COLLECTION = "codex_jobs"
CODEX_JOB_ARTIFACTS_SUBCOLLECTION = "artifacts"
DEFAULT_WORKSPACE_SLUG = "easyoutfitapp"
DEFAULT_JOB_KIND = "wardrobe_metadata_audit"
SUPPORTED_JOB_KINDS = {DEFAULT_JOB_KIND}
MAX_AUDIT_ITEMS = 50
MAX_ARTIFACT_CONTENT_CHARS = 200_000


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_now_iso() -> str:
    return _utc_now().isoformat()


def _utc_now_ms() -> int:
    return int(_utc_now().timestamp() * 1000)


def _require_db():
    if not firebase_initialized or db is None:
        raise RuntimeError("Firestore not available for Codex jobs")
    return db


def _job_ref(job_id: str):
    return _require_db().collection(CODEX_JOBS_COLLECTION).document(job_id)


def _normalize_workspace_slug(value: str | None) -> str:
    slug = " ".join((value or "").split()).strip().lower()
    return slug or DEFAULT_WORKSPACE_SLUG


def _normalize_job_kind(value: str | None) -> str:
    normalized = " ".join((value or "").split()).strip().lower()
    if normalized not in SUPPORTED_JOB_KINDS:
        raise ValueError(f"Unsupported codex job kind: {value}")
    return normalized


def _serialize_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, list):
        return [_serialize_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _serialize_value(val) for key, val in value.items()}
    return value


def _serialize_snapshot(snapshot) -> dict[str, Any]:
    payload = snapshot.to_dict() or {}
    payload["id"] = snapshot.id
    return _serialize_value(payload)


def _sanitize_artifact_content(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        normalized = content
    else:
        normalized = json.dumps(content, indent=2, ensure_ascii=True, default=str)
    if len(normalized) > MAX_ARTIFACT_CONTENT_CHARS:
        return normalized[:MAX_ARTIFACT_CONTENT_CHARS]
    return normalized


def _normalize_artifact_spec(spec: dict[str, Any], *, job_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    content = _sanitize_artifact_content(spec.get("content"))
    artifact_id = str(spec.get("artifact_id") or uuid.uuid4())
    filename = str(spec.get("filename") or f"{artifact_id}.txt")
    mime_type = str(spec.get("mime_type") or "text/plain")
    created_at_iso = _utc_now_iso()
    created_at_ms = _utc_now_ms()
    metadata = {
        "artifact_id": artifact_id,
        "job_id": job_id,
        "kind": str(spec.get("kind") or "report"),
        "label": str(spec.get("label") or filename),
        "filename": filename,
        "mime_type": mime_type,
        "size_bytes": len(content.encode("utf-8")),
        "created_at": created_at_iso,
        "created_at_ms": created_at_ms,
    }
    document = {
        **metadata,
        "content": content,
        "updated_at": created_at_iso,
        "updated_at_ms": created_at_ms,
    }
    return metadata, document


def _build_wardrobe_audit_output_schema() -> dict[str, Any]:
    nullable_string = {"type": ["string", "null"]}
    nullable_string_array = {
        "type": ["array", "null"],
        "items": {"type": "string"},
    }
    return {
        "type": "object",
        "properties": {
            "summary": {"type": "string", "minLength": 20},
            "global_findings": {"type": "array", "items": {"type": "string"}},
            "priority_item_ids": {"type": "array", "items": {"type": "string"}},
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "item_id": {"type": "string"},
                        "status": {"type": "string", "enum": ["ok", "review", "reprocess"]},
                        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                        "issues": {"type": "array", "items": {"type": "string"}},
                        "recommended_changes": {
                            "type": "object",
                            "properties": {
                                "name": nullable_string,
                                "type": nullable_string,
                                "subType": nullable_string,
                                "style": nullable_string_array,
                                "occasion": nullable_string_array,
                                "mood": nullable_string_array,
                                "season": nullable_string_array,
                                "natural_description": nullable_string,
                            },
                            "required": [
                                "name",
                                "type",
                                "subType",
                                "style",
                                "occasion",
                                "mood",
                                "season",
                                "natural_description",
                            ],
                            "additionalProperties": False,
                        },
                        "rationale": {"type": "string"},
                    },
                    "required": ["item_id", "status", "confidence", "issues", "recommended_changes", "rationale"],
                    "additionalProperties": False,
                },
            },
            "next_actions": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["summary", "global_findings", "priority_item_ids", "items", "next_actions"],
        "additionalProperties": False,
    }


def _sanitize_wardrobe_item(item_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    metadata = payload.get("metadata") or {}
    visual = metadata.get("visualAttributes") or {}
    dominant_colors = payload.get("dominantColors") or []
    simplified_colors: list[str] = []
    for color in dominant_colors[:3]:
        if isinstance(color, dict):
            name = str(color.get("name") or "").strip()
            if name:
                simplified_colors.append(name)
        elif isinstance(color, str) and color.strip():
            simplified_colors.append(color.strip())

    return {
        "id": item_id,
        "name": payload.get("name"),
        "type": payload.get("type"),
        "subType": payload.get("subType"),
        "brand": payload.get("brand"),
        "style": payload.get("style") or [],
        "occasion": payload.get("occasion") or [],
        "mood": payload.get("mood") or [],
        "season": payload.get("season") or [],
        "dominant_colors": simplified_colors,
        "processing_status": payload.get("processing_status"),
        "has_background_removed_image": bool(
            payload.get("backgroundRemovedUrl") or payload.get("background_removed_url")
        ),
        "visual_attributes": {
            "wearLayer": visual.get("wearLayer"),
            "sleeveLength": visual.get("sleeveLength"),
            "material": visual.get("material"),
            "pattern": visual.get("pattern"),
            "fit": visual.get("fit"),
            "formalLevel": visual.get("formalLevel"),
            "neckline": visual.get("neckline"),
            "genderTarget": visual.get("genderTarget"),
            "statementLevel": visual.get("statementLevel"),
        },
        "natural_description": metadata.get("naturalDescription"),
        "createdAt": payload.get("createdAt"),
        "updatedAt": payload.get("updatedAt"),
    }


def _fetch_user_wardrobe_items(user_id: str, *, item_ids: list[str] | None, max_items: int) -> list[dict[str, Any]]:
    firestore_db = _require_db()
    items: list[dict[str, Any]] = []

    if item_ids:
        for item_id in item_ids[:MAX_AUDIT_ITEMS]:
            snapshot = firestore_db.collection("wardrobe").document(item_id).get()
            if not snapshot.exists:
                continue
            payload = snapshot.to_dict() or {}
            owner_id = str(payload.get("userId") or payload.get("user_id") or "")
            if owner_id != user_id:
                continue
            items.append(_sanitize_wardrobe_item(snapshot.id, payload))
        return items[:max_items]

    query = firestore_db.collection("wardrobe").where("userId", "==", user_id).limit(max_items)
    for snapshot in query.stream():
        payload = snapshot.to_dict() or {}
        items.append(_sanitize_wardrobe_item(snapshot.id, payload))
    return items[:max_items]


def _build_wardrobe_audit_prompt(*, user_id: str, selected_items: list[dict[str, Any]], note: str | None) -> str:
    summary = {
        "user_id": user_id,
        "item_count": len(selected_items),
        "types": sorted({str(item.get("type") or "unknown") for item in selected_items}),
    }
    note_line = f"Operator note: {note.strip()}\n\n" if note and note.strip() else ""
    serialized_items = json.dumps(selected_items, indent=2, ensure_ascii=True, default=str)
    return (
        "You are auditing EasyOutfit wardrobe metadata before any production model changes.\n"
        "Review the existing saved metadata for likely mistakes, suspicious gaps, and items that should be re-run through image analysis.\n"
        "Do not invent information that is not supported by the saved metadata.\n"
        "Prefer conservative recommendations.\n\n"
        f"{note_line}"
        "Return JSON that matches the provided schema exactly.\n"
        "Use item status meanings:\n"
        "- ok: metadata looks usable as-is\n"
        "- review: metadata has likely issues but can probably be fixed manually\n"
        "- reprocess: item should be re-run through the hosted image-analysis pipeline\n\n"
        f"Audit summary:\n{json.dumps(summary, indent=2, ensure_ascii=True)}\n\n"
        f"Wardrobe items to audit:\n{serialized_items}\n"
    )


def _build_job_context(job_kind: str, *, requested_by: str, request_payload: dict[str, Any]) -> dict[str, Any]:
    if job_kind != DEFAULT_JOB_KIND:
        raise ValueError(f"Unsupported codex job kind: {job_kind}")

    raw_item_ids = request_payload.get("item_ids") or []
    item_ids = [str(item_id).strip() for item_id in raw_item_ids if str(item_id).strip()]
    max_items = min(int(request_payload.get("max_items") or 20), MAX_AUDIT_ITEMS)
    note = str(request_payload.get("note") or "").strip() or None
    selected_items = _fetch_user_wardrobe_items(requested_by, item_ids=item_ids, max_items=max_items)
    if not selected_items:
        raise ValueError("No wardrobe items available for Codex audit")

    return {
        "workspace_slug": _normalize_workspace_slug(request_payload.get("workspace_slug")),
        "prompt": _build_wardrobe_audit_prompt(user_id=requested_by, selected_items=selected_items, note=note),
        "output_schema": _build_wardrobe_audit_output_schema(),
        "selected_item_ids": [str(item.get("id") or "") for item in selected_items],
        "selected_item_count": len(selected_items),
        "selected_items": selected_items,
        "note": note,
    }


def queue_codex_job(*, requested_by: str, job_kind: str, request_payload: dict[str, Any]) -> dict[str, Any]:
    normalized_kind = _normalize_job_kind(job_kind)
    context_packet = _build_job_context(normalized_kind, requested_by=requested_by, request_payload=request_payload)
    workspace_slug = _normalize_workspace_slug(
        request_payload.get("workspace_slug") or context_packet.get("workspace_slug")
    )
    now_ms = _utc_now_ms()
    job_id = str(uuid.uuid4())
    payload = {
        "workspace_slug": workspace_slug,
        "requested_by": requested_by,
        "job_kind": normalized_kind,
        "status": "pending",
        "request_payload": _serialize_value(request_payload),
        "context_packet": _serialize_value(context_packet),
        "claimed_by": None,
        "claimed_at": None,
        "claimed_at_ms": None,
        "completed_at": None,
        "completed_at_ms": None,
        "failed_at": None,
        "failed_at_ms": None,
        "canceled_at": None,
        "canceled_at_ms": None,
        "error_message": None,
        "result_payload": None,
        "artifacts": [],
        "created_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP,
        "created_at_ms": now_ms,
        "updated_at_ms": now_ms,
    }
    _job_ref(job_id).set(payload)
    return get_codex_job(job_id)


def get_codex_job(job_id: str) -> dict[str, Any] | None:
    snapshot = _job_ref(job_id).get()
    if not snapshot.exists:
        return None
    return _serialize_snapshot(snapshot)


def get_codex_job_for_user(job_id: str, requested_by: str) -> dict[str, Any] | None:
    job = get_codex_job(job_id)
    if not job:
        return None
    if str(job.get("requested_by") or "") != requested_by:
        return None
    return job


def claim_next_codex_job(*, worker_id: str, workspace_slug: str | None, job_kinds: list[str] | None = None) -> dict[str, Any] | None:
    firestore_db = _require_db()
    normalized_workspace = _normalize_workspace_slug(workspace_slug)
    normalized_job_kinds = {_normalize_job_kind(kind) for kind in (job_kinds or [DEFAULT_JOB_KIND])}
    transaction = firestore_db.transaction()

    @firestore.transactional
    def _claim(transaction_obj):
        query = firestore_db.collection(CODEX_JOBS_COLLECTION).where("status", "==", "pending").limit(25)
        snapshots = list(transaction_obj.get(query))
        candidates: list[Any] = []
        for snapshot in snapshots:
            payload = snapshot.to_dict() or {}
            if _normalize_workspace_slug(payload.get("workspace_slug")) != normalized_workspace:
                continue
            if str(payload.get("job_kind") or "") not in normalized_job_kinds:
                continue
            candidates.append(snapshot)

        candidates.sort(key=lambda snap: int((snap.to_dict() or {}).get("created_at_ms") or 0))
        if not candidates:
            return None

        claimed_snapshot = candidates[0]
        now_ms = _utc_now_ms()
        transaction_obj.update(
            claimed_snapshot.reference,
            {
                "status": "running",
                "claimed_by": worker_id,
                "claimed_at": firestore.SERVER_TIMESTAMP,
                "claimed_at_ms": now_ms,
                "updated_at": firestore.SERVER_TIMESTAMP,
                "updated_at_ms": now_ms,
            },
        )
        return claimed_snapshot.id

    job_id = _claim(transaction)
    if not job_id:
        return None
    return get_codex_job(job_id)


def _write_job_artifacts(job_id: str, artifact_specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not artifact_specs:
        return []

    firestore_db = _require_db()
    job_reference = _job_ref(job_id)
    batch = firestore_db.batch()
    metadata_entries: list[dict[str, Any]] = []
    for artifact_spec in artifact_specs:
        metadata, document = _normalize_artifact_spec(artifact_spec, job_id=job_id)
        artifact_ref = job_reference.collection(CODEX_JOB_ARTIFACTS_SUBCOLLECTION).document(metadata["artifact_id"])
        batch.set(artifact_ref, document)
        metadata_entries.append(metadata)

    batch.commit()
    return metadata_entries


def complete_codex_job(
    *,
    job_id: str,
    worker_id: str,
    model: str | None,
    result_payload: dict[str, Any] | None,
    raw_output: str | None,
    command_stdout: str | None,
    command_stderr: str | None,
    artifacts: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    job = get_codex_job(job_id)
    if not job:
        raise ValueError("Codex job not found")
    if str(job.get("status") or "") not in {"running", "pending"}:
        raise ValueError(f"Codex job {job_id} is not active")
    claimed_by = str(job.get("claimed_by") or "")
    if claimed_by and claimed_by != worker_id:
        raise ValueError("Codex job is claimed by a different worker")

    artifact_specs = list(artifacts or [])
    if raw_output:
        artifact_specs.append(
            {
                "kind": "raw_output",
                "label": "Raw Codex Output",
                "filename": "raw-output.json",
                "mime_type": "application/json",
                "content": raw_output,
            }
        )
    if command_stdout:
        artifact_specs.append(
            {
                "kind": "stdout",
                "label": "Codex Stdout",
                "filename": "codex-stdout.log",
                "mime_type": "text/plain",
                "content": command_stdout,
            }
        )
    if command_stderr:
        artifact_specs.append(
            {
                "kind": "stderr",
                "label": "Codex Stderr",
                "filename": "codex-stderr.log",
                "mime_type": "text/plain",
                "content": command_stderr,
            }
        )

    metadata_entries = _write_job_artifacts(job_id, artifact_specs)
    now_ms = _utc_now_ms()
    update_payload: dict[str, Any] = {
        "status": "completed",
        "claimed_by": worker_id,
        "completed_at": firestore.SERVER_TIMESTAMP,
        "completed_at_ms": now_ms,
        "updated_at": firestore.SERVER_TIMESTAMP,
        "updated_at_ms": now_ms,
        "error_message": None,
        "artifacts": metadata_entries,
    }
    if result_payload is not None:
        update_payload["result_payload"] = _serialize_value(result_payload)
    if model:
        update_payload["completed_model"] = model
    _job_ref(job_id).update(update_payload)
    return get_codex_job(job_id)


def fail_codex_job(*, job_id: str, worker_id: str, error_message: str) -> dict[str, Any]:
    job = get_codex_job(job_id)
    if not job:
        raise ValueError("Codex job not found")
    claimed_by = str(job.get("claimed_by") or "")
    if claimed_by and claimed_by != worker_id:
        raise ValueError("Codex job is claimed by a different worker")
    now_ms = _utc_now_ms()
    _job_ref(job_id).update(
        {
            "status": "failed",
            "claimed_by": worker_id or claimed_by or None,
            "failed_at": firestore.SERVER_TIMESTAMP,
            "failed_at_ms": now_ms,
            "updated_at": firestore.SERVER_TIMESTAMP,
            "updated_at_ms": now_ms,
            "error_message": str(error_message or "Unknown Codex job failure")[:4000],
        }
    )
    return get_codex_job(job_id)


def cancel_codex_job(*, job_id: str, requested_by: str) -> dict[str, Any]:
    job = get_codex_job_for_user(job_id, requested_by)
    if not job:
        raise ValueError("Codex job not found")
    if str(job.get("status") or "") in {"completed", "failed", "canceled"}:
        raise ValueError(f"Codex job {job_id} is already terminal")
    now_ms = _utc_now_ms()
    _job_ref(job_id).update(
        {
            "status": "canceled",
            "canceled_at": firestore.SERVER_TIMESTAMP,
            "canceled_at_ms": now_ms,
            "updated_at": firestore.SERVER_TIMESTAMP,
            "updated_at_ms": now_ms,
        }
    )
    return get_codex_job(job_id)


def list_job_artifacts(*, job_id: str) -> list[dict[str, Any]]:
    job = get_codex_job(job_id)
    if not job:
        raise ValueError("Codex job not found")
    snapshots = _job_ref(job_id).collection(CODEX_JOB_ARTIFACTS_SUBCOLLECTION).order_by("created_at_ms").stream()
    return [_serialize_snapshot(snapshot) for snapshot in snapshots]


def get_job_artifact_content(*, job_id: str, artifact_id: str) -> str | None:
    snapshot = _job_ref(job_id).collection(CODEX_JOB_ARTIFACTS_SUBCOLLECTION).document(artifact_id).get()
    if not snapshot.exists:
        return None
    payload = snapshot.to_dict() or {}
    return str(payload.get("content") or "")
