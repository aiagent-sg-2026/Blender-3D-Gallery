# Procedural geometry and architectural interfaces

<!-- KB-SUMMARY-START -->
Define a metre-based geometry contract with dimensions, local origin, facing, registration planes, repeat pitch and tolerances. A module's outer width, connector pitch and usable opening can differ. Align connectors and retain each shared post once; close a measured interface with an explicit adapter rather than hiding a mismatch by scaling. Inspect actual exported world geometry, including handles and moving leaves, for clearances. Use manifoldness requirements appropriate to the asset role. Keep source modifiers editable and inspect evaluated/exported topology; solver names and capabilities are version-specific. Test door motion, floor coverage, camera space and runtime colliders separately. Discrete sweep samples, component bounds and ray probes provide bounded evidence, not continuous collision or construction certification. Keep scene-specific dimensions and navigation budgets in project records.
<!-- KB-SUMMARY-END -->

## Build a small interface contract

Record floor finish elevation, shell/profile height, pivot axis, connector positions, nominal gap, allowed rotation and shared-component policy. Distinguish the room's planning grid from its clear interior. Model an opening's fixed frame, movable parts and collision representation explicitly.

For repeated bays, verify first, middle and terminal joints. End returns and corners need their own allocation; a successful two-piece preview does not prove a long run. A closed source box can still intersect its neighbour or leave an assembly gap.

## Topology and modifiers

The [Boolean modifier manual](https://docs.blender.org/manual/en/5.1/modeling/modifiers/generate/booleans.html) distinguishes solver assumptions. Query the installed modifier RNA for Python enum identifiers; UI labels and older examples can differ. Inspect slivers, normals, duplicate internal faces and material assignment after a Boolean.

A read-only native inspection on 5.1.2 returned `FLOAT`, `EXACT` and `MANIFOLD` for the `solver` enum. This confirms available identifiers, not that every solver succeeds on every input.

Keep authoring modifiers in the source. Exporting a temporary evaluated representation can preserve editability while making delivery topology explicit. In Edit Mode use BMesh rather than stale object-mode arrays; see the [BMesh API](https://docs.blender.org/api/current/bmesh.html). Do not assume every valid visual asset must be a watertight printing solid: establish that requirement by role.

## Clearance method

1. Measure the exported frame in its own coordinates.
2. Measure usable space with moving hardware present.
3. Sample each leaf separately and together against nearby geometry and the floor union.
4. Drive the actual controller through the opening, including closed and occupied states.
5. Check the camera separately from the body collider.

The [Foundation module-fit record](../verification/foundation-v1/module-fit/README.md) is a project example of these steps. Its door widths, capsule radius and draw-call cap are not defaults for other projects. Reuse the method and establish new expected values from the new contract.
