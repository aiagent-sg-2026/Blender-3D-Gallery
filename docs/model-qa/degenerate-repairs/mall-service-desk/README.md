# Mall service desk topology repair

Status: PASS for static source/GLB topology repair. The immutable campaign baseline had 172 exact-zero triangles; delivery has zero, with 7,832 total triangles (8,024 before). Twenty additional source precision residues meet the 0.1 micrometre altitude and quantized-collinearity checks. They are recorded separately from exact-zero triangles.

The saved source preserves all 37 editable parts, authored mesh/text/curve data, materials, transforms, collection memberships and scene semantics. Non-destructive cleanup targets six reviewed meshes and all editable text. Reopening the saved source and reimporting the actual delivery both report zero degenerate triangles. The complete fresh generator regression saves a source with studio configuration and validates its real GLB; preview rendering is skipped.

The delivered GLB is reconstructed from the original triangle indices using the staged native cleanup as a geometry oracle. Vertex positions, normals, material definitions, bounds and root transforms remain unchanged. Byte length remains 245,748 because original buffer capacity and attributes are retained. Existing preview images remain applicable.

- [Delivery comparison](delivery-comparison.json), [index repair](index-repair.json)
- [Native source receipt](source-repair.json), [native export comparison](source-geometry-comparison.json), [delivery reimport](delivery-reimport.json)
- [Failing pre-fix regression](regression-before.log), [fresh generator regression](generator-regression.log)
- [Shared staging driver compatibility](shared-driver-compatibility.json): the essentials CLI now delegates to the common reviewed Object-root staging driver without changing its arguments. Native trash-bin staging and comparison passed.
- [Verification](verification.json), [browser results](browser-results.json)

681 tests and the production build passed. All six discovery/Viewer browser cases passed at 1440/768/390 pixels. Actual consumed GLB hashes were checked, along with keyboard orbit/zoom/reset, reload, close/reopen, focus restoration and stopped render loop. The desktop Viewer capture was visually inspected: both counter heights, fluting, plaque and raised SERVICE sign are intact. These are Chromium/SwiftShader checks; physical devices, FPS and deployment are outside this result.
