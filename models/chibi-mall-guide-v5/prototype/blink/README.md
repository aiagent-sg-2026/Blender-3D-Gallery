# Step 3 prototype: blink, brows, cheeks (2026-11-15)

Question: can a shape-key blink hide the eyes cleanly, and where should the keys live? Prototype only: an ellipsoid head (about 14.5k triangles with eyes), no body, no rig, no mouth cavity, no texture, flat colours. All numbers are starting values in `build.py`. Not a model of the guide.

## Run

```sh
for M in lid eyes; do BLINK_MODE=$M blender --background --factory-startup --python-exit-code 1 \
  --python models/chibi-mall-guide-v5/prototype/blink/build.py -- /tmp/blink-out; done
for M in lid eyes; do node models/chibi-mall-guide-v5/prototype/blink/shoot.mjs /tmp/blink-out /tmp/blink-out/shots $M; done
```

`shoot.mjs` needs the repository's `playwright` and `three`; it serves the repo root and screenshots headless Chromium (software GL) with the repository's Three.js 0.187.0. Blender 5.1.2.

## Two blink methods compared

| | `lid`: skin covers the eye (key on `Head`) | `eyes`: eyes sink behind the skin (key on a merged `Eyes` mesh) |
| --- | --- | --- |
| Front-facing eye vertices visible, open | 157 of 273 per eye | 314 of 546 (both eyes) |
| Visible at blink = 1 | 13 and 15 (slivers at the lower edge) | **0** |
| Visible at blink = 0.5 | 132 and 133 | 102 |
| Look at blink = 1 | the skin swells into two bumps, reads as a swollen lid | clean skin, no bump |
| Keys per mesh | `Head`: smile, surprised, blink | `Head`: smile, surprised; `Eyes`: blink |

Visibility is a ray cast from the front against the evaluated head mesh, counted over eye vertices whose normal faces forward. It measures geometry, not how a lash line or texture would look.

## Findings

1. The `eyes` method hides the eyes fully and looks clean; the `lid` method does not (slivers remain and the skin bulges). Recommendation: `eyes`, with a lash line from the face texture.
2. Consequence for the standard: the three keys then sit on two meshes (`Head` and `Eyes`), so the runtime must drive each mesh by key name. Both meshes loaded in Three.js with their names intact (`Head`: smile, surprised; `Eyes`: blink). An untested alternative is one merged head-and-eyes mesh with all three keys and two material primitives.
3. Problems the prototype exposed:
   - The eye opening is the intersection of a flat eye ellipsoid with the curved head, so it came out as slanted crescents, not a designed shape. The real head needs a modelled opening or a texture-defined eye.
   - At 35 degrees the near-edge eye pokes past the head silhouette.
   - The smile key lifts the cheek over the lower eye; it reads as a squint but is too strong. It needs tuning.
   - Brow and mouth changes are barely visible without a texture; mouth has no cavity.
4. Not covered: textured eyes, mouth interior, body, rig, performance, a real browser GPU, the gallery viewer and the mall runtime.

## Files

`build.py` (build and measure), `view.html` and `shoot.mjs` (Three.js check), `build-report-*.json` (measurements and config), `shots/` (screenshots: front views of both methods and the `eyes` keys, plus one 35-degree view).
