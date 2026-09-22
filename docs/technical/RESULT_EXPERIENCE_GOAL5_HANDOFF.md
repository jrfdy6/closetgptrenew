# Saved outfit experience — Goal 5 handoff

Stacked on the accepted Goal 4 commit `fd148750a91cf226249a47f6b0a949562267bd31` (`codex/recommendation-fidelity`). This phase implements private saved results and their existing actions. No production deployment, real provider call, account mutation, credit reset, billing change or later-goal work was performed.

## Result and return flow

- `/outfits/[id]` loads the owned saved outfit through the new active API `GET /api/outfits/{id}`. It verifies a real Firebase ID token, rejects missing/foreign/deleted documents and returns private, no-store responses. The read uses a transaction for a consistent outfit, garment and preview-ledger snapshot and performs no writes.
- Configured and Surprise Me generation navigate to the confirmed persisted ID. A response without a valid saved ID remains an error. Duplicate clicks are fenced; no second client-side save or automatic flatlay request occurs. Dashboard cards open this same result instead of invoking the former history-write chain.
- My Looks cards open that result. Cards use the selected garments' original photos, an explicit favorite action, and truthful empty/unavailable states. Existing search and filters remain available with a simpler hierarchy. An incomplete capsule shows nonblocking guidance while existing saved looks remain accessible. List failures show an explicit retry; stale reads and account changes cannot restore another account's list or mutation result.
- The shared viewer presents saved occasion/style/mood/weather, available styling notes, original pieces, favorite/wear history and explicit feedback save. Internal ranking is not a customer quality score. Sign-in returns to a validated saved-outfit path; quiz onboarding still has priority. Arbitrary/external redirects are rejected.
- Current owned garment documents supply photo URLs. Unavailable/foreign garments become safe placeholders; cleared current photos cannot revive a URL from an older outfit snapshot. Legacy `favorite` is normalized while explicit `isFavorite: false` wins. Existing text feedback stored as `userFeedback` survives reload.

## Flatlay authority and recovery

The private `flat_lay_requests/{outfit_id}` ledger supplies the visible status, current request identity and completed image. Public outfit aliases cannot make an old image current. The reader never reserves, claims, settles or retries paid work.

Source identity now matches at reservation, worker claim, provider admission, completion and saved read. Each referenced garment must remain owned and available, and its saved source fingerprint must match the current source. Same-ID photo replacements therefore invalidate the earlier preview. A confirmed old completion may be replaced only by an explicit new request under the existing credit contract. A pending earlier request remains held until settlement. A mismatched ledger outfit ID is nonrunnable and is not rewritten or refunded by worker recovery.

Legacy requests without provable source identity, missing private ledgers with prior queued/pending/completed/error aliases, and unknown provider/worker outcomes stay on a visible review hold. An inconsistent `retryable: true` cannot bypass an unknown outcome. No inferred debit/refund or automatic provider retry is added. API and worker lifecycle mirrors remain byte-identical.

The saved page polls only pending work and restores status on return. Credit settlement changes trigger a balance refresh, so refunding the last credit enables an explicit retry. Balance errors have their own recovery state and clear after a successful read. An image-load failure offers image-only reload without another request or credit use. Changed pieces show an explanation. Download/share validate image data and show pending, success or actionable failure; late responses are discarded after navigation. Existing private image-sharing boundaries are unchanged.

## Wear transaction and compatibility

New clients POST `/api/outfits/{id}/worn` with `idempotency_key` and the browser's IANA `timezone`. The server derives the date from its own clock. The verified owner, saved outfit and every garment are read before any write. A single transaction commits:

1. Outfit wear count and current last-wear fields.
2. Each owned garment's wear count and last-wear fields.
3. One `outfit_history` event (`wear-v1-…`, `wear_operation_version: 1`).
4. Private operation and local-day receipts in `outfit_wear_receipts`.

The same key returns the same event across dates. Different keys for the same outfit and local day return that day's existing event. Contending outfits sharing a garment retry atomically. Aborted writes do not partially increment counts; a lost acknowledgment can safely retry.

Receipt fields `event_id`, `history_id`, `wear_date`, `timezone`, `date_worn` identify the original event. `wear_count`, `last_worn`, `last_wear_date`, `last_wear_timezone` and `garment_wear_counts` reflect current authoritative records, including a delayed replay after later wears. `event_wear_count` and `event_garment_wear_counts` preserve the event-time snapshot. The UI adopts authoritative counts and invalidates reads begun before a mutation acknowledgment.

The pending key survives failed acknowledgment and remount in session storage, scoped by owner and outfit, with an in-memory fallback. New clients clear it only after a valid acknowledgment. Duplicate day receipts remain the server's final protection.

For API-first rollout, both proxies and the API accept a genuinely empty legacy request body through the same transaction. Its deterministic key uses owner, outfit and server UTC day. Explicit `null`, malformed JSON and invalid supplied keys remain rejected. **Old bodyless clients cannot recover an original action across UTC midnight:** they lack a persistent action key or client timezone. New clients retain the explicit key across dates.

Managed events/receipts are protected in both tracked Firestore rules, and the existing history edit/delete API refuses managed events. History's weekly parser accepts the new millisecond timestamps and legacy numeric seconds. The active new callers no longer use `/outfit-history/mark-worn`; that legacy endpoint itself is unchanged. Old cached dashboard clients may still call it until refreshed. The new operation intentionally omits the former nontransactional XP, TVE, preference and `user_stats` side effects. Outfit, garment and history data are authoritative; this phase adds no points/rewards claim or undo-wear feature.

## Validation

Controlled fixtures only:

- Frontend: **691 tests passed in 51 suites**.
- Backend: **432 tests passed, one Linux-only supervisor test skipped on macOS** (433 collected).
- Production Next.js build: **passed**, using placeholder public Firebase configuration and a local backend URL. The initial sandbox attempt could not fetch existing Google Fonts; the authorized network-enabled build succeeded. No deployment was run.
- TypeScript: **124 pre-existing diagnostics**, down from the accepted 129; **zero in changed files**. Existing build type/lint bypass settings remain, so this is not a clean whole-repository typecheck.
- `git diff --check` and lifecycle mirror parity: passed.

Focused regressions cover actual active API registration/auth, read-only detail transactions, ownership/redaction, favorite/feedback aliases, strict proxies, generated-ID navigation, account fences, lost acknowledgments, 8-way transaction contention, cross-outfit garment contention, delayed receipt replay, legacy-body rollout compatibility, changed source identity at each lifecycle boundary, incomplete/legacy looks, last-credit refund recovery and stale-read mutation races.

Browser checks used the actual product My Looks/detail pages, shared controller/viewer, hooks/services and CSS in `/private/tmp/easyoutfit-goal5-browser` on `http://127.0.0.1:3035`. Firebase/auth, subscription and API persistence were isolated local fixtures. Public garment photographs were used; the completed-preview photograph is a loading/layout fixture, **not evidence of AI image fidelity**.

Verified desktop and 390×844 layouts, My Looks→detail, favorite→reload persistence, wear count/date readback, explicit flatlay→queued→leave→return with the same request, completed preview/download feedback, image-only retry and current-piece display after an edit. Both narrow pages had document width382 within viewport390; measured result action heights were44px or greater. No console errors occurred in this pass (one existing logo sizing warning). Final counters before reviewer takeover: 15 detail reads, 3 list reads, 1 favorite write, 1 wear write, 1 explicit flatlay request, **0 generation calls** from navigation/reload/retry.

Evidence logs: `/private/tmp/goal5-frontend-final.log`, `/private/tmp/goal5-backend-final.log`, `/private/tmp/goal5-tsc-final.log`, `/private/tmp/goal5-build.log`. The parent also independently reviewed the saved UI and re-ran bounded frontend/backend checks; final parent acceptance is recorded in the coordinating thread.

## Release and limits

Goal 6 owns the coordinated stack release, real authenticated walkthrough, production provider/worker status checks and rollback. Deploy the matching API and worker together with the protected receipt/history rules, then the frontend; verify the Admin credentials and prior worker prerequisites from earlier handoffs. Existing schema documents are additive; no destructive migration is required. Do not roll back to writers that bypass managed wear receipts or omit source guards while new operations are active.

This phase does not prove cloud Firestore contention behavior, physical-phone capture, real flatlay fidelity/latency, analytics accuracy outside the authoritative wear records or customer retention. The source fingerprint identifies owner/source URL; overwriting bytes at an unchanged URL remains outside that identity guarantee. Legacy unprovable preview records need deliberate review; opening them does not spend a credit. Native OS sharing and real cross-device behavior still require the release walkthrough. The ten-item/full-questionnaire requirement, provider choice, pricing/credits and Stripe scope remain unchanged.
