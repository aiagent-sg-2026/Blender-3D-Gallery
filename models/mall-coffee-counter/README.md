# Mall Coffee Counter

Original Shopping Mall017, not global500 ID017. Independently editable customer handoff ledge, staff worktop, hollow storage, shelves, front panels/ribs and outward-opening staff-side cabinet door. No appliances or branding. Overall1.84m width ×1.14m height ×0.924m closed depth; staff worktop0.97m high. Metres; Blender Zup/-Yfront and GLTF Yup/+Zfront. No plumbing/electrical/hygiene/load/accessibility certification.

## Local evidence
- PASS real GLB:3532triangles,193124bytes,29meshes, no textures, Khronos0errors0warnings. See reports/assets.json.
- PASS60 independently reset/play sampled poses; actual105degree midpoint, exactclosed reset; four cabinet leaf/handle meshes vs21fixed cabinet/shelf/top meshes conservativeOBB sweep. Designed hinge joints explicitly excluded.
- PASS saved source edit/reopen/reexport changes DOOR_Handle mesh and roughness without regeneration; canonical source unchanged. reports/sources.json,verify-source.log.
- PASS focused3tests and build. reports/focused-test.log,build.log.
- PASS Gallery actualGLBhash, orbit/zoom/exactreset, repeatedclose/reopen, no errors/overflow:1440/768/390 Chromium viewport cases. reports/browser/results.json.
- PASS isolated Three.js animation visiblepose change and exactreset. reports/animation-browser/results.json. Existing Gallery has static orbit/zoom controls, not animation controls.
- PASS all488existingassets and every existing collection unchanged. reports/catalog-preservation.json.
- PASS actual five Blender previews plus Gallery and staff-side animation browser screenshots inspected. Physical Android/iOS NOT TESTED. NOT DEPLOYED.

## Reproduction
Blender4.0.2 --background --python models/mall-coffee-counter/generate.py
Blender4.0.2 --background --python models/mall-coffee-counter/inspect_sources.py
node models/mall-coffee-counter/validate.mjs
node models/mall-coffee-counter/verify_source_edit.mjs
node --test tests/mall-coffee-counter.test.mjs
npm run build
node scripts/test-mall-coffee-counter-browser.mjs
node scripts/test-mall-coffee-counter-animation.mjs

## Visual review corrections
Initial rear-open render cropped the open door; only that camera framing was corrected and rerendered. Initial animation camera viewed the customer face and obscured most of the door; changed to staff-side view and reran the same animation checks with unchanged assertions. GLB remained byte-identical.
