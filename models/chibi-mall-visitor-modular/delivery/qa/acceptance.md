# Swept-lock visual acceptance

The independent reviewer passed the five reopened hair paths on GLB `60650f47aac716cb5a11fa69bee58c06546aa2199a25c2bde6dcc37ce566ab6f`. The owner requested the four-angle comparison for review. Owner review is pending.

| Path | Reference feature | Independent verdict |
| --- | --- | --- |
| S1 | Upper curl on the reference profile | PASS |
| S2 | Middle sweep behind the ear | PASS |
| S3 | Lower forward sweep above the ear | PASS |
| Q1 | Long outward sweep in three-quarter view | PASS |
| B1 | Inward-ending C on the back of the head | PASS |

The previous delivery combined the hair into one welded shell. Under neutral lighting, several terminal forms disappeared into the supporting surface. Its earlier acceptance checked the direction and hairline, and gave dark material boundaries too much weight. The reviewed replacement uses a rooted foundation and fifteen closed swept sections with separately editable geometry. Earlier repair trials identified a stray tangent-space fold on the reverse overlap and local penetration of the lower sweep by the supporting cap. The final review traces the whole visible section through the taper at normal viewing size and in adjacent views.

[Four native-material views](before-after-hair.png) · [Four neutral views](independent/technical/review-sheets/four-angle-comparison.png) · [Failed prior witnesses](independent/technical/review-sheets/source-old119-witnesses.png) · [Signed visual observations](independent/visual-review.md) · [Independent technical report](independent/technical/report.md).

The complete character has 7,994 triangles and measures 1.3000 m in rest pose. Khronos Validator recorded 0 errors and 0 warnings. All twelve motion clips, six expressions, and four accessory states passed the application checks. Three full replay paths reproduced the GLB byte for byte. The native guide check moved all 66 saved curves in turn, and the actual edited-guide export changed the hair. The chosen native master is exactly the independent reviewer’s copy. It also passed the native mesh, materials and source-to-export portrait check.

The screen-space scale, pose and lights are fixed for both runtime assets. The original three-quarter camera is estimated at −28°. The visual signature covers the five requested hair paths. The source sheet uses different facial expressions between views.

[Native master](../visitor.blend) · [GLB](../visitor.glb) · [Offline preview](../preview.html) · [Build and hashes](build.json) · [Acceptance measurements](acceptance.json).

The rebuild kit uses the name `hair_temple_fit.py` for its temple-fitting helper. This preserves a separate earlier authoring tool at its original path. The complete build reproduced the exact reviewed GLB and four comparison frames after the rename. [Independent export binding](independent/release-source/).
