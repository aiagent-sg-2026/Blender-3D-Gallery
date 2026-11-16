# Chibi Visitor v2 · Technical QA

Test environment: 2026-11-16, macOS ARM64 VM, Blender 5.2.3 LTS, Unity Editor 6000.0.85f2 (Personal), UnityGLTF 2.24.0, Three.js 0.187.0, Khronos glTF Validator 2.0.0-dev.3.10.

## Status

| Gate | Result | Evidence |
|---|---|---|
| Original authoring | PASS | `generate.py` generated `.blend`, `.glb` and four camera renders |
| Visual front/side/back/3/4 | SELF-REVIEW | Rendered views in `previews/`; initial floating hair/jeans seams repaired; no independent owner art sign-off |
| Modular transform hierarchy | PASS | Eight `MOD_*` groups in GLB |
| Blender GLB independent import | PASS | `verify_blender.py`: 21 meshes, 21,581 vertices, 37,008 triangles, 16 materials |
| Unity model import | PASS | Unity Editor log `CHIBI_UNITY_IMPORT_PASS meshes=21 vertices=21581 materials=16 roots=8` |
| UnityGLTF round-trip | PASS | Unity Editor log `CHIBI_UNITY_GLB_EXPORT_PASS bytes=1283304` |
| Unity-derived GLB Blender import | PASS | 21 meshes, 21,581 vertices, 37,008 triangles, 16 materials; same bounds as source |
| Khronos native GLB | PASS | 0 errors, 0 warnings |
| Khronos Unity round-trip GLB | PASS | 0 errors, 0 warnings; the informational unused tangent messages are not warnings |
| Chrome WebGL desktop fixture | PASS | 1280x800: model loaded, 21 meshes; screenshot `webgl-desktop.webp` |
| Chrome WebGL mobile fixture | PASS | 390x844: model loaded, 21 meshes; screenshot `webgl-mobile.webp` |
| Rig/skin/Idle/Walk/Run | NOT RUN | Intentionally absent: 0 animation clips |
| Published GitHub Pages | NOT VERIFIED HERE | Confirm separately using this release's GitHub Actions and live URL |

Measured native GLB: **921,072 bytes**, **21 meshes**, **21,581 vertices**, **37,008 triangles**, **16 materials**, **0 animation clips**, height **1.804 m**. Mesh budget ≤25, triangle budget ≤40k, GLB size ≤5 MiB; one static character pass. Approximate draw calls are 21 (one material per mesh), subject to runtime material batching.

Native GLB SHA-256: `d15347af78f1264d86d1f8d2411f50f4bd6c2766252337fac7f646781602e08e`.
Blender .blend SHA-256: `8633fa3c07600b8ed228c06b58e7f0dbc40d93b531923042e472d45dec79acc1`.
Unity round-trip GLB SHA-256 (not committed): `00cb5d27ef4b5d2c47ee0a1926fd84482cbbacfb877f0fa5e9261926e507dc18`.

Studio preview image uses Blender Cycles, AgX and a neutral floor; live browser fixture uses a light-gray environment and standard Three.js PBR. Desktop/mobile browser console emitted GPU `ReadPixels` stall warnings during screenshot capture; no application load error was observed. These warnings are environment/performance related and not evidence of a production FPS guarantee.

## Prior deployment regression also corrected

Commit `aad703e` previously broke GitHub Pages CI at `scripts/catalog.mjs:86`, because `models/chibi-visitor-demo/metadata.json` did not provide required `display.previewRotationY`. This release adds required metadata `display`, `accuracy_notes`, `attribution` and `rights` to the preceding v1 entry. Both v1 and v2 metadata were validated by the current catalog validator. The v1 GLB itself independently passed Khronos with 0 errors and 0 warnings.

## Remaining gates

Human visual approval, genuine deformable character rig, realistic walk/run/sit animation, mobile physical-device FPS, Unity appearance equivalence beyond mesh/material counts, and real Mall integration remain untested. Do not claim production character animation or complete physical-device compatibility.
