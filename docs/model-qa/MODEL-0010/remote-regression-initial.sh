set -e
python3 - <<'PY'
from pathlib import Path
assert not any(Path('.').iterdir()), 'Recovery workspace must be empty.'
PY
git init -q
git remote add origin https://github.com/yapweijun1996/Blender-3D-Gallery.git
git sparse-checkout init --no-cone
git fetch --depth=1 --filter=blob:none origin 1e94207991e702451ce931d3f76d30925a903453
python3 - <<'PY' > /tmp/model0010-sparse-7fc1.txt
import json,subprocess
catalog=json.loads(subprocess.check_output(['git','show','FETCH_HEAD:models/catalog.json']))
paths={'/.gitignore','/AGENTS.md','/package.json','/package-lock.json','/index.html','/vite.config.js','/src/','/scripts/','/data/','/public/','/models/catalog.json'}
assets=[a for c in catalog['collections'] for a in c['assets']];assert len(assets)==567
for a in assets:
 for key in ['file','thumbnail','metadata']:
  if a.get(key):paths.add('/'+a[key])
print('\n'.join(sorted(paths)))
PY
git sparse-checkout set --no-cone --stdin < /tmp/model0010-sparse-7fc1.txt
git checkout -q -b codex/model-qa-m0010-regression FETCH_HEAD
mkdir -p output
cat > run-model0010-regression.sh <<'RUN'
set -e
node -e "require('node:assert/strict').equal(process.version,'v24.21.0')"
npm ci --ignore-scripts --no-audit --no-fund > output/install.log 2>&1
npx playwright install chromium webkit > output/browser-install.log 2>&1
npm run build > output/build.log 2>&1
TEST_ARTIFACT_DIR=output/game node scripts/test-game-browser.mjs > output/game.log 2>&1
TEST_ARTIFACT_DIR=output/experience node scripts/test-game-experience.mjs > output/experience.log 2>&1
node --input-type=module - <<'JS'
import fs from 'node:fs';
import assert from 'node:assert/strict';
const game=JSON.parse(fs.readFileSync('output/game/results.json','utf8'));
const experience=JSON.parse(fs.readFileSync('output/experience/results.json','utf8'));
assert.equal(game.results.length,46);assert.ok(game.results.every(x=>x.passed));assert.deepEqual(game.errors,[]);assert.deepEqual(game.selection,{from:null,case:null});
assert.equal(experience.results.length,31);assert.ok(experience.results.every(x=>x.passed));assert.deepEqual(experience.errors,[]);assert.equal(experience.selection,null);
fs.writeFileSync('output/acceptance.json',JSON.stringify({game:{tests:46,passed:46,selection:game.selection},experience:{tests:31,passed:31,selection:experience.selection},catalog_entries:567,node:process.version,platform:process.platform,arch:process.arch,physical_mobile:'Excluded by owner; existing browser emulation scenarios retained'},null,2)+'\n');
JS
RUN
npx --yes --package=node@24.21.0 -c 'sh run-model0010-regression.sh'
git diff --exit-code -- src scripts models data public package.json package-lock.json vite.config.js index.html
python3 - <<'PY'
from pathlib import Path
import json,hashlib,subprocess,tarfile,datetime
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert head=='1e94207991e702451ce931d3f76d30925a903453'
files=[Path(p.decode()) for p in subprocess.check_output(['git','ls-files','-z']).split(b'\0') if p and Path(p.decode()).is_file()]
manifest={'source_sha':head,'observed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checked_out_files':[{'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],'sparse_checkout':'All567 catalog exports, previews and metadata plus complete application/build/browser-script/public/data directories; native authoring files omitted from browser-only recovery.'}
Path('output/source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
files=[Path('output')/p for p in ['install.log','browser-install.log','build.log','game.log','experience.log','game/results.json','experience/results.json','acceptance.json','source-manifest.json']]
e={'files':[{'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]};Path('output/evidence-manifest.json').write_text(json.dumps(e,indent=2)+'\n');files.append(Path('output/evidence-manifest.json'))
with tarfile.open('regression-evidence.tar.gz','w:gz') as t:
 for p in files:t.add(p,arcname=str(p),recursive=False)
p=Path('regression-evidence.tar.gz');print(json.dumps({'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'files':len(files),'source_sha':head}))
PY
