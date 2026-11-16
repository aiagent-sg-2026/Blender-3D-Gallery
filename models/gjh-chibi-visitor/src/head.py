"""Skull, ears and the face: projected decal pieces with expression shape keys.

The face is one mesh ("Face") made of thin, opaque decal pieces lifted a
millimetre or two above the skin and textured from the face atlas. Each
expression is a shape key: pieces that should disappear sink a few
millimetres under the skin, pieces that should appear rise from under it.
"""
import math

from mathutils import Vector
from mathutils.bvhtree import BVHTree

import config as C
from mesh import Part, loft, ring, smoothstep, lerp, sweep
import materials as M

SHOW = {"blush": 0.0024, "mouth": 0.0024, "eye": 0.0022, "brow": 0.0022, "arc": 0.0027}
HIDE = -0.0040
EXPRESSIONS = ["blink", "happy", "wink_L", "surprised", "thinking", "excited", "talk"]


# ------------------------------------------------------------------ skull
def skull_point(theta, phi):
    """Chibi skull: a rounded ellipsoid with a forward, full-cheeked lower face."""
    cx, cy, cz = C.HEAD_CENTER
    rx, ry, rz = C.HEAD_RADII
    power = C.HEAD_ROUNDNESS[0] if theta >= 0.0 else C.HEAD_ROUNDNESS[1]
    c = max(math.cos(theta), 0.0) ** power
    x = rx * c * math.cos(phi)
    y = ry * c * math.sin(phi)
    z = rz * math.sin(theta)
    front = max(0.0, -math.sin(phi))
    zw = cz + z
    if y < 0.0:
        y *= lerp(1.0, C.FACE_FLATTEN, front)
    jaw = smoothstep(C.JAW_START_Z, C.CHIN_Z, zw)
    x *= lerp(1.0, C.JAW_MIN_SCALE, jaw)
    cheek = math.exp(-((zw - C.CHEEK_Z) / 0.045) ** 2) * front
    x += math.copysign(C.CHEEK_PUFF * cheek, x) if abs(x) > 1e-6 else 0.0
    y -= C.LOWER_FORWARD * smoothstep(cz, C.CHIN_Z, zw) * (0.4 + 0.6 * front)
    return Vector((cx + x, cy + y, cz + z))


def build_skull(materials):
    part = Part("Skull", materials["skin"])
    seg, rings_n = C.HEAD_SEGMENTS, C.HEAD_RINGS
    rings = []
    for k in range(1, rings_n):
        theta = -math.pi / 2 + math.pi * k / rings_n
        rings.append([skull_point(theta, 2 * math.pi * i / seg) for i in range(seg)])
    bottom = skull_point(-math.pi / 2, 0.0)
    top = skull_point(math.pi / 2, 0.0)
    loft(part, rings, "head", cap_start=bottom, cap_end=top)
    return part


def build_ears(materials):
    parts = []
    for side in (1.0, -1.0):
        part = Part("Ear", materials["skin"])
        ex, ey, ez = C.EAR_CENTER
        t, d, h = C.EAR_SIZE
        spine = [Vector((side * ex, ey, ez - h / 2 + h * s / 3)) for s in range(4)]
        spine = [p + Vector((side * 0.006 * math.sin(math.pi * s / 3), -0.004 * s, 0)) for s, p in enumerate(spine)]
        # Frame x runs front-back (depth), frame y sticks out sideways (thickness).
        radii = [(d * 0.45, t * 0.5), (d * 0.55, t * 0.55), (d * 0.55, t * 0.55), (d * 0.42, t * 0.45)]
        # The sweep frame is right-handed on both sides, so no winding flip is needed.
        sweep(part, spine, radii, "head", count=8, hint=(1.0, 0.0, 0.0),
              dome_start=(h * 0.18, 1), dome_end=(h * 0.2, 1))
        parts.append(part)
    return parts


def build_nose(skull_part, materials):
    """A small soft bump on the skull surface: the sheet's tiny chibi nose."""
    part = Part("Nose", materials["skin"])
    project = Projector(skull_part)
    nx, nz = C.NOSE_CENTER
    w, d, h = C.NOSE_SIZE
    base = project(nx, nz, -0.003)
    frame = (Vector((1, 0, 0)), Vector((0, 0, 1)), Vector((0, -1, 0)))   # loft towards the viewer
    rings = [ring(base + Vector((0, -d * k, 0)), frame, w * s, h * s, 8) for k, s in ((0.0, 1.0), (0.55, 0.92), (0.9, 0.6))]
    loft(part, rings, "head", cap_start="flat", cap_end=base + Vector((0.0, -d * 1.1, 0.0)))
    return part


def build_neck(materials):
    part = Part("Neck", materials["skin"])
    rings = []
    for k in range(4):
        z = lerp(C.NECK_BOTTOM_Z, C.NECK_TOP_Z, k / 3)
        frame = (Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1)))
        rings.append(ring((0.0, C.NECK_CENTER_Y, z), frame, C.NECK_RADIUS, C.NECK_RADIUS * 0.95, 10))
    loft(part, rings, "spine", cap_start="flat", cap_end="flat")
    return part


# ------------------------------------------------------------------ decal projection
class Projector:
    """Projects face-plane points (x, z) onto the skull along +Y."""

    def __init__(self, skull_part):
        self.tree = BVHTree.FromPolygons([tuple(v) for v in skull_part.verts], skull_part.faces)

    def __call__(self, x, z, offset):
        hit, normal, _, _ = self.tree.ray_cast(Vector((x, -1.0, z)), Vector((0.0, 1.0, 0.0)))
        if hit is None:
            raise ValueError(f"face point ({x:.3f}, {z:.3f}) misses the skull")
        if normal.y > 0:
            normal = -normal
        return hit + normal * offset


class FaceBuilder:
    def __init__(self, projector, material):
        self.project = projector
        self.part = Part("Face", material)
        self.keys = {name: [] for name in EXPRESSIONS}

    def piece(self, samples, faces, uvs, shapes, tag="head"):
        """samples: canonical coordinates; shapes: {'basis': fn, key: fn} where
        fn(sample) -> (x, z, offset)."""
        base = len(self.part.verts)
        basis_fn = shapes["basis"]
        for s in samples:
            x, z, off = basis_fn(s)
            self.part.vert(self.project(x, z, off), tag)
            for name in EXPRESSIONS:
                fn = shapes.get(name, basis_fn)
                kx, kz, koff = fn(s)
                self.keys[name].append(self.project(kx, kz, koff))
        for f, uv in zip(faces, uvs):
            self.part.face(tuple(i + base for i in f), uv)


def disc_samples(segments, rings):
    """Centre + concentric rings, canonical unit disc. Faces wind towards -Y."""
    samples = [(0.0, 0.0)]
    for r in range(1, rings + 1):
        rad = r / rings
        for i in range(segments):
            a = 2 * math.pi * i / segments
            samples.append((rad * math.cos(a), rad * math.sin(a)))
    faces = []
    for i in range(segments):
        j = (i + 1) % segments
        faces.append((0, 1 + i, 1 + j))
    for r in range(1, rings):
        a0, b0 = 1 + (r - 1) * segments, 1 + r * segments
        for i in range(segments):
            j = (i + 1) % segments
            faces.append((a0 + i, a0 + j, b0 + j, b0 + i)[::-1])
    return samples, faces


def strip_samples(columns):
    """Two-row strip, a in [-1, 1] across, b in {-1, 1}. Faces wind towards -Y."""
    samples = []
    for i in range(columns + 1):
        a = -1.0 + 2.0 * i / columns
        samples.append((a, -1.0))
        samples.append((a, 1.0))
    faces = []
    for i in range(columns):
        p, q = 2 * i, 2 * (i + 1)
        faces.append((p, q, q + 1, p + 1))
    return samples, faces


def uv_for(region, samples, faces):
    return [[M.atlas_uv(region, 0.5 + 0.5 * samples[i][0], 0.5 + 0.5 * samples[i][1]) for i in f] for f in faces]


def build_face(skull_part, materials):
    fb = FaceBuilder(Projector(skull_part), materials["face"])
    ew, eh = C.EYE_SIZE

    for side in (1.0, -1.0):
        ex, ez = side * C.EYE_CENTER[0], C.EYE_CENTER[1]
        is_left = side > 0

        # Open eye disc.
        samples, faces = disc_samples(16, 3)
        faces = _side_faces(faces, side)
        def eye_shape(sx=1.0, sz=1.0, dz=0.0, dx=0.0, off=SHOW["eye"]):
            return lambda s: (ex + dx + s[0] * ew / 2 * sx * side, ez + dz + s[1] * eh / 2 * sz, off)
        hidden = eye_shape(0.85, 0.10, -eh * 0.12, 0.0, HIDE)
        shapes = {
            "basis": eye_shape(),
            "blink": hidden,
            "happy": hidden,
            "excited": hidden,
            "surprised": eye_shape(1.12, 1.20, 0.005),
            # Thinking: lower lids rise (a sceptical squint) and both eyes shift sideways.
            "thinking": eye_shape(0.96, 0.66, 0.010, 0.007),
        }
        if is_left:
            shapes["wink_L"] = hidden
        fb.piece(samples, faces, uv_for("eye", samples, faces), shapes)

        # Closed-eye arc, hidden under the skin until a closing expression.
        samples, faces = strip_samples(10)
        faces = _side_faces(faces, side)
        def arc(curve, dz, off=SHOW["arc"], scale=1.0):
            def fn(s):
                a, b = s
                thick = 0.0058 * (1.0 - 0.55 * a * a)
                return (ex + a * ew / 2 * 0.95 * scale * side,
                        ez + dz * scale + curve * a * a * scale + b * thick / 2 * scale, off)
            return fn
        happy_arc = arc(-0.020, 0.006)
        def chevron(off=SHOW["arc"]):
            """Squeezed '> <' eye: the strip bends into a V pointing at the nose."""
            def fn(s):
                a, b = s
                thick = 0.0062
                x_local = (abs(a) * 2.0 - 1.0) * ew / 2 * 0.78        # +1 outer corner, -1 apex (inner)
                z_local = -a * eh * 0.30
                return (ex + x_local * side, ez + 0.002 + z_local + b * thick / 2, off)
            return fn
        shapes = {
            "basis": arc(0.0, -eh * 0.10, HIDE, 0.4),
            "blink": arc(0.010, -0.014),
            "happy": happy_arc,
            "excited": chevron(),
        }
        if is_left:
            shapes["wink_L"] = happy_arc
        fb.piece(samples, faces, uv_for("eye_closed", samples, faces), shapes)

        # Brow.
        bx, bz = side * C.BROW_CENTER[0], C.BROW_CENTER[1]
        bl, bt = C.BROW_SIZE
        samples, faces = strip_samples(8)
        faces = _side_faces(faces, side)
        def brow(dz=0.0, arch=C.BROW_ARCH, tilt=0.0):
            def fn(s):
                a, b = s
                inner = (1.0 - a) / 2.0           # 1 at the inner (nose) end
                thick = bt * (0.50 + 0.70 * inner)          # tapered towards the outer end
                z = bz + dz + arch * (1.0 - a * a) + tilt * a + b * thick / 2.0
                return (bx + a * bl / 2.0 * side, z, SHOW["brow"])
            return fn
        shapes = {
            "basis": brow(),
            "surprised": brow(0.018, C.BROW_ARCH * 1.9),
            "happy": brow(0.005),
            "excited": brow(0.008, C.BROW_ARCH * 1.3),
            "blink": brow(-0.002),
            "thinking": brow(0.016, C.BROW_ARCH * 1.3, 0.007) if is_left else brow(-0.006, C.BROW_ARCH * 0.3, -0.004),
        }
        if is_left:
            shapes["wink_L"] = brow(-0.003)
        fb.piece(samples, faces, uv_for("brow", samples, faces), shapes)

        # Blush.
        cx, cz = side * C.BLUSH_CENTER[0], C.BLUSH_CENTER[1]
        bw, bh = C.BLUSH_SIZE
        samples, faces = disc_samples(12, 3)
        faces = _side_faces(faces, side)
        def blush(scale=1.0):
            return lambda s: (cx + s[0] * bw / 2 * scale * side, cz + s[1] * bh / 2 * scale, SHOW["blush"])
        shapes = {"basis": blush(), "happy": blush(1.12), "excited": blush(1.18), "wink_L": blush(1.08)}
        fb.piece(samples, faces, uv_for("blush", samples, faces), shapes)

    # Closed smile line.
    mx, mz = C.MOUTH_CENTER
    mw = C.MOUTH_WIDTH
    samples, faces = strip_samples(10)
    def smile(width=1.0, curve=C.MOUTH_CURVE, dx=0.0, off=SHOW["mouth"], scale=1.0, tilt=0.0):
        def fn(s):
            a, b = s
            thick = C.MOUTH_LINE * (1.0 - 0.55 * a * a)
            return (mx + dx + a * mw / 2 * width * scale,
                    mz + curve * a * a * scale + tilt * a + b * thick / 2 * scale, off)
        return fn
    hidden_smile = smile(0.6, 0.0, 0.0, HIDE, 0.5)
    fb.piece(samples, faces, uv_for("mouth_line", samples, faces), {
        "basis": smile(),
        "happy": hidden_smile, "excited": hidden_smile, "wink_L": hidden_smile,
        "surprised": hidden_smile, "talk": hidden_smile,
        "thinking": smile(0.55, -0.003, 0.013, tilt=0.004),
    })

    # Open mouth (hidden in the basis): D-shaped smile, O for surprise.
    samples, faces = disc_samples(16, 3)
    def opened(half_w, top, bottom, dz=0.0, curve=0.0, off=SHOW["mouth"]):
        def fn(s):
            a, b = s
            z = mz + dz + (b * top if b > 0 else b * bottom) + curve * a * a
            return (mx + a * half_w, z, off)
        return fn
    happy_mouth = opened(0.030, 0.003, 0.022, 0.004, 0.006)
    fb.piece(samples, faces, uv_for("mouth_open", samples, faces), {
        "basis": opened(0.010, 0.001, 0.004, 0.0, 0.0, HIDE),
        "happy": happy_mouth,
        "wink_L": happy_mouth,
        "excited": opened(0.040, 0.004, 0.034, 0.004, 0.009),
        "surprised": opened(0.019, 0.020, 0.023, -0.007),
        "talk": opened(0.022, 0.005, 0.014, 0.0, 0.003),
    })
    return fb


def _side_faces(faces, side):
    """Canonical faces wind towards -Y for +X pieces; mirrored pieces flip."""
    if side > 0:
        return faces
    return [tuple(reversed(f)) for f in faces]


def add_shape_keys(obj, face_builder):
    obj.shape_key_add(name="Basis", from_mix=False)
    for name in EXPRESSIONS:
        key = obj.shape_key_add(name=name, from_mix=False)
        for i, co in enumerate(face_builder.keys[name]):
            key.data[i].co = co
        key.slider_min = 0.0
        key.slider_max = 1.0
        key.value = 0.0          # Blender 5 creates new keys at full strength
