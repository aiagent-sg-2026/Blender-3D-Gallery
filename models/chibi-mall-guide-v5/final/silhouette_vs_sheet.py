"""Silhouette overlap of the rigged guide (rest pose) with reference sheet B, front, side and back.
Both silhouettes are put at 751 px per metre, feet on the same row, and centred by the x-centroid of their masks; the sheet's held sign is part of both.
Run: blender --background GUIDE.blend --python silhouette_vs_sheet.py -- SHEET.png OUT.json OUT_OVERLAY.png"""
import bpy, sys, json, math
import numpy as np
sheet_path, out_json, out_png = sys.argv[sys.argv.index('--') + 1:][:3]
sc = bpy.context.scene; rig = bpy.data.objects['Rig']; rig.animation_data_clear()
for o in bpy.data.objects:
    if o.type == 'MESH': o.hide_render = False
N = 800; sc.render.engine = 'BLENDER_WORKBENCH'; sc.render.resolution_x = N; sc.render.resolution_y = N; sc.render.film_transparent = True
sc.display.shading.light = 'FLAT'; sc.display.shading.color_type = 'SINGLE'; sc.display.shading.single_color = (1, 1, 1)
cd = bpy.data.cameras.new('cam'); cd.type = 'ORTHO'; cd.ortho_scale = N / 751.0; cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam
def ours(az):
    a = math.radians(az); cam.location = (math.sin(a) * 4, -math.cos(a) * 4, 0.54); cam.rotation_euler = (math.radians(90), 0, a)
    sc.render.filepath = '/tmp/_sil.png'; bpy.ops.render.render(write_still=True)
    return np.array(bpy.data.images.load('/tmp/_sil.png').pixels[:], dtype=np.float32).reshape(N, N, 4)[::-1][:, :, 3] > 0.5
sh = bpy.data.images.load(sheet_path); W, H = sh.size; px = np.array(sh.pixels[:], dtype=np.float32).reshape(H, W, 4)[:, :, :3][::-1]
bg = np.median(np.concatenate([px[:10, :10].reshape(-1, 3), px[-10:, -10:].reshape(-1, 3)]), axis=0); smask = np.linalg.norm(px - bg, axis=2) > 0.09; cell = W // 4
def place(mask):
    ys, xs = np.where(mask); bottom = ys.max(); cx = xs.mean(); out = np.zeros((N, N), dtype=bool); return mask, bottom, cx
res = {}; tiles = []
for name, cidx, az in (('front', 0, 0), ('side', 2, 90), ('back', 3, 180)):
    m_s = smask[:, cidx * cell:(cidx + 1) * cell]; m_o = ours(az)
    def crop(m, bottom_target=620, w=N):
        ys, xs = np.where(m); b = ys.max(); cx = int(xs.mean()); out = np.zeros((N, N), dtype=bool)
        for y, x in zip(ys, xs):
            yy = y - b + bottom_target; xx = x - cx + N // 2
            if 0 <= yy < N and 0 <= xx < N: out[yy, xx] = True
        return out
    a_s, a_o = crop(m_s), crop(m_o); iou = (a_s & a_o).sum() / (a_s | a_o).sum(); res[name] = round(float(iou), 3)
    img = np.ones((N, N, 3), dtype=np.float32) * np.array([0.92, 0.91, 0.97]); img[a_s] = (0.35, 0.50, 0.95); img[a_o & ~a_s] = (0.95, 0.30, 0.30); img[a_o & a_s] = (0.55, 0.40, 0.65); tiles.append(img[60:700])
json.dump(res, open(out_json, 'w')); sheet = np.concatenate(tiles, axis=1); o = np.dstack([sheet, np.ones(sheet.shape[:2], dtype=np.float32)])[::-1]
im = bpy.data.images.new('o', sheet.shape[1], sheet.shape[0], alpha=True); im.pixels = o.reshape(-1).tolist(); im.filepath_raw = out_png; im.file_format = 'PNG'; im.save(); print('IOU', res)
