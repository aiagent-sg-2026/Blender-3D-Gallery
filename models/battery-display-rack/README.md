# Battery Display Rack

Original brand-neutral procedural model for GJH Virtual Mall, store **S16**, priority **P1**. Existing category: **Retail**. Status: draft / **NEEDS REVIEW**, pending manager art approval. No external geometry, textures, fonts, logos, brand text or real product packaging.

The rack has a perforated back with **192 actual through-holes**, **20 punched hanging cards** in four rows, metal peg hooks, **72 generic cells** (32 AA, 32 AAA, eight button cells), shallow transparent blister bubbles, a blank header and two open lower storage compartments. Orange, teal and violet cards distinguish cell types without readable text. The source retains **296 independently editable closed mesh parts**; vertex colours allow several generic finishes while sharing three materials.

Measured exported dimensions are **1 × 2 × 0.5 m** (width, height, depth). The GLB has **20,580 triangles**, **24,594 vertices**, **1,000,488 bytes**, **three meshes / three primitives / three shared materials**, no images and no animation. Two materials are opaque and one is alpha blended for the blister bubbles; no transmission extension is required. The source studio floor, lights and camera are excluded from export. Three asset primitives do not establish the complete mall's 200 draw-call budget.

Units are metres, with the origin at the floor centre of the full base footprint. Blender uses +Z up / -Y front; glTF uses +Y up / +Z front. The generator has no random inputs. Export bakes saved source edits in a temporary copy, batches by shared material and preserves the source. An independent clean-directory build reproduced the exact GLB bytes.

From the repository root:

```sh
/opt/homebrew/bin/blender --background --python models/battery-display-rack/generate.py
node models/battery-display-rack/validate.mjs
/opt/homebrew/bin/blender --background --python models/battery-display-rack/inspect_sources.py
node models/battery-display-rack/verify_source_edit.mjs
npm run validate:assets
npm test
npm run build
node models/battery-display-rack/verify_page.mjs
```

Append `-- --export-source --skip-render` to export the saved source without rebuilding geometry. Source inspection checks manifold solids, actual hole topology, counts, mount/card contact and floor datum; it also edits a disposable copy and re-exports it. Reproducible scratch exports in `reports/source-edit/` are ignored by Git.

The template is `../self-checkout-machine/` (source/export/preview/metadata/report layout and layered quality gate); the recently added phone display supplies the shared-material batching and browser harness pattern. `reports/duplicate-search.json` records catalog and recursive metadata identity searches, with no close match. Measured format, geometry, editability, reproducibility and browser evidence are recorded in `reports/`; final check scope is in `reports/acceptance.json`. Final hero/front/side/3q previews and the 1440 × 900 Chromium page are visually inspected as part of acceptance.

Static visual prop only. Electrical operation, real merchandising capacity, load or stability certification, full 17-shop 70 × 60 m mall integration/performance, physical Android/iOS, WebKit and manager art approval remain unverified. Public redistribution terms are unspecified; owner-project reuse is authorized. No push or deployment.
