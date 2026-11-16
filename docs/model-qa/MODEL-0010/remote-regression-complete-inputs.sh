set -e
python3 - <<'PREFLIGHT'
from pathlib import Path
import json,subprocess,shutil
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()=='1e94207991e702451ce931d3f76d30925a903453'
assert not subprocess.check_output(['git','diff','--name-only'],text=True).strip()
assert Path('output/build.log').exists() and not Path('output/game.log').exists()
assert not Path('output/build-attempt2.log').exists()
shutil.copyfile('output/build.log','output/build-attempt2.log')
Path('output/setup-failure2.json').write_text(json.dumps({'job_id':'99c7dc81-fc66-4607-a8c0-7c427c73045b','status':'FAILED','phase':'isolated Vite build','tests':'NOT_RUN','observed_error':'PWA closeBundle ENOENT for dist after transformation failed.','confirmed_setup_gap':'Catalog-only sparse model checkout omitted direct application LOD, customization-module and solar-demo glob dependencies.','correction':'Checkout the complete models directory and rebuild, preserving original application and browser scripts.'},indent=2)+'\n')
PREFLIGHT
git sparse-checkout add --no-cone /models/
MODEL_QA_NODE_BIN=$(npx --yes node@24.21.0 -p 'process.execPath')
"$MODEL_QA_NODE_BIN" -e "require('node:assert/strict').equal(process.version,'v24.21.0')"
"$MODEL_QA_NODE_BIN" scripts/validate-assets.mjs > output/build.log 2>&1
"$MODEL_QA_NODE_BIN" node_modules/vite/bin/vite.js build >> output/build.log 2>&1
TEST_ARTIFACT_DIR=output/game "$MODEL_QA_NODE_BIN" scripts/test-game-browser.mjs > output/game.log 2>&1
TEST_ARTIFACT_DIR=output/experience "$MODEL_QA_NODE_BIN" scripts/test-game-experience.mjs > output/experience.log 2>&1
"$MODEL_QA_NODE_BIN" --input-type=module - <<'JS'
import fs from 'node:fs';
import assert from 'node:assert/strict';
const game=JSON.parse(fs.readFileSync('output/game/results.json','utf8'));
const experience=JSON.parse(fs.readFileSync('output/experience/results.json','utf8'));
assert.equal(game.results.length,46);assert.ok(game.results.every(x=>x.passed));assert.deepEqual(game.errors,[]);assert.deepEqual(game.selection,{from:null,case:null});
assert.equal(experience.results.length,31);assert.ok(experience.results.every(x=>x.passed));assert.deepEqual(experience.errors,[]);assert.equal(experience.selection,null);
fs.writeFileSync('output/acceptance.json',JSON.stringify({game:{tests:46,passed:46,selection:game.selection},experience:{tests:31,passed:31,selection:experience.selection},catalog_entries:567,node:process.version,platform:process.platform,arch:process.arch,physical_mobile:'Excluded by owner; existing browser emulation scenarios retained'},null,2)+'\n');
JS
git diff --exit-code -- src scripts models data public package.json package-lock.json vite.config.js index.html
python3 - <<'PY'
from pathlib import Path
import json,hashlib,subprocess,tarfile,datetime
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert head=='1e94207991e702451ce931d3f76d30925a903453'
files=[Path(p.decode()) for p in subprocess.check_output(['git','ls-files','-z']).split(b'\0') if p and Path(p.decode()).is_file()]
manifest={'source_sha':head,'observed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checked_out_files':[{'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],'sparse_checkout':'Complete models directory plus application/build/browser-script/public/data directories. All catalog assets, non-catalog LODs, customization modules and solar-demo glob inputs are present.'}
Path('output/source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
files=[Path('output')/p for p in ['install.log','browser-install.log','build.log','game.log','experience.log','game/results.json','experience/results.json','acceptance.json','source-manifest.json','browser-install-attempt1.log','setup-failure.json','build-attempt2.log','setup-failure2.json']]
e={'files':[{'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]};Path('output/evidence-manifest.json').write_text(json.dumps(e,indent=2)+'\n');files.append(Path('output/evidence-manifest.json'))
with tarfile.open('regression-evidence.tar.gz','w:gz') as t:
 for p in files:t.add(p,arcname=str(p),recursive=False)
p=Path('regression-evidence.tar.gz');print(json.dumps({'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'files':len(files),'source_sha':head}))
PY
