# Round Event Platform

Original plain circular event platform for the mall, category **Mall Fixtures**.
No external geometry, textures, fonts, brands, text, lights, stairs or ornamental
rim. The existing rectangular `outdoor-stage` is untouched and was not reused.
Candidate reconciliation is in `reports/duplicate-search.json`.

Measured GLB: 8 x 0.3000000119 x 8 m (X/Y/Z), floor-centred origin, Y up,
front +Z. Blender authoring uses Z up and front -Y. One closed editable source
mesh exports to one stored GLB mesh with three opaque material primitives:
2,304 triangles, 1,938 exported vertices, 79,116 bytes. Three base-color and
roughness material roles, `Platform_Top`, `Platform_Edge`, `Platform_BaseTrim`,
let the scene apply its theme. No colliders or animations are included.

The top edge has an 8 mm chamfer; a small inset graphite foot finishes the
base without a projecting rim. The 192-sided outline has a maximum theoretical
chord deviation of 0.536 mm from a 4 m radius circle. This is a visual asset,
not structural or accessibility certification.

UVMap is exported: planar top/bottom discs and two half-circumference side
strips share a padded, nonoverlapping unit atlas. Source area measurements give
0.0574998-0.0576124 UV units/m (under 0.2% density variation). There are no
mirrored or stacked islands and no textures. The UV atlas is available for
future baking; scalar PBR materials need no baking. No texel-density claim is
made without an image resolution.

From this directory:

```sh
/opt/homebrew/bin/blender --background --python generate.py
/opt/homebrew/bin/blender --background --python generate.py -- --export-source --skip-render
/opt/homebrew/bin/blender --background --python inspect_sources.py
node validate.mjs
```

Default generation deterministically rebuilds source, GLB and four PNG views:
hero, front, side and 3q. `--export-source` exports saved edits without rebuilding.
Only the asset hierarchy is exported; the preview studio is source-only. The
source check reopens the native file, verifies manifold geometry and UV scale,
compares source replay with the delivered GLB, then saves/reopens a disposable
mesh/material edit and verifies it through an independent Blender GLB import.
The canonical source is unchanged by this check.

Create a lightweight card thumbnail with Pillow (not required by the generator):

```sh
python3 -c "from PIL import Image; Image.open('previews/hero.png').resize((640,480)).save('previews/hero.webp',quality=88,method=6)"
```

From the repository root run `npm run validate:assets`, `npm test`,
`npm run build`, then `node models/round-event-platform/check-page.mjs`.
The page check uses the repository harness, checks the consumed GLB hash and
renders at 1440 x 900 in headless Chromium, with keyboard orbit/zoom. Its
screenshot is `~/Documents/MallQueue/reports/round-event-platform-page.png`.
Evidence is in `reports/`. Physical devices, WebKit, the complete mall scene,
sustained performance and deployment are not verified by these local checks.
