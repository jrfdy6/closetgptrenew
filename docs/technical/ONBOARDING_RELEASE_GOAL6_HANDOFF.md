# Goal 6 — integrated onboarding release

Status: controlled rollout of accepted source
`801b6679062e0ad1df6c0f5e085ddeac5c4d8724` is **partially live**. Protected
Firestore rules and the matching Railway API are deployed and verified. Worker
repair `f371ff43` has **passed bounded production compatibility**: three natural
garment jobs completed with valid persisted original/derived contracts, then
the worker was stopped as agreed. Authenticated paused flatlay admission returned
503 with no new reservation and unchanged credit. Frontend production, configured
recommendation fidelity, full signed-in workflows, provider-image/settlement and
physical-device gates remain open.

## Candidate and scope

Branch `codex/onboarding-integrated-release` preserves all five accepted commits:

| Goal | Accepted commit |
| --- | --- |
| Durable onboarding state | `bf16ab125e7b7b51ae62e4cc3fdc7cfe1eb49f8f` |
| Image worker durability | `d8bbaccd22a9aa2636acba06da253551d8a6879a` |
| Capsule onboarding experience | `e47733446e32147d51dfb66a49ab0cbee5cd940e` |
| Recommendation fidelity | `fd148750a91cf226249a47f6b0a949562267bd31` |
| Saved outfit experience | `b0f7dfb3d5a56c5aa3ff43f7c24b52735d90f768` |

The full quiz, ten unique usable garments and category coverage, incremental
saves/resume, explicit flatlay creation, original photographs, existing hosted
providers and credit settlement remain intact. Stripe/prices, mixed PR #3,
Jev, new models, imports/reminders and a new multiple-required-item selector
remain excluded. Do not reset credits, delete historical outfits or transfer
the owner's photographs to the test account.

## Privileged boundary migration

The candidate moves profile, onboarding, quiz, garment and image privileged work
to Railway. Vercel contains thin fixed-origin proxies and the browser Firebase
client, with no Firebase Admin package/runtime or service-account credentials.
Do not provision Vercel Admin keys to make the release work. The canonical
operator playbook was updated first; the production architecture describes the
same candidate boundary.

Migrated Railway endpoints verify bearer tokens with revocation checks, deny
disabled/anonymous users and mismatched UID assertions in headers/query/body,
and preserve account authority, private job state and quiz/wear receipts.
The active direct `/api/auth/profile` GET/PUT clients use the same protected
profile contract. Profile transactions execute outside the request event loop.
Fresh profile edits cannot establish quiz completion through `stylePreferences`
or `preferences.style`: the transaction permits these edits only with completion
or legacy evidence in the stored profile before applying the update. Name-only
signup and completed/legacy profile edits remain supported.

Proxy destinations come from trusted configuration and fixed application paths,
not request headers or URLs. Proxies forward bearer authorization and required
body/content type, reject redirects and non-JSON responses, and return private,
no-store JSON. The default upstream request deadline is 50 seconds. Multipart
`/api/image/upload` preserves file/field semantics with a 45-second upstream
deadline. Timeouts can leave writes committed; confirm by retry/readback.

Unused frontend endpoints return `410`: `/api/profile/save`,
`/api/user/style-profile`, `/api/update-style-profile`, `/api/upload-photo`,
`/api/delete-photo`, `/api/migrate`, `/api/image/upload-direct`, `/api/analyze`
and `/api/admin/fix-onboarding-status`. Active callers use supported paths;
retirement does not authorize restoring permissive identity or migration scans.

Raw image-URL admission retains its previous policy. The worker checks
`original_source` at use time; no new general URL-admission or external-fetch
safety guarantee is claimed by this migration.

## Narrow integrated fix

The worker's oldest-only flatlay query could repeatedly launch an unclaimable
private ledger and starve later valid requests. The selector now advances using
a Firestore document snapshot, reads at most one candidate per idle dispatch,
and wraps after exhausting the queue. The transaction remains the sole claim
authority. Held ledgers and credits are not modified to force progress.

Regressions cover tied queue times, thirty held rows before a valid row,
deleted/dequeued cursor records, an earlier arrival, wraparound, and an actual
declined ledger claim followed by a valid claim. The coordinator/process suites
retain their standard-library-only CI contract.

## Verification before cloud changes

These checks cover the integrated migration, including the profile completion
guard and exact onboarding parity fixes. Source freeze, independent acceptance
and Linux CI remain distinct release gates.

| Check | Latest recorded result | Release follow-up |
| --- | --- | --- |
| Full frontend | 720 tests in 57 suites passed | Includes runtime Admin-boundary guards |
| Full backend | 534 tests: 533 passed, one macOS-specific skip | Includes completion-guard, transaction and route-registration regressions |
| Executed TypeScript parity oracles | 189 quiz cases and 241 onboarding cases match | Frozen-source mapping, submission hashes, state, classification and timestamp behavior |
| Coordinator/process standard-library-only run | 29 tests: 28 passed, one macOS-specific skip | Linux CI on the final candidate remains required |
| Firestore rules emulator | 263 checks passed against the exact source hash below | Recheck if rules change |
| Parent independent real local Firestore emulator service checks | Frozen-source 25/25 passed, including completion guards and concurrent drafts | Transaction contention can return retryable exhaustion; retries converge without a dual winner |
| Production build | Passed with public Firebase client configuration and no server Firebase credentials | All 134 compiled server-route traces exclude Firebase Admin |
| Typecheck | 115 existing diagnostics; baseline 124 at `3ed2ecc4`; zero new diagnostic positions or changed-file errors | Repository-wide typecheck remains failing; the existing build skips type/lint gates |
| Accepted source and CI | `801b6679062e0ad1df6c0f5e085ddeac5c4d8724`; Linux runs `35798351924` and `35798348416` passed | A subsequent diagnostic candidate needs separate acceptance |
| Authenticated deployed/provider-image/physical-device checks | **Pending** | Local and viewport tests do not replace these gates |

The parent independently verified all 14 canonical public-health/private-debug
checks before release on September 22, 2026, and read-only verification confirmed
all three canonical backend URL environment variables. Reading the Firebase
Rules release and source succeeded. Synthetic `projects.test` was denied to the
current service account (HTTP 403); no IAM change, alternate credential, rules
deployment or app-document operation was used to bypass it. Current signed-in
operator Firebase-console sign-in has since been verified read-only; actual
publication and source-hash proof are now recorded below. Full deployed client
workflow evidence remains a release gate.

The rules emulator checks cover owner/foreign/anonymous policy, server-owned
profile authority, private job/receipt collections, managed wear immutability
and legacy behavior. They are local evidence, distinct from the independent
service-level emulator checks and from authenticated deployed-rule evidence.

## Observed controlled rollout — September 22–23, 2026

- Rules: `projects/closetgptrenew/rulesets/7bcef845-f06e-4825-af58-b248f21164a3`,
  published `2026-09-22T23:48:31.140678Z`. Official REST source SHA matches the
  accepted `eafa27b…f9811ca` exactly. Five console rules simulations passed;
  these are synthetic checks, not actual app-document writes.
- API: deployment `12c21fda-3559-48f3-a07c-102089bff6e3`, accepted source `801b6679`,
  one running instance `2798efdd-46dc-439b-94ad-eb0ae8e29501`. All 16 health and
  missing-bearer/private-route checks passed. A signed-in profile name save and
  reload passed, and the original name was restored. This tested the live
  compatibility path, not the new preview proxy. Two same-day bodyless Wear UI
  submissions left the exact outfit and all three garments at wear count one;
  readback found one matching managed history, one day receipt and one retry-key
  receipt (12/12 checks). This closes the API-first legacy wear compatibility gate,
  not the new-preview proxy or provider-image gates.
- Worker: deployment `777045cd-8f01-4f64-ab2f-bf2a18e75362`, same accepted source,
  one instance `09cf0f47-3e0f-465c-bb43-232c959b27ca`, started its coordinator at
  `00:03:32 UTC`. Claims and finite automatic retries progressed, but no successful
  garment completion was observed. Eight observed failed attempts took 48–91
  seconds and recorded `processing_failed`; all four inspected jobs had protected
  originals. No model/network/inference root cause is inferred from that coarse
  code. Official `railway down` exited successfully; by `00:14:21 UTC` the worker
  had no active instances, and its exact deployment was `REMOVED`. Logs recorded
  the container stop signal at `00:14:11 UTC` and `Worker stopped` at `00:14:14 UTC`.
  OS-level child reaping is not independently proven by these observations.
- The historical expired Neo flatlay request settled through normal worker
  expiry as `legacy_request_needs_review`; its reserved credit was refunded once
  (remaining credits 0 to 1, unchanged refill period). No manual credit write,
  request retry or provider image call was performed. No provider-start field
  was present; that does not prove historical provider billing.
- Vercel preview `dpl_2gsS5zGiCygBJWY1wvjwWHYQndy2` is ready at accepted `801b6679`.
  Authenticated preview checks remain pending. Production still uses
  `dpl_6jcTmawjEhem86s3ZtaKbMmNsLYn`; no frontend promotion has occurred.

The API admission variable was originally present with value `false` and is now
configured `true` on the running accepted API. Restore that exact prior state
only at the deliberate readiness gate. Before `main` is integrated, use
`--skip-deploys` for the variable change, followed by explicit reviewed-commit
deployment: a normal variable update can automatically rebuild the older linked
`main`. Runtime SSH flag inspection was unavailable because no SSH keys were
configured; none were created. Authenticated paused-handler proof is recorded
below under the completed U2NET runtime check.

The failed initial CLI-upload API candidate did not replace the running API:
its monorepo archive omitted required files. The official `serviceInstanceDeploy`
API with explicit `commitSha` and `latestCommit: false` successfully deployed the
accepted Git source. Use this controlled path rather than unverified archives.

## Worker diagnostic run and remaining evidence gap

Accepted diagnostic source `4581d43cae2b9cff726cd1219dd8b681bf1b36ff` was deployed
for one bounded worker-only run after independent review and two successful Linux
CI runs (`35801948799`, `35801945634`). API source, rules and admission pause were
unchanged.

The contained failure needs more precise evidence than the public
`processing_failed` code. The narrow candidate forwards at most two finite
stage/category entries from the alpha and fallback inference processes through
the existing result manifests to coordinator operational logs. An optional HTTP
error status is constrained to integer 400–599. Every receiving boundary reapplies
the allowlist. No exception messages, URLs, object IDs, credentials, traceback
contents or frame locals are serialized. Diagnostics do not enter garment/job
lifecycle records or user-facing errors.

Diagnostic extraction and inference sidecar persistence are best effort. A broken
exception property or optional diagnostic file cannot turn successful inference
into a failure or obscure the original safe failure envelope. Existing models,
providers, leases, deadlines, automatic attempt budgets and public statuses are
unchanged. This candidate diagnoses the blocker; it does not claim to fix the
underlying image-preparation failure.

The focused diagnostic/process suites ran 55 tests: 54 passed and one expected
macOS skip. The full backend ran 542 tests: 541 passed and one expected macOS skip.
Independent review resolved the diagnostic-accessor fault and found no remaining
blocking issue. Real nested subprocess tests verify both inference causes cross
the manifest boundaries while original preservation and retry behavior remain
unchanged. Frontend, rules and API source are unchanged from accepted `801b6679`.
Deployment `00ccfc8d-2ac4-42c3-84a3-df69d5b8b810` ran one instance
`c04fd293-198e-45e4-9c09-6d5b84f5874a`. A naturally eligible second attempt began
at `00:29:20 UTC` and failed at `00:30:41 UTC` with both `alpha_process` and
`fallback_process` classified `process_crashed`. No Python failure manifest was
returned. That category included any nonzero integer exit and did not establish
a signal, native failure or OOM cause.

The coordinator started the next naturally eligible garment in the same tick
before the observer stopped the service. `Worker stopped` was recorded at
`00:30:50 UTC`; the stop command exited zero and no active instances remained.
The second job had no terminal event before shutdown; its existing durable lease
was retained for normal recovery. No manual garment or paid-request retry occurred.

Official 60-second metrics for this run sampled 0.306–1.861 GB memory against an
8 GB limit, and CPU up to 1.117 against an 8 limit. Sparse samples are not peak
measurements or OOM counters; they do not justify changing resources, models or
deadlines. The exact diagnostic build resolved rembg 2.0.85, onnxruntime 1.30.0,
NumPy 2.5.3, PyMatting 1.1.16, Pillow 12.3.0, SciPy 1.18.1 and scikit-image 0.26.0.
The selected native wheels target CPython 3.12 on Linux x86_64; this records the
active Nixpacks build, not the inactive worker Dockerfile or API dependency pins.
Next evidence is finite exit/signal classification from the supervisor,
best-effort last-stage markers, and optional bounded cgroup-v2 `oom`/`oom_kill`
counter deltas. Only a fixed, capped file read and two nonnegative integer deltas
are permitted; unavailable/malformed/reset counters are omitted. The deltas
describe container-level events during inference, not proof that this child was
killed by OOM. Any further worker run requires a fresh source/test review; keep
API admission paused.

## Exit/stage/cgroup diagnostic run

The follow-up candidate changes only worker diagnostic extraction and its tests.
It classifies the supervisor's retained return code into finite signal/nonzero
exit categories; exit 74 is a neutral category, not proof the registration barrier
caused the production failure. Best-effort progress markers identify the last
inference import/input/removal/output stage. The outer supervisor, coordinator,
lifecycle, model/provider settings, resources, retry budgets and deadlines remain
unchanged. Missing marker or counter evidence stays unknown rather than being
invented. Counter evidence is projected through the same finite schema before
operational logging and never enters user/job records.

Focused checks ran 64 tests: 63 passed and one expected macOS skip. Standard-library
checks ran 33: 32 passed and one expected macOS skip. Full backend checks ran 551:
550 passed and one expected macOS skip. Regressions include actual SIGKILL, exit 1,
the real missing-registration-barrier exit 74, native exits through the production
`--infer` path, malformed codes, optional marker-write failures and bounded cgroup
read/reset/overflow behavior. Generic tests isolate host cgroup availability.
The reviewed full commit is `763220d87aabb3db6f5601f4dd2241f28bcaf010`.
Both Linux CI runs `35803352368` and
`35803349677` passed before independent acceptance of one bounded worker run.

Deployment `1991b798-cb02-46cc-9acd-45f4028de4df`, instance
`c5870f80-3a46-4b82-a342-d0b0c87eac3b`, started a naturally eligible third
garment attempt at `00:47:34 UTC`. The attempt failed at `00:50:25 UTC` with
both `alpha_removal` and `fallback_removal` classified `process_sigkill`.
Each interval recorded `container_oom_delta: 0` and
`container_oom_kill_delta: 1`. This is strong OOM-associated removal evidence;
cgroup-wide counters do not identify the exact killed PID or prove the configured
8 GB memory limit was reached. Official 60-second samples peaked at 4.740 GB;
they are sparse samples, not an observed peak-RSS measurement.

The coordinator started another naturally eligible third attempt in the same
tick as the first outcome. No terminal outcome was observed for that second
start before shutdown; preserve its existing lease for normal recovery.
`Worker stopped` was logged at `00:50:33.438 UTC`, the platform stop marker at
`00:50:34.479 UTC`, and official stop completion at `00:50:35 UTC` returned zero
with no active instances. No manual retry, credit reset or provider call was
used to create evidence. API admission remains paused. Another worker deployment
requires a separately reviewed repair candidate and explicit runtime gate.

## Explicit historical model compatibility repair — local candidate

Commit `0751cbbc19ff79d56350ea876edc9c26ffd913cc` changed worker rembg from
`2.0.50` to `>=2.0.67` for Python 3.12 compatibility. Both inspected historical
versions selected U2NET for a sessionless `remove` call. The actual diagnostic
build resolved rembg 2.0.85, which now selects BRIA for that same call. This is
dependency-default drift relative to source intent; no claim is made that every
historic production deployment's package/model was measured.

Official PyPI wheel SHA-256 values were verified independently:

- rembg 2.0.67: `365236b7521a1a0ffc86315de80ab7005cd9705cd02feebfaaec39fb21feb45a`.
- rembg 2.0.85: `9642672c3e879d576d0270ccfeada3d1c75585b9c78a7970d53a5c6874c0c1f2`.

The candidate pins only worker `rembg==2.0.85`, calls `new_session('u2net')`
inside each existing inference child and passes that exact session to `remove`
in both modes. Initialization stays within the existing process deadline and
failure/fallback contract. Finite session-stage diagnostics distinguish loading
from removal without serializing exception messages or model URLs. The U2NET
prediction and normalization functions are identical across the inspected
2.0.67 and 2.0.85 source artifacts, using 320×320 model input and the same
canonical weight URL/checksum. This restores model selection without downgrading
unrelated library behavior. It does not claim a measured memory improvement yet.

Keep input/reference bounds, alpha settings, `OMP_NUM_THREADS` behavior,
240/60/360-second deadlines, independent child processes, attempt budgets,
credits, original publication and usable-garment readiness unchanged. A garment
remains usable with its saved original and recognized/corrected category;
background removal must not become an onboarding requirement. No hosted flatlay
provider/model or cloud resources are changed by this repair.

Local validation uses only the ten approved public `upload-batch` photographs.
Their copies in the temporary capsule folder were verified byte-identical.
The Mac uses Python 3.12 on x86_64; official PyPI has no compatible wheel for
the deployed ONNX Runtime 1.30.0. The isolated local environment uses ONNX
1.23.2 and NumPy 2.3.5 with Numba 0.62.1 because compatible Mac Numba requires
NumPy below 2.4. Production dependency declarations are not downgraded. Other
recorded image-library versions match the diagnostic build. These local checks
cannot prove the Linux production memory limit or OOM behavior.

The canonical U2NET download is 175,997,641 bytes and matches upstream MD5
`60024c5c889badc19c04ad937298a77b`; its recorded SHA-256 is
`8d10d2f3bb75ae3b6d527c77944fc5e7dcd94b29809d47a739a7a728a912b491`.
Focused job/projection/coordinator tests passed 53/53; standard-library process
checks passed 32 with one expected platform skip. The full backend ran 557 tests:
556 passed and one expected macOS skip. Independent code review found no blocking
finding. Exact-source Linux CI and the bounded production result are recorded
below; further dispatch and the overall release remain separately gated.

The actual `process_garment` → isolated subprocess → production `--infer`
pipeline completed all ten approved public photographs using U2NET and the
existing alpha settings. Storage was substituted with local PNG publication;
no cloud documents, owner photos, credits or paid image requests were touched.
The existing 360-second outer supervisor bounded each run. Model weights were
downloaded and integrity-checked before the batch, so batch timings exclude
cold model download. All ten runs completed in alpha mode without fallback,
published original first and preserved the expected normalized-original pixels.

| Public fixture | Processing seconds | Sampled maximum process-tree RSS, GB |
| --- | ---: | ---: |
| White T-shirt on carpet | 12.88 | 1.567 |
| Blue jeans | 5.04 | 0.882 |
| Nike sneakers on box | 15.14 | 1.471 |
| Black hoodie | 4.78 | 0.849 |
| Cardigan | 15.52 | 1.482 |
| Denim jacket | 18.76 | 1.593 |
| Brown dress shoes | 14.99 | 1.303 |
| White sweatshirt | 5.18 | 0.775 |
| Chinos | 7.31 | 1.280 |
| Cargo shorts | 6.06 | 1.006 |

RSS was sampled every 100 ms across each job's process tree on the compatible
Mac runtime. These maxima can miss transient peaks and exclude the production
coordinator and platform overhead; they are not Linux cgroup or capacity proof.
The harness also records macOS `ru_maxrss`, complete package versions, source
photo hashes, asset publication order and output dimensions in its evidence JSON.

Visual review used untouched RGBA cutouts composited over defined light/dark
backgrounds; hidden RGB under zero alpha was not mistaken for retained clutter.
It found no major garment-body loss but did find real quality limits:

- The white tee, blue jeans and black hoodie retain silhouette, graphics and
  seams with mild edge softness. The white sweatshirt retains logos, zipper,
  cuffs and hood, with soft edges most noticeable against dark backgrounds.
- Sneaker bodies and logos remain, and the box is removed, but long dangling
  lace ends are truncated.
- The cardigan retains carpet inside one sleeve/body opening; the denim jacket
  retains table inside underarm openings and between its front panels.
- Dress shoes retain floor in some lace loops and a thin loose lace fades.
  Chinos retain a small sheet patch inside the folded crotch opening.
- Cargo shorts preserve the silhouette, pockets and drawstrings, with mild fringe.

Ten successful jobs therefore establish local processing compatibility, not
premium cutout quality or final hosted-flatlay fidelity. Original photographs
remain the protected source of truth. Do not alter readiness or credits to hide
these defects, and do not present the compositor/cutout as the polished final
outfit image. Separate provider-image and production worker gates remain open.

Local review artifacts are under `/private/tmp/easyoutfit-u2net-qa-output/`:
`evidence.json`, `review.html`, and per-fixture original, cutout and explicitly
labeled QA-only light/dark composites. Model integrity and full dependency
freeze are recorded in adjacent temporary QA artifacts. Preserve those artifacts
with the release evidence; they are not production assets.

## Accepted U2NET bounded production run and paused admission

Exact repair `f371ff435e31c57dbd7d9371751ea487b07858d1` passed Linux CI runs
`35815385682` and `35815383219` and independent source/limited visual review.
Preflight found five naturally eligible Neo garments and no global flatlay queue
candidates; API source remained `801b6679` with admission paused. No exhausted
attempt budget was reset or manually retried.

Worker deployment `bad70802-4e46-4d19-ad0c-afee3b4734f2` ran the exact commit,
completing three naturally claimed first attempts at `03:52:21`, `03:52:41`
and `03:53:06 UTC`. Each completion was accepted and persisted as public/private
`done`, with matching attempt-scoped protected original and derived references.
All used alpha; recorded processing times were 78.36, 17.19 and 9.66 seconds.
The first run includes cold runtime preparation; it is not a controlled isolated
model-download benchmark. No flatlay-child activity or failure diagnostic appeared.

The observer stopped at the three-success bound. Stop completed at `03:53:22 UTC`
with no active instances; platform stop and graceful `Worker stopped` markers
were recorded at `03:53:19.528` and `03:53:25.684 UTC`. A fourth job started in
the same tick as the third completion; its ordinary lease was preserved. At the
post-run readback, the ten garments were five previously exhausted failures,
three done, one processing and one pending. No manual retry or credit reset
occurred. This bounded success does not authorize continuous dispatch or imply
that the old exhausted jobs were repaired automatically.

Official build logs confirm rembg 2.0.85, ONNX Runtime 1.30.0, NumPy 2.5.3, Pillow
12.3.0, PyMatting 1.1.16, scikit-image 0.26.0, SciPy 1.18.1, Numba 0.67.0 and
llvmlite 0.49.0 on CPython 3.12/Linux x86_64. Thus the local Numba 0.62.1 and
llvmlite 0.45.1 are additional recorded Mac differences. Sparse 60-second service
memory samples reached 1.054 GB against the existing 8 GB limit. They are not
peak RSS, a general capacity guarantee or proof that every possible OOM event
was absent. No resource settings were changed.

After the worker stopped, one authenticated Neo Create flatlay action returned
HTTP 503 at `03:55:15.804901403 UTC`, corroborating the UI pause/no-credit-used
message. Readback found credit still one and refill timestamp unchanged, only
the historical failed/refunded ledger, no new reservation/provider-start fields,
an empty global queue, and the latest outfit still `awaiting_consent` with no
private ledger. There was no immediate pre-click ledger snapshot; this is
corroborated status/persistent-state evidence, not a cryptographic before/after
comparison. The authenticated paused-admission gate is accepted. Keep admission
paused and worker stopped until the next explicit readiness gate.

The three persisted production cutouts were separately exported read-only with
verified ownership, attempt, protected-original/derived path bindings, Storage
generation and checksums. Original and cutout PNG bytes were retained unchanged;
light/dark composites are QA-only. Visual review identified the approved public
denim jacket, brown dress shoes and white logo hoodie. The main garment bodies,
colors, seams and logos survive relative to their persisted originals, but table
patches remain in jacket gaps, floor remains inside shoe-lace loops, a thin lace
tail fades and the hoodie has soft/jagged edge fringe. These are usable
compatibility cutouts, not premium flatlay or hosted-generator fidelity proof.
Decoded persisted originals did not exactly match the pre-browser local fixture
pixels; the cause is unproven. That mismatch is recorded separately from the
verified production record/path identity and visual garment identity.

## Local configured recommendation fidelity candidate

The canonical browser check created a Casual / Minimalist / Subtle outfit with
a red cardigan, khaki cargo shorts and navy/white shoes. The color alone does not
prove that outfit wrong. Source review did establish a narrower defect: ordinary
semantic filtering computes the requested mood without requiring it, the soft
scorer does not use mood, and novelty/strategy adjustments can dominate the small
style score. The existing plain-over-graphic preference did not distinguish a
plain neutral alternative from a plain accent. The displayed ranking score is
not evidence of complete requested-style or mood fidelity.

The local repair extends the existing bounded preference only for Minimalist /
Subtle. After novelty and strategy ordering, an eligible same-category candidate
with known plain pattern and neutral palette can move ahead of less-supported
visual cues only when weather, compatibility and occasion scores are no worse.
The final diversity swap preserves that decision unless there is comparable
practical evidence. Required garments, complete combinations and limited-closet
fallbacks remain available; no color is banned. Other moods retain the existing
Minimalist plain-over-graphic behavior.

Saved nonempty root color strings are the only palette evidence. Missing, empty,
malformed list/object and explicitly unknown colors remain unknown across the raw
record, admission normalization and typed wardrobe model. Populated mood correction precedence is
root `mood`, root `moodTags`, root metadata, then analysis metadata. Explicit
unknown corrections cannot revive an older prediction. Numeric statement levels
must be finite and within 0–10; the historical synthesized zero supplies no
positive Subtle evidence. A named non-neutral color is an accent, not evidence
of brightness, saturation or incompatibility. Partial plain/neutral support is
never described as proof of complete Subtle fit.

Factual notes name graphic, statement or accent compromises, acknowledge an
affected required piece and disclose incomplete color/pattern evidence. They
do not endorse the request from the diversity-inclusive score. Tests exercise
the actual composer with anonymized saved facts, adverse novelty/strategy
adjustments and final swaps; they also cover required pieces, scarce/unknown
closets, practical-score constraints, the fallback route, correction parity and
notes. The 51 focused checks pass. The full backend ran 581 tests: 580 passed
with one expected macOS skip. Independent review found no remaining blocker;
the candidate may be frozen and pushed to PR 10 for exact-source Linux CI.
API deployment, worker restart and admission changes remain separately gated.

## Original production state

Refresh these values immediately before any mutation; they are a recovery
inventory, not a recommendation to restore unsafe legacy writers.

| Surface | Original observed artifact |
| --- | --- |
| API | Railway deployment `9b8e9d61-229f-4e25-8c9f-3659a8130d79`, successful/running, commit `ba62aed8aa573cbae1e16933fab5dae42afb130d` |
| Worker | Railway deployment `9c03de98-4f1c-4640-946d-394de485148e`, crashed/stopped, commit `5bb9ccff329d62c19fd0e684ed344d6dbe66c7b5` |
| Frontend | Vercel production deployment `dpl_6jcTmawjEhem86s3ZtaKbMmNsLYn`, commit `bb5f14bf`; refresh before mutation |
| Firestore | `projects/closetgptrenew/rulesets/4180bc45-e15b-4fb2-9dfe-669174ac2af1`, release `cloud.firestore`, updated 2025-10-25 |

Canonical targets are the ones in `EASYOUTFIT_OPERATOR_PLAYBOOK.md`:
Railway project `97ed14e7-f7a6-4f86-b919-94f133ed478e`, production environment
`240a7503-5fbc-49aa-9e9b-dc543c572dce`, API service
`43e4d1da-678f-4232-89ea-4394e404a372`, worker service
`cc65e747-accb-48a8-a4fd-fd3a3e30eaeb`; Vercel project
`prj_X8XE8UKf5R54oscVbNrXBdWgpMkB`, team
`team_OnDYjnYcXBXVSXCkAYZbToU6`.

## Rules and environment boundary

Use `frontend/firestore.rules` as the explicit release source, SHA-256
`eafa27b3270d6906835309c68a10b13b71822852d8a35f8b501e36da9f9811ca`.
The candidate intentionally constrains direct user-document writes to safe
bootstrap/name edits; full profile changes go through verified Railway APIs.
It also denies direct access to private jobs, onboarding state and receipts,
and protects managed wear history. The backend rules copy additionally contains
a pre-existing nested `users/{uid}/wardrobe/{itemId}` grant absent from live and
frontend rules; do not activate that unrelated grant. Refresh the complete
live-to-final-source rules diff before release. Deploy Firestore rules only,
without implicitly deploying Storage rules or indexes.

Vercel uses `BACKEND_URL`, `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_BACKEND_URL`
pointing to `https://closetgptrenew-production.up.railway.app`; the parent verified
all three read-only. No Vercel Admin credentials or `firebase-admin` package are
required. Keep privileged Firebase access in the intended Railway services.
Public browser Firebase configuration remains separate. The previous Vercel
Admin credential-entry proposal is withdrawn; do not import backend credentials
or restore old Admin handlers as a release or recovery step.

## Controlled release and recovery

1. Freeze the tested clean cumulative source and obtain independent parent
   acceptance of source, tests,
   final rules drift/hash, recovery plan and remaining live gates. Record the
   actual SHA and CI results; the accepted base is recorded above. Do not
   merge stacked PRs one by one or allow Git triggers to publish intermediate
   runtime combinations.
2. Refresh the original production inventory and canonical environment bindings.
   Use the intended signed-in operator console without bypassing the service
   account denial. Keep `main` untouched while validating the accepted
   candidate through controlled official deployment interfaces.
3. Pause new flatlay admission and keep worker dispatch stopped while establishing
   compatibility. Apply and verify the exact protected frontend Firestore rules
   before enabling writes that rely on them. Record the deployed ruleset ID and
   actual client allow/deny evidence. Deploy and verify the matching Railway API,
   including strict bearer identity, profile/quiz authority, upload ownership,
   private receipts and legacy bodyless-wear compatibility.
4. Deliberately retire any old worker deployment before starting the candidate
   worker (`backend/worker`, `python main.py`, one replica). Verify bounded
   recovery and independent garment/flatlay progress. Do not use the stale
   `backend/Dockerfile.worker` path. Resume admissions only after compatibility
   and dispatch are verified.
5. Verify the configured authenticated frontend preview, then release a frontend
   build made with Production environment values. A Preview promotion does not
   imply a rebuild with Production variables. Verify all canonical domains and
   retain the Railway-only privileged boundary.
6. Integrate only the final accepted cumulative candidate into `main` once the
   controlled rollout is compatible. Confirm Git source connections and record
   actual API/worker/frontend/rules artifacts, source SHA, live evidence and
   parent acceptance.

The accepted Goal 5 commit `b0f7dfb3d5a56c5aa3ff43f7c24b52735d90f768` is now
**historical evidence only, not a compatible complete fallback**. Its versioned
asset readers, leases and receipts were compatible with the earlier queue-only
candidate, but it predates the privileged-boundary migration and protected
profile rules. It also retains the queue-starvation defect. Do not deploy it
blindly or restore Vercel Admin keys to make its old writers work.

Contain incidents by setting `EASYOUTFIT_FLATLAY_REQUESTS_PAUSED=true` on the API,
applying that setting and verifying admission is paused, then stopping the worker
deployment. The API flag alone does not stop queued work. Record the prior flag
value/presence and restore that exact state only after deliberate verification.
The coordinator's SIGTERM handling terminates/reaps children and retains leases
for normal recovery.

Prepare and review a forward repair or a separately proven recovery candidate
that retains Railway Admin ownership, protected rules, versioned asset readers,
private job ledgers, receipts and immutable assets. Never blindly restore the
original API/worker/rules after new writes exist. Neither an old source SHA nor
a successful historical deployment is proof of a compatible recovery artifact.
Record actual recovery build/deployment IDs and health/contract evidence when
available; none is claimed here.

The immutable archive `easyoutfit-goal6-goal5-rollback-source.tar.gz`, SHA-256
`5085bebe9134be5551d05e2dc5b8706a8f659ce068ec06c5434b6f0773649310`, and its
matching full-commit manifest are retained as historical source evidence. The
archive name does not designate a supported full rollback, prebuilt image or
live recovery pass for the current candidate.

## Remaining live gates

Use only the explicitly authorized test account and public human-style garment
photos. It already contains ten garments and historical empty outfits; preserve
them and do not label its walkthrough a fresh zero-to-ten account test.

Required: authenticated save/readback and resume; category/coverage behavior;
configured, random and existing one-required-item generation; valid two-piece
one-piece/shoes combinations; saved owned detail without regeneration;
favorite/feedback persistence; one wear event on retry; explicit flatlay
queue/leave/return, authoritative settlement and delivered-image comparison;
physical-phone capture/HEIC and interrupted-network resume. A fresh-account
gate requires a separately authorized fresh identity if still needed.

Inspect the historical queued request through normal lifecycle handling.
Do not infer provider invocation, reset quotas or retry an ambiguous paid
request. Record real timing/cost only when observed. Final live evidence,
deployment IDs, limitations and parent acceptance must be appended before this
goal is marked complete.
