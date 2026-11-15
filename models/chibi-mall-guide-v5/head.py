"""Head builder: skull, ears, nose and face patches (brows, mouth, cheeks) as one `Head` mesh; eyes as a separate `Eyes` mesh.
Shape keys: Head has `smile` and `surprised`; Eyes has `blink` (the eyes sink behind the skin; see prototype/blink/README.md).
Blender only. Character's left = +X."""
import math
import config as C
import kit

def _surf():
    h = C.HEAD
    return lambda x, z: kit.super_front_y(h['c'], h['r'], x, z, p_bot=h['p_bot'], rz_bot=h['rz_bot'])

def build_head(bpy, bmesh, mats):
    h = C.HEAD; surf = _surf(); groups = {}
    bm = bmesh.new()
    kit.add_super(bm, h['c'], h['r'], p_bot=h['p_bot'], rz_bot=h['rz_bot'], seg=56, rings=40, mi=0)
    e = C.EAR
    ex = kit.super_side_x(h['c'], h['r'], e['y'], e['z'], p_bot=h['p_bot'], rz_bot=h['rz_bot']) + e['r'][0] * 0.2   # ears sit on the skull side
    for sx in (1, -1): kit.add_super(bm, (sx * ex, e['y'], e['z']), e['r'], seg=14, rings=10, mi=0)
    n = C.NOSE; kit.add_super(bm, (0.0, surf(0.0, n['z']) - n['r'][1] * 0.6, n['z']), n['r'], seg=12, rings=8, mi=0)
    # brows (two arched bands), material 1
    b = C.BROW; groups['brows'] = []
    for sx in (1, -1):
        cx = sx * b['x']
        top = lambda u, cx=cx: b['z'] + b['arch'] * (1 - u * u) + b['th'] / 2 * (1 - 0.6 * abs(u))
        bot = lambda u, cx=cx: b['z'] + b['arch'] * (1 - u * u) - b['th'] / 2 * (1 - 0.6 * abs(u))
        groups['brows'] += kit.add_band(bm, surf, (-1.0, 1.0), top, bot, lambda u, cx=cx: cx + u * b['hw'], b['lift'], mi=1)
    # mouth: open smile, material 2
    m = C.MOUTH
    zt = lambda u: m['z'] + m['corner'] * u * u
    zb = lambda u: m['z'] + m['corner'] * u * u - m['depth'] * (1 - u * u) ** 0.8
    groups['mouth'] = kit.add_band(bm, surf, (-1.0, 1.0), zt, zb, lambda u: m['x'] + u * m['hw'], m['lift'], steps_u=16, steps_v=4, mi=2)
    # cheeks (blush), material 3
    k = C.CHEEK; groups['cheeks'] = []
    for sx in (1, -1):
        groups['cheeks'] += kit.add_patch(bm, surf, (sx * k['x'], k['z']), k['r'], k['r'], k['lift'], rings=3, seg=18, mi=3)
    bm.verts.index_update(); idx = {g: [v.index for v in vs] for g, vs in groups.items()}
    head = kit.finish('Head', bm, [mats['skin'], mats['brow'], mats['mouth_red'], mats['blush']])
    # shape keys
    head.shape_key_add(name='Basis', from_mix=False)
    co = [v.co.copy() for v in head.data.vertices]
    def key(name, fn):
        # displaced patch vertices are re-projected onto the skull so they keep their original lift above the skin
        sk = head.shape_key_add(name=name, from_mix=False)
        for i, c0 in enumerate(co):
            c = fn(i, c0.copy())
            if (c - c0).length > 0: c.y += surf(c.x, c.z) - surf(c0.x, c0.z)
            sk.data[i].co = c
        sk.value = 0.0
    brows, mouth, cheeks = set(idx['brows']), set(idx['mouth']), set(idx['cheeks'])
    def smile(i, c):
        if i in mouth:
            u = (c.x - m['x']) / m['hw']; c.z += 0.010 * u * u - 0.002
        elif i in cheeks: c.z += 0.006; c.y -= 0.002
        elif i in brows: c.z += 0.003
        return c
    def surprised(i, c):
        if i in brows: c.z += 0.016
        elif i in mouth:
            c.x = m['x'] + (c.x - m['x']) * 0.55; c.z = m['z'] + (c.z - m['z']) * 1.6 - 0.006
        return c
    key('smile', smile); key('surprised', surprised)
    # eyes: two patches merged in one mesh, blink key sinks them behind the skin
    ey = C.EYE; bm = bmesh.new()
    hl = lambda u, v: 1 if math.hypot(u + 0.30, v - 0.35) < 0.24 else 0
    for sx in (1, -1):
        kit.add_patch(bm, surf, (sx * ey['x'], ey['z']), ey['a'], ey['b'], ey['lift'], rings=7, seg=32, mi_fn=hl)
    eyes = kit.finish('Eyes', bm, [mats['eye_dark'], mats['white']])
    eyes.shape_key_add(name='Basis', from_mix=False)
    sk = eyes.shape_key_add(name='blink', from_mix=False)
    for i, v in enumerate(eyes.data.vertices):
        sk.data[i].co = (v.co.x, v.co.y + 0.016, v.co.z)
    sk.value = 0.0
    return head, eyes
