# Shopping Mall geometry and texel-density QA

Read-only snapshot: 2026-11-15, Asia/Singapore. This is a structural/numeric audit, not release or visual acceptance.

Start with [prioritized findings and causes](findings.md).

Scanned 62 Shopping Mall catalog GLBs and 5 supporting/local artifacts. Revision: `3f5c663bc11026ca58f79247f3c253172ebd19b5`.

Format errors: 0 assets. Textured primary models: 11; image-free primary models: 51.
Primary models with exact zero-area triangles at the default pose: 18. Primary density measurement gaps: 0.
Original-input preservation: PASS, 509 files checked.

## Interpretation

- Actual density uses decoded image resolution and the assigned material faces in exported geometry. Texel Density Checker 2026.1.1 is checked against a separate world/UV-area oracle. Duplicate image-node bindings with the same mapping are collapsed in the CSV.
- No approved px/m target exists in the current asset contract. Measured ranges are observations, not density PASS/FAIL. Images absent from a GLB mean actual image density is N_A; 1024-based UV references in raw evidence are explicitly hypothetical.
- An asset range can span different images, resolutions, material channels and surface roles. Compare like-for-like image/material usage before setting a target; a broad range alone is not a demonstrated defect.
- 5 original source density probes disagree with the independent oracle; original states remain in the CSV. Inspect any separate diagnostics before trusting those source values.
- 3D Print Toolbox 1.5.0 solid/degenerate reports are recorded per mesh. Its 0.1 mm small-element threshold is a diagnostic, not proof that a small font/detail is defective. Exact zero-area delivered triangles are listed separately.
- UV/hard-normal seams split GLB vertices. Raw and position-welded topology observations are separate. Welding at 1e-7 m affects disposable diagnostics only and can merge coincident intentional parts; boundary counts require role review, especially text, leaves and visual planes.
- Source curves/modifiers are evaluated with Blender 5.1.2; delivery is independently validated from original GLB bytes, then imported separately. Rootless character sources may contain staging/variants; their counts are not asset-equivalence proof.
- Source file-version tuples include a file-format subversion, not an application patch number. A source with a newer major/minor file format than Blender 5.1 needs matching-version authoring review; this audit does not assert lossless source fidelity.
- 5 MiB, 100k triangles and 2048 image dimensions are proposed review targets from docs/assets.md, not frozen per-asset acceptance gates.
- Sources/exports are not saved or repaired. Preview images, UV readability, shader appearance, animation states, collision, browsers, FPS, rights approval and physical devices are NOT_RUN in this report. Other QA campaigns and publication statuses are unchanged.

## Evidence

- [Complete records](summary.json), [asset CSV](assets.csv), [per-object geometry CSV](geometry.csv), [texture density CSV](texture-density.csv).
- [Input inventory and hashes](inventory.json), [execution](execution.json), [original-file preservation](preservation.json).
- [Current Collection/Empty calibration](scanner-calibration-current.json).
- [Final verification](verification.json).
- [Scanner revision and actor rechecks](scanner-revisions/rechecks.json): initial outputs are retained. Importer-generated bone display geometry is not serialized asset geometry.
- [Source n-gon area/density diagnostic](source-density-ngon-diagnostic.json).
- Each table row links exact GLB structure/validator and Blender source/delivery reports. Source mapping supplements, if present, retain the original unresolved record.

## Image-textured primary models

| Asset | Images | Measured range px/m | Density state |
| --- | ---: | ---: | --- |
| mall-floor-tile-module | 1 | 859.555–859.555 | MEASURED_TARGET_UNSET |
| mall-ceiling-panel-module | 1 | 111.203–111.203 | MEASURED_TARGET_UNSET |
| mall-atrium-balcony | 1 | 700.645–859.680 | MEASURED_TARGET_UNSET |
| mall-digital-advertising-screen | 1 | 852.941–852.941 | MEASURED_TARGET_UNSET |
| gjh-m056-premium-wall-shelf-straight | 2 | 107.467–403.537 | MEASURED_TARGET_UNSET |
| gjh-m057-premium-wall-shelf-corner | 2 | 195.749–686.895 | MEASURED_TARGET_UNSET |
| gjh-m058-premium-wall-shelf-endcap | 2 | 150.919–945.798 | MEASURED_TARGET_UNSET |
| gjh-m059-premium-wall-shelf-narrow | 2 | 142.323–437.947 | MEASURED_TARGET_UNSET |
| gjh-m060-premium-wall-shelf-wide | 2 | 105.888–332.448 | MEASURED_TARGET_UNSET |
| gjh-m061-premium-wall-shelf-low | 2 | 105.888–332.449 | MEASURED_TARGET_UNSET |
| gjh-m062-curved-luxury-wall-shelf | 2 | 105.888–332.448 | MEASURED_TARGET_UNSET |

## Priority: exact zero-area delivery triangles

These are zero results from the raw GLB position/transform area calculation. Blender world-space Float32 evaluation can classify additional very small triangles as zero; those observations stay separate. Clean-up needs a separate change and retest; format conformance alone does not remove these triangles.

| Asset | Exact zero triangles | Total triangles | Fraction |
| --- | ---: | ---: | ---: |
| mall-queue-short | 960 | 7,252 | 13.2% |
| mall-queue-long | 960 | 7,252 | 13.2% |
| mall-queue-post | 480 | 3,344 | 14.4% |
| mall-trash-bin | 470 | 8,088 | 5.8% |
| mall-directory-kiosk | 394 | 5,360 | 7.4% |
| mall-advertising-lightbox | 200 | 7,168 | 2.8% |
| mall-waste-sorting-station | 199 | 11,508 | 1.7% |
| mall-service-desk | 172 | 8,024 | 2.1% |
| mall-display-shelf | 164 | 5,712 | 2.9% |
| mall-floor-direction-sign | 139 | 13,404 | 1.0% |
| mall-event-booth | 118 | 4,632 | 2.5% |
| gjh-areca-planter | 100 | 5,160 | 1.9% |
| gjh-m057-premium-wall-shelf-corner | 60 | 13,680 | 0.4% |
| escalator | 11 | 65,408 | 0.0% |
| atm-kiosk | 4 | 2,504 | 0.2% |
| passenger-lift | 4 | 7,656 | 0.1% |
| mall-wayfinding-ceiling-sign | 2 | 11,524 | 0.0% |
| mall-food-court-tray-station | 2 | 5,412 | 0.0% |

## Full asset results

| Asset | Group | Triangles | KiB | Exact zero triangles | Boundary observation: source / GLB welded | Density | Evidence |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| gjh-lounge-bench | shopping-mall | 5,640 | 228.8 | 0 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/gjh-lounge-bench.json) · [Blender](blender/gjh-lounge-bench.json) |
| gjh-areca-planter | shopping-mall | 5,160 | 117.0 | 100 | 1404 / 1012 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/gjh-areca-planter.json) · [Blender](blender/gjh-areca-planter.json) |
| gjh-mall-visitor | supporting-character | 10,356 | 361.3 | 0 | 628 / 8 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/gjh-mall-visitor.json) · [Blender](blender/gjh-mall-visitor.json) |
| mall-waste-sorting-station | shopping-mall | 11,508 | 468.2 | 199 | 6800 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-waste-sorting-station.json) · [Blender](blender/mall-waste-sorting-station.json) |
| mall-directory-kiosk | shopping-mall | 5,360 | 173.9 | 394 | 1460 / 12 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-directory-kiosk.json) · [Blender](blender/mall-directory-kiosk.json) |
| mall-advertising-lightbox | shopping-mall | 7,168 | 230.3 | 200 | 1764 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-advertising-lightbox.json) · [Blender](blender/mall-advertising-lightbox.json) |
| mall-trash-bin | shopping-mall | 8,088 | 330.3 | 470 | 1124 / 48 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-trash-bin.json) · [Blender](blender/mall-trash-bin.json) |
| mall-display-shelf | shopping-mall | 5,712 | 168.4 | 164 | 480 / 24 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-display-shelf.json) · [Blender](blender/mall-display-shelf.json) |
| mall-event-booth | shopping-mall | 4,632 | 210.6 | 118 | 1732 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-event-booth.json) · [Blender](blender/mall-event-booth.json) |
| mall-glass-railing-post | shopping-mall | 1,024 | 56.2 | 0 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-glass-railing-post.json) · [Blender](blender/mall-glass-railing-post.json) |
| mall-glass-railing-1m | shopping-mall | 3,236 | 171.7 | 0 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-glass-railing-1m.json) · [Blender](blender/mall-glass-railing-1m.json) |
| mall-glass-railing-2m | shopping-mall | 3,236 | 171.7 | 0 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-glass-railing-2m.json) · [Blender](blender/mall-glass-railing-2m.json) |
| mall-floor-tile-module | shopping-mall | 604 | 152.3 | 0 | 0 / 0 | MEASURED_TARGET_UNSET | [GLB](glb/mall-floor-tile-module.json) · [Blender](blender/mall-floor-tile-module.json) |
| mall-ceiling-panel-module | shopping-mall | 1,724 | 143.7 | 0 | 0 / 0 | MEASURED_TARGET_UNSET | [GLB](glb/mall-ceiling-panel-module.json) · [Blender](blender/mall-ceiling-panel-module.json) |
| mall-service-desk | shopping-mall | 8,024 | 240.0 | 172 | 1132 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-service-desk.json) · [Blender](blender/mall-service-desk.json) |
| mall-floor-direction-sign | shopping-mall | 13,404 | 548.7 | 139 | 7648 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-floor-direction-sign.json) · [Blender](blender/mall-floor-direction-sign.json) |
| mall-queue-post | shopping-mall | 3,344 | 95.6 | 480 | 576 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-queue-post.json) · [Blender](blender/mall-queue-post.json) |
| mall-queue-short | shopping-mall | 7,252 | 186.7 | 960 | 1152 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-queue-short.json) · [Blender](blender/mall-queue-short.json) |
| mall-queue-long | shopping-mall | 7,252 | 187.9 | 960 | 1152 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-queue-long.json) · [Blender](blender/mall-queue-long.json) |
| mall-ceiling-light-module | shopping-mall | 1,900 | 122.1 | 0 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-ceiling-light-module.json) · [Blender](blender/mall-ceiling-light-module.json) |
| mall-shopfront-door | shopping-mall | 2,604 | 142.3 | 0 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-shopfront-door.json) · [Blender](blender/mall-shopfront-door.json) |
| mall-shopfront-roller-shutter | shopping-mall | 4,608 | 247.0 | 0 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-shopfront-roller-shutter.json) · [Blender](blender/mall-shopfront-roller-shutter.json) |
| mall-glass-partition | shopping-mall | 852 | 53.1 | 0 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-glass-partition.json) · [Blender](blender/mall-glass-partition.json) |
| mall-structural-column | shopping-mall | 1,404 | 76.9 | 0 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-structural-column.json) · [Blender](blender/mall-structural-column.json) |
| mall-atrium-balcony | shopping-mall | 4,940 | 474.8 | 0 | 0 / 0 | MEASURED_TARGET_UNSET | [GLB](glb/mall-atrium-balcony.json) · [Blender](blender/mall-atrium-balcony.json) |
| mall-escalator-landing | shopping-mall | 1,616 | 81.4 | 0 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-escalator-landing.json) · [Blender](blender/mall-escalator-landing.json) |
| mall-escalator-handrail | shopping-mall | 5,100 | 114.4 | 0 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-escalator-handrail.json) · [Blender](blender/mall-escalator-handrail.json) |
| mall-lift-call-panel | shopping-mall | 2,608 | 97.6 | 0 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-lift-call-panel.json) · [Blender](blender/mall-lift-call-panel.json) |
| mall-lift-floor-indicator | shopping-mall | 596 | 42.3 | 0 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-lift-floor-indicator.json) · [Blender](blender/mall-lift-floor-indicator.json) |
| mall-emergency-exit-door | shopping-mall | 6,004 | 308.0 | 0 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-emergency-exit-door.json) · [Blender](blender/mall-emergency-exit-door.json) |
| mall-fire-hose-reel-cabinet | shopping-mall | 15,156 | 463.5 | 0 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-fire-hose-reel-cabinet.json) · [Blender](blender/mall-fire-hose-reel-cabinet.json) |
| mall-sprinkler-head | shopping-mall | 2,752 | 69.1 | 0 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-sprinkler-head.json) · [Blender](blender/mall-sprinkler-head.json) |
| mall-cctv-camera | shopping-mall | 2,572 | 99.2 | 0 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-cctv-camera.json) · [Blender](blender/mall-cctv-camera.json) |
| mall-digital-advertising-screen | shopping-mall | 5,116 | 650.1 | 0 | 0 / 0 | MEASURED_TARGET_UNSET | [GLB](glb/mall-digital-advertising-screen.json) · [Blender](blender/mall-digital-advertising-screen.json) |
| mall-wayfinding-ceiling-sign | shopping-mall | 11,524 | 660.2 | 2 | 3800 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-wayfinding-ceiling-sign.json) · [Blender](blender/mall-wayfinding-ceiling-sign.json) |
| mall-food-court-tray-station | shopping-mall | 5,412 | 345.4 | 2 | 1340 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-food-court-tray-station.json) · [Blender](blender/mall-food-court-tray-station.json) |
| mall-retail-pop-up-cart | shopping-mall | 6,860 | 459.6 | 0 | 588 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-retail-pop-up-cart.json) · [Blender](blender/mall-retail-pop-up-cart.json) |
| shopping-cart | shopping-mall | 10,636 | 523.9 | 0 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/shopping-cart.json) · [Blender](blender/shopping-cart.json) |
| shopping-basket | shopping-mall | 4,260 | 224.9 | 0 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/shopping-basket.json) · [Blender](blender/shopping-basket.json) |
| atm-kiosk | shopping-mall | 2,504 | 134.9 | 4 | 136 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/atm-kiosk.json) · [Blender](blender/atm-kiosk.json) |
| mall-entrance | shopping-mall | 2,700 | 148.9 | 0 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-entrance.json) · [Blender](blender/mall-entrance.json) |
| mall-corridor | shopping-mall | 3,264 | 177.5 | 0 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-corridor.json) · [Blender](blender/mall-corridor.json) |
| cinema-entrance | shopping-mall | 4,256 | 224.4 | 0 | 280 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/cinema-entrance.json) · [Blender](blender/cinema-entrance.json) |
| mall-toilet-entrance | shopping-mall | 1,404 | 78.0 | 0 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-toilet-entrance.json) · [Blender](blender/mall-toilet-entrance.json) |
| escalator | shopping-mall | 65,408 | 4563.2 | 11 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/escalator.json) · [Blender](blender/escalator.json) |
| mall-shopper | supporting-character | 4,012 | 398.5 | 0 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-shopper.json) · [Blender](blender/mall-shopper.json) |
| passenger-lift | shopping-mall | 7,656 | 412.4 | 4 | 512 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/passenger-lift.json) · [Blender](blender/passenger-lift.json) |
| mall-water-dispenser | shopping-mall | 3,252 | 173.6 | 0 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-water-dispenser.json) · [Blender](blender/mall-water-dispenser.json) |
| mall-glass-showcase | shopping-mall | 1,712 | 94.6 | 0 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-glass-showcase.json) · [Blender](blender/mall-glass-showcase.json) |
| mall-shoe-bag-rack | shopping-mall | 5,088 | 258.0 | 0 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-shoe-bag-rack.json) · [Blender](blender/mall-shoe-bag-rack.json) |
| mall-fitting-room | shopping-mall | 4,900 | 250.9 | 0 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-fitting-room.json) · [Blender](blender/mall-fitting-room.json) |
| mall-bar-stool | shopping-mall | 5,544 | 266.6 | 0 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-bar-stool.json) · [Blender](blender/mall-bar-stool.json) |
| mall-coffee-counter | shopping-mall | 3,532 | 188.6 | 0 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-coffee-counter.json) · [Blender](blender/mall-coffee-counter.json) |
| interactive-shopping-cart | shopping-mall | 5,564 | 173.5 | 0 | 40 / 40 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/interactive-shopping-cart.json) · [Blender](blender/interactive-shopping-cart.json) |
| gjh-m056-premium-wall-shelf-straight | shopping-mall | 8,700 | 693.4 | 0 | 0 / 0 | MEASURED_TARGET_UNSET | [GLB](glb/gjh-m056-premium-wall-shelf-straight.json) · [Blender](blender/gjh-m056-premium-wall-shelf-straight.json) |
| gjh-m057-premium-wall-shelf-corner | shopping-mall | 13,680 | 1031.8 | 60 | 0 / 0 | MEASURED_TARGET_UNSET | [GLB](glb/gjh-m057-premium-wall-shelf-corner.json) · [Blender](blender/gjh-m057-premium-wall-shelf-corner.json) |
| gjh-m058-premium-wall-shelf-endcap | shopping-mall | 11,044 | 843.6 | 0 | 0 / 0 | MEASURED_TARGET_UNSET | [GLB](glb/gjh-m058-premium-wall-shelf-endcap.json) · [Blender](blender/gjh-m058-premium-wall-shelf-endcap.json) |
| gjh-m059-premium-wall-shelf-narrow | shopping-mall | 8,700 | 692.6 | 0 | 0 / 0 | MEASURED_TARGET_UNSET | [GLB](glb/gjh-m059-premium-wall-shelf-narrow.json) · [Blender](blender/gjh-m059-premium-wall-shelf-narrow.json) |
| gjh-m060-premium-wall-shelf-wide | shopping-mall | 12,600 | 959.0 | 0 | 0 / 0 | MEASURED_TARGET_UNSET | [GLB](glb/gjh-m060-premium-wall-shelf-wide.json) · [Blender](blender/gjh-m060-premium-wall-shelf-wide.json) |
| gjh-m061-premium-wall-shelf-low | shopping-mall | 10,800 | 842.3 | 0 | 0 / 0 | MEASURED_TARGET_UNSET | [GLB](glb/gjh-m061-premium-wall-shelf-low.json) · [Blender](blender/gjh-m061-premium-wall-shelf-low.json) |
| gjh-m062-curved-luxury-wall-shelf | shopping-mall | 9,156 | 710.3 | 0 | 0 / 0 | MEASURED_TARGET_UNSET | [GLB](glb/gjh-m062-curved-luxury-wall-shelf.json) · [Blender](blender/gjh-m062-curved-luxury-wall-shelf.json) |
| mall-shopfront-fascia-210 | shopping-mall | 72 | 8.3 | 0 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-shopfront-fascia-210.json) · [Blender](blender/mall-shopfront-fascia-210.json) |
| mall-shopfront-fascia-120 | shopping-mall | 72 | 8.4 | 0 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-shopfront-fascia-120.json) · [Blender](blender/mall-shopfront-fascia-120.json) |
| mall-column-ceiling-collar | shopping-mall | 144 | 15.0 | 0 | 0 / 0 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/mall-column-ceiling-collar.json) · [Blender](blender/mall-column-ceiling-collar.json) |
| gjh-mall-visitor-v2 | supporting-character | 13,936 | 563.5 | 0 | 632 / 8 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/gjh-mall-visitor-v2.json) · [Blender](blender/gjh-mall-visitor-v2.json) |
| gjh-mall-visitor-v2-lod1 | supporting-lod | 6,257 | 363.9 | 0 | 632 / 1099 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/gjh-mall-visitor-v2-lod1.json) · [Blender](blender/gjh-mall-visitor-v2-lod1.json) |
| chibi-mall-visitor-local | local-uncatalogued-character | 97,824 | 1605.9 | 0 | 690 / 690 | N_A_NO_IMAGE_TEXTURES | [GLB](glb/chibi-mall-visitor-local.json) · [Blender](blender/chibi-mall-visitor-local.json) |

## Review flags

| Asset | Flags |
| --- | --- |
| gjh-lounge-bench | SOURCE_FILE_NEWER_THAN_READER |
| gjh-areca-planter | BOUNDARY_TOPOLOGY_OBSERVED_ROLE_REVIEW; EXACT_ZERO_AREA_TRIANGLES_DEFAULT_POSE; SOURCE_FILE_NEWER_THAN_READER |
| gjh-mall-visitor | BOUNDARY_TOPOLOGY_OBSERVED_ROLE_REVIEW; SOURCE_FILE_NEWER_THAN_READER |
| mall-waste-sorting-station | BOUNDARY_TOPOLOGY_OBSERVED_ROLE_REVIEW; EXACT_ZERO_AREA_TRIANGLES_DEFAULT_POSE |
| mall-directory-kiosk | BOUNDARY_TOPOLOGY_OBSERVED_ROLE_REVIEW; EXACT_ZERO_AREA_TRIANGLES_DEFAULT_POSE |
| mall-advertising-lightbox | BOUNDARY_TOPOLOGY_OBSERVED_ROLE_REVIEW; EXACT_ZERO_AREA_TRIANGLES_DEFAULT_POSE |
| mall-trash-bin | BOUNDARY_TOPOLOGY_OBSERVED_ROLE_REVIEW; EXACT_ZERO_AREA_TRIANGLES_DEFAULT_POSE |
| mall-display-shelf | BOUNDARY_TOPOLOGY_OBSERVED_ROLE_REVIEW; EXACT_ZERO_AREA_TRIANGLES_DEFAULT_POSE |
| mall-event-booth | BOUNDARY_TOPOLOGY_OBSERVED_ROLE_REVIEW; EXACT_ZERO_AREA_TRIANGLES_DEFAULT_POSE |
| mall-service-desk | BOUNDARY_TOPOLOGY_OBSERVED_ROLE_REVIEW; EXACT_ZERO_AREA_TRIANGLES_DEFAULT_POSE |
| mall-floor-direction-sign | BOUNDARY_TOPOLOGY_OBSERVED_ROLE_REVIEW; EXACT_ZERO_AREA_TRIANGLES_DEFAULT_POSE |
| mall-queue-post | BOUNDARY_TOPOLOGY_OBSERVED_ROLE_REVIEW; EXACT_ZERO_AREA_TRIANGLES_DEFAULT_POSE |
| mall-queue-short | BOUNDARY_TOPOLOGY_OBSERVED_ROLE_REVIEW; EXACT_ZERO_AREA_TRIANGLES_DEFAULT_POSE |
| mall-queue-long | BOUNDARY_TOPOLOGY_OBSERVED_ROLE_REVIEW; EXACT_ZERO_AREA_TRIANGLES_DEFAULT_POSE |
| mall-wayfinding-ceiling-sign | BOUNDARY_TOPOLOGY_OBSERVED_ROLE_REVIEW; EXACT_ZERO_AREA_TRIANGLES_DEFAULT_POSE |
| mall-food-court-tray-station | BOUNDARY_TOPOLOGY_OBSERVED_ROLE_REVIEW; EXACT_ZERO_AREA_TRIANGLES_DEFAULT_POSE |
| mall-retail-pop-up-cart | BOUNDARY_TOPOLOGY_OBSERVED_ROLE_REVIEW |
| atm-kiosk | BOUNDARY_TOPOLOGY_OBSERVED_ROLE_REVIEW; EXACT_ZERO_AREA_TRIANGLES_DEFAULT_POSE |
| cinema-entrance | BOUNDARY_TOPOLOGY_OBSERVED_ROLE_REVIEW |
| escalator | EXACT_ZERO_AREA_TRIANGLES_DEFAULT_POSE |
| passenger-lift | BOUNDARY_TOPOLOGY_OBSERVED_ROLE_REVIEW; EXACT_ZERO_AREA_TRIANGLES_DEFAULT_POSE |
| interactive-shopping-cart | BOUNDARY_TOPOLOGY_OBSERVED_ROLE_REVIEW |
| gjh-m057-premium-wall-shelf-corner | EXACT_ZERO_AREA_TRIANGLES_DEFAULT_POSE |
| gjh-mall-visitor-v2 | BOUNDARY_TOPOLOGY_OBSERVED_ROLE_REVIEW |
| gjh-mall-visitor-v2-lod1 | BOUNDARY_TOPOLOGY_OBSERVED_ROLE_REVIEW |
| chibi-mall-visitor-local | BOUNDARY_TOPOLOGY_OBSERVED_ROLE_REVIEW |

## Reproduce

```sh
python3 scripts/test-shopping-mall-qa.py /absolute/path/scanner-calibration.json
python3 scripts/qa-shopping-mall.py --output /absolute/path/new-report-directory --workers 2
cp /absolute/path/scanner-calibration.json /absolute/path/new-report-directory/scanner-calibration-current.json
python3 scripts/qa-shopping-mall-source-supplements.py /absolute/path/new-report-directory
python3 scripts/report-shopping-mall-qa.py /absolute/path/new-report-directory
```

Use a new output directory; earlier evidence is not overwritten. Requires repository Node dependencies, Blender and the installed exact P0 extensions. Separate processes, not concurrent bpy threads, provide isolation. Source scripts from model folders are never executed.
