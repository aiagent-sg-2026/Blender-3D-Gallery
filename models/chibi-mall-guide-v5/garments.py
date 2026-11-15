"""Garment builders: vest, shirt, neckerchief, shorts, cap. Blender only. Each returns the created objects."""
import math
import config as C
import kit

def _hex_lin(h):
    def f(c):
        c /= 255.0; return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (f(int(h[0:2], 16)), f(int(h[2:4], 16)), f(int(h[4:6], 16)), 1.0)

def make_materials(bpy):
    mats = {}
    for name, hx in C.PALETTE.items():
        m = bpy.data.materials.new(name); m.use_nodes = True
        b = m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = _hex_lin(hx)
        b.inputs['Roughness'].default_value = 0.38 if name == 'brass' else 0.5
        if name == 'brass': b.inputs['Metallic'].default_value = 0.6
        m.diffuse_color = _hex_lin(hx)
        mats[name] = m
    return mats

def torso_front_y(x, z, spec, p_top=2.6, p_bot=4.0):
    """Front (-Y) surface of the vest-style superellipsoid (same construction as kit.add_super) at (x, z)."""
    cx, cy, cz = spec['c']; rx, ry, rz = spec['r']
    zn = (z - cz) / rz
    if abs(zn) >= 1: return cy
    p = p_top if zn >= 0 else p_bot
    f = math.sqrt(max(0.0, 1 - abs(zn) ** p)) / math.sqrt(1 - zn * zn)
    rho2 = 1 - zn * zn
    t = rho2 - ((x - cx) / (f * rx)) ** 2
    return cy - f * ry * math.sqrt(max(0.0, t))

def build_vest(bm_mod, mats):
    bm = bm_mod.new(); v = C.VEST
    kit.add_super(bm, v['c'], v['r'], p_top=2.6, p_bot=4.0, seg=72, rings=44, mi=0)
    ax = [(sx * a[0], a[1], a[2]) for sx in (1, -1) for a in C.ARM_PATH[:2]]
    def cut(p):
        if p.z < v['z_hem'] or p.z > v['z_neck']: return True
        # armholes: distance to the shoulder axis in the Y-Z plane, only on the arm side
        return abs(p.x) > 0.06 and math.hypot(p.y, p.z - v['armhole_z']) < v['armhole_r']
    kit.delete_faces(bm, cut)
    import bmesh
    bmesh.ops.solidify(bm, geom=list(bm.faces), thickness=v['thick'])
    # brass details sit flush: centre = surface - own depth radius + 1 mm, so they never reach the shirt behind the vest
    def flush(x, z, ry): return torso_front_y(x, z, v) - ry + 0.001
    for z in (0.395, 0.350):
        kit.add_super(bm, (0.0, flush(0.0, z, 0.0045), z), (0.0075, 0.0045, 0.0075), seg=14, rings=8, mi=1)
    kit.add_super(bm, (0.058, flush(0.058, 0.405, 0.006), 0.405), (0.018, 0.006, 0.018), seg=20, rings=10, mi=1)
    for sx in (1, -1):
        kit.add_super(bm, (sx * 0.056, flush(sx * 0.056, 0.318, 0.005), 0.318), (0.022, 0.005, 0.012), seg=16, rings=8, mi=0)
    return kit.finish('Vest', bm, [mats['jade'], mats['brass']])

def build_shirt(bm_mod, mats):
    bm = bm_mod.new(); s = C.SHIRT
    kit.add_super(bm, s['c'], s['r'], p_top=2.6, p_bot=4.0, seg=64, rings=40)
    kit.delete_faces(bm, lambda p: p.z < s['z_hem'] or p.z > s['z_neck'] or (abs(p.x) > 0.06 and math.hypot(p.y, p.z - C.VEST['armhole_z']) < s['armhole_r']))
    for sx in (1, -1):   # short sleeves: the first part of the arm path, open at the cuff
        pts = [(sx * a[0], a[1], a[2]) for a in C.ARM_PATH[:2]]
        # stop at sleeve_to_z along the elbow segment
        t = (pts[0][2] - s['sleeve_to_z']) / (pts[0][2] - pts[1][2])
        end = tuple(pts[0][i] + (pts[1][i] - pts[0][i]) * t for i in range(3))
        kit.add_tube(bm, [pts[0], ((pts[0][0] + end[0]) / 2, (pts[0][1] + end[1]) / 2, (pts[0][2] + end[2]) / 2), end], [0.037, 0.036, 0.035], sides=16, cap_start=False, cap_end=False)
    return kit.finish('Shirt', bm, [mats['ivory']])

def build_neckerchief(bm_mod, mats):
    bm = bm_mod.new()
    kit.add_torus(bm, (0.0, 0.010, 0.466), 0.072, 0.010, seg=32, tube=8)
    kit.add_super(bm, (0.0, -0.078, 0.466), (0.022, 0.016, 0.018), seg=16, rings=10)
    v = C.VEST
    for sx in (1, -1):   # flaps lie on the vest front, tilted to follow its slope
        z = 0.428; w = (z - v['c'][2]) / v['r'][2]
        phi = math.atan((v['r'][1] * w / v['r'][2]) / math.sqrt(max(1e-6, 1 - w * w)))
        kit.add_super(bm, (sx * 0.013, torso_front_y(sx * 0.013, z, v) - 0.007, z), (0.011, 0.004, 0.024), seg=14, rings=8, rot_x=phi)
    return kit.finish('Neckerchief', bm, [mats['ivory']])

def build_shorts(bm_mod, mats):
    bm = bm_mod.new(); s = C.SHORTS
    kit.add_super(bm, s['c'], s['r'], p_top=3.0, p_bot=5.0, seg=32, rings=18)
    kit.delete_faces(bm, lambda p: p.z < 0.20 and abs(p.x) < 0.098)
    for sx in (1, -1):
        kit.add_tube(bm, [(sx * s['leg_x'], 0.013, 0.262), (sx * s['leg_x'], 0.013, s['z_hem'])], [s['leg_r'], s['leg_r'] + 0.002], sides=18, cap_start=False, cap_end=False)
        kit.add_torus(bm, (sx * s['leg_x'], 0.013, s['z_hem']), s['leg_r'] + 0.002, 0.006, seg=20, tube=6)
    return kit.finish('Shorts', bm, [mats['charcoal']])

def build_cap(bm_mod, mats):
    bm = bm_mod.new(); c = C.CAP
    kit.add_super(bm, c['c'], c['r'], p_bot=6.0, seg=36, rings=18, mi=0)
    kit.add_torus(bm, (0.0, c['c'][1], c['z_rim']), 0.127, 0.008, scale_xy=(1.0, 0.96), seg=40, tube=8, mi=1)
    kit.add_super(bm, (0.104, c['c'][1] - 0.078, 0.945), (0.012, 0.007, 0.012), seg=16, rings=10, mi=2)
    return kit.finish('Cap', bm, [mats['cap_jade'], mats['ivory'], mats['brass']])
