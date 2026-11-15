# Chibi character framework — design proposal (v0.1)

Status: **proposal, 2026-11-15**. Nothing is implemented. The owner asked for a general framework after being advised to wait for a second character; this document records why the evidence supports building it now and how, extracting from existing code rather than designing in the abstract. Related: [chibi character standard](chibi-character-standard.md), [Mall Guide v5 plan](chibi-mall-guide-v5/plan.md).

## 1. Evidence from the repository

Counts below are from a rough grep of `models/*/*.py` on 2026-11-15 and are not exact.

| Character | Generator size | Notes |
| --- | --- | --- |
| child-character, construction-worker, female-office-worker, male-office-worker, nurse, warehouse-worker | about 125 to 146 lines each | each carries its own small helpers (`mat`, `ell`) |
| gjh-mall-visitor (v1) | 207 lines | own `mat`, `ell`, `loft`, `path`, `node` |
| gjh-mall-visitor-v2 | 452 lines | already split: `rig.py`, `generate-lod.py` |
| gjh-visitor-v3 | 1,021 lines | already split: `animations.py`, `export.py`, generator |
| chibi-mall-visitor | 655 lines | plus `face_sculpt.py`, `hair_sculpt.py` |
| chibi-visitor-v4 | 1,060 lines | own `g_ellipsoid`, `g_loft`, `g_tube`, `Part`, `Projector`, fuse, AO bake |

The same geometry and material helpers are reimplemented many times, and v2/v3 already converged on a rig / animation / export split. The framework is therefore an extraction of existing practice.

## 2. Scope

In: a Python package, run in headless Blender or through the Blender MCP, that builds a chibi humanoid character from a spec. Out: automatic creation of good hair or faces (the framework supplies building blocks; character code decides the shape), a Blender extension UI (later), image-to-3D services, and changes to already accepted models.

## 3. Layers

1. `kit`: ellipsoid, loft, tube, sweep, fuse, AO bake, material creation. Merge v4 and GJH helpers.
2. `spec`: declarative character data: proportions, palette, part list, sockets, expression keys, clip list, budgets.
3. `builders`: head, hair, garments, limbs, shoes, props. Each reads the spec and is replaceable.
4. `rig`: humanoid rigid single-bone binding (about 17 bones), `SOCKET_*` sockets, skinned meshes exported as scene roots (see standard section 12).
5. `shapekeys`: smile, surprised, blink, with brows and cheeks.
6. `anim`: clip library (idle, blink, bouncy walk, calm walk, wave, hold-and-point, put sign down) and foot-contact baking checks as in GJH.
7. `export` and `qa`: export profiles (full, low-detail) and the G1 to G6 gates as callable functions.

## 4. Key decisions

- Spec-driven: character = spec + small override code.
- Two kinds of module: bpy-free (spec validation, naming, budgets, socket rules; testable with plain Python) and bpy-dependent (geometry, rig; tested with headless Blender plus GLB checks).
- The framework has a version recorded in each character's metadata so rebuilds are reproducible and G2 means something.
- Existing models are not touched; migration is opt-in.
- Location proposal: `tools/chibi-framework/`; each `models/<name>/` keeps only its spec, override code and outputs.

## 5. Risks

- Over-abstraction: extract bottom-up, and accept a layer only when two real users exist.
- Blender version: 5.1.2 is installed; the GJH README names 5.2.3. Declare supported versions and check them.
- Determinism: framework changes must not silently change older outputs; use a golden test (rebuild one existing character and compare hashes or explain differences).
- Scope creep: first version covers chibi humanoids only.
- Maintenance: there is no named maintainer; keep the first version small.

## 6. Phases (order, not durations)

1. Inventory duplicated helpers across `models/*/*.py` and decide what enters `kit`.
2. Extract `kit` and pass a golden test by rebuilding the smallest existing character (e.g. child-character).
3. Define the v5 spec and write bpy-free validation.
4. Rig, sockets, shape keys, animation: prove on a test model, then use on v5.
5. Build v5 on the framework and run gates G1 to G6.
6. Build the next new character on the framework as the second real user (older characters are not migrated).
7. Later: optional Blender extension UI.

## 7. Owner decisions (2026-11-15)

- Location and name: `tools/chibi-framework/`.
- Validation: Python only; no Node-side duplicate of the spec rules, so it does not run in `npm test`. Python tests run with plain Python (bpy-free modules) and headless Blender.
- Older characters: **none are migrated**; the framework serves new characters only. Consequence for the plan: phase 2's golden test may rebuild an existing character (e.g. child-character) only in a scratch location to compare output, never replacing the accepted model; and phase 6 (migrate an older character as a second user) is dropped. The second real user is the next new character after v5, so the "two real users" rule for accepting a layer is checked against v5 plus that character, or against the golden-test rebuild when only v5 exists.
- Versioning and review: the owner approves each framework version; a fresh agent does the independent review.

## 8. Open

- The golden-test target character (suggested child-character, the smallest) and what counts as a pass (identical hash, or documented differences).
- Supported Blender versions (5.1.2 installed; GJH README names 5.2.3).
