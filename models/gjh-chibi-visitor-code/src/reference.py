"""Stage 0: cut the front, side and back views out of the owner's character sheet
and turn each into a binary silhouette mask that later stages compare against.

Runs inside Blender (bpy + numpy only). Writes PNG crops, PNG masks and
reference/landmarks.json with pixel bounds and the derived pixels-per-metre.
"""
import json
import os

import bpy
import numpy as np

import config as C


def load_sheet(path):
    image = bpy.data.images.load(path, check_existing=True)
    width, height = image.size
    pixels = np.array(image.pixels[:], dtype=np.float32).reshape(height, width, 4)
    # Blender stores rows bottom-up; flip so row 0 is the top of the sheet.
    return (pixels[::-1, :, :3] * 255.0).astype(np.float32)


def save_png(array, path):
    """Save an HxW (mask) or HxWx3 (colour) array, row 0 at the top."""
    height, width = array.shape[:2]
    rgba = np.ones((height, width, 4), dtype=np.float32)
    if array.ndim == 2:
        rgba[..., :3] = array[..., None].astype(np.float32)
    else:
        rgba[..., :3] = array / 255.0
    image = bpy.data.images.new(os.path.basename(path), width, height, alpha=False)
    image.pixels[:] = rgba[::-1].ravel()
    image.filepath_raw = path
    image.file_format = "PNG"
    image.save()
    bpy.data.images.remove(image)


def flood_background(passable):
    """Flood fill from the crop border through passable pixels (4-connected)."""
    filled = np.zeros_like(passable)
    filled[0, :] = passable[0, :]
    filled[-1, :] = passable[-1, :]
    filled[:, 0] = passable[:, 0]
    filled[:, -1] = passable[:, -1]
    while True:
        grown = filled.copy()
        grown[1:, :] |= filled[:-1, :]
        grown[:-1, :] |= filled[1:, :]
        grown[:, 1:] |= filled[:, :-1]
        grown[:, :-1] |= filled[:, 1:]
        grown &= passable
        if np.array_equal(grown, filled):
            return filled
        filled = grown


def largest_component(mask):
    """Keep the largest 4-connected component (drops stray specks)."""
    labels = np.zeros(mask.shape, dtype=np.int32)
    best_label, best_size, current = 0, 0, 0
    ys, xs = np.nonzero(mask)
    for y0, x0 in zip(ys, xs):
        if labels[y0, x0]:
            continue
        current += 1
        stack = [(y0, x0)]
        labels[y0, x0] = current
        size = 0
        while stack:
            y, x = stack.pop()
            size += 1
            for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if 0 <= ny < mask.shape[0] and 0 <= nx < mask.shape[1] and mask[ny, nx] and not labels[ny, nx]:
                    labels[ny, nx] = current
                    stack.append((ny, nx))
        if size > best_size:
            best_label, best_size = current, size
    return labels == best_label


def silhouette(rgb, cut_floor_row):
    # The background is a smooth vertical gradient, so estimate it per row from
    # the crop's left and right border strips (which never contain the figure).
    strip = C.REF_BG_STRIP
    border = np.concatenate([rgb[:, :strip], rgb[:, -strip:]], axis=1)
    background_row = np.median(border, axis=1)  # H x 3
    distance = np.abs(rgb - background_row[:, None, :]).max(axis=2)
    # The background is cool (blue above red); the tee is a warm white of
    # similar brightness, so compare the blue-minus-red tint as well.
    tint = rgb[..., 2] - rgb[..., 0]
    background_tint = background_row[:, 2] - background_row[:, 0]
    tint_gap = np.abs(tint - background_tint[:, None])
    # Floor shadow and the soft halo round the figure stay under both limits.
    passable = (distance <= C.REF_BG_DISTANCE) & (tint_gap <= C.REF_BG_TINT_GAP)
    background = flood_background(passable)
    # Anything the border fill cannot reach is figure, which also fills the
    # lit parts of the white shoes that match the background colour.
    figure = ~background
    # Everything below the sole line is floor shadow or label, never figure.
    figure[cut_floor_row:, :] = False
    return largest_component(figure)


def mask_edge(mask):
    inner = mask.copy()
    inner[1:, :] &= mask[:-1, :]
    inner[:-1, :] &= mask[1:, :]
    inner[:, 1:] &= mask[:, :-1]
    inner[:, :-1] &= mask[:, 1:]
    return mask & ~inner


def outline_overlay(rgb, mask, colour=(255.0, 0.0, 0.0)):
    """Crop with the mask outline drawn on it, for eyeballing the mask."""
    overlay = rgb.copy()
    overlay[mask_edge(mask)] = colour
    return overlay


def build(out_dir):
    ref_dir = os.path.join(out_dir, "reference")
    sheet = load_sheet(os.path.join(ref_dir, C.REF_SHEET))
    result = {"sheet": C.REF_SHEET, "views": {}}
    for view, box in C.REF_VIEWS.items():
        x0, y0, x1, y1 = box["crop"]
        crop = sheet[y0:y1, x0:x1]
        mask = silhouette(crop, box["floor_row"] - y0)
        ys, xs = np.nonzero(mask)
        top, bottom = int(ys.min()), int(ys.max())
        left, right = int(xs.min()), int(xs.max())
        height_px = bottom - top + 1
        save_png(crop, os.path.join(ref_dir, f"{view}.png"))
        save_png(mask.astype(np.float32), os.path.join(ref_dir, f"{view}-mask.png"))
        save_png(outline_overlay(crop, mask), os.path.join(ref_dir, f"{view}-overlay.png"))
        result["views"][view] = {
            "crop": box["crop"],
            "top": top, "bottom": bottom, "left": left, "right": right,
            "height_px": height_px,
            "px_per_m": height_px / C.HEIGHT,
            "area_px": int(mask.sum()),
        }
    heights = [v["height_px"] for v in result["views"].values()]
    result["height_spread"] = (max(heights) - min(heights)) / max(heights)
    with open(os.path.join(ref_dir, "landmarks.json"), "w") as handle:
        json.dump(result, handle, indent=2)
    return result


def gate(result):
    """Stage 0 gate: the three views agree on figure height within 2 %."""
    return {
        "stage": 0,
        "name": "reference",
        "checks": [{
            "name": "view height spread",
            "value": round(result["height_spread"], 4),
            "limit": C.REF_MAX_HEIGHT_SPREAD,
            "pass": result["height_spread"] <= C.REF_MAX_HEIGHT_SPREAD,
        }],
    }
