# Blender extension selection and admission

<!-- KB-SUMMARY-START -->
Prefer the official Blender Extensions listing and author-linked source. Match the exact extension version, Blender range, platform, manifest/module identity, dependencies and license to the intended workflow. A Python implementation or available toolbar is not proof of background/MCP compatibility. Inspect operator RNA and poll requirements after an isolated registration test; modal workspace tools may require a real editor and events. Separate listing-verified, source-reviewed, registered, background-tested and target-export-tested states. Test a disposable scene/profile before changing a working setup, record package hashes and preserve source files. Retain existing candidate names such as Rigify, Moveset and PropHandoff as unreviewed unless independently evaluated. The five-extension catalog dated 2026-11-15 verifies published versions/ranges only; none was installed or execution-tested by this research. Recommendations depend on authoring needs, not popularity alone.
<!-- KB-SUMMARY-END -->

## Dated catalog

Reviewed 2026-11-15. All five official listings declare GPL-3.0-or-later. Their declared minimum versions are below Blender 5.1.2; that alone does not establish compatibility with 5.1.2. This is listing evidence, not a successful registration/background test.

### HiFi Architecture Builder 4.6.7

[Official version history](https://extensions.blender.org/add-ons/hifi-builder/versions/): published 2026-11-12; Blender 4.2+. Architecture generators and game-engine preparation. Some advertised workflows target GTA V/FiveM/Sollumz; verify the selected generator's actual GLB output and runtime interfaces separately. Listing verified; source audit, installed operators, background operation and target export have not been tested here.

### Place Helper 2.0.0

[Official version history](https://extensions.blender.org/add-ons/placehelper/versions/): published 2026-06-29; Blender 4.2+. Place, Transform Pro, Scatter and Dynamic Place are viewport-oriented tools. Useful for manual scene dressing; linked/object duplication modes need ownership checks. Listing verified; background/MCP execution has not been tested here. The official listing links [AIGODLIKE/PlaceHelper](https://github.com/AIGODLIKE/PlaceHelper).

### Bool Tool 2.1.0

[Official listing](https://extensions.blender.org/add-ons/bool-tool/): published 2026-07-14; Blender 4.5+. Convenience operators and cutter management around Blender Boolean modifiers. It does not introduce a replacement Boolean solver or itself establish faster Boolean evaluation. Listing verified; installed operators and background behavior have not been tested here.

### Texel Density Checker 2026.1.1

[Official listing](https://extensions.blender.org/add-ons/texel-density-checker/): published 2026-07-06; Blender 4.2+. Calculates/adjusts density and visualizes UV distribution. The Extensions version states it has no C++ backend. Listing verified; operator context, registration and background execution have not been tested here.

### 3D Print Toolbox 1.5.0

[Official version history](https://extensions.blender.org/add-ons/print3d-toolbox/versions/): published 2026-10-19; Blender 4.2+. Geometry/printing analysis and file-export tools; the listing declares file permission for STL/PLY/OBJ export. Use suitable mesh checks as a supplement to GLB validation. Listing verified; current Python report/operator APIs and background execution have not been tested here.

## Verification scope

This catalog does not establish installation, security review, animation quality, generated-model quality, phone compatibility or headless support. Other candidates in the earlier KB policy are retained as unreviewed; this research does not silently approve them.

## Admission procedure

1. Record the official package/version, manifest, license, platform limits and package hash.
2. Review the relevant source and external dependencies. A listing permission declaration does not describe all possible Python behavior.
3. Register it in an isolated Blender profile; identify the actual module and required operators from the running API.
4. Separate interactive gestures from executable background operations. Do not invent a UI context when an editor/event loop is required.
5. Produce a small owned fixture, inspect its data, export and independently load the result.
6. Admit only the tested workflow and preserve rollback instructions.

The [5.1 extension manifest guide](https://docs.blender.org/manual/zh-hans/5.1/advanced/extensions/getting_started.html) describes package metadata. A declared range, successful registration and a working operation are three different checks.

For the current script-heavy asset workflow, prioritize a demonstrated gap: density/geometry QA, manual dressing or new architecture generation. Existing validated modules can remain the production inputs while a new generator is evaluated in isolation. This is an engineering recommendation, not a universal extension ranking.
