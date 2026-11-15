"""Render six axis-aligned workbench views (texture colour) of a part GLB to see its orientation.
Run: blender --background --factory-startup --python axis_views.py -- PART.glb OUT.png"""
import bpy, sys, math
from mathutils import Vector
glb, out = sys.argv[sys.argv.index('--') + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=glb)
sc = bpy.context.scene; sc.render.engine = 'BLENDER_WORKBENCH'; sh = sc.display.shading; sh.light = 'STUDIO'; sh.color_type = 'SINGLE'; sh.single_color = (0.75, 0.6, 0.5)
sc.render.resolution_x = sc.render.resolution_y = 300; sc.render.film_transparent = False
w = bpy.data.worlds.new('w'); w.color = (0.9, 0.9, 0.95); sc.world = w
cam = bpy.data.objects.new('c', bpy.data.cameras.new('c')); sc.collection.objects.link(cam); sc.camera = cam; cam.data.type = 'ORTHO'; import numpy as np; ext = max(np.ptp(np.array([(o.matrix_world @ v.co)[:] for v in o.data.vertices]), axis=0).max() for o in bpy.data.objects if o.type == 'MESH'); cam.data.ortho_scale = ext * 1.2; ctr = sum((Vector(c) for o in bpy.data.objects if o.type == 'MESH' for c in [np.mean([(o.matrix_world @ v.co)[:] for v in o.data.vertices], axis=0)]), Vector()) 
views = {'-Y(front)': (90, 0, 0, (0, -3, 0)), '+Y(back)': (90, 0, 180, (0, 3, 0)), '+X': (90, 0, 90, (3, 0, 0)), '-X': (90, 0, -90, (-3, 0, 0)), '+Z(top)': (0, 0, 0, (0, 0, 3)), '-Z(bottom)': (180, 0, 0, (0, 0, -3))}
import os; base = out[:-4]; paths = []
for k, (rx, ry, rz, loc) in views.items():
    cam.location = loc; cam.rotation_euler = (math.radians(rx), math.radians(ry), math.radians(rz)); sc.render.filepath = f'{base}_{len(paths)}.png'; bpy.ops.render.render(write_still=True); paths.append(sc.render.filepath)
print('VIEWS', list(views), paths)
