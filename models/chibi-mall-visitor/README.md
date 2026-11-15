# Chibi Mall Visitor

A static, full-body character modelled in Blender to follow the supplied chibi visitor reference. The blue short-sleeve hoodie, navy shorts, high-top sneakers, watch, satchel and daypack are modelled on all sides. The side-parted fringe has three broad overlapping locks with rounded roots and tapered tips. The cheek volume and feathered vertex-colour blush sit beneath the outer eyes, above a tapered chin. The fixed smile has a deeper opening, tapered upper teeth and a domed coral tongue. The side-by-side comparison uses the supplied reference as its left panel.

- `chibi-mall-visitor.glb`: character only, with a single placement root, glTF +Y up and front +Z. No animations, armature, morph targets, external textures or UI.
- `scene.blend`: editable source with separate feature, clothing and accessory collections, plus a portrait studio.
- `preview.png`: portrait rendered in Blender. The pedestal, backdrop, lights and camera stay in the studio scene.
- `reference-comparison.webp` pairs a face crop from the supplied reference with a front render of the reimported GLB at matched head height.
- `face-comparison.webp` preserves the earlier two sculpt stages for comparison.
- `glb-three-quarter.webp`: the exported GLB rendered independently in desktop Chrome using Three.js.

To rebuild with Blender 5.1.2, run from the repository root in a fresh background process:

```sh
blender --background --factory-startup --python-exit-code 1 --python models/chibi-mall-visitor/generate.py
```

The generator replaces the blend, GLB and portrait in this directory. Set `CHIBI_OUT` to write to another directory, or set `CHIBI_DRAFT=1` for a lower-resolution portrait only. No add-on or downloaded asset is required.

Local verification: Khronos glTF Validator returned no errors, warnings or informational messages for the 1,644,488-byte GLB. Three.js loaded 136 meshes, drawing 97,824 triangles. Front, side, rear and three-quarter views were rendered in desktop Chrome. This is a standalone local asset; it is not registered in the gallery or published.
