#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse
from typing import Any


DEFAULT_API_BASE = os.getenv(
    "EASYOUTFIT_CODEX_API_BASE_URL",
    "http://localhost:8080/api/codex-jobs",
)
DEFAULT_WORKSPACE_ROOT = os.getenv(
    "EASYOUTFIT_LOCAL_CODEX_WORKSPACE_ROOT",
    "/Users/neo/Desktop/closetgptrenew",
)
DEFAULT_WORKSPACE_SLUG = os.getenv("EASYOUTFIT_LOCAL_CODEX_WORKSPACE_SLUG", "easyoutfitapp")
DEFAULT_MODEL = os.getenv("EASYOUTFIT_LOCAL_CODEX_BRIDGE_MODEL", "gpt-5.4-mini")
DEFAULT_REASONING_EFFORT = os.getenv("EASYOUTFIT_LOCAL_CODEX_BRIDGE_REASONING_EFFORT", "medium")
DEFAULT_POLL_SECONDS = float(os.getenv("EASYOUTFIT_LOCAL_CODEX_BRIDGE_POLL_SECONDS", "1"))
DEFAULT_TIMEOUT_SECONDS = int(os.getenv("EASYOUTFIT_LOCAL_CODEX_BRIDGE_TIMEOUT_SECONDS", "420"))
DEFAULT_HTTP_TIMEOUT_SECONDS = int(os.getenv("EASYOUTFIT_LOCAL_CODEX_HTTP_TIMEOUT_SECONDS", "45"))
DEFAULT_HTTP_RETRIES = int(os.getenv("EASYOUTFIT_LOCAL_CODEX_HTTP_RETRIES", "3"))
DEFAULT_ERROR_BACKOFF_SECONDS = float(os.getenv("EASYOUTFIT_LOCAL_CODEX_ERROR_BACKOFF_SECONDS", "8"))
DEFAULT_MAX_ERROR_BACKOFF_SECONDS = float(os.getenv("EASYOUTFIT_LOCAL_CODEX_MAX_ERROR_BACKOFF_SECONDS", "60"))
RETRYABLE_HTTP_STATUS_CODES = {502, 503, 504}
SUPPORTED_JOB_KINDS = ["wardrobe_metadata_audit", "upload_image_analysis"]


def _headers(token: str | None) -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["X-Local-Codex-Token"] = token
    return headers


def _request_json(
    method: str,
    url: str,
    *,
    token: str | None = None,
    payload: dict[str, Any] | None = None,
    timeout: int = DEFAULT_HTTP_TIMEOUT_SECONDS,
    attempts: int = DEFAULT_HTTP_RETRIES,
) -> Any:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, headers=_headers(token), method=method)
    last_error: Exception | None = None
    for attempt in range(1, max(1, attempts) + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = response.read().decode("utf-8")
            if not raw.strip():
                return None
            return json.loads(raw)
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code in RETRYABLE_HTTP_STATUS_CODES and attempt < attempts:
                time.sleep(min(4.0, float(attempt)))
                continue
            raise
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            if attempt < attempts:
                time.sleep(min(4.0, float(attempt)))
                continue
            raise
    if last_error is not None:
        raise last_error
    return None


def _claim_next_job(*, api_base: str, token: str | None, worker_id: str, workspace_slug: str) -> dict[str, Any] | None:
    payload = _request_json(
        "POST",
        f"{api_base.rstrip('/')}/claim-next",
        token=token,
        payload={
            "worker_id": worker_id,
            "workspace_slug": workspace_slug,
            "job_kinds": SUPPORTED_JOB_KINDS,
        },
    )
    if not isinstance(payload, dict) or not payload.get("job_available"):
        return None
    return payload


def _complete_job(
    *,
    api_base: str,
    token: str | None,
    job_id: str,
    worker_id: str,
    model: str,
    result_payload: dict[str, Any],
    raw_output: str,
    command_stdout: str,
    command_stderr: str,
    artifacts: list[dict[str, Any]] | None = None,
) -> None:
    payload: dict[str, Any] = {
        "worker_id": worker_id,
        "model": model,
        "result_payload": result_payload,
        "raw_output": raw_output,
        "command_stdout": command_stdout,
        "command_stderr": command_stderr,
        "artifacts": artifacts or [],
    }
    _request_json(
        "POST",
        f"{api_base.rstrip('/')}/{job_id}/complete",
        token=token,
        payload=payload,
        timeout=90,
        attempts=4,
    )


def _fail_job(*, api_base: str, token: str | None, job_id: str, worker_id: str, error_message: str) -> None:
    _request_json(
        "POST",
        f"{api_base.rstrip('/')}/{job_id}/fail",
        token=token,
        payload={"worker_id": worker_id, "error_message": error_message[:4000]},
        timeout=60,
        attempts=4,
    )


def _run_codex_job(
    *,
    workspace_root: Path,
    model: str,
    reasoning_effort: str,
    prompt: str,
    output_schema: dict[str, Any],
    timeout_seconds: int,
) -> tuple[dict[str, Any], str, str, str]:
    with tempfile.TemporaryDirectory(prefix="easyoutfit-codex-job-") as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        schema_path = temp_dir / "schema.json"
        output_path = temp_dir / "output.json"
        schema_path.write_text(json.dumps(output_schema, indent=2), encoding="utf-8")

        command = [
            "codex",
            "exec",
            "-c",
            f'model_reasoning_effort="{reasoning_effort}"',
            "--cd",
            str(workspace_root),
            "--sandbox",
            "read-only",
            "--output-schema",
            str(schema_path),
            "--output-last-message",
            str(output_path),
            "--model",
            model,
            "-",
        ]
        if not (workspace_root / ".git").exists():
            command.insert(-1, "--skip-git-repo-check")

        completed = subprocess.run(
            command,
            input=prompt,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
        if completed.returncode != 0:
            error_excerpt = (stderr or stdout or "no output").strip()
            raise RuntimeError(
                f"codex exec exited with code {completed.returncode}: "
                f"{error_excerpt[-4000:]}"
            )
        if not output_path.exists():
            raise RuntimeError("codex exec completed without writing an output message file")
        raw_output = output_path.read_text(encoding="utf-8").strip()
        parsed = json.loads(raw_output)
        if not isinstance(parsed, dict):
            raise RuntimeError("codex exec did not return a JSON object")
        return parsed, raw_output, stdout[-12000:], stderr[-12000:]


def _build_markdown_artifact(job: dict[str, Any], result_payload: dict[str, Any]) -> dict[str, Any]:
    items = result_payload.get("items") if isinstance(result_payload.get("items"), list) else []
    lines = [
        "# EasyOutfit Codex Audit",
        "",
        f"- Job ID: {job.get('job_id') or ''}",
        f"- Job kind: {job.get('job_kind') or 'wardrobe_metadata_audit'}",
        f"- Workspace: {job.get('workspace_slug') or DEFAULT_WORKSPACE_SLUG}",
        "",
        "## Summary",
        "",
        str(result_payload.get("summary") or "").strip() or "No summary provided.",
        "",
    ]
    global_findings = result_payload.get("global_findings") if isinstance(result_payload.get("global_findings"), list) else []
    if global_findings:
        lines.append("## Global Findings")
        lines.append("")
        for finding in global_findings:
            lines.append(f"- {finding}")
        lines.append("")
    if items:
        lines.append("## Item Reviews")
        lines.append("")
        for item in items:
            item_id = str(item.get("item_id") or "unknown")
            status = str(item.get("status") or "unknown")
            rationale = str(item.get("rationale") or "").strip()
            issues = item.get("issues") if isinstance(item.get("issues"), list) else []
            lines.append(f"### {item_id}")
            lines.append("")
            lines.append(f"- Status: {status}")
            if issues:
                lines.append(f"- Issues: {', '.join(str(issue) for issue in issues)}")
            if rationale:
                lines.append(f"- Rationale: {rationale}")
            lines.append("")
    next_actions = result_payload.get("next_actions") if isinstance(result_payload.get("next_actions"), list) else []
    if next_actions:
        lines.append("## Next Actions")
        lines.append("")
        for action in next_actions:
            lines.append(f"- {action}")
        lines.append("")
    return {
        "kind": "report_markdown",
        "label": "Wardrobe Metadata Audit Report",
        "filename": "wardrobe-metadata-audit.md",
        "mime_type": "text/markdown",
        "content": "\n".join(lines).strip(),
    }


def _build_json_artifact(result_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": "result_json",
        "label": "Structured Codex Result",
        "filename": "wardrobe-metadata-audit.json",
        "mime_type": "application/json",
        "content": json.dumps(result_payload, indent=2, ensure_ascii=True),
    }


def _workspace_temp_dir(workspace_root: Path) -> Path:
    temp_root = workspace_root / ".codex-job-tmp"
    temp_root.mkdir(parents=True, exist_ok=True)
    return temp_root


def _guess_suffix_from_url(image_url: str) -> str:
    parsed = urlparse(image_url)
    extension = Path(parsed.path).suffix.strip()
    if extension:
        return extension
    return ".jpg"


def _stage_image_for_codex(*, workspace_root: Path, image_url: str) -> tuple[Path, tempfile.TemporaryDirectory[str]]:
    temp_dir = tempfile.TemporaryDirectory(
        prefix="upload-analysis-",
        dir=str(_workspace_temp_dir(workspace_root)),
    )
    temp_path = Path(temp_dir.name)

    if image_url.startswith("data:"):
        header, encoded = image_url.split(",", 1)
        mime_type = header.split(";")[0].replace("data:", "").strip()
        suffix = mimetypes.guess_extension(mime_type) or ".jpg"
        image_path = temp_path / f"upload{suffix}"
        image_path.write_bytes(base64.b64decode(encoded))
        return image_path, temp_dir

    suffix = _guess_suffix_from_url(image_url)
    image_path = temp_path / f"upload{suffix}"
    request = urllib.request.Request(image_url, headers={"User-Agent": "easyoutfit-codex-bridge/1.0"})
    with urllib.request.urlopen(request, timeout=DEFAULT_HTTP_TIMEOUT_SECONDS) as response:
        image_path.write_bytes(response.read())
    return image_path, temp_dir


def _build_upload_image_prompt(*, image_path: Path, source_name: str | None, source_url: str | None) -> str:
    relative_path = image_path.as_posix()
    source_name_line = f"Source filename: {source_name}\n" if source_name else ""
    source_url_line = f"Source URL: {source_url}\n" if source_url else ""
    return (
        "You are analyzing a single clothing item image for EasyOutfit.\n"
        "Inspect the local image file and return JSON that matches the provided schema exactly.\n"
        "Be conservative and precise. Do not invent garments, colors, or brands that are not visible.\n"
        "Use normalized lowercase values for style, season, occasion, and mood arrays.\n"
        "If a field is unclear, use 'unknown' or an empty string rather than guessing.\n\n"
        f"{source_name_line}"
        f"{source_url_line}"
        f"Local image path: {relative_path}\n"
    )


def _run_upload_image_analysis_job(
    *,
    workspace_root: Path,
    model: str,
    reasoning_effort: str,
    timeout_seconds: int,
    context_packet: dict[str, Any],
) -> tuple[dict[str, Any], str, str, str]:
    image_url = str(context_packet.get("image_url") or "").strip()
    if not image_url:
        raise RuntimeError("Upload image analysis job missing image_url")
    output_schema = context_packet.get("output_schema") if isinstance(context_packet.get("output_schema"), dict) else None
    if not output_schema:
        raise RuntimeError("Upload image analysis job missing output_schema")

    source_name = str(context_packet.get("file_name") or context_packet.get("source_name") or "").strip() or None
    source_url = image_url
    image_path, temp_dir = _stage_image_for_codex(workspace_root=workspace_root, image_url=image_url)
    try:
        prompt = _build_upload_image_prompt(
            image_path=image_path.relative_to(workspace_root),
            source_name=source_name,
            source_url=source_url,
        )
        return _run_codex_job(
            workspace_root=workspace_root,
            model=model,
            reasoning_effort=reasoning_effort,
            prompt=prompt,
            output_schema=output_schema,
            timeout_seconds=timeout_seconds,
        )
    finally:
        temp_dir.cleanup()


def run_once(
    *,
    api_base: str,
    token: str | None,
    worker_id: str,
    workspace_slug: str,
    workspace_root: Path,
    model: str,
    reasoning_effort: str,
    timeout_seconds: int,
) -> bool:
    job = _claim_next_job(api_base=api_base, token=token, worker_id=worker_id, workspace_slug=workspace_slug)
    if not job:
        return False

    job_id = str(job.get("job_id") or "")
    job_kind = str(job.get("job_kind") or "")
    context_packet = job.get("context_packet") if isinstance(job.get("context_packet"), dict) else {}
    prompt = str(context_packet.get("prompt") or "").strip()
    output_schema = context_packet.get("output_schema") if isinstance(context_packet.get("output_schema"), dict) else None

    if not job_id:
        return True

    try:
        if job_kind == "upload_image_analysis":
            result_payload, raw_output, stdout, stderr = _run_upload_image_analysis_job(
                workspace_root=workspace_root,
                model=model,
                reasoning_effort=reasoning_effort,
                timeout_seconds=timeout_seconds,
                context_packet=context_packet,
            )
        else:
            if not prompt or not output_schema:
                _fail_job(
                    api_base=api_base,
                    token=token,
                    job_id=job_id,
                    worker_id=worker_id,
                    error_message="Job context missing prompt or output schema",
                )
                return True
            result_payload, raw_output, stdout, stderr = _run_codex_job(
                workspace_root=workspace_root,
                model=model,
                reasoning_effort=reasoning_effort,
                prompt=prompt,
                output_schema=output_schema,
                timeout_seconds=timeout_seconds,
            )
        artifacts = [_build_json_artifact(result_payload)]
        if job_kind == "wardrobe_metadata_audit":
            artifacts.append(_build_markdown_artifact(job, result_payload))
        _complete_job(
            api_base=api_base,
            token=token,
            job_id=job_id,
            worker_id=worker_id,
            model=model,
            result_payload=result_payload,
            raw_output=raw_output,
            command_stdout=stdout,
            command_stderr=stderr,
            artifacts=artifacts,
        )
        return True
    except Exception as exc:
        _fail_job(
            api_base=api_base,
            token=token,
            job_id=job_id,
            worker_id=worker_id,
            error_message=str(exc),
        )
        return True


def run_loop(
    *,
    api_base: str,
    token: str | None,
    worker_id: str,
    workspace_slug: str,
    workspace_root: Path,
    model: str,
    reasoning_effort: str,
    timeout_seconds: int,
    poll_seconds: float,
) -> None:
    backoff_seconds = DEFAULT_ERROR_BACKOFF_SECONDS
    while True:
        try:
            claimed = run_once(
                api_base=api_base,
                token=token,
                worker_id=worker_id,
                workspace_slug=workspace_slug,
                workspace_root=workspace_root,
                model=model,
                reasoning_effort=reasoning_effort,
                timeout_seconds=timeout_seconds,
            )
            backoff_seconds = DEFAULT_ERROR_BACKOFF_SECONDS
            time.sleep(poll_seconds if not claimed else 1.0)
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            print(f"[easyoutfit-codex-bridge] loop error: {exc}", file=sys.stderr, flush=True)
            time.sleep(backoff_seconds)
            backoff_seconds = min(backoff_seconds * 1.5, DEFAULT_MAX_ERROR_BACKOFF_SECONDS)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the EasyOutfit local Codex bridge.")
    parser.add_argument("--api-base", default=DEFAULT_API_BASE)
    parser.add_argument("--token", default=os.getenv("EASYOUTFIT_LOCAL_CODEX_TOKEN"))
    parser.add_argument("--workspace-root", default=DEFAULT_WORKSPACE_ROOT)
    parser.add_argument("--workspace-slug", default=DEFAULT_WORKSPACE_SLUG)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--reasoning-effort", default=DEFAULT_REASONING_EFFORT)
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--poll-seconds", type=float, default=DEFAULT_POLL_SECONDS)
    parser.add_argument("--worker-id", default=f"{socket.gethostname()}-easyoutfit-codex")
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    workspace_root = Path(args.workspace_root).expanduser()
    if not workspace_root.exists():
        print(f"workspace root does not exist: {workspace_root}", file=sys.stderr)
        return 1

    if args.once:
        claimed = run_once(
            api_base=args.api_base,
            token=args.token,
            worker_id=args.worker_id,
            workspace_slug=args.workspace_slug,
            workspace_root=workspace_root,
            model=args.model,
            reasoning_effort=args.reasoning_effort,
            timeout_seconds=args.timeout_seconds,
        )
        return 0 if claimed else 2

    run_loop(
        api_base=args.api_base,
        token=args.token,
        worker_id=args.worker_id,
        workspace_slug=args.workspace_slug,
        workspace_root=workspace_root,
        model=args.model,
        reasoning_effort=args.reasoning_effort,
        timeout_seconds=args.timeout_seconds,
        poll_seconds=args.poll_seconds,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
