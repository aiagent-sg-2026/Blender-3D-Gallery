# Floor-Stand TV

Original procedural retail television for S13/S14, priority P1. Existing category:
Equipment. Draft; local evidence is recorded separately from manager approval.
The opaque blank panel, slim aluminium column, graphite weighted-base form,
four floor pads, rear attachment rails, vents and cable cover use three shared
materials and six functional meshes. No brands, readable text or external assets.

## Rebuild and check

Run from this folder with Blender 5.2.3 LTS:

```sh
/opt/homebrew/bin/blender --background --python-exit-code 1 --python generate.py
node validate.mjs
/opt/homebrew/bin/blender --background --python-exit-code 1 --python inspect_sources.py
node verify_source_edit.mjs
```

Append `-- --skip-render` for geometry only. Append `-- --export-source` to
export the saved `.blend` without rebuilding and discarding manual edits. The
optional `--views=front,side` argument selects previews to rerender. The
controlled edit proof uses the system temporary directory, leaving the source
and delivery GLB unchanged. Source objects remain editable by functional module;
joined subparts can be selected as connected vertex islands.

Run the repository gates from the repository root:

```sh
npm run validate:assets
npm test
npm run build
node models/tv-floor-stand/verify_page.mjs
```

`reports/assets.json` measures the actual GLB: approximately 1.23 m wide,
1.83 m tall and 0.52 m deep. The panel housing is approximately 1.23 x 0.72 m.
The asset root is at the centre of the floor footprint. Authoring uses Blender
+Z up/front -Y, exporting glTF +Y up/front +Z, in metres. Studio objects are
excluded from the export. There are no textures, animations or decoder extensions.

## Reuse and limits

Before creation, 581 catalog assets and 624 metadata files were searched.
No close floor-stand TV was found. `tv-wall-mounted` was **NOT FOUND**; its
construction could not be reused or visually matched. `build_panel` implements
original geometry at the requested dimensions and can be reused by a future
wall variant. The existing desktop monitor and wall advertising screen have
different mounts and uses; neither was modified.

The base depicts a weighted enclosure; no mass, stability or load claim is made.
The screen is a static visual surface. Full mall assembly performance, physical
devices, WebKit and manager art approval are unverified. See
`reports/acceptance.json` for executed checks and `reports/khronos.json` for the
format validator result. Local Chromium evidence is scoped to the exported GLB.
