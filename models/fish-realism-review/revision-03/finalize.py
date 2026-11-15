"""Bind the static CC0 bass and verify source deformation in isolated review files."""
import bpy,math,json,sys,importlib.util
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('base',HERE.parent/'create_review.py');B=importlib.util.module_from_spec(spec);spec.loader.exec_module(B)
spec=importlib.util.spec_from_file_location('preview',HERE/'create_review.py');P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
slug=sys.argv[sys.argv.index('--')+1];folder=HERE/slug
bpy.ops.wm.open_mainfile(filepath=str(folder/(slug+'-review.blend')));s=bpy.context.scene
mesh=[o for o in s.objects if o.type=='MESH' and not o.hide_render]
if slug=='barramundi':
 root=bpy.data.objects.new('AnimatedBassRoot',None);s.collection.objects.link(root);B.ROOT=root
 for o in mesh:
  world=o.matrix_world.copy();o.parent=None;o.data.transform(world);o.matrix_world.identity();o.parent=root
 rig=B.add_rig('bass')
 # Spatial weighting feathers only the distal fin membranes onto their own bones.
 for o in mesh:
  for v in o.data.vertices:
   x,y,z=v.co;fin=None;w=0
   if -.55<x<1.0 and z>.43:fin='Dorsal';w=min(.85,(z-.43)/.30)
   elif .05<x<.95 and z<-.40:fin='Anal';w=min(.85,(-z-.40)/.25)
   elif -1.0<x<-.25 and abs(y)>.22 and -.48<z<.05:fin='Pectoral_L' if y>0 else 'Pectoral_R';w=min(.75,(abs(y)-.22)/.18)
   if fin and w>0:
    for g in list(v.groups):o.vertex_groups[g.group].add([v.index],g.weight*(1-w),'REPLACE')
    o.vertex_groups[fin].add([v.index],w,'REPLACE')
 for o in mesh:
  for m in o.modifiers:
   if m.type=='ARMATURE':m.use_deform_preserve_volume=True
 s.frame_end=73
# Keep texture pigment and skeleton; tame uniformly reflective imported fin maps.
if slug in ['barramundi','betta']:
 for mat in {m for o in mesh for m in o.data.materials if m and m.use_nodes}:
  n=mat.node_tree.nodes;l=mat.node_tree.links;p=next((x for x in n if x.type=='BSDF_PRINCIPLED'),None)
  if not p:continue
  for name,op,value in [('Metallic','MULTIPLY',.18),('Roughness','MAXIMUM',.39)]:
   sock=p.inputs[name]
   if sock.is_linked:
    old=sock.links[0].from_socket;l.remove(sock.links[0]);a=n.new('ShaderNodeMath');a.operation=op;a.inputs[1].default_value=value;l.new(old,a.inputs[0]);l.new(a.outputs[0],sock)
   else:sock.default_value=value if name=='Roughness' else .03
  for node in n:
   if node.type=='NORMAL_MAP':node.inputs['Strength'].default_value=.40 if slug=='betta' else .65
# Measure actual evaluated vertices, not just the presence of keyframes.
def points():
 dg=bpy.context.evaluated_depsgraph_get();return [o.evaluated_get(dg).matrix_world@v.co for o in mesh for v in o.evaluated_get(dg).data.vertices]
frames=[1,19,37,55,73] if slug!='betta' else [1,36,72,108,144]
poses=[];lo=Vector((1e8,)*3);hi=-lo
for f in frames:
 s.frame_set(f);bpy.context.view_layer.update();p=points();poses.append(p)
 for v in p:
  for d in range(3):lo[d]=min(lo[d],v[d]);hi[d]=max(hi[d],v[d])
maxmotion=max((a-b).length for a,b in zip(poses[0],poses[1]));loop=max((a-b).length for a,b in zip(poses[0],poses[-1]));assert maxmotion>.0001,(slug,maxmotion)
report={'slug':slug,'source_animation':'Take 01 (BlueMesh)' if slug=='betta' else 'Swim_Loop (added in this review)','sampled_frames':frames,'max_vertex_displacement':maxmotion,'loop_endpoint_displacement':loop,'mesh_count':len(mesh),'bones':sum(len(o.data.bones) for o in s.objects if o.type=='ARMATURE'),'packed_images':all(i.packed_file for i in bpy.data.images if i.source=='FILE'),'production_modified':False}
(folder/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
if slug=='betta':
 # The full animated fin envelope determines the crop, including tall dorsal tips.
 s.camera.data.ortho_scale=max(5.05,(hi.z-lo.z)*s.render.resolution_x/s.render.resolution_y*1.14);P.aim(s.camera,(lo+hi)/2)
s.frame_set(24 if slug=='betta' else 13);s.render.filepath=str(folder/'preview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(folder/(slug+'-review.blend')));bpy.ops.render.render(write_still=True)
bpy.ops.object.select_all(action='DESELECT')
for o in s.objects:
 if o.type not in ['CAMERA','LIGHT'] and not o.hide_render:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(folder/(slug+'-review.glb')),export_format='GLB',use_selection=True,export_animations=True,export_frame_range=True,export_force_sampling=True)
# Compact animated inspection render retains the same camera and materials.
s.render.engine='BLENDER_EEVEE';s.render.resolution_x=640;s.render.resolution_y=424;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';anim=folder/'frames';anim.mkdir(exist_ok=True)
for index,frame in enumerate(range(1,s.frame_end,3 if slug=='betta' else 2)):
 s.frame_set(frame);s.render.filepath=str(anim/('%03d.png'%index));bpy.ops.render.render(write_still=True)
print('FINALIZED',json.dumps(report),flush=True)
