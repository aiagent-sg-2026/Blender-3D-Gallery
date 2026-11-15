"""Hair: eight thick, blunt, rounded lobes (three fringe lobes, two side lobes, three back lobes) wrapped on the skull.
Blender only. Lobes overlap each other and the skull on purpose (the creases between lobes are the intersections); they are one mesh."""
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

def build_hair(bmesh, mats):
    bm = bmesh.new(); r = math.radians
    for (az, el, off, size, roll, tilt) in C.HAIR_LOBES:
        p, n = skull_point(r(az), r(el), off)
        kit.add_lobe(bm, p, n, size, roll=r(roll), p=C.HAIR_P, tilt=r(tilt))
    return kit.finish('Hair', bm, [mats['hair']])
