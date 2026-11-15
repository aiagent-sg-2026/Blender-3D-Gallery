"""Step 3 prototype: head with eye openings, lid blink, brows, cheeks, mouth corners.

Run:  blender --background --factory-startup --python-exit-code 1 \
        --python models/chibi-mall-guide-v5/prototype/blink/build.py -- OUT_DIR
Blender space: Z up, character faces -Y (exports to glTF +Z). 1 unit = 1 m, character about 1.0 m tall.
Prototype only: no body, no rig, no mouth cavity, no texture. All numbers are starting values.
"""
import bpy, bmesh, math, sys, json, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree

OUT = sys.argv[sys.argv.index('--') + 1]
MODE = os.environ.get('BLINK_MODE', 'lid')   # 'lid': skin covers the eye (key on Head); 'eyes': eyes sink behind the skin (key on merged Eyes mesh)
os.makedirs(OUT, exist_ok=True)

# ---- config (single source for this prototype) ----
C = dict(
    head_centre=(0.0, 0.0, 0.80), rx=0.185, ry=0.175, rz=0.18,
    seg_u=96, seg_v=64,
    eye_x=0.078, eye_z=0.775, eye_r=0.055, eye_scale=(1.0, 0.30, 1.15), eye_sink=0.0125,
    lid_core=0.050, lid_radius=0.078,   # blink: full-strength core radius and falloff radius around each eye (xz plane)
    brow_dz=0.068, brow_w=0.050, brow_h=0.012, brow_bump=0.005,
    cheek_dx=0.115, cheek_dz=-0.055, cheek_r=0.060,
    mouth_z=0.700, mouth_w=0.038,
)
hc = Vector(C['head_centre'])

def smooth(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)

def surface_y(x, z):
    """Front (-Y) surface of the base head ellipsoid at (x, z)."""
    u = (x / C['rx']) ** 2 + ((z - hc.z) / C['rz']) ** 2
    return hc.y - C['ry'] * math.sqrt(max(0.0, 1.0 - u))

# ---- head mesh: ellipsoid ----
bpy.ops.wm.read_factory_settings(use_empty=True)
bm = bmesh.new()
bmesh.ops.create_uvsphere(bm, u_segments=C['seg_u'], v_segments=C['seg_v'], radius=1.0)
for v in bm.verts:
    v.co = Vector((v.co.x * C['rx'], v.co.y * C['ry'], v.co.z * C['rz'])) + hc
# base-shape details (brow ridge, mouth groove) baked into the basis
for v in bm.verts:
    if v.co.y > hc.y - 0.02:      # back half: untouched
        continue
    for sx in (-1, 1):
        d = math.hypot(v.co.x - sx * C['eye_x'], (v.co.z - (C['eye_z'] + C['brow_dz'])) * 2.2)
        v.co.y -= C['brow_bump'] * (1 - smooth(d / C['brow_w']))
    dm = math.hypot(v.co.x / C['mouth_w'] * 0.6, (v.co.z - C['mouth_z']) / 0.006)
    v.co.y += 0.003 * (1 - smooth(dm / 1.0))
me = bpy.data.meshes.new('Head'); bm.to_mesh(me); bm.free()
head = bpy.data.objects.new('Head', me)
bpy.context.scene.collection.objects.link(head)
for p in me.polygons: p.use_smooth = True
head.shape_key_add(name='Basis', from_mix=False)

def add_key(name, fn):
    k = head.shape_key_add(name=name, from_mix=False)
    for i, v in enumerate(me.vertices):
        k.data[i].co = fn(v.co.copy(), i)
    k.value = 0.0
    return k

# ---- eyes: separate meshes, protruding through the head surface ----
eye_front = {}
eye_cy = {}
def make_eye(side):
    x = side * C['eye_x']; z = C['eye_z']
    cy = surface_y(x, z) + C['eye_sink']          # centre sunk slightly behind the skin
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=20, radius=C['eye_r'])
    for v in bm.verts:
        v.co = Vector((v.co.x * C['eye_scale'][0], v.co.y * C['eye_scale'][1], v.co.z * C['eye_scale'][2])) + Vector((x, cy, z))
    m = bpy.data.meshes.new('Eye'); bm.to_mesh(m); bm.free()
    o = bpy.data.objects.new('Eye.L' if side > 0 else 'Eye.R', m)
    bpy.context.scene.collection.objects.link(o)
    for p in m.polygons: p.use_smooth = True
    eye_front[side] = cy - C['eye_r'] * C['eye_scale'][1]
    eye_cy[side] = cy
    return o
eyes = [make_eye(+1), make_eye(-1)]
eyes_obj = None
if MODE == 'eyes':
    bpy.ops.object.select_all(action='DESELECT')
    for e in eyes: e.select_set(True)
    bpy.context.view_layer.objects.active = eyes[0]
    bpy.ops.object.join()
    eyes_obj = eyes[0]; eyes_obj.name = 'Eyes'; eyes_obj.data.name = 'Eyes'
    eyes_obj.shape_key_add(name='Basis', from_mix=False)
    kb = eyes_obj.shape_key_add(name='blink', from_mix=False)
    for i, v in enumerate(eyes_obj.data.vertices):
        kb.data[i].co = Vector((v.co.x, v.co.y + 0.040, v.co.z))   # sink 40 mm behind the skin
    kb.value = 0.0
    eyes = [eyes_obj]

# ---- shape keys ----
def blink_fn(co, i):
    """Lid: skin inside the core radius is pushed out to just in front of the eye dome; smooth falloff outside."""
    for side in (-1, 1):
        ex = side * C['eye_x']
        d = math.hypot(co.x - ex, co.z - C['eye_z'])
        if d >= C['lid_radius'] or co.y >= hc.y: continue
        t = 1.0 - smooth((d - C['lid_core']) / (C['lid_radius'] - C['lid_core']))
        dx = (co.x - ex) / (C['eye_r'] * C['eye_scale'][0] * 1.25)
        dz = (co.z - C['eye_z']) / (C['eye_r'] * C['eye_scale'][2] * 1.25)
        q = 1.0 - dx * dx - dz * dz
        depth = C['eye_r'] * C['eye_scale'][1] * (math.sqrt(q) if q > 0 else 0.0)
        dome = eye_cy[side] - depth - 0.004        # skin sits 4 mm in front of the eye dome
        target = min(co.y, dome)
        co.y = co.y + (target - co.y) * t
    return co

def surprised_fn(co, i):
    for side in (-1, 1):
        d = math.hypot(co.x - side * C['eye_x'], (co.z - (C['eye_z'] + C['brow_dz'])) * 2.2)
        t = 1.0 - smooth(d / C['brow_w'])
        if t > 0 and co.y < hc.y: co.z += C['brow_h'] * t
    dm = math.hypot(co.x / (C['mouth_w'] * 0.8), (co.z - C['mouth_z']) / 0.02)
    if dm < 1 and co.y < hc.y: co.z -= 0.010 * (1 - smooth(dm))   # mouth drops (no cavity in prototype)
    return co

def smile_fn(co, i):
    for side in (-1, 1):
        d = math.hypot(co.x - side * C['cheek_dx'], co.z - (C['eye_z'] + C['cheek_dz']))
        t = 1.0 - smooth(d / C['cheek_r'])
        if t > 0 and co.y < hc.y:
            co.z += 0.012 * t; co.y -= 0.008 * t
        dm = math.hypot(co.x - side * C['mouth_w'], (co.z - C['mouth_z']) / 0.7)
        tm = 1.0 - smooth(dm / 0.03)
        if tm > 0 and co.y < hc.y: co.z += 0.010 * tm
        # brows relax up slightly
        db = math.hypot(co.x - side * C['eye_x'], (co.z - (C['eye_z'] + C['brow_dz'])) * 2.2)
        tb = 1.0 - smooth(db / C['brow_w'])
        if tb > 0 and co.y < hc.y: co.z += 0.003 * tb
    return co

add_key('smile', smile_fn); add_key('surprised', surprised_fn)
if MODE == 'lid': add_key('blink', blink_fn)

# ---- materials ----
def mat(name, rgb, rough):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*rgb, 1); b.inputs['Roughness'].default_value = rough
    return m
skin = mat('Skin', (0.93, 0.64, 0.50), 0.55); eyem = mat('Eye', (0.07, 0.035, 0.02), 0.15)
head.data.materials.append(skin)
for e in eyes: e.data.materials.append(eyem)

# ---- measurement: how much of each eye is visible from the front, per key ----
def eye_visibility(key_values):
    """Count front-facing eye vertices (basis normal.y < -0.25) that a ray from the front reaches without hitting the head."""
    for ob in [head] + ([eyes_obj] if eyes_obj else []):
        for k in ob.data.shape_keys.key_blocks:
            if k.name != 'Basis': k.value = key_values.get(k.name, 0.0)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    em = head.evaluated_get(dg).to_mesh()
    verts = [v.co.copy() for v in em.vertices]
    tri_idx = []
    for p in em.polygons:
        vs = list(p.vertices)
        for j in range(1, len(vs) - 1): tri_idx.append((vs[0], vs[j], vs[j + 1]))
    bvh = BVHTree.FromPolygons(verts, tri_idx)
    sc = C['eye_scale']; res = {}
    for e in eyes:
        ev = e.evaluated_get(dg).to_mesh()
        total = vis = 0
        for bv, v in zip(e.data.vertices, ev.vertices):
            side = 1 if bv.co.x > 0 else -1
            cen = Vector((side * C['eye_x'], eye_cy[side], C['eye_z']))
            rel = bv.co - cen
            n = Vector((rel.x / sc[0] ** 2, rel.y / sc[1] ** 2, rel.z / sc[2] ** 2)).normalized()
            if n.y > -0.25: continue
            total += 1
            if bvh.ray_cast(v.co + Vector((0, -0.0005, 0)), Vector((0, -1, 0)), 1.0)[0] is None: vis += 1
        res[e.name] = (vis, total)
        e.evaluated_get(dg).to_mesh_clear()
    head.evaluated_get(dg).to_mesh_clear()
    return res

# only count the front half of each eye (those whose y is in front of the eye centre)
def front_visibility(key_values):
    r = eye_visibility(key_values)
    return r

measure = {}
for label, kv in [('open', {}), ('blink', {'blink': 1.0}), ('blink_half', {'blink': 0.5}), ('smile', {'smile': 1.0}), ('surprised', {'surprised': 1.0})]:
    measure[label] = front_visibility(kv)
for ob in [head] + ([eyes_obj] if eyes_obj else []):
    for k in ob.data.shape_keys.key_blocks:
        if k.name != 'Basis': k.value = 0.0

# ---- export ----
glb = os.path.join(OUT, f'blink-prototype-{MODE}.glb')
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', export_morph=True, export_morph_normal=True,
                          export_animations=False, export_yup=True, export_apply=False)
tris = sum(len(p.vertices) - 2 for o in [head] + eyes for p in o.data.polygons)
report = dict(mode=MODE, config=C, triangles=tris, eye_visibility_vis_total=measure)
json.dump(report, open(os.path.join(OUT, f'build-report-{MODE}.json'), 'w'), indent=1)
print('EXPORTED', glb, 'triangles', tris)
print(json.dumps(measure))
