# Sea

A real-time GLSL rendered with React Three Fiber. Open water wrapped around a
sphere, hanging in mid-air, with a siamese fighting fish swimming inside it.
Swell, chop, whitecaps, dispersive refraction and caustics are all shader work.

**[Live demo](https://0s0ka.github.io/sea/)**

## How it works

Three passes per frame. `Water` subscribes to `useFrame` with priority 1, which
turns off R3F's automatic render, and composes the frame by hand: the scene
without the water into a colour target, the water's back faces into a distance
target, then the visible frame. Subtracting the front face distance from the
back one gives the thickness of water under each pixel, and refraction strength,
absorption and the subsurface glow all read from it.

**Geometry.** An icosphere, welded with `mergeVertices` after `uv` and `normal`
are dropped — they differ between adjacent faces and would block the merge, and
the shader computes its own normal anyway. 144k vertices come out as 24k, which
matters because the vertex shader evaluates the height field three times per
vertex: once for the displacement and twice more for the normal.

**Swell.** Three directional waves. On a sphere a direction is a unit vector `d`
and the phase is `dot(p, d)`, which makes lines of constant phase great circles.
The wave wraps the whole ball and there is no seam at the poles, which is the
part a naive port of Gerstner waves gets wrong. Crest sharpness raises
`0.5 + 0.5·sin(x)` to a power, pulling the profile toward narrow crests sitting
above wide flat troughs.

**Chop.** Fbm drifting through its own noise domain. The octave count is
fractional, so the next octave fades in as the sea state rises instead of
popping into existence.

**Normals.** Rebuilt analytically. A tangent frame is built at each vertex, the
two neighbouring points are displaced by the same field, and the normal is their
cross product. Skip this and the lighting still reads as a smooth ball no matter
how large the waves get.

**Optics.** Screen-space refraction with one ray per colour channel for
dispersion, Beer-Lambert absorption against the measured thickness, a
Fresnel-weighted sky reflection, a sun highlight, and a subsurface term that
lights thin crests from behind. The sky is procedural and lives in one
`lib/sky.glsl` used by both the background dome and the reflection term, so the
two cannot drift apart.

**Caustics.** Two noise fields at different scales and speeds; where their
values agree a bright line appears, and taking that difference to a high power
leaves a mesh of thin filaments. The pattern is projected onto the plane
perpendicular to the sun, so it falls along the light rather than sticking to
the world axes.

Nothing about it is a fixed value. Caustics are the surface focusing sunlight,
so all four parameters are read back off the wave uniforms every frame, after
those have been damped, which means they inherit the same easing and stay right
even if the CALM and STORM tables are re-tuned. Brightness comes from steepness,
amplitude times frequency, because that is what decides how hard the surface
bends a ray: flat water focuses nothing and the pattern all but disappears.
Scale follows the chop frequency, since shorter waves focus light into a finer
mesh, drift follows the chop speed, and sharpness opens into a broad wash over
calm water and closes into filaments under chop. It is injected into the model's own `MeshStandardMaterial`
through `onBeforeCompile` and added to `totalEmissiveRadiance`, which makes it
behave like light instead of a decal, and leaves every texture and PBR parameter
of the model intact. The same patch adds the swim wave to the vertex stage,
after `<skinning_vertex>` so it layers on top of skeletal animation.

## Quick start

Requires Node 20.19+ or 22.12+.

React is pinned to the 19.2 line on purpose. React Three Fiber 9.7 declares
`react@">=19 <19.3"`, so once 19.3 shipped to `latest` a caret range started
resolving to a version its reconciler will not accept and `npm install` failed
with `ERESOLVE`. Lift the pin when a fiber release widens that peer range.

```bash
git clone https://github.com/0s0ka/sea.git
cd sea
npm install
npm run dev
```

Then open the printed URL, usually `http://localhost:5173`.

## The fish

`public/models/betta.glb` is "Betta Splendens" by BlueMesh, CC BY 4.0 (see
Credits). It carries a six second skeletal swim cycle, which plays on loop while
the rig carries it around a closed path inside the sphere.

It came out of Sketchfab as a 9.5 MB glTF and was packed with:

```bash
npx @gltf-transform/cli optimize scene.gltf public/models/betta.glb \
  --compress false --simplify false \
  --texture-compress webp --texture-size 2048
```

1.27 MB, or about 1 MB over the wire once the server gzips it. Two of those
flags are deliberate. `--compress false` because Draco and meshopt both quantise
positions: Draco then wants an external decoder, and meshopt leaves the geometry
in a normalised local space that the swim shader would have to compensate for.
Nearly all of the saving is in the textures anyway. `--simplify false` because
the default pipeline decimates the body by about a quarter, and the veil fins
are the whole point of a betta.

Two things the loader fixes up, both worth knowing about if you swap the model:

- Sketchfab wraps its exports in a fully transparent placeholder cube. Left
  alone it widens the bounding box, adds a draw call, and — since the caustics
  patch writes into `totalEmissiveRadiance` — lights up as a glowing crate
  around the fish. Anything fully transparent and untextured is dropped.
- The body material is exported as `alphaMode: BLEND`, but its base colour alpha
  is 97% pure 0 or 255. It is a cutout mask for the fin silhouettes, not
  translucency. As blending it would land in the transparent pass with depth
  writes off and the fins, body and eyes would sort against each other at
  random, so it is converted to `alphaTest`.

The scene still runs with no asset at all: delete the glb and a procedural fish
built from primitives takes over, driven by the same patched material.

To swap in a different model, the `FISH` block in `src/settings.js` is the only
place to touch. Lengths there are fractions of the model's own bounding box, so
a model exported at a different scale needs no renumbering.

| Field         | What it does                                                 |
| ------------- | ------------------------------------------------------------ |
| `size`        | body length as a fraction of the sphere radius               |
| `forwardAxis` | local axis the head points down; `-y` for the bundled model  |
| `sideAxis`    | local axis the body bends along                              |
| `yaw`         | extra spin about the vertical, if the model does not face +Z |
| `bend`        | swim wave amplitude, as a fraction of body length            |
| `bendReach`   | how far forward the bend spreads, 0 tail only, 1 whole body  |
| `bendWaves`   | full sine cycles along the body                              |

The swim path is not a fixed circle either. Its radius is the sphere radius less
the deepest wave trough and less the half-diagonal of the fitted body, so the
loop tightens as the sea gets up and the fish never breaks the surface, fins
included, however far it banks.

`bend` is set to zero whenever the loaded model brings its own animation clip:
there is no sense layering a procedural bend on top of a hand-authored swim.

## Controls

Drag to orbit, scroll to zoom. Panning is disabled and the distance is clamped
so the camera cannot end up inside the water.

The lil-gui panel exposes two dials, and nothing else.

| Control     | What it does                                                       |
| ----------- | ------------------------------------------------------------------ |
| sea state   | Blends the whole wave and foam set from flat calm through to storm |
| time of day | Sweeps the sun and the sky from dawn through noon to dusk          |

Everything a viewer would otherwise be able to break — optics, foam response,
caustics, the fish rig — is derived from those two in `src/uniforms.js`. Foam
ramps in behind the waves, so flat water carries none and whitecaps only appear
once there is enough swell to break on. Time of day moves sun elevation, azimuth
and colour together with the zenith and horizon tints, and the key light reads
the same sun, so the crest highlight, the caustics on the fish and the glow in
the dome stay consistent. Colours interpolate in linear light: `Color.set()`
reads a hex string as sRGB and converts on the way in.

Both dials write straight into `CONTROLS`, a plain object outside React, and the
uniforms are damped toward it every frame. Dragging costs zero re-renders, and a
jump from calm to storm plays out as rising weather rather than as a swapped
frame.

## Credits

This work is based on "Betta Splendens"
(https://sketchfab.com/3d-models/betta-splendens-f4eeb7f50ad24873842bd954ad27d23b)
by BlueMesh (https://sketchfab.com/VapTor) licensed under CC-BY-4.0
(http://creativecommons.org/licenses/by/4.0/)

The noise, caustics and water shaders were written for this project.

## Licence

MIT. See [LICENSE](./LICENSE).
