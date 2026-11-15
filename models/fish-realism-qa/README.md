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

## Posed fin-surface contact

A later oblique/rest-geometry audit found that the earlier fixed paired-pelvic root coordinate lay outside the curved body even though its bone weights followed the spine. `fin_attachment.py` now owns a small embedded ventrolateral root curve. Verification measures signed distance from actual evaluated fin roots to the actual posed body surface at five phases, in both source and reimported GLB. Tubular sensory-ray bases must straddle the skin; a caudal leading edge must intersect the peduncle. This complements weight continuity rather than treating correct weights as sufficient contact evidence. Earlier playback receipts remain historical and do not establish this later criterion.

The routed architecture instruction module was absent in this checkout; scoped repository contracts and observable source/export/browser evidence were used.

On macOS hosts where bundled Chromium/SwiftShader screenshot preparation stalls, set `FISH_CHROME_PATH` to an installed Chrome executable and `FISH_WEBGL_BACKEND=metal`. The optional runtime is recorded in browser receipts; all existing assertions still apply. This is a QA environment choice, not a physical-device performance claim.

Invoke Blender with `--python-exit-code 1` before `--python SCRIPT` so failed Python assertions stop shell automation. Newly written receipts and source/artifact hashes remain mandatory.
