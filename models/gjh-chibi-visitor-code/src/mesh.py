"""Mesh building toolkit written for this character.

Geometry is collected in `Part` objects (vertices, faces, per-corner UVs and a
per-vertex skin tag). Parts that share a material are merged into one Blender
object by `make_object`, which keeps the draw-call count low.

Winding rule used everywhere: a ring is counter-clockwise around the loft
direction (right-hand rule) and quads are (a_i, a_i+1, b_i+1, b_i), which
gives outward normals without a recalculation step.
"""
import math

import bpy
from mathutils import Vector


class Part:
    def __init__(self, name, material):
        self.name = name
        self.material = material
        self.verts = []
        self.tags = []
        self.faces = []
        self.uvs = []

    def vert(self, co, tag):
        self.verts.append(Vector(co))
        self.tags.append(tag)
        return len(self.verts) - 1

    def face(self, indices, uv=None):
        self.faces.append(tuple(indices))
        self.uvs.append(uv if uv is not None else [(0.0, 0.0)] * len(indices))

    def triangles(self):
        return sum(len(f) - 2 for f in self.faces)


# ------------------------------------------------------------------ rings
def frame_from(direction, hint=(0.0, 0.0, 1.0)):
    """Right-handed frame (x, y, d) with d along direction."""
    d = Vector(direction).normalized()
    h = Vector(hint)
    if abs(d.dot(h.normalized())) > 0.95:
        h = Vector((1.0, 0.0, 0.0)) if abs(d.x) < 0.9 else Vector((0.0, 1.0, 0.0))
    x = h.cross(d).normalized()
    y = d.cross(x).normalized()
    return x, y, d


def superellipse(angle, rx, ry, power):
    c, s = math.cos(angle), math.sin(angle)
    e = 2.0 / power
    return (rx * math.copysign(abs(c) ** e, c), ry * math.copysign(abs(s) ** e, s))


def ring(center, frame, rx, ry, count, power=2.0, phase=0.0, shift=(0.0, 0.0)):
    """Closed loop of `count` points, counter-clockwise around frame d."""
    x_axis, y_axis, _ = frame
    c = Vector(center)
    points = []
    for i in range(count):
        a = phase + 2.0 * math.pi * i / count
        u, v = superellipse(a, rx, ry, power)
        points.append(c + x_axis * (u + shift[0]) + y_axis * (v + shift[1]))
    return points


def dome(center, frame, rx, ry, count, length, steps, power=2.0, phase=0.0, tip_shift=(0.0, 0.0),
         sign=1.0):
    """Rings that close a tube end as a rounded cap, plus the tip point.

    Rings keep the frame's orientation; sign=-1 grows the dome backwards (for
    the start of a loft). Rings are ordered from the base towards the tip.
    """
    _, _, d = frame
    rings = []
    for k in range(1, steps + 1):
        t = k / (steps + 1)
        theta = t * math.pi / 2.0
        scale = math.cos(theta)
        offset = length * math.sin(theta) * sign
        shift = (tip_shift[0] * t, tip_shift[1] * t)
        rings.append(ring(Vector(center) + d * offset, frame, rx * scale, ry * scale, count, power, phase, shift))
    tip = Vector(center) + d * length * sign + frame[0] * tip_shift[0] + frame[1] * tip_shift[1]
    return rings, tip


# ------------------------------------------------------------------ lofts
def loft(part, rings, tag, cap_start=None, cap_end=None, v_range=(0.0, 1.0), u_range=(0.0, 1.0),
         closed=True):
    """Join rings with quads. cap_start/cap_end: None (open), 'flat', or a tip Vector.

    `tag` is a string or a callable(Vector) -> str for skin tags.
    Returns the vertex index rows.
    """
    tag_of = tag if callable(tag) else (lambda _co: tag)
    rows = []
    for r in rings:
        rows.append([part.vert(co, tag_of(co)) for co in r])
    count = len(rings[0])
    span = count if closed else count - 1
    n_rows = len(rows)
    for k in range(n_rows - 1):
        v0 = v_range[0] + (v_range[1] - v_range[0]) * k / (n_rows - 1)
        v1 = v_range[0] + (v_range[1] - v_range[0]) * (k + 1) / (n_rows - 1)
        for i in range(span):
            j = (i + 1) % count
            u0 = u_range[0] + (u_range[1] - u_range[0]) * i / span
            u1 = u_range[0] + (u_range[1] - u_range[0]) * (i + 1) / span
            part.face((rows[k][i], rows[k][j], rows[k + 1][j], rows[k + 1][i]),
                      [(u0, v0), (u1, v0), (u1, v1), (u0, v1)])
    if closed:
        _cap(part, rows[0], rings[0], cap_start, tag_of, start=True, v=v_range[0])
        _cap(part, rows[-1], rings[-1], cap_end, tag_of, start=False, v=v_range[1])
    return rows


def _cap(part, row, points, cap, tag_of, start, v):
    if cap is None:
        return
    if cap == "flat":
        center = sum(points, Vector()) / len(points)
    else:
        center = Vector(cap)
    c = part.vert(center, tag_of(center))
    count = len(row)
    for i in range(count):
        j = (i + 1) % count
        if start:
            part.face((c, row[j], row[i]), [(0.5, v), (0.5, v), (0.5, v)])
        else:
            part.face((c, row[i], row[j]), [(0.5, v), (0.5, v), (0.5, v)])


# ------------------------------------------------------------------ sweeps
def catmull(points, samples):
    """Catmull-Rom spline through points, `samples` points total."""
    pts = [Vector(p) for p in points]
    ext = [pts[0] * 2 - pts[1]] + pts + [pts[-1] * 2 - pts[-2]]
    out = []
    segments = len(pts) - 1
    for s in range(samples):
        t = s / (samples - 1) * segments
        i = min(int(t), segments - 1)
        f = t - i
        p0, p1, p2, p3 = ext[i], ext[i + 1], ext[i + 2], ext[i + 3]
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f * f
                          + (-p0 + 3 * p1 - 3 * p2 + p3) * f * f * f))
    return out


def transport_frames(spine, hint):
    """Parallel-transport frames along a polyline (x, y, tangent)."""
    tangents = []
    for i in range(len(spine)):
        a = spine[max(i - 1, 0)]
        b = spine[min(i + 1, len(spine) - 1)]
        tangents.append((b - a).normalized())
    frames = [frame_from(tangents[0], hint)]
    for i in range(1, len(spine)):
        x_prev, _, t_prev = frames[-1]
        t = tangents[i]
        rot = t_prev.rotation_difference(t)
        x = (rot @ x_prev)
        x = (x - t * x.dot(t)).normalized()
        frames.append((x, t.cross(x).normalized(), t))
    return frames


def sweep(part, spine, radii, tag, count, power=2.0, hint=(0.0, 0.0, 1.0), cap_start="flat",
          cap_end="flat", dome_end=None, dome_start=None, v_range=(0.0, 1.0)):
    """Tube along `spine` (list of Vectors) with radii [(rx, ry), ...] per point.

    dome_start / dome_end: (length, steps) to close that end with a rounded cap.
    """
    frames = transport_frames(spine, hint)
    rings = [ring(p, f, rx, ry, count, power) for p, f, (rx, ry) in zip(spine, frames, radii)]
    start_tip = cap_start
    end_tip = cap_end
    if dome_start:
        rx, ry = radii[0]
        extra, tip = dome(spine[0], frames[0], rx, ry, count, dome_start[0], dome_start[1], power, sign=-1.0)
        rings = list(reversed(extra)) + rings
        start_tip = tip
    if dome_end:
        rx, ry = radii[-1]
        extra, tip = dome(spine[-1], frames[-1], rx, ry, count, dome_end[0], dome_end[1], power)
        rings = rings + extra
        end_tip = tip
    return loft(part, rings, tag, cap_start=start_tip, cap_end=end_tip, v_range=v_range)


def sweep_on_surface(part, spine, normals, radii, tag, count, power=2.0, cap_start="flat", cap_end="flat",
                     v_range=(0.0, 1.0), phase=0.0):
    """Tube whose section's y axis follows the given surface normals, so a flat
    section (strap, lock) lies flat on the surface it follows."""
    rings = []
    for i, p in enumerate(spine):
        a = spine[max(i - 1, 0)]
        b = spine[min(i + 1, len(spine) - 1)]
        d = (b - a).normalized()
        x = Vector(normals[i]).cross(d).normalized()
        y = d.cross(x).normalized()
        rx, ry = radii[i]
        rings.append(ring(p, (x, y, d), rx, ry, count, power, phase))
    return loft(part, rings, tag, cap_start=cap_start, cap_end=cap_end, v_range=v_range)


def box_project_uvs(part, tile, keep=None):
    """Replace face UVs with a box projection in metres / tile, choosing the
    plane from each face's dominant normal axis. Faces where keep(uv) is true
    keep their UVs. Keeps the weave continuous across separately built tubes."""
    for k, face in enumerate(part.faces):
        if keep and keep(part.uvs[k]):
            continue
        pts = [part.verts[i] for i in face]
        n = (pts[1] - pts[0]).cross(pts[2] - pts[0])
        ax = max(range(3), key=lambda a: abs(n[a]))
        if ax == 0:
            part.uvs[k] = [(p.y / tile, p.z / tile) for p in pts]
        elif ax == 1:
            part.uvs[k] = [(p.x / tile, p.z / tile) for p in pts]
        else:
            part.uvs[k] = [(p.x / tile, p.y / tile) for p in pts]


# ------------------------------------------------------------------ objects
def make_object(name, parts, collection):
    """Merge parts into one mesh object; tags become a 'skin_tag' string list."""
    verts, faces, uvs, tags, materials = [], [], [], [], []
    for part in parts:
        base = len(verts)
        verts.extend(part.verts)
        tags.extend(part.tags)
        for f, uv in zip(part.faces, part.uvs):
            faces.append(tuple(i + base for i in f))
            uvs.append(uv)
            materials.append(part.material)
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([tuple(v) for v in verts], [], faces)
    uv_layer = mesh.uv_layers.new(name="UVMap")
    loop = 0
    for poly, uv in zip(mesh.polygons, uvs):
        for k in range(poly.loop_total):
            uv_layer.data[poly.loop_start + k].uv = uv[k]
        loop += poly.loop_total
    unique = []
    for m in materials:
        if m not in unique:
            unique.append(m)
    for m in unique:
        mesh.materials.append(m)
    for poly, m in zip(mesh.polygons, materials):
        poly.material_index = unique.index(m)
    mesh.validate(clean_customdata=False)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj["skin_tags"] = tags
    return obj


def shade(obj, angle_deg=60.0):
    mesh = obj.data
    mesh.shade_smooth()
    mesh.set_sharp_from_angle(angle=math.radians(angle_deg))


def signed_volume(part):
    """Signed volume of a part's faces (positive when they face outwards)."""
    volume = 0.0
    for face in part.faces:
        p0 = part.verts[face[0]]
        for i in range(1, len(face) - 1):
            volume += p0.dot(part.verts[face[i]].cross(part.verts[face[i + 1]])) / 6.0
    return volume


def triangle_count(obj):
    return sum(len(p.vertices) - 2 for p in obj.data.polygons)


def lerp(a, b, t):
    return a + (b - a) * t


def smoothstep(e0, e1, x):
    if e0 == e1:
        return 0.0 if x < e0 else 1.0
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3.0 - 2.0 * t)


