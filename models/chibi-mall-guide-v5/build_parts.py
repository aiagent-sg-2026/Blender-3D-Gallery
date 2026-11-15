"""Step 5: build the named body and garment parts (head and hair are still blockout placeholders), report triangles,
primitives and part-to-part overlaps, and render four views.
Run (repository root):
  blender --background --factory-startup --python-exit-code 1 --python models/chibi-mall-guide-v5/build_parts.py -- OUT_DIR
"""
import bpy, bmesh, sys, os, json, math, itertools
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import config as C, kit, garments, limbs
OUT = sys.argv[sys.argv.index('--') + 1]; os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
mats = garments.make_materials(bpy)

parts = []
parts.append(garments.build_cap(bmesh, mats)); parts.append(garments.build_vest(bmesh, mats))
parts.append(garments.build_shirt(bmesh, mats)); parts.append(garments.build_neckerchief(bmesh, mats))
parts.append(garments.build_shorts(bmesh, mats))
for fn in (limbs.build_arms, limbs.build_gloves, limbs.build_legs, limbs.build_socks, limbs.build_shoes):
    parts.extend(fn(bmesh, mats))
# placeholders (not part of this step's budget): head from the blockout, plus the neck
placeholders = []
for name in ('Head', 'Neck'):
    p = C.PARTS[name]; bm = bmesh.new()
    kit.add_super(bm, p['c'], p['r'], p_bot=p.get('p_bot', 2.0), rz_bot=p.get('rz_bot'), seg=36, rings=24)
    placeholders.append(kit.finish(name + '_placeholder', bm, [mats['skin']]))

# ---- report ----
dg = bpy.context.evaluated_depsgraph_get()
tris = {o.name: kit.tri_count(o) for o in parts}
prims = {o.name: len({p.material_index for p in o.data.polygons}) for o in parts}
mats_used = sorted({o.data.materials[p.material_index].name for o in parts for p in o.data.polygons})
def bvh(o):
    me = o.data; vs = [v.co.copy() for v in me.vertices]; tr = []
    for p in me.polygons:
        pv = list(p.vertices)
        for j in range(1, len(pv) - 1): tr.append((pv[0], pv[j], pv[j + 1]))
    return BVHTree.FromPolygons(vs, tr), vs, tr
trees = {o.name: bvh(o) for o in parts + placeholders}
names = [o.name for o in parts + placeholders]
overlaps = {}
for a, b in itertools.combinations(names, 2):
    pairs = trees[a][0].overlap(trees[b][0])
    if pairs:
        cs = [sum((trees[a][1][i] for i in trees[a][2][pa]), Vector()) / 3 for pa, _ in pairs]
        overlaps[f'{a} x {b}'] = dict(n=len(pairs), x=[round(min(c.x for c in cs), 3), round(max(c.x for c in cs), 3)],
                                      y=[round(min(c.y for c in cs), 3), round(max(c.y for c in cs), 3)], z=[round(min(c.z for c in cs), 3), round(max(c.z for c in cs), 3)])
report = dict(parts=len(parts), triangles_total=sum(tris.values()), triangles=tris,
              primitives_named_parts=sum(prims.values()), materials_used=mats_used, materials=len(mats_used),
              primitives_if_merged_by_material=len(mats_used), overlaps=overlaps)
dims = Vector((0, 0, 0)); zs = [v.co.z for o in parts for v in o.data.vertices]
report['height_m_parts_only'] = (max(zs) - min(zs))

# ---- render: Workbench material colours, four orthographic views ----
N = 700; sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'; sc.render.resolution_x = N; sc.render.resolution_y = N
sc.display.shading.light = 'STUDIO'; sc.display.shading.color_type = 'MATERIAL'; sc.display.shading.show_cavity = True
sc.render.film_transparent = False
sc.world = bpy.data.worlds.new('w'); sc.world.color = (0.92, 0.91, 0.97)
sc.view_settings.view_transform = 'Standard'
cd = bpy.data.cameras.new('cam'); cd.type = 'ORTHO'; cd.ortho_scale = 1.12
cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam
views = {'front': 0, 'three-quarter': 35, 'side': 90, 'back': 180}
imgs = []
for name, az in views.items():
    a = math.radians(az)
    cam.location = (math.sin(a) * 4 * -1 * -1 if False else math.sin(a) * 4, -math.cos(a) * 4, 0.52)
    cam.rotation_euler = (math.radians(90), 0, a)
    sc.render.filepath = os.path.join(OUT, f'parts-{name}.png'); bpy.ops.render.render(write_still=True)
    imgs.append(np.array(bpy.data.images.load(sc.render.filepath).pixels[:], dtype=np.float32).reshape(N, N, 4))
sheet = np.concatenate(imgs, axis=1)
im = bpy.data.images.new('sheet', sheet.shape[1], N, alpha=True); im.pixels = sheet.reshape(-1).tolist()
im.filepath_raw = os.path.join(OUT, 'parts-sheet.png'); im.file_format = 'PNG'; im.save()
json.dump(report, open(os.path.join(OUT, 'parts-report.json'), 'w'), indent=1)
print(json.dumps({k: report[k] for k in ('parts', 'triangles_total', 'primitives_named_parts', 'materials')})); print('OVERLAPS', json.dumps(report['overlaps']))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'parts.blend'))
