"""Render sample frames of every clip from guide-rigged.blend in Workbench with texture colours.
Run: blender --background GUIDE.blend --python render_poses.py -- OUT.png"""
import bpy, sys, math, numpy as np
out = sys.argv[sys.argv.index('--') + 1]; rig = bpy.data.objects['Rig']; sc = bpy.context.scene
acts = {a.name: a for a in bpy.data.actions}
shots = [x for x in [('idle', 16), ('walk_calm', 10), ('walk_calm', 28), ('walk_bouncy', 7), ('wave', 24), ('point', 19)] if x[0] in acts]
N = 520; sc.render.engine = 'BLENDER_WORKBENCH'; sc.render.resolution_x = N; sc.render.resolution_y = N
sc.display.shading.light = 'FLAT'; sc.display.shading.color_type = 'TEXTURE'; sc.view_settings.view_transform = 'Standard'
sc.world = bpy.data.worlds.new('w'); sc.world.color = (0.92, 0.91, 0.97)
cd = bpy.data.cameras.new('cam'); cd.type = 'ORTHO'; cd.ortho_scale = 1.25; cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam
a = math.radians(25); cam.location = (math.sin(a) * 4, -math.cos(a) * 4, 0.55); cam.rotation_euler = (math.radians(90), 0, a)
rig.animation_data.action = None
for tr in rig.animation_data.nla_tracks: tr.mute = True
tiles = []
for name, f in shots:
    rig.animation_data.action = acts[name]; sc.frame_set(f)
    sc.render.filepath = '/tmp/_pose.png'; bpy.ops.render.render(write_still=True)
    tiles.append(np.array(bpy.data.images.load('/tmp/_pose.png').pixels[:], dtype=np.float32).reshape(N, N, 4))
sheet = np.concatenate(tiles, axis=1); im = bpy.data.images.new('s', sheet.shape[1], N, alpha=True); im.pixels = sheet.reshape(-1).tolist()
im.filepath_raw = out; im.file_format = 'PNG'; im.save(); print('POSES', [s[0] for s in shots])
