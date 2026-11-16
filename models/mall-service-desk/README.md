# Mall Service Desk

Original decorative service counter and sign for the owner's mall asset library. Jade panels, walnut worktops, champagne-brass detailing, an open staff side and a lower guest-counter section. No functional service workflow or accessibility certification is implied.

## Files and reproduction

- Real editable Blender source: sources/mall-service-desk.blend
- Standalone glTF 2.0 export: exports/mall-service-desk.glb
- Rendered preview: previews/mall-service-desk.webp
- Measurements and source checks: reports/assets.json and reports/sources.json

Authored with Blender 4.0.2, Ubuntu ARM64, CPU Cycles. Deterministic geometry, no random seed or external textures/models/fonts; labels use bundled Bfont. From the repository root:

    blender --background --python models/mall-service-desk/generate.py
    blender --background --python models/mall-service-desk/inspect_sources.py
    python3 models/mall-service-desk/prepare_previews.py
    node models/mall-service-desk/validate.mjs
    npm test
    npm run build
    node scripts/test-mall-service-desk.mjs

Preview conversion requires Pillow; validation uses the repository Node dependencies. Website builds use checked-in assets and do not execute Blender. Render pixels may vary across versions/hardware. Measured GLB: 2.880 × 1.870 × 0.961 m (X/Y/Z), 7,832 triangles, 245,748 bytes, five material primitives. Origin is floor centre, Blender +Z/glTF +Y up; front is Blender +Y/glTF -Z.

Edit SERVICE and HOW CAN WE HELP? text in the named FONT source objects or generator. GLB text is mesh geometry, not a runtime editable widget. Studio camera, lighting and ground stay out of the export. After source design changes, use the generator as the reproducible source of truth and regenerate/validate metadata hashes and previews.

## Rights

Original asset; reuse in the owner's projects is authorized. Public redistribution terms have not been specified. Gallery downloads remain disabled; interactive viewing still serves GLB bytes. No CC0/MIT artwork license, mall endorsement or fabrication suitability is implied.

See verification.md for historical checks and limits. The 2026-11-15 topology repair is documented in [the campaign report](../../docs/model-qa/degenerate-repairs/mall-service-desk/README.md). The current saved source was verified in Blender 5.1.2; the original authoring version was 4.0.2.

## Topology repair (2026-11-15)

Six reviewed meshes and all editable text have an idempotent, non-destructive cleanup modifier. The saved source retains all 37 authored parts. The delivered GLB preserves the original vertex/normal/material bytes and removes only reviewed triangle indices: 172 exact-zero triangles and 20 source precision residues. Unused buffer capacity is retained, so byte size is unchanged. Existing previews remain valid.

Run the complete fresh source/export regression without rendering:

    blender --background --python models/mall-service-desk/test_degenerate_cleanup.py

Saved Object-root source staging is owned by `scripts/repair-static-blender-source.py`; pass this folder's reviewed `generate.py` with `--generator`. It requires a distinct output directory and original source SHA. The mall essentials entry point delegates to the same driver and retains its existing CLI. Re-exporting with a newer Blender may repack vertices/normals; compare the actual exported geometry rather than requiring legacy binary identity.
