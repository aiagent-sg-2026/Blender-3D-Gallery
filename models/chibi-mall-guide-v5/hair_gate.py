"""Silhouette gate for the head rows (sheet rows 0..360: cap, hair, face) against reference sheet B, using the whole built figure.
Run: blender --background --factory-startup --python-exit-code 1 --python models/chibi-mall-guide-v5/hair_gate.py -- OUT_DIR
Same method and thresholds as blockout/build_and_compare.py (mean 8 px / max 15 px at 645 px/m, converted to 751 px/m).
Front: right-hand half-width about the centre line (the sign prop is on the other side). Side: rear and front extents, one common x shift
fitted on the body rows (sheet rows 380..750, excluding the sign rows 330..520 for the front extent)."""
import bpy, bmesh, sys, os, json, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import config as C, figure
OUT = sys.argv[sys.argv.index('--') + 1]; os.makedirs(OUT, exist_ok=True)
ref = json.load(open(os.path.join(HERE, 'blockout', 'sheet-b-silhouette.json')))
HEAD_ROWS = 360; V4_ROWS = 300   # v4's G4 used head rows at z >= 0.60 m (sheet rows 0..300); rows up to 360 also include chin, neck and collar
bpy.ops.wm.read_factory_settings(use_empty=True)
mats, parts, placeholders = figure.build_all(bpy, bmesh)
N = 800; ORTHO = N / C.SHEET_PX_PER_M; sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'; sc.render.resolution_x = N; sc.render.resolution_y = N; sc.render.film_transparent = True
sc.display.shading.light = 'FLAT'; sc.display.shading.color_type = 'SINGLE'; sc.display.shading.single_color = (1, 1, 1)
sc.view_settings.view_transform = 'Standard'
cd = bpy.data.cameras.new('cam'); cd.type = 'ORTHO'; cd.ortho_scale = ORTHO
cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam
def shot(name, loc, rot):
    cam.location = loc; cam.rotation_euler = rot; sc.render.filepath = os.path.join(OUT, name + '.png'); bpy.ops.render.render(write_still=True)
    a = np.array(bpy.data.images.load(sc.render.filepath).pixels[:], dtype=np.float32).reshape(N, N, 4)[::-1]; return a[:, :, 3] > 0.5
front = shot('gate-front', (0, -4, 0.54), (math.radians(90), 0, 0)); side = shot('gate-side', (4, 0, 0.54), (math.radians(90), 0, math.radians(90)))
def rows_of(mask):
    ys = np.where(mask.any(axis=1))[0]; top = int(ys[0]); ext = {}
    for y in range(top, int(ys[-1]) + 1):
        xs = np.where(mask[y])[0]
        if len(xs): ext[y - top] = (int(xs[0]), int(xs[-1]))
    return top, ext
ft, fext = rows_of(front); st, sext = rows_of(side)
rf = ref['front']['rows']; rs = ref['side']['rows']; cx = sum((r[1] + r[2]) / 2 for r in rf[10:60]) / 50
# one shift for the side view, fitted on body rows
d = []
for i in range(380, 750):
    if i in sext and i < len(rs):
        d.append(sext[i][1] - rs[i][2])
        if not 330 <= i <= 520: d.append(sext[i][0] - rs[i][1])
shift = float(np.median(d))
def series(R):
    return (np.array([(fext[i][1] - N / 2) - (rf[i][2] - cx) for i in range(0, R) if i in fext]),
            np.array([(sext[i][1] - shift) - rs[i][2] for i in range(0, R) if i in sext]),
            np.array([(sext[i][0] - shift) - rs[i][1] for i in range(0, R) if i in sext and not 330 <= i <= 520]))
fe, sr, sf = series(HEAD_ROWS); fe3, sr3, sf3 = series(V4_ROWS)
mm, mx = C.GATE_MEAN_M * C.SHEET_PX_PER_M, C.GATE_MAX_M * C.SHEET_PX_PER_M
def stat(e): return dict(mean_abs_px=round(float(np.abs(e).mean()), 1), max_abs_px=round(float(np.abs(e).max()), 1), bias_px=round(float(e.mean()), 1),
                         worst_rows=[int(j) for j in np.argsort(-np.abs(e))[:4]])
rep = dict(rows=f'0..{HEAD_ROWS}', gate_px=dict(mean=round(mm, 1), max=round(mx, 1)), side_shift_px=shift,
           front=stat(fe), side_rear=stat(sr), side_front=stat(sf))
rep['rows_0_300'] = dict(front=stat(fe3), side_rear=stat(sr3), side_front=stat(sf3))
rep['pass'] = {k: bool(rep[k]['mean_abs_px'] <= mm and rep[k]['max_abs_px'] <= mx) for k in ('front', 'side_rear', 'side_front')}
rep['pass_rows_0_300'] = {k: bool(rep['rows_0_300'][k]['mean_abs_px'] <= mm and rep['rows_0_300'][k]['max_abs_px'] <= mx) for k in ('front', 'side_rear', 'side_front')}
band = []
for i in range(0, HEAD_ROWS + 1, 30):
    band.append(dict(row=i, front=(round(rf[i][2] - cx), round(fext[i][1] - N / 2)) if i in fext else None,
                     side=((rs[i][1], rs[i][2]), (round(sext[i][0] - shift), round(sext[i][1] - shift))) if i in sext else None))
rep['bands'] = band
json.dump(rep, open(os.path.join(OUT, 'hair-gate.json'), 'w'), indent=1)
def overlay(name, cell, mask, top_o, offset, rows=HEAD_ROWS + 40):
    sw = ref['size'][0] // 4; H = ref['size'][1]
    src = bpy.data.images.load(os.path.join(HERE, 'reference', 'turnaround-b.png'))
    px = np.array(src.pixels[:], dtype=np.float32).reshape(ref['size'][1], ref['size'][0], 4)[::-1][:, cell * sw:(cell + 1) * sw, :3].copy()
    top_s = ref['front']['top'] if cell == 0 else ref['side']['top']
    edge = mask & ~(np.roll(mask, 1, 0) & np.roll(mask, -1, 0) & np.roll(mask, 1, 1) & np.roll(mask, -1, 1))
    for y, x in zip(*np.where(edge)):
        sy = top_s + (y - top_o); sx = int(round(x + offset))
        if top_s <= sy < top_s + rows and 0 <= sx < sw: px[sy, sx] = (1, 0, 0)
    crop = px[top_s - 5: top_s + rows]
    out = np.dstack([crop, np.ones(crop.shape[:2], dtype=np.float32)])[::-1]
    im = bpy.data.images.new(name, sw, crop.shape[0], alpha=True); im.pixels = out.reshape(-1).tolist()
    im.filepath_raw = os.path.join(OUT, name + '.png'); im.file_format = 'PNG'; im.save()
overlay('gate-overlay-front', 0, front, ft, cx - N / 2); overlay('gate-overlay-side', 2, side, st, -shift)
print('GATE', json.dumps({k: rep[k] for k in ('front', 'side_rear', 'side_front', 'pass', 'rows_0_300', 'pass_rows_0_300', 'gate_px', 'side_shift_px')}))
