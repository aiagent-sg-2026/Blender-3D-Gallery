"""Build the primitive blockout, render orthographic front and side silhouettes at 751 px/m and compare them with sheet B.
Run (repository root): blender --background --factory-startup --python-exit-code 1 \
    --python models/chibi-mall-guide-v5/blockout/build_and_compare.py -- OUT_DIR
Comparison rows are sheet rows from the cap top. Front: right half-width about the body centre line (the sign prop sits on the left).
Side: rear extent, and front extent outside the rows the sign and hand cover (sheet rows 330..520).
"""
import bpy, bmesh, sys, os, json, math
import numpy as np
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import config as C
OUT = sys.argv[sys.argv.index('--') + 1]; os.makedirs(OUT, exist_ok=True)
ref = json.load(open(os.path.join(HERE, 'sheet-b-silhouette.json')))

bpy.ops.wm.read_factory_settings(use_empty=True)
def ellipsoid(name, c, r, rz_bot=None, seg=48, rings=32, p_bot=2.0, p_top=2.0):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=1.0)
    for v in bm.verts:
        z = v.co.z; rz = r[2] if (rz_bot is None or z >= 0) else rz_bot
        f = 1.0
        pp = p_bot if z < 0 else p_top
        if pp != 2.0 and abs(z) < 0.9999: f = math.sqrt(max(0.0, 1 - abs(z) ** pp)) / math.sqrt(1 - z * z)
        v.co = Vector((v.co.x * f * r[0] + c[0], v.co.y * f * r[1] + c[1], z * rz + c[2]))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    for p in me.polygons: p.use_smooth = True
    return o
for name, p in C.PARTS.items():
    if p.get('mirror'):
        for side, sx in (('.L', 1), ('.R', -1)):
            ellipsoid(name + side, (sx * p['c'][0], p['c'][1], p['c'][2]), p['r'], p_bot=p.get('p_bot', 2.0), p_top=p.get('p_top', 2.0))
    else:
        ellipsoid(name, p['c'], p['r'], p.get('rz_bot'), p_bot=p.get('p_bot', 2.0), p_top=p.get('p_top', 2.0))

# ---- render silhouettes: orthographic, 800x800 at exactly SHEET_PX_PER_M ----
N = 800; ORTHO = N / C.SHEET_PX_PER_M
sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'; sc.render.resolution_x = N; sc.render.resolution_y = N
sc.render.film_transparent = True; sc.display.shading.light = 'FLAT'; sc.display.shading.color_type = 'SINGLE'
sc.display.shading.single_color = (1, 1, 1); sc.render.image_settings.file_format = 'PNG'
sc.view_settings.view_transform = 'Standard'
cam_d = bpy.data.cameras.new('cam'); cam_d.type = 'ORTHO'; cam_d.ortho_scale = ORTHO
cam = bpy.data.objects.new('cam', cam_d); sc.collection.objects.link(cam); sc.camera = cam
CENTRE_Z = 0.5 + 0.02   # lift the frame slightly so nothing is clipped
def shot(name, loc, rot):
    cam.location = loc; cam.rotation_euler = rot
    sc.render.filepath = os.path.join(OUT, name + '.png'); bpy.ops.render.render(write_still=True)
    img = bpy.data.images.load(sc.render.filepath); a = np.array(img.pixels[:], dtype=np.float32).reshape(N, N, 4)[::-1]
    return a[:, :, 3] > 0.5
front = shot('blockout-front', (0, -4, CENTRE_Z), (math.radians(90), 0, 0))
side = shot('blockout-side', (4, 0, CENTRE_Z), (math.radians(90), 0, math.radians(90)))

def rows_of(mask):
    ys = np.where(mask.any(axis=1))[0]; top, bot = int(ys[0]), int(ys[-1])
    ext = {}
    for y in range(top, bot + 1):
        xs = np.where(mask[y])[0]; ext[y - top] = (int(xs[0]), int(xs[-1]))
    return top, bot, ext
ft, fb, fext = rows_of(front); st, sb, sext = rows_of(side)
report = {'px_per_m': C.SHEET_PX_PER_M, 'render_height_px': fb - ft + 1, 'sheet_height_px': ref['front']['height_px']}

# front: half-width (right of centre) per sheet row
rf = ref['front']['rows']; cx_sheet = sum((r[1] + r[2]) / 2 for r in rf[10:60]) / 50
errs = []
for i, (y, a, b) in enumerate(rf):
    if i not in fext: continue
    sheet_hw = b - cx_sheet; ours = fext[i][1] - N / 2   # our +x is image right = character's left (no prop)
    errs.append((i, ours - sheet_hw))
e = np.array([x[1] for x in errs])
report['front'] = dict(rows=len(e), mean_abs_px=float(np.abs(e).mean()), max_abs_px=float(np.abs(e).max()), bias_px=float(e.mean()),
                       worst_rows=[errs[j][0] for j in np.argsort(-np.abs(e))[:5]])
# side: rear extent and front extent (excluding sign/hand rows), aligned by one fitted shift; sheet y axis same rows
rs = ref['side']['rows']
def side_err(use_front):
    d = []
    for i, (y, a, b) in enumerate(rs):
        if i not in sext: continue
        if use_front:
            if 330 <= i <= 520: continue
            d.append(sext[i][0] - a)
        else:
            d.append(sext[i][1] - b)
    return np.array(d)
sr, sf = side_err(False), side_err(True)
shift = float(np.median(np.concatenate([sr, sf])))   # one common x shift of the render against the sheet
report['side'] = dict(shift_px=shift,
    rear=dict(mean_abs_px=float(np.abs(sr - shift).mean()), max_abs_px=float(np.abs(sr - shift).max())),
    front=dict(mean_abs_px=float(np.abs(sf - shift).mean()), max_abs_px=float(np.abs(sf - shift).max())))
bands = []
for i in range(0, 751, 50):
    sr_ = rf[i][2] - cx_sheet if i < len(rf) else None
    o_ = fext[i][1] - N / 2 if i in fext else None
    sf_ = (rs[i][1], rs[i][2]) if i < len(rs) else None
    os_ = (sext[i][0] - shift, sext[i][1] - shift) if i in sext else None
    bands.append(dict(row=i, front_sheet=sr_, front_ours=o_, side_sheet=sf_, side_ours=os_))
report['bands'] = bands
mm = C.GATE_MEAN_M * C.SHEET_PX_PER_M; mx = C.GATE_MAX_M * C.SHEET_PX_PER_M
report['gate_px'] = dict(mean=mm, max=mx)
report['pass'] = dict(front=bool(report['front']['mean_abs_px'] <= mm and report['front']['max_abs_px'] <= mx),
                      side=bool(max(report['side']['rear']['mean_abs_px'], report['side']['front']['mean_abs_px']) <= mm and
                                max(report['side']['rear']['max_abs_px'], report['side']['front']['max_abs_px']) <= mx))

# ---- overlay PNG in sheet pixel space: sheet silhouette (grey) vs blockout (red outline) ----
def overlay(name, cell_idx, mask, top_o, offset):
    sw = ref['size'][0] // 4; H = ref['size'][1]
    src = bpy.data.images.load(os.path.join(HERE, '..', 'reference', 'turnaround-b.png'))
    px = np.array(src.pixels[:], dtype=np.float32).reshape(ref['size'][1], ref['size'][0], 4)[::-1][:, cell_idx * sw:(cell_idx + 1) * sw, :3].copy()
    top_s = ref['front']['top'] if cell_idx == 0 else ref['side']['top']
    ys, xs = np.where(mask)
    # edge of mask
    edge = mask & ~(np.roll(mask, 1, 0) & np.roll(mask, -1, 0) & np.roll(mask, 1, 1) & np.roll(mask, -1, 1))
    ey, ex = np.where(edge)
    for y, x in zip(ey, ex):
        sy = top_s + (y - top_o); sx = int(round(x + offset))
        if 0 <= sy < H and 0 <= sx < sw: px[sy, sx] = (1, 0, 0)
    out = np.dstack([px, np.ones(px.shape[:2], dtype=np.float32)])[::-1]
    im = bpy.data.images.new(name, sw, H, alpha=True); im.pixels = out.reshape(-1).tolist()
    im.filepath_raw = os.path.join(OUT, name + '.png'); im.file_format = 'PNG'; im.save()
overlay('overlay-front', 0, front, ft, cx_sheet - N / 2)
overlay('overlay-side', 2, side, st, -shift)
json.dump(report, open(os.path.join(OUT, 'blockout-report.json'), 'w'), indent=1)
print(json.dumps(report))
