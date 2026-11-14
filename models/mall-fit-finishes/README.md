# Mall fit finishes

Two original asset families close the measured P0 fit-study gaps: shopfront fascia (2.10 m and 1.20 m width variants) and square-column ceiling collar. Each has a separate editable `.blend`, standalone GLB and preview. These assets are used in the [updated fit study](../../docs/verification/p0-assembly/README.md); they are now registered locally in the Gallery catalog with lightweight JPEG cards and per-asset metadata.

| Asset | glTF X / Y / Z dimensions, m | Triangles | GLB bytes |
| --- | --- | ---: | ---: |
| mall-shopfront-fascia-210 | 2.10 / 0.60 / 0.06 | 72 | 8,548 |
| mall-shopfront-fascia-120 | 1.20 / 0.60 / 0.06 | 72 | 8,552 |
| mall-column-ceiling-collar | 1.20 / 0.032 / 1.20; 0.60 square clear hole | 144 | 15,384 |

## Coordinates and assembly

Metres; Blender +Z up / front −Y converts to glTF +Y up / front +Z. No scaling is needed in the sample.

Fascia roots are bottom-centred. Place them at Blender Z=2.4, Y=−1.5, X=0 for the 2.10 m door variant and X=±1.65 for the 1.20 m partition variants. The top is Z=3.0. Six separately editable closed mesh objects include four frame rails, an ivory infill and an unbranded replacement sign face. The sign face is a separate material/object; no typography, UV template, logo, lighting or runtime content replacement is provided. Both widths have their own source and GLB; they are variants of one family.

The collar root is the centre of its trim underside. Place it at Blender (−1.8,0,3.0) in the sample, replacing the omitted 1.20 m ceiling bay. Eight separate trim objects and four closure panels cover the ring around the 0.60 m square cap. Outer registration planes are ±0.60 m; the inner hole planes are ±0.30 m. Trim underside is Z=0 and panel underside is Z=0.008 locally, matching the adjacent ceiling recess. The inner opening has nominal contact rather than a fabrication tolerance. No clips, hangers or physical fixing system are included.

**Visible ceiling reveal:** the fascia top meets the ceiling-grid underside at 3.0 m. Between grid rails, the existing ceiling face is recessed 8 mm; that shallow line remains intentional. It is not asserted to be a sealed or fire-rated joint. The smooth collar infill is deliberately distinct from the textured existing panels.

## Reproduce and preserve edits

Requires Blender 5.1.2 and the repository's locked Node dependencies. Review scripts before running. From repository root:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --threads 4 --python-exit-code 1 --python models/mall-fit-finishes/generate.py
node models/mall-fit-finishes/validate.mjs
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --threads 2 --python-exit-code 1 --python models/mall-fit-finishes/check-source.py
```

Normal generation replaces only this collection's three sources, exports and previews. For saved manual source edits, add `-- --export-source --skip-render`; this exports the saved roots without regeneration. Back up personal edits before regeneration. Reproduction may change binary or render hashes across toolchains; refresh metadata hashes after intentionally rebuilding.

## Executed checks and limits

- Actual standalone GLBs: Khronos 0 errors / 0 warnings; each below 50 KB and 300 triangles; embedded static opaque PBR, no external dependencies. See `reports/glb-validation.json`.
- All source mesh components have closed edge incidence and positive signed volume. Each source was reopened, one component's vertices raised 4 mm and roughness changed, saved/reopened/re-exported in a temporary copy, and the changed geometry/material verified after actual GLB import. Canonical source hashes stayed unchanged. See `reports/source-proof.json`.
- Sample coverage: 6,525 fascia rays, 2,700 collar ring rays and nine clear-hole probes passed. New component boxes have no positive overlap greater than 10 micrometres along all three axes with other components in the sample. This is bounded sampling and box-based evidence, not proof of all triangle intersections or physical tolerance.
- The updated sample was inspected in Blender renders and Chromium at desktop/phone viewport sizes, including underside and column-joint views. See the fit-study report for exact results and limits.
- No physical mobile/Safari or customer-scene integration check is claimed. Local Gallery registration is verified in `reports/browser/results.json`; deployment is tracked separately by repository CI. See LICENSE.md for rights.
