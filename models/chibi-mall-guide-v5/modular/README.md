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

## Update: Hunyuan3D-2.1 hair (shape-only), same day
- Second GPU trial (Runpod secure RTX 4090, about 15 minutes, roughly 0.25 USD; pod terminated, `list-pods` empty): `tencent/Hunyuan3D-2.1` shape generation only (no texture stage), 2 hair references x seeds 1-3. The `hair_3q` references give a complete bob with a scalloped fringe and a head cavity (`candidates/hunyuan-hair-candidates.png`, right two columns); the `hair_front` ones came out as small half-width shells and were not used.
- `assemble.py` now accepts `HAIR=hy_hair_3q_s1` (decimates to 30k triangles, one solid chestnut material `HAIR_TARGET=7A4A32`, non-uniform fit with `HAIR_FIT=1 HAIR_W=1.3 HAIR_D=1.3 HAIR_H=1.0`, `HAIR_UP_X=0 HAIR_DROP_WIDE=0`, `CAP_DZ=0 CAP_DY=0`). Result: `assembled-hunyuan-hair/assembled-three.png`. The imported object uses quaternion rotation, so `rotation_mode='XYZ'` is set before any rotation.
- Hair is clearly better than the TRELLIS hair (no halo loops, no scalp patches). Remaining: mesh is untextured (flat colour, no strand shading); cap sits on top without a fitted tilt; shoes, A-pose arms and the floating sign are unchanged; no rig, clips, validator run or independent review yet.
- Licence: Hunyuan3D 2.1 community licence excludes the EU, UK and South Korea, and its source files carry a "non-commercial" header; do not publish this hair until the owner has read `LICENSE` in the Hunyuan3D-2.1 repository. TRELLIS.2 (MIT) could not be tried: it needs the gated `facebook/dinov3-vitl16-pretrain-lvd1689m` encoder (HTTP 401 without a Hugging Face token that has accepted Meta's licence).
