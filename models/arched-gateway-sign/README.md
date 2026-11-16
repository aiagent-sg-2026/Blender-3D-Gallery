# Arched Gateway Sign

Original brand-neutral mall portal, category **Mall Fixtures**. No external assets,
textures, fonts, text or logos. Existing entrance and festival models are untouched;
candidate reconciliation is in `reports/duplicate-search.json`.

Measured export: 12 × 6 × 1.30 m (width × height × depth), floor-centred origin,
glTF Y up / front +Z. Blender source uses Z up / front -Y. Three runtime meshes,
three shared opaque materials, 5,616 triangles, 280,808 bytes. The source retains
30 independently editable mesh components. No animations or colliders.

The rectangular through passage measures 10.639999 m wide and at least 4.006 m
high across its full width and 1.30 m depth. Centre clearance is 4.102 m.
Height is rounded down to the millimetre from actual exported triangle clipping;
the walking volume has zero triangle intersections (10 μm boundary tolerance).
These are visual geometry dimensions, not building or accessibility certification.

`SIGN_Band` is a separate mesh/node, 10.90 × 0.85 × 0.28 m, with its pivot at
the band centre. `SIGN_TextAnchor` is at glTF [0, 4.575, 0.641], facing +Z.
The scene supplies text; theme the three shared frame, band and trim materials.
The graphite border and brackets are in `TRIM_Details`.

From this directory:

```sh
/opt/homebrew/bin/blender --background --python generate.py
/opt/homebrew/bin/blender --background --python generate.py -- --export-source --skip-render
/opt/homebrew/bin/blender --background --python inspect_sources.py
node validate.mjs
```

Default generation deterministically rebuilds and replaces native source/GLB.
`--export-source` preserves saved source edits. Previews are hero/front/side/3q;
PNG-to-WebP uses Pillow, quality 88, method 6. Saved-source export and a second
rebuild reproduce the delivered GLB SHA-256. Source QA reopens a disposable edit
and checks its independent GLB import; the delivered source stays unchanged.

Run repository `npm run validate:assets`, `npm test`, `npm run build`, then
`node models/arched-gateway-sign/check-page.mjs` from the repository root.
Evidence is in `reports/`; the requested 1440 × 900 page screenshot is written to
`~/Documents/MallQueue/reports/arched-gateway-sign-page.png`. Local checks do not
verify the complete 17-shop mall, physical hardware, structural safety or release.
