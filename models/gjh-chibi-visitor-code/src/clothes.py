"""Tee (torso, collar, sleeves), wide cuffed jeans and chunky sneakers."""
import math

from mathutils import Vector

import config as C
from body import mirror
from mesh import Part, box_project_uvs, dome, lerp, loft, ring, sweep

Z_FRAME = (Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1)))
DOWN_FRAME = (Vector((1, 0, 0)), Vector((0, -1, 0)), Vector((0, 0, -1)))


def tee_section(z):
    """Interpolated (half width, front y, back y, power) of the tee at height z."""
    s = C.TEE_SECTIONS
    if z <= s[0][0]:
        return s[0][1:]
    for a, b in zip(s, s[1:]):
        if a[0] <= z <= b[0]:
            t = (z - a[0]) / (b[0] - a[0])
            return tuple(lerp(a[i], b[i], t) for i in range(1, 5))
    return s[-1][1:]


def tee_surface_y(x, z, back, lift=0.0):
    """y of the tee surface at (x, z) on the front (back=False) or back side."""
    hw, yf, yb, power = tee_section(z)
    yc, ry = (yf + yb) / 2.0, (yb - yf) / 2.0
    k = max(0.0, 1.0 - abs(x / hw) ** power) ** (1.0 / power)
    return yc + ry * k + lift if back else yc - ry * k - lift


def tee_ring(z, count, scale=1.0):
    hw, yf, yb, power = tee_section(z)
    center = (0.0, (yf + yb) / 2.0, z)
    return ring(center, Z_FRAME, hw * scale, (yb - yf) / 2.0 * scale, count, power, phase=-math.pi / 2)


def build_tee(materials):
    part = Part("Tee", materials["tee"])
    n = C.TEE_SEGMENTS
    hem_z = C.TEE_SECTIONS[0][0]
    # Inner hem lip gives the cloth a visible thickness from below.
    rings = [tee_ring(hem_z + 0.012, n, 0.93), tee_ring(hem_z, n, 0.985)]
    rings += [tee_ring(z, n) for z, *_ in C.TEE_SECTIONS]
    # Collar: rolled band round the neck, then down inside and closed.
    top = C.TEE_SECTIONS[-1][0]
    # A thicker rolled crew-neck rib so the collar reads from the front.
    rings.append(ring((0.0, 0.0, C.COLLAR_Z - 0.004), Z_FRAME, C.COLLAR_INNER + 0.014, C.COLLAR_INNER + 0.012, n, 2.0,
                      phase=-math.pi / 2, shift=(0.0, -0.004)))
    rings.append(ring((0.0, 0.0, C.COLLAR_Z + 0.002), Z_FRAME, C.COLLAR_INNER + 0.009, C.COLLAR_INNER + 0.008, n, 2.0,
                      phase=-math.pi / 2, shift=(0.0, -0.004)))
    rings.append(ring((0.0, 0.0, C.COLLAR_Z + 0.002), Z_FRAME, C.COLLAR_INNER, C.COLLAR_INNER * 0.96, n, 2.0,
                      phase=-math.pi / 2, shift=(0.0, -0.004)))
    rings.append(ring((0.0, 0.0, top - 0.022), Z_FRAME, C.COLLAR_INNER * 0.96, C.COLLAR_INNER * 0.92, n, 2.0,
                      phase=-math.pi / 2, shift=(0.0, -0.004)))
    loft(part, rings, "spine", cap_start=None, cap_end="flat")
    sleeve = build_sleeve(materials)
    return [part, sleeve, mirror(sleeve)]


def build_sleeve(materials):
    part = Part("Sleeve_L", materials["tee"])
    root, end = Vector(C.SLEEVE_ROOT), Vector(C.SLEEVE_END)
    axis = (end - root).normalized()
    (r0x, r0y), (r1x, r1y) = C.SLEEVE_RADII
    spine = [root - axis * 0.02, root, root.lerp(end, 0.5), end]
    radii = [(r0x * 0.9, r0y * 0.9), (r0x, r0y), (lerp(r0x, r1x, 0.5), lerp(r0y, r1y, 0.5)), (r1x, r1y)]
    # Lip: turn inwards at the opening and run back up inside the sleeve.
    spine += [end + axis * 0.002, end - axis * 0.014]
    radii += [(r1x * 0.90, r1y * 0.90), (r1x * 0.82, r1y * 0.82)]
    sweep(part, spine, radii, "arm.L", count=C.SLEEVE_SEGMENTS, hint=(0.0, -1.0, 0.0),
          cap_start="flat", cap_end=None)
    return part


# ------------------------------------------------------------------ jeans
def build_jeans(materials):
    pelvis = Part("JeansPelvis", materials["jeans"])
    hw, yf, yb = C.JEANS_HIP
    n = C.LEG_SEGMENTS + 6
    rings = []
    for z, scale in ((C.CROTCH_Z + 0.015, 0.86), (C.CROTCH_Z + 0.05, 0.95), (C.CROTCH_Z + 0.09, 1.0),
                     (C.JEANS_WAIST_Z - 0.02, 0.97), (C.JEANS_WAIST_Z, 0.92)):
        rings.append(ring((0.0, (yf + yb) / 2, z), Z_FRAME, hw * scale, (yb - yf) / 2 * scale, n, 2.6,
                          phase=-math.pi / 2))
    loft(pelvis, rings, "hips", cap_start=None, cap_end="flat", v_range=(0.55, 0.85))
    leg, cuff = build_leg(materials)
    # One continuous denim weave across pelvis and legs.
    for part in (pelvis, leg):
        box_project_uvs(part, C.DENIM_TILE_M)
    return [pelvis, leg, mirror(leg), cuff, mirror(cuff)]


def build_leg(materials):
    part = Part("Leg_L", materials["jeans"])
    n = C.LEG_SEGMENTS
    sections = [(C.CROTCH_Z + 0.07, C.LEG_SECTIONS[0][1] - 0.004, C.LEG_SECTIONS[0][2] * 0.96,
                 C.LEG_SECTIONS[0][3] * 0.96)] + list(C.LEG_SECTIONS)
    rings = [ring((x, 0.0, z), DOWN_FRAME, rx, ry, n, 2.2, phase=math.pi) for z, x, rx, ry in sections]
    loft(part, rings, "leg.L", cap_start="flat", cap_end=None, v_range=(0.0, 0.55))
    # Rolled cuff: a soft band, lighter inside fabric (top band of the denim texture).
    bottom, top, extra = C.CUFF
    z_last, x_last, rx_last, ry_last = sections[-1]
    cuff_rings = []
    for z, grow in ((top + 0.004, -0.004), (top, extra * 0.7), (top - 0.008, extra), (lerp(top, bottom, 0.5), extra),
                    (bottom + 0.008, extra), (bottom, extra * 0.6), (bottom + 0.004, -0.006)):
        cuff_rings.append(ring((x_last, 0.0, z), DOWN_FRAME, rx_last + grow, ry_last + grow, n, 2.2, phase=math.pi))
    cuff = Part("Cuff_L", materials["cuff"])
    loft(cuff, cuff_rings, "leg.L", cap_start=None, cap_end="flat")
    return part, cuff


# ------------------------------------------------------------------ shoes
SHOE_PROFILE = [  # (s along heel->toe, half width, height as a fraction of SHOE_HEIGHT)
    (0.00, 0.050, 0.86),
    (0.12, 0.057, 0.98),
    (0.40, 0.063, 1.00),
    (0.62, 0.069, 0.86),
    (0.82, 0.071, 0.78),
    (0.95, 0.067, 0.68),
]


def build_shoe(materials):
    upper = Part("Shoe_L", materials["shoe"])
    sole = Part("Sole_L", materials["sole"])
    n = C.SHOE_SEGMENTS
    x = C.SHOE_CENTER_X
    heel_y = C.SHOE_CENTER_Y + C.SHOE_LENGTH / 2
    toe_dir = Vector((0, -1, 0))
    frame = (Vector((1, 0, 0)), Vector((0, 0, 1)), toe_dir)   # right-handed: X x Z = -Y
    base_z = C.SOLE_HEIGHT * 0.55

    def y_at(s):
        return heel_y - s * (C.SHOE_LENGTH - 0.03)

    profile = [(s, hw, f * C.SHOE_HEIGHT) for s, hw, f in SHOE_PROFILE]
    rings = []
    for s, hw, h in profile:
        rings.append(ring((x, y_at(s), base_z + h / 2 - 0.004), frame, hw, h / 2, n, 3.2))
    s, hw, h = profile[-1]
    toe_rings, tip = dome((x, y_at(s), base_z + h / 2 - 0.006), frame, hw, h / 2, n, 0.034, 2, 3.2,
                          tip_shift=(0.0, -0.010))
    heel_rings, heel_tip = dome((x, y_at(0.0), base_z + profile[0][2] / 2 - 0.004), frame, profile[0][1],
                                profile[0][2] / 2, n, 0.022, 2, 3.2, sign=-1.0)
    loft(upper, list(reversed(heel_rings)) + rings + toe_rings, "foot.L", cap_start=heel_tip, cap_end=tip)

    # Sole: a slightly wider slab under the upper, flat bottom on z = 0.
    sole_rings = []
    hs = C.SOLE_HEIGHT
    ns = 8                                    # the slab needs fewer sides than the upper
    for s, hw, _ in SHOE_PROFILE:
        sole_rings.append(ring((x, y_at(s), hs / 2), frame, hw + 0.006, hs / 2, ns, 4.0, phase=math.pi / 8))
    s, hw, _ = SHOE_PROFILE[-1]
    toe, tip = dome((x, y_at(s), hs / 2), frame, hw + 0.006, hs / 2, ns, 0.040, 2, 4.0, phase=math.pi / 8)
    heel, heel_tip = dome((x, y_at(0.0), hs / 2), frame, SHOE_PROFILE[0][1] + 0.006, hs / 2, ns, 0.028, 2, 4.0,
                          phase=math.pi / 8, sign=-1.0)
    loft(sole, list(reversed(heel)) + sole_rings + toe, "foot.L", cap_start=heel_tip, cap_end=tip)

    # Laces: three grey bars across the instep, sitting just on the upper's top.
    laces = Part("Laces_L", materials["sole"])
    lace_frame = (Vector((1, 0, 0)), Vector((0, 0, 1)), toe_dir)
    for s in (0.40, 0.50, 0.60):
        _, hw, f = min(profile, key=lambda p: abs(p[0] - s))
        h = f
        top = base_z + h - 0.004
        y = y_at(s)
        bar = [ring((x, y + dy, top + 0.0015 - abs(dy) * 0.4), lace_frame, hw * 0.42, 0.0022, 4, 6.0,
                    phase=math.pi / 4) for dy in (0.005, -0.005)]
        loft(laces, bar, "foot_rigid.L", cap_start="flat", cap_end="flat")
    return [upper, sole, laces, mirror(upper), mirror(sole), mirror(laces)]
