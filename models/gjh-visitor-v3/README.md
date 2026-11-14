# GJH Mall Visitor v3 — development preview

New character built from the owner's "GJH Visitor v3.0" sheet: adult male, A-pose, navy open zip hoodie over a white tee, khaki chinos, white sneakers, black backpack, blue lanyard with ID card, steel watch on the left wrist, wavy black hair. Independent of v1 and v2.

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --python models/gjh-visitor-v3/generate.py
node --test tests/gjh-visitor-v3.test.mjs
```

Conventions match v2: glTF +Y up, metres, floor Y=0, front +Z, 1.78 m. Skinned humanoid with the 12 contract clips `idle`, `walk`, `run`, `turn_left`, `turn_right`, `sit_down`, `stand_up`, `pick_up`, `carry`, `wave`, `point`, `push_cart`; interaction clips are poses only, the mall owns collisions, seats and props. Call `createVisitorCustomization(scene)` from `customization.js` before display (hair wavy/short and colour, hoodie on/off, skin tone, backpack, badge, watch; `dispose()` when discarded).

Layout: `generate.py` (geometry, materials), `rig.py`, `animations.py`, `export.py`, `validate.py` (re-imports the GLB in Blender); Node tests in `tests/gjh-visitor-v3.test.mjs`. Known gaps: face and hair are simpler than the sheet; no per-part names like the plan's `GJH_VISITOR_V3` tree; no Python unit tests, LOD, no textures, no device performance data; the sheet's triangle/texture targets are unverified.
