# Gamification launch verification — September 24, 2026

**Status: locally verified release candidate; not yet released to production.**

The candidate is the gamification polish work on `codex/gamification-launch-polish`, based on `cfe6cdd425e93eee624d3ac7c9b4c4e3236aa8b3`. That SHA identifies the already released base, **not these uncommitted candidate changes**. This is the pre-merge verification record. The release PR and dated operator ledger record subsequent immutable commits, deployment IDs and runtime checks. The [baseline audit](../gamification-launch-audit-2026-09-24.md) records earlier failures; it is not the current verification verdict.

The bounded final source review found no remaining launch blocker in the reviewed reward, ownership, epoch, recovery, and challenge fixes after the archived cold-start correction. This is evidence for the tested behavior, not a claim that every workflow, device, or production failure mode has been exercised.

## Evidence and its limits

| Verification | Recorded result | What this establishes |
|---|---|---|
| Backend CI command | **439 tests passed across the exact 28 modules** in `.github/workflows/app-integration-tests.yml`; exit 0 in 9.251 seconds, completed 12:03:04 UTC | Local execution of the selected CI contracts, including the new reward and recovery regressions. The evidence manifest records no source drift and matching workflow dependency pins. This is not a remote GitHub CI run or a clean Linux dependency installation. |
| Frontend full suite | **950 tests passed in 78 suites** | Full Jest verification before the final visual adjustments. |
| Final affected frontend checks | **15 affected tests passed**, followed by a successful production-config build | Targeted verification of the subsequent changes. Do not describe the 950-test run as a second full run after those adjustments. |
| TypeScript comparison | **110 existing diagnostics; no added normalized diagnostics** in the recorded baseline comparison | No newly introduced diagnostics in that comparison; this is not a clean TypeScript check. |
| Firestore emulator catalog exercise | **59 definitions; 532 transaction commits**, run `cd0d71462b5e`, PASS | Real emulator transaction execution and reward/progress/receipt assertions over the catalog; maximum four writes per transaction in that exercise, zero production requests or provider calls. Some completion thresholds and histories were seeded. It does not prove 59 natural browser journeys or a year of real activity. |
| Actual browser action | Enrolled in a challenge, then submitted an outfit rating through the UI with the preceding nine ratings/progress seeded | The actual final user action crossed the threshold through the application. The UI showed **350 total XP, level 2, Style Contributor, and Completed 1**. Reload preserved the result without another award; retry/concurrency behavior was tested separately at the service and component layers. It does not establish ten naturally entered ratings. |
| Desktop presentation | Light and dark modes, badge keyboard activation with Enter, Escape dismissal, restored focus, and no horizontal overflow at **1280 px** | The observed desktop interactions and layout passed. This is not a comprehensive accessibility audit. |
| Responsive/mobile candidate | **UNVERIFIED** | The attempted in-app-browser viewport change did not change the effective 1280 px viewport; Chrome was unavailable. No candidate mobile-responsive pass may be inferred from that attempt. |
| Native phone behavior | **NOT PASSED / NOT VERIFIED** | Native camera and share behavior were not exercised for this candidate. Earlier waivers or older screenshots do not constitute a current pass. |
| Production acceptance | **PENDING** | No deployment or production smoke test of this candidate is recorded here. |

The browser observations above were supplied by the root integration run. The independent review used source inspection, local tests, transaction doubles, and the reproduced failure cases; it did not independently operate a browser or production account.

## Reviewed boundaries

- **Owned facts and badge awards:** eligibility queries use the shared ownership rules, reject conflicting aliases and deleted records, and share the award transaction. The first observed account epoch is retained across reads, badge checks, and transaction retries. A clear between eligibility and commit cannot award into the new account epoch.
- **Rating durability:** feedback and its pending reward marker commit together. Settlement atomically writes the five-XP ledger receipt and clears the marker. API retries and worker recovery use the same operation key as the previous implementation; an existing or privacy-scrubbed receipt prevents another award. Unmarked historical feedback is not automatically backfilled.
- **Analytics-only clearing:** only fresh work can adopt preserved pending feedback. The helper requires protected, owned, completed analytics-only deletion-job evidence for every intervening epoch. Missing proof, a different clearing scope, or an old in-flight epoch remains rejected. This proof is deliberately bounded to at most 100 epoch transitions.
- **Cold-start milestones:** owned persisted wardrobe facts drive the existing 10/25/50 thresholds. New qualifying progress awards the staged 50/100/200 XP and the existing final token reward once. Active or archived completion suppresses backfill even without modern receipts; archived partial milestone markers are preserved. The archived-only completion regression was also checked in the real emulator and in targeted tests.
- **Challenge dates and enrollment:** period identity, rolling streak/duration windows, half-open deadlines, delayed pre-deadline actions, expiry, and legacy completion suppression have dedicated regressions. Late processing does not consume the next enrollment period. Role Defender uses consistent calendar-week semantics across spring DST.
- **Authoritative time and annual progress:** new uploads receive server creation time; upload challenge facts use the Firestore snapshot creation timestamp, not caller-supplied dates. Annual progress rejects actual wear dates outside the enrolled cycle while retaining valid backdating inside it. Unknown historical upload times are not manufactured as eligible evidence.
- **Reward receipts and repeated actions:** wear, rating, challenge completion, milestones, and keyed token pulls have replay/concurrency coverage. Distinct COMMON pulls preserve both pending bonuses; repeating a pull does not debit again. Current role promotion requires a recent streak and ignores undone wear history. Backend gacha/role tests do not imply that new user controls were shipped; dormant challenges are excluded from the available list.
- **Automation and privacy:** tests exercise leased job ownership, transaction failures, lost acknowledgements, retry backoff/exhaustion, paging across midnight, weekly scheduling, daily reconciliation, stale-worker fencing, and account clearing. Reward repair runs before fallible derived-cache work. Failure in wear projection does not prevent the privacy worker from progressing. API and worker privacy implementations are byte-equal under a CI assertion.

These checks preserve the full questionnaire and ten-item capsule contract. They do not authorize a new feature, change reward formulas, weaken protected fields, or replace production acceptance.

## CI and repeatable checks

The authoritative selected backend command is in [App integration contracts](../../.github/workflows/app-integration-tests.yml). Run it from `backend/` with `PYTHONPATH=.:tests`; running from the repository root can import the unrelated root `src` tree. The workflow explicitly includes:

- `test_gamification_catalog`, `test_gamification_automation`, `test_feedback_reward_recovery`, and `test_badge_eligibility`;
- `test_tve_epoch_hooks`, `test_derived_epoch_hooks`, upload/API creation contracts, canonical wear and reward integration;
- onboarding/profile contracts, privacy lifecycle and mirror checks, route registration, and the Firestore index manifest.

Frontend CI runs the full Jest suite; its patterns include the new components and hooks. The production-config build is a separate recorded local verification. Real-emulator catalog exercises and browser acceptance are additional evidence, not substitutes for or automatic steps in that CI workflow.

## Artifact ledger — release owner to complete

The reports and harness listed below were copied to durable private `launch-polish-evidence/` under the evidence directory, with SHA-256 `manifest.json`. The temporary paths identify their original working locations. Subsequent deployment IDs belong in the release PR and dated runtime ledger; the base release IDs must not be substituted.

| Artifact | Candidate evidence / pending identifier |
|---|---|
| Frozen candidate commit and PR | **PENDING — ROOT TO RECORD** |
| Backend 439-test report / exact source manifest | `launch-polish-backend-exact-ci.json` and adjacent `.log` in the durable evidence directory below; preserved in the durable evidence directory |
| Frontend full-suite report | `/private/tmp/easyoutfit-gamification-build/report.md`, `summary.json`, and `jest-results.json`; preserved in the durable evidence directory |
| Final 15-test report, production build and source manifest | Same directory: `visual-followup-jest.json`, `build.log`, `source-manifest.json`. Local build ID `build-1790250806167`; manifest SHA-256 `d4f07139aa1020fc7b9170a8be39117b473d06b8fe68883374ca0dbb88a55ed5`. These are local build identifiers, not Vercel deployment IDs; preserved in the durable evidence directory |
| Emulator 59-definition / 532-transaction report and harness revision | `/private/tmp/easyoutfit-catalog-emulator-proof/result.json` and `run.log`, run ID `cd0d71462b5e`; harness SHA-256 recorded in the durable manifest |
| Archived cold-start real-emulator regression | Preserved in the private `launch-polish-evidence/catalog/result.json` report |
| Browser evidence: action, reload/retry, desktop light/dark and keyboard | Rating readback: `/private/tmp/easyoutfit-full-release-qa/launch-feedback-evidence.json`. Separate visual/keyboard screenshot or recording IDs Preserved in the private `launch-polish-evidence/catalog/result.json` report |
| Remote GitHub CI run for exact candidate SHA | **PENDING — NOT YET RECORDED** |
| Railway API deployment and running source revision | **PENDING — NOT RELEASED** |
| Railway rewards/privacy worker deployment and running source revision | **PENDING — NOT RELEASED** |
| Vercel candidate deployment, production promotion and canonical-domain checks | **PENDING — NOT RELEASED** |
| Image worker / rules / indexes disposition | **PENDING — ROOT TO RECORD whether unchanged or independently verified** |
| Candidate responsive/mobile acceptance | **UNVERIFIED — effective test viewport remained 1280 px** |

Durable working evidence directory: `/Users/neo/Documents/Codex/AI-Clone/workspaces/easyoutfitapp/docs/full-audit-release-prep-2026-09-23/`. Related records there include `gamification-automation-reliability-2026-09-24.md`, `gamification-derived-integration-emulator.json`, `gamification-launch-polish-emulator.json`, `launch-polish-badge-emulator.json`, and `launch-polish-index-review-2026-09-24.md`. Local backend/worker logs, `gamification-runner-health.json`, and `gamification-no-provider-key-proof.json` are under `/private/tmp/easyoutfit-full-release-qa/`. Their existence and local health are not production runtime acceptance.

Release coordination and containment remain governed by the [operator playbook](EASYOUTFIT_OPERATOR_PLAYBOOK.md). Preserve reward receipts and privacy markers during recovery, deploy matching API and rewards-worker source, and record the matching frontend artifact before claiming the candidate is live. This document does not establish natural multiweek scheduling reliability, production load behavior, mobile responsiveness, or native-device acceptance.
