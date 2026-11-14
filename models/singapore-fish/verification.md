# Fish collection and swimming verification

## Delivered scope

FISH-001 through FISH-060: 20 P0, 27 P1 and 13 P2 original stylized fish assets. Each includes an independent Blender scene, editable 11-bone skeleton, weighted body/tail/fins, one embedded `Swim_Loop` GLB clip, Blender-rendered poster and metadata. Loops vary from 1.6 to 3.2 seconds. Rays emphasize paired wing movement; elongated fish propagate a whole-body wave; other families emphasize tail propulsion and fin stabilization. No forward trajectory or inflation is claimed.

The gallery adds a fish-specific playback owner without changing the behavior of other models. Swimming starts automatically except under reduced-motion preferences. Play/Pause allows explicit control. Hidden documents suspend the clock; close disposes the mixer, skeleton textures and controls. Cards remain static and GLBs load on demand.

## Verification

- Blender 5.1.2 regenerated all 60 sources and exports successfully.
- `node models/singapore-fish/validate.mjs`: PASS. All 60 distinct GLBs have zero glTF errors and zero warnings, one named clip and valid skins. All source files are present. Total runtime GLBs: 12,441,368 bytes; 3,756–6,748 triangles each. See `validation.json`.
- `node models/singapore-fish/test-animation.mjs`: PASS. Three.js loads all 60 exported clips. Every track has matching loop endpoints. Actual CPU-skinned tail and fin vertices differ between quarter-cycle and three-quarter-cycle poses, normalized by authoring length. Eel tail movement substitutes for absent paired fins; ray body-wing vertices are checked. See `animation-validation.json`.
- Blender ran `inspect-sources.py`: PASS. All 60 sources have one isolated scene, a stable FISH identifier, nonempty editable mesh anatomy with armature modifiers, one 11-bone rig with an action and a studio camera. See `source-validation.json`.
- `npm run build`: PASS on an isolated worktree based on remote main. Includes the full existing GLB validation. A final `npx vite build` also passed after matching the playback button to the existing outline-button style. Vite retains its bundle-size advisory.
- `npm test`: PASS, 587 tests, zero failures on the isolated worktree.
- `node models/singapore-fish/test-swim-browser.mjs`: PASS. Chromium canvas pixel comparisons prove visible pose changes after Play and stable images after Pause for Barramundi, Stingray, Swamp Eel, Reef Shark, Pufferfish, Betta, Lionfish and Guppy at desktop width, plus Stingray at 390px. Reduced-motion starts paused, explicit playback works, normal preferences autoplay, live preference changes pause, and closing removes controls. No page, console or HTTP errors. See `swim-browser-validation.json` and `swim-*.png`.
- `node scripts/test-shopping-cart-browser.mjs`: PASS at 1440, 768 and 390px. Grab, add/remove, steering, push, stop, release and reset still work; desktop collision behavior also passes.
- Visual review: `swim-phases.jpg`, representative Blender GIF loops and desktop/mobile runtime screenshots. Static-generation acceptance previously verified all 60 viewers, 60 filtered cards, Chinese search and lazy loading; current animation validation covers all 60 GLBs with representative runtime playback checks.

## Export contract

Editable source meshes remain under their ASSET root. Temporary export copies bake mesh transforms and flatten skinned mesh nodes to identity-transform scene roots, avoiding glTF skin-parent warnings. Sources retain their original geometry and hierarchy. Consequently this collection omits the optional single-root registry claim; existing catalog validation remains unchanged.

## Limits and release scope

Stylized, procedurally animated reference assets, not biomechanically or taxonomically validated specimens. Shared body families simplify species anatomy. Supplied Chinese/English/local aliases may overlap and are not asserted to be scientific equivalents. Dimensions are illustrative. No schooling, route navigation, puffer inflation or dried anchovy variant. Browser evidence uses Chromium software rendering; physical devices and Safari/WebKit are not verified. GitHub main publication is authorized by the user; deployment is a separate action and is not claimed here. Unrelated working-tree changes are excluded from the focused release.
