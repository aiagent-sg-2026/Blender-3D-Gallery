"""Fit the built figure to the aligned TRELLIS target by coordinate descent on a few config values.
Objective J (mm) = mean distance target->ours + mean distance ours->target (target samples near the held sign are ignored).
Run (repo root): blender --background --factory-startup --python-exit-code 1 --python models/chibi-mall-guide-v5/trellis-trial/fit_to_target.py -- TARGET.glb OUT_DIR [ROUNDS]
Writes OUT_DIR/fit.json (overrides for config.py), fit-log.txt and fit-history.json. The target is first aligned exactly as in align_compare.py (translation only, shoes fitted)."""
import bpy, bmesh, sys, os, json, time, copy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import config as C, figure
args = sys.argv[sys.argv.index('--') + 1:]; glb, OUT = args[0], args[1]; ROUNDS = int(args[2]) if len(args) > 2 else 3
os.makedirs(OUT, exist_ok=True); LOG = open(os.path.join(OUT, 'fit-log.txt'), 'w')
def log(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); LOG.write(s + '\n'); LOG.flush()
bpy.ops.wm.read_factory_settings(use_empty=True)
def clear_figure():
    for o in list(bpy.data.objects):
        if o.name != 'TARGET': bpy.data.objects.remove(o)
    for m in list(bpy.data.meshes):
        if m.users == 0: bpy.data.meshes.remove(m)
    for m in list(bpy.data.materials): bpy.data.materials.remove(m)
# --- target ---
before = set(bpy.data.objects.keys()); bpy.ops.import_scene.gltf(filepath=glb)
new = [bpy.data.objects[n] for n in bpy.data.objects.keys() if n not in before]; tgt = [o for o in new if o.type == 'MESH'][0]; tgt.name = 'TARGET'
bpy.ops.object.select_all(action='DESELECT'); tgt.select_set(True); bpy.context.view_layer.objects.active = tgt
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
for o in new:
    if o is not tgt and o.type != 'MESH': bpy.data.objects.remove(o)
bpy.context.view_layer.update()
tp = np.array([(tgt.matrix_world @ v.co)[:] for v in tgt.data.vertices])
tgt.location = Vector((-(tp[:, 0].min() + tp[:, 0].max()) / 2, 0.0, -tp[:, 2].min())); bpy.context.view_layer.update()
def world_arrays(objs):
    V, T, off = [], [], 0
    for o in objs:
        me = o.data; me.calc_loop_triangles(); w = o.matrix_world
        V.append(np.array([(w @ v.co)[:] for v in me.vertices])); T.append(np.array([t.vertices[:] for t in me.loop_triangles]) + off); off += len(me.vertices)
    return np.vstack(V), np.vstack(T)
def bvh_from(V, T): return BVHTree.FromPolygons([tuple(v) for v in V], [tuple(t) for t in T])
# shoe alignment (x, y), once
clear_figure(); mats, parts, placeholders = figure.build_all(bpy, bmesh)
shoes = [o for o in parts if o.name.startswith('Shoe')]; SP, _ = world_arrays(shoes); tb = bvh_from(*world_arrays([tgt]))
for it in range(14):
    tb = bvh_from(*world_arrays([tgt])); ds = []
    for p in SP:
        loc, n, i, d = tb.find_nearest(Vector(p))
        if loc is not None and d < 0.06: ds.append(np.array(loc[:]) - p)
    dd = np.mean(ds, axis=0); dd[2] = 0; tgt.location = tgt.location - Vector(dd); bpy.context.view_layer.update()
TV, TT = world_arrays([tgt]); tb = bvh_from(TV, TT)
rng = np.random.default_rng(0); A = 0.5 * np.linalg.norm(np.cross(TV[TT[:, 1]] - TV[TT[:, 0]], TV[TT[:, 2]] - TV[TT[:, 0]]), axis=1)
pick = rng.choice(len(TT), size=6000, p=A / A.sum()); r1 = rng.random((6000, 1)); r2 = rng.random((6000, 1)); fl = r1 + r2 > 1; r1[fl] = 1 - r1[fl]; r2[fl] = 1 - r2[fl]
S = TV[TT[pick, 0]] + r1 * (TV[TT[pick, 1]] - TV[TT[pick, 0]]) + r2 * (TV[TT[pick, 2]] - TV[TT[pick, 0]])
S = S[~((S[:, 0] < -0.16) & (S[:, 2] > 0.30) & (S[:, 2] < 0.66))]
log('target aligned; samples', len(S))
# --- parameters (path into config, step) and coupled updates ---
BASE_ARM = [tuple(a) for a in C.ARM_PATH]; ARM = {'dx': 0.0}
def getp(path):
    o = C
    for k in path: o = o[k] if isinstance(o, (dict, list, tuple)) else getattr(o, k)
    return o
def setp(path, v):
    if path[0] == 'ARM_DX': ARM['dx'] = v; return
    o = C if len(path) == 1 else getp(path[:-1])
    if len(path) == 1: setattr(C, path[0], v); return
    parent = getp(path[:-1]) if len(path) > 2 else getattr(C, path[0])
    if len(path) == 2: parent[path[1]] = v
    else:
        grand = getp(path[:-2]); key = path[-2]; t = list(grand[key]); t[path[-1]] = v; grand[key] = tuple(t)
def getv(path): return ARM['dx'] if path[0] == 'ARM_DX' else getp(path)
def post():
    vr, vc = C.VEST['r'], C.VEST['c']; C.SHIRT['r'] = (vr[0] - 0.011, vr[1] - 0.013, vr[2] - 0.012); C.SHIRT['c'] = vc
    C.SHORTS['leg_x'] = C.LEG['x']; C.SHOE['x'] = C.LEG['x'] + 0.004
    C.ARM_PATH = [(a[0] + ARM['dx'], a[1], a[2]) for a in BASE_ARM]
PARAMS = [(('CAP', 'c', 2), 0.012), (('CAP', 'c', 1), 0.012), (('CAP', 'r', 0), 0.012), (('CAP', 'r', 1), 0.012), (('CAP', 'r', 2), 0.01), (('CAP', 'shear'), 0.1),
          (('HEAD', 'c', 1), 0.01), (('HEAD', 'r', 0), 0.01), (('HEAD', 'r', 1), 0.01), (('HEAD', 'r', 2), 0.01), (('HEAD', 'rz_bot'), 0.01),
          (('HAIR_T_MULT',), 0.15), (('HAIR_OFF_ADD',), 0.01), (('HAIR_W_MULT',), 0.1),
          (('VEST', 'r', 0), 0.008), (('VEST', 'r', 1), 0.008), (('VEST', 'c', 1), 0.008), (('VEST', 'c', 2), 0.008),
          (('SHORTS', 'r', 0), 0.008), (('SHORTS', 'c', 2), 0.008), (('ARM_DX',), 0.008), (('LEG', 'x'), 0.008)]
def evaluate():
    post(); clear_figure(); mats, parts, placeholders = figure.build_all(bpy, bmesh)
    OV, OT = world_arrays(parts + placeholders); ob = bvh_from(OV, OT)
    d1 = np.array([ob.find_nearest(Vector(p))[3] for p in S]); sub = OV[::3]
    d2 = np.array([tb.find_nearest(Vector(p))[3] for p in sub])
    return float((d1.mean() + d2.mean()) * 1000), float(d1.mean() * 1000), float(d2.mean() * 1000)
t0 = time.time(); best = evaluate(); log('start J=%.2f (t2o %.2f, o2t %.2f) eval %.1fs' % (best + (time.time() - t0,)))
hist = [dict(step='start', J=best[0], t2o=best[1], o2t=best[2])]
for rnd in range(ROUNDS):
    scale = 1.0 / (2 ** rnd); improved = False
    for path, step in PARAMS:
        cur = getv(path); st = step * scale
        for sign in (1, -1):
            setp(path, cur + sign * st); res = evaluate()
            if res[0] < best[0] - 0.02:
                best = res; improved = True; cur = cur + sign * st; log('round %d %s -> %.4f  J=%.2f (t2o %.2f, o2t %.2f)' % ((rnd, '.'.join(map(str, path)), cur) + best)); hist.append(dict(step=list(path), value=cur, J=best[0], t2o=best[1], o2t=best[2])); break
            setp(path, cur)
    log('round %d done J=%.2f elapsed %.0fs' % (rnd, best[0], time.time() - t0))
    if not improved and rnd > 0: break
post()
fit = {'CAP': {k: list(v) if isinstance(v, tuple) else v for k, v in C.CAP.items()}, 'HEAD': {k: list(v) if isinstance(v, tuple) else v for k, v in C.HEAD.items()},
       'VEST': {k: list(v) if isinstance(v, tuple) else v for k, v in C.VEST.items()}, 'SHORTS': {k: list(v) if isinstance(v, tuple) else v for k, v in C.SHORTS.items()},
       'SHIRT': {k: list(v) if isinstance(v, tuple) else v for k, v in C.SHIRT.items()}, 'LEG': dict(C.LEG), 'SHOE': dict(C.SHOE),
       'ARM_PATH': [list(a) for a in C.ARM_PATH], 'HAIR_T_MULT': C.HAIR_T_MULT, 'HAIR_W_MULT': C.HAIR_W_MULT, 'HAIR_OFF_ADD': C.HAIR_OFF_ADD}
json.dump(fit, open(os.path.join(OUT, 'fit.json'), 'w'), indent=1); json.dump(hist, open(os.path.join(OUT, 'fit-history.json'), 'w'), indent=1)
log('FINAL J=%.2f (t2o %.2f, o2t %.2f)' % best)
