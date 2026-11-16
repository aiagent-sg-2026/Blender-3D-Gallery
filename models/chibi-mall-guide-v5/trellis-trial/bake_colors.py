"""Bake the TRELLIS seed-1 texture colours onto the built figure as vertex colours.
For every vertex of the figure: nearest point on the aligned target surface, UV of that point, texture colour (bilinear) -> linear vertex colour.
Faces keep their flat material (not baked) for the designed details: eyes, brows, mouth, cheeks, brass buttons/badge/pin.
Run (repo root): blender --background --factory-startup --python-exit-code 1 --python models/chibi-mall-guide-v5/trellis-trial/bake_colors.py -- TARGET.glb OUT_DIR
Outputs: OUT_DIR/colors-seed1.npz (vertex colours per part, in vertex order), colour-report.json, baked-sheet.png (4 views)."""
import bpy, bmesh, sys, os, json, math
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import config as C, figure
glb, OUT = sys.argv[sys.argv.index('--') + 1:][:2]; os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
mats, parts, placeholders = figure.build_all(bpy, bmesh)
before = set(bpy.data.objects.keys()); bpy.ops.import_scene.gltf(filepath=glb)
new = [bpy.data.objects[n] for n in bpy.data.objects.keys() if n not in before]; tgt = [o for o in new if o.type == 'MESH'][0]; tgt.name = 'TARGET'
bpy.ops.object.select_all(action='DESELECT'); tgt.select_set(True); bpy.context.view_layer.objects.active = tgt
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
for o in new:
    if o is not tgt and o.type != 'MESH': bpy.data.objects.remove(o)
bpy.context.view_layer.update()
def world_bvh(o):
    """BVH of o in WORLD space (BVHTree.FromObject is object space, which ignores the translation applied to the target)."""
    me = o.data; V = [tuple(o.matrix_world @ v.co) for v in me.vertices]; T = [tuple(p.vertices) for p in me.polygons]; return BVHTree.FromPolygons(V, T)
def wpts(objs): return np.vstack([np.array([(o.matrix_world @ v.co)[:] for v in o.data.vertices]) for o in objs])
tp = wpts([tgt]); tgt.location = Vector((-(tp[:, 0].min() + tp[:, 0].max()) / 2, 0.0, -tp[:, 2].min())); bpy.context.view_layer.update()
shoes = [o for o in parts if o.name.startswith('Shoe')]; SP = wpts(shoes)
for it in range(14):
    bvh = world_bvh(tgt); ds = []
    for p in SP:
        loc, n, i, d = bvh.find_nearest(Vector(p))
        if loc is not None and d < 0.06: ds.append(np.array(loc[:]) - p)
    dd = np.mean(ds, axis=0); dd[2] = 0; tgt.location = tgt.location - Vector(dd); bpy.context.view_layer.update()
bvh = world_bvh(tgt)
# texture
mat = tgt.data.materials[0]; img = [n.image for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE'][0]
W, H = img.size; tex = np.array(img.pixels[:], dtype=np.float32).reshape(H, W, 4)[:, :, :3]
def srgb_to_lin(c): return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
uvl = tgt.data.uv_layers.active.data; mw = tgt.matrix_world
def sample(co):
    loc, nrm, idx, dist = bvh.find_nearest(Vector(co))
    poly = tgt.data.polygons[idx]; ls = list(poly.loop_indices)[:3]
    P = [mw @ tgt.data.vertices[tgt.data.loops[l].vertex_index].co for l in ls]; uv = [uvl[l].uv for l in ls]
    v0, v1 = P[1] - P[0], P[2] - P[0]; vp = loc - P[0]
    d00, d01, d11, d20, d21 = v0.dot(v0), v0.dot(v1), v1.dot(v1), vp.dot(v0), vp.dot(v1); den = d00 * d11 - d01 * d01
    if abs(den) < 1e-20: b1 = b2 = 0.0
    else: b1 = (d11 * d20 - d01 * d21) / den; b2 = (d00 * d21 - d01 * d20) / den
    b0 = 1 - b1 - b2; u = b0 * uv[0][0] + b1 * uv[1][0] + b2 * uv[2][0]; v = b0 * uv[0][1] + b1 * uv[1][1] + b2 * uv[2][1]
    x = (u % 1.0) * (W - 1); y = (v % 1.0) * (H - 1); x0, y0 = int(x), int(y); x1, y1 = min(x0 + 1, W - 1), min(y0 + 1, H - 1); fx, fy = x - x0, y - y0
    c = (tex[y0, x0] * (1 - fx) + tex[y0, x1] * fx) * (1 - fy) + (tex[y1, x0] * (1 - fx) + tex[y1, x1] * fx) * fy
    return c, dist
# slots kept flat (designed details)
KEEP = {('Head', 1), ('Head', 2), ('Head', 3), ('Vest', 1), ('Cap', 2)}
ALLOWED = {'Cap': ['cap_jade', 'ivory'], 'Vest': ['jade'], 'Shirt': ['ivory'], 'Neckerchief': ['ivory'], 'Shorts': ['charcoal'], 'Arm': ['skin'], 'Glove': ['white'],
           'Leg': ['skin'], 'Sock': ['ivory'], 'Shoe': ['jade', 'sole', 'ivory'], 'Head': ['skin'], 'Hair': ['hair']}
def pal_lin(name):
    h = C.PALETTE[name]; return srgb_to_lin(np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]))
def lin_to_lab(c):
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]); xyz = M @ c / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116); return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])
DE_MAX = 28.0; RADIUS = 0.06; MATCH_PALETTE = os.environ.get('MATCH_PALETTE', '1') == '1'
baked_mat = bpy.data.materials.new('BakedColor'); baked_mat.use_nodes = True
nt = baked_mat.node_tree; bsdf = nt.nodes['Principled BSDF']; attr = nt.nodes.new('ShaderNodeAttribute'); attr.attribute_name = 'target_color'
nt.links.new(attr.outputs['Color'], bsdf.inputs['Base Color']); bsdf.inputs['Roughness'].default_value = 0.45
store = {}; stats = {}
for o in parts:
    if o.name == 'Eyes': continue
    key = o.name.split('.')[0]; allowed = ALLOWED[key]; pal = [(n, pal_lin(n), lin_to_lab(pal_lin(n))) for n in allowed]
    me = o.data; nv = len(me.vertices); cols = np.zeros((nv, 3)); ok = np.zeros(nv, dtype=bool); n_far = n_rej = 0
    for i, v in enumerate(me.vertices):
        c, d = sample(o.matrix_world @ v.co); cl = srgb_to_lin(c)
        if d > RADIUS: n_far += 1; continue
        lab = lin_to_lab(cl)
        if min(np.linalg.norm(lab - p[2]) for p in pal) > DE_MAX: n_rej += 1; continue
        cols[i] = cl; ok[i] = True
    nb = [[] for _ in range(nv)]
    for e in me.edges: a_, b_ = e.vertices; nb[a_].append(b_); nb[b_].append(a_)
    base = np.median(cols[ok], axis=0) if ok.sum() > 5 else pal[0][1]
    for i in range(nv):
        if not ok[i]: cols[i] = base
    if MATCH_PALETTE and len(pal) == 1 and ok.sum() > 5:     # keep the target's shading, move its overall colour to the sheet B palette value
        ratio = pal[0][1] / np.maximum(base, 1e-4); cols = np.clip(cols * ratio, 0, 1)
    for it in range(3):      # light smoothing removes single-vertex speckle but keeps the large shading
        cols = np.array([(cols[i] + sum(cols[j] for j in nb[i])) / (1 + len(nb[i])) if nb[i] else cols[i] for i in range(nv)])
    store[o.name] = cols.astype(np.float32)
    ca = me.color_attributes.new('target_color', 'FLOAT_COLOR', 'POINT')
    for i in range(nv): ca.data[i].color = (*cols[i], 1.0)
    me.materials.append(baked_mat); bi = len(me.materials) - 1; n_baked = 0
    for p in me.polygons:
        if (o.name, p.material_index) not in KEEP: p.material_index = bi; n_baked += 1
    mean_lin = cols.mean(axis=0); lin2s = np.where(mean_lin <= 0.0031308, mean_lin * 12.92, 1.055 * mean_lin ** (1 / 2.4) - 0.055)
    stats[o.name] = dict(verts=nv, accepted=int(ok.sum()), too_far=n_far, rejected_colour=n_rej, baked_faces=n_baked, mean_srgb_hex='%02X%02X%02X' % tuple(int(round(x * 255)) for x in lin2s))
np.savez_compressed(os.path.join(OUT, 'colors-seed1.npz'), **store)
json.dump(dict(texture=[W, H], radius_m=RADIUS, max_deltaE=DE_MAX, parts=stats), open(os.path.join(OUT, 'colour-report.json'), 'w'), indent=1)
# render 4 views, flat vertex colours (no lighting), material colours for kept details
tgt.hide_render = True
N = 700; sc = bpy.context.scene; sc.render.engine = 'BLENDER_WORKBENCH'; sc.render.resolution_x = N; sc.render.resolution_y = N
sc.display.shading.light = 'STUDIO'; sc.display.shading.color_type = 'MATERIAL'; sc.view_settings.view_transform = 'Standard'
sc.world = bpy.data.worlds.new('w'); sc.world.color = (0.92, 0.91, 0.97)
for m in bpy.data.materials: m.diffuse_color = (*[0.5] * 3, 1) if m.name == 'BakedColor' else m.diffuse_color
sc.display.shading.color_type = 'VERTEX'
cd = bpy.data.cameras.new('cam'); cd.type = 'ORTHO'; cd.ortho_scale = 1.12; cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam
tiles = []
for az in (0, 35, 90, 180):
    a = math.radians(az); cam.location = (math.sin(a) * 4, -math.cos(a) * 4, 0.52); cam.rotation_euler = (math.radians(90), 0, a)
    sc.render.filepath = os.path.join(OUT, 'tmp.png'); bpy.ops.render.render(write_still=True)
    tiles.append(np.array(bpy.data.images.load(sc.render.filepath).pixels[:], dtype=np.float32).reshape(N, N, 4))
sheet = np.concatenate(tiles, axis=1); im = bpy.data.images.new('s', sheet.shape[1], N, alpha=True); im.pixels = sheet.reshape(-1).tolist()
im.filepath_raw = os.path.join(OUT, 'baked-sheet.png'); im.file_format = 'PNG'; im.save()
print('BAKED', json.dumps({k: v['mean_srgb_hex'] for k, v in stats.items()}))
