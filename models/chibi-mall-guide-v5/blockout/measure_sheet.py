"""Measure the silhouette of reference sheet B (front and side views) and print per-row half-widths.
Run: blender --background --factory-startup --python measure_sheet.py -- SHEET.png OUT.json
The sheet has four equal-width views on a flat background: front, three-quarter, side, back.
"""
import bpy, sys, json
import numpy as np
src, out = sys.argv[sys.argv.index('--') + 1:][:2]
img = bpy.data.images.load(src)
w, h = img.size
px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)[:, :, :3][::-1]  # top row first
bg = np.median(np.concatenate([px[:10, :10].reshape(-1, 3), px[-10:, -10:].reshape(-1, 3)]), axis=0)
dist = np.linalg.norm(px - bg, axis=2)
mask = dist > 0.09
res = {'size': [w, h], 'bg': bg.round(3).tolist()}
cell = w // 4
for name, i in (('front', 0), ('side', 2)):
    m = mask[:, i * cell:(i + 1) * cell]
    rows = np.where(m.any(axis=1))[0]
    cols = np.where(m.any(axis=0))[0]
    top, bot = int(rows[0]), int(rows[-1])
    # per-row extents
    ext = []
    for y in range(top, bot + 1):
        xs = np.where(m[y])[0]
        ext.append([y, int(xs[0]), int(xs[-1])] if len(xs) else [y, -1, -1])
    res[name] = {'top': top, 'bottom': bot, 'height_px': bot - top + 1, 'x_min': int(cols[0]), 'x_max': int(cols[-1]), 'rows': ext}
json.dump(res, open(out, 'w'))
print('measured', {k: (v['top'], v['bottom'], v['x_min'], v['x_max']) for k, v in res.items() if isinstance(v, dict)})
