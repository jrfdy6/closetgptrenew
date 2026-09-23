# Capsule onboarding experience — Goal 3 handoff

Goal 3 makes the saved onboarding state from Goal 1 and image recovery contract
from Goal 2 visible as **Your style → Your capsule → Your first look**. It starts
at accepted Goal 2 commit `d8bbaccd22a9aa2636acba06da253551d8a6879a` and stacks on
`codex/image-worker-durability`. This is a reviewable implementation; release and
live end-to-end validation remain Goal 6.

## User journey

The full signed-in questionnaire is unchanged. Its question catalog is
byte-identical to the accepted base, including all gender variants. Section
labels explain the purpose of each group, distinguish spending from measurements,
and retain units, optional questions and privacy guidance. Explicit single-choice
selection now advances after a 400 ms confirmation pause. A visible instruction
before the options explains this behavior. Next remains available to continue
immediately, and Previous lets people review retained answers. Both automatic
and manual advancement focus the next question heading; saved progress remains
visible. Sliders require Next, and the final answer requires an explicit Save
and continue. Restored answers and slider defaults never trigger advancement.
Repeated introductory copy is reduced after the first question on mobile.

One cancellable timer is replaced by rapid reselection and invalidated by manual
navigation, submission, draft conflict/reload, account changes and unmount. The
destination comes from the latest draft and active gender variant, retaining
next-unanswered guest continuation without overwriting newer answers. Returning
to the same question or account cannot revive an earlier selection timer.

Guest signup continues at the first unanswered question in the full variant.
Guest answers are not promoted to a completed profile. A confirmed new account
gets a UID-bound session-storage transfer receipt before transfer begins. A
refresh can expose explicit Retry setup for that same account. Current account
checks fence reads, writes and cleanup; delayed acknowledgments remove guest
copies only when both original snapshots still match. Existing server drafts
and completed profiles remain authoritative. Profile submission includes only
the currently active question variant, retaining older answers in the draft
without sending conflicting body/size answers to profile normalization.

After profile submission, the capsule shows persisted wardrobe items and the
actual missing categories. Completion still requires ten unique usable garments
and shoes plus either tops/bottoms or a one-piece. Failed wardrobe reads show a
retryable error instead of a zero count. Original photos count while cutouts are
pending or failed. Category correction uses the existing owned update route;
processing retry uses Goal 2's expected-attempt endpoint through a narrow proxy.
Continue waits for refreshed server readiness and displays reconciliation errors.

The recap places one primary Create my first outfit action beside its ready
confirmation, before the photos and profile detours. It routes directly to
`/outfits/generate?onboarding=1`, where the existing occasion/style/mood form is
inline. The entry checks current saved profile and capsule readiness. Generation
requires an explicit configured or Surprise me action; visiting the page or
dashboard does not automatically create the first outfit. Estimated weather is
labeled, with a manual conditions selector. Flatlay creation remains a separate
explicit action with the existing credit contract. The dashboard offers a
stage-appropriate resume card instead of forcing an upload modal.

## Photo persistence and recovery

The uploader can save one item or several without weakening the ten-item capsule
gate. JPEG/PNG/WebP originals are uploaded without lossy client recompression;
HEIC is converted locally. Each tile retains its stable ID, uploaded URL and
prepared save payload across retries. Exact-byte SHA-256 matches identify
duplicates within the selected batch and saved inventory when hashes exist.
This is not perceptual deduplication of alternate photos of the same garment.

Each acknowledged item updates onboarding independently. The legacy batch
completion callback fires once only when selected work has resolved, preserving
dashboard and wardrobe callers that close their dialog on completion. Partial
failures stay visible. Removing a failed selection or successfully retrying it
can resolve the batch. Unmount/account changes prevent subsequent work and
callbacks; an already dispatched request may still settle.

Successfully acknowledged garments survive leave/return through persisted
inventory. A photo that has uploaded but has not reached acknowledged item save
is still an unsaved selection: the UI says so and warns on browser leave. This
change does not introduce a durable pre-save photo staging service. Transfer
receipts survive refresh in the same browser session, not loss of that session.

The active wardrobe GET projection now preserves safe original URLs, hashes,
soft-delete markers and public processing/retry fields. Missing images remain
missing. The active image-upload route returns sanitized retryable 503 on
storage failure instead of claiming success with a random placeholder URL;
the client also rejects fallback upload responses before analysis/save.

## Verification

September 23 Goal 6 auto-advance follow-up: the page, draft-hook and skin-tone
slider suites passed **56 tests in three suites**. They cover the 400 ms delay,
rapid reselection, manual navigation cancellation (including leaving/returning),
all gender variants, fresh null and stale question cursors, restored drafts,
slider persistence, conflicts/reload, account changes, unmount, retained guest
continuation and explicit final submission. Targeted lint has no errors and
retains the existing hook-dependency/test-mock warnings. The frontend production
build passed using non-secret placeholder Firebase client settings and network
access for existing Google Fonts; no environment/configuration file changed.
The repository build still skips its type/lint gates. These local checks do
not replace independent preview browser acceptance or the remaining phone
capsule journey. The earlier Goal 3 validation below records its original scope.

- Frontend: `npm test -- --runInBand` — **546 tests in 44 suites passed**.
- Backend: `python -m unittest discover -s tests -p 'test_*.py'` — **323 tests:
  322 passed, one Linux-only process test skipped on macOS**.
- Production `npm run build` passed with non-secret placeholder Firebase public
  configuration and the installed Next 14.2.35 dependencies. The first sandboxed
  attempt could not resolve Google Fonts; the network-enabled retry succeeded.
  No dependency or lockfile change was made.
- Separate `npx tsc --noEmit --pretty false` still reports the existing **139
  diagnostics**, with **zero in changed files**. The repository's build already
  skips type/lint validation; a successful build is not a clean whole-repo type
  check. `git diff --check` passed.

Tests cover continued guest signup, account switches and delayed acknowledgments,
full active-variant submission, saved capsule count/coverage and read failures,
category/retry errors, explicit completion, upload fallback rejection, original
preservation, failed-sibling batch recovery, unmount fences and no first-outfit
auto-generation. Retry-proxy tests cover ownership-preserving forwarding and
safe failure responses.

Browser verification used an isolated local Next harness importing the actual
changed components and hooks, with synthetic authentication and API fixtures.
The authorized public garment photos were served locally. Desktop and 390×844
checks covered quiz selection/Next/focus, a four-piece capsule, ten shirts failing
coverage, original photos with failed cutouts, read/category-save errors, recap
placement and navigation into configuration. Explicit occasion/style/mood and
manual-weather actions emitted their selected configuration through fixture
callbacks. The mobile quiz had no horizontal overflow. Recent console warning
and error snapshots were empty; the temporary viewport override was reset.
The recap destination in that harness uses the actual shared configuration
component with fixture callbacks, not the production generator page/API.

No live signup, Firestore/Storage write, provider request, paid flatlay, physical
phone upload or production deployment was performed for this implementation.
These component/contract checks do not establish production integration or image
quality. Local fixture files and photo assets are not committed.

## Release and follow-on boundaries

The frontend needs the compatible Goal 1 onboarding API/rules and Goal 2 image
worker/retry API, including this safe wardrobe projection. Goal 6 must verify the
full authorized photos on a real phone, interrupted upload/save/return, guest
signup recovery, category corrections, processing retry, first outfit persistence
and explicit flatlay/credit settlement in the intended deployed environment.
Use `EASYOUTFIT_OPERATOR_PLAYBOOK.md` and preserve the earlier goals' protected
state and original-image compatibility when rolling back.

Recommendation fidelity and result presentation remain Goals 4 and 5. This goal
does not change providers, prices, Stripe, credits, production data, historical
photo cleanup or the number of selected-item controls.
