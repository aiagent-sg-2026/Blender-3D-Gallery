"""Export and inspect one independently reviewed fish, then render its swim loop."""
import bpy,bmesh,json,sys,math,hashlib
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[1];slug=sys.argv[sys.argv.index('--')+1];OUT=HERE/slug
bpy.ops.wm.open_mainfile(filepath=str(OUT/(slug+'.blend')));s=bpy.context.scene
sys.path.insert(0,str(HERE))
from fin_weights import attach_fin_roots
if any(o.type=='MESH' and o.get('deform_role') in ['dorsal','anal','pectoral'] and not o.get('fin_root_anchor') for o in s.objects):
 attach_fin_roots(s);s.frame_set(13);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(slug+'.blend')))
 s.render.filepath=str(OUT/'preview.png');bpy.ops.render.render(write_still=True);camera=s.camera;original_matrix=camera.matrix_world.copy();original_scale=camera.data.ortho_scale
 camera.location=(-1.15,-7,.55);camera.rotation_euler=(Vector((-1.03,0,.02))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=1.65;s.render.filepath=str(OUT/'head-detail.png');bpy.ops.render.render(write_still=True);camera.matrix_world=original_matrix;camera.data.ortho_scale=original_scale;s.render.filepath=str(OUT/'preview.png')
else:s.frame_set(13)
END_FRAME=int(s.frame_end);SPAN=END_FRAME-1

def observe(label):
 meshes=[o for o in s.objects if o.type=='MESH'];anchors=0
 if label=='source':
  for o in meshes:
   if o.get('deform_role') not in ['dorsal','anal','pectoral']:continue
   uv=o.data.uv_layers.active;indices={loop.vertex_index for loop in o.data.loops if abs(uv.data[loop.index].uv.y)<1e-7}
   assert indices
   for i in indices:
    for group in o.data.vertices[i].groups:
     if o.vertex_groups[group.group].name in ['Dorsal','Anal','Pectoral_L','Pectoral_R'] or o.vertex_groups[group.group].name.startswith('DorsalWave_'):assert group.weight<1e-6,(o.name,i,group.weight)
   anchors+=1
 frames=[1,1+SPAN//4,1+SPAN//2,1+SPAN*3//4,END_FRAME];poses=[];roles={};contacts=[]
 from fin_attachment import check_surface_contact
 for f in frames:
  s.frame_set(f);contacts.append({'frame':f,'fins':check_surface_contact(s)});dg=bpy.context.evaluated_depsgraph_get();frame={}
  for o in meshes:
   ev=o.evaluated_get(dg);p=[ev.matrix_world@v.co for v in ev.data.vertices];assert p and all(math.isfinite(c) for v in p for c in v),(label,o.name,f);frame[o.name]=p
  poses.append(frame)
 for name in poses[0]:
  movement=max((a-b).length for a,b in zip(poses[0][name],poses[1][name]));endpoint=max((a-b).length for a,b in zip(poses[0][name],poses[-1][name]));assert endpoint<.0001,(label,name,endpoint);roles[name]={'motion':movement,'loop_error':endpoint}
 for prefix in (['Dorsal_','Pectoral_'] if slug=='ribbonfish' else ['Caudal_','Dorsal_','Anal_','Pectoral_']):
  found=[v['motion'] for k,v in roles.items() if k.startswith(prefix)];assert found and max(found)>.001,(label,prefix,found)
 ribbon_wave=None
 if slug=='ribbonfish':
  assert not any(o.name.startswith(('Caudal_','Pelvic_','Anal_')) for o in meshes),'Hairtail has no caudal/pelvic fins or visible broad anal fin'
  dorsal=next(o for o in meshes if o.name.startswith('Dorsal_ContinuousWave'))
  span=[0.0]*len(dorsal.data.vertices)
  for loop in dorsal.data.loops:span[loop.vertex_index]=dorsal.data.uv_layers.active.data[loop.index].uv.y
  tips=[v.index for v in dorsal.data.vertices if span[v.index]>.98];samples=[]
  for x in [-.9,.2,1.3]:
   index=min(tips,key=lambda i:abs((dorsal.matrix_world@dorsal.data.vertices[i].co).x-x));ys=[pose[dorsal.name][index].y for pose in poses];assert max(ys)-min(ys)>.005,(label,'Dorsal wave is static',x,ys);samples.append({'x':x,'y_samples':ys,'range':max(ys)-min(ys)})
  assert max(abs(a-b) for a,b in zip(samples[0]['y_samples'],samples[1]['y_samples']))>.005,'Dorsal probes must have distinct wave phases'
  body=next(o for o in meshes if o.name.startswith('Ribbon_ContinuousBody'));indices=[v.index for v in body.data.vertices if (body.matrix_world@v.co).x>1.80];tail_motion=max((poses[0][body.name][i]-poses[1][body.name][i]).length for i in indices);assert tail_motion>.005
  ribbon_wave={'dorsal_probes':samples,'tapered_tail_motion':tail_motion,'separate_caudal_fin':False}
 if slug in ['threadfin','fourfinger-threadfin']:
  filaments=[v for name,v in roles.items() if name.startswith('Pectoral_Filament_')]
  assert len(filaments)==8,(label,'Four sensory rays per flank required',len(filaments))
  assert all(v['motion']>.001 for v in filaments),(label,'Sensory rays must move with their fins')
 expected_barbels=2*len(json.loads((HERE/'profiles.json').read_text())[slug].get('barbels',[]));barbels=[o for o in meshes if o.name.startswith('Barbel_')];assert len(barbels)==expected_barbels,(label,'Mouth-barbel count',len(barbels),expected_barbels)
 assert any(o.type=='ARMATURE' for o in s.objects)
 return {'barbel_meshes':len(barbels),'surface_contact':contacts,'ribbon_wave':ribbon_wave,'fin_roots_checked':anchors,'meshes':len(meshes),'vertices':sum(len(o.data.vertices) for o in meshes),'motion_by_mesh':roles,'frames':frames,'packed_images':all(i.packed_file for i in bpy.data.images if i.source=='FILE')}
source=observe('source');s.frame_set(13)
# Flatten only temporary skinned mesh copies; keep editable source parenting intact.
root=next(o for o in s.objects if o.name.startswith('ASSET_PhotoInformed_'));selected=[root]+list(root.children_recursive);saved=[]
for o in [o for o in selected if o.type=='MESH']:
 saved.append((o,o.parent,o.matrix_basis.copy(),o.data));world=o.matrix_world.copy();o.data=o.data.copy();o.parent=None;o.matrix_world=world
 # Closed body caps had collinear cylinder UVs and n-gons. Give those caps
 # a small planar head/tail footprint and triangulate them before tangent export.
 uv=o.data.uv_layers.active
 for poly in o.data.polygons:
  if len(poly.vertices)>4 and uv:
   for li in poly.loop_indices:
    p=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(.035+.08*p.y,.50+.12*p.z)
 bm=bmesh.new();bm.from_mesh(o.data);ngons=[f for f in bm.faces if len(f.verts)>4]
 if ngons:bmesh.ops.triangulate(bm,faces=ngons)
 bm.to_mesh(o.data);bm.free();o.data.update()
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
bpy.ops.object.select_all(action='DESELECT')
for o in selected:o.select_set(True)
glb=OUT/'model.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_nla_strips_merged_animation_name='Swim_Loop',export_frame_range=True,export_force_sampling=True,export_tangents=True,export_texcoords=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));s=bpy.context.scene;export=observe('glb_reimport');assert len(bpy.data.actions)==1
report={'slug':slug,'source':source,'export':export,'source_sha256':hashlib.sha256((OUT/(slug+'.blend')).read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256(glb.read_bytes()).hexdigest(),'actions':[a.name for a in bpy.data.actions],'visual_acceptance':'separate_manual_gate'};(OUT/'motion-verification.json').write_text(json.dumps(report,indent=2)+'\n')
if '--export-only' in sys.argv:sys.exit(0)
bpy.ops.wm.open_mainfile(filepath=str(OUT/(slug+'.blend')));s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';s.render.resolution_x=720;s.render.resolution_y=480;s.render.resolution_percentage=100;frames=OUT/'frames';frames.mkdir(exist_ok=True)
for i,f in enumerate(range(1,END_FRAME,2)):
 s.frame_set(f);s.render.filepath=str(frames/('%03d.png'%i));bpy.ops.render.render(write_still=True)
print('FINISHED',slug,flush=True)
