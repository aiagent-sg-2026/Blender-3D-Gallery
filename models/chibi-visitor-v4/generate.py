"""Chibi Visitor v4 - procedural Blender build from the supplied character sheet.

Run it in the connected Blender through the Blender MCP `execute_blender_code`
tool (call build(), then write_outputs()), or headless from the repository root:

    blender --background --factory-startup --python-exit-code 1 \
        --python models/chibi-visitor-v4/generate.py

It only touches a scene named "Chibi Visitor v4" and data it tagged itself, so
an interactive session is never reset. Units are metres, the feet stand on
z = 0, the character faces -Y (glTF +Z) and the total height is 1.00 m.
All shapes are authored here by hand; no downloaded or generated mesh is used.
"""
import math as m
import os

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

SCENE = "Chibi Visitor v4"
TAG = "cv4"
TAU = m.tau
HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))


# ----------------------------------------------------------------- maths
def sp(v, e):
    return m.copysign(abs(v) ** e, v)


def sstep(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


def spline(keys):
    """Catmull-Rom through evenly spaced keys; f(t) with t in 0..1."""
    k = [tuple(map(float, q)) for q in keys]
    n = len(k)

    def f(t):
        x = min(max(t, 0.0), 1.0) * (n - 1)
        i = min(int(x), n - 2)
        u = x - i
        p0, p1, p2, p3 = k[max(i - 1, 0)], k[i], k[i + 1], k[min(i + 2, n - 1)]
        return tuple(
            0.5 * (2 * b + (c - a) * u + (2 * a - 5 * b + 4 * c - d) * u * u + (3 * b - a - 3 * c + d) * u ** 3)
            for a, b, c, d in zip(p0, p1, p2, p3))
    return f


def curve(keys):
    """Smooth Hermite interpolation of (x, a, b, ...) keys over x."""
    xs = [q[0] for q in keys]
    ys = [q[1:] for q in keys]
    n = len(keys)

    def tangent(i):
        a, b = max(i - 1, 0), min(i + 1, n - 1)
        return [(q - p) / (xs[b] - xs[a]) for p, q in zip(ys[a], ys[b])]
    ts = [tangent(i) for i in range(n)]

    def f(x):
        x = min(max(x, xs[0]), xs[-1])
        i = 0
        while i < n - 2 and x > xs[i + 1]:
            i += 1
        h = xs[i + 1] - xs[i]
        u = (x - xs[i]) / h
        h00, h10 = 2 * u ** 3 - 3 * u * u + 1, u ** 3 - 2 * u * u + u
        h01, h11 = -2 * u ** 3 + 3 * u * u, u ** 3 - u * u
        return tuple(h00 * a + h10 * h * ta + h01 * b + h11 * h * tb
                     for a, b, ta, tb in zip(ys[i], ys[i + 1], ts[i], ts[i + 1]))
    return f


def path3(ctrl, steps):
    f = spline(ctrl)
    return [Vector(f(i / steps)) for i in range(steps + 1)]


def rot_z(deg):
    return Matrix.Rotation(m.radians(deg), 3, "Z")


# ------------------------------------------------------------ geometry
def g_param(fn, nu, nv):
    """Closed surface from fn(u, v), u pole to pole, v around."""
    v = [fn(0.0, 0.0)]
    for i in range(1, nu):
        for j in range(nv):
            v.append(fn(i / nu, j / nv))
    v.append(fn(1.0, 0.0))
    f = [(0, 1 + j, 1 + (j + 1) % nv) for j in range(nv)]
    for i in range(nu - 2):
        a = 1 + i * nv
        b = a + nv
        f += [(a + j, b + j, b + (j + 1) % nv, a + (j + 1) % nv) for j in range(nv)]
    a, last = 1 + (nu - 2) * nv, len(v) - 1
    f += [(last, a + (j + 1) % nv, a + j) for j in range(nv)]
    return v, f


def g_ellipsoid(c, r, rot=None, nu=12, nv=20, e1=1.0, e2=1.0):
    """Ellipsoid, or a rounded box when e1/e2 are below one."""
    c = Vector(c)
    rm = rot or Matrix.Identity(3)

    def fn(u, v):
        su, cu, a = m.sin(m.pi * u), m.cos(m.pi * u), TAU * v
        return c + rm @ Vector((r[0] * sp(su, e1) * sp(m.cos(a), e2),
                                r[1] * sp(su, e1) * sp(m.sin(a), e2), r[2] * sp(cu, e1)))
    return g_param(fn, nu, nv)


def g_loft(rings, cap0=True, cap1=True, closed=False):
    n, count = len(rings[0]), len(rings)
    v = [Vector(p) for ring_ in rings for p in ring_]
    f = []
    for i in range(count if closed else count - 1):
        a, b = i * n, ((i + 1) % count) * n
        f += [(a + j, a + (j + 1) % n, b + (j + 1) % n, b + j) for j in range(n)]
    if not closed:
        for flag, ring_, base in ((cap0, rings[0], 0), (cap1, rings[-1], (count - 1) * n)):
            if flag:
                v.append(sum(ring_, Vector()) / n)
                k = len(v) - 1
                f += [(k, base + j, base + (j + 1) % n) for j in range(n)]
    return v, f


def ring(z, rx, ry, cx=0.0, cy=0.0, n=32, e=2.0, rib=0.0):
    out = []
    for j in range(n):
        a = TAU * j / n
        s = 1.0 + (rib if j % 2 else -rib)
        out.append(Vector((cx + rx * s * sp(m.cos(a), 2 / e), cy + ry * s * sp(m.sin(a), 2 / e), z)))
    return out


def frames(pts, hint=None, normals=None, closed=False):
    n = len(pts)
    tan = []
    for i in range(n):
        a = pts[(i - 1) % n] if (closed or i > 0) else pts[i]
        b = pts[(i + 1) % n] if (closed or i < n - 1) else pts[i]
        tan.append((b - a).normalized())
    nor, prev = [], Vector(hint or (0, 0, 1))
    for i in range(n):
        h = Vector(normals[i]) if normals else prev
        q = h - tan[i] * h.dot(tan[i])
        if q.length < 1e-6:
            q = tan[i].orthogonal()
        q.normalize()
        nor.append(q)
        prev = q
    return tan, nor, [t.cross(q) for t, q in zip(tan, nor)]


def g_sweep(pts, section, hint=None, normals=None, closed=False, cap=True):
    """Sweep section(i) -> [(binormal, normal) offsets] along pts."""
    _, nor, bin_ = frames(pts, hint, normals, closed)
    rings = [[p + bin_[i] * b + nor[i] * h for b, h in section(i)] for i, p in enumerate(pts)]
    return g_loft(rings, cap, cap, closed)


def circle(r, n=10, squash=1.0):
    return [(r * m.cos(TAU * k / n), r * squash * m.sin(TAU * k / n)) for k in range(n)]


def g_tube(pts, radii, n=12, squash=1.0, **kw):
    return g_sweep(pts, lambda i: circle(radii[i], n, squash), **kw)


def bvh_of(geom):
    return BVHTree.FromPolygons([tuple(p) for p in geom[0]], [tuple(f) for f in geom[1]])


def dense(outline, n=6):
    """Subdivide polygon edges so a decal can bend with the surface."""
    out = []
    for i, (ax, az) in enumerate(outline):
        bx, bz = outline[(i + 1) % len(outline)]
        out += [(lerp(ax, bx, k / n), lerp(az, bz, k / n)) for k in range(n)]
    return out


def ell(cx, cz, a, b, n=28):
    return [(cx + a * m.cos(TAU * k / n), cz + b * m.sin(TAU * k / n)) for k in range(n)]


class Projector:
    """Drops 2D shapes onto a surface along a direction."""

    def __init__(self, bvh, direction=Y, e1=X, e2=Z, origin=(0, 0, 0)):
        self.bvh, self.d = bvh, Vector(direction).normalized()
        self.e1, self.e2, self.o = Vector(e1), Vector(e2), Vector(origin)

    def drop(self, a, b, off):
        loc, nor, _, _ = self.bvh.ray_cast(self.o + self.e1 * a + self.e2 * b - self.d * 2.0, self.d)
        if loc is None:
            return None
        if nor.dot(self.d) > 0:
            nor = -nor
        return loc + nor * off

    def decal(self, outline, off, rings=3):
        n = len(outline)
        cx, cz = sum(p[0] for p in outline) / n, sum(p[1] for p in outline) / n
        c = self.drop(cx, cz, off)
        v = [c]
        for k in range(1, rings + 1):
            t = k / rings
            for a, b in outline:
                v.append(self.drop(cx + (a - cx) * t, cz + (b - cz) * t, off) or c)
        f = [(0, 1 + j, 1 + (j + 1) % n) for j in range(n)]
        for k in range(rings - 1):
            a0 = 1 + k * n
            b0 = a0 + n
            f += [(a0 + j, b0 + j, b0 + (j + 1) % n, a0 + (j + 1) % n) for j in range(n)]
        return v, f

    def strip(self, line, widths, off):
        n = len(line)
        v, f, last = [], [], None
        for i, (x, z) in enumerate(line):
            ax, az = line[max(i - 1, 0)]
            bx, bz = line[min(i + 1, n - 1)]
            tx, tz = bx - ax, bz - az
            ln = m.hypot(tx, tz) or 1.0
            nx, nz, w = -tz / ln, tx / ln, widths[i] / 2
            for a, b in ((x + nx * w, z + nz * w), (x, z), (x - nx * w, z - nz * w)):
                last = self.drop(a, b, off) or last
                v.append(last)
        for i in range(n - 1):
            a = i * 3
            f += [(a, a + 1, a + 4, a + 3), (a + 1, a + 2, a + 5, a + 4)]
        return v, f

    def facing(self, _centre):
        return -self.d


class Part:
    """Collects closed pieces into one multi-material mesh object."""

    def __init__(self, name):
        self.name, self.v, self.f, self.mi, self.mats, self.col, self.uv = name, [], [], [], [], {}, None

    def add(self, geom, material, outward=None, colors=None):
        verts = [Vector(p) for p in geom[0]]
        bm = bmesh.new()
        bv = [bm.verts.new(p) for p in verts]
        bm.verts.index_update()
        for face in geom[1]:
            try:
                bm.faces.new([bv[i] for i in face])
            except ValueError:
                pass
        bm.normal_update()
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        if outward is not None:
            if sum(fc.normal.dot(outward(fc.calc_center_median())) for fc in bm.faces) < 0:
                bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
        base = len(self.v)
        self.v += verts
        for fc in bm.faces:
            mt = material(fc.calc_center_median()) if callable(material) else material
            if mt not in self.mats:
                self.mats.append(mt)
            self.f.append([base + q.index for q in fc.verts])
            self.mi.append(self.mats.index(mt))
        bm.free()
        if colors:
            for i, c in enumerate(colors):
                self.col[base + i] = c
        return geom

    def build(self, coll, parent):
        me = bpy.data.meshes.new(self.name)
        me[TAG] = 1
        me.from_pydata([tuple(p) for p in self.v], [], self.f)
        for mt in self.mats:
            me.materials.append(mt)
        me.polygons.foreach_set("material_index", self.mi)
        me.polygons.foreach_set("use_smooth", [True] * len(self.f))
        if self.col:
            attr = me.color_attributes.new(name="Col", type="BYTE_COLOR", domain="CORNER")
            idx = [0] * len(me.loops)
            me.loops.foreach_get("vertex_index", idx)
            flat = []
            for i in idx:
                flat += self.col.get(i, (1.0, 1.0, 1.0, 1.0))
            attr.data.foreach_set("color", flat)
        me.update()
        if self.uv:                                          # uv(position, normal) -> (u, v)
            layer = me.uv_layers.new(name="UVMap")
            idx = [0] * len(me.loops)
            me.loops.foreach_get("vertex_index", idx)
            per = [self.uv(v.co, v.normal) for v in me.vertices]
            layer.data.foreach_set("uv", [c for i in idx for c in per[i]])
        ob = bpy.data.objects.new(self.name, me)
        ob[TAG] = 1
        coll.objects.link(ob)
        ob.parent = parent
        return ob


def fuse(geoms, voxel=0.003, smooth=6, ratio=0.2):
    """Melt overlapping closed pieces into one smooth skin, like a sculpt remesh."""
    sc = bpy.data.scenes[SCENE]
    v, f = [], []
    for gv, gf in geoms:
        base = len(v)
        v += [tuple(q) for q in gv]
        f += [[base + i for i in face] for face in gf]
    me = bpy.data.meshes.new("cv4 fuse")
    me.from_pydata(v, [], f)
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("cv4 fuse", me)
    sc.collection.objects.link(ob)
    remesh = ob.modifiers.new("Remesh", "REMESH")
    remesh.mode, remesh.voxel_size = "VOXEL", voxel
    soften = ob.modifiers.new("Smooth", "SMOOTH")
    soften.factor, soften.iterations = 0.5, smooth
    ob.modifiers.new("Decimate", "DECIMATE").ratio = ratio
    layer = sc.view_layers[0]
    layer.update()
    out = bpy.data.meshes.new_from_object(ob.evaluated_get(layer.depsgraph))
    geom = ([q.co.copy() for q in out.vertices], [list(q.vertices) for q in out.polygons])
    bpy.data.meshes.remove(out)
    bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.meshes.remove(me)
    return geom


# ------------------------------------------------------------ materials
def lin(h):
    t = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in t]


def srgb(h):
    return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def mat(name, h, rough=0.5, metal=0.0, vcol=False, image=None):
    a = bpy.data.materials.new(name)
    a[TAG] = 1
    a.use_nodes = True
    c = (1.0, 1.0, 1.0) if vcol else lin(h)
    a.diffuse_color = (*lin(h), 1)
    b = a.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*c, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if image:
        node = a.node_tree.nodes.new("ShaderNodeTexImage")
        node.image = image
        a.node_tree.links.new(node.outputs["Color"], b.inputs["Base Color"])
    if vcol:
        node = a.node_tree.nodes.new("ShaderNodeVertexColor")
        node.layer_name = "Col"
        a.node_tree.links.new(node.outputs["Color"], b.inputs["Base Color"])
    return a


SKIN, BLUSH = "FBD2B2", "F59C92"


def materials():
    return dict(
        skin=mat("Skin", SKIN, 0.55),
        hair=mat("Hair", "50342A", 0.38), hair2=mat("Hair light", "593A2F", 0.38),
        brow=mat("Brow", "4A2E22", 0.6), lash=mat("Lash", "38211A", 0.6), white=mat("Eye white", "FFFFFF", 0.35),
        iris=mat("Iris", "40251A", 0.3), iris2=mat("Iris glow", "6A3E27", 0.3), pupil=mat("Pupil", "1B0F0C", 0.25),
        mouth=mat("Mouth", "B23E39", 0.5), tongue=mat("Tongue", "F28E80", 0.45),
        blue=mat("Hoodie", "3F66DC", 0.62), rib=mat("Hoodie rib", "3A5ECE", 0.66), seam=mat("Hoodie seam", "3354BC", 0.66),
        tee=mat("Tee", "F7F7F4", 0.6), cord=mat("Drawstring", "F5F5F5", 0.5),
        navy=mat("Shorts", "363A58", 0.66), cuff=mat("Shorts cuff", "3E4364", 0.66), stitch=mat("Shorts seam", "2A2D45", 0.7),
        sock=mat("Sock", "F8F8F8", 0.7), shoe=mat("Shoe", "3D52A6", 0.55), rubber=mat("Shoe rubber", "F6F6F8", 0.4),
        bag=mat("Bag", "D2A66C", 0.62), bag2=mat("Bag trim", "BC8E57", 0.6), strap=mat("Strap", "6A4630", 0.6),
        watch=mat("Watch", "25262E", 0.42), screen=mat("Watch screen", "4B5060", 0.2, 0.3),
    )


# ----------------------------------------------------------------- head
HC = Vector((0.0, 0.028, 0.757))          # skull centre
HB, HV, HTOP, HEXP = 0.172, 0.188, 0.150, 4.2
HH = HC + Vector((0.0, 0.004, 0.004))     # hair centre


def head_point(u, v):
    cu, su, a = m.cos(m.pi * u), m.sin(m.pi * u), TAU * v
    if cu >= 0:
        h, z = su, HTOP * cu
    else:
        ex = 2.3 + (HEXP - 2.3) * sstep(0.45, -0.15, m.sin(a))    # square jaw in front, round nape
        h, z = sp(su, 2 / ex), HV * sp(cu, 2 / ex)
    wide = 0.151 + 0.031 * sstep(-0.125, 0.05, z)            # wide cranium, narrow cheeks
    box = 2 / (2.0 + 0.9 * sstep(0.02, -0.08, z))            # flat face plane below the brow
    p = Vector((wide * h * sp(m.cos(a), box), HB * h * sp(m.sin(a), box), z))
    front = sstep(0.0, -0.09, p.y)
    p.y -= 0.017 * front * m.exp(-(p.x / 0.13) ** 2 - ((p.z + 0.120) / 0.055) ** 2)      # muzzle and cheeks
    p.y += 0.011 * front * m.exp(-(p.x / 0.16) ** 2 - ((p.z + 0.060) / 0.040) ** 2)      # eye line sits back
    p.x += m.copysign(0.005, p.x) * front * m.exp(-((abs(p.x) - 0.12) / 0.05) ** 2 - ((p.z + 0.115) / 0.05) ** 2)
    return HC + p


TEX_X, TEX_Z, TEX_W = -0.24, 0.53, 0.48                      # face texture window in metres (front view)


def face_texture(size=1024):
    """Paint eyes, brows, mouth and blush as one front-projected image."""
    import numpy as np
    px = TEX_W / size
    axis = (np.arange(size) + 0.5) * px
    gx, gz = np.meshgrid(axis + TEX_X, axis + TEX_Z)        # row 0 is the bottom row, as Blender stores it
    img = np.empty((size, size, 3))
    img[:] = srgb(SKIN)

    def cover(d):                                            # signed distance (negative inside) -> coverage
        return np.clip(0.5 - d / px, 0.0, 1.0)

    def paint(colour, alpha):
        c = colour if isinstance(colour, np.ndarray) else np.array(colour)
        img[:] = img * (1 - alpha[..., None]) + c * alpha[..., None]

    def oval(cx, cz, a, b):
        return (np.sqrt(((gx - cx) / a) ** 2 + ((gz - cz) / b) ** 2) - 1) * min(a, b)

    def capsule(p, q, r):
        dx, dz = q[0] - p[0], q[1] - p[1]
        t = np.clip(((gx - p[0]) * dx + (gz - p[1]) * dz) / (dx * dx + dz * dz), 0, 1)
        return np.hypot(gx - p[0] - t * dx, gz - p[1] - t * dz) - r

    def soft(cx, cz, a, b):
        return np.exp(-((gx - cx) / a) ** 2 - ((gz - cz) / b) ** 2)

    paint(srgb(BLUSH), 0.55 * soft(0.118, 0.632, 0.036, 0.026) + 0.55 * soft(-0.118, 0.632, 0.036, 0.026))
    paint(srgb("E8A688"), 0.30 * soft(0.0, 0.6455, 0.007, 0.0035))                          # under the nose
    for s in (-1, 1):
        paint(srgb("EDA688"), 0.55 * soft(s * 0.187, 0.650, 0.009, 0.022))                  # inner ear
        ex, ix = s * 0.082, s * 0.0795
        white = cover(oval(ex, 0.683, 0.0385, 0.0405))
        paint(srgb("5A372A"), 0.75 * cover(oval(ex, 0.683, 0.0398, 0.0418)) * np.clip((0.678 - gz) / 0.01, 0, 1))
        paint([0.985, 0.985, 0.99], white)
        paint([0.78, 0.79, 0.86], 0.55 * white * np.clip((gz - 0.698) / 0.026, 0, 1))        # lid shadow
        iris = cover(oval(ix, 0.6805, 0.0325, 0.0390)) * white
        t = np.clip((gz - 0.6415) / 0.078, 0, 1)[..., None] ** 0.75
        paint(np.array(srgb("935A36")) * (1 - t) + np.array(srgb("341C13")) * t, iris)
        rim = np.sqrt(((gx - ix) / 0.0325) ** 2 + ((gz - 0.6805) / 0.0390) ** 2)
        paint(srgb("2A160F"), 0.6 * iris * np.clip((rim - 0.78) / 0.22, 0, 1))
        paint(srgb("160B08"), cover(oval(ix, 0.686, 0.0175, 0.0225)) * white)
        paint([1.0, 1.0, 1.0], cover(oval(ix - s * 0.012, 0.701, 0.0095, 0.0095)))
        paint([1.0, 1.0, 1.0], cover(oval(ix + s * 0.013, 0.666, 0.0045, 0.0045)))
        lash = cover(oval(ex, 0.6885, 0.0435, 0.0455)) * (1 - cover(oval(ex, 0.6795, 0.0405, 0.0425)))
        lash = np.maximum(lash * np.clip((gz - 0.686) / 0.006, 0, 1),
                          cover(capsule((ex + s * 0.033, 0.7045), (ex + s * 0.0505, 0.7125), 0.0027)))
        paint(srgb("33201A"), lash)
        f = spline([(s * 0.047, 0.752, 0.0050), (s * 0.066, 0.764, 0.0075), (s * 0.086, 0.767, 0.0075),
                    (s * 0.106, 0.760, 0.0055), (s * 0.122, 0.747, 0.0025)])
        pts = [f(i / 20) for i in range(21)]
        brow = np.zeros_like(gx)
        for a, b in zip(pts, pts[1:]):
            brow = np.maximum(brow, cover(capsule(a, b, (a[2] + b[2]) / 2)))
        paint(srgb("4A2E22"), brow)
    a, top = 0.038, 0.628
    u = np.clip(1 - (gx / a) ** 2, 0, 1)
    top_z, low_z = top - 0.007 * u, top - 0.035 * u ** 0.42
    mouth = np.maximum(np.maximum(gz - top_z, low_z - gz), np.abs(gx) - a)
    paint(srgb("A63A33"), cover(mouth))
    paint(srgb("EE8578"), cover(np.maximum(mouth, oval(0.0, 0.6025, 0.024, 0.0095))))
    teeth = top_z - 0.0012 - 0.0075 * np.sqrt(np.clip(1 - (gx / (0.9 * a)) ** 2, 0, 1))
    paint(srgb("FAF6F2"), cover(np.maximum(np.maximum(mouth, teeth - gz), np.abs(gx) - 0.9 * a)))
    image = bpy.data.images.new("CV4 face", size, size, alpha=False)
    image[TAG] = 1
    image.pixels.foreach_set(np.dstack([img, np.ones((size, size))]).astype(np.float32).ravel())
    image.pack()
    return image


def face_uv(co, normal):
    """Front projection; surfaces turned away sample the plain skin row."""
    u = min(max((co.x - TEX_X) / TEX_W, 0.004), 0.996)
    return (u, min(max((co.z - TEX_Z) / TEX_W, 0.004), 0.996) if normal.y < 0.2 else 0.004)


def sculpted_skull():
    """Skull baked from the sculpt workflow (sculpt_head.py), or None to fall back to the parametric one."""
    import json
    path = os.path.join(HERE, "sources", "head-sculpt.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        d = json.load(f)
    return [tuple(v) for v in d["verts"]], d["faces"]


def build_head(mt):
    """Head, ears, nose and neck fused into one skin, with the face painted on."""
    part = Part("Head")
    skull = sculpted_skull() or g_param(head_point, 44, 72)
    pieces = [skull, g_loft([ring(z, 0.047, 0.045, 0, 0.008, 24) for z in (0.52, 0.56, 0.6)])]
    for s in (-1, 1):
        pieces.append(g_ellipsoid((s * 0.176, 0.032, 0.651), (0.020, 0.036, 0.046), rot_z(-s * 40), 12, 20))
    nose = Projector(bvh_of(skull)).drop(0.0, 0.652, 0.0)
    pieces.append(g_ellipsoid(nose, (0.0085, 0.0075, 0.0060), None, 8, 12))
    part.add(fuse(pieces, 0.003, 5, 0.14), mat("Skin face", SKIN, 0.55, image=face_texture()))
    part.uv = face_uv
    return part


# ----------------------------------------------------------------- hair
def hshell(az, el, radius):
    """Point on the hair shell: az 0 front, +90 the character's left; el up."""
    a, e = m.radians(az), m.radians(el)
    ce, se = m.cos(e), m.sin(e)
    if se >= 0:                                              # flat-topped dome, rounded off at the back
        h, v = sp(ce, 2 / 2.7), sp(se, 2 / 2.7)
        y = -h * m.cos(a)
        if y > 0:
            y *= 1 - 0.16 * sstep(0.4, 0.85, v) - 0.2 * sstep(0.85, 1.0, v)
        side = 1 - 0.045 * sstep(0.1, 0.6, v)                # narrow the upper dome sideways to match the sheet's crown width
        return HH + Vector((h * m.sin(a) * side, y, 0.82 * v)) * radius
    return HH + Vector((ce * m.sin(a), -ce * m.cos(a), se)) * radius


def hframe(az, el, radius):
    p = hshell(az, el, radius)
    n = (hshell(az + 1, el, radius) - hshell(az - 1, el, radius)).cross(
        hshell(az, el + 1, radius) - hshell(az, el - 1, radius))
    if n.length < 1e-9:
        n = p - HH
    n.normalize()
    return p, (n if n.dot(p - HH) > 0 else -n)


def hairline(az):
    a = abs(((az + 180) % 360) - 180)
    if a <= 30:
        return 40.0
    if a <= 66:
        return lerp(40, -8, sstep(30, 66, a))
    if a <= 100:
        return lerp(-8, -15, sstep(75, 100, a))
    if a <= 128:
        return lerp(-15, -60, sstep(100, 128, a))
    return -60.0


def g_cap(radius, nv=72, nr=16, solid=False):
    v = [hshell(0, 90, radius)]
    for i in range(1, nr + 1):
        for j in range(nv):
            az = 360 * j / nv - 180
            v.append(hshell(az, lerp(90, hairline(az), i / nr), radius))
    f = [(0, 1 + j, 1 + (j + 1) % nv) for j in range(nv)]
    for i in range(nr - 1):
        a = 1 + i * nv
        b = a + nv
        f += [(a + j, b + j, b + (j + 1) % nv, a + (j + 1) % nv) for j in range(nv)]
    if solid:                                                # close it towards the centre of the head
        v.append(HH.copy())
        a = 1 + (nr - 1) * nv
        f += [(len(v) - 1, a + (j + 1) % nv, a + j) for j in range(nv)]
    return v, f


def g_leaf(pts, normals, width, thick=None, groove=0.12, tip=0.06, taper=2.2, root=0.6, belly=0.4):
    """Leaf-shaped hair lock: narrow root, wide belly, pointed tip, ridged dome."""
    seg = len(pts) - 1
    th = thick or min(0.038, 0.32 * width)

    def section(i):
        t = i / seg
        w = width * max(tip, (root + (1 - root) * sstep(0.0, 0.3, t)) * (1 - t ** taper) ** 0.8)
        h = th * (w / width) ** 0.6
        out = []
        for k in range(13):                                  # strand ridges across the top
            a = m.pi * k / 12
            out.append((-m.cos(a) * w / 2, m.sin(a) * h * (1 - (groove if k % 2 == 0 and 0 < k < 12 else 0))))
        for k in range(1, 4):
            a = m.pi + m.pi * k / 4
            out.append((-m.cos(a) * w / 2, m.sin(a) * h * belly))
        return out
    return g_sweep(pts, section, normals=normals)


def g_lock(ctrl, width, radius, seg=16, **kw):
    """Lock following the hair shell; ctrl is (az, el, radius scale) keys."""
    f = spline(ctrl)
    pts, nor = [], []
    for i in range(seg + 1):
        az, el, rs = f(i / seg)
        p, n = hframe(az, el, radius * rs)
        pts.append(p)
        nor.append(n)
    return g_leaf(pts, nor, width, **kw)


def hair_locks():
    locks = []                                               # (ctrl, width, radius): broad shingled locks off a crown whorl
    for k in range(-3, 4):                                   # nape: fewer, wider locks
        az, sw = 180 + k * 29, 9 if k % 2 else -9
        tip = {3: -30, 2: -44}.get(abs(k), -56)
        locks.append(([(az - 0.3 * sw, 14, 0.98), (az, -12, 1.0), (az + 0.5 * sw, -36, 1.01), (az + sw, tip, 0.99)],
                      0.135, 0.190))
    for k in range(-3, 3):                                   # lower back
        az, sw = 180 + (k + 0.5) * 30, -10 if k % 2 else 10
        locks.append(([(az, 46, 0.98), (az, 24, 1.0), (az + 0.5 * sw, 2, 1.01), (az + sw, -20, 1.06)], 0.150, 0.197))
    for k in range(-2, 3):                                   # upper back: a fan opening monotonically from the whorl
        az = 180 + k * 40
        sw = 0.25 * (az - 180)
        wide, tip = (0.170, 0) if k == 0 else (0.150, 8)
        locks.append(([(180 + 0.6 * (az - 180), 78, 0.98), (az, 52, 1.0), (az + 0.5 * sw, 30, 1.01), (az + sw, tip, 1.06)], wide, 0.201))
    for k in range(-2, 2):                                   # crown whorl: locks curl round a point behind the apex
        az = 180 + (k + 0.5) * 72
        locks.append(([(az - 40, 84, 0.97), (az - 12, 76, 1.0), (az + 18, 62, 1.01), (az + 40, 46, 1.05)], 0.130, 0.203))
    return locks


def build_hair(mt):
    part = Part("Hair")
    geoms = [g_cap(0.186, solid=True)]
    locks = hair_locks()
    shell = []                                               # kept as separate shingles (not remeshed) so creases survive
    for ctrl, width, radius in locks:
        ctrl = ctrl[:-1] + [(ctrl[-1][0], ctrl[-1][1], 1.10)]  # tips lift off the shell and shadow the row below
        shell.append(g_lock(ctrl, width, radius, thick=0.030, groove=0.0))
    front = [  # (ctrl, width, radius, taper): swept from the part above the left brow
        ([(25, 52, 0.97), (60, 74, 1.0), (120, 78, 1.0), (165, 62, 1.01)], 0.125, 0.198, 2.6),      # over the top
        ([(10, 56, 0.97), (-40, 76, 1.0), (-110, 78, 1.0), (-160, 62, 1.01)], 0.125, 0.198, 2.6),
        ([(-10, 66, 1.0), (-45, 58, 1.06), (-75, 44, 1.10), (-90, 30, 1.08)], 0.110, 0.198, 2.2),   # crest on the right
        ([(-82, 30, 0.99), (-78, 8, 1.0), (-70, -8, 1.0), (-64, -19, 1.0)], 0.070, 0.194, 2.6),    # sideburns
        ([(84, 30, 0.99), (80, 8, 1.0), (72, -8, 1.0), (64, -18, 1.0)], 0.070, 0.194, 2.6),
        ([(-40, 40, 0.97), (-66, 22, 1.0), (-78, 4, 1.01), (-74, -12, 1.03)], 0.115, 0.196, 2.0),   # temples
        ([(50, 40, 0.97), (70, 22, 1.0), (80, 4, 1.01), (76, -12, 1.03)], 0.115, 0.196, 2.0),
        ([(14, 50, 0.97), (-30, 44, 1.0), (-66, 26, 1.02), (-90, 4, 1.08), (-102, -6, 1.30)], 0.130, 0.198, 1.6),
        ([(8, 60, 0.97), (-35, 56, 1.0), (-68, 36, 1.01), (-92, 17, 1.05), (-104, 9, 1.31)], 0.135, 0.200, 1.6),
        ([(42, 48, 0.97), (66, 38, 1.0), (86, 20, 1.02), (92, 4, 1.08), (102, -4, 1.29)], 0.130, 0.198, 1.6),
        ([(40, 58, 0.97), (64, 52, 1.0), (82, 35, 1.01), (92, 21, 1.05), (104, 14, 1.30)], 0.135, 0.200, 1.6),
        ([(22, 50, 0.97), (-4, 40, 1.0), (-26, 22, 1.0), (-38, -4, 1.0)], 0.140, 0.200, 2.0),      # fringe
        ([(28, 48, 0.98), (14, 36, 1.0), (-2, 18, 1.005), (-10, -8, 1.0)], 0.125, 0.202, 2.0),
        ([(31, 44, 0.99), (24, 30, 1.0), (12, 13, 1.01), (4, -5, 1.005)], 0.095, 0.204, 2.0),
        ([(33, 46, 0.98), (40, 32, 1.0), (42, 14, 1.0), (37, -8, 1.0)], 0.110, 0.202, 2.0),
    ]
    for i, (ctrl, width, radius, taper) in enumerate(front):
        geoms.append(g_lock(ctrl, width, radius, taper=taper, root=0.72, tip=0.06, groove=0.0))
    tufts = [
        ([(0.052, -0.004, 0.905), (0.046, -0.008, 0.940), (0.026, -0.011, 0.968), (-0.004, -0.012, 0.986),
          (-0.030, -0.012, 0.986)], (0, 0, 1), 0.052, 0.030),
        ([(0.0, 0.03, 0.915), (-0.004, 0.050, 0.940), (-0.008, 0.068, 0.950), (-0.012, 0.086, 0.944)],
         (0, 0, 1), 0.056, 0.030),
    ]
    for ctrl, hint, width, thick in tufts:
        pts = path3(ctrl, 14)
        geoms.append(g_leaf(pts, [hint] * len(pts), width, thick, belly=0.85, root=0.85, taper=1.4, tip=0.07, groove=0.0))
    part.add(fuse(geoms, 0.0026, 4, 0.2), mt["hair"])
    for g in shell:
        part.add(g, mt["hair"])
    return part


# ----------------------------------------------------------------- body
TORSO = curve([  # z, half width, half depth, centre y
    (0.296, 0.110, 0.085, -0.010), (0.312, 0.117, 0.090, -0.010), (0.335, 0.119, 0.092, -0.011),
    (0.360, 0.123, 0.096, -0.012), (0.400, 0.123, 0.097, -0.013), (0.450, 0.117, 0.092, -0.010),
    (0.500, 0.106, 0.083, -0.004), (0.535, 0.090, 0.071, 0.000), (0.556, 0.068, 0.058, 0.002),
    (0.572, 0.050, 0.047, 0.004)])
TORSO_E = 2.3


def torso_ring(z, n=48, grow=0.0, rib=0.0):
    rx, ry, cy = TORSO(z)
    return ring(z, rx + grow, ry + grow, 0.0, cy, n, TORSO_E, rib)


def collar_path(n=48):
    pts, nor, rad = [], [], []
    for k in range(n):
        t = TAU * k / n
        d = min(t, TAU - t)                                  # angle from the front
        z = 0.551 + 0.008 * (1 - m.cos(t)) / 2 - 0.046 * m.exp(-(d / 0.50) ** 2)
        pts.append(Vector((0.077 * m.sin(t), 0.004 - 0.067 * m.cos(t), z)))
        nor.append(Vector((m.sin(t), -m.cos(t), 0.0)))
        rad.append((0.026 + 0.007 * (1 - m.cos(t)) / 2) * (1 - 0.34 * m.exp(-(d / 0.3) ** 2)))
    return pts, nor, rad


def build_hoodie(mt):
    part = Part("Hoodie")
    body = g_loft([torso_ring(lerp(0.300, 0.572, i / 30)) for i in range(31)])
    part.add(body, mt["blue"])
    bvh = bvh_of(body)
    band = []
    for i in range(7):
        t = i / 6
        band.append(torso_ring(lerp(0.295, 0.338, t), 96, 0.003 + 0.0028 * m.sin(m.pi * t), 0.009 * m.sin(m.pi * t)))
    part.add(g_loft(band), mt["rib"])
    for s in (-1, 1):                                        # sleeves with ribbed cuffs
        a, b = Vector((s * 0.066, 0.004, 0.502)), Vector((s * 0.1215, 0.006, 0.439))
        rad = curve([(0.0, 0.047), (0.45, 0.046), (0.84, 0.0405), (1.0, 0.0395)])
        ts = [i / 10 * 0.86 for i in range(11)]
        part.add(g_tube([a.lerp(b, t) for t in ts], [rad(t)[0] for t in ts], 20, 1.06, hint=Y, cap=True), mt["blue"])
        cuff = [0.84, 0.88, 0.94, 0.985, 1.0]
        grow = [0.0005, 0.0026, 0.003, 0.002, -0.004]
        part.add(g_sweep([a.lerp(b, t) for t in cuff],
                         lambda i: [(r * (1 + (0.02 if k % 2 else -0.02)) * m.cos(TAU * k / 40),
                                     1.06 * r * (1 + (0.02 if k % 2 else -0.02)) * m.sin(TAU * k / 40))
                                    for k in range(40) for r in [rad(cuff[i])[0] + grow[i]]], hint=Y), mt["rib"])

    def hood(u, v):                                          # hood resting on the back
        cu, su, a = m.cos(m.pi * u), m.sin(m.pi * u), TAU * v
        t = (cu + 1) / 2                                     # 0 bottom tip, 1 top
        k = sp(su, 0.3) if cu > 0 else su                    # broad top edge, rounded point below
        wide = 0.012 + 0.096 * sstep(0.0, 0.62, t) ** 0.8
        deep = 0.056 * (0.55 + 0.45 * m.sin(m.pi * t ** 0.8) ** 0.7)
        return Vector((wide * k * m.cos(a), 0.082 + deep * k * m.sin(a), 0.502 + 0.070 * sp(cu, 0.9)))
    hood_geom = g_param(hood, 20, 32)
    part.add(hood_geom, mt["blue"])
    back = Projector(bvh_of(hood_geom), direction=-Y)
    part.add(back.strip([(0.0, lerp(0.562, 0.440, i / 12)) for i in range(13)], [0.0036] * 13, 0.0012), mt["seam"],
             outward=back.facing)
    pts, nor, rad = collar_path()
    part.add(g_sweep(pts, lambda i: circle(rad[i], 12), normals=nor, closed=True), mt["blue"])
    pr = Projector(bvh)
    part.add(pr.decal(dense([(-0.042, 0.558), (0.042, 0.558), (0.0, 0.500)], 8), 0.0015, 4), mt["tee"], outward=pr.facing)
    pocket = [(0.072, 0.343), (0.068, 0.362), (0.057, 0.387), (0.046, 0.407), (-0.046, 0.407), (-0.057, 0.387),
              (-0.068, 0.362), (-0.072, 0.343)]
    part.add(pr.decal(dense(pocket, 4), 0.0032, 5), mt["blue"], outward=pr.facing)
    for s in (-1, 1):
        side = [(s * p[0], p[1]) for p in pocket[:4]]
        f = spline(side)
        line = [f(i / 10) for i in range(11)]
        part.add(pr.strip(line, [0.0042] * 11, 0.0042), mt["seam"], outward=pr.facing)
    part.add(pr.strip([(-0.046 + 0.0092 * i, 0.407) for i in range(11)], [0.0042] * 11, 0.0042), mt["seam"],
             outward=pr.facing)
    for s in (-1, 1):                                        # drawstrings with aglets
        line = [pr.drop(s * lerp(0.036, 0.041, i / 10), lerp(0.522, 0.437, i / 10), 0.0045) for i in range(11)]
        part.add(g_tube(line, [0.0036] * 11, 8), mt["cord"])
        part.add(g_tube(line[8:], [0.0056] * 3, 10), mt["cord"])
    return part, bvh


def build_shorts(mt):
    part = Part("Shorts")
    top = curve([(0.250, 0.126, 0.080), (0.270, 0.1275, 0.0815), (0.292, 0.116, 0.080), (0.310, 0.105, 0.077),
                 (0.345, 0.098, 0.075)])
    body = g_loft([ring(z, *top(z), 0.0, 0.0, 40, 2.5) for z in [lerp(0.250, 0.345, i / 8) for i in range(9)]])
    part.add(body, mt["navy"])
    pr = Projector(bvh_of(body))
    part.add(pr.strip([(0.0, lerp(0.300, 0.268, i / 6)) for i in range(7)], [0.0032] * 7, 0.0012), mt["stitch"],
             outward=pr.facing)
    for s in (-1, 1):                                        # pocket openings
        f = spline([(s * 0.070, 0.300), (s * 0.090, 0.290), (s * 0.108, 0.276), (s * 0.118, 0.266)])
        part.add(pr.strip([f(i / 8) for i in range(9)], [0.0030] * 9, 0.0012), mt["stitch"], outward=pr.facing)
    for s in (-1, 1):
        legs = ((0.207, 0.0655, 0.0830), (0.240, 0.0655, 0.0830), (0.262, 0.0630, 0.0810), (0.276, 0.0570, 0.0750))
        part.add(g_loft([ring(z, rx, ry, s * 0.0665, 0.0, 32, 2.4) for z, rx, ry in legs]), mt["navy"])   # buried tops
        rolls = [(0.2030, -0.0030), (0.2060, 0.0030), (0.2210, 0.0042), (0.2340, 0.0034), (0.2385, -0.0020)]
        part.add(g_loft([ring(z, 0.0655 + g, 0.083 + g, s * 0.0665, 0.0, 32, 2.4) for z, g in rolls]), mt["cuff"])
    return part


def build_limbs(mt, s):
    side = "L" if s > 0 else "R"
    arm = Part("Arm." + side)
    ctrl = [(s * 0.095, 0.006, 0.470), (s * 0.135, 0.004, 0.410), (s * 0.168, 0.0, 0.352), (s * 0.177, -0.003, 0.322)]
    pts = path3(ctrl, 12)
    rad = curve([(0.0, 0.035), (0.5, 0.036), (0.85, 0.0325), (1.0, 0.031)])
    arm.add(g_tube(pts, [rad(i / 12)[0] for i in range(13)], 16, hint=Y), mt["skin"])
    tilt = Matrix.Rotation(m.radians(-s * 10), 3, "Y")
    hand = Vector((s * 0.1815, -0.004, 0.302))
    arm.add(g_ellipsoid(hand, (0.030, 0.037, 0.040), tilt, 14, 20, 0.82, 0.82), mt["skin"])            # palm
    curl = tilt @ Matrix.Rotation(m.radians(s * 22), 3, "Y")
    for k in range(4):                                       # fingers curled towards the thigh
        base = hand + tilt @ Vector((s * 0.010, -0.0285 + 0.019 * k, -0.026))
        arm.add(g_ellipsoid(base + curl @ Vector((0.0, 0.0, -0.008)), (0.0125, 0.0108, 0.0215), curl, 10, 12), mt["skin"])
    thumb = tilt @ Matrix.Rotation(m.radians(-24), 3, "X")
    arm.add(g_ellipsoid(hand + tilt @ Vector((-s * 0.006, -0.040, -0.008)), (0.0125, 0.0125, 0.026), thumb, 10, 12),
            mt["skin"])
    leg = Part("Leg." + side)
    cx, cy = s * 0.068, 0.006
    leg.add(g_loft([ring(z, r, r * 1.16, cx, cy, 24) for z, r in ((0.10, 0.040), (0.16, 0.042), (0.225, 0.043))]),
            mt["skin"])
    sock = [(0.060, 0.042), (0.110, 0.0435), (0.127, 0.0445), (0.1325, 0.0438), (0.1345, 0.0410)]
    leg.add(g_loft([ring(z, r, r * 1.14, cx, cy, 24) for z, r in sock]), mt["sock"])
    return arm, leg, pts


def build_shoe(mt, s):
    part = Part("Shoe." + ("L" if s > 0 else "R"))
    yaw = rot_z(s * 8)
    ankle = Vector((s * 0.070, 0.006, 0.0))
    origin = ankle + yaw @ Vector((0.0, -0.040, 0.0))        # shoe centre on the ground

    def world(f, l, z):                                      # f forward, l to the character's left
        return origin + yaw @ Vector((l, -f, z))

    def sole_ring(z, k, n=44):
        out = []
        for j in range(n):
            a = TAU * j / n
            f = 0.108 * sp(m.cos(a), 2 / 2.7)
            out.append(world(f * k, (0.0625 + 0.004 * f / 0.108) * k * sp(m.sin(a), 2 / 2.7), z))
        return out
    part.add(g_loft([sole_ring(z, k) for z, k in ((0.0, 0.95), (0.005, 1.0), (0.029, 1.0), (0.034, 0.965))]),
             mt["rubber"])
    high = curve([(-0.100, 0.066), (-0.060, 0.073), (-0.020, 0.071), (0.020, 0.057), (0.050, 0.044), (0.080, 0.035),
                  (0.100, 0.031)])
    wide = curve([(-0.100, 0.053), (-0.020, 0.056), (0.060, 0.058), (0.100, 0.056)])

    def upper(u, v):
        f = 0.101 * sp(m.cos(m.pi * u), 0.8)
        k, a = sp(m.sin(m.pi * u), 0.62 if u < 0.5 else 0.42), TAU * v
        sa = m.sin(a)
        z = 0.030 + (high(f)[0] * k * sp(sa, 0.55) if sa > 0 else 0.014 * k * sa)
        return world(f, wide(f)[0] * k * sp(m.cos(a), 0.55), z)
    geom = g_param(upper, 22, 32)
    toe_line = (origin + yaw @ Vector((0.0, -0.047, 0.0)))
    fwd = yaw @ Vector((0.0, -1.0, 0.0))
    part.add(geom, lambda c: mt["rubber"] if (c - toe_line).dot(fwd) > 0 else mt["shoe"])
    bvh = bvh_of(geom)
    top = Projector(bvh, direction=-Z, e1=yaw @ X, e2=fwd, origin=origin + Z * 0.5)
    for f in (0.034, 0.016, -0.002):                         # laces hugging the instep
        line = [top.drop(0.034 * (k / 5 - 1), f, 0.0028) for k in range(11)]
        part.add(g_tube(line, [0.0046] * 11, 8, hint=Z), mt["rubber"])
    part.add(g_ellipsoid(world(-0.004, 0.0, 0.103), (0.032, 0.020, 0.020), yaw, 10, 16, 0.8, 0.8), mt["shoe"])  # tongue
    pts, nor, rad = [], [], []
    for k in range(28):                                      # padded collar
        t = TAU * k / 28
        pts.append(world(-0.046 + 0.040 * m.cos(t), 0.040 * m.sin(t), 0.094 + 0.007 * m.cos(t)))
        nor.append(yaw @ Vector((m.sin(t), -m.cos(t), 0.0)))
        rad.append(0.0105)
    part.add(g_sweep(pts, lambda i: circle(rad[i], 10), normals=nor, closed=True), mt["shoe"])
    for sign in (-1, 1):                                     # side stripes
        pr = Projector(bvh, direction=yaw @ Vector((-sign, 0, 0)), e1=fwd, e2=Z, origin=origin)
        for shift in (0.012, -0.026):
            bar = [(shift + 0.012, 0.068), (shift - 0.010, 0.068), (shift - 0.026, 0.044), (shift - 0.004, 0.044)]
            part.add(pr.decal(dense(bar, 5), 0.0016, 4), mt["rubber"], outward=pr.facing)
    return part


def build_bag(mt, torso_bvh):
    part = Part("Bag")
    centre = Vector((-0.093, -0.121, 0.336))
    rm = rot_z(20) @ Matrix.Rotation(m.radians(-9), 3, "Y")   # yaw to the front right, slight roll

    def loc(x, y, z):
        return centre + rm @ Vector((x, y, z))
    part.add(g_ellipsoid(centre, (0.062, 0.027, 0.066), rm, 16, 28, 0.32, 0.32), mt["bag"])
    part.add(g_ellipsoid(loc(0, -0.0255, 0.026), (0.0645, 0.0080, 0.042), rm, 14, 24, 0.42, 0.36), mt["bag"])
    part.add(g_ellipsoid(loc(0, -0.002, 0.064), (0.0645, 0.0295, 0.0078), rm, 12, 24, 0.5, 0.34), mt["bag"])
    part.add(g_ellipsoid(loc(0, -0.0345, -0.004), (0.0085, 0.0040, 0.022), rm, 8, 12, 0.5, 0.5), mt["bag2"])
    part.add(g_ellipsoid(loc(0, -0.0375, -0.013), (0.0125, 0.0036, 0.0085), rm, 8, 12, 0.4, 0.4), mt["bag2"])
    for sx in (-1, 1):
        part.add(g_ellipsoid(loc(sx * 0.056, 0.004, 0.060), (0.011, 0.0065, 0.017), rm, 8, 12, 0.45, 0.45), mt["bag2"])
    ctrl = [loc(0.056, 0.004, 0.070), (-0.02, -0.110, 0.418), (0.012, -0.102, 0.463), (0.042, -0.086, 0.506),
            (0.066, -0.040, 0.546), (0.070, 0.0, 0.554), (0.062, 0.04, 0.536), (0.036, 0.075, 0.480),
            (0.0, 0.086, 0.438), (-0.060, 0.076, 0.390), (-0.106, 0.040, 0.362), (-0.130, -0.020, 0.366),
            loc(-0.056, 0.004, 0.070)]
    raw = path3([tuple(p) for p in ctrl], 96)
    pts, nor = [], []
    for i, p in enumerate(raw):
        t = i / 96
        near, n, _, _ = torso_bvh.find_nearest(p)
        axis = Vector((0.0, TORSO(near.z)[2], near.z))
        if n.dot(near - axis) < 0:
            n = -n
        w = sstep(0.0, 0.14, t) * sstep(1.0, 0.86, t)
        pts.append(p.lerp(near + n * 0.0045, w))
        nor.append(n.lerp((p - axis).normalized(), 1 - w))
    half, th = 0.0095, 0.0024
    band = [(-half, -th), (-half, th), (-half * 0.5, th * 1.25), (half * 0.5, th * 1.25), (half, th), (half, -th)]
    part.add(g_sweep(pts, lambda i: band, normals=nor), mt["strap"])
    return part


def build_watch(mt, arm_pts):
    part = Part("Watch")
    c, axis = arm_pts[9], (arm_pts[10] - arm_pts[8]).normalized()
    out = (X - axis * axis.x).normalized()
    side = axis.cross(out)
    prof = [(-0.0100, 0.030), (-0.0080, 0.0372), (0.0080, 0.0372), (0.0100, 0.030)]
    part.add(g_loft([[c + axis * d + (out * m.cos(TAU * k / 24) + side * m.sin(TAU * k / 24)) * r for k in range(24)]
                     for d, r in prof]), mt["watch"])
    rm = Matrix((side, out, axis)).transposed()               # local x side, y outward, z along the arm
    part.add(g_ellipsoid(c + out * 0.0370, (0.0175, 0.0062, 0.0195), rm, 12, 20, 0.4, 0.4), mt["watch"])
    part.add(g_ellipsoid(c + out * 0.0408, (0.0138, 0.0032, 0.0158), rm, 10, 16, 0.4, 0.4), mt["screen"])
    return part


# ---------------------------------------------------------------- scene
def reset_scene():
    sc = bpy.data.scenes.get(SCENE) or bpy.data.scenes.new(SCENE)
    for ob in list(sc.collection.all_objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for c in list(sc.collection.children_recursive):
        bpy.data.collections.remove(c)
    for block in (bpy.data.meshes, bpy.data.cameras, bpy.data.lights, bpy.data.materials, bpy.data.images):
        for d in list(block):
            if d.get(TAG) and d.users == 0:
                block.remove(d)
    return sc


def build_studio(sc, coll):
    world = bpy.data.worlds.get(SCENE) or bpy.data.worlds.new(SCENE)
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    out, mix, path = (nt.nodes.new(t) for t in ("ShaderNodeOutputWorld", "ShaderNodeMixShader", "ShaderNodeLightPath"))
    ambient, backdrop = nt.nodes.new("ShaderNodeBackground"), nt.nodes.new("ShaderNodeBackground")
    ambient.inputs["Color"].default_value = (*lin("F2F2FA"), 1)
    ambient.inputs["Strength"].default_value = 0.70
    backdrop.inputs["Color"].default_value = (*lin("EBEAF7"), 1)
    nt.links.new(path.outputs["Is Camera Ray"], mix.inputs[0])
    nt.links.new(ambient.outputs[0], mix.inputs[1])
    nt.links.new(backdrop.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    sc.world = world

    def light(name, loc, energy, size, colour=(1, 1, 1)):
        data = bpy.data.lights.new(name, "AREA")
        data[TAG] = 1
        data.energy, data.size, data.color = energy, size, colour
        ob = bpy.data.objects.new(name, data)
        ob.location = loc
        ob.rotation_euler = (Vector((0, 0, 0.55)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        coll.objects.link(ob)
    light("Key", (-1.3, -2.2, 2.3), 80, 2.2, (1.0, 0.97, 0.94))
    light("Fill", (2.0, -1.6, 1.0), 30, 2.5, (0.93, 0.95, 1.0))
    light("Rim", (0.8, 2.2, 2.0), 45, 2.0)
    cam = bpy.data.cameras.new("Camera")
    cam[TAG] = 1
    ob = bpy.data.objects.new("Camera", cam)
    coll.objects.link(ob)
    sc.camera = ob
    sc.render.engine = "BLENDER_EEVEE"
    try:                                                     # soft contact shading for the previews
        sc.eevee.use_raytracing = True
        sc.eevee.ray_tracing_method = "SCREEN"
        sc.eevee.ray_tracing_options.resolution_scale = "1"
        sc.eevee.fast_gi_resolution = "1"
        sc.eevee.shadow_ray_count, sc.eevee.shadow_step_count = 3, 6
    except (AttributeError, TypeError):
        pass
    sc.view_settings.view_transform = "Standard"
    sc.render.image_settings.file_format = "PNG"
    return ob


def aim_camera(sc, azimuth, centre=(0, 0, 0.495), ortho=1.054, distance=4.0, lens=None):
    """azimuth 0 looks at the front, 90 at the character's left side."""
    cam, a = sc.camera, m.radians(azimuth)
    target = Vector(centre)
    cam.location = target + Vector((m.sin(a), -m.cos(a), 0.0)) * distance
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    if lens:
        cam.data.type, cam.data.lens = "PERSP", lens
    else:
        cam.data.type, cam.data.ortho_scale = "ORTHO", ortho


def build():
    sc = reset_scene()
    model = bpy.data.collections.new("CV4 Model")
    studio = bpy.data.collections.new("CV4 Studio")
    sc.collection.children.link(model)
    sc.collection.children.link(studio)
    root = bpy.data.objects.new("ChibiVisitorV4", None)
    root[TAG] = 1
    root.empty_display_size = 0.1
    model.objects.link(root)
    mt = materials()
    hoodie, torso_bvh = build_hoodie(mt)
    parts = [build_head(mt), build_hair(mt), hoodie, build_shorts(mt)]
    for s in (1, -1):
        arm, leg, arm_pts = build_limbs(mt, s)
        parts += [arm, leg, build_shoe(mt, s)]
        if s > 0:
            parts.append(build_watch(mt, arm_pts))
    parts.append(build_bag(mt, torso_bvh))
    objs = [p.build(model, root) for p in parts]
    build_studio(sc, studio)
    if bpy.context.window:
        bpy.context.window.scene = sc
    tris = sum(len(f) - 2 for p in parts for f in p.f)
    lo = [min(v[i] for p in parts for v in p.v) for i in range(3)]
    hi = [max(v[i] for p in parts for v in p.v) for i in range(3)]
    return {"objects": [o.name for o in objs], "triangles": tris,
            "min": [round(q, 4) for q in lo], "max": [round(q, 4) for q in hi]}


VIEWS = {"front": 0, "side": 90, "back": 180, "three-quarter": 32}


def write_outputs(out=None):
    """Save the editable source, the GLB and the orthographic previews (CV4_OUT overrides the folder)."""
    out = out or os.environ.get("CV4_OUT", HERE)
    sc = bpy.data.scenes[SCENE]
    for sub in ("sources", "exports", "previews"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, "sources", "chibi-visitor-v4.blend"), copy=True, compress=True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, "exports", "chibi-visitor-v4.glb"), export_format="GLB",
                              collection="CV4 Model", export_yup=True, export_apply=True,
                              export_vertex_color="MATERIAL", export_animations=False)
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 740, 1360, 100
    for name, azimuth in VIEWS.items():
        aim_camera(sc, azimuth, (0, 0.028 if name == "side" else 0.0, 0.4946), 680 / 645)
        sc.render.filepath = os.path.join(out, "previews", name + ".png")
        bpy.ops.render.render(write_still=True, scene=sc.name)
    return {"written": ["sources/chibi-visitor-v4.blend", "exports/chibi-visitor-v4.glb"] + ["previews/%s.png" % n for n in VIEWS]}


if __name__ == "__main__":
    RESULT = build()
    if bpy.app.background or os.environ.get("CV4_WRITE") == "1":
        RESULT.update(write_outputs())
    print("CV4", RESULT)
