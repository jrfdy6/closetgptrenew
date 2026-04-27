from __future__ import annotations

import logging
import os
from typing import Any, Literal

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field

from ..auth.auth_service import get_current_user_id
from ..services.ai_runtime.codex_jobs import (
    DEFAULT_JOB_KIND,
    DEFAULT_WORKSPACE_SLUG,
    cancel_codex_job,
    claim_next_codex_job,
    complete_codex_job,
    fail_codex_job,
    get_codex_job_for_user,
    get_job_artifact_content,
    list_job_artifacts,
    queue_codex_job,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/codex-jobs", tags=["codex-jobs"])


def _env_flag_enabled(name: str) -> bool:
    return (os.getenv(name) or "").strip().lower() in {"1", "true", "yes", "on"}


def _allowed_operator_ids() -> set[str]:
    raw = os.getenv("EASYOUTFIT_CODEX_OPERATOR_USER_IDS", "")
    return {item.strip() for item in raw.split(",") if item.strip()}


def _require_codex_job_user_access(current_user_id: str) -> None:
    access_mode = (os.getenv("EASYOUTFIT_CODEX_JOB_ACCESS") or "operators").strip().lower()
    if access_mode == "authenticated":
        return
    if _env_flag_enabled("ENABLE_INTERNAL_DEBUG_ROUTES"):
        return
    if current_user_id in _allowed_operator_ids():
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Codex jobs are restricted to EasyOutfit operators",
    )


def _require_local_codex_token(x_local_codex_token: str | None) -> None:
    expected = (os.getenv("EASYOUTFIT_LOCAL_CODEX_TOKEN") or "").strip()
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="EASYOUTFIT_LOCAL_CODEX_TOKEN is not configured",
        )
    if (x_local_codex_token or "").strip() != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid local Codex bridge token")


class CodexJobCreateRequest(BaseModel):
    job_kind: Literal["wardrobe_metadata_audit"] = DEFAULT_JOB_KIND
    item_ids: list[str] = Field(default_factory=list)
    max_items: int = Field(default=20, ge=1, le=50)
    note: str | None = None
    workspace_slug: str = DEFAULT_WORKSPACE_SLUG


class CodexJobArtifactPayload(BaseModel):
    kind: str
    label: str
    filename: str
    mime_type: str = "text/plain"
    content: str


class CodexJobArtifactResponse(BaseModel):
    artifact_id: str
    kind: str
    label: str
    filename: str
    mime_type: str
    size_bytes: int | None = None
    created_at: str | None = None
    preview: str | None = None


class CodexJobCreateResponse(BaseModel):
    success: bool
    job_id: str
    status: str
    job_kind: str
    workspace_slug: str
    selected_item_count: int | None = None


class CodexJobStatusResponse(BaseModel):
    success: bool
    job_id: str
    status: str
    job_kind: str
    workspace_slug: str
    requested_by: str
    claimed_by: str | None = None
    error_message: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    completed_at: str | None = None
    failed_at: str | None = None
    result_payload: dict[str, Any] | None = None
    artifacts: list[CodexJobArtifactResponse] = Field(default_factory=list)


class CodexJobClaimRequest(BaseModel):
    worker_id: str
    workspace_slug: str = DEFAULT_WORKSPACE_SLUG
    job_kinds: list[str] = Field(default_factory=lambda: [DEFAULT_JOB_KIND])


class CodexJobClaimResponse(BaseModel):
    success: bool
    job_available: bool
    job_id: str | None = None
    status: str | None = None
    workspace_slug: str | None = None
    job_kind: str | None = None
    request_payload: dict[str, Any] | None = None
    context_packet: dict[str, Any] | None = None


class CodexJobCompleteRequest(BaseModel):
    worker_id: str
    model: str | None = None
    result_payload: dict[str, Any] | None = None
    raw_output: str | None = None
    command_stdout: str | None = None
    command_stderr: str | None = None
    artifacts: list[CodexJobArtifactPayload] = Field(default_factory=list)


class CodexJobFailRequest(BaseModel):
    worker_id: str
    error_message: str


def _build_artifact_responses(job_id: str) -> list[CodexJobArtifactResponse]:
    rendered: list[CodexJobArtifactResponse] = []
    for artifact in list_job_artifacts(job_id=job_id):
        artifact_id = str(artifact.get("artifact_id") or "")
        preview = None
        if artifact_id:
            content = get_job_artifact_content(job_id=job_id, artifact_id=artifact_id)
            if content:
                preview = content[:2000]
        rendered.append(
            CodexJobArtifactResponse(
                artifact_id=artifact_id,
                kind=str(artifact.get("kind") or ""),
                label=str(artifact.get("label") or ""),
                filename=str(artifact.get("filename") or ""),
                mime_type=str(artifact.get("mime_type") or "text/plain"),
                size_bytes=int(artifact.get("size_bytes") or 0) or None,
                created_at=str(artifact.get("created_at") or "") or None,
                preview=preview,
            )
        )
    return rendered


def _build_status_response(job: dict[str, Any]) -> CodexJobStatusResponse:
    job_id = str(job.get("id") or "")
    return CodexJobStatusResponse(
        success=True,
        job_id=job_id,
        status=str(job.get("status") or "unknown"),
        job_kind=str(job.get("job_kind") or ""),
        workspace_slug=str(job.get("workspace_slug") or ""),
        requested_by=str(job.get("requested_by") or ""),
        claimed_by=str(job.get("claimed_by") or "") or None,
        error_message=str(job.get("error_message") or "") or None,
        created_at=str(job.get("created_at") or "") or None,
        updated_at=str(job.get("updated_at") or "") or None,
        completed_at=str(job.get("completed_at") or "") or None,
        failed_at=str(job.get("failed_at") or "") or None,
        result_payload=job.get("result_payload") if isinstance(job.get("result_payload"), dict) else None,
        artifacts=_build_artifact_responses(job_id),
    )


@router.post("", response_model=CodexJobCreateResponse)
async def create_codex_job(
    request: CodexJobCreateRequest,
    current_user_id: str = Depends(get_current_user_id),
):
    _require_codex_job_user_access(current_user_id)
    try:
        job = queue_codex_job(
            requested_by=current_user_id,
            job_kind=request.job_kind,
            request_payload=request.dict(),
        )
        context_packet = job.get("context_packet") if isinstance(job.get("context_packet"), dict) else {}
        return CodexJobCreateResponse(
            success=True,
            job_id=str(job.get("id") or ""),
            status=str(job.get("status") or "pending"),
            job_kind=str(job.get("job_kind") or request.job_kind),
            workspace_slug=str(job.get("workspace_slug") or request.workspace_slug),
            selected_item_count=int(context_packet.get("selected_item_count") or 0) or None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Failed to create Codex job")
        raise HTTPException(status_code=500, detail=f"Unable to create Codex job: {str(exc)}") from exc


@router.get("/{job_id}", response_model=CodexJobStatusResponse)
async def get_codex_job_status(job_id: str, current_user_id: str = Depends(get_current_user_id)):
    _require_codex_job_user_access(current_user_id)
    job = get_codex_job_for_user(job_id, current_user_id)
    if not job:
        raise HTTPException(status_code=404, detail="Codex job not found")
    return _build_status_response(job)


@router.get("/{job_id}/artifacts", response_model=list[CodexJobArtifactResponse])
async def get_codex_job_artifacts(job_id: str, current_user_id: str = Depends(get_current_user_id)):
    _require_codex_job_user_access(current_user_id)
    job = get_codex_job_for_user(job_id, current_user_id)
    if not job:
        raise HTTPException(status_code=404, detail="Codex job not found")
    return _build_artifact_responses(job_id)


@router.post("/{job_id}/cancel", response_model=CodexJobStatusResponse)
async def cancel_user_codex_job(job_id: str, current_user_id: str = Depends(get_current_user_id)):
    _require_codex_job_user_access(current_user_id)
    try:
        job = cancel_codex_job(job_id=job_id, requested_by=current_user_id)
        return _build_status_response(job)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/claim-next", response_model=CodexJobClaimResponse)
async def claim_codex_job(
    request: CodexJobClaimRequest,
    x_local_codex_token: str | None = Header(default=None, alias="X-Local-Codex-Token"),
):
    _require_local_codex_token(x_local_codex_token)
    try:
        job = claim_next_codex_job(
            worker_id=request.worker_id,
            workspace_slug=request.workspace_slug,
            job_kinds=request.job_kinds,
        )
        if not job:
            return CodexJobClaimResponse(success=True, job_available=False)
        return CodexJobClaimResponse(
            success=True,
            job_available=True,
            job_id=str(job.get("id") or ""),
            status=str(job.get("status") or "running"),
            workspace_slug=str(job.get("workspace_slug") or ""),
            job_kind=str(job.get("job_kind") or ""),
            request_payload=job.get("request_payload") if isinstance(job.get("request_payload"), dict) else None,
            context_packet=job.get("context_packet") if isinstance(job.get("context_packet"), dict) else None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Failed to claim Codex job")
        raise HTTPException(status_code=500, detail=f"Unable to claim Codex job: {str(exc)}") from exc


@router.post("/{job_id}/complete", response_model=CodexJobStatusResponse)
async def complete_codex_job_route(
    job_id: str,
    request: CodexJobCompleteRequest,
    x_local_codex_token: str | None = Header(default=None, alias="X-Local-Codex-Token"),
):
    _require_local_codex_token(x_local_codex_token)
    try:
        job = complete_codex_job(
            job_id=job_id,
            worker_id=request.worker_id,
            model=request.model,
            result_payload=request.result_payload,
            raw_output=request.raw_output,
            command_stdout=request.command_stdout,
            command_stderr=request.command_stderr,
            artifacts=[artifact.dict() for artifact in request.artifacts],
        )
        return _build_status_response(job)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Failed to complete Codex job")
        raise HTTPException(status_code=500, detail=f"Unable to complete Codex job: {str(exc)}") from exc


@router.post("/{job_id}/fail", response_model=CodexJobStatusResponse)
async def fail_codex_job_route(
    job_id: str,
    request: CodexJobFailRequest,
    x_local_codex_token: str | None = Header(default=None, alias="X-Local-Codex-Token"),
):
    _require_local_codex_token(x_local_codex_token)
    try:
        job = fail_codex_job(job_id=job_id, worker_id=request.worker_id, error_message=request.error_message)
        return _build_status_response(job)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Failed to fail Codex job")
        raise HTTPException(status_code=500, detail=f"Unable to fail Codex job: {str(exc)}") from exc
