"""Hair: layered, swept locks wrapped on the skull. Each lock is an elliptical section swept along a path over the skull and
tapering to rounded ends (no points), so the locks read as broad, blunt, overlapping strands. Layer A covers the skull; layer B
sits on top and overlaps the seams of layer A. Locks overlap each other and the skull on purpose; they are one mesh. Blender only."""
import math
from mathutils import Vector
import config as C
import kit

def skull_point(az, el, off):
    """Point on the skull at azimuth az (0 = front, + toward the character's left) and elevation el (radians), pushed out by off."""
    h = C.HEAD; c = Vector(h['c']); rx, ry, rz = h['r']
    d = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    p = c + Vector((rx * d.x, ry * d.y, rz * d.z))
    n = Vector((d.x / rx, d.y / ry, d.z / rz)).normalized()
    return p + n * off, n

def lock_geometry(spec, steps=None):
    steps = steps or C.HAIR_STEPS
    az0, el0, az1, el1, swirl, W, T, off = spec[:8]; flare = spec[8] if len(spec) > 8 else 0.0; r = math.radians
    opts = spec[9] if len(spec) > 9 else {}; taper = opts.get('taper', C.HAIR_TAPER); endmin = opts.get('endmin', C.HAIR_END_MIN)
    pts, nrm, ws, ts = [], [], [], []
    for i in range(steps + 1):
        t = i / steps
        az = az0 + (az1 - az0) * t + swirl * math.sin(math.pi * t)
        el = el0 + (el1 - el0) * t
        s = max(math.sin(math.pi * t) ** taper, endmin)   # blunt ends: a floor keeps them from tapering to a point
        belly = 1.0 + 0.25 * math.sin(math.pi * min(1.0, t * 1.4))   # a little fuller toward the root
        p, n = skull_point(r(az), r(el), off + flare * t * t + T * 0.55 * s)   # flare pushes the lower end outward
        pts.append(p); nrm.append(n); ws.append(W * s * belly); ts.append(T * s)
    return pts, nrm, ws, ts

def build_hair(bmesh, mats):
    bm = bmesh.new()
    for spec in C.HAIR_LOCKS:
        pts, nrm, ws, ts = lock_geometry(spec)
        kit.add_lock(bm, pts, nrm, ws, ts, sides=C.HAIR_SIDES, cap_rings=C.HAIR_CAP_RINGS)
    return kit.finish('Hair', bm, [mats['hair']])
