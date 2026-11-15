# Sources and evidence register

Reviewed 2026-11-15, Asia/Singapore. Version information is a dated observation and must be checked again before installation or migration. This register records what supports the handbook; it is not a compatibility certification.

## Official Blender sources

The versioned manual pages below were reviewed through official search-index excerpts where direct page fetches were blocked. Such excerpts support the specific claims in the linked chapters, not a claim that the complete manual or extension source was audited. Dynamic `current`/`main` API URLs can change. References pinned to 5.0 are explicitly identified; installed 5.1.2 RNA and experiments resolve the particular version-sensitive details tested here.

| Source | Supported subject | Evidence boundary |
| --- | --- | --- |
| [Operator API](https://docs.blender.org/api/current/bpy.ops.html) | Context, polling and operator execution | Dynamic API reference; only two polls calibrated locally |
| [Python threading gotchas](https://docs.blender.org/api/main/info_gotchas_threading.html) | Concurrent Python/Blender execution hazards | Dynamic API guidance, not an audit of the MCP server |
| [ID API](https://docs.blender.org/api/current/bpy.types.ID.html) | Datablock users and copies | Object/mesh sharing also tested locally |
| [Object API 5.0](https://docs.blender.org/api/5.0/bpy.types.Object.html) | Evaluated object and temporary mesh lifecycle | Version 5.0; not a blanket 5.1 signature guarantee |
| [Dependency graph 5.0](https://docs.blender.org/api/5.0/bpy.types.Depsgraph.html) | Original versus evaluated data | Version 5.0 example |
| [BMesh API](https://docs.blender.org/api/current/bmesh.html) | Edit-mode mesh access/update | Dynamic reference; current update signature inspected natively |
| [Command line 5.1](https://docs.blender.org/manual/en/5.1/advanced/command_line/arguments.html) | Flag ordering, background mode and Python exit code | Exception exit code tested; flags do not provide an OS sandbox |
| [Boolean modifier 5.1](https://docs.blender.org/manual/en/5.1/modeling/modifiers/generate/booleans.html) | Solver assumptions and limitations | Enum identifiers inspected; solver quality not benchmarked |
| [UV editing 5.1](https://docs.blender.org/manual/de/5.1/modeling/meshes/uv/editing.html) | UV scale and packing tools | Manual reference; density estimate is an engineering method |
| [glTF exporter 5.1](https://docs.blender.org/manual/en/5.1/addons/import_export/scene_gltf2.html) | Recognized material nodes and texture channels | Scalar material factors tested; textured appearance not tested |
| [glTF animation 5.1](https://docs.blender.org/manual/nl/5.1/addons/import_export/scene_gltf2.html) | Animation export modes and supported channels | Object translation tested; skin/morph/baking not calibrated |
| [Normal Map node 5.1](https://docs.blender.org/manual/en/5.1/render/shader_nodes/displacement/normal_map.html) | Normal convention and non-color input | No normal-map visual experiment |
| [Cycles baking 5.1](https://docs.blender.org/manual/en/5.1/render/cycles/baking.html) | Active image targets and baking setup | No new baking experiment |
| [Actions 5.1](https://docs.blender.org/manual/en/5.1/animation/actions.html) | Action slots and animation organization | One object Action/slot calibrated |
| [Armature modifier 5.1](https://docs.blender.org/manual/en/5.1/modeling/modifiers/deform/armature.html) | Bone/group deformation binding | No humanoid skinning or IK experiment |
| [Extension manifests 5.1](https://docs.blender.org/manual/zh-hans/5.1/advanced/extensions/getting_started.html) | Package metadata and declared dependencies | No extension registration/source audit |
| [Scripting introduction 5.1](https://docs.blender.org/manual/id/5.1/advanced/scripting/introduction.html) | Learning entry points | Roadmap sequencing is an engineering recommendation |

Language variants are linked where they supplied the reviewed official excerpt; the document version is the relevant compatibility marker.

## Official extension catalog sources

| Candidate | Published version/date observed | Minimum Blender declared | Authoritative listing |
| --- | --- | --- | --- |
| HiFi Architecture Builder | 4.6.7 / 2026-11-12 | 4.2 | [Version history](https://extensions.blender.org/add-ons/hifi-builder/versions/) |
| Place Helper | 2.0.0 / 2026-06-29 | 4.2 | [Version history](https://extensions.blender.org/add-ons/placehelper/versions/) |
| Bool Tool | 2.1.0 / 2026-07-14 | 4.5 | [Listing](https://extensions.blender.org/add-ons/bool-tool/) |
| Texel Density Checker | 2026.1.1 / 2026-07-06 | 4.2 | [Listing](https://extensions.blender.org/add-ons/texel-density-checker/) |
| 3D Print Toolbox | 1.5.0 / 2026-10-19 | 4.2 | [Version history](https://extensions.blender.org/add-ons/print3d-toolbox/versions/) |

All five listings declare GPL-3.0-or-later. Package hashes, full source, platform dependencies and installation behavior were not audited. The listing-linked [Place Helper repository](https://github.com/AIGODLIKE/PlaceHelper) establishes the source destination, not a completed source review. The connected application reported none of these five enabled; that does not establish whether disabled packages are installed.

## Format and consumer sources

| Source | Supported subject | Evidence boundary |
| --- | --- | --- |
| [Khronos glTF 2.0 specification](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html) | Metres, axes, hierarchy, accessors, skins, materials and animation | Format requirements; application support still needs testing |
| [Khronos glTF Validator](https://github.com/KhronosGroup/glTF-Validator) | Structural validation and issue severity | Installed package README and actual validation inspected |
| [Khronos production validation tutorial](https://github.com/KhronosGroup/Vulkan-Tutorial/blob/main/en/Advanced_glTF/Tooling_Production_Pipeline/03_validation.adoc) | Independent pipeline validation | Tutorial guidance, not a universal acceptance budget |
| [Three.js InstancedMesh](https://threejs.org/docs/pages/InstancedMesh.html) | Shared geometry/material instancing and bounds | Dynamic consumer reference; no new FPS benchmark |
| [Three.js WebGLRenderer](https://threejs.org/docs/pages/WebGLRenderer.html) | Renderer statistics and transparency sorting | Dynamic reference; sorting does not solve all transparent overlap |
| [Three.js Material](https://threejs.org/docs/pages/Material.html) | Material rendering and double-sided transparent passes | Dynamic reference; optimize only after checking the visual result |

## Native and repository evidence

- [Probe source](verification/knowledge-probe.py), [independent checker](verification/check-probe.mjs), [PASS receipt](verification/probe-results.json) and [retained failed timing assumption](verification/animation-time-assumption.json). The receipt identifies Blender/Python, output hashes, numeric observations and validator issues. See [calibration](calibration.md) for exact coverage and limitations.
- [Read-only API receipt](verification/native-api.json): Blender 5.1.2 BMesh signature, Boolean solver identifiers and enabled-target-extension list. Reading an identifier does not test the operation.
- Installed exporter source inspected at `/Applications/Blender.app/Contents/Resources/5.1/scripts/addons_core/io_scene_gltf2/__init__.py` for exporter RNA settings, and `node_modules/gltf-validator/README.md` for the installed validation interface. These local paths are inspection locations, not portable download links.
- The MCP server also supplied bundled RST excerpts without a document version. Older Principled names in those excerpts are a reason to check native inputs: the installed 5.1.2 probe reports `Coat Weight`. Bundled text is not evidence that all current APIs match it.

Direct manual HTTP attempts returned access errors; a guessed upstream exporter source tag returned 404. No conclusions depend on those failed fetches. This research did not install an extension, modify the connected scene, certify an entire asset pipeline or test a physical phone.
