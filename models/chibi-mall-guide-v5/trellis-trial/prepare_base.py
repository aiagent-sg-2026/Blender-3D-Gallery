"""Prepare the TRELLIS seed-1 reconstruction as the base model: report and fix the material, put the feet on z = 0 centred on the body,
split the held sign into its own object, render four views with the real texture, export GLBs.
Run (repo root): blender --background --factory-startup --python-exit-code 1 --python models/chibi-mall-guide-v5/trellis-trial/prepare_base.py -- TARGET.glb OUT_DIR"""
import bpy, bmesh, sys, os, json, math
import numpy as np
from mathutils import Vector
glb, OUT = sys.argv[sys.argv.index('--') + 1:][:2]; os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=glb)
ms = [o for o in bpy.data.objects if o.type == 'MESH']; assert len(ms) == 1; body = ms[0]; body.name = 'Body'
bpy.ops.object.select_all(action='DESELECT'); body.select_set(True); bpy.context.view_layer.objects.active = body
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
for o in [o for o in bpy.data.objects if o.type != 'MESH']: bpy.data.objects.remove(o)
YAW = float(os.environ.get('YAW', '0'))   # degrees about Z; most TRELLIS results face +X, so YAW=-90 turns them to face -Y (the front)
if YAW:
    body.rotation_mode = 'XYZ'; body.rotation_euler = (0, 0, math.radians(YAW)); bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
mat = body.data.materials[0]; bsdf = mat.node_tree.nodes['Principled BSDF']
rep = {'material': mat.name, 'metallic': bsdf.inputs['Metallic'].default_value, 'roughness': bsdf.inputs['Roughness'].default_value,
       'base_color_linked': bool(bsdf.inputs['Base Color'].is_linked), 'triangles': len(body.data.polygons), 'verts': len(body.data.vertices)}
bsdf.inputs['Metallic'].default_value = 0.0; bsdf.inputs['Roughness'].default_value = 0.55
# feet on z = 0, centred on the body (the sign is excluded from the x centre)
me = body.data; P = np.array([v.co[:] for v in me.vertices]); nosign = P[~((P[:, 0] < -0.16) & (P[:, 2] > -0.2) & (P[:, 2] < 0.16))]
body.location = Vector((-(nosign[:, 0].min() + nosign[:, 0].max()) / 2, -(nosign[:, 1].min() + nosign[:, 1].max()) / 2 * 0, -P[:, 2].min()))
bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
NOSPLIT = os.environ.get('NOSPLIT', '0') == '1'   # keep the sign in the body mesh (it moves with the right arm)
# split the sign: found from the texture colour (brass rim and handle) and geometry, not from a fixed box
me = body.data
img = [n.image for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE'][0]; TW, TH = img.size; tex = np.array(img.pixels[:], dtype=np.float32).reshape(TH, TW, 4)[:, :, :3]
uvl = me.uv_layers.active.data
def face_col(p):
    u = float(np.mean([uvl[l].uv[0] for l in p.loop_indices])); v = float(np.mean([uvl[l].uv[1] for l in p.loop_indices])); return tex[int(v * (TH - 1)), int(u * (TW - 1))]
cent = np.array([p.center[:] for p in me.polygons]); cols = np.array([face_col(p) for p in me.polygons])
gold = (cols[:, 0] > 0.5) & (cols[:, 1] > 0.4) & (cols[:, 2] < 0.35) & (cent[:, 0] < -0.09) & (cent[:, 2] > 0.18) & (cent[:, 2] < 0.70)
gr = (cols[:, 0] > 0.5) & (cols[:, 1] > 0.4) & (cols[:, 2] < 0.35); print('DBG gold pts x', np.percentile(cent[gr, 0], [0, 25, 50, 75, 100]).round(3), 'y', np.percentile(cent[gr, 1], [0, 50, 100]).round(3), 'z', np.percentile(cent[gr, 2], [0, 25, 50, 75, 100]).round(3))
print('DBG gold_raw', int(((cols[:, 0] > 0.5) & (cols[:, 1] > 0.4) & (cols[:, 2] < 0.35)).sum()), 'x<-.09', int((cent[:, 0] < -0.09).sum()), 'zrange', cent[:, 2].min().round(3), cent[:, 2].max().round(3), 'xrange', cent[:, 0].min().round(3), cent[:, 0].max().round(3))
zlo, zhi = cent[gold, 2].min(), cent[gold, 2].max(); thr = zlo + 0.30 * (zhi - zlo)   # the lowest 30 percent of the brass is the handle, the rest the board rim
rim = gold & (cent[:, 2] > thr); handle = gold & ~rim
c0 = np.median(cent[rim], axis=0); R = float(np.percentile(np.linalg.norm(cent[rim] - c0, axis=1), 85))
u_, s_, vt = np.linalg.svd(cent[rim] - c0); nrm = vt[2]                      # board plane normal
dist = np.linalg.norm(cent - c0, axis=1); depth = np.abs((cent - c0) @ nrm)
is_sign_colour = gold | (cols[:, 1] > 0.72) | ((cols[:, 1] > cols[:, 0] + 0.05) & (cols[:, 1] > cols[:, 2] + 0.05))   # brass, ivory, green icon (not hair, skin or glove white-grey)
board = (dist < R * 1.12) & (depth < 0.035) & is_sign_colour & (cent[:, 0] < -0.08)
hp = cent[handle]; hb, ht = hp[hp[:, 2].argmin()], hp[hp[:, 2].argmax()]; ax = ht - hb; ax /= max(np.linalg.norm(ax), 1e-9)
t = np.clip(((cent - hb) @ ax), -0.02, np.linalg.norm(ht - hb) + 0.04); d_line = np.linalg.norm(cent - (hb + np.outer(t, ax)), axis=1)
not_white = ~((cols.min(axis=1) > 0.8))
handle_sel = (d_line < 0.016) & not_white & (cent[:, 0] < -0.09)
sel = board | handle_sel
rep['sign'] = dict(rim_faces=int(rim.sum()), handle_faces=int(handle.sum()), board_faces=int(board.sum()), handle_selected=int(handle_sel.sum()), centre=c0.round(3).tolist(), radius=round(float(R), 3))
if NOSPLIT: sel = np.zeros(len(me.polygons), dtype=bool)
if sel.any():
    bpy.ops.object.mode_set(mode='EDIT'); ebm = bmesh.from_edit_mesh(me); ebm.faces.ensure_lookup_table()
    for f in ebm.faces: f.select_set(False)
    for f in ebm.faces:
        if sel[f.index]: f.select_set(True)
    bmesh.update_edit_mesh(me); bpy.ops.mesh.separate(type='SELECTED'); bpy.ops.object.mode_set(mode='OBJECT')
objs = [o for o in bpy.data.objects if o.type == 'MESH']; objs.sort(key=lambda o: len(o.data.polygons)); body = objs[-1]
sign = objs[0] if len(objs) > 1 else None
if sign is not None: sign.name = 'Sign'
rep['body_triangles'] = len(body.data.polygons); rep['sign_triangles'] = len(sign.data.polygons) if sign else 0
rep['body_bbox'] = [np.array([(body.matrix_world @ v.co)[:] for v in body.data.vertices]).min(0).round(3).tolist(), np.array([(body.matrix_world @ v.co)[:] for v in body.data.vertices]).max(0).round(3).tolist()]
# render: unlit texture colours and a lit view
N = 700; sc = bpy.context.scene; sc.render.engine = 'BLENDER_WORKBENCH'; sc.render.resolution_x = N; sc.render.resolution_y = N
sc.display.shading.light = 'FLAT'; sc.display.shading.color_type = 'TEXTURE'; sc.view_settings.view_transform = 'Standard'
sc.world = bpy.data.worlds.new('w'); sc.world.color = (0.92, 0.91, 0.97)
cd = bpy.data.cameras.new('cam'); cd.type = 'ORTHO'; cd.ortho_scale = 1.12; cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam
tiles = []
for az in (0, 35, 90, 180):
    a = math.radians(az); cam.location = (math.sin(a) * 4, -math.cos(a) * 4, 0.52); cam.rotation_euler = (math.radians(90), 0, a)
    sc.render.filepath = os.path.join(OUT, 'tmp.png'); bpy.ops.render.render(write_still=True)
    tiles.append(np.array(bpy.data.images.load(sc.render.filepath).pixels[:], dtype=np.float32).reshape(N, N, 4))
sheet = np.concatenate(tiles, axis=1); im = bpy.data.images.new('s', sheet.shape[1], N, alpha=True); im.pixels = sheet.reshape(-1).tolist()
im.filepath_raw = os.path.join(OUT, 'base-views.png'); im.file_format = 'PNG'; im.save()
for o in [x for x in (body, sign) if x]: o.select_set(False)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, 'base-with-sign.glb'), export_format='GLB', export_yup=True, use_selection=True)
bpy.ops.object.select_all(action='DESELECT'); body.select_set(True); bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, 'base-body.glb'), export_format='GLB', export_yup=True, use_selection=True)
json.dump(rep, open(os.path.join(OUT, 'base-report.json'), 'w'), indent=1); print('REPORT', json.dumps(rep))
