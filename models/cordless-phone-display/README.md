# Cordless Phone Display

Original, brand-neutral static retail model for GJH Virtual Mall store **S17**, priority **P1**. Existing category: **Equipment**. Status: draft / **NEEDS REVIEW**, pending manager art review. No external geometry, models, images, textures, fonts, logos or product packaging. Numeric keypad legends use original seven-segment geometry; the LCD and price card are blank.

The display includes a slightly rear-leaning cordless landline handset, twelve keypad buttons, navigation control, earpiece slots, microphone details and antenna stub. Its charging base has a seated cradle, page button, indicator and rear socket details. An empty price-card holder sits beside the phone on a low plinth.

Measured exported size is **0.30000001 × 0.29072919 × 0.22000000 m**, in width, height, depth order. The plinth top is 0.04800000 m above the floor. The source retains **104 editable mesh parts**. The GLB batches these into **3 meshes / 3 primitives / 3 shared opaque materials**, with **11,104 triangles**, **14,530 vertices**, **418,380 bytes**, no textures and no animation. Camera, lights and studio floor are excluded from the GLB.

Units are metres; the origin is the floor centre of the plinth footprint. Authoring uses Blender +Z up / -Y front; export uses glTF +Y up / +Z front. The generator has no random inputs. Export bakes saved source edits in a temporary copy and preserves the original source. Independent generation in a directory containing only `generate.py` reproduced the exact GLB bytes.

From the repository root:

```sh
/opt/homebrew/bin/blender --background --python models/cordless-phone-display/generate.py
node models/cordless-phone-display/validate.mjs
/opt/homebrew/bin/blender --background --python models/cordless-phone-display/inspect_sources.py
node models/cordless-phone-display/verify_source_edit.mjs
npm run validate:assets
npm test
npm run build
node models/cordless-phone-display/verify_page.mjs
```

Append `-- --export-source --skip-render` to the generator command to export saved source edits without rebuilding geometry. The source inspection exercises a mesh and material edit on a disposable copy under `reports/source-edit/`.

`reports/assets.json`, `sources.json`, `reproducibility.json`, `khronos.json`, `browser.json` and `acceptance.json` record measured evidence and check scope. Duplicate search found no close telephone or handset model before production. Final hero/front/side/3q previews and the actual 1440 × 900 Chromium model page were visually reviewed; final check outcomes are in the acceptance report.

This is a static visual asset. Telephone, wireless and charging operation, real pricing, full 17-shop 70 × 60 m mall integration and its 200 draw-call performance budget, physical Android/iOS, WebKit and manager art approval remain unverified. Reuse in the owner's projects is authorized; public redistribution terms remain unspecified. No push or deployment is included.
