# Shopping Mall degenerate geometry repairs

Active campaign: repair and publish one asset at a time. A fresh raw GLB scan of the 62 primary mall exports at main `1e942079` confirms 15 remaining affected assets. The already-repaired three queue models are outside this remaining list. The older full mall audit remains a historical snapshot.

[Baseline and hashes](baseline.json) · [Current progress](progress.json)

| Asset | Baseline exact zero-area triangles | State in this revision |
| --- | ---: | --- |
| mall-trash-bin | 470 | repaired |
| mall-directory-kiosk | 394 | repaired |
| mall-advertising-lightbox | 200 | repaired |
| mall-waste-sorting-station | 199 | repaired |
| mall-service-desk | 172 | repaired |
| mall-display-shelf | 164 | repaired |
| mall-floor-direction-sign | 139 | repaired |
| mall-event-booth | 118 | repaired |
| gjh-areca-planter | 100 | repaired |
| gjh-m057-premium-wall-shelf-corner | 60 | repaired |
| escalator | 11 | repaired |
| atm-kiosk | 4 | repaired |
| passenger-lift | 4 | repaired |
| mall-food-court-tray-station | 2 | repaired |
| mall-wayfinding-ceiling-sign | 2 | repaired |

Each repaired row must have updated editable source, actual GLB geometry/provenance, a failing-then-passing regression and asset-specific verification. Publication is checked against the live remote main ref after each push; a progress row alone does not prove publication. No deployment, phone/FPS or certification claim is made.

Final raw scan: [68 current primary Mall GLBs](final-scan.json), including the original 62 and six subsequent additions, have zero exact-zero triangles and zero Validator errors. Reproduce with `node scripts/scan-glb-topology.mjs docs/model-qa/degenerate-repairs/final-scan-inventory.json /new/owned/report-directory`. The manifest binds current bytes by SHA; raw per-primitive evidence is in final-scan-details.json.gz. This scan covers default/bind pose only and does not certify deformation poses, all LODs or hardware performance.
