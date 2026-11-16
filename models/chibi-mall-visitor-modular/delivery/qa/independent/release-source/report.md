# R20 final-source packaging addendum

**PASS for this narrow source/export check.** The prior r20 technical report remains separate; no model, authoring source, delivery or earlier report was edited.

- Exact signed native: `44d9f04a5c46918fcd81b845e432973bd559e0181756fb81d8a49dde94e4cbdd`.
- Expected and independently re-exported GLB: `60650f47aac716cb5a11fa69bee58c06546aa2199a25c2bde6dcc37ce566ab6f`.
- Identical sculpt input: `1e4b7f7a91b551226d5644e0872134c9e852832382e0b09b72e4282e8fe7fe00`.

The18-file r20 source matches its earlier independent frozen snapshot. Compared with the frozen20-file release authoring tree, the participating Python changes are exactly: the tiny helper moves from `hair_contours.py` to `hair_temple_fit.py` with identical bytes; `hair_bake.py` and `swept_locks.py` each replace that one import name. All other common files are byte-identical. The older standalone canonical `authoring/hair_contours.py` remains present, SHA `c94e25313baf0492fa64743aac5df5e5d4a6ba2baa3d1f0ba8ae59afdd181a9d`, and was rechecked unchanged. It is not included in this tested release snapshot or imported by the smoke test.

The release tree also contains `hair-lock-mattes.npz` and `hair-measurements.npz`, absent from r20/source. Their hashes are recorded separately; neither filename is referenced by the participating Python source. Therefore this report claims only three participating module changes, not identity of the whole file set.

A clean Blender process opened the frozen signed master and ran the final frozen `scene.py --export-only`. It exited0 and produced a GLB byte-identical to60650f47. A separate explicit import smoke confirmed `hair_temple_fit`, `swept_locks` and `hair_bake` resolve from the frozen release tree, without importing the old `hair_contours` name. Release originals, frozen source, signed inputs and the canonical legacy file were rehashed unchanged afterward.

The initial combined probe exited1 because its added assertion incorrectly expected export-only to load the lazy procedural helper path. Its export had already produced identical60650f47 bytes. The original command/log/receipt/script remain under `instrumentation-first/`; the subsequent pure export and explicitly labelled import smoke both exited0. This is not a hidden model failure or procedural rebuild proof.

`freeze.json` holds all source/input hashes; `confirmed-commands.json` records exact argv, UTC times and exit codes; `report.json` binds the evidence. Full procedural/collection rebuild, baking, guide exports, ZIP and visual/formal acceptance are outside this addendum.
