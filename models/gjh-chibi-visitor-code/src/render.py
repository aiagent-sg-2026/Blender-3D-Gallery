"""Studio, cameras and renders: colour previews (Eevee) and silhouettes (Workbench)."""
import math
import os

import bpy
import numpy as np
from mathutils import Vector

import config as C
import materials as M

VIEWS = {
    # name: (camera direction from the figure, Euler rotation)
    "front": ((0.0, -1.0, 0.0), (math.pi / 2, 0.0, 0.0)),
    "side": ((1.0, 0.0, 0.0), (math.pi / 2, 0.0, math.pi / 2)),
    "back": ((0.0, 1.0, 0.0), (math.pi / 2, 0.0, math.pi)),
}
SIL_SIZE = (300, 480)          # width, height of silhouette renders
SIL_CENTER_Z = 0.66


def setup_studio():
    scene = bpy.context.scene
    world = bpy.data.worlds.get("Studio") or bpy.data.worlds.new("Studio")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = M.linear("#ECEDF8")
    bg.inputs["Strength"].default_value = 0.60
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    for obj in [o for o in bpy.data.objects if o.name.startswith("STUDIO_")]:
        bpy.data.objects.remove(obj, do_unlink=True)

    def light(name, kind, energy, rotation, size, colour=(1.0, 1.0, 1.0)):
        data = bpy.data.lights.new(name, kind)
        data.energy = energy
        data.color = colour
        if kind == "SUN":
            data.angle = size
        else:
            data.shadow_soft_size = size
        obj = bpy.data.objects.new(name, data)
        obj.rotation_euler = rotation
        scene.collection.objects.link(obj)
        return obj

    light("STUDIO_Key", "SUN", 3.0, (math.radians(50), 0.0, math.radians(-35)), math.radians(12))
    light("STUDIO_Fill", "SUN", 1.2, (math.radians(65), 0.0, math.radians(60)), math.radians(30), (0.92, 0.94, 1.0))
    light("STUDIO_Rim", "SUN", 1.6, (math.radians(-120), 0.0, math.radians(10)), math.radians(20))
    eevee = scene.eevee
    for attr, value in (("use_shadows", True), ("shadow_ray_count", 2), ("use_gtao", True)):
        if hasattr(eevee, attr):
            setattr(eevee, attr, value)


def camera(name, location, rotation, ortho_scale=None, lens=85.0):
    scene = bpy.context.scene
    cam_data = bpy.data.cameras.get(name) or bpy.data.cameras.new(name)
    if ortho_scale:
        cam_data.type = "ORTHO"
        cam_data.ortho_scale = ortho_scale
    else:
        cam_data.type = "PERSP"
        cam_data.lens = lens
    cam_data.clip_start = 0.05
    cam_data.clip_end = 50.0
    cam = bpy.data.objects.get(name)
    if cam is None:
        cam = bpy.data.objects.new(name, cam_data)
        scene.collection.objects.link(cam)
    cam.location = location
    cam.rotation_euler = rotation
    scene.camera = cam
    return cam


def look_at_rotation(location, target):
    direction = Vector(target) - Vector(location)
    return direction.to_track_quat("-Z", "Y").to_euler()


def render(path, engine, size, transparent=False, samples=32):
    scene = bpy.context.scene
    scene.render.engine = engine
    scene.render.resolution_x, scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = transparent
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA" if transparent else "RGB"
    if engine == "BLENDER_EEVEE" and hasattr(scene.eevee, "taa_render_samples"):
        scene.eevee.taa_render_samples = samples
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    return path


def ortho_view(view, size=SIL_SIZE, center_z=SIL_CENTER_Z, px_per_m=C.RENDER_PX_PER_M):
    direction, rotation = VIEWS[view]
    scale = max(size) / px_per_m
    loc = Vector(direction) * 6.0 + Vector((0.0, 0.0, center_z))
    return camera("QA_Camera", loc, rotation, ortho_scale=scale)


def preview_views(out_dir, prefix="preview", size=(600, 960)):
    """Colour orthographic front/side/back plus a perspective 3/4 view."""
    os.makedirs(out_dir, exist_ok=True)
    setup_studio()
    paths = []
    for view in ("front", "side", "back"):
        ortho_view(view, size=size, px_per_m=size[1] / 1.37)
        paths.append(render(os.path.join(out_dir, f"{prefix}-{view}.png"), "BLENDER_EEVEE", size))
    loc = Vector((-2.2, -3.4, 1.25))
    camera("QA_Camera", loc, look_at_rotation(loc, (0.0, 0.0, 0.66)), lens=70.0)
    paths.append(render(os.path.join(out_dir, f"{prefix}-three-quarter.png"), "BLENDER_EEVEE", size))
    return paths


def face_closeup(out_dir, name="face", size=(640, 640)):
    setup_studio()
    loc = Vector((0.0, -2.0, 0.98))
    camera("QA_Camera", loc, look_at_rotation(loc, (0.0, 0.0, 0.98)), lens=135.0)
    return render(os.path.join(out_dir, f"{name}.png"), "BLENDER_EEVEE", size)


def silhouette(view, path):
    """Workbench flat render with transparent film; returns a bool mask (row 0 top)."""
    scene = bpy.context.scene
    ortho_view(view)
    scene.display.shading.light = "FLAT"
    scene.display.shading.color_type = "SINGLE"
    scene.display.shading.single_color = (1.0, 1.0, 1.0)
    render(path, "BLENDER_WORKBENCH", SIL_SIZE, transparent=True)
    image = bpy.data.images.load(path, check_existing=False)
    w, h = image.size
    alpha = np.array(image.pixels[:], dtype=np.float32).reshape(h, w, 4)[::-1, :, 3]
    bpy.data.images.remove(image)
    return alpha > 0.5


def row_to_z(row):
    """Silhouette render row (top = 0) to world height in metres."""
    h = SIL_SIZE[1]
    return SIL_CENTER_Z + (h / 2.0 - row - 0.5) / C.RENDER_PX_PER_M
