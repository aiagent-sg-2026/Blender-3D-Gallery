"""Backpack (body, front pocket, top handle, two shoulder straps) and the watch."""
import math

from mathutils import Vector
from mathutils.bvhtree import BVHTree

import config as C
from body import mirror
from clothes import Z_FRAME, tee_section
from mesh import Part, catmull, dome, frame_from, loft, ring, sweep, sweep_on_surface


def build_backpack(materials, torso):
    pack = Part("Backpack", materials["backpack"])
    cx, cy, cz = C.PACK_CENTER
    hw, hd, hh = C.PACK_SIZE
    n = 16
    rings = []
    bottom = cz - hh
    # Rounded box: soft bottom, straight sides, domed top.
    for z, sx, sd in ((bottom, 0.86, 0.80), (bottom + 0.012, 0.97, 0.95), (bottom + 0.04, 1.0, 1.0),
                      (cz + hh * 0.45, 1.0, 1.0), (cz + hh * 0.78, 0.96, 0.96)):
        rings.append(ring((cx, cy, z), Z_FRAME, hw * sx, hd * sd, n, 3.2))
    top_rings, tip = dome((cx, cy, cz + hh * 0.78), Z_FRAME, hw * 0.96, hd * 0.96, n, hh * 0.30, 2, 3.2)
    loft(pack, rings + top_rings, "chest", cap_start="flat", cap_end=tip)

    # Front pocket on the outer (+Y) face.
    pocket = Part("Pocket", materials["backpack"])
    pw, pd, ph = C.POCKET_SIZE
    face_y = cy + hd * 0.98
    p_rings = []
    for z, s in ((C.POCKET_Z - ph, 0.80), (C.POCKET_Z - ph + 0.008, 0.97), (C.POCKET_Z + ph - 0.010, 1.0),
                 (C.POCKET_Z + ph, 0.88)):
        p_rings.append(ring((cx, face_y, z), Z_FRAME, pw * s, pd * s, 12, 3.5))
    loft(pocket, p_rings, "chest", cap_start="flat", cap_end="flat")

    # Top grab handle: a small arch.
    handle = Part("Handle", materials["backpack"])
    top_z = cz + hh * 0.78 + hh * 0.30
    arch = [Vector((cx + 0.034 * math.cos(a), cy + 0.010, top_z - 0.014 + 0.020 * math.sin(a)))
            for a in (math.pi * k / 6 for k in range(7))]
    sweep(handle, arch, [(0.009, 0.006)] * len(arch), "chest", count=6, hint=(0.0, 1.0, 0.0))

    strap = build_strap(materials, torso)
    return [pack, pocket, handle, strap, mirror(strap)]


def build_strap(materials, torso):
    """Left strap: pack top, over the shoulder, down the chest, then round the
    side between the arm and the body to the bottom corner of the pack.

    Every sample is ray-cast onto the tee torso and lifted along the hit
    normal, so the strap lies on the cloth without cutting into it.
    """
    part = Part("Strap_L", materials["backpack"])
    verts, faces = [], []
    for piece in torso:
        base = len(verts)
        verts += [tuple(v) for v in piece.verts]
        faces += [tuple(i + base for i in f) for f in piece.faces]
    tree = BVHTree.FromPolygons(verts, faces)
    # Half the section height plus clearance for the cloth curving across the strap width.
    lift = C.STRAP_THICKNESS / 2 * 1.26 + 0.006
    # (point near the surface, inward ray direction) for each control point.
    controls = []
    for x, y in ((0.072, 0.075), (0.080, 0.035), (0.086, -0.005), (0.092, -0.040)):
        controls.append((Vector((x, y, 0.80)), Vector((0.0, 0.0, -1.0))))
    for x, z in ((0.098, 0.730), (0.108, 0.690), (0.117, 0.650), (0.124, 0.615)):
        controls.append((Vector((x, -0.30, z)), Vector((0.0, 1.0, 0.0))))
    # Round the side in one gentle descending curve, always moving outwards and back.
    for deg, z in ((-32.0, 0.578), (-14.0, 0.552), (4.0, 0.532), (22.0, 0.516), (40.0, 0.503)):
        hw, yf, yb, _ = tee_section(z)
        yc = (yf + yb) / 2.0
        a = math.radians(deg)
        outward = Vector((math.cos(a), math.sin(a), 0.0))
        controls.append((Vector((0.0, yc, z)) + outward * 0.40, -outward))
    samples = 28
    origins = catmull([c[0] for c in controls], samples)
    directions = catmull([c[1] for c in controls], samples)
    spine, normals = [], []
    for origin, direction in zip(origins, directions):
        direction = direction.normalized()
        hit, normal, _, _ = tree.ray_cast(origin - direction * 0.3, direction)
        if hit is None:
            raise ValueError(f"strap sample {tuple(origin)} misses the tee")
        if normal.dot(direction) > 0:
            normal = -normal
        # Extra clearance over the shoulder, where the cloth curves across the strap.
        spine.append(hit)
        normals.append(normal)
    # The tee is faceted: smooth the hit normals before lifting the strap off it.
    for _ in range(6):
        normals = [normals[0]] + [(normals[i - 1] + normals[i] * 2 + normals[i + 1]).normalized()
                                  for i in range(1, len(normals) - 1)] + [normals[-1]]
    spine = [p + n * (lift + 0.008 * max(0.0, min(1.0, (p.z - 0.715) / 0.025))) for p, n in zip(spine, normals)]
    # Finish into the bottom corner of the pack.
    end = Vector((0.098, C.PACK_CENTER[1] - C.PACK_SIZE[1] * 0.4, C.PACK_CENTER[2] - C.PACK_SIZE[2] + 0.045))
    spine.append(spine[-1].lerp(end, 0.5))
    normals.append(normals[-1])
    spine.append(end)
    normals.append(Vector((0.7, 0.0, -0.7)).normalized())
    # Start inside the pack top.
    start = Vector((0.068, C.PACK_CENTER[1] - C.PACK_SIZE[1] * 0.2, C.PACK_CENTER[2] + C.PACK_SIZE[2] * 0.85))
    spine.insert(0, start)
    normals.insert(0, Vector((0.0, 0.0, 1.0)))
    w, t = C.STRAP_WIDTH / 2, C.STRAP_THICKNESS / 2
    # Four-sided flat section (rectangle corners at 45 degrees).
    sweep_on_surface(part, spine, normals, [(w * 1.26, t * 1.26)] * len(spine), "strap.L", count=4, power=6.0,
                     phase=math.pi / 4)
    return part


def build_watch(materials):
    part = Part("Watch", materials["watch"])
    elbow, wrist = Vector(C.ELBOW), Vector(C.WRIST)
    axis = (wrist - elbow).normalized()
    t = (C.WATCH_Z - elbow.z) / (wrist.z - elbow.z)
    center = elbow.lerp(wrist, t)
    frame = frame_from(axis, (0.0, -1.0, 0.0))
    r = C.WATCH_RADIUS
    hw = C.WATCH_WIDTH / 2
    # Band with a rectangular section: inner/outer x near/far edge, looped by
    # repeating the first ring. Inner faces point at the arm, outer ones away.
    loop = [(-hw, r - 0.004), (-hw, r + 0.002), (hw, r + 0.002), (hw, r - 0.004)]
    rings = [ring(center + axis * a, frame, rad, rad, 12) for a, rad in loop]
    rings.append(rings[0])
    loft(part, rings, "forearm.L", cap_start=None, cap_end=None)
    # Watch face: a flat rounded box on the outer-front side of the wrist.
    out_dir = Vector((0.8, -0.6, 0.0))
    out_dir = (out_dir - axis * out_dir.dot(axis)).normalized()
    x_axis = (axis - out_dir * axis.dot(out_dir)).normalized()
    face_frame = (x_axis, out_dir.cross(x_axis).normalized(), out_dir)
    fw, fl, ft = C.WATCH_FACE
    base = center + out_dir * (r - 0.001)
    f_rings = [ring(base + out_dir * dz, face_frame, fl / 2 * s, fw / 2 * s, 12, 3.5)
               for dz, s in ((0.0, 0.9), (0.003, 1.0), (ft, 1.0), (ft + 0.0015, 0.84))]
    loft(part, f_rings, "forearm.L", cap_start="flat", cap_end="flat")
    return part
