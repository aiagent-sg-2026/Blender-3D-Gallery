# Findings and recommended order

Follow-up on the same date: the three queue models were repaired and re-exported in the [axis-cap repair](../queue-stanchions-degenerate-fix-2026-11-15/README.md). This file and its measurements remain the original pre-repair snapshot; the other assets were not changed by that repair.

This read-only audit covers 62 Shopping Mall catalog exports plus five supporting/local artifacts: three mall characters, the visitor LOD and an uncatalogued local chibi visitor. All 67 GLBs passed Khronos validation with zero errors and warnings. That confirms format conformance, not geometric cleanliness or release acceptance. See the [full report](README.md) and [machine-readable results](summary.json).

## 1. Clean confirmed degenerate geometry first

Eighteen primary mall models contain triangles whose computed area is exactly zero in the raw GLB measurement. The largest counts are the short/long queue assemblies (960 each), single queue post (480), trash bin (470) and directory kiosk (394). Source geometry, Blender re-import and independent GLB counts agree for those five examples. Remaining per-object details and near-zero thresholds stay in the raw reports; different arithmetic/evaluation paths can classify tiny triangles differently and their counts must not be added together.

For the queue family the [generator](../../../models/mall-queue-stanchions/generate.py) gives a specific cause: `lathe()` emits a complete 48-vertex ring even when a profile radius is zero. Adjacent quads then contain coincident axis vertices. Five two-ended profiles account for `5 × 2 × 48 = 480` zero-area triangles per post; each two-post assembly doubles the count. This source explanation matches all three measured queue assets. Do not assume every other asset's degeneracy has the same cause without inspecting its generator.

Recommended next change: repair axis endpoints/caps in the queue generator, rebuild only the three queue exports, and verify degenerate counts, dimensions, pivots, materials and actual loader behavior. No generator, source, export or thumbnail was changed by this audit. The full priority table in [README](README.md#priority-exact-zero-area-delivery-triangles) lists the other 15 models for separate review.

## 2. Establish density goals by material and use

Eleven primary exports have image resources; all observed delivery image/material mappings were measured successfully. Fifty-one have no image textures, so actual image density is N_A. A hypothetical 1024-pixel UV reference is not an actual texture measurement or a reason to add textures.

For example, the floor tile's 512² image measured about 859.555 px/m and the advertising screen's 1024×576 artwork about 852.941 px/m. The seven premium shelf assets and the ceiling/atrium materials have their own image resolutions and mappings; consult [texture-density.csv](texture-density.csv) before comparing them. Asset ranges may combine base-color/data maps and different surface roles.

There is no approved global px/m target in the current contract. Do not label these measurements compliant/noncompliant, normalize every image to one value, or rescale existing UVs automatically. Define a small set of targets for floor, storefront/wood and close-up signage/packaging, with exceptions for viewing distance and text legibility, before making changes.

### Source n-gon measurement limitation

Five M057 source objects initially failed the independent density cross-check. Each contains two concave n-gons. Texel Density Checker 2026.1.1 computes polygon geometry area using a vertex-zero triangle fan; in these L-shaped cases that overcounts the area. For example, the cabinet base's fan area is 3.586867 m² versus the evaluated polygon area of 3.164363 m².

The [temporary-triangulation diagnostic](source-density-ngon-diagnostic.json) triangulated copies, without saving source or export. All five operator results then agreed with the independent oracle. The cabinet base measured 258.204 px/m, close to the separately imported GLB's 258.206 px/m; the source's original direct operator value was 245.574. The original five disagreement records remain in [texture-density.csv](texture-density.csv). This is a measurement-method limitation, not evidence that those UVs should be rescaled. Use a disposable triangulated representation for this case and retain the original authoring polygons.

## 3. Keep topology and source limitations explicit

- Source text, leaves, visual planes and coincident decorative parts can legitimately have boundary edges. Raw Print Toolbox observations and a disposable position-weld diagnostic are separate from a role-specific defect decision. Printing overhang/thickness rules are not GLB acceptance gates.
- Three source files use a newer major/minor file format than the installed Blender 5.1 reader. The delivered GLBs were checked independently, but lossless authoring-source fidelity requires matching-version review. Source file-format subversions are not application patch numbers.
- Six authoring roots are Collections, whereas delivery roots are Empty objects. The first object-only source lookup was insufficient; exact Collection membership was subsequently scanned. Both the initial gaps and [source supplements](source-supplements/execution.json) are retained. This is a scanner-boundary correction, not a source-asset defect.
- The Blender importer generated an 80-triangle bone-display Icosphere for the visitor and LOD. The [installed importer provenance](scanner-revisions/importer-boundary.json) identifies it as a UI helper. Actor rechecks suppressed bone shapes, retained skinning and reconciled delivered triangle counts with raw GLB data. [Original results and the correction](scanner-revisions/rechecks.json) are retained; no asset triangles were deleted.

Visual quality, UV legibility, shader appearance, animated poses, collision, device FPS and publication approval are outside this audit. Physical-device runs are not part of this report.

## Reuse and evidence

The applicable `3d:product-model-qa` v1.0.1 procedure supplied structural/resource and evidence rules. Its complete visual/browser/release procedure was not claimed. Existing installed P0 operator contracts, source/GLB separation and original-file hashes were reused. Known-value fixtures independently require 64/128 px/m on two material assignments, N_A for an untextured patch, the expected boundary count, and Collection-source/Empty-delivery mapping. See [current calibration](scanner-calibration-current.json) and [final verification](verification.json).
