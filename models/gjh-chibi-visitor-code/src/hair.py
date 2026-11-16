"""Hair: a thick cap that carries the overall volume, covered by layered,
feather-like locks (wide roots, pointed tips) that radiate from the crown
whorl like the owner's sheet. Locks are generated in rows (shingles) plus a
hand-placed swept fringe. Everything uses the lock texture (v = 0 root -> 1 tip).

Directions use the skull parametrisation from head.skull_point:
theta = latitude (90 deg = crown), phi = longitude with -90 deg = front (-Y),
0 deg = character's left (+X), 90 deg = back, 180 deg = character's right.
"""
import math

from mathutils import Vector

import config as C
from head import skull_point
from mesh import Part, loft, lerp, ring, smoothstep

D = math.radians


def piecewise(f, table):
    """Linear interpolation of table [(f, value)...] sorted by f ascending."""
    if f <= table[0][0]:
        return table[0][1]
    for (f0, v0), (f1, v1) in zip(table, table[1:]):
        if f0 <= f <= f1:
            return lerp(v0, v1, (f - f0) / (f1 - f0))
    return table[-1][1]


def front_factor(phi):
    return -math.sin(phi)          # 1 front, 0 sides, -1 back


def hairline(phi):
    return D(piecewise(front_factor(phi), C.HAIRLINE_DEG))


def mass(phi):
    return piecewise(front_factor(phi), C.HAIR_MASS)


def edge(phi):
    return piecewise(front_factor(phi), C.HAIR_EDGE)


def thickness(theta, phi):
    """Hair height above the skull. Below the hairline it falls towards the
    skin so fringe and side locks come down onto the face and temples."""
    th = hairline(phi)
    if theta <= th:
        drop = max(0.12, 1.0 + (theta - th) / D(C.HAIR_DROP_DEG))
        return edge(phi) * drop
    u = (theta - th) / (math.pi / 2 - th)
    m = lerp(mass(phi), C.HAIR_CROWN, smoothstep(0.45, 0.95, u))
    # The sheet's crown peaks above the face and towards the character's right:
    # thin the top on the left (+X) and at the back so the outline matches.
    top = smoothstep(*C.HAIR_CROWN_TRIM_BAND, u)
    m *= 1.0 - top * (C.HAIR_CROWN_TRIM_LEFT * max(0.0, math.cos(phi))
                      + C.HAIR_CROWN_TRIM_BACK * max(0.0, math.sin(phi)))
    return lerp(edge(phi), m, smoothstep(0.0, C.HAIR_FADE, u))


def radial(theta, phi):
    p = skull_point(theta, phi)
    return (p - Vector(C.HEAD_CENTER)).normalized()


def surface(theta, phi, extra=0.0):
    """Point on the hair mass (skull + thickness), lifted by `extra`."""
    p = skull_point(theta, phi)
    return p + radial(theta, phi) * (thickness(theta, phi) + extra)


# ------------------------------------------------------------------ cap
def build_cap(materials):
    part = Part("HairCap", materials["hair"])
    seg, rows = C.HAIR_SHELL_SEGMENTS, C.HAIR_SHELL_RINGS
    phis = [2 * math.pi * i / seg for i in range(seg)]
    rings = []
    # Inner lip: just above the skin at the hairline, gives the edge thickness.
    rings.append([skull_point(hairline(p), p) + radial(hairline(p), p) * 0.003 for p in phis])
    for k in range(rows):
        t = k / rows
        rings.append([surface(lerp(hairline(p), math.pi / 2, t), p) for p in phis])
    top = surface(math.pi / 2, 0.0)
    loft(part, rings, "head", cap_start=None, cap_end=top, v_range=(1.0, 0.0))
    return part


# ------------------------------------------------------------------ locks
def lock(part, root, tip, width, thick, mid=None, lift=0.0, bend=0.0, embed=0.40, steps=None):
    """A feather-like lock lying on the hair surface.

    root/tip/mid: (theta_deg, phi_deg). lift: extra height of the tip above
    the surface (flicks). bend: sideways sag of the middle (degrees of phi).
    """
    steps = steps or C.HAIR_LOCK_STEPS
    r_t, r_p = D(root[0]), D(root[1])
    t_t, t_p = D(tip[0]), D(tip[1])
    if mid is None:
        mid = ((root[0] + tip[0]) / 2.0, (root[1] + tip[1]) / 2.0 + bend)
    m_t, m_p = D(mid[0]), D(mid[1])
    spine, normals, widths, thicks = [], [], [], []
    for i in range(steps + 1):
        s = i / steps
        # Quadratic Bezier in (theta, phi) that passes through root, mid, tip.
        a, b, c = (1 - s) ** 2, 2 * (1 - s) * s, s * s
        mt = 2 * m_t - (r_t + t_t) / 2
        mp = 2 * m_p - (r_p + t_p) / 2
        th = a * r_t + b * mt + c * t_t
        ph = a * r_p + b * mp + c * t_p
        w = width * piecewise(s, C.LOCK_WIDTH_PROFILE)
        tk = thick * piecewise(s, C.LOCK_THICK_PROFILE)
        up = lift * smoothstep(0.35, 1.0, s)
        # Roots sink into the cap so their flat start caps never show.
        sink = thick * C.LOCK_ROOT_SINK * (1.0 - smoothstep(0.0, 0.35, s))
        spine.append(surface(th, ph, tk * (0.5 - embed) + up - sink))
        normals.append(radial(th, ph))
        widths.append(w)
        thicks.append(tk)
    rings = []
    count = C.HAIR_LOCK_SEGMENTS
    for i, p in enumerate(spine):
        a = spine[max(i - 1, 0)]
        b = spine[min(i + 1, len(spine) - 1)]
        d = (b - a).normalized()
        x = normals[i].cross(d).normalized()
        y = d.cross(x).normalized()
        rings.append(ring(p, (x, y, d), widths[i] / 2, thicks[i] / 2, count, C.HAIR_LOCK_POWER))
    # Pointed tip: one shrinking ring ahead of the last one, then the point.
    d = (spine[-1] - spine[-2]).normalized()
    x = normals[-1].cross(d).normalized()
    y = d.cross(x).normalized()
    w, tk = widths[-1], thicks[-1]
    # Blunt, rounded tip (the sheet's locks end in soft points, not needles).
    tip_len = max(w, tk) * 0.45
    rings.append(ring(spine[-1] + d * tip_len * 0.55, (x, y, d), w / 2 * 0.82, tk / 2 * 0.85, count,
                      C.HAIR_LOCK_POWER))
    tip_point = spine[-1] + d * tip_len
    loft(part, rings, "head", cap_start="flat", cap_end=tip_point, v_range=(0.0, 1.0))


def angular_width(width, theta_deg, phi_deg):
    """Metres of surface width -> degrees of longitude at that latitude."""
    radius = (surface(D(theta_deg), D(phi_deg)) - Vector(C.HEAD_CENTER)).length
    circumference = max(radius * math.cos(D(theta_deg)), 0.05)
    return math.degrees(width / circumference)


def in_gap(phi_deg, gap):
    if gap is None:
        return False
    p = (phi_deg + 180.0) % 360.0 - 180.0
    return gap[0] <= p <= gap[1]


def row_locks(row):
    """Evenly spaced locks round the head; tips follow the hairline."""
    specs = []
    for k in range(row["count"]):
        phi = row["phi0"] + 360.0 * k / row["count"]
        if in_gap(phi, row.get("gap")):
            continue
        p = D(phi)
        side = math.cos(p)                         # +1 left side, -1 right side
        if "tip_theta" in row:
            tip_theta = row["tip_theta"]
        else:
            tip_theta = math.degrees(hairline(p)) + row["tip_above_hairline"]
        root_theta = min(tip_theta + row["length_deg"], 86.0)
        sweep = row["sweep"] * side                # tips sweep towards the back
        lift = row["lift"] * (0.35 + 0.65 * abs(side))
        specs.append(dict(root=(root_theta, phi), tip=(tip_theta, phi + sweep),
                          width=row["width"], thick=row["thick"], lift=lift, bend=sweep * 0.25))
    return specs


def build_locks(materials):
    part = Part("HairLocks", materials["hair"])
    specs = []
    for row in C.HAIR_ROWS:
        specs.extend(row_locks(row))
    specs.extend(C.HAIR_FRINGE)
    specs.extend(C.HAIR_EXTRA)
    for spec in specs:
        lock(part, **spec)
    return part
