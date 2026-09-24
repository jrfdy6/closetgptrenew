# Outfit admission and mutation contract

Every mounted outfit creation path must call
`require_outfit_creation_ready(db, user_id)` before generation, then commit through
`persist_created_outfit(db, user_id, outfit_id, outfit, admission)`. Daily
suggestions use the same readiness helper inside their own final transaction.
The final transaction rechecks the captured `app_data_epoch`, readiness, and each
owned garment. Client completion flags and garment metadata are not evidence.

New accounts need the existing completed style-profile contract plus ten unique,
usable garments with top/bottom/shoes or one-piece/shoes coverage. Generated looks
must be complete and contain the one required base item when supplied. Admitted
manual saves can contain one through ten exact selected garments.

Protected `onboarding_states` completion milestones preserve prior completion.
Legacy saved-outfit evidence without a milestone must have immutable Firestore
`DocumentSnapshot.create_time` earlier than the fixed rollout cutoff, owned
garment references, and a complete combination. The default cutoff is
`2026-09-23T00:00:00Z`; server configuration
`EASYOUTFIT_ONBOARDING_GRANDFATHER_CUTOFF` can explicitly replace it. Invalid
configuration disables this legacy evidence path. Editable `createdAt` fields
cannot backdate evidence. The cutoff must remain fixed after rollout.

Readiness denial is HTTP 409 with `detail` containing `code: onboarding_required`,
`resume: /onboarding`, `stage: style|capsule`, `profile_complete`, and `capsule`.
The existing capsule shape is retained. Firestore direct outfit writes must stay
denied so newly caller-created documents cannot become completion evidence.
Wardrobe reads and capsule sources union all five historical owner fields, reject
conflicting aliases, and hide deleted records. Generator inputs use the same
ownership predicate and normalize `userId` in the verified in-memory snapshot;
this does not migrate stored ownership.

`PUT /api/outfits/{id}` accepts only name, description, notes, occasion, style,
mood, season, items, and isFavorite. It returns `success`, matching `id` and
`outfit_id`, and the canonical saved projection, also nested under `outfit`.
Selected items are reloaded from owned wardrobe documents. Changing the selected
set clears a prior preview; an active private reservation remains held until its
normal lifecycle settles the obsolete request.

`DELETE /api/outfits/{id}` returns `success`, matching IDs, and `deleted: true`.
The record is soft-deleted, hidden from active reads/library/stats, and remains
available to immutable wear history. Repeating deletion retries any interrupted
pending flatlay settlement through the existing lifecycle. It does not directly
alter credits, and duplicate/late settlements cannot refund twice.

Saved projections include `flat_lay_admission_paused` and
`flat_lay_admission_reason`. Global pause disables `flat_lay_request_allowed`
without hiding existing completed previews. Missing owned original photos also
disable requests. Request POST checks pause before reserving any credit.

Canonical outfit ratings create one deterministic `outfit_feedback` document per
user/outfit. Its first `created_at` is immutable across retries and edits. Rewards
use the same deterministic `reward_operation_id`, and preference/reward callbacks
carry the saved app-data epoch. Favorite, rating, edit, and delete writes all check
ownership, soft deletion, and the app-data deletion fence.
Profile, quiz, and onboarding transactions retain the epoch from their first
read across Firestore retries, so a completed concurrent data clear cannot cause
an old form submission to restore the cleared answers.

`wear_statistics.weekly_wear_summary(db, uid, now=None)` provides the shared
Monday-based weekly count in `users/{uid}.location_data.timezone`, default UTC.
It excludes undone/future events and preserves history of deleted outfits.
Only accounts with no owned history records use active outfits' lastWorn fallback.
The helper is read-only; storage errors propagate rather than becoming zero counts.

Credential-free regression suites cover admission, mutations, public projection,
both alternate generators, private flatlay settlement, HTTP persistence and
ratings, and Monday/timezone/DST wear counts. Live provider and cloud writes are
outside these checks.
