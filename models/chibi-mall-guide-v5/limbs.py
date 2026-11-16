"""Limb builders: arms, gloves, legs, socks, shoes. Blender only. Character's left = +X; names use .L (+X) and .R (-X)."""
import config as C
import kit

SIDES = (('.L', 1), ('.R', -1))

def build_arms(bm_mod, mats):
    out = []
    for suf, sx in SIDES:
        bm = bm_mod.new()
        kit.add_tube(bm, [(sx * a[0], a[1], a[2]) for a in C.ARM_PATH], C.ARM_RADII, sides=16, cap_start=True, cap_end=False)
        kit.add_super(bm, (sx * C.ARM_PATH[0][0], C.ARM_PATH[0][1], C.ARM_PATH[0][2]), (0.031, 0.031, 0.031), seg=16, rings=10)   # shoulder ball
        out.append(kit.finish('Arm' + suf, bm, [mats['skin']]))
    return out

def build_gloves(bm_mod, mats):
    out = []; wx, wy, wz = C.ARM_PATH[-1]
    for suf, sx in SIDES:
        bm = bm_mod.new()
        kit.add_tube(bm, [(sx * wx, wy, wz + 0.012), (sx * wx, wy, wz - 0.006)], [0.031, 0.030], sides=16, cap_start=False, cap_end=False)   # cuff
        kit.add_super(bm, (sx * (wx + 0.002), 0.038, 0.240), (0.036, 0.040, 0.046), seg=20, rings=14)                                       # mitten
        kit.add_super(bm, (sx * (wx + 0.007), 0.0, 0.246), (0.014, 0.016, 0.026), seg=12, rings=8)                                          # thumb (front)
        out.append(kit.finish('Glove' + suf, bm, [mats['white']]))
    return out

def build_legs(bm_mod, mats):
    out = []; L = C.LEG
    for suf, sx in SIDES:
        bm = bm_mod.new()
        kit.add_tube(bm, [(sx * L['x'], L['y'], L['z_top']), (sx * L['x'], L['y'], L['z_sock'])], [L['r_top'], L['r_bot'] + 0.002], sides=14, cap_start=False, cap_end=False)
        out.append(kit.finish('Leg' + suf, bm, [mats['skin']]))
    return out

def build_socks(bm_mod, mats):
    out = []; L = C.LEG
    for suf, sx in SIDES:
        bm = bm_mod.new()
        kit.add_tube(bm, [(sx * L['x'], L['y'], L['z_sock']), (sx * L['x'], L['y'], L['z_bot'] + 0.006)], [L['sock_r'], L['sock_r'] - 0.003], sides=16, cap_start=False, cap_end=False)
        kit.add_torus(bm, (sx * L['x'], L['y'], L['z_sock']), L['sock_r'], 0.005, seg=20, tube=6)
        out.append(kit.finish('Sock' + suf, bm, [mats['ivory']]))
    return out

def build_shoes(bm_mod, mats):
    out = []; S = C.SHOE
    for suf, sx in SIDES:
        x = sx * S['x']; y = S['y']; bm = bm_mod.new()
        kit.add_super(bm, (x, y, 0.014), (0.052, 0.098, 0.014), p_top=4.0, p_bot=6.0, seg=28, rings=12, mi=1)          # sole (ivory)
        kit.add_super(bm, (x, y + 0.010, 0.046), (0.048, 0.080, 0.034), p_bot=4.0, seg=28, rings=14, mi=0)             # upper (jade)
        kit.add_super(bm, (x, y - 0.058, 0.032), (0.040, 0.040, 0.026), seg=20, rings=12, mi=1)                        # toe cap (ivory)
        kit.add_super(bm, (x, y - 0.004, 0.077), (0.026, 0.030, 0.010), seg=16, rings=8, mi=1)                         # lace plate (ivory)
        out.append(kit.finish('Shoe' + suf, bm, [mats['jade'], mats['sole']]))
    return out
