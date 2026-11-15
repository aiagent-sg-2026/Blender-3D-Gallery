# Sequential fish realism QA

The owner authorized automatic one-at-a-time improvement of the remaining 57 fish, with small-batch previews, on 2026-11-15. Barramundi, Betta and stingray remain at their accepted versions under `models/fish-realism-review/`.

`queue.json` tracks the exact remaining set in original FISH-ID order. Work is isolated from production until the item has passed its applicable gates. A passing file parser or a moving mesh is insufficient proof of visual quality.

## Per-fish loop

1. Inspect the current production render and actual reference photographs. Record the chosen visual species where a supplied common name is ambiguous; preserve the supplied aliases.
2. Correct that fish's silhouette, mouth, eye size/placement, gill contour, fin layout, material response and markings. Reuse utilities, not an indiscriminate single anatomy across species.
3. Render a neutral side view and relevant detail view. Check silhouette and surface against photographs, inspect fin edge thickness and natural folds, and fix visible failures before proceeding.
4. Keep a cyclic swim appropriate to its locomotion. Check actual tail/fin deformation and loop endpoints. An eel-like wave, ray undulation and tail-driven swim have separate criteria.
5. Reopen the source and real exported GLB, validate finite geometry and animation, compare motion at probes, inspect validator errors/warnings, and preserve the three accepted fish.
6. Record what passed, what changed and any unresolved limits. Mark partial work honestly. Show small batches in chat without requiring per-item owner approval.

No paid asset purchases, protected viewer extraction, destructive Git operations, or unrelated changes are authorized by this workflow. Reference-only photographs are linked, not embedded or redistributed as textures. Sources and evidence must remain reproducible and attributed.

## Evidence and publication

Passed models are original photo-informed art studies. They are not photogrammetry, measured specimens or certified identification aids. Owner acceptance of the earlier three models is recorded separately; `agent_qa_pass` denotes this authorized independent QA workflow.

The browser check uses the existing built gallery and identifies the original model's bundled URL by its exact bytes, then substitutes the draft GLB for that one request. It tests actual rendering and Play/Pause in desktop and mobile viewports. Catalog captions in these fixture screenshots still describe the baseline entry; they are not metadata for the draft. No production file changes are made by the fixture.

Sources and GLBs contain packed textures. Optional PNG authoring caches need not be distributed separately; run `generate.py` without `--reuse-textures` to regenerate them. `fin_weights.py` anchors fin roots to the same spine deformation as the body, feathering independent motion toward distal membranes. `finish.py` validates this anchor rule, temporarily flattens skinned meshes and repairs closed-cap UVs/triangulation for portable tangent export.

`complete_item.py` seals a visually inspected source only when its current artifact hash, zero-error/zero-warning glTF validation, real animation tests, desktop/mobile browser receipts and the 79-file preservation guard agree. Render previews and head details are reviewed separately from these deterministic checks.

## Live promotion

On 2026-11-15 the owner additionally authorized replacing the corresponding live catalog entries and pushing each passing batch to main. `models/fish-realism-release/releases.json` owns the promoted set. Draft browser receipts remain historical isolated checks; release browser receipts test actual catalog paths and response hashes without substitution. Only a verified deployment and live receipt establish online availability.
