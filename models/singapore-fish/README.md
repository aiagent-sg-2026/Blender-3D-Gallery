# Singapore & Malaysia Fish Collection

60 original stylized Blender fish studies, FISH-001 through FISH-060, following the user-supplied names, priorities and visual brief. Seafood-market, freshwater, marine and ornamental entries share one searchable collection in the 3D Model Library. `species.json` is the authoring source of truth; each row contains slug, localized name, English/local aliases, priority, silhouette, palette, markings and illustrative length in metres.

Each slug directory contains:

- `sources/<slug>.blend`: independent editable scene with mesh anatomy, materials and preview camera.
- `exports/model.glb`: animated, Y-up glTF 2.0 asset; geometry originates in Blender.
- `previews/hero.png` and `thumbnail.webp`: Blender studio render and lightweight gallery poster.
- `metadata/model.json`: stable FISH identifier, priority, source location, display settings and accuracy limits.

No third-party models, textures or scripts were downloaded. Geometry and materials are original. Reuse in the owner's projects is authorized; public redistribution terms have not been specified. Git publication is separate from application deployment; no deployment is claimed here.

These are stylized reference studies, not scientific identification models. Common names in the brief overlap and may refer to different species; the collection retains the supplied names as aliases without asserting taxonomic equivalence. Dimensions are illustrative asset sizes, not measured specimens or species limits. Simplified bodies, fins, scale tiles, markings, gills, mouths, barbels and eyes support scene use. Each source contains an editable 11-bone rig. One seamless `Swim_Loop` clip drives the tail, body and fin skin weights. Timing varies from 1.6 to 3.2 seconds by body family: ray wing beats, eel-like body waves, or tail propulsion with fin stabilization. No puffer inflation, fish-school trajectory simulation or dried anchovy variant is included.

## Reproduce

Use Blender 5.1.2 (the authoring version) or a compatible version with the built-in glTF exporter. From the repository root:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --python models/singapore-fish/generate.py
uv run --with pillow python models/singapore-fish/register.py
node models/singapore-fish/validate.mjs
node models/singapore-fish/test-animation.mjs
/Applications/Blender.app/Contents/MacOS/Blender --background --python models/singapore-fish/inspect-sources.py
npm run build
node models/singapore-fish/test-browser.mjs
node models/singapore-fish/test-swim-browser.mjs
```

Pass one or more slugs after `--` to generate.py to regenerate only those entries. The generator creates isolated scenes rather than opening or editing the user's current Blender scene. The registration step preserves other catalog collections. Pillow is used only for poster compression and the contact sheet, not for model generation.

See `verification.md`, `validation.json`, `source-validation.json`, `contact-sheet.jpg` and browser screenshots for local acceptance evidence.

## Animation playback

The library loads the GLB on demand. Fish viewers play swimming automatically unless the system requests reduced motion. The Play/Pause swimming control is available in either mode. Playback suspends when the document is hidden and disposes its mixer, skeleton resources and controls when closed. The viewer uses the embedded clip; it does not synthesize animation outside Blender. The source hierarchy stays organized beneath its ASSET root; exported skinned mesh nodes are flattened to scene roots with identity transforms as required by glTF skinning. The registry therefore does not claim a single runtime root.

`swim.py` owns rigging and loop parameters, imported by `generate.py`. `render-motion.py` renders representative source poses for preview review. GIF previews are in the Barramundi, Stingray, Swamp Eel and Betta `previews` directories. `animation-validation.json` measures deformed GLB tail and fin vertices and checks every clip endpoint.
