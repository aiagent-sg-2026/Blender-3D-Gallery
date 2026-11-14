"""GJH Visitor v3: MPFB2 human base, body-offset clothing, procedural hair and accessories.

Run headless with Blender 5.1+ and the MPFB extension (v2.0.18) installed:
  blender --background --python models/gjh-visitor-v3/generate.py [-- --quick]
--quick skips animations and preview renders (geometry iteration only).
"""
from pathlib import Path
import math
import random
import sys
import bpy
import bmesh
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
QUICK = '--quick' in sys.argv
HEIGHT = 1.78

from materials import make_materials, mat  # noqa: E402

bpy.ops.wm.read_factory_settings(use_empty=True)
from bl_ext.user_default.mpfb.services.humanservice import HumanService  # noqa: E402

scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
M = make_materials()

# ---------------------------------------------------------------- base human
MACRO = {'gender': 1.0, 'age': 0.5, 'muscle': 0.55, 'weight': 0.48, 'proportions': 0.65,
         'height': 0.62, 'cupsize': 0.5, 'firmness': 0.5,
         'race': {'asian': 1.0, 'caucasian': 0.0, 'african': 0.0}}
body = HumanService.create_human(macro_detail_dict=MACRO)
rig = HumanService.add_builtin_rig(body, 'game_engine')
rig.name = 'GJHVisitorV3'
rig.data.name = 'GJHVisitorV3Humanoid'
body.name = 'Body skin'
bpy.ops.object.select_all(action='DESELECT')
bpy.context.view_layer.objects.active = body
body.select_set(True)
bpy.ops.object.shape_key_remove(all=True, apply_mix=True)
for mod in list(body.modifiers):
    if mod.type == 'MASK':
        body.modifiers.remove(mod)

BONES = {b.name for b in rig.data.bones}
TORSO = {'pelvis', 'spine_01', 'spine_02', 'spine_03', 'clavicle_l', 'clavicle_r'}
UPPER = {'upperarm_l', 'upperarm_r'}
LOWER = {'lowerarm_l', 'lowerarm_r'}
LEGS = {'thigh_l', 'thigh_r', 'calf_l', 'calf_r'}
FEET = {'foot_l', 'foot_r', 'ball_l', 'ball_r'}


def group_index(obj):
    return {g.index: g.name for g in obj.vertex_groups}


def dominant(obj):
    """Dominant deform bone per vertex, plus membership of non-bone groups."""
    names = group_index(obj)
    dom, member = [], []
    for v in obj.data.vertices:
        best, weight, groups = None, 0.0, set()
        for g in v.groups:
            name = names[g.group]
            groups.add(name)
            if name in BONES and g.weight > weight:
                best, weight = name, g.weight
        dom.append(best)
        member.append(groups)
    return dom, member


def bone_head(name):
    return rig.matrix_world @ rig.data.bones[name].head_local


def bone_tail(name):
    return rig.matrix_world @ rig.data.bones[name].tail_local


def along(name, co):
    """0..1 position of a point along a bone."""
    h, t = bone_head(name), bone_tail(name)
    d = t - h
    return max(0.0, min(1.0, (co - h).dot(d) / d.length_squared))


dom, member = dominant(body)
coords = [v.co.copy() for v in body.data.vertices]
WAIST = bone_head('thigh_l').z + .07
ANKLE = bone_head('foot_l').z
NECK = bone_head('neck_01').z

# Keep the eyes; drop the remaining helper geometry (tights, skirt, teeth, lashes, joint cubes).
eye_l = {i for i, m in enumerate(member) if 'helper-l-eye' in m}
eye_r = {i for i, m in enumerate(member) if 'helper-r-eye' in m}
hair_helper = {i for i, m in enumerate(member) if 'helper-hair' in m}
real = {i for i, m in enumerate(member) if 'body' in m}
lips = {i for i, m in enumerate(member) if 'lips' in m}

# Regions (vertex sets on the real body surface).
def region(pred):
    return {i for i in real if dom[i] and pred(i, dom[i], coords[i])}

tee_region = region(lambda i, b, c: (b in TORSO and c.z >= WAIST - .02 and c.z < NECK + .01)
                    or (b in UPPER and along(b, c) < .42))
hoodie_region = region(lambda i, b, c: (b in TORSO and c.z >= WAIST - .07 and c.z < NECK + .02)
                       or b in UPPER or (b in LOWER and along(b, c) < .9))
pants_region = region(lambda i, b, c: (b in LEGS and c.z > ANKLE + .025)
                      or (b in TORSO and c.z < WAIST + .03))
shoe_region = region(lambda i, b, c: b in FEET or (b in ('calf_l', 'calf_r') and c.z < ANKLE + .045))


def neighbours(mesh):
    adj = [set() for _ in mesh.vertices]
    for e in mesh.edges:
        a, b = e.vertices
        adj[a].add(b)
        adj[b].add(a)
    return adj


ADJ = neighbours(body.data)


def erode(verts, rings=1):
    out = set(verts)
    for _ in range(rings):
        out = {i for i in out if ADJ[i] <= out}
    return out


def inflate(bm, obj, rules):
    """Push limb vertices out to a minimum radius around their bone axis (loose cloth)."""
    names = group_index(obj)
    layer = bm.verts.layers.deform.active
    for v in bm.verts:
        weights = {names[k]: w for k, w in v[layer].items() if names[k] in BONES}
        if not weights:
            continue
        bone = max(weights, key=weights.get)
        if bone not in rules:
            continue
        h, t = bone_head(bone), bone_tail(bone)
        axis = (t - h).normalized()
        k = max(0.0, min(1.0, (v.co - h).dot(axis) / (t - h).length))
        foot = h + axis * (v.co - h).dot(axis)
        radial = v.co - foot
        r0, r1 = rules[bone]
        rmin = r0 + (r1 - r0) * k
        if radial.length < rmin and radial.length > 1e-6:
            v.co = foot + radial.normalized() * rmin


def smooth_boundary(bm, iterations=16):
    for _ in range(iterations):
        moves = {}
        for v in bm.verts:
            if not v.is_boundary:
                continue
            ring = [e.other_vert(v) for e in v.link_edges if e.is_boundary]
            if len(ring) == 2:
                moves[v] = v.co.lerp((ring[0].co + ring[1].co) / 2, .5)
        for v, co in moves.items():
            v.co = co


def shell(name, verts, offset, material, smooth=6, factor=.5, rules=None):
    """Duplicate the body faces fully inside `verts`, push along normals and soften anatomy."""
    obj = body.copy()
    obj.data = body.data.copy()
    obj.name = name
    obj.data.name = name
    scene.collection.objects.link(obj)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    keep = set(verts)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if not all(v.index in keep for v in f.verts)], context='FACES')
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    bm.normal_update()
    for v in bm.verts:
        v.co += v.normal * offset
    smooth_boundary(bm)
    if rules:
        inflate(bm, obj, rules)
    for _ in range(smooth):
        inner = [v for v in bm.verts if not v.is_boundary]
        new = {v: sum((e.other_vert(v).co for e in v.link_edges), Vector()) / len(v.link_edges) for v in inner}
        for v, co in new.items():
            v.co = v.co.lerp(co, factor)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.materials.clear()
    obj.data.materials.append(material)
    for p in obj.data.polygons:
        p.material_index = 0
        p.use_smooth = True
    return obj


# Open-front zip hoodie: remove a vertical front strip of the torso.
def front_open(i):
    c = coords[i]
    return dom[i] in TORSO and c.y < -.02 and abs(c.x) < .036

hoodie = shell('Hoodie body', {i for i in hoodie_region if not front_open(i)}, .018, M['hoodie'], smooth=8,
               rules={'upperarm_l': (.056, .05), 'upperarm_r': (.056, .05), 'lowerarm_l': (.05, .045), 'lowerarm_r': (.05, .045)})
# Snap the open-front boundary to straight zipper lines.
_bm = bmesh.new()
_bm.from_mesh(hoodie.data)
for v in _bm.verts:
    if v.is_boundary and v.co.y < -.03 and abs(v.co.x) < .1 and WAIST - .1 < v.co.z < NECK - .03:
        v.co.x = math.copysign(.036, v.co.x)
_bm.to_mesh(hoodie.data)
_bm.free()
tee = shell('Tee shirt', tee_region, .007, M['tee'], smooth=6,
            rules={'upperarm_l': (.05, .048), 'upperarm_r': (.05, .048)})
pants = shell('Chino trousers', pants_region, .012, M['chino'], smooth=8,
              rules={'thigh_l': (.088, .07), 'thigh_r': (.088, .07), 'calf_l': (.068, .062), 'calf_r': (.068, .062)})
shoes = shell('Sneaker upper', shoe_region, .014, M['shoe'], smooth=10, factor=.6,
              rules={'foot_l': (.048, .046), 'foot_r': (.048, .046), 'ball_l': (.036, .03), 'ball_r': (.036, .03)})

# ---------------------------------------------------------------- hair surface (before the body is trimmed)
def centroid(ids):
    return sum((coords[i] for i in ids), Vector()) / len(ids)


head_c = bone_head('head')
eye_z = centroid(eye_l).z
ears = {i for i, m in enumerate(member) if 'ears' in m}


def hairline(c):
    rel = c - head_c
    if rel.y < -.055:
        return eye_z + .07      # forehead
    if rel.y < .015:
        return eye_z + .028     # temples and above the ears
    return eye_z - .075         # back of the head down to the nape


scalp = {i for i in real if dom[i] in ('head', 'neck_01') and i not in ears and coords[i].z > hairline(coords[i])}
cap = shell('Hair cap', scalp, .011, M['hair'], smooth=6)
crop = shell('Alternate hair crop', scalp, .004, M['hair'], smooth=4)

# ---------------------------------------------------------------- body surface
bm = bmesh.new()
bm.from_mesh(body.data)
bm.verts.ensure_lookup_table()
hidden = erode(tee_region | pants_region | shoe_region, 1)
keep_helpers = eye_l | eye_r
kill = [f for f in bm.faces if all(v.index in hidden for v in f.verts)
        or all(v.index not in real and v.index not in keep_helpers for v in f.verts)]
bmesh.ops.delete(bm, geom=kill, context='FACES')
bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
bm.to_mesh(body.data)
bm.free()


def assign_material_by_group(obj, group_name, material):
    idx = obj.vertex_groups[group_name].index
    if material.name not in obj.data.materials:
        obj.data.materials.append(material)
    slot = list(obj.data.materials).index(material)
    inside = {v.index for v in obj.data.vertices if any(g.group == idx and g.weight > .5 for g in v.groups)}
    for p in obj.data.polygons:
        if all(v in inside for v in p.vertices):
            p.material_index = slot


body.data.materials.clear()
body.data.materials.append(M['skin'])
assign_material_by_group(body, 'lips', M['lips'])
assign_material_by_group(body, 'helper-l-eye', M['eye_white'])
assign_material_by_group(body, 'helper-r-eye', M['eye_white'])
for p in body.data.polygons:
    p.use_smooth = True

# ---------------------------------------------------------------- helpers for added parts
def finish(obj, bone=None, weights=None, material=None):
    """Parent to the rig and skin either rigidly to one bone or with explicit weights."""
    obj.parent = rig
    if material is not None:
        obj.data.materials.clear()
        obj.data.materials.append(material)
    for p in obj.data.polygons:
        p.use_smooth = True
    if bone or weights:
        for g in list(obj.vertex_groups):
            obj.vertex_groups.remove(g)
    if bone:
        g = obj.vertex_groups.new(name=bone)
        g.add(list(range(len(obj.data.vertices))), 1.0, 'REPLACE')
    if weights:
        for name, items in weights.items():
            g = obj.vertex_groups.get(name) or obj.vertex_groups.new(name=name)
            for i, w in items:
                g.add([i], w, 'REPLACE')
    if not any(m.type == 'ARMATURE' for m in obj.modifiers):
        obj.modifiers.new('Armature', 'ARMATURE').object = rig
    return obj


def mesh_obj(name, verts, faces):
    d = bpy.data.meshes.new(name)
    d.from_pydata(verts, [], faces)
    d.update()
    o = bpy.data.objects.new(name, d)
    scene.collection.objects.link(o)
    return o


def ellipsoid(name, centre, axes, basis=None, seg=10, rings=6):
    verts, faces = [], []
    for r in range(1, rings):
        t = math.pi * r / rings
        for s in range(seg):
            a = 2 * math.pi * s / seg
            verts.append((math.sin(t) * math.cos(a), math.sin(t) * math.sin(a), math.cos(t)))
    verts = [(0, 0, 1)] + verts + [(0, 0, -1)]
    for s in range(seg):
        faces.append((0, 1 + s, 1 + (s + 1) % seg))
    for r in range(rings - 2):
        for s in range(seg):
            a = 1 + r * seg + s
            b = 1 + r * seg + (s + 1) % seg
            faces.append((a, a + seg, b + seg, b))
    last = len(verts) - 1
    base = 1 + (rings - 2) * seg
    for s in range(seg):
        faces.append((base + (s + 1) % seg, base + s, last))
    basis = basis or Matrix.Identity(3)
    out = [Vector(centre) + basis @ Vector((x * axes[0], y * axes[1], z * axes[2])) for x, y, z in verts]
    return mesh_obj(name, out, faces)


def tube(name, points, radius, sides=8, flat=1.0):
    verts, faces = [], []
    pts = [Vector(p) for p in points]
    for j, p in enumerate(pts):
        d = (pts[min(j + 1, len(pts) - 1)] - pts[max(j - 1, 0)]).normalized()
        a = d.cross(Vector((0, 0, 1)))
        if a.length < .01:
            a = Vector((1, 0, 0))
        a.normalize()
        b = d.cross(a)
        for i in range(sides):
            ang = 2 * math.pi * i / sides
            verts.append(p + radius * (math.cos(ang) * a + flat * math.sin(ang) * b))
    for j in range(len(pts) - 1):
        for i in range(sides):
            a = j * sides + i
            b = j * sides + (i + 1) % sides
            faces.append((a, b, b + sides, a + sides))
    faces.append(tuple(reversed(range(sides))))
    faces.append(tuple((len(pts) - 1) * sides + i for i in range(sides)))
    return mesh_obj(name, verts, faces)


def box(name, centre, size, basis=None):
    basis = basis or Matrix.Identity(3)
    h = [s / 2 for s in size]
    corners = [Vector(centre) + basis @ Vector((sx * h[0], sy * h[1], sz * h[2]))
               for sz in (-1, 1) for sy in (-1, 1) for sx in (-1, 1)]
    faces = [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)]
    return mesh_obj(name, corners, faces)


# Ray-cast helper against the visible skin to place surface details.
depsgraph = bpy.context.evaluated_depsgraph_get()
TREES = {}


def surface(x, z, y0=-1.0, obj=None):
    """First hit travelling from y0 towards the body (front by default, back when y0 > 0)."""
    obj = obj or body
    if obj.name not in TREES:
        TREES[obj.name] = BVHTree.FromPolygons([v.co.copy() for v in obj.data.vertices], [tuple(p.vertices) for p in obj.data.polygons])
    hit = TREES[obj.name].ray_cast(Vector((x, y0, z)), Vector((0, 1 if y0 < 0 else -1, 0)))
    return hit[0]


# ---------------------------------------------------------------- face details
for side, ids in (('l', eye_l), ('r', eye_r)):
    c = centroid(ids)
    front = min(coords[i].y for i in ids)
    radius = max((coords[i] - c).length for i in ids)
    finish(ellipsoid(f'Eye iris {side}', (c.x, front + .0012, c.z), (radius * .48, .0014, radius * .48), seg=12, rings=6),
           'head', material=M['iris'])
    finish(ellipsoid(f'Eye pupil {side}', (c.x, front - .0004, c.z), (radius * .2, .0008, radius * .2), seg=10, rings=4),
           'head', material=M['pupil'])
    sign = 1 if side == 'l' else -1
    brow = []
    for t in (-.9, -.3, .3, .9):
        x = c.x + sign * t * radius * 1.25
        z = c.z + radius * 1.55 + (.0015 if abs(t) < .5 else -.001 * (t * sign > 0))
        p = surface(x, z)
        if p:
            brow.append(p + Vector((0, -.0018, 0)))
    if len(brow) >= 3:
        finish(tube(f'Brow {side}', brow, .0042, sides=6, flat=.5), 'head', material=M['brow'])

# ---------------------------------------------------------------- hair
finish(cap, 'head')
finish(crop, 'head')
rng = random.Random(30)
clumps = []
ids = sorted(scalp)
for i in ids[::3]:
    co = coords[i]
    rel = co - head_c
    n = rel.normalized()
    front = rel.y < -.03
    if front and co.z < eye_z + .075:
        continue
    if not front and co.z < eye_z + .06:
        continue  # sides and nape stay a close crop (cap only)
    if front:
        sweep = Vector((.55, -.35, -.75))           # fringe falls forward and to the character's left
    elif rel.y < .02:
        sweep = Vector((math.copysign(.5, rel.x), .6, -.35))
    else:
        sweep = Vector((-.15, .55, -.8))
    d = (sweep - n * sweep.dot(n)).normalized()
    side = n.cross(d).normalized()
    basis = Matrix((d, side, n)).transposed()
    length = rng.uniform(.04, .058) * (.85 if front else 1)
    centre = co + n * .013 + d * length * .3
    clumps.append(ellipsoid('Hair clump', centre, (length, rng.uniform(.024, .032), rng.uniform(.011, .014)), basis, seg=10, rings=6))
bpy.ops.object.select_all(action='DESELECT')
for o in clumps:
    o.select_set(True)
bpy.context.view_layer.objects.active = clumps[0]
bpy.ops.object.join()
hair = bpy.context.object
hair.name = 'Hair wavy clumps'
finish(hair, 'head', material=M['hair'])

# ---------------------------------------------------------------- hoodie hood and hems
neck_c = bone_head('neck_01')
back_y = max(coords[i].y for i in real if dom[i] in ('spine_03',) and coords[i].z > NECK - .08)
hood_p = surface(0, NECK - .06, y0=1.0, obj=hoodie)
hood_y = hood_p.y if hood_p else back_y + .02
hood = ellipsoid('Hoodie hood', (0, hood_y + .016, NECK - .07), (.13, .034, .065), seg=16, rings=8)
finish(hood, 'spine_03', material=M['hoodie'])
for side, sgn in (('l', 1), ('r', -1)):
    finish(tube(f'Hoodie drawstring {side}', [(sgn * .035, -.105, NECK - .02), (sgn * .04, -.118, NECK - .13)], .0025, 6),
           'spine_03', material=M['tee'])

# ---------------------------------------------------------------- backpack and straps
chest_back = max(coords[i].y for i in real if dom[i] in ('spine_02', 'spine_03'))
_bp = surface(0, bone_head('spine_02').z + .05, y0=1.0, obj=hoodie)
pack_c = Vector((0, (_bp.y if _bp else chest_back + .03) + .072, bone_head('spine_02').z + .05))
pack = box('Backpack body', pack_c, (.30, .14, .40))
mod = pack.modifiers.new('Bevel', 'BEVEL')
mod.width = .045
mod.segments = 4
bpy.context.view_layer.objects.active = pack
bpy.ops.object.modifier_apply(modifier='Bevel')
finish(pack, 'spine_03', material=M['pack'])
pocket = box('Backpack pocket', pack_c + Vector((0, .075, -.08)), (.22, .04, .17))
mod = pocket.modifiers.new('Bevel', 'BEVEL')
mod.width = .02
mod.segments = 3
bpy.context.view_layer.objects.active = pocket
bpy.ops.object.modifier_apply(modifier='Bevel')
finish(pocket, 'spine_03', material=M['pack_trim'])
shoulder_z = bone_head('clavicle_l').z
for side, sgn in (('l', 1), ('r', -1)):
    x = sgn * .11
    pts = [(x, pack_c.y - .05, pack_c.z + .17), (x, .03, shoulder_z + .035)]
    for z in (shoulder_z - .02, shoulder_z - .12, shoulder_z - .25, shoulder_z - .36):
        p = surface(x, z, obj=hoodie)
        pts.append((x, (p.y if p else -.12) - .014, z))
    pts.append((sgn * .15, -.02, shoulder_z - .44))
    finish(tube(f'Backpack strap {side}', pts, .022, 8, flat=.25), 'spine_03', material=M['pack'])

# ---------------------------------------------------------------- lanyard, badge, watch
card_z = shoulder_z - .26
card_p = surface(0, card_z, obj=tee)
card_y = (card_p.y if card_p else -.12) - .014
for side, sgn in (('l', 1), ('r', -1)):
    pts = [(sgn * .006, card_y, card_z + .05), (sgn * .03, card_y + .004, card_z + .14),
           (sgn * .055, -.06, NECK + .005), (sgn * .055, .0, NECK + .03), (0, .045, NECK + .035)]
    finish(tube(f'Lanyard strap {side}', pts, .006, 6, flat=.3), 'spine_03', material=M['lanyard'])
finish(box('ID badge card', (0, card_y, card_z), (.06, .004, .085)), 'spine_03', material=M['card'])
finish(box('ID badge header', (0, card_y - .0025, card_z + .03), (.06, .002, .02)), 'spine_03', material=M['lanyard'])
wrist = bone_head('hand_l')
fore = (bone_head('hand_l') - bone_head('lowerarm_l')).normalized()
a = fore.cross(Vector((0, 0, 1))).normalized()
b = fore.cross(a)
ring_pts = []
near = [(coords[i] - wrist).length for i in real if dom[i] == 'lowerarm_l' and abs((coords[i] - wrist - fore * -.03).dot(fore)) < .008 and (coords[i] - wrist).length < .08]
radius = min(max(near) if near else .028, .03) + .003
band = tube('Watch band', [wrist - fore * .045, wrist - fore * .02], radius, 16)
finish(band, 'lowerarm_l', material=M['watch'])
face = ellipsoid('Watch face', wrist - fore * .033 + b * (radius + .002), (.016, .016, .005), Matrix((a, fore, b)).transposed(), seg=14, rings=4)
finish(face, 'lowerarm_l', material=M['watch'])

# ---------------------------------------------------------------- shoes: soles and laces
for side in ('l', 'r'):
    ids = [i for i in shoe_region if dom[i] in (f'foot_{side}', f'ball_{side}')]
    xs = [coords[i].x for i in ids]
    ys = [coords[i].y for i in ids]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    w, l = (max(xs) - min(xs)) / 2 + .016, (max(ys) - min(ys)) / 2 + .02
    sole = ellipsoid(f'Sneaker sole {side}', (cx, cy, .012), (w, l, .016), seg=20, rings=6)
    finish(sole, f'foot_{side}', material=M['sole'])
    for k in range(3):
        y = cy - l * .2 - k * .02
        near = [coords[i].z for i in ids if abs(coords[i].y - y) < .012 and abs(coords[i].x - cx) < .02]
        z = (max(near) if near else ANKLE) + .019
        finish(tube(f'Sneaker lace {side}', [(cx - .022, y, z), (cx + .022, y, z)], .0025, 5), f'foot_{side}', material=M['tee'])

# ---------------------------------------------------------------- zip tapes and polygon budget
for sgn, side in ((1, 'l'), (-1, 'r')):
    edge = sorted((v.co.copy() for v in hoodie.data.vertices
                   if abs(v.co.x - sgn * .036) < .002 and v.co.y < -.03 and WAIST - .1 < v.co.z < NECK - .03), key=lambda c: c.z)
    if len(edge) > 3:
        pts = [edge[0]] + [edge[k] for k in range(2, len(edge) - 1, 3)] + [edge[-1]]
        finish(tube(f'Hoodie zip tape {side}', [p + Vector((0, -.003, 0)) for p in pts], .006, 6, flat=.5),
               'spine_02', material=M['hoodie_tape'])
BUDGET = {'Hair wavy clumps': .45, 'Hoodie body': .55, 'Chino trousers': .5, 'Tee shirt': .5,
          'Body skin': .5, 'Sneaker upper': .6}
for name, ratio in BUDGET.items():
    obj = bpy.data.objects[name]
    mod = obj.modifiers.new('Budget', 'DECIMATE')
    mod.ratio = ratio
    if name == 'Body skin':
        mod.vertex_group = 'head'      # keep the face at full resolution
        mod.invert_vertex_group = True
        mod.vertex_group_factor = 1.0
    with bpy.context.temp_override(object=obj, active_object=obj):
        bpy.ops.object.modifier_move_to_index(modifier='Budget', index=0)
        bpy.ops.object.modifier_apply(modifier='Budget')

# ---------------------------------------------------------------- scale to target height
bpy.context.view_layer.update()
meshes = [o for o in scene.objects if o.type == 'MESH']
pts = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
low, high = min(p.z for p in pts), max(p.z for p in pts)
factor = HEIGHT / (high - low)
S = Matrix.Translation((0, 0, -low * factor)) @ Matrix.Scale(factor, 4)
for o in meshes:
    mw = o.matrix_world.copy()
    o.parent = None
    o.matrix_world = S @ mw
rig.matrix_world = S @ rig.matrix_world
bpy.ops.object.select_all(action='DESELECT')
for o in meshes + [rig]:
    o.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in meshes:
    o.parent = rig
    o.matrix_parent_inverse = Matrix.Identity(4)
bpy.context.view_layer.update()
pts = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
print('V3 HEIGHT', round(min(p.z for p in pts), 4), round(max(p.z for p in pts), 4),
      'TRIS', sum(len(p.vertices) - 2 for o in meshes for p in o.data.polygons))

if QUICK:
    from export import quick_render
    quick_render(scene, rig, ROOT)
else:
    from animations import build_animations
    from export import render_and_export
    build_animations(scene, rig, [o for o in meshes if 'sneaker' in o.name.lower()])
    render_and_export(scene, rig, ROOT, mat)
