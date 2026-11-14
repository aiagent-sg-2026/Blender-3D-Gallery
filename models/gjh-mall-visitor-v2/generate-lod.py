"""Derive a skinned, animated LOD from the validated high-detail export."""
from pathlib import Path
import bpy
root=Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(root/'exports/gjh-mall-visitor-v2.glb'))
for obj in bpy.context.scene.objects:
    if obj.type=='MESH':
        transform=obj.matrix_world.copy()
        obj.parent=None
        obj.matrix_world=transform
        modifier=obj.modifiers.new('LOD triangle reduction','DECIMATE')
        modifier.ratio=.45
        bpy.context.view_layer.objects.active=obj
        bpy.ops.object.modifier_apply(modifier=modifier.name)
bpy.ops.export_scene.gltf(filepath=str(root/'exports/gjh-mall-visitor-v2-lod1.glb'),export_format='GLB',export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_cameras=False,export_lights=False)
