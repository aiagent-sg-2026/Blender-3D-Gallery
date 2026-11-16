"""Align the TRELLIS seed-1 reconstruction to the built figure and measure the 3D deviation per part.
Run (repo root): blender --background --factory-startup --python-exit-code 1 --python models/chibi-mall-guide-v5/trellis-trial/align_compare.py -- TARGET.glb OUT_DIR
The target is only moved by a translation (found by a trimmed nearest-point fit on the legs, shoes, shorts, vest and shirt); it keeps its own scale (about 1.00 m tall)."""
import bpy, bmesh, sys, os, json, math
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import config as C, figure
glb, OUT = sys.argv[sys.argv.index('--') + 1:][:2]; os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
mats, parts, placeholders = figure.build_all(bpy, bmesh)
before = set(bpy.data.objects.keys())
bpy.ops.import_scene.gltf(filepath=glb)
new = [bpy.data.objects[n] for n in bpy.data.objects.keys() if n not in before]
meshes = [o for o in new if o.type == 'MESH']
assert len(meshes) == 1, [o.name for o in new]
tgt = meshes[0]; tgt.name = 'TARGET'
# make the target's world transform explicit: unparent keeping the transform
bpy.ops.object.select_all(action='DESELECT'); tgt.select_set(True); bpy.context.view_layer.objects.active = tgt
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
for o in new:
    if o is not tgt and o.type != 'MESH': bpy.data.objects.remove(o)
bpy.context.view_layer.update()
def tri_bvh(o):
    dg = bpy.context.evaluated_depsgraph_get(); return BVHTree.FromObject(o, dg)
def world_pts(o): return np.array([(o.matrix_world @ v.co)[:] for v in o.data.vertices])
tp = world_pts(tgt); report = {'target_bbox_min': tp.min(0).round(3).tolist(), 'target_bbox_max': tp.max(0).round(3).tolist()}
# ---- translation fit ----
fit_names = ['Shoe.L', 'Shoe.R']   # x and y are fitted on the shoes only; z is fixed so the target's soles sit on z = 0
fit_pts = np.vstack([world_pts(bpy.data.objects[n]) for n in fit_names])
tgt.location = Vector((-(tp[:, 0].min() + tp[:, 0].max()) / 2, 0.0, -tp[:, 2].min()))   # start: feet on z = 0, centred in x
shift = np.array(tgt.location[:])
for it in range(14):
    bpy.context.view_layer.update(); bvh = tri_bvh(tgt); diffs = []
    for p in fit_pts:
        loc, nrm, idx, dist = bvh.find_nearest(Vector(p))
        if loc is not None and dist < 0.06: diffs.append(np.array(loc[:]) - p)
    d = np.mean(diffs, axis=0); d[2] = 0.0
    tgt.location = tgt.location - Vector(d) * -1 * -1 if False else tgt.location - Vector(d)
    shift -= d
report['translation_applied'] = shift.round(4).tolist(); report['fit_pairs_last'] = len(diffs)
bpy.context.view_layer.update(); bvh = tri_bvh(tgt)
# ---- measure: ours -> target, per part ----
res = {}
for o in parts + placeholders:
    pts = world_pts(o); ds = []
    for p in pts:
        loc, nrm, idx, dist = bvh.find_nearest(Vector(p)); ds.append(dist)
    ds = np.array(ds) * 1000.0
    res[o.name] = dict(verts=len(ds), mean_mm=round(float(ds.mean()), 1), p95_mm=round(float(np.percentile(ds, 95)), 1), max_mm=round(float(ds.max()), 1))
report['ours_to_target'] = res
# ---- measure: target -> ours (area-weighted samples), attributed to the nearest of our parts ----
rng = np.random.default_rng(0); me = tgt.data; me.calc_loop_triangles()
V = np.array([(tgt.matrix_world @ v.co)[:] for v in me.vertices]); T = np.array([t.vertices[:] for t in me.loop_triangles])
A = 0.5 * np.linalg.norm(np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]]), axis=1)
pick = rng.choice(len(T), size=12000, p=A / A.sum()); r1 = rng.random((12000, 1)); r2 = rng.random((12000, 1)); flip = (r1 + r2 > 1)
r1[flip] = 1 - r1[flip]; r2[flip] = 1 - r2[flip]
S = V[T[pick, 0]] + r1 * (V[T[pick, 1]] - V[T[pick, 0]]) + r2 * (V[T[pick, 2]] - V[T[pick, 0]])
trees = {o.name: tri_bvh(o) for o in parts + placeholders}
sign_mask = (S[:, 0] < -0.16) & (S[:, 2] > 0.30) & (S[:, 2] < 0.66)     # the held sign sits on the character's right; we have no sign
by = {}; d_all = []
for p, sm in zip(S, sign_mask):
    if sm: continue
    best = (1e9, None)
    for n, t in trees.items():
        loc, nrm, idx, dist = t.find_nearest(Vector(p))
        if loc is not None and dist < best[0]: best = (dist, n)
    d_all.append(best[0]); by.setdefault(best[1], []).append(best[0])
report['target_to_ours'] = {k: dict(samples=len(v), mean_mm=round(float(np.mean(v)) * 1000, 1), p95_mm=round(float(np.percentile(v, 95)) * 1000, 1)) for k, v in by.items()}
d_all = np.array(d_all) * 1000
report['target_to_ours_all'] = dict(samples=len(d_all), mean_mm=round(float(d_all.mean()), 1), p95_mm=round(float(np.percentile(d_all, 95)), 1), excluded_sign=int(sign_mask.sum()))
json.dump(report, open(os.path.join(OUT, 'align-report.json'), 'w'), indent=1)
# ---- silhouettes: ours (red) over target (blue) ----
N = 700; sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'; sc.render.resolution_x = N; sc.render.resolution_y = N; sc.render.film_transparent = True
sc.display.shading.light = 'FLAT'; sc.display.shading.color_type = 'SINGLE'; sc.view_settings.view_transform = 'Standard'
cd = bpy.data.cameras.new('cam'); cd.type = 'ORTHO'; cd.ortho_scale = 1.12
cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam
def mask(vis_ours, az):
    for o in parts + placeholders: o.hide_render = not vis_ours
    tgt.hide_render = vis_ours; a = math.radians(az)
    cam.location = (math.sin(a) * 4, -math.cos(a) * 4, 0.52); cam.rotation_euler = (math.radians(90), 0, a)
    sc.display.shading.single_color = (1, 1, 1); sc.render.filepath = os.path.join(OUT, 'tmp.png'); bpy.ops.render.render(write_still=True)
    return np.array(bpy.data.images.load(sc.render.filepath).pixels[:], dtype=np.float32).reshape(N, N, 4)[::-1][:, :, 3] > 0.5
tiles = []
for az in (0, 35, 90, 180):
    mo = mask(True, az); mt = mask(False, az); img = np.ones((N, N, 3), dtype=np.float32) * np.array([0.92, 0.91, 0.97])
    img[mt] = (0.35, 0.50, 0.95); img[mo & ~mt] = (0.95, 0.30, 0.30); img[mo & mt] = (0.55, 0.40, 0.65)
    tiles.append(img); inter = (mo & mt).sum(); uni = (mo | mt).sum(); report.setdefault('silhouette_iou', {})[str(az)] = round(float(inter / uni), 3)
sheet = np.concatenate(tiles, axis=1); out = np.dstack([sheet, np.ones(sheet.shape[:2], dtype=np.float32)])[::-1]
im = bpy.data.images.new('ov', sheet.shape[1], N, alpha=True); im.pixels = out.reshape(-1).tolist(); im.filepath_raw = os.path.join(OUT, 'overlay-ours-vs-target.png'); im.file_format = 'PNG'; im.save()
json.dump(report, open(os.path.join(OUT, 'align-report.json'), 'w'), indent=1)
print('REPORT', json.dumps({k: report[k] for k in ('translation_applied', 'target_to_ours_all', 'silhouette_iou')}))
