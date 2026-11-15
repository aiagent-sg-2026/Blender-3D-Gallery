# Quality checks and delivery evidence

<!-- KB-SUMMARY-START -->
Use layered acceptance: source editability, exported structure, measured geometry/materials, target-runtime behavior and observed performance. Khronos validation checks format rules; it does not certify design, readable labels, physical clearance or a usable interaction. Check finite coordinates, degeneracy, normals, bounds, role-appropriate topology, UVs, actual images, skin/clip content and resource references. Reopen a source, edit a controlled copy, re-export and independently load it when editability matters. Compare the actual tested GLB hash with the loaded artifact. Distinguish metadata-only image stubs from decoded/rendered pixels. A CLI success is not an artifact check; propagate Python exceptions to a nonzero exit. Keep failed attempts and apply justified harness corrections uniformly. Samples, desktop emulation and a single graphics backend establish only their recorded coverage. Reuse an applicable existing QA Skill after reading its current definition.
<!-- KB-SUMMARY-END -->

## Evidence layers

| Layer | Useful check | Does not establish |
| --- | --- | --- |
| Source | Reopen, inspect object ownership, edit a copy and re-export | Suitability of every authoring workflow |
| Format | [Khronos validator](https://github.com/KhronosGroup/glTF-Validator), severity counts and required extensions | Intended scale, appearance or user behavior |
| Asset | Independent bounds, topology, images, material factors and clips | Complete scene integration |
| Scene | Collision, sweep, route, camera and interaction scenarios | Every continuous path or physical certification |
| Runtime | Real loader/browser, graphics backend, failures and lifecycle | Other devices or stable frame rate everywhere |

The [Khronos production tutorial](https://github.com/KhronosGroup/Vulkan-Tutorial/blob/main/en/Advanced_glTF/Tooling_Production_Pipeline/03_validation.adoc) gives examples of structural failures. Review informational messages and warnings rather than silently weakening the validator. Compression/extension support should be checked against the specific validator and consumer versions.

## Geometry and image scope

Require watertight geometry for assets whose contract requires a closed solid. Intentional visual planes need a different rule. A manifold check does not prove that separate components do not intersect. An AABB/OBB test is not identical to a triangle or swept-volume test; record tolerances and exclusions.

Read image pixels when asserting image validity, and render them when asserting appearance. Inspect UV orientation and visible text at the intended distance. A decoder stub used in a structural Node loader must not be reported as visual acceptance.

## Reproducibility

Record source/export hashes, generator and tool versions, relevant settings, expected values and observable results. Byte hashes identify tested files; they do not promise identical bytes across exporter versions. Compare semantics when investigating a deliberate rebuild.

The existing route `3d:product-model-qa` remains a reusable QA reference; discover its active definition when using it. No new Skill is registered here. Keep source-model creation separate from website presentation and release status.

The [calibration](calibration.md) preserves an incorrect zero-start animation assumption and its correction. It does not rewrite the failed result as a pass. Unmeasured performance or extension compatibility remains unmeasured, not implicitly successful.
