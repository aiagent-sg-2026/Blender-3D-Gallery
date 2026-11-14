"""Re-import the exported GLB in Blender and report mesh, rig, material and action evidence.
Run: blender --background --python models/gjh-visitor-v3/validate.py"""
from pathlib import Path
import json
import bpy
root = Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(root / 'exports/gjh-visitor-v3.glb'))
meshes = [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith('V3_')]  # importer adds an Icosphere bone-display helper
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE']
tris = sum(len(m.data.polygons) for m in meshes if all(len(p.vertices) == 3 for p in m.data.polygons[:1]))
report = {'meshes': len(meshes), 'armatures': len(arm), 'bones': len(arm[0].data.bones) if arm else 0,
          'skinned': all(len(m.vertex_groups) > 0 and (m.parent in arm or any(mod.type == 'ARMATURE' for mod in m.modifiers)) for m in meshes),
          'materials': len(bpy.data.materials), 'actions': sorted(a.name.split('|')[-1] for a in bpy.data.actions),
          'triangles': sum(len(m.data.loop_triangles) or len(m.data.polygons) for m in meshes)}
for m in meshes:
    if not (len(m.vertex_groups) > 0 and (m.parent in arm or any(mod.type == 'ARMATURE' for mod in m.modifiers))): print('UNSKINNED', m.name, len(m.vertex_groups), m.parent, [x.type for x in m.modifiers])
print('VALIDATE ' + json.dumps(report))
assert report['armatures'] == 1 and report['skinned'] and len(report['actions']) >= 12
