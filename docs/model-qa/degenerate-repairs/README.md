# Shopping Mall degenerate geometry repairs

Active campaign: repair and publish one asset at a time. A fresh raw GLB scan of the 62 primary mall exports at main `1e942079` confirms 15 remaining affected assets. The already-repaired three queue models are outside this remaining list. The older full mall audit remains a historical snapshot.

[Baseline and hashes](baseline.json) · [Current progress](progress.json)

| Asset | Baseline exact zero-area triangles | State in this revision |
| --- | ---: | --- |
| mall-trash-bin | 470 | repaired |
| mall-directory-kiosk | 394 | repaired |
| mall-advertising-lightbox | 200 | repaired |
| mall-waste-sorting-station | 199 | repaired |
| mall-service-desk | 172 | pending |
| mall-display-shelf | 164 | pending |
| mall-floor-direction-sign | 139 | pending |
| mall-event-booth | 118 | pending |
| gjh-areca-planter | 100 | pending |
| gjh-m057-premium-wall-shelf-corner | 60 | pending |
| escalator | 11 | pending |
| atm-kiosk | 4 | pending |
| passenger-lift | 4 | pending |
| mall-food-court-tray-station | 2 | pending |
| mall-wayfinding-ceiling-sign | 2 | pending |

Each repaired row must have updated editable source, actual GLB geometry/provenance, a failing-then-passing regression and asset-specific verification. Publication is checked against the live remote main ref after each push; a progress row alone does not prove publication. No deployment, phone/FPS or certification claim is made.
