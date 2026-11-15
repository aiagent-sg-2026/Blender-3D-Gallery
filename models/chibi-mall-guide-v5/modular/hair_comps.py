"""Split a hair GLB into loose parts and render them with one colour each (largest 12) to choose which to delete. Run: blender -b --factory-startup --python hair_comps.py -- HAIR.glb OUT.png"""
import bpy, sys, math, colorsys, numpy as np
glb, out = sys.argv[sys.argv.index('--') + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=glb)
o = [o for o in bpy.data.objects if o.type == 'MESH'][0]; bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM'); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.separate(type='LOOSE'); bpy.ops.object.mode_set(mode='OBJECT')
ms = sorted([x for x in bpy.data.objects if x.type == 'MESH'], key=lambda x: -len(x.data.vertices))
sc = bpy.context.scene; sc.render.engine = 'BLENDER_WORKBENCH'; sc.display.shading.light = 'STUDIO'; sc.display.shading.color_type = 'OBJECT'
for i, m in enumerate(ms):
    m.color = (*colorsys.hsv_to_rgb(i / 12 % 1, 0.9, 0.9), 1) if i < 12 else (0.5, 0.5, 0.5, 1)
    if i < 12:
        P = np.array([v.co[:] for v in m.data.vertices]); print('COMP', i, len(P), P.min(0).round(2), P.max(0).round(2))
sc.render.resolution_x = sc.render.resolution_y = 400; w = bpy.data.worlds.new('w'); w.color = (1, 1, 1); sc.world = w
cam = bpy.data.objects.new('c', bpy.data.cameras.new('c')); sc.collection.objects.link(cam); sc.camera = cam; cam.data.type = 'ORTHO'; cam.data.ortho_scale = 1.1
for i, az in enumerate((0, 90)):
    a = math.radians(az); cam.location = (math.sin(a) * 4, -math.cos(a) * 4, 0); cam.rotation_euler = (math.radians(90), 0, a); sc.render.filepath = f'{out[:-4]}_{i}.png'; bpy.ops.render.render(write_still=True)
