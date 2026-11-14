# Mall Glass Showcase

Original Shopping Mall list 011 asset: an upright modular retail display tower, not the sloped food-display cabinet. It is an unbranded illustrative prop with a hollow interior, transparent glass side/back/front panes, three independently editable shelves, neutral aluminium frame, opaque plinth, separate door pivot and handle, and a real `DoorOpenClose` clip authored at frames 1/30/60.

Geometry uses metres, Blender +Z up / -Y front, floor-centred origin, and exports glTF +Y up / +Z front. Fixed budgets are under 10,000 triangles, 80 mesh primitives, and 1 MB. No merchandise, product certification, or engineering performance is claimed.

Generate and validate on the required host after the Blender 4.0.2 wrapper is available:

```sh
/srv/agent-workstation/workspaces/blender-mall-four-20261112/blender-local.sh --background --threads 2 --python-exit-code 1 --python models/mall-glass-showcase/generate.py
/home/ai-agent/.local/bin/node models/mall-glass-showcase/validate.mjs
/home/ai-agent/.local/bin/node --test tests/mall-glass-showcase.test.mjs
```

## Verified locally (2026-11-14)
PASS: 1,712 triangles, 96,840 GLB bytes, 20 mesh primitives, 5 materials, no textures, 1 DoorOpenClose animation. Khronos0 errors/0 warnings. Closed dimensions0.75m wide x1.8m high x0.532m deep including handle. Transparent panes/shelves and outward door sweep sampled across all60frames; source-edit proof checks changed vertices and roughness, saved/reopened/re-exported and canonical source hash unchanged.

PASS: actual five studio render views, desktop/mobile-width gallery and animated open preview inspected. Chromium1440/768/390 gallery loads by actual GLB SHA, orbit/zoom/exact reset/close/reopen cycles; isolated AnimationMixer changed pixels/exact reset. Gallery playback UI and physical Android/iOS are not claimed. Build and focused tests pass; existing CI remains unchanged.

Source-review corrections: door's initial swing direction would enter the shelves; corrected outward105deg. Handle moved to latch side and shelves use glass rather than opaque metal. Initial open camera framing cropped the door; corrected framing and actual final preview inspected. Reopened source proof operates on a copy. Codex environment could not resolve external Git object alternates; host materialized standalone objects and checked integrity. No protection or approval bypassed.

Catalog: independent mall-retail-showcases collection, preserves all484 existing entries AND their collection membership; not inserted into fixed four-item Mall Essentials. Production source is initial Shopping Mall list011, not an inferred ID in the500 master list.

Release: localPASS, remote CI/Pages pending. Reports folder contains source, GLB, build and browser evidence.

2026-11-14 follow-up: independent review found clearance loop action paused after LoopOnce end. Reset action before sweep and added actual midpoint angle assertion, rechecked all60frames with unchanged GLB;PASS. Prior animation pixel proof remained valid.
