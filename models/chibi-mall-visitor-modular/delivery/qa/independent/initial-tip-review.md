# Initial lock-tip review — reopened 119

**119 is REWORK under the reopened hair-tip gate.** User rejection supersedes its earlier hair acceptance, including the Metal addendum. The earlier reports remain historical evidence; their PASS must not be carried into this review or a later candidate.

Reviewer: `/root/visitor_visual_review`, independent non-author. Freshly inspected the original large front, both quarters, side and back, then rejected 119 material and clay at normal head size and enlarged. No model, source, input or capture was edited.

## Four-panel reading and five fixed target locks

The reference has thick shared root masses, but several **bodies end as identifiable tapered tips over another layer**. Reading a curved stripe is insufficient: the eye can follow the body, locate its endpoint, and identify the small exposed-underlayer/occlusion wedge below it. Outer tips additionally make a notch against the background. Internal dark negative space need not be a see-through hole.

Coordinates below are approximate native pixels in the original **1536 × 1024** sheet. Path points follow visible ridges/emergences, not invented hidden anatomical roots. Tip boxes locate the feature and are not numerical matching tolerances.

| ID | Reference visible path → endpoint | What separates the tip | Fresh 119 observation |
| --- | --- | --- | --- |
| **S1 — upper side-fan curl** | Large side: **(858,73) → (875,100) → tip (905,122)**; tip neighborhood x899–912/y116–128. | The convex body turns right/down, narrows, then ends above a darker underlayer. Its lower edge and the small wedge beneath the point distinguish it from the next body. | A substantial upper projection survives in clay, so this is not the same failure as every lower lock. Its terminal is heavier/less clearly hooked; the surviving lobe does not establish the missing lower tips. Preserve the useful body while checking its terminal directly. |
| **S2 — middle rearward side tooth** | Large side: visible emergence **(850,123) → (875,144) → tip (897,154)**; x890–905/y148–161. | It exits beneath the upper curl and points rearward; a dark wedge immediately below the narrowing end exposes a different lower body. The endpoint stops before that lower body continues. | Material suggests this separate swept tooth. In side clay, its end is not independently traceable and merges into the broad side mass. A material contour was previously mistaken for an independently terminating body. |
| **S3 — lower forward fan above the ear** | Large side: **(803,96) → (816,137) → tip (851,163)**; x844–858/y157–169. | The long front body bends toward the rear and narrows above the ear. The exposed lower/temple region and underside wedge keep the point distinct from both the hair behind it and the temporal piece below it. | The colored underside suggests a curl, but clay combines the lower fan endings into one swollen volume flowing into the temporal cap. The reader cannot recover the same discrete terminal. |
| **Q1 — outer upper front-quarter sweep** | Left large quarter: **(175,72) → (126,85) → (79,107) → tip (48,119)**; x41–56/y112–126. | The outgoing curved point forms a small background notch before the lower tier resumes. The upper and lower sweeps retain separate endpoints rather than one smooth side wall. | The overall sweep direction survives, but the clay outer tier is a broad rounded ledge with insufficient distinct hooked endpoints/notches. Overall head silhouette was too coarse a substitute for this local silhouette. |
| **B1 — inward-ending left back C lock** | Large back: **(1077,72) → (1044,100) → tip (1050,137)**; x1043–1058/y131–146. | The body curls left/down and ends inward over the rear layer. The pointed end, curved lower edge and narrow dark underlap let the layer behind continue separately. It is not a groove running indefinitely down the cap. | The material C is easy to see, but its inward endpoint largely disappears in back clay into a continuous shell. This is a clear material-versus-terminal counterexample, despite the acceptable broad rear sweep. |

The side contains more than these selected targets; these five are stable, high-impact witnesses for the next review, not a license to ignore another conspicuously fused end. The front forehead opening and some positive lobes remain; they cannot cancel the failed side/back terminals.

## Why the previous review passed fused terminals

The old V02–V04 language already required thick curved locks and tapered overlapping ends. **My application was insufficient**: I judged the overall sweep, large mass and dark material curves, without requiring an endpoint-by-endpoint demonstration. I treated missing clay definition as a harmless diagnostic difference and accepted colored/normal-like contours as evidence of an actual terminal. The later material-patch work then concentrated attention on surface continuity rather than this unresolved structure.

The direct evidence is the material/clay discrepancy at S2/S3/B1. “Fused” here means **visually continuous with the supporting mass**; this report has not measured welded vertices, separate objects or a particular shader/bake cause. Material or custom-normal appearance may help a finished body, but cannot be the sole evidence that its tip exists. This is a review false positive, not a newly approved simplification of the reference.

## Gate for blind candidates

Use the same lock IDs and pinned front/quarter/true-side/back cameras, final material and neutral clay. Inspect normal head display size first, then close up. Clay must remove albedo and normal/bump detail; keep enough light to distinguish the upper body, its underside and the supporting layer. If custom shading leaves depth ambiguous, provide a geometric-normal or grazing diagnostic rather than assuming separation.

For **each** target:

1. Trace one rounded body along the reference direction to **one locatable endpoint**. Its last segment narrows; a round cap lump or an endless dark groove does not count.
2. Show an actual readable terminal edge/undercut and exposed-underlayer wedge in clay as well as material. Outer Q1 must preserve its local silhouette notch. Internal locks need not create holes through to the background, and roots may remain shared.
3. Confirm the same body/endpoint in a neighboring quarter or grazing angle: overlap order and depth must remain consistent. A tip may be legitimately occluded in one angle; select another revealing view. An unobservable end remains **NOT_REVIEWED**, not PASS.
4. Reject a candidate if its “extra locks” disappear into the cap when material detail is removed, or if sharpening creates detached spikes instead of thick curved tapered bodies. Do not average a failed end away with good color, a good main C, or other passed locks.

**What clears the gate:** all five paths can be followed to distinct, appropriately tapered, overlapping terminal forms at normal size, supported by clay and a consistent second angle; the main sweep, root volume, ear transition, rear layering and material remain intact. Evidence must bind to the exact candidate. Do not certify an unseen underside or require separate mesh objects as an implementation rule.

The new check has a known negative witness: rejected 119 must fail it, especially S2/S3/B1. A corrected positive candidate is **not yet verified**. This detection rule is project-local; no global skill or model was changed. Future source fixes belong to the builder.

## Evidence identity

- Original: `/Users/yapweijun/Downloads/Chibi Mall Visitor Character Sheet.png`, SHA-256 `0915b9e7b41d35177cb890580935b9c1db355539a1183861b2387c936f110f6f`.
- Rejected GLB: `review/hair-rebuild/119/visitor.glb`, SHA-256 `88ee2069c389ef8aa9d4308f11ecb0fad9805e9d6b5eba0cd913f045b83b5cbd`.
- Used bound `119/qa/hair-material.png`, `hair-clay.png`, and registered RGB; actual GLB/reference and all listed image hashes were rechecked against `hair-study.json` (`4fc1314ec63bace06aef8ea5e2b3583312e0dfdb3cb1ae9d8da4b06ae556087f`) and `registration/manifest.json` (`1b9d211117873e1182b3af6b6b834088217e02cb355d94bf03253bb4ec3198b6`). Normal and 2× crops were review-only temporary derivatives.

This is a targeted tip/overlap review, not a new palette, motion, technical or native-source certification. Original projection is uncertain; the visible paths and terminal relationships, rather than exact image coordinates, define acceptance.

Signed: `/root/visitor_visual_review` — independent non-author visual reviewer.
