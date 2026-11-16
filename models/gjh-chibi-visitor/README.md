# GJH Chibi Visitor

This comparison set contains three independent Unity builds of the same written GJH Chibi Visitor concept. The terra, sol, and astra AI models generated their own geometry using the Unity editor builder; they are visual alternatives, not three interchangeable parts of one mesh.

## Variants

| Variant | Visible distinction |
| --- | --- |
| terra | Angular happy-eye chevrons and a compact, simpler face and chest mark. |
| sol | Broad face screen with curved happy arcs, a rounded hood roll, and a more layered hoodie. |
| astra | Curved happy arcs with more layered ring headphones and clothing accents. |

All three share a white rounded helmet and hoodie, purple accents, tall fins, black face screen, headphones, short limbs, and a default happy expression. Their GLBs have the `GJHChibiVisitor` scene root, use +Y up and +Z forward, contain no external resources, and contain no animation clips.

## Measurements

These values are measured from the packaged GLBs. Triangle counts include each mesh instance in the scene; vertex counts count unique stored position accessors, matching the gallery's catalog metrics.

| Variant | GLB bytes | Triangles | Vertices | Animation clips | Front preview |
| --- | ---: | ---: | ---: | ---: | ---: |
| terra | 38,328 | 10,848 | 800 | 0 | under 150 KiB |
| sol | 135,980 | 14,352 | 3,236 | 0 | under 150 KiB |
| astra | 100,344 | 14,736 | 2,272 | 0 | under 150 KiB |

## Reproduce

The three source Unity projects use Unity **6000.0.85f2** and `com.unity.cloud.gltfast` **6.21.0**. Each project README records its Unity build and GLB reimport commands. Generate the GLB and four PNG previews in the source project first. The packaging step below only reads the Unity projects; it copies each `Assets/Editor/ChibiBuilder.cs`, GLB, and PNG previews into this repository.

Install Pillow for the optional packaging dependency, then run from the repository root:

```sh
python3 -m pip install Pillow
python3 models/gjh-chibi-visitor/package.py \
  --terra-project /Users/admin/Documents/Unity/ChibiMallGuide \
  --sol-project /Users/admin/Documents/Unity/ChibiMallGuide-sol \
  --astra-project /Users/admin/Documents/Unity/ChibiMallGuide-astra
npm run validate:assets
node models/gjh-chibi-visitor/validate.mjs
npm test
npm run build
```

The packager converts the four faithful 1024-pixel renders per variant to WebP, reducing the front thumbnail below 150 KiB. It also recomputes GLB accessor min/max values from the embedded vertex data. Unity's sol and astra exports rounded some declared bounds by a few floating-point units; this corrects that metadata only and leaves vertex/index data unchanged. It then measures file bytes, triangles, vertices, and animation clips from the resulting GLB and writes each variant's `metadata.json` and the collection registration.

## Character-sheet fidelity

The owner's original character-sheet image was not included with the inputs. The models follow the written design reference in [`docs/gjh-chibi-visitor-design.md`](../../docs/gjh-chibi-visitor-design.md); exact proportions and sheet fidelity cannot be confirmed. The screen sits proud of the helmet in side view, the fins use simplified straight-sided geometry, and hoodie seams and accessories are stylized. The design reference lists alternate expressions, outfits, and accessories, but each gallery GLB exports only the happy expression with the white hoodie. These comparison assets do not represent the complete modular concept sheet or an official GJH spokesperson.

The variants differ in face and clothing detail: terra uses sharper chevron eyes and a more compact chest treatment; sol uses a broader screen and rounded hood roll; astra has more layered headphone rings and clothing accents. These are visible differences in the supplied previews, not a claim of exact sheet matching.

## Rights

The gallery metadata uses the same rights wording as the existing GJH Mall Visitor entry:

> Original asset; reuse in the owner's projects is authorized. Public redistribution terms have not been specified.

Gallery downloads are disabled for these assets. This does not define a public redistribution license; rights and third-party marks in any future reference material would need their own review.
