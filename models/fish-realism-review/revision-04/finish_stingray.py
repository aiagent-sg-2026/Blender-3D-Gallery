"""Export one real morph-animation clip and render the review loop."""
import bpy,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;OUT=HERE/'stingray'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'stingray-review.blend'));s=bpy.context.scene
sys.path.insert(0,str(HERE))
from portable_morphs import make_portable,restore_independent_wave_bases
for o in list(s.objects):
 if o.type=='MESH' and o.data.shape_keys:
  make_portable(o)
  if o.name=='Maskray_ContinuousDisc':restore_independent_wave_bases(o)
s.frame_set(13);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'stingray-review.blend'))
s.render.filepath=str(OUT/'preview.png');bpy.ops.render.render(write_still=True)
s.frame_set(1);bpy.ops.object.select_all(action='DESELECT')
for o in s.objects:
 if o.type not in ['CAMERA','LIGHT']:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT/'stingray-review.glb'),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_nla_strips_merged_animation_name='Natural_Swim_Loop',export_frame_range=True,export_force_sampling=True,export_morph=True,export_morph_animation=True,export_tangents=True)
# The review GIF uses the same scene, camera and material response.
s.render.engine='BLENDER_EEVEE';s.render.resolution_x=768;s.render.resolution_y=512;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';frames=OUT/'frames';frames.mkdir(exist_ok=True)
for i,f in enumerate(range(1,97,2)):
 s.frame_set(f);s.render.filepath=str(frames/('%03d.png'%i));bpy.ops.render.render(write_still=True)
print('EXPORTED_AND_RENDERED',flush=True)
