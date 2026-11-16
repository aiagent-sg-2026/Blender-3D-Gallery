"""Materials and procedurally painted textures (numpy -> PNG -> packed image).

Atlas rows are painted top-down (row 0 = top of the image); `save_texture`
flips them into Blender's bottom-up pixel order. UV v = 1 - row / size.
"""
import math
import os

import bpy
import numpy as np

import config as C


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_rgb(hex_string):
    h = hex_string.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def linear(hex_string):
    return tuple(srgb_to_linear(c) for c in hex_rgb(hex_string)) + (1.0,)


# ------------------------------------------------------------------ painting helpers
def canvas(width, height, hex_string):
    img = np.zeros((height, width, 3), dtype=np.float32)
    img[...] = hex_rgb(hex_string)
    return img


def grid(height, width):
    ys, xs = np.mgrid[0:height, 0:width].astype(np.float32)
    return xs + 0.5, ys + 0.5


def ellipse_mask(xs, ys, cx, cy, rx, ry, soft=1.5):
    d = np.sqrt(((xs - cx) / rx) ** 2 + ((ys - cy) / ry) ** 2)
    edge = soft / max(min(rx, ry), 1.0)
    return np.clip((1.0 - d) / edge + 0.5, 0.0, 1.0)


def blend(img, mask, colour):
    colour = np.array(colour, dtype=np.float32)
    img[...] = img * (1.0 - mask[..., None]) + colour * mask[..., None]


def save_texture(img, path, name):
    height, width = img.shape[:2]
    rgba = np.ones((height, width, 4), dtype=np.float32)
    rgba[..., :3] = np.clip(img, 0.0, 1.0)
    image = bpy.data.images.new(name, width, height, alpha=False)
    image.pixels[:] = rgba[::-1].ravel()
    image.filepath_raw = path
    image.file_format = "PNG"
    image.save()
    # Reload from disk so the exporter embeds exactly the saved PNG bytes.
    bpy.data.images.remove(image)
    loaded = bpy.data.images.load(path)
    loaded.name = name
    loaded.colorspace_settings.name = "sRGB"
    loaded.pack()
    return loaded


# ------------------------------------------------------------------ face atlas
# Regions in atlas pixels (x0, y0, x1, y1), top-left origin, for a 512 atlas.
ATLAS = {
    "eye": (0, 0, 256, 256),
    "brow": (256, 0, 512, 64),
    "mouth_line": (256, 64, 512, 128),
    "mouth_open": (256, 128, 512, 256),
    "blush": (0, 256, 256, 512),
    "nose": (256, 256, 384, 384),
    "skin": (384, 256, 512, 384),
    "eye_closed": (256, 384, 512, 512),
}


def atlas_uv(region, u, v):
    """Map local (u, v) in 0..1 (v up) inside an atlas region to atlas UVs."""
    x0, y0, x1, y1 = ATLAS[region]
    size = float(C.FACE_ATLAS_SIZE)
    x = x0 + (x1 - x0) * u
    y_top = y0 + (y1 - y0) * (1.0 - v)
    return (x / size, 1.0 - y_top / size)


def paint_face_atlas():
    size = C.FACE_ATLAS_SIZE
    img = canvas(size, size, C.PALETTE["skin"])
    xs, ys = grid(size, size)

    # Eye: white sclera ellipse, big gradient iris, pupil, highlights, lash line.
    x0, y0, x1, y1 = ATLAS["eye"]
    sub = (slice(y0, y1), slice(x0, x1))
    ex, ey = xs[sub] - x0, ys[sub] - y0
    eye = img[sub]
    blend(eye, np.ones_like(ex), (1.0, 1.0, 1.0))
    eye[...] = np.array(hex_rgb("#FBF8F6"))
    # Near-black iris (sheet), warming to a dark brown at the bottom.
    iris_top, iris_bottom = np.array(hex_rgb("#0C0705")), np.array(hex_rgb("#4A2C1E"))
    t = np.clip((ey - 40.0) / 200.0, 0.0, 1.0)[..., None]
    iris_colour = iris_top * (1 - t) + iris_bottom * t
    # Chibi eyes are almost all iris: only a thin white shows at the sides.
    iris = ellipse_mask(ex, ey, 128, 138, 110, 122)
    eye[...] = eye * (1 - iris[..., None]) + iris_colour * iris[..., None]
    ring_mask = np.clip(iris - ellipse_mask(ex, ey, 128, 138, 98, 110), 0, 1)
    blend(eye, ring_mask * 0.6, hex_rgb("#120806"))
    blend(eye, ellipse_mask(ex, ey, 128, 146, 50, 56), hex_rgb("#0B0605"))
    blend(eye, ellipse_mask(ex, ey, 88, 86, 36, 30), (1.0, 1.0, 1.0))
    blend(eye, ellipse_mask(ex, ey, 170, 196, 15, 13), (1.0, 1.0, 1.0))
    blend(eye, ellipse_mask(ex, ey, 154, 64, 9, 8) * 0.85, (1.0, 1.0, 1.0))
    # Heavy upper lash line following the top of the eye outline, with a small
    # wing at the outer corner (u -> 1 is the outer corner for both eyes).
    outer = ellipse_mask(ex, ey, 128, 128, 128, 128, soft=1.0)
    inner = ellipse_mask(ex, ey, 128, 164, 116, 120, soft=1.0)
    lash = np.clip(outer - inner, 0, 1) * (ey < 132)
    blend(eye, lash, hex_rgb("#120A07"))
    wing = ellipse_mask(ex, ey, 226, 58, 30, 15) * (ex > 196)
    blend(eye, wing, hex_rgb("#120A07"))
    # Soft lower lid shade.
    lower = np.clip(outer - ellipse_mask(ex, ey, 128, 120, 124, 126, soft=1.0), 0, 1) * (ey > 170)
    blend(eye, lower * 0.5, hex_rgb("#8C6A5A"))

    # Closed eye / happy arc graphic: dark lash colour, slightly lighter centre.
    x0, y0, x1, y1 = ATLAS["eye_closed"]
    img[y0:y1, x0:x1] = np.array(hex_rgb("#1A100C"))

    for region, colour in (("brow", C.PALETTE["brow"]), ("mouth_line", C.PALETTE["mouth"])):
        x0, y0, x1, y1 = ATLAS[region]
        img[y0:y1, x0:x1] = np.array(hex_rgb(colour))

    # Open mouth: dark red throat at the top band, white teeth strip, pink tongue.
    x0, y0, x1, y1 = ATLAS["mouth_open"]
    sub = (slice(y0, y1), slice(x0, x1))
    mx, my = xs[sub] - x0, ys[sub] - y0
    mouth = img[sub]
    mouth[...] = np.array(hex_rgb("#6E2622"))
    blend(mouth, (my < 22).astype(np.float32), hex_rgb("#FFFFFF"))
    blend(mouth, ellipse_mask(mx, my, 128, 128, 92, 46), hex_rgb("#E07A72"))

    # Blush: radial gradient from pink to skin at the edge.
    x0, y0, x1, y1 = ATLAS["blush"]
    sub = (slice(y0, y1), slice(x0, x1))
    bx, by = xs[sub] - x0, ys[sub] - y0
    d = np.sqrt(((bx - 128) / 128) ** 2 + ((by - 128) / 128) ** 2)
    strength = np.clip(1.0 - d, 0.0, 1.0) ** 1.4 * 0.75
    blend(img[sub], strength, hex_rgb(C.PALETTE["blush"]))

    # Nose: faint warm shade, fading to skin.
    x0, y0, x1, y1 = ATLAS["nose"]
    sub = (slice(y0, y1), slice(x0, x1))
    nx, ny = xs[sub] - x0, ys[sub] - y0
    d = np.sqrt(((nx - 64) / 64) ** 2 + ((ny - 64) / 64) ** 2)
    blend(img[sub], np.clip(1.0 - d, 0, 1) ** 1.5 * 0.45, hex_rgb("#E2A688"))
    return img


def paint_hair():
    """Lock texture: u across the lock, v from root (0, bottom) to tip (1, top)."""
    width, height = 128, 256
    rng = np.random.default_rng(7)
    base = np.array(hex_rgb(C.PALETTE["hair"]))
    columns = 1.0 + 0.16 * np.convolve(rng.standard_normal(width + 6), np.ones(4) / 4, mode="same")[3:width + 3]
    img = np.zeros((height, width, 3), dtype=np.float32)
    rows = np.linspace(1.0, 0.0, height)[:, None]          # row 0 is the tip (v = 1)
    root_shade = 0.62 + 0.38 * np.clip(rows / 0.45, 0.0, 1.0)
    sheen = 1.0 + 0.22 * np.exp(-((rows - 0.62) / 0.12) ** 2)
    img[...] = base * (columns[None, :] * root_shade * sheen)[..., None]
    return img


def paint_denim():
    width, height = 256, 256
    rng = np.random.default_rng(11)
    base = np.array(hex_rgb(C.PALETTE["jeans"]))
    xs, ys = grid(height, width)
    # Diagonal twill whose period divides the tile, so the texture repeats seamlessly.
    twill = 0.05 * np.sin((xs + ys) * 2 * math.pi * 36 / width) + 0.035 * rng.standard_normal((height, width))
    fade = 1.0 + 0.10 * np.sin(xs / width * 2 * math.pi * 2)
    return base * (1.0 + twill)[..., None] * fade[..., None]


# ------------------------------------------------------------------ materials
def principled(name, colour_hex, roughness, image=None):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = linear(colour_hex)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = 0.0
    if image is not None:
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = image
        tex.interpolation = "Linear"
        mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    mat.diffuse_color = linear(colour_hex)
    return mat


def build(out_dir):
    tex_dir = os.path.join(out_dir, "textures")
    os.makedirs(tex_dir, exist_ok=True)
    face = save_texture(paint_face_atlas(), os.path.join(tex_dir, "face-atlas.png"), "FaceAtlas")
    hair = save_texture(paint_hair(), os.path.join(tex_dir, "hair-locks.png"), "HairLocks")
    denim = save_texture(paint_denim(), os.path.join(tex_dir, "denim.png"), "Denim")
    R = C.ROUGHNESS
    P = C.PALETTE
    return {
        "skin": principled("Skin", P["skin"], R["skin"]),
        "face": principled("Face", P["skin"], R["face"], face),
        "hair": principled("Hair", P["hair"], R["hair"], hair),
        "tee": principled("Tee", P["tee"], R["tee"]),
        "jeans": principled("Jeans", P["jeans"], R["jeans"], denim),
        "cuff": principled("JeansCuff", P["cuff"], R["jeans"]),
        "shoe": principled("ShoeUpper", P["shoe"], R["shoe"]),
        "sole": principled("ShoeSole", P["sole"], R["sole"]),
        "backpack": principled("Backpack", P["backpack"], R["backpack"]),
        "watch": principled("Watch", P["watch"], R["watch"]),
    }
