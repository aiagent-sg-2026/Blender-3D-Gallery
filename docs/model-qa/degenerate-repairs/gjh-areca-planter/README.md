# Areca planter topology repair

Status: PASS. Raw GLB Float64 exact-zero triangles: 100 → 0. The native Float32 source counted 172 before; these are different arithmetic scopes, not additive counts. Native source reopen, canonical GLB re-import and fresh generation/export/re-import now report zero. All 213 authored parts, including 198 palm leaflets, remain editable.

The source was already Blender 5.2.3 LTS. An official checksum/signature-verified matching binary was used without replacing the installed 5.1.2. A real negative control confirms that the generator rejects 5.1.2 before writing saved sources.

Preserving the original triangulation required a derived FACE/BOOLEAN attribute: 63 alternate diagonals among 864 ceramic faces. Original vertex/polygon/curve/UV/material and scene data remain intact. The selector is recomputed from native source loop triangles and requires unmodified source topology; new modifier stacks need review. A universal Fixed setting changed genuine cap diagonals. Welding coincident poles also shifted Float32 heights and introduced 11–119 nm slivers. Both failures were rejected; ceramic cleanup now retains loop diagonals and original vertex positions without a weld.

The source profile defines analytic zero-radius radial poles. The 125 positive-area remnants all lie on the ceramic cap planes at source heights 0.055/0.54 m, include a nominal pole (maximum measured radius 1.93e-16 m), and have perpendicular line error ≤ 1.427e-10 m. A separately opted-in 2e-10 m (0.2 nm) analytic calibration handles these rotated lines; 1 um grid collinearity is inappropriate for them. The default criteria remain unchanged. Actual frozen fixtures refuse removal without opt-in and protect both a real 1 nm face and the existing 10 um face.

The native export filters calibrated indices through the repository Node tools and refuses residues outside the ceramic material. A source/GLB hash-bound review then reconstructs canonical indices from the original delivery. Canonical positions, normals, materials, bounds and pivots are unchanged. Delivery has 4,935 triangles (5,160 before), remains 119,760 bytes and retains original attribute capacity. Existing previews remain applicable.

- [Native source preservation and derived attribute](source-repair.json), [strict source comparison](source-geometry-comparison.json)
- [Independent analytic-pole review](analytic-pole-review.json), [unchanged-source export control](unchanged-source-control.json)
- [Rejected fixed diagonals](rejected-fixed-diagonals.json), [rejected weld shifts](rejected-weld-shift.json)
- [Index repair](index-repair.json), [canonical comparison](delivery-comparison.json), [actual re-import](delivery-reimport.json)
- [Failing pre-fix regression](regression-before.log), [tool positive/negative controls](tool-controls.log)
- [Fresh native generator/export/import](generator-regression.log), [prior shared native regressions](shared-generators.log), [prior waste regression](shared-waste-generator.log)
- [Compatible toolchain](toolchain.json), [downgrade refusal](version-downgrade-guard.json)
- [Verification](verification.json), [browser results](browser-results.json)

693 tests and the build passed. All eight prior repaired assets' native generator regressions passed after the shared changes. All nine bench/planter browser cases passed at 1440/768/390, including consumed SHA, discovery, orbit/zoom/reset/reload, close/reopen, focus and render-loop cleanup. The actual desktop Viewer image was inspected: ceramic flutes, brass rings, soil, stems and leaflets are intact. No phone/FPS, deployment or broader model certification is claimed.
