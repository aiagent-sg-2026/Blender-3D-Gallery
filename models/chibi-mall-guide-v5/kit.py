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


def super_front_y(c, r, x, z, p_top=2.0, p_bot=2.0, rz_bot=None):
    """Front (-Y) surface of the shape add_super builds, at (x, z). Returns the centre y when (x, z) is outside the shape."""
    zn = (z - c[2]) / (r[2] if (rz_bot is None or z >= c[2]) else rz_bot)
    if abs(zn) >= 1.0: return c[1]
    pp = p_top if zn >= 0 else p_bot
    f = math.sqrt(max(0.0, 1 - abs(zn) ** pp)) / math.sqrt(1 - zn * zn)
    t = (1 - zn * zn) - ((x - c[0]) / (f * r[0])) ** 2
    return c[1] - f * r[1] * math.sqrt(max(0.0, t))


def _smooth(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


def add_patch(bm, surf_y, c, a, b, lift, rings=6, seg=28, mi=0, mi_fn=None):
    """Elliptical raised patch lying on a surface: boundary exactly on the ellipse (a, b) in the X-Z plane, flush with the skin there,
    rising by `lift` toward the centre. mi_fn(rho_mid, theta_mid) may return a different material slot per face. Returns new verts."""
    n0 = len(bm.faces); grid = []; verts = []
    for k in range(rings + 1):
        rho = k / rings; ring = []
        for j in range(seg if k else 1):
            th = 2 * math.pi * j / seg
            x = c[0] + a * rho * math.cos(th); z = c[1] + b * rho * math.sin(th)
            y = surf_y(x, z) - lift * math.sqrt(max(0.0, 1 - rho * rho)) - 0.0004
            v = bm.verts.new((x, y, z)); ring.append(v); verts.append(v)
        grid.append(ring)
    for j in range(seg):
        bm.faces.new((grid[0][0], grid[1][(j + 1) % seg], grid[1][j]))
    for k in range(1, rings):
        for j in range(seg):
            bm.faces.new((grid[k][j], grid[k][(j + 1) % seg], grid[k + 1][(j + 1) % seg], grid[k + 1][j]))
    bm.faces.ensure_lookup_table()
    for f in bm.faces[n0:]:
        f.material_index = mi
        if mi_fn:
            cx = sum(v.co.x for v in f.verts) / len(f.verts); cz = sum(v.co.z for v in f.verts) / len(f.verts)
            f.material_index = mi_fn((cx - c[0]) / a, (cz - c[1]) / b)
    return verts


def add_band(bm, surf_y, u_range, top_fn, bot_fn, x_fn, lift, steps_u=14, steps_v=3, mi=0):
    """Curved band on a surface: for u in u_range, z runs from top_fn(u) to bot_fn(u) at x = x_fn(u); lift fades to 0 at both z edges."""
    n0 = len(bm.faces); grid = []; verts = []
    for i in range(steps_u + 1):
        u = u_range[0] + (u_range[1] - u_range[0]) * i / steps_u; col = []
        for j in range(steps_v + 1):
            t = j / steps_v; x = x_fn(u); z = top_fn(u) + (bot_fn(u) - top_fn(u)) * t
            y = surf_y(x, z) - lift * math.sin(math.pi * t) * math.sin(math.pi * (i / steps_u)) ** 0.5 - 0.0004
            v = bm.verts.new((x, y, z)); col.append(v); verts.append(v)
        grid.append(col)
    for i in range(steps_u):
        for j in range(steps_v):
            bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))
    bm.faces.ensure_lookup_table()
    for f in bm.faces[n0:]: f.material_index = mi
    return verts
