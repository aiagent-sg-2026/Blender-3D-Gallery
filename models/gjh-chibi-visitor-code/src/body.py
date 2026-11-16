"""Exposed skin below the tee: arms from inside the sleeve to the hands.

Only what can be seen is modelled; the torso and legs under the clothes are
left out, which saves triangles and removes body/cloth clipping.
The left side (+X) is built and mirrored for the right.
"""
from mathutils import Vector

import config as C
from mesh import Part, catmull, sweep, lerp


def mirror(part, name_suffix="R"):
    out = Part(part.name + "_" + name_suffix, part.material)
    out.verts = [Vector((-v.x, v.y, v.z)) for v in part.verts]
    out.tags = [swap_side(t) for t in part.tags]
    out.faces = [tuple(reversed(f)) for f in part.faces]
    out.uvs = [list(reversed(uv)) for uv in part.uvs]
    return out


def swap_side(tag):
    if tag.endswith(".L"):
        return tag[:-2] + ".R"
    if tag.endswith(".R"):
        return tag[:-2] + ".L"
    return tag


def build_arm(materials):
    """One tube from inside the sleeve to the fingertips, plus a thumb."""
    part = Part("Arm_L", materials["skin"])
    sh, el, wr, tip = (Vector(p) for p in (C.SHOULDER_JOINT, C.ELBOW, C.WRIST, C.FINGER_TIP))
    knuckle = wr.lerp(tip, 0.45)
    control = [sh.lerp(el, 0.35), el, wr, knuckle, tip]
    spine = catmull(control, 15)
    r_up, r_el, r_wr = C.ARM_RADII
    hand_t, hand_w = 0.021, 0.036
    radii = []
    for i, p in enumerate(spine):
        t = i / (len(spine) - 1)
        if t < 0.25:
            r = lerp(r_up, r_el, t / 0.25)
            radii.append((r, r))
        elif t < 0.5:
            r = lerp(r_el, r_wr, (t - 0.25) / 0.25)
            radii.append((r, r))
        elif t < 0.62:
            k = (t - 0.5) / 0.12
            radii.append((lerp(r_wr * 0.95, hand_t, k), lerp(r_wr, hand_w * 0.92, k)))
        else:
            k = (t - 0.62) / 0.38
            radii.append((lerp(hand_t, hand_t * 0.85, k), lerp(hand_w, hand_w * 0.80, k)))
    sweep(part, spine, radii, "arm.L", count=C.ARM_SEGMENTS, hint=(0.0, -1.0, 0.0),
          cap_start="flat", dome_end=(0.013, 2))

    # Thumb: a short tube on the front (-Y) side of the hand.
    base = wr + Vector(C.THUMB_BASE) - Vector((0.0, 0.0, C.WRIST[2]))
    tip_t = wr + Vector(C.THUMB_TIP) - Vector((0.0, 0.0, C.WRIST[2]))
    thumb_spine = catmull([base, base.lerp(tip_t, 0.5) + Vector((0.004, -0.004, 0.0)), tip_t], 4)
    sweep(part, thumb_spine, [(0.012, 0.012), (0.012, 0.011), (0.011, 0.010), (0.009, 0.009)], "arm.L",
          count=7, hint=(0.0, -1.0, 0.0), cap_start="flat", dome_end=(0.008, 1))
    return part
