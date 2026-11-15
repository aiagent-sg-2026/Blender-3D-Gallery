set -e
python3 - <<'PREFLIGHT'
from pathlib import Path
import hashlib
base=Path('docs/model-qa/MODEL-0012')
for folder in ['source','reimport']:
 assert len(list((base/folder).glob('*.png')))==7
for folder in ['contact-source','contact-reimport']:
 assert not (base/folder).exists()
assert not Path('output/model-qa/MODEL-0012/reexport').exists()
assert hashlib.sha256(Path('models/eight-ball-billiards/scene.blend').read_bytes()).hexdigest()=='6b06dedf3da537c411afc7c6c4589268fb6945e4dfd22e8af4ed35a5abc71672'
PREFLIGHT
nice -n 15 /Applications/Blender.app/Contents/MacOS/Blender --background --disable-autoexec --threads 1 models/eight-ball-billiards/scene.blend --python-exit-code 1 --python scripts/model-qa-cue-ball-contact.py -- --ball-number 6 --output docs/model-qa/MODEL-0012/contact-source > /tmp/model-0012-contact-source.log 2>&1
nice -n 15 /Applications/Blender.app/Contents/MacOS/Blender --background --disable-autoexec --threads 1 --python-exit-code 1 --python scripts/model-qa-cue-ball-contact.py -- --ball-number 6 --glb models/eight-ball-billiards/exports/billiards-scene.glb --output docs/model-qa/MODEL-0012/contact-reimport > /tmp/model-0012-contact-reimport.log 2>&1
nice -n 15 /Applications/Blender.app/Contents/MacOS/Blender --background --disable-autoexec --threads 1 models/eight-ball-billiards/scene.blend --python-exit-code 1 --python docs/model-qa/MODEL-0012/export-replay.py -- output/model-qa/MODEL-0012/reexport > /tmp/model-0012-export-replay.log 2>&1
