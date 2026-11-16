"""Export web delivery copies from accepted packed Blender sources, never edit sources."""
import bpy,bmesh,json,sys,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[1]
slug=sys.argv[sys.argv.index('--')+1]
manifest=json.loads((HERE/'releases.json').read_text());item=manifest['models'][slug]
source=REPO/item['source'];out=HERE/slug;out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.frame_set(1)
selected=[o for o in s.objects if o.type in ['MESH','ARMATURE','EMPTY'] and not o.hide_render and o.name not in ['Cube_0','Icosphere']]
for o in [o for o in selected if o.type=='MESH' and not o.data.shape_keys]:
 world=o.matrix_world.copy();o.data=o.data.copy();o.parent=None;o.matrix_world=world
 uv=o.data.uv_layers.active
 for poly in o.data.polygons:
  if len(poly.vertices)>4 and uv:
   for li in poly.loop_indices:
    p=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(.035+.08*p.y,.50+.12*p.z)
 bm=bmesh.new();bm.from_mesh(o.data);ngons=[f for f in bm.faces if len(f.verts)>4]
 if ngons:bmesh.ops.triangulate(bm,faces=ngons)
 bm.to_mesh(o.data);bm.free();o.data.update()
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
limit=item.get('delivery_fin_texture_limit')
if limit:
 assert isinstance(limit,int) and 128<=limit<=1024
 resized={}
 for obj in selected:
  if obj.type!='MESH':continue
  for material in obj.data.materials:
   if not material or not material.use_nodes:continue
   for node in material.node_tree.nodes:
    if node.type!='TEX_IMAGE' or not node.image:continue
    image=node.image
    if image in resized:node.image=resized[image];continue
    if not image.name.startswith(tuple(slug+part for part in ['_fin_','_spiny_','_tail_'])) or max(image.size)<=limit:continue
    copy=image.copy();copy.name=image.name+'_Delivery'+str(limit);ratio=limit/max(image.size);copy.scale(max(1,round(image.size[0]*ratio)),max(1,round(image.size[1]*ratio)));copy.pack();resized[image]=copy;node.image=copy
 assert resized,'Requested fin texture limit must resize actual fin images'
 print('DOWNSAMPLED_FIN_IMAGES',len(resized),limit,flush=True)
bpy.ops.object.select_all(action='DESELECT')
for o in selected:o.select_set(True)
output=out/'model.glb'
bpy.ops.export_scene.gltf(filepath=str(output),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_nla_strips_merged_animation_name='Swim_Loop',export_frame_range=True,export_force_sampling=True,export_tangents=True,export_texcoords=True,export_image_format='WEBP',export_image_quality=95)
item['source_sha256']=hashlib.sha256(source.read_bytes()).hexdigest();item['glb_sha256']=hashlib.sha256(output.read_bytes()).hexdigest();item['bytes']=output.stat().st_size
(out/'export-receipt.json').write_text(json.dumps(item,indent=2)+'\n')
print('EXPORTED',slug,item['bytes'],flush=True)
