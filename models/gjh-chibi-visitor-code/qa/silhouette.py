"""Silhouette comparison between the model and the character sheet.

Both masks are reduced to their outer outline per row (left-most and right-most
figure pixel), which ignores inner gaps (between legs, arm and body) that the
sheet mask cannot resolve. Rows are compared at matching heights in metres,
after aligning both figures horizontally on the leg band.

Runs inside Blender. Usage: compare(out_dir) after the model is built.
"""
import json
import os

import bpy
import numpy as np

import config as C
import render


def load_mask(path):
    image = bpy.data.images.load(path, check_existing=False)
    w, h = image.size
    mask = np.array(image.pixels[:], dtype=np.float32).reshape(h, w, 4)[::-1, :, 0] > 0.5
    bpy.data.images.remove(image)
    return mask


def extents(mask):
    """Per-row (left, right) in pixels, NaN where the row is empty."""
    rows = mask.shape[0]
    left = np.full(rows, np.nan)
    right = np.full(rows, np.nan)
    for r in range(rows):
        xs = np.nonzero(mask[r])[0]
        if len(xs):
            left[r], right[r] = xs[0], xs[-1] + 1
    return left, right


def sample_reference(view, landmarks, z_values):
    ref = load_mask(os.path.join(landmarks["dir"], f"{view}-mask.png"))
    info = landmarks["views"][view]
    scale = info["px_per_m"]
    left, right = extents(ref)
    rows = np.clip(np.round(info["bottom"] - z_values * scale).astype(int), 0, ref.shape[0] - 1)
    l_m, r_m = left[rows] / scale, right[rows] / scale
    # The sheet top row is the crown; above it the reference has no figure.
    above = info["bottom"] - z_values * scale < info["top"]
    l_m[above] = np.nan
    r_m[above] = np.nan
    return l_m, r_m


def sample_model(mask, z_values):
    left, right = extents(mask)
    rows = np.clip(np.round(render.SIL_SIZE[1] / 2.0 - 0.5 - (z_values - render.SIL_CENTER_Z) * C.RENDER_PX_PER_M)
                   .astype(int), 0, mask.shape[0] - 1)
    return left[rows] / C.RENDER_PX_PER_M, right[rows] / C.RENDER_PX_PER_M


def band_center(left, right, z_values, band):
    sel = (z_values >= band[0]) & (z_values <= band[1]) & ~np.isnan(left)
    return float(np.mean((left[sel] + right[sel]) / 2.0))


def compare(out_dir, qa_dir, bands=None):
    """Render silhouettes, compare with the sheet, write overlays + JSON."""
    ref_dir = os.path.join(out_dir, "reference")
    with open(os.path.join(ref_dir, "landmarks.json")) as handle:
        landmarks = json.load(handle)
    landmarks["dir"] = ref_dir
    os.makedirs(qa_dir, exist_ok=True)
    step = 1.0 / C.RENDER_PX_PER_M
    z_values = np.arange(0.0, C.HEIGHT + 0.06, step)
    bands = bands or {"head": (0.80, 1.40), "body": (C.REF_TRUST_MIN_Z, 0.80)}
    result = {"px_per_m": C.RENDER_PX_PER_M, "views": {}}
    for view in ("front", "side", "back"):
        mask = render.silhouette(view, os.path.join(qa_dir, f"sil-{view}.png"))
        ml, mr = sample_model(mask, z_values)
        rl, rr = sample_reference(view, landmarks, z_values)
        # Align horizontally on the leg band (same rule for both figures).
        m_c = band_center(ml, mr, z_values, C.REF_ALIGN_BAND)
        r_c = band_center(rl, rr, z_values, C.REF_ALIGN_BAND)
        ml, mr = ml - m_c, mr - m_c
        rl, rr = rl - r_c, rr - r_c
        view_result = {"rows": {}}
        for band, (z0, z1) in bands.items():
            sel = (z_values >= z0) & (z_values < z1)
            both = sel & ~np.isnan(ml) & ~np.isnan(rl)
            only_one = sel & (np.isnan(ml) != np.isnan(rl))
            err = np.concatenate([np.abs(ml[both] - rl[both]), np.abs(mr[both] - rr[both])]) * C.RENDER_PX_PER_M
            # Rows where only one figure exists count as a full-width miss.
            miss = []
            for idx in np.nonzero(only_one)[0]:
                width = (mr[idx] - ml[idx]) if not np.isnan(ml[idx]) else (rr[idx] - rl[idx])
                miss.append(width / 2.0 * C.RENDER_PX_PER_M)
            all_err = np.concatenate([err, np.array(miss), np.array(miss)]) if miss else err
            inter, union = 0.0, 0.0
            for idx in np.nonzero(sel)[0]:
                a = (ml[idx], mr[idx]) if not np.isnan(ml[idx]) else None
                b = (rl[idx], rr[idx]) if not np.isnan(rl[idx]) else None
                if a and b:
                    inter += max(0.0, min(a[1], b[1]) - max(a[0], b[0]))
                    union += max(a[1], b[1]) - min(a[0], b[0])
                elif a or b:
                    w = (a or b)
                    union += w[1] - w[0]
            worst = []
            for idx in np.nonzero(both)[0]:
                for side_name, m_v, r_v in (("left", ml[idx], rl[idx]), ("right", mr[idx], rr[idx])):
                    worst.append((abs(m_v - r_v) * C.RENDER_PX_PER_M, round(float(z_values[idx]), 3), side_name,
                                  round(float(m_v), 3), round(float(r_v), 3)))
            for idx in np.nonzero(only_one)[0]:
                worst.append((999.0, round(float(z_values[idx]), 3), "row-only-in-" + ("model" if np.isnan(rl[idx]) else "sheet"),
                              None, None))
            worst.sort(key=lambda w: -w[0])
            view_result.setdefault("worst", {})[band] = [
                {"px": round(w[0], 1), "z": w[1], "edge": w[2], "model": w[3], "sheet": w[4]} for w in worst[:8]]
            view_result["rows"][band] = {
                "mean_px": round(float(np.mean(all_err)), 2) if len(all_err) else None,
                "max_px": round(float(np.max(all_err)), 2) if len(all_err) else None,
                "p90_px": round(float(np.percentile(all_err, 90)), 2) if len(all_err) else None,
                "iou": round(inter / union, 4) if union else None,
            }
        # Height of the figure: top row of the model vs the sheet.
        top_model = float(np.max(z_values[~np.isnan(ml)]))
        view_result["model_top_m"] = round(top_model, 4)
        view_result["profile"] = profile_rows(z_values, ml, mr, rl, rr)
        result["views"][view] = view_result
        write_overlay(view, mask, z_values, rl + m_c, rr + m_c, os.path.join(qa_dir, f"overlay-{view}.png"))
    with open(os.path.join(qa_dir, "silhouette.json"), "w") as handle:
        json.dump(result, handle, indent=2)
    return result


def profile_rows(z_values, ml, mr, rl, rr, every=0.05):
    rows = []
    for z in np.arange(0.10, 1.31, every):
        i = int(np.argmin(np.abs(z_values - z)))
        def r3(v):
            return None if np.isnan(v) else round(float(v), 3)
        rows.append({"z": round(float(z), 2), "model": [r3(ml[i]), r3(mr[i])], "sheet": [r3(rl[i]), r3(rr[i])]})
    return rows


def write_overlay(view, mask, z_values, rl, rr, path):
    """Model silhouette in grey with the sheet outline (red) drawn on top."""
    h, w = mask.shape
    img = np.zeros((h, w, 4), dtype=np.float32)
    img[..., 3] = 1.0
    img[mask, :3] = 0.55
    for z, l, r in zip(z_values, rl, rr):
        if np.isnan(l):
            continue
        row = int(round(h / 2.0 - 0.5 - (z - render.SIL_CENTER_Z) * C.RENDER_PX_PER_M))
        if 0 <= row < h:
            for x in (l, r):
                col = int(round(x * C.RENDER_PX_PER_M))
                if 0 <= col < w:
                    img[row, col, :3] = (1.0, 0.1, 0.1)
    image = bpy.data.images.new(os.path.basename(path), w, h, alpha=True)
    image.pixels[:] = img[::-1].ravel()
    image.filepath_raw = path
    image.file_format = "PNG"
    image.save()
    bpy.data.images.remove(image)
