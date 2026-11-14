"""Reopen the assembled Blender scene, pose door hinges, render, preserve canonical source."""
from pathlib import Path
import bpy,math,json,hashlib
P=Path(__file__).resolve().parent;source=P/'corridor.blend';before=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source));pivots=[]
for o in bpy.context.scene.objects:
 if o.name.startswith(('HINGE_Left','HINGE_Right')):
  o.rotation_mode='XYZ';o.rotation_euler.z=(-1 if o.name.startswith('HINGE_Left') else 1)*math.pi/2;pivots.append(o.name)
bpy.context.view_layer.update();bpy.context.scene.render.filepath=str(P/'blender-open-doors.png');bpy.ops.render.render(write_still=True)
assert before==hashlib.sha256(source.read_bytes()).hexdigest()
(P/'blender-open-proof.json').write_text(json.dumps({'sourceSha256':before,'sourceUnchanged':True,'hinges':pivots,'degrees':90,'passed':len(pivots)==4},indent=2)+'\n')
assert len(pivots)==4
