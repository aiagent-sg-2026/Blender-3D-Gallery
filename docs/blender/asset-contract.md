# Reusable asset production contract

<!-- KB-SUMMARY-START -->
A reusable asset needs a stable ID, category/tags, dimensions and units, local origin/facing, pivots/connectors, editable source, export, materials/images, rights and measured evidence. Specify required topology and target budgets by asset role; do not promote one project's limits to every model. Record generator inputs/seeds and distinguish procedural rebuild from exporting a manually edited source. State repeat pitch/shared components, moving hierarchy, clip names and runtime responsibilities where relevant. Keep visual geometry, colliders, business interaction and gallery metadata as separate interfaces. Preserve a tested export's identity and record any simplification or decoder requirement. Source/editability proof, GLB validation and runtime acceptance are separate deliverables. Installation or a thumbnail alone does not establish that a model is interactive, optimized or ready for publication.
<!-- KB-SUMMARY-END -->

## Minimum handoff

| Contract | Examples of required information |
| --- | --- |
| Identity | Stable asset ID, revision, role and scene/theme tags |
| Geometry | Metre dimensions, origin, facing, bounds, pivots and connector planes |
| Appearance | Material slots, texture dimensions/color interpretation, UV assumptions and image provenance |
| Motion | Hierarchy, Actions/clips, time range, root-motion policy and target consumer |
| Delivery | Source, generator/configuration, GLB, validation, previews and tested artifact hashes |
| Rights | Authorship, third-party inputs, permitted use and unresolved redistribution terms |

Store per-project classification and commercial content outside the generic Blender domain. A scene theme and an object type are different metadata axes; choose their actual vocabulary in the consuming project's contract.

## Source versus derivative

Preserve an editable native model and its external dependencies. A generated export is a delivery representation, not a replacement for every authoring feature. For a scripted asset, offer explicit rebuild/export paths and document which one preserves saved edits.

The official [Blender glTF documentation](https://docs.blender.org/manual/en/5.1/addons/import_export/scene_gltf2.html) describes an interchange pipeline. The additional handoff fields above are engineering recommendations drawn from [local project practice](../verification/foundation-v1/module-fit/README.md), not mandatory fields in the glTF specification.

Use [quality and delivery](quality-delivery.md) for verification ownership. New asset variants should have distinct identities when their interfaces differ; do not conceal dimensional changes in unrelated model updates.
