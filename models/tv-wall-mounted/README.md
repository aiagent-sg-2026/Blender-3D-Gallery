# Wall-Mounted TV

Original brand-neutral 55-inch-class TV for S13 and S14. The procedural panel construction is adapted from `tv-floor-stand`: same 1.23 x 0.72 m housing, 16:9 active screen, slim bezel and rear ventilation. The blank screen has a restrained neutral emissive material; no UI, text, logos or external assets. `MOUNT_VESAWallBracket` is an independently editable fixed bracket with a nominal 400 x 200 mm attachment pattern.

Metres; glTF +Y up / +Z front. Root `ASSET_TVWallMounted` stays at the floor centre beneath the full depth envelope. Panel centre is 1.47 m above the floor; bottom is 1.11 m. This floor datum intentionally leaves the TV elevated. Place a wall at rear plane glTF Z = -0.073 m. No wall is exported.

From this folder:

```sh
/opt/homebrew/bin/blender --background --python-exit-code 1 --python generate.py
node validate.mjs
/opt/homebrew/bin/blender --background --python-exit-code 1 --python inspect_sources.py
node verify_source_edit.mjs
```

Append `-- --export-source` to export saved source edits without rebuilding; `-- --skip-render` skips previews. `-- --views=hero,front,side,3q,rear` selects renders. The exported asset has three shared materials and three functional mesh nodes. Studio floor, camera and lighting stay outside the exported root.

From the repository root run `npm run validate:assets`, `npm test`, `npm run build`, then `node models/tv-wall-mounted/verify_page.mjs`. The browser check opens the actual production GLB at 1440 x 900, verifies its SHA-256, exercises orbit/reset and saves `~/Documents/MallQueue/reports/tv-wall-mounted-page.png`.

See metadata and `reports/` for measurements and observed gates. Static visual prop only; installation, structural/electrical suitability, physical phones, WebKit and full mall performance are unverified. Public redistribution terms remain unspecified; owner-project reuse is authorized.
