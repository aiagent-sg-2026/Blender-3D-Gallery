set -e
git init -q
git remote add origin https://github.com/yapweijun1996/Blender-3D-Gallery.git
git sparse-checkout init --no-cone
git sparse-checkout set --no-cone --stdin <<'FILES'
/.gitignore
/AGENTS.md
/package.json
/package-lock.json
/scripts/test-model-qa-browser.mjs
/scripts/browser-test-utils.mjs
/tests/ball-04.test.mjs
/tests/helpers/ball-geometry-checks.mjs
/models/catalog.json
/models/eight-ball-billiards/exports/ball_04.glb
/models/eight-ball-billiards/exports/billiards-scene.glb
FILES
git fetch --depth=1 --filter=blob:none origin 34d008ba9f156c7f98ec58fc47f227f354f9dd81
git checkout -q -b codex/model-qa-m0010-live FETCH_HEAD
npm ci --ignore-scripts --no-audit --no-fund
npx --yes node@24.21.0 --version
