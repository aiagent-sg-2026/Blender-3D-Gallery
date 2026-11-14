# Mall Shoe and Bag Rack

Original initial Shopping Mall list015 asset, not global500 ID015. Distinct from the existing prayer-room shoe cubby and household shoe cabinet: three sloped retail shoe shelves with retaining lips, an adjacent two-peg handbag bay, and a pull-out inventory drawer. Independent meshes and materials, real metre units, floor origin, Blender +Z/-Y front and glTF +Y/+Z front. Empty display surfaces support reusable scene assembly; no copied merchandise or load-rating claims.

## Local PASS
5,088 triangles;264,228GLB bytes;36mesh parts;4materials;1DrawerOpenClose clip. Fixed budgets8,000triangles/800,000bytes/80mesh parts. Actual five rendered views and browser preview pixels inspected. Khronos0errors/0warnings. Source copy has edited vertices/material roughness, was saved/reopened/reexported, canonical source unchanged. Closed dimensions1.2m wide,1.675m high,0.492m deep including pull. Drawer opens0.22m and resets. All60frames rechecked with live animation, full drawer bounds clear underside of cap.

Chromium1440/768/390: real GLB hash, WebGL draw, orbit, zoom, exact reset, close/reopen cycles, no errors. Isolated Three.js animation pixels change and reset exactly. No gallery animation playback UI or physical Android/iOS test claimed. Build and focused tests PASS. Release pending existing CI/Pages, no changed gate.

## Reproduce
Run Blender4.0.2 background with --python generate.py, then --python inspect_sources.py (paths relative to this asset). Run node models/mall-shoe-bag-rack/validate.mjs, node models/mall-shoe-bag-rack/verify_source_edit.mjs, node --test tests/mall-shoe-bag-rack.test.mjs, npm run build, node scripts/test-mall-shoe-bag-rack-browser.mjs and node scripts/test-mall-shoe-bag-rack-animation.mjs.

## Correction evidence
Initial focused catalog tests caught a missing required display.previewRotationY metadata field; added explicit0, validator unchanged. Independent review found clearance loop was still paused after LoopOnce end; now resets its action before sweep and asserts actual midpoint travel. Clearance checks full drawer including front/side walls, not only the bottom. Initial logs retained. Equivalent paused-loop issue in glass showcase validator corrected and reverified without modifying either GLB. All485 existing catalog entries and collection memberships retained; rack receives independent mall-footwear-displays collection (total486 entries). No500-completion claim.
