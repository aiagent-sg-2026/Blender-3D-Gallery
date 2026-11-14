# Billiards functional scale checks

MODEL-0004 initially passed silhouette, topology, shading and Viewer checks,
but a follow-up size check found that its rack intersected a five-row pack of
fifteen touching balls at the pack's authored 57.15 mm diameter. Initial commit
cb0c0c60 was therefore not accepted; its own Actions run was cancelled before
Pages deployment. No subsequent model was started.

A functional prop needs its intended contents checked at the actual scale.
A plausible outline is insufficient. Freeze the original dimensions and
reproduce the failure against the real exported geometry before resizing.
Keep contained-object dimensions and packing fixed; do not shrink the balls
to make the rack pass. Here the seven rack checks retain the original five
joint/normal/support checks and add two actual triangle/sphere collision
checks, one per export. The initial revised rack passes the five original
checks but fails both capacity checks.

`models/eight-ball-billiards/rack_geometry.py` owns the 350 mm equilateral
centerline shared by generator and guarded follow-up migration. Only three
rack bar transforms and longitudinal coordinates change; radius, UVs,
face/material assignments, seating and all unrelated source/export payloads
remain preserved. Nineteen rack/table/cue regressions and 645 unit tests pass.
The capacity analysis is supporting geometry reasoning; direct exported
triangle/sphere checks and multi-angle native views remain required.

The source/import and diagnostic witnesses are documented under MODEL-0004.
Temporary witness spheres are never saved or exported into product assets.
Final main/Actions/production acceptance is a separate release gate recorded
in the campaign tracker, not implied by this local lesson.
