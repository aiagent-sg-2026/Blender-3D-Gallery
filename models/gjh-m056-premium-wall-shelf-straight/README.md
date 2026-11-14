# GJH-M056 Premium Wall Shelf Straight

GJH360 identity M056 is independent of Gallery500 IDs. Dimensions2.4m wide ×0.55m deep ×2.4m high. Source Blender Zup/-Yfront; GLTF Yup/+Zfront; floor-centre origin. User-supplied visual concept informed emerald lacquer, champagne gold, warm wood, dark stone base and warm-looking LEDs. No NewMoon logo, Since1999 text, packaging, plants or products copied or embedded. Blank brand-header panel is independently editable.

## Deliverables and contracts
- sources/gjh-m056-premium-wall-shelf-straight.blend and generate.py.
- exports/lod0.glb through lod3.glb; optimized.glb is byte-identical LOD0. Dedicated exports/collision.glb is a conservative2.4×2.4×0.55m box, not part of the rendered model. Main collision node is a descriptor.
- Stable cabinet, trim, brand_header, shelf_1–3, LED_1–3, LED_header/LED_base, price_rail_1–3. Header LED has a connected wood canopy; shelf LEDs touch each shelf underside, verified from actual GLB bounds.
- support-manifest.json declares named parts, LOD paths and3rows of8external-product anchors. Each row accepts1–8 external items; currently no product URLs or baked products.
- Wood/stone appearances are original baked256pxPNG textures embedded in every GLB, not Blender-only procedural shading. LED emission is warm3000K-looking, not photometric certification or a promise of physically illuminating neighbouring objects in WebGL.

## Measured evidence
- LOD0:8700triangles,710044bytes; LOD1:3132triangles,338236bytes; LOD2:1276triangles,223232bytes; LOD3:348triangles,156160bytes. Each29meshes,2textures. These are measured counts, not assumed percentage reductions.
- PASS actual Khronos validation for4LODs and collider:0errors/0warnings. Dimensions, unique/stable names,24identical anchor world positions and shelf support heights checked. reports/assets.json.
- PASS saved blend edited-copy reopen/reexport, canonical source unchanged. reports/sources.json and verify-source-supported-led.log.
- PASS3focused tests and build. reports/focused-test.log/build.log.
- PASS8render previews visually inspected by parent, including correction of initially unsupported header light strip. First structural report retained as pre-support-assets.json; that report did not claim visual approval.
- PASS Gallery1440/768/390 Chromium viewport cases:actualGLBhash, WebGL drawing with embedded texture loads, orbit/zoom/exactreset, repeatedclose/reopen, no page/request errors or overflow. reports/browser/results.json and screenshots.
- PASS all489existing asset objects and collections preserved; one independent registration added. reports/catalog-preservation.json.

## Explicit limits
PhysicalAndroid/iOS NOT TESTED. NOT DEPLOYED. Gallery provides model inspection/orbit/zoom. The separate ?page=shelf-inspector demo implements shelf highlight, emissive LED toggling, runtime text header and manual LOD0–3 switching. Its focused browser evidence is documented in docs/shelf-inspector-qa.md; asset validation alone does not establish runtime correctness. Automatic runtime LOD and external product loading are NOT implemented by these files. Collider is a coarse proxy, not a structural/safety simulation. No official brand endorsement or accessibility/load/lighting certification.

## Reproduce
Blender4.0.2 --background --python models/gjh-m056-premium-wall-shelf-straight/generate.py
Blender4.0.2 --background --python models/gjh-m056-premium-wall-shelf-straight/inspect_sources.py
node models/gjh-m056-premium-wall-shelf-straight/validate.mjs
node models/gjh-m056-premium-wall-shelf-straight/verify_source_edit.mjs
node --test tests/gjh-m056.test.mjs
npm run build
node scripts/test-gjh-m056-browser.mjs
