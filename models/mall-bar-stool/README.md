# Mall Bar Stool

Original Shopping Mall019, not global500 ID019. Editable low-back upholstered seat and backrest swivel90degrees around vertical axis; fixed column, base and circular footrest. Seat top0.778m; overall0.48m wide/deep and1.04m tall. Metres; Blender Zup/-Yfront and GLTF Yup/+Zfront. No safety/load/accessibility certification.

## Local evidence
- PASS real GLB:5544triangles,272972bytes,15meshes, no textures, Khronos0errors0warnings. See reports/assets.json.
- PASS animation:60independently reset/play sampled poses; actual90degree midpoint, exactclosed reset;6upper meshes vs9stationary meshes OBB sweep and fixed matrices unchanged.
- PASS saved source edit/reopen/reexport changes BACK_Cushion mesh and roughness without regeneration; canonical source unchanged. reports/sources.json,verify-source.log.
- PASS focused3tests and build. reports/focused-test.log,build.log.
- PASS Gallery actualGLBhash, orbit/zoom/exactreset, repeatedclose/reopen, no errors/overflow:1440/768/390 Chromium viewport cases. reports/browser/results.json.
- PASS isolated Three.js animation visiblepose change and exactreset. reports/animation-browser/results.json. Existing Gallery has static orbit/zoom controls, not animation controls.
- PASS all487existingasset objects and every existing collection unchanged. reports/catalog-preservation.json.
- PASS actual five Blender views and desktop/mobile-width Gallery plus swivel browser screenshots inspected. Physical Android/iOS NOT TESTED. NOT DEPLOYED.

## Reproduction
Blender4.0.2 --background --python models/mall-bar-stool/generate.py
Blender4.0.2 --background --python models/mall-bar-stool/inspect_sources.py
node models/mall-bar-stool/validate.mjs
node models/mall-bar-stool/verify_source_edit.mjs
node --test tests/mall-bar-stool.test.mjs
npm run build
node scripts/test-mall-bar-stool-browser.mjs
node scripts/test-mall-bar-stool-animation.mjs
