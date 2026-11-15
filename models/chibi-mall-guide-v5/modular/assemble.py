"""Assemble the four TRELLIS parts (body, hair, cap, sign) into one modular figure, 1.00 m tall, feet on z=0, facing -Y.
Run: blender --background --factory-startup --python assemble.py -- PARTS_DIR OUT_DIR   (env BODY=body_s3 HAIR=hair_s1 CAP=cap_s2 SIGN=sign_s3, HAIR_W=1.3 CAP_W=0.73, HAIR_DY, HAIR_DZ, CAP_DZ, HAIR_TARGET=4A2C22)"""
import bpy, sys, os, json, math
import numpy as np
from mathutils import Vector
PARTS, OUT = sys.argv[sys.argv.index('--') + 1:][:2]; os.makedirs(OUT, exist_ok=True)
E = lambda k, d: float(os.environ.get(k, d)); S = lambda k, d: os.environ.get(k, d)
bpy.ops.wm.read_factory_settings(use_empty=True)

def load(name, obj_name):
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=os.path.join(PARTS, name + '.glb'))
    new = [o for o in bpy.data.objects if o not in before]; ms = [o for o in new if o.type == 'MESH']; assert len(ms) == 1; o = ms[0]; o.name = obj_name
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o; bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    for x in new:
        if x is not o and x.name in bpy.data.objects: bpy.data.objects.remove(x)
    m = o.data.materials[0]; m.name = obj_name + 'Mat'; b = m.node_tree.nodes['Principled BSDF']; b.inputs['Metallic'].default_value = 0.0; b.inputs['Roughness'].default_value = 0.55
    return o
def apply(o):
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o; bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
def verts(o): return np.array([v.co[:] for v in o.data.vertices])
def place(o, scale=None, loc=None):
    if scale is not None: o.scale = (scale,) * 3
    if loc is not None: o.location = loc
    apply(o)

rep = {}
body = load(S('BODY', 'body_s3'), 'Body'); P = verts(body)
body.location = (-(P[:, 0].min() + P[:, 0].max()) / 2, 0, -P[:, 2].min()); apply(body); P = verts(body); H = P[:, 2].max()
# head: widest row above the neck (min-width row between 55 and 80 percent of the height)
rows = np.linspace(0.55 * H, 0.80 * H, 40); wd = [np.ptp(P[(P[:, 2] > z - 0.01) & (P[:, 2] < z + 0.01), 0]) if ((P[:, 2] > z - 0.01) & (P[:, 2] < z + 0.01)).sum() > 3 else 9 for z in rows]
zneck = rows[int(np.argmin(wd))]; head = P[P[:, 2] > zneck + 0.01]; zt = head[:, 2].max(); hw = np.ptp(head[:, 0]); hc = np.array([(head[:, 0].min() + head[:, 0].max()) / 2, (head[:, 1].min() + head[:, 1].max()) / 2])
rep['body'] = dict(height=H, neck_z=zneck, head_top=zt, head_width=hw, head_depth=np.ptp(head[:, 1]), head_centre_xy=hc.tolist(), eye_row_est=zt - 0.45 * (zt - zneck))
print('HEAD', rep['body'])

hair = load(S('HAIR', 'hair_s1'), 'Hair')
# recolour: remap every texel to the chestnut target, keeping the baked shading
img = [n.image for n in hair.data.materials[0].node_tree.nodes if n.type == 'TEX_IMAGE'][0]; W, Hh = img.size; px = np.array(img.pixels[:], dtype=np.float32).reshape(Hh, W, 4)
t = S('HAIR_TARGET', '4A2C22'); tgt = np.array([int(t[i:i + 2], 16) / 255 for i in (0, 2, 4)]) ** 2.2
lum = px[:, :, :3].mean(axis=2); lo, hi = np.percentile(lum, [2, 98]); k = np.clip((lum - lo) / max(hi - lo, 1e-6), 0, 1)
px[:, :, :3] = tgt[None, None, :] * (0.55 + 1.5 * k[:, :, None]); img.pixels = px.ravel().tolist(); img.update()
def drop_wide(o, frac, xmax=9, idx=()):
    import bmesh
    bm = bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table(); total = np.ptp([v.co.x for v in bm.verts]); seen = set(); comps = []
    for v in bm.verts:
        if v.index in seen: continue
        st = [v]; seen.add(v.index); c = []
        while st:
            x = st.pop(); c.append(x)
            for e in x.link_edges:
                y = e.other_vert(x)
                if y.index not in seen: seen.add(y.index); st.append(y)
        comps.append(c)
    comps.sort(key=lambda c: -len(c)); kill = []
    for r, c in enumerate(comps):
        if (frac and np.ptp([x.co.x for x in c]) > frac * total) or max(abs(x.co.x) for x in c) > xmax or r in idx or (E('HAIR_UP_X', 0.3) and np.mean([x.co.z for x in c]) > E('HAIR_UP_Z', 0.1) and max(abs(x.co.x) for x in c) > E('HAIR_UP_X', 0.3)) or (E('HAIR_DROP_THIN', 0) and min(np.ptp([x.co[a] for x in c]) for a in range(3)) < E('HAIR_DROP_THIN', 0) and max(np.ptp([x.co[a] for x in c]) for a in range(3)) > E('HAIR_THIN_MAX', 0.28)): kill += c
    bmesh.ops.delete(bm, geom=kill, context='VERTS'); bm.to_mesh(o.data); bm.free(); return len(kill)
DROP = [int(x) for x in S('HAIR_DROP_IDX', '').split(',') if x]
if E('HAIR_DROP_WIDE', 0.7) > 0 or DROP or E('HAIR_DROP_THIN', 0) or E('HAIR_UP_X', 0.3): rep['hair_dropped_verts'] = drop_wide(hair, E('HAIR_DROP_WIDE', 0.7), E('HAIR_DROP_XMAX', 9), DROP)
hair.rotation_euler = (0, 0, math.radians(E('HAIR_ROT', 0))); apply(hair)
Q = verts(hair); hair_w = np.ptp(Q[:, 0]); sh = E('HAIR_W', 1.3) * hw / hair_w
Q = Q * sh; Q[:, 2] *= E('HAIR_SZ', 0.72); ztop = zt + E('HAIR_DZ', 0.03)
hair.scale = (sh, sh, sh * E('HAIR_SZ', 0.72)); place(hair, None, (hc[0] - (Q[:, 0].min() + Q[:, 0].max()) / 2, hc[1] + E('HAIR_DY', 0.04) - (Q[:, 1].min() + Q[:, 1].max()) / 2, ztop - Q[:, 2].max()))
Q = verts(hair); rep['hair'] = dict(scale=sh, bbox=[Q.min(0).tolist(), Q.max(0).tolist()])

cap = load(S('CAP', 'cap_s2'), 'Cap'); C = verts(cap); sc_ = E('CAP_W', 0.73) * hw / np.ptp(C[:, 0]); C = C * sc_
place(cap, sc_, (hc[0] - (C[:, 0].min() + C[:, 0].max()) / 2, hc[1] + E('CAP_DY', 0.03) - (C[:, 1].min() + C[:, 1].max()) / 2, Q[:, 2].max() + E('CAP_DZ', -0.04) - C[:, 2].min() - 0.4 * np.ptp(C[:, 2])))
C = verts(cap); rep['cap'] = dict(scale=sc_, bbox=[C.min(0).tolist(), C.max(0).tolist()])

sign = load(S('SIGN', 'sign_s3'), 'Sign'); G = verts(sign)
# right hand (character's right = -X): the open glove at the end of the -X arm
arm = P[(P[:, 0] < P[:, 0].min() + 0.07) & (P[:, 2] > 0.25 * H) & (P[:, 2] < 0.6 * H)]; hand = arm.mean(0); rep['right_hand'] = hand.tolist()
ss = E('SIGN_H', 0.40) / np.ptp(G[:, 2]); G = G * ss
place(sign, ss, (hand[0] - (G[:, 0].min() + G[:, 0].max()) / 2 + E('SIGN_DX', 0.0), hand[1] + E('SIGN_DY', -0.06), hand[2] - (G[:, 2].min() + 0.12 * np.ptp(G[:, 2]))))
G = verts(sign); rep['sign'] = dict(scale=ss, bbox=[G.min(0).tolist(), G.max(0).tolist()])

# scale everything so cap top to sole is 1.00 m
top = max(verts(o)[:, 2].max() for o in (body, hair, cap)); f = 1.0 / top; rep['total_height_before_scale'] = top; rep['final_scale'] = f
for o in (body, hair, cap, sign): o.location = (0, 0, 0); o.scale = (f,) * 3; apply(o)
json.dump(rep, open(os.path.join(OUT, 'assemble-report.json'), 'w'), indent=1)

# lit workbench renders of the whole figure
sc = bpy.context.scene; sc.render.engine = 'BLENDER_WORKBENCH'; sh_ = sc.display.shading; sh_.light = 'STUDIO'; sh_.color_type = 'TEXTURE'
sc.render.resolution_x = sc.render.resolution_y = 420; w = bpy.data.worlds.new('w'); w.color = (0.9, 0.9, 0.95); sc.world = w
cam = bpy.data.objects.new('c', bpy.data.cameras.new('c')); sc.collection.objects.link(cam); sc.camera = cam; cam.data.type = 'ORTHO'; cam.data.ortho_scale = 1.15
for i, az in enumerate((0, 45, 90, 180)):
    a = math.radians(az); cam.location = (math.sin(a) * 4, -math.cos(a) * 4, 0.5); cam.rotation_euler = (math.radians(90), 0, a); sc.render.filepath = os.path.join(OUT, f'view{i}.png'); bpy.ops.render.render(write_still=True)
bpy.ops.object.select_all(action='DESELECT')
for o in (body, hair, cap, sign): o.select_set(True)
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, 'assembled.glb'), export_format='GLB', use_selection=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'assembled.blend'))
print('DONE')
