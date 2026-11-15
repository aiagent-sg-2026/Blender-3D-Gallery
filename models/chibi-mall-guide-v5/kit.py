"""Small bmesh helpers for the Mall Guide build (seed of the future framework `kit`; Blender only).
All functions append geometry to a bmesh and tag new faces with a material slot index."""
import bmesh, bpy, math
from mathutils import Vector


def _tag(faces, mi):
    for f in faces: f.material_index = mi


def add_super(bm, c, r, p_top=2.0, p_bot=2.0, rz_bot=None, seg=28, rings=18, mi=0, rot_x=0.0):
    """Ellipsoid / superellipsoid centred at c with radii r. p > 2 squares that half; rz_bot overrides the lower z radius."""
    n0 = len(bm.faces)
    ret = bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=1.0)
    for v in ret['verts']:
        z = v.co.z; pp = p_bot if z < 0 else p_top; f = 1.0
        if pp != 2.0 and abs(z) < 0.9999: f = math.sqrt(max(0.0, 1 - abs(z) ** pp)) / math.sqrt(1 - z * z)
        rz = r[2] if (rz_bot is None or z >= 0) else rz_bot
        lx, ly, lz = v.co.x * f * r[0], v.co.y * f * r[1], z * rz
        if rot_x:   # tilt about the X axis through the centre: local +Z leans toward +Y by rot_x
            ly, lz = ly * math.cos(rot_x) - lz * 0 + lz * math.sin(rot_x), lz * math.cos(rot_x) - ly * math.sin(rot_x)
        v.co = Vector((lx + c[0], ly + c[1], lz + c[2]))
    bm.faces.ensure_lookup_table(); _tag(bm.faces[n0:], mi)
    return ret['verts']


def add_tube(bm, pts, radii, sides=14, cap_start=True, cap_end=True, mi=0, squash=1.0):
    """Tube along a polyline with per-point radii (parallel-transport frames). squash scales the local second axis."""
    pts = [Vector(p) for p in pts]; n0 = len(bm.faces)
    tang = []
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized(); tang.append(t)
    up = Vector((0, 1, 0)) if abs(tang[0].y) < 0.9 else Vector((1, 0, 0))
    rings = []
    nrm = tang[0].cross(up).normalized()
    for i, p in enumerate(pts):
        if i: nrm = (nrm - tang[i] * nrm.dot(tang[i])).normalized()
        bi = tang[i].cross(nrm).normalized(); ring = []
        for k in range(sides):
            a = 2 * math.pi * k / sides
            ring.append(bm.verts.new(p + nrm * math.cos(a) * radii[i] + bi * math.sin(a) * radii[i] * squash))
        rings.append(ring)
    for i in range(len(rings) - 1):
        for k in range(sides):
            bm.faces.new((rings[i][k], rings[i][(k + 1) % sides], rings[i + 1][(k + 1) % sides], rings[i + 1][k]))
    if cap_start: bm.faces.new(rings[0][::-1])
    if cap_end: bm.faces.new(rings[-1])
    bm.faces.ensure_lookup_table(); _tag(bm.faces[n0:], mi)
    return rings


def add_torus(bm, c, major, minor, scale_xy=(1.0, 1.0), seg=36, tube=8, mi=0):
    n0 = len(bm.faces); rings = []
    for i in range(seg):
        a = 2 * math.pi * i / seg; ring = []
        for j in range(tube):
            b = 2 * math.pi * j / tube; rr = major + minor * math.cos(b)
            ring.append(bm.verts.new((c[0] + rr * math.cos(a) * scale_xy[0], c[1] + rr * math.sin(a) * scale_xy[1], c[2] + minor * math.sin(b))))
        rings.append(ring)
    for i in range(seg):
        for j in range(tube):
            bm.faces.new((rings[i][j], rings[(i + 1) % seg][j], rings[(i + 1) % seg][(j + 1) % tube], rings[i][(j + 1) % tube]))
    bm.faces.ensure_lookup_table(); _tag(bm.faces[n0:], mi)


def delete_faces(bm, pred):
    kill = [f for f in bm.faces if pred(f.calc_center_median())]
    bmesh.ops.delete(bm, geom=kill, context='FACES')
    loose = [v for v in bm.verts if not v.link_faces]
    bmesh.ops.delete(bm, geom=loose, context='VERTS')


def finish(name, bm, mats, collection=None):
    """Turn a bmesh into an object with the given material list; flat-shaded polygons become smooth."""
    bm.normal_update(); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    for m in mats: me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    (collection or bpy.context.scene.collection).objects.link(ob)
    return ob


def tri_count(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)
