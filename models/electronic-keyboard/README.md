# Electronic Keyboard (61 Keys)

Original, brand-neutral static music equipment for store S15, P1. Existing category: Equipment. No external assets, fonts, text, logos or product packaging.

The notched keyboard has 36 white keys and 25 raised black keys, C2 through C7 inclusive. Five octaves use the correct two/three black-key grouping. The blank panel has abstract knobs, buttons and speaker ribs. A tubular X-frame with rubber feet supports the chassis; an open tilted music rest includes a retaining tray. Controls, keys and stand are static; there is no sound or folding animation.

The `.blend` retains individually editable parts. Export evaluates modifiers and merges temporary copies into three meshes, each with one shared material; it preserves the saved source. Units are metres, origin is at the floor centre of the complete footprint, and the GLB uses +Y up / +Z front (Blender +Z up / -Y front).

Run from the repository root:

```sh
/opt/homebrew/bin/blender --background --python-exit-code 1 --python models/electronic-keyboard/generate.py
node models/electronic-keyboard/validate.mjs
/opt/homebrew/bin/blender --background --python-exit-code 1 --python models/electronic-keyboard/inspect_sources.py
node models/electronic-keyboard/verify_source_edit.mjs
npm run validate:assets
npm test
npm run build
node models/electronic-keyboard/check_browser.mjs
```

To export saved manual edits, append `-- --export-source --skip-render` to the generator command. To rebuild without rendering, append `-- --skip-render`. To render saved geometry only, append `-- --export-source --previews-only`. Source-edit QA writes disposable files into the system temporary directory and confirms that the original source hash stays unchanged.

Measured numbers and tested GLB identity are in `reports/assets.json`; source, Khronos, reproducibility and Chromium evidence are adjacent. Preview PNGs are hero, front, side and 3q; none of the studio lights or camera are exported. The overall envelope includes the 0.46 m deep feet and raised music rest. Review remains required; physical mobile hardware and the full S15 assembly are unverified. Owner-project reuse is authorized; public redistribution terms are unspecified.
