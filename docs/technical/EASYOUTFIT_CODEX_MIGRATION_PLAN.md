# EasyOutfit Codex Migration Plan

## Goal

Move EasyOutfit toward the `aiclone` Codex-runner architecture without breaking the production paths that currently depend on direct OpenAI API calls.

This is a hybrid migration, not a full replacement.

## Current Reality

EasyOutfit currently uses `OPENAI_API_KEY` in three different ways:

1. **Synchronous image analysis during upload**
   - Frontend entry: `frontend/src/lib/services/clothingImageAnalysis.ts`
   - Frontend proxy: `frontend/src/app/api/analyze-image/route.ts`
   - Backend route: `backend/src/routes/image_analysis.py`
   - Main inference service: `backend/src/services/openai_service.py`
   - Current behavior: upload request waits for a GPT-4o vision response and returns structured clothing metadata immediately.

2. **Asynchronous flat-lay generation and enhancement**
   - Worker entry: `backend/worker/main.py`
   - Current behavior: Railway worker composes a flat lay, then optionally enhances it with `gpt-image-1` via `/v1/images/edits`.

3. **Embeddings / RAG-style utilities**
   - `backend/src/routes/knowledge.py`
   - `backend/src/routes/rag_ingest.py`
   - `backend/src/services/embedding_service.py`
   - Current behavior: direct embedding calls against OpenAI.

Separate note:
- `backend/mcp_http_gateway.py` and the `closetgptrenewopenaisdk` service are for OpenAI Apps SDK / OAuth gateway concerns.
- That service is not the same thing as the inference path behind `OPENAI_API_KEY`.

## What `aiclone` Actually Provides

The `aiclone` repo uses two distinct patterns:

1. **Provider router**
   - Example: `backend/app/routes/content_generation.py`
   - Purpose: choose among `openai`, `codex`, `gemini`, `ollama`
   - Shape: still a normal request/response path

2. **Local Codex runner queue**
   - Queue routes: `backend/app/routes/content_generation.py`
   - Job store: `backend/app/services/local_codex_generation_service.py`
   - Local worker bridge: `scripts/local_codex_bridge.py`
   - Runner execution: `scripts/runners/run_codex_workspace_execution.py`
   - Shape: enqueue -> local machine claims -> `codex exec` runs -> result posts back

The second pattern is the real Codex-runner architecture. It is text-first, queue-based, and local-machine bound.

## Migration Principle

Do **not** force EasyOutfit's current image-analysis and image-editing production paths through the local Codex runner first.

Reasons:
- upload analysis is synchronous and user-facing
- the current local runner depends on a machine being online
- current queue contracts are text-oriented, not image-oriented
- flat-lay enhancement currently produces binary image artifacts, not just text JSON

So the first move is:
- centralize AI boundaries
- separate workloads by runtime shape
- only migrate the Codex-compatible workloads first

## Target Architecture

Introduce one EasyOutfit AI runtime layer under:

`backend/src/services/ai_runtime/`

Suggested modules:

- `backend/src/services/ai_runtime/__init__.py`
- `backend/src/services/ai_runtime/runtime_config.py`
- `backend/src/services/ai_runtime/vision_runtime.py`
- `backend/src/services/ai_runtime/image_edit_runtime.py`
- `backend/src/services/ai_runtime/embedding_runtime.py`
- `backend/src/services/ai_runtime/codex_jobs.py`
- `backend/src/services/ai_runtime/codex_bridge_client.py`

Responsibilities:

- `vision_runtime.py`
  - single home for clothing-image analysis
  - replaces direct `OpenAI(...)` construction in request handlers/services

- `image_edit_runtime.py`
  - single home for flat-lay enhancement and any future image-edit calls
  - keeps binary/image concerns isolated from text inference concerns

- `embedding_runtime.py`
  - single home for embeddings
  - allows later provider swaps without touching routes

- `codex_jobs.py`
  - EasyOutfit-local queue abstraction
  - modeled after `aiclone` local codex jobs
  - should be used only for batch/operator/background reasoning tasks at first

- `codex_bridge_client.py`
  - optional helper for queue creation / polling if routes or workers need it

## Workload Classification

### Keep direct API for now

These should stay off the local Codex runner in phase 1:

- clothing image analysis in `backend/src/services/openai_service.py`
- sync upload analysis routed through `backend/src/routes/image_analysis.py`
- flat-lay enhancement in `backend/worker/main.py`
- embeddings in `knowledge.py` / `rag_ingest.py`

They can still move behind the new runtime layer, but should keep direct provider execution initially.

### Good first Codex-runner candidates

These are better fits for the `aiclone` queue model:

- batch wardrobe metadata audit
- operator review of low-confidence clothing analyses
- explanation generation for why an outfit failed validation
- batch re-analysis planning after schema changes
- support/admin summaries for “why did this item/outfit fail?”
- recommendation-quality reports that inspect saved metadata and output a structured remediation plan

### Possible later Codex-runner candidates

Only after the queue path is proven stable:

- optional offline metadata enrichment pass for already-uploaded items
- operator-triggered “repair these 50 items” jobs
- internal curation jobs for style tags, occasion tags, or validation notes

## Phase Plan

## Phase 1: Centralize AI Boundaries

Goal:
- no product behavior change
- remove scattered direct OpenAI usage from routes/services

Changes:
- move clothing vision logic from `backend/src/services/openai_service.py` behind `vision_runtime.py`
- move worker image-edit logic from `backend/worker/main.py` helper blocks behind `image_edit_runtime.py`
- move embedding calls from `knowledge.py`, `rag_ingest.py`, and `embedding_service.py` behind `embedding_runtime.py`

Success criteria:
- one place to swap providers for each AI workload type
- request handlers no longer instantiate OpenAI clients directly

## Phase 2: Port the EasyOutfit Local Codex Queue

Goal:
- add the `aiclone` queue pattern to EasyOutfit without changing the main user flows

Implementation status:
- initial Firestore-backed queue service now lives in `backend/src/services/ai_runtime/codex_jobs.py`
- API surface now lives in `backend/src/routes/codex_jobs.py`
- local bridge runner now lives in `scripts/local_codex_bridge_easyoutfit.py`
- the first supported job kind is `wardrobe_metadata_audit`

Suggested files:
- `backend/src/routes/codex_jobs.py`
- `backend/src/services/ai_runtime/codex_jobs.py`
- `scripts/local_codex_bridge_easyoutfit.py`
- `scripts/run_local_codex_bridge_easyoutfit.sh`
- optional: `docs/technical/EASYOUTFIT_LOCAL_CODEX_BRIDGE.md`

Recommended API surface:

- `POST /api/codex-jobs`
- `POST /api/codex-jobs/claim-next`
- `GET /api/codex-jobs/{job_id}`
- `GET /api/codex-jobs/{job_id}/artifacts`
- `POST /api/codex-jobs/{job_id}/complete`
- `POST /api/codex-jobs/{job_id}/fail`
- `POST /api/codex-jobs/{job_id}/cancel`

Initial storage can be simple:
- JSON file job store, modeled after `aiclone`
- or Postgres only if EasyOutfit already has a natural durable store for it

Recommendation:
- start with file-backed or Firestore-backed job state for speed
- do not introduce a new database dependency just for the first iteration

## Phase 3: Add First Safe Job Types

Recommended initial job kinds:

1. `wardrobe_metadata_audit`
   - input: list of wardrobe item IDs and metadata
   - output: structured review notes, inconsistencies, recommended corrections

2. `outfit_failure_summary`
   - input: outfit payload, validation errors, weather, occasion, user profile snapshot
   - output: concise failure explanation plus remediation suggestions

3. `batch_item_reanalysis_review`
   - input: saved analysis payloads from existing wardrobe items
   - output: priority list of items that should be re-run through the vision path

4. `support_case_summary`
   - input: failed request logs, user-visible error, relevant metadata
   - output: operator-readable diagnosis

All of these are:
- async
- tolerant of queue latency
- not required for core user interaction
- text/JSON oriented

## Phase 4: Decide Whether to Migrate Any Production Async Path

Only after the queue path has proven reliable should EasyOutfit consider a deeper move.

Possible candidate:
- operator-triggered batch metadata repair job

Not recommended as the first queue migration:
- upload-time image analysis
- the only flat-lay enhancement path in production

## Environment Variables

Keep current variables:

- `OPENAI_API_KEY`
- Firebase variables

Add EasyOutfit-local Codex variables:

- `ENABLE_LOCAL_CODEX_JOBS=false`
- `LOCAL_CODEX_BRIDGE_TOKEN=...`
- `LOCAL_CODEX_JOB_STORE_DIR=/absolute/path`
- `LOCAL_CODEX_BRIDGE_MODEL=gpt-5.4-mini`
- `LOCAL_CODEX_BRIDGE_REASONING_EFFORT=medium`
- `LOCAL_CODEX_BRIDGE_TIMEOUT_SECONDS=420`
- `LOCAL_CODEX_BRIDGE_POLL_SECONDS=4`
- `LOCAL_CODEX_WORKSPACE_SLUG=easyoutfitapp`
- `LOCAL_CODEX_BRIDGE_WORKSPACE_ROOT=/Users/neo/Desktop/closetgptrenew`

Optional future provider abstraction variables:

- `EASYOUTFIT_VISION_PROVIDER=openai`
- `EASYOUTFIT_IMAGE_EDIT_PROVIDER=openai`
- `EASYOUTFIT_EMBEDDING_PROVIDER=openai`

## File-by-File Rollout Order

1. Create the runtime layer:
- `backend/src/services/ai_runtime/runtime_config.py`
- `backend/src/services/ai_runtime/vision_runtime.py`
- `backend/src/services/ai_runtime/image_edit_runtime.py`
- `backend/src/services/ai_runtime/embedding_runtime.py`

2. Rewire current callers:
- `backend/src/services/openai_service.py`
- `backend/src/routes/image_analysis.py`
- `backend/worker/main.py`
- `backend/src/routes/knowledge.py`
- `backend/src/routes/rag_ingest.py`
- `backend/src/services/embedding_service.py`

3. Add Codex queue support:
- `backend/src/services/ai_runtime/codex_jobs.py`
- `backend/src/routes/codex_jobs.py`
- backend app/router registration

4. Add local bridge tooling:
- `scripts/local_codex_bridge_easyoutfit.py`
- `scripts/run_local_codex_bridge_easyoutfit.sh`

5. Add first operator-only job creator:
- likely a new admin/internal route or script for `wardrobe_metadata_audit`

## Non-Goals

This migration should **not** do these things initially:

- replace all OpenAI calls with local Codex jobs
- make production uploads depend on a local laptop
- route binary image workflows through the current text-first job contract
- mix the Apps SDK gateway service with the inference/runtime migration

## Recommended First Implementation

If only one step is taken now, it should be:

**Build Phase 1 only.**

That gives EasyOutfit:
- one AI runtime boundary
- cleaner provider swaps later
- a safe base to port the `aiclone` queue model afterward

If two steps are taken:

1. build Phase 1
2. add one operator-only Codex job type in Phase 3

That is the lowest-risk path that still makes EasyOutfit meaningfully more like `aiclone`.
