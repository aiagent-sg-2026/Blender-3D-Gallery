# GJH-M057 Premium Wall Shelf Corner

Original procedural, editable 90-degree corner display fixture. GJH-M057 belongs to the separate GJH360 backlog, not the Gallery500 ID sequence. No official branding, logos, packaging or embedded products.

## Design interpretation

The source backlog repeats a 2.4 × 0.55 × 2.4 m outer size. This approved corner interpretation instead uses two nominal 1.2 m arms, each with 0.55 m local depth, and a measured outer **1.2 × 1.2 × 2.4 m** (width × depth × height). It does **not** satisfy the repeated 2.4 × 0.55 m outer footprint. The glTF XYZ dimensions are recorded precisely in metadata (Y is height).

Blender uses metre units, +Z up and -Y front; glTF uses +Y up and +Z front. Origin is floor centre. Three continuous L-shaped shelves, emerald cabinet panels, separate champagne-gold trims, warm-looking emissive LED strips, original baked wood/stone textures, 24 product-placement anchors (8 per row), and a separate static L-shaped collider are editable. The two independently editable front-edge header panels sit on the continuous wood canopy; their inner separation is intentional, not a missing rear wall. No mirror or simulated physical lighting certification is claimed.

## Artifacts and runtime contract

- `sources/gjh-m057-premium-wall-shelf-corner.blend`: canonical editable source.
- `exports/optimized.glb`: identical to LOD0; four explicit LOD files and `collision.glb` accompany it.
- `previews/`: five full/detail views and three additional LOD previews, actually reviewed.
- `support-manifest.json`: stable named rows, LEDs, headers, anchors and collider.
- Each header label anchor has local +Z outward and +Y up, with a 0.44 × 0.36 m safe surface. Runtime overlays sit at local Z +0.002 m.
- Shelf Inspector supports M056/M057 selection, manual LOD0–3, row highlight, LED toggle, two-face text replacement and reset. Gallery supports orbit, zoom and reset.
- Automatic LOD selection and external product loading are **not implemented**. Real Android/iOS devices were **not tested**; Chromium viewport/touch emulation is not physical-device certification.

## Verified local evidence

| LOD | Triangles | Bytes |
| --- | ---: | ---: |
| 0 | 13,680 | 1,056,536 |
| 1 | 4,944 | 469,480 |
| 2 | 2,032 | 285,952 |
| 3 | 576 | 180,092 |

- PASS `reports/assets.json`: all four LODs plus collider have zero Khronos errors/warnings; 42 semantic meshes, two embedded original PNG textures, bounded scale, stable 24 anchors, positive L-footprint checks, empty notch, supported LEDs and rear-panel spine contact.
- PASS complete label-rectangle ray tests: 9 sample points per label, diagonal and face-normal views, all four LODs. Actual browser screenshots are also inspected, not inferred from these ray tests.
- PASS `reports/sources.json`: canonical saved source opened, edited copy saved/reopened and re-exported without regeneration; canonical source remained unchanged.
- PASS `reports/catalog-preservation.json`: all 554 pre-existing model entries and collection memberships preserved; one new registration, 555 total at this baseline.
- PASS final focused asset/runtime units (11), build, Gallery at 1440/768/390 and M057 Inspector desktop/touch. Gallery final evidence is `reports/browser-front-header`; runtime evidence is `output/shelf-inspector-m057-visible` and accompanying Inspector documentation. Earlier four M056 regression scenarios also passed.
- PASS actual final 8-view Blender visual review. Runtime label readability checked independently after the correction below.

These are local checks, not a claim of successful CI or deployment. Parent release verification remains separate.

## Corrections and preserved failures

Initial exported label-up orientation failed the structural check and was corrected. A rear-corner seam was closed with an independently editable spine. The renderer lacks OpenImageDenoiser: that failed run is preserved; final previews use supported Cycles 128 samples without denoising. An exact concave-boundary ray was replaced with explicit inside/outside samples after documenting float32 boundary ambiguity, without weakening other footprint checks.

The original rear-positioned 1 m runtime labels were visually occluded despite interaction tests passing. A first anchor-only correction failed the new face-normal visibility test and was rejected. Final front-edge panels, trims and 0.44 m label regions were regenerated across every LOD and source; all eight previews were regenerated. The earlier screenshots and failed logs remain evidence, not accepted results. `reports/header-binary-preservation.json` describes only the rejected intermediate anchor-only experiment, not the final front-header geometry.

## Reproduce

Run the existing Blender 4.x environment with `-b -P generate.py` (from this asset directory or using its repository-relative path). `--skip-render` skips all previews, useful only when image evidence is already valid. Then run `node models/gjh-m057-premium-wall-shelf-corner/validate.mjs`, the Blender `inspect_sources.py` script and `verify_source_edit.mjs`. Focused checks are `node --test tests/gjh-m057.test.mjs` and, after the normal repository build, `node scripts/test-gjh-m057-browser.mjs`. Use the repository's Shelf Inspector browser script for runtime evidence. Do not overwrite prior failed evidence when rerunning.

See `LICENSE.md` for rights limits. No structural load, safety, accessibility, photometric or official-brand certification is made.
