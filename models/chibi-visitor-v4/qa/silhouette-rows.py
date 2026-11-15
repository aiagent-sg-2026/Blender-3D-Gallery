import bpy, numpy as np, sys
S = sys.argv[sys.argv.index('--') + 1]
def load(p):
    im = bpy.data.images.load(p); w, h = im.size
    return np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4)[::-1].copy()
def mask(a):
    bg = a[:, :3, :3].mean(1, keepdims=True)
    return np.abs(a[:, :, :3] - bg).max(2) > 0.06
ref = load(S + "/ref.png")
cx = {"front": 215, "side": 575, "back": 920}
for n, c in cx.items():
    r = mask(ref[170:850, c - 185:c + 185]); m_ = mask(load(S + "/r/" + n + ".png"))
    print(n, "(z: ref L/R half-width px | mine L/R | diff)")
    for y in range(14, 300, 13):
        out = []
        for mk in (r, m_):
            xs = np.where(mk[y])[0]
            out.append((185 - xs.min(), xs.max() - 185) if len(xs) else (0, 0))
        z = (829 - (170 + y)) / 645
        print("  z=%.3f  ref %4d %4d | mine %4d %4d | d %+4d %+4d" % (z, *out[0], *out[1], out[1][0] - out[0][0], out[1][1] - out[0][1]))
