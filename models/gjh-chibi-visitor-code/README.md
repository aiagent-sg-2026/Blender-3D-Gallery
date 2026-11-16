# GJH Chibi Visitor (Male, 18)

A 1.3 m, 2.5-head chibi mall visitor built entirely from new Blender Python code to
the owner's character sheet v1.0 (`reference/character-sheet-v1.webp`). It has a white tee,
wide cuffed jeans, chunky white sneakers, a black backpack and a watch on the left wrist.
The model carries seven face expressions and twelve animation clips.

- No generated or downloaded meshes (no TRELLIS, Hunyuan3D or RunPod) and no code from other
  models in this repository. Only the repository-wide checks (`npm run validate:assets`,
  `npm test`, catalog rules) are shared.
- Plan: `docs/gjh-chibi-visitor-code-plan.md`. Gate results: `qa/run-001/report.json`.

## Build

```bash
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python models/gjh-chibi-visitor-code/src/build.py -- --out models/gjh-chibi-visitor-code --keep-going
```

Then run the browser check and the tests:

```bash
node models/gjh-chibi-visitor-code/qa/check-glb.mjs
```

```bash
node --test tests/gjh-chibi-visitor-code.test.mjs
```

The build takes about 30 seconds with renders (`--no-renders` skips them). Without
`--keep-going` it stops at the first failed gate; with it, every stage runs and the exit
code is still non-zero if any gate fails.

## Layout

| Path | What it holds |
|---|---|
| `src/config.py` | Every number: landmarks measured from the sheet, sections, colours, budgets, rig joints |
| `src/mesh.py` | `Part` container, superellipse rings, lofts, sweeps (incl. surface-following), object merge |
| `src/reference.py` | Stage 0: crops the sheet views and extracts silhouette masks |
| `src/head.py` | Skull, ears, neck, projected decal face and its 7 shape keys |
| `src/body.py` / `src/clothes.py` / `src/props.py` | Arms and hands; tee, jeans, sneakers; backpack, straps, watch |
| `src/hair.py` | Hair cap plus rows of feather locks and a swept fringe |
| `src/materials.py` | Palette materials and painted textures (face atlas, hair locks, denim) |
| `src/rig.py` | 20 deform bones, 3 sockets, code-computed skin weights |
| `src/anim.py` | 12 clips (two-bone leg IK in code), pushed as NLA tracks |
| `src/render.py` / `src/export.py` | Studio renders, silhouettes, GLB export, previews |
| `src/build.py` | Entry point and gates |
| `qa/silhouette.py`, `qa/checks.py` | Silhouette comparison, measurements, overlaps, weights, deformation, motion |
| `qa/check-glb.mjs` | three.js browser check (Playwright) |
| `exports/`, `sources/`, `previews/`, `textures/`, `qa/run-001/` | Outputs |

## Contents of the GLB

- 8 skinned meshes (Body, Face, Hair, Tee, Jeans, Shoes, Backpack, Watch), 10 materials
  (10 draw calls), 3 embedded PNG textures, 7,964 triangles, about 0.8 MB.
- One skin: `root, hips, spine, chest, neck, head`, `shoulder/upper_arm/forearm/hand .L/.R`,
  `thigh/shin/foot .L/.R`, plus sockets `SOCKET_Back`, `SOCKET_Wrist_L`, `SOCKET_Hand_R`.
- Morph targets on `Face`: `blink, happy, wink_L, surprised, thinking, excited, talk`.
- Clips (30 fps, in place): `Idle, Walk, Run, Sit, Wave, Talk, ShopBrowse, PickUp, Inspect,
  Point, Nod, Cheer`. Every clip also keys the face weights, so switching clips resets the face.

The gallery viewer shows the static rest pose. Clips and expressions are for runtime use and
are verified by `qa/check-glb.mjs`.

## Deviations from the plan

- No separate blockout mesh: the proportion gate (stage 1) measures the detailed model.
- Rest pose has the arms hanging as on the sheet, not a 30-degree A-pose, so silhouettes can
  be compared directly with the sheet.
- The sheet's white sneakers match its background colour, so the sheet mask is not trusted
  below 0.10 m and silhouette gates ignore those rows.
- `Default` is the basis face, so there are seven shape keys (six sheet expressions minus
  Default, plus `blink` and `talk`).
- The mouth-open shape key is named `talk` (the plan said `talk_open`).
- Hair is a thick cap covered by rows of feather locks plus a swept fringe, instead of a
  single shell cut into 6-8 locks (that read as a helmet in early renders).

## Known limitations

- Two gates stay open (see `qa/run-001/report.json`): the worst rows of the hair outline miss
  the sheet by about 22 px (means pass at about 6-7 px), and inner knee/elbow triangles compress
  below 20 % of their rest area in the deepest bends (no visible tearing in close-ups).
- Hands are mittens with a thumb (the 20-bone rig has no finger bones).
- The gallery shows the rest pose only; clips need a runtime player.
- Open review items: the sheet's parted, swept fringe is not reproduced, and each strap keeps a
  small corner where it turns under the arm.

See `qa/run-001/report.json` and the plan document for gate results and known limitations.
