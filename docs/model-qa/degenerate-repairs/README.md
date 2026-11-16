# Shopping Mall degenerate geometry repairs

Completed campaign: 15 originally affected assets repaired and individually published. The baseline raw GLB scan of the 62 primary mall exports at main `1e942079` identified these remaining affected assets. The already-repaired three queue models are outside this remaining list. The older full mall audit remains a historical snapshot.

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

All 15 publication commits are recorded in progress.json and verified as ancestors of the final asset commit eefd6c61. The final project test run passes 720 tests; build passes. Per-asset native/source/edit/browser receipts retain rejected attempts and their causes. Physical phone acceptance was waived by the user and remains untested.

Knowledge maintenance: existing canonical Skill `blender:glb-export-qa` is updated to v1.0.6, with exact full body/file readback and independently recomputed attachment hashes; the `blender` KB discovery pointer also has exact content readback. [Storage verification](kb-sync.json) preserves advisory enablement, all prior optional metadata, generic acceptance 0 executed and runtime/production flags false. No duplicate Skill was created. New lessons cover original exporter matching, texture semantics, shared-index splitting, static parts in rigid animation containers, source action snapshots, additive report contracts and same-toolchain edit controls.

KB Fast Skills was applied through complete reads of `kb-mcp:fast-skills@1.0.0`, `agent:context-engineering@1.1.0` and `agent:execution-efficiency@1.0.0`: bounded retrieval, current verification records, sequential owning-runtime checks and reuse of evidence for unchanged inputs. Runtime verification remains independent from KB storage verification.
