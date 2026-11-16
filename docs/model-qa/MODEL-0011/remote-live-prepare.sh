set -e
python3 - <<'FRESH'
from pathlib import Path
assert not Path('.git').exists() and not Path('output').exists()
FRESH
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
/tests/ball-05.test.mjs
/tests/helpers/ball-geometry-checks.mjs
/models/catalog.json
/models/eight-ball-billiards/exports/ball_05.glb
/models/eight-ball-billiards/exports/billiards-scene.glb
FILES
git fetch --depth=1 --filter=blob:none origin 24e5fd5d7a6f092f138a0f00c276d0e779a86ac2
git checkout -q -b codex/model-qa-m0011-live FETCH_HEAD
npm ci --ignore-scripts --no-audit --no-fund
npx --yes node@24.21.0 --version
