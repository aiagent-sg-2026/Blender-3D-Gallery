"""Retouch the TRELLIS texture of the prepared body: repaint the sign's icon as the reference's right-pointing arrow and lift the hair colour.
Both edits are made in texture space through the mesh's own UVs (each texel is mapped back to its 3D position on a chosen triangle).
Run: blender --background --factory-startup --python retouch_texture.py -- BODY.glb OUT.glb PREVIEW_DIR
BODY.glb: output of prepare_base.py with NOSPLIT=1 (feet on z = 0, character faces -Y, +X = the character's left, the sign on the character's right)."""
import bpy, sys, os, json, math
import numpy as np
from mathutils import Vector
src, dst, PREV = sys.argv[sys.argv.index('--') + 1:][:3]; os.makedirs(PREV, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=src)
body = [o for o in bpy.data.objects if o.type == 'MESH'][0]; me = body.data
mat = me.materials[0]; img = [n.image for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE'][0]; W, H = img.size
tex = np.array(img.pixels[:], dtype=np.float32).reshape(H, W, 4); orig = tex.copy()
uvl = me.uv_layers.active.data; polys = me.polygons; verts = np.array([v.co[:] for v in me.vertices])
def tri_data(p):
    ls = list(p.loop_indices)[:3]; return np.array([verts[me.loops[l].vertex_index] for l in ls]), np.array([uvl[l].uv[:] for l in ls])
def fcol(p):
    _, uv = tri_data(p); u, v = uv.mean(axis=0); return orig[int(np.clip(v, 0, 1) * (H - 1)), int(np.clip(u, 0, 1) * (W - 1)), :3]
cent = np.array([p.center[:] for p in polys]); cols = np.array([fcol(p) for p in polys])
def raster(tri_idx, fn):
    """Call fn(ix, iy, P3d) for every texel centre inside the UV triangle of face tri_idx; P3d is the matching point on the 3D triangle."""
    P, UV = tri_data(polys[tri_idx]); px = UV * np.array([W, H]); x0, y0 = np.floor(px.min(axis=0)).astype(int); x1, y1 = np.ceil(px.max(axis=0)).astype(int)
    a, b, c = px; den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
    if abs(den) < 1e-9: return
    for iy in range(max(y0, 0), min(y1 + 1, H)):
        for ix in range(max(x0, 0), min(x1 + 1, W)):
            x, y = ix + 0.5, iy + 0.5; l1 = ((b[1] - c[1]) * (x - c[0]) + (c[0] - b[0]) * (y - c[1])) / den; l2 = ((c[1] - a[1]) * (x - c[0]) + (a[0] - c[0]) * (y - c[1])) / den; l3 = 1 - l1 - l2
            if l1 >= -0.01 and l2 >= -0.01 and l3 >= -0.01: fn(ix, iy, l1 * P[0] + l2 * P[1] + l3 * P[2])
rep = {}
# ---- 1. the sign ----
gold = (cols[:, 0] > 0.5) & (cols[:, 1] > 0.4) & (cols[:, 2] < 0.35) & (cent[:, 0] < -0.09) & (cent[:, 2] > 0.18) & (cent[:, 2] < 0.70)
zlo, zhi = cent[gold, 2].min(), cent[gold, 2].max(); rim = gold & (cent[:, 2] > zlo + 0.30 * (zhi - zlo))
c0 = np.median(cent[rim], axis=0); R = float(np.percentile(np.linalg.norm(cent[rim] - c0, axis=1), 85))
_, _, vt = np.linalg.svd(cent[rim] - c0); n = vt[2] / np.linalg.norm(vt[2])
e1 = np.array([1.0, 0, 0]) - n * n[0]; e1 /= np.linalg.norm(e1); e2 = np.cross(n, e1)
if e2[2] < 0: e2 = -e2
depth = np.abs((cent - c0) @ n); dist = np.linalg.norm(cent - c0, axis=1)
is_ivory_green = (cols[:, 1] > 0.72) | ((cols[:, 1] > cols[:, 0] + 0.05) & (cols[:, 1] > cols[:, 2] + 0.05))
skin_like = (cols[:, 0] > 0.65) & (cols[:, 1] > 0.38) & (cols[:, 1] < 0.72) & (cols[:, 2] < 0.65) & (cols[:, 0] > cols[:, 1] + 0.08)
board = np.where((dist < R * 1.06) & (depth < 0.045) & (cent[:, 0] < -0.09) & ~skin_like)[0]
inner = board[is_ivory_green[board] & ~gold[board]]
if len(inner) > 20: c0 = cent[inner].mean(axis=0)     # centre of the board face itself (the rim median is biased by the handle side)
rep['sign'] = dict(centre=c0.round(3).tolist(), radius=round(R, 3), normal=n.round(3).tolist(), board_faces=int(len(board)))
IVORY = np.array([0.96, 0.92, 0.82]); GREEN = np.array([0.20, 0.42, 0.31]); painted = [0]
def arrow(a, b):   # a along e1 (toward the character's left = viewer's right), b up; in units of the board radius
    shaft = (-0.52 <= a <= 0.08) and abs(b) <= 0.13
    head = (0.08 <= a <= 0.56) and abs(b) <= 0.40 * (0.56 - a) / 0.48
    return shaft or head
def paint_sign(ix, iy, p):
    q = p - c0; a, b = (q @ e1) / R * SIDE[0], (q @ e2) / R; old = orig[iy, ix, :3]
    if np.linalg.norm(old - IVORY) > 0.0 and (old[0] > 0.5 and old[1] > 0.4 and old[2] < 0.35): return    # keep the brass rim
    tex[iy, ix, :3] = GREEN if arrow(a, b) else IVORY; painted[0] += 1
SIDE = [1.0]
for fi in board:
    nf = np.array(polys[int(fi)].normal[:]); SIDE[0] = 1.0 if nf @ np.array([0.0, -1.0, 0.0]) >= 0 else -1.0     # seen from behind, the arrow still points to the viewer's right
    raster(int(fi), paint_sign)
rep['sign']['texels_painted'] = painted[0]
# ---- 2. hair colour ----
face_zone = (cent[:, 1] < -0.10) & (np.abs(cent[:, 0]) < 0.14) & (cent[:, 2] > 0.55) & (cent[:, 2] < 0.73)     # eyes, brows, mouth, cheeks stay untouched
lum = cols @ np.array([0.2126, 0.7152, 0.0722]); darkbrown = (cols[:, 0] >= cols[:, 2]) & (lum < 0.30) & (cols.max(axis=1) < 0.45)
hair = np.where((cent[:, 2] > 0.50) & ~face_zone)[0]      # whole head region; only dark-brown texels are changed below
TARGET = np.array([int('4A', 16), int('2C', 16), int('22', 16)]) / 255.0 * np.array([1.0, 1.0, 1.0])           # the sheet B hair value used for the hand-built figure (sRGB)
cur = cols[hair][darkbrown[hair]].mean(axis=0); gain = np.clip(TARGET / np.maximum(cur, 1e-3), 1.0, 2.2)
rep['hair'] = dict(faces=int(len(hair)), current_mean_srgb=(cur * 255).round().astype(int).tolist(), gain=gain.round(2).tolist())
MEAN_L = float(cur @ np.array([0.2126, 0.7152, 0.0722])); done = set()
def paint_hair(ix, iy, p):
    if (ix, iy) in done: return
    done.add((ix, iy)); old = orig[iy, ix, :3]
    l = float(old @ np.array([0.2126, 0.7152, 0.0722]))
    if old.max() < 0.40 and l < 0.30: tex[iy, ix, :3] = np.clip(TARGET * min(max(l / MEAN_L, 0.35), 1.7), 0, 1)   # keep the texel's shading, take the sheet's brown hue
for fi in hair:
    if cols[fi][1] > cols[fi][0] + 0.03: continue      # greenish face = the cap
    raster(int(fi), paint_hair)
rep['hair']['texels_changed'] = len(done)
img.pixels = tex.reshape(-1).tolist(); img.update(); img.pack()
bpy.ops.object.select_all(action='SELECT'); bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_yup=True, use_selection=True)
json.dump(rep, open(os.path.join(PREV, 'retouch-report.json'), 'w'), indent=1)
# preview of the texture
im2 = bpy.data.images.new('t', W, H, alpha=True); im2.pixels = tex.reshape(-1).tolist(); im2.filepath_raw = os.path.join(PREV, 'texture-retouched.png'); im2.file_format = 'PNG'; im2.save()
print('RETOUCH', json.dumps(rep))
