"""Run with Blender. Creates an isolated copy, edits real text, and re-exports it."""
from pathlib import Path
import shutil
import sys
import runpy
import hashlib
import json
import bpy
here=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
sys.path.insert(0,str(here.parents[1]/'scripts'))
out=Path(sys.argv[sys.argv.index('--')+1]).resolve()
assert out != here and not out.exists(), 'Choose a new isolated output directory'
source=here/'sources/mall-event-booth.blend'
delivery=here/'exports/mall-event-booth.glb'
hash_file=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={'source':hash_file(source),'glb':hash_file(delivery)}
for base in (out,out/'baseline'):
    for name in ('sources','exports','previews'):
        (base/name).mkdir(parents=True)
    shutil.copy2(here/'generate.py',base/'generate.py')
shutil.copy2(source,out/'baseline/sources/mall-event-booth.blend')
sys.argv=['generate.py','--','--export-source','--no-render']
runpy.run_path(str(out/'baseline/generate.py'),run_name='__main__')
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
bpy.context.preferences.filepaths.save_version=0
assert bpy.data.objects['PosterPanel editable headline'].data.body=='YOUR STORY'
bpy.data.objects['PosterPanel editable headline'].data.body='NEW STORY'
bpy.ops.wm.save_as_mainfile(filepath=str(out/'sources/mall-event-booth.blend'),compress=True)
sys.argv=['generate.py','--','--export-source','--no-render']
runpy.run_path(str(out/'generate.py'),run_name='__main__')
after={'source':hash_file(source),'glb':hash_file(delivery)}
assert before==after
(out/'edit-execution.json').write_text(json.dumps({'status':'PASS','blender':bpy.app.version_string,
    'originalBefore':before,'originalAfter':after,'baselineSourceSha256':hash_file(out/'baseline/sources/mall-event-booth.blend'),
    'beforeLabel':'YOUR STORY','afterLabel':'NEW STORY','render':'NOT_RUN; real saved-source export exercised'},indent=2)+'\n')
