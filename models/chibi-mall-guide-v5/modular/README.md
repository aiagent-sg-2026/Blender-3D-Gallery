# Modular Mall Guide (TRELLIS parts), status 2026-11-15

Goal: customisable guide built from four separately reconstructed parts (body, hair, cap, sign) instead of one fused mesh.

## What exists
- `ref/`: part reference images (Codex imagegen, AI concept images, rights not cleared) and their 887 px crops (`ref/crops/`).
- 16 TRELLIS candidates (4 parts x seeds 1-4), reconstructed on one Runpod RTX 4090 (secure cloud, 0.89 USD/h, about 25 minutes of GPU); contact sheets in `candidates/`. Candidate GLBs are not committed (rights).
- `assemble.py`: scales, orients and places body_s3, hair_s1, cap_s2, sign_s3 as four separate meshes (1.00 m, feet on z=0), recolours the hair texture, drops hair loose parts that form a halo, exports `assembled.glb`. `inspect_part.py`, `axis_views.py`, `hair_comps.py`, `sheet.py`, `fixmat.py` are helpers.
- `assembled/`: Three.js render of the assembly (`assembled-three.png`), measurements (`assemble-report.json`).

## Chosen candidates and why
body_s3 (closed smile like the sheet; shoes mottled), cap_s2 (pillbox with brass pin, clean), sign_s3 (rounded board with green right arrow, clean), hair_s1 (only hair with bangs above the eyes after scaling).

## Known defects (own reading, not independently reviewed)
- Hair is the weak part: TRELLIS made wig shells with thin side loops. After deleting the worst loops, small curved fragments remain at both sides and small scalp patches show at the top; the hair is much darker than the sheet's chestnut (texture remap not strong enough).
- Shoes are mottled; the A-pose arms are away from the body; the sign floats beside the right hand (not attached to the hand, no rig yet).
- Not done: rig, clips, blink, validator run, silhouette overlap, independent review.
