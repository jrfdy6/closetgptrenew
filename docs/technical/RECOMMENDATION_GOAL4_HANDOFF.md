# Recommendation fidelity — Goal 4 handoff

This change is stacked on the accepted Goal 3 commit `e47733446e32147d51dfb66a49ab0cbee5cd940e` (`codex/capsule-onboarding-experience`). It keeps the full questionnaire, ten-piece capsule, existing providers, explicit flatlay action and previous ownership/completeness contracts. It does not deploy or implement the later saved-look/wear presentation goal.

## Behavior and data path

- Manual configured, shuffle and dashboard flows still use `/api/outfits-existing-data/generate-personalized`. Dashboard now loads the authenticated saved profile before generation and fences account switches and failed profile reads.
- Raw optional profile answers survive conversion. Separate derived signals interpret `Round/Apple`, `Inverted Triangle`, every `skin_tone_0..100` value and real height ranges. Feet/inches punctuation survives validation. `5'8" - 5'11"` crosses the coarse height buckets and does not receive an unrelated short-person adjustment. Missing age, body shape or undertone remains unknown. Skin depth never implies warm/cool undertone; weight alone never implies plus size or measured fit.
- Saved `analysis.metadata` and root file metadata merge deliberately. Populated root corrections override older predictions; explicit unknown, zero and false survive. Unknown analysis fields and raw analysis remain available. The authoritative owned-record loader and real `ClothingItem` conversion both use the shared merge. A corrected recognized root garment type wins an older AI core-category prediction.
- Minimalist prefers a known plain piece over a graphic in the same category when weather/compatibility scores are no worse and existing hard filters admit the alternative. This runs after diversity/strategy ordering and in the completeness safety net. A final diversity swap cannot replace a plain piece with a graphic solely for novelty. Required pieces remain required. Unknown pattern is not treated as plain.
- The occasion fallback uses known temperature ranges/warmth before variety, then the same plain preference. Graphics remain eligible when needed; no new recommender/model or required-item selector is added.
- Final styling notes are regenerated after personalization, required-item repair and authoritative admission. A retained graphic is identified as a partial Minimalist match; required graphics are acknowledged. Notes describe actual recorded colors/textures rather than generic harmony, inferred fit, guessed wear dates or numeric quality claims. Both result and dashboard expose the compromise.
- Weather temperature, normalized condition, original condition and source/flags survive converter → validator → request → save → history readback. Documented aliases are deliberate (`Partly Cloudy` → `Cloudy`, `Light Rain` → `Rainy`); `Overcast` stays `Overcast`, unknown conditions become `Unknown`, never fabricated `Clear`. Absent temperature uses a labeled 72°F fallback. Legacy supplied contexts without source are not relabeled observed.
- Persisted results now retain final `outfitAnalysis`; outfit history response models retain weather and notes. The result removes internal ranking display; feedback confirms its save without training percentages; dashboard no longer presents the gamification heuristic as an AI fit score. Internal diagnostic scores remain available to existing logic.

## Validation

Controlled fixtures only, with no live account edits, provider calls or production writes:

- Frontend: **571 passing tests in 46 suites**.
- Backend: **356 passing tests, one Linux-only supervisor test skipped on macOS** (357 collected).
- Production Next.js build: **passed**, using placeholder public configuration and a local backend URL. The first sandboxed attempt could not fetch existing Google Fonts; the permitted network-enabled retry passed. No deployment was run.
- TypeScript: **129 existing diagnostics**, down from the accepted baseline's 139 after correcting Jest assertion typing in a changed test file; **zero diagnostics in changed files**. The repository build still uses its existing type/lint bypass settings; this is not a clean whole-repo typecheck.
- `git diff --check`: passed.

New tests exercise real profile analyzers, every slider value, actual quiz ranges, shared root/nested garment fixtures, actual request conversion and active HTTP endpoint, configured/random-selected contexts, required graphics, malformed/unknown optional values, fallback completeness, final compromise notes and exact weather/notes history readback. Actual robust composition is exercised with an artificial strong graphic strategy bonus, recent plain-item wear penalty and a final diversity swap; plain selection still wins when practical. Weather-worse plain alternatives do not override graphics. Corrected dress plus shoes remains a valid two-item composition.

Local evidence logs are `/private/tmp/easyoutfit-goal4-frontend-tests-final.txt`, `/private/tmp/easyoutfit-goal4-backend-tests-final.txt`, `/private/tmp/easyoutfit-goal4-build.txt`, and `/private/tmp/easyoutfit-goal4-tsc.txt`.

## Limits and next handoff

These tests establish deterministic contracts, not human satisfaction, measured garment fit or a month of appropriate outfits. The existing recommender still has heuristic rules and older fallback paths; real wardrobe visual quality and broader occasion/weather combinations require the integrated Goal 6 walkthrough. Physical-phone capture and real provider flatlay fidelity remain unverified here. No model/provider changes, credits, Stripe/prices, historical-row deletion or production mutation occurred.

Goal 5 owns addressable saved results, richer presentation, wear persistence and return navigation. It should reuse the factual `outfitAnalysis` and saved weather provenance. Do not reintroduce ranking/training percentages as quality claims. Goal 6 owns Vercel Admin configuration, real authenticated browser/provider checks and coordinated release/rollback of the accepted stack. Existing prior handoff prerequisites continue to apply.
