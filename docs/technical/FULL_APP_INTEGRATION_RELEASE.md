# Full-app integration release — September 23, 2026

This candidate preserves the existing page structure, questionnaire and ten-item capsule. All new-user outfit creation paths use server-owned completion evidence. Historical completion must be supported by protected milestones or immutable pre-rollout saved-outfit metadata.

Wear recording now commits counts, history, TVE, XP and tokens together. Durable receipts deduplicate uncertain retries, concurrent submissions, undo and reactivation. Leased jobs update challenges and caches. Undo reverses physical/current progress while keeping earned rewards. Every delayed writer and transactional retry retains its original account-data epoch so clearing data cannot be undone by late work.

Profile, garment and outfit mutations are server-owned. Owned reads consistently support legacy identity aliases and reject conflicts. Clearing app data is a resumable, bounded process: it preserves login, billing/credits/privacy and minimal receipts, drains image jobs, removes owned storage generations, and reports failure/retry honestly.

Existing frontend clients use canonical mutations, refresh after acknowledged wear, show unavailable data without fabricated success, and reuse existing navigation. Payment-return copy requires verified state; no payment integration or transaction was changed. Paid flatlay admission remains explicitly paused until the compatible release is verified. No new customer page or AI model is introduced by this change.

## Verification before deployment

- Integrated backend: 476 tests run, 475 passed and one platform-specific skip.
- Frontend: 889 tests plus ten middleware policy checks passed.
- Typecheck: 114 baseline diagnostics versus110 candidate; zero added diagnostic identities. Build configuration still skips type/lint failures; the repository is not wholly type-clean.
- Production-config frontend build passed with existing public Firebase client config and canonical Railway origins, without Firebase Admin credentials.
- Real Firebase rules emulator:793 checks passed; source SHA256 `1ddc121a3bac204aff875a10ab2606bd84863e5fe4c9199946ab33d4a87d3dea`.
- Real Firebase privacy integration:40 checks passed using disposable Auth/Firestore/Storage data, including failed-storage resume, exact-once refund, retained entitlements and late-job fencing.
- Real Firestore wear integration: concurrent retries converge to one event/reward. Initial contention can fail; retry with the same key recovers. Undo/reactivation/backdating/projection/rating receipts passed.
- Mounted API audit:219 routes,196 denial checks, no duplicate routes or missing modules. Global health reset is additionally operator-gated.
- Public browser pages:24 viewport combinations passed. Full authenticated browser acceptance and deployment evidence must be recorded separately; these are not implied by source tests.

Browser upload acceptance uses demo-only storage ACL/image-analysis adapters; it verifies transport/UI/persistence, not a new provider quality trial. Previously accepted hosted flatlay evidence remains applicable. Physical-phone camera/OS behavior is waived by the owner, not marked passed.

## Deployment requirements

Deploy the compatible backend, worker mirrors, protected frontend Firestore rules, and composite indexes. Run `python -m src.worker.gamification_runner` in a dedicated backend-root Railway service using existing server-side Firebase access. Its config is `backend/railway.gamification.toml`; it polls projection/deletion queues and leased maintenance. Do not add Admin keys to Vercel.

Keep intermediate Git deployments from publishing mixed versions. Validate a production-config frontend artifact and authenticated preview before releasing canonical domains. Reopen flatlay admission only after matching runtime verification. Recovery preserves protected rules, private ledgers and the Railway Admin boundary; old permissive rules or Vercel Admin keys are not a rollback strategy.

No release artifact is claimed by this document until exact deployment IDs and smoke/observation results are appended.
