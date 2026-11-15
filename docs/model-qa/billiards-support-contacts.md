# Billiards support-contact regression ownership

Repeated placement defects appeared in independently reviewed pack assets:
table sights/slab, the rack above cloth, then chalk above a wooden rail.
All looked plausible in broad scene previews; actual intended contact was
missing. MODEL-0005's measured 1.5 mm gap reproduced both visually and in an
exported-geometry test, before applying a 1.6 mm root translation.

Measure the actual supporting geometry and intended footprint. Do not derive
contact from an asset-root coordinate, an old remembered height or a material
label. Curved/beveled edges and pocket openings can invalidate a bounding-box
comparison alone. Chalk now verifies five footprint rays against actual rail
triangles, including flat-top height, and independently constrains penetration.
A 0.1 mm overlap is intentional for these reviewed static contacts.

Permanent checks have separate model ownership:

- `tests/pool-table.test.mjs`: all twelve sights seated in their rails, and slab
  supported by the cabinet without moving the playing surface.
- `tests/triangle-rack.test.mjs`: rack seated on preserved cloth; separate
  geometry/normal/capacity checks also remain mandatory.
- `tests/chalk.test.mjs`: actual rail triangles cover the chalk footprint,
  bottom contact stays within tolerance, and core/sleeve scale/contact remains.

The generator owns authored placement; revision-guarded one-time migrations
preserve historical baselines and scope the saved repair. Expected contact in
regressions comes from the supporting exported surface, not from repeating
the migration's translation constant. Only assets intentionally resting on a
support have this requirement; floating/orbiting subjects need their own intent.

Keep this lesson project-local with its verified source and exported checks.
No global Skill or KB memory was written. Main/Actions/production release
acceptance remains a separate gate in the campaign tracker.
