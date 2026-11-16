"""Sample flat colours from reference sheet B (front cell). Run in Blender: blender -b --python parts_palette.py -- OUT.json"""
import bpy, sys, json, numpy as np
out = sys.argv[sys.argv.index('--') + 1]
img = bpy.data.images.load('models/chibi-mall-guide-v5/reference/turnaround-b.png')
w, h = img.size
px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)[:, :, :3][::-1]   # top row first, linear values
SPOTS = {  # (x in front cell, y in sheet) chosen on flat areas of each part
    'vest_jade': (232, 540), 'shirt_ivory': (193, 505), 'shorts_charcoal': (215, 640), 'skin_arm': (172, 560),
    'sock_ivory': (215, 735), 'shoe_jade': (330, 792), 'sole_ivory': (200, 806), 'cap_jade': (250, 100),
    'brass_pin': (338, 115), 'glove_white': (368, 612), 'hair_brown': (250, 195), 'badge_brass': (306, 503)}
res = {}
for k, (x, y) in SPOTS.items():
    patch = px[y - 2:y + 3, x - 2:x + 3].reshape(-1, 3); m = np.median(patch, axis=0)
    srgb = np.where(m <= 0.0031308, m * 12.92, 1.055 * np.power(np.maximum(m, 0), 1 / 2.4) - 0.055)
    res[k] = {'linear': m.round(4).tolist(), 'hex': '%02X%02X%02X' % tuple(int(round(c * 255)) for c in srgb)}
json.dump(res, open(out, 'w'), indent=1); print(json.dumps({k: v['hex'] for k, v in res.items()}))
