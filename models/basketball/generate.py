"""Original deterministic size-7 basketball; Blender 5.x, metres, no external assets.

Eight-panel ball: two perpendicular great-circle seams cross at the poles (+/-Z) and
two curved "C" seams loop around the +/-X axis, crossing the X-Z belt seam. Channels
are real recessed geometry (exact Boolean of round tubes) with a black rubber material.
The pebbled grain is a tangent-space normal map baked in Cycles from 3D Voronoi bumps,
so it is seamless on the sphere and survives glTF export.
"""
from pathlib import Path
import json
import math
import sys

import bpy
import bmesh
from mathutils import Vector

HERE = Path(__file__).resolve().parent
SLUG = "basketball"
ROOT = "ASSET_Basketball"
RADIUS = 0.1193            # 29.5 in / 74.9 cm circumference (FIBA/NBA size 7)
CHANNEL_RADIUS = 0.0030    # round groove: ~6 mm wide, ~3 mm deep at the surface
C_SEAM_RADIUS_DEG = 54.0   # angular radius of each C seam around +/-X
C_SEAM_ELONGATION_DEG = 6.0
SEAM_SAMPLES = 256
TARGET = Vector((0, 0, RADIUS))
MATERIAL_NAMES = ("Pebbled orange rubber", "Black channel rubber")
TEXTURE_SIZE = (2048, 1024)


def srgb(rgb):
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb) + (1,)


def seam_curves():
    """Return the four closed seam polylines on a unit sphere centred at the origin."""
    curves = {}
    ts = [2 * math.pi * i / SEAM_SAMPLES for i in range(SEAM_SAMPLES)]
    curves["SEAM_GreatCircle_XZ"] = [Vector((math.cos(t), 0, math.sin(t))) for t in ts]
    curves["SEAM_GreatCircle_YZ"] = [Vector((0, math.cos(t), math.sin(t))) for t in ts]
    for sign, label in ((1, "PosX"), (-1, "NegX")):
        axis = Vector((sign, 0, 0))
        points = []
        for t in ts:
            r = math.radians(C_SEAM_RADIUS_DEG + C_SEAM_ELONGATION_DEG * math.cos(2 * t))
            direction = Vector((0, math.sin(t), math.cos(t)))
            points.append((axis * math.cos(r) + direction * math.sin(r)).normalized())
        curves["SEAM_CurvedC_" + label] = points
    return curves


def cutter_object(curves):
    """Round tubes centred on the ball surface; joined into one Boolean operand."""
    parts = []
    for name, points in curves.items():
        data = bpy.data.curves.new(name, "CURVE")
        data.dimensions = "3D"
        data.bevel_depth = CHANNEL_RADIUS
        data.bevel_resolution = 3
        spline = data.splines.new("POLY")
        spline.points.add(len(points) - 1)
        for point, p in zip(spline.points, points):
            point.co = (*(p * RADIUS), 1)
        spline.use_cyclic_u = True
        obj = bpy.data.objects.new(name, data)
        bpy.context.scene.collection.objects.link(obj)
        parts.append(obj)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.convert(target="MESH")
    bpy.ops.object.join()
    cutter = bpy.context.object
    cutter.name = "CUTTER_SeamChannels"
    return cutter


def pebble_bake(ball):
    """Bake 3D Voronoi pebbles to a tangent-space normal map on the ball UVs."""
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 4
    scene.cycles.seed = 0
    scene.cycles.device = "CPU"
    image = bpy.data.images.new("T_Basketball_Pebble_Normal", *TEXTURE_SIZE, alpha=False, float_buffer=False)
    image.colorspace_settings.name = "Non-Color"
    mat = bpy.data.materials.new("BAKE_Pebbles")
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = nodes["Principled BSDF"]
    coords = nodes.new("ShaderNodeTexCoord")
    voronoi = nodes.new("ShaderNodeTexVoronoi")
    voronoi.voronoi_dimensions = "3D"
    voronoi.feature = "SMOOTH_F1"
    voronoi.inputs["Scale"].default_value = 1 / 0.0029
    voronoi.inputs["Smoothness"].default_value = 0.35
    voronoi.inputs["Randomness"].default_value = 0.85
    ramp = nodes.new("ShaderNodeMapRange")
    ramp.inputs["From Min"].default_value = 0.0
    ramp.inputs["From Max"].default_value = 0.55
    ramp.inputs["To Min"].default_value = 1.0
    ramp.inputs["To Max"].default_value = 0.0
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.55
    bump.inputs["Distance"].default_value = 0.0004
    links.new(coords.outputs["Object"], voronoi.inputs["Vector"])
    links.new(voronoi.outputs["Distance"], ramp.inputs["Value"])
    links.new(ramp.outputs["Result"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    target = nodes.new("ShaderNodeTexImage")
    target.image = image
    nodes.active = target
    ball.data.materials.clear()
    ball.data.materials.append(mat)
    bpy.ops.object.select_all(action="DESELECT")
    ball.select_set(True)
    bpy.context.view_layer.objects.active = ball
    scene.render.bake.margin = 8
    scene.render.bake.normal_space = "TANGENT"
    bpy.ops.object.bake(type="NORMAL", normal_space="TANGENT", margin=8, use_clear=True)
    image.filepath_raw = str(HERE / "sources" / "textures" / "basketball_pebble_normal.png")
    image.file_format = "PNG"
    image.save()
    image.filepath = "//textures/basketball_pebble_normal.png"
    ball.data.materials.clear()
    bpy.data.materials.remove(mat)
    return image


def build(root):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64, radius=RADIUS, location=(0, 0, 0))
    ball = bpy.context.object
    ball.name = "BALL_Shell"
    bpy.ops.object.shade_smooth()
    image = pebble_bake(ball)

    orange = bpy.data.materials.new(MATERIAL_NAMES[0])
    orange.use_nodes = True
    nodes, links = orange.node_tree.nodes, orange.node_tree.links
    bsdf = nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = srgb((0.80, 0.33, 0.11))
    bsdf.inputs["Roughness"].default_value = 0.62
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = image
    tex.interpolation = "Linear"
    normal = nodes.new("ShaderNodeNormalMap")
    normal.space = "TANGENT"
    normal.uv_map = "UVMap"
    normal.inputs["Strength"].default_value = 1.0
    links.new(tex.outputs["Color"], normal.inputs["Color"])
    links.new(normal.outputs["Normal"], bsdf.inputs["Normal"])
    orange.diffuse_color = srgb((0.80, 0.33, 0.11))
    orange.use_backface_culling = True

    black = bpy.data.materials.new(MATERIAL_NAMES[1])
    black.use_nodes = True
    bb = black.node_tree.nodes["Principled BSDF"]
    bb.inputs["Base Color"].default_value = srgb((0.035, 0.033, 0.032))
    bb.inputs["Roughness"].default_value = 0.5
    black.diffuse_color = srgb((0.035, 0.033, 0.032))
    black.use_backface_culling = True

    ball.data.materials.append(orange)
    curves = seam_curves()
    cutter = cutter_object(curves)
    cutter.data.materials.clear()
    cutter.data.materials.append(black)
    cutter.hide_render = True
    cutter.display_type = "WIRE"
    cutter.parent = root
    ball.parent = root
    ball.location = (0, 0, RADIUS)
    cutter.location = (0, 0, RADIUS)
    boolean = ball.modifiers.new("Recessed seam channels", "BOOLEAN")
    boolean.operation = "DIFFERENCE"
    boolean.solver = "EXACT"
    boolean.object = cutter
    boolean.use_self = True
    boolean.use_hole_tolerant = True
    boolean.material_mode = "TRANSFER"
    cutter.hide_set(True)
    return curves


def aim(obj, point):
    obj.rotation_euler = (Vector(point) - obj.location).to_track_quat("-Z", "Y").to_euler()


def studio():
    scene = bpy.context.scene
    scene.world = bpy.data.worlds.new("Slate studio")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.12, 0.16, 0.2, 1)
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.45
    for name, location, energy, size in (("Key", (-0.6, -0.9, 1.3), 42, 0.9), ("Fill", (0.9, -0.3, 0.8), 26, 0.9),
                                         ("Rim", (0, 0.9, 0.9), 45, 0.6)):
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.name = "STUDIO_" + name
        light.data.energy = energy
        light.data.shape = "DISK"
        light.data.size = size
        aim(light, TARGET)
    bpy.ops.object.camera_add()
    scene.camera = bpy.context.object
    scene.camera.name = "STUDIO_Camera"
    scene.camera.data.type = "ORTHO"
    scene.camera.data.ortho_scale = 0.33
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 32
    scene.cycles.seed = 0
    scene.cycles.use_denoising = True
    scene.render.resolution_x = scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = "AgX"


def export_copy(root):
    """Evaluate the Boolean into a temporary mesh; the saved source keeps the modifier."""
    ball = bpy.data.objects["BALL_Shell"]
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    mesh = bpy.data.meshes.new_from_object(ball.evaluated_get(depsgraph), depsgraph=depsgraph)
    mesh.name = "MESH_Basketball"
    copy = bpy.data.objects.new("MESH_Basketball", mesh)
    bpy.context.scene.collection.objects.link(copy)
    copy.matrix_world = ball.matrix_world.copy()
    copy.parent = root
    copy.matrix_parent_inverse = root.matrix_world.inverted()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-6)
    # Tangents for the normal map need triangles; Boolean output contains n-gons.
    bmesh.ops.triangulate(bm, faces=bm.faces, quad_method="BEAUTY", ngon_method="BEAUTY")
    # Exact Boolean leaves micro slivers where tubes cross; collapse them (10-20 micron tolerance).
    for _ in range(8):
        slivers = [f for f in bm.faces if f.calc_area() < 1e-10]
        if not slivers:
            break
        bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=2e-5)
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY", ngon_method="BEAUTY")
    assert not [f for f in bm.faces if f.calc_area() < 1e-10], "sliver triangles remain"
    bm.to_mesh(mesh)
    bm.free()
    bpy.ops.object.select_all(action="DESELECT")
    copy.select_set(True)
    bpy.context.view_layer.objects.active = copy
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))
    return copy


def export(path):
    root = bpy.data.objects[ROOT]
    copy = export_copy(root)
    try:
        bpy.ops.object.select_all(action="DESELECT")
        root.select_set(True)
        copy.select_set(True)
        bpy.ops.export_scene.gltf(filepath=str(path), export_format="GLB", use_selection=True,
                                  export_yup=True, export_animations=False, export_extras=True,
                                  export_texcoords=True, export_normals=True, export_cameras=False,
                                  export_lights=False, export_tangents=True, export_image_format="JPEG", export_jpeg_quality=90)
    finally:
        mesh = copy.data
        bpy.data.objects.remove(copy, do_unlink=True)
        bpy.data.meshes.remove(mesh)


def source_measurements(curves):
    root = bpy.data.objects[ROOT]
    seams = {}
    for name, points in curves.items():
        # glTF coordinates: (x, z, -y), ball centre at height RADIUS.
        seams[name] = [[round(p.x * RADIUS, 7), round(p.z * RADIUS + RADIUS, 7), round(-p.y * RADIUS, 7)] for p in points[::8]]
    return {"blender_version": bpy.app.version_string, "radius_m": RADIUS, "diameter_m": 2 * RADIUS,
            "circumference_m": round(2 * math.pi * RADIUS, 5), "channel_radius_m": CHANNEL_RADIUS,
            "panels": 8, "seams": seams,
            "editable_meshes": sum(obj.type == "MESH" for obj in root.children_recursive)}


def render_views():
    scene = bpy.context.scene
    for name, delta in (("hero", (0.55, -0.9, 0.42)), ("front", (0, -1.1, 0.05)),
                        ("side", (1.1, 0, 0.08)), ("3q", (-0.62, -0.85, 0.6))):
        scene.camera.location = TARGET + Vector(delta)
        aim(scene.camera, TARGET)
        scene.render.image_settings.file_format = "PNG"
        scene.render.filepath = str(HERE / "previews" / (name + ".png"))
        bpy.ops.render.render(write_still=True)
        if name == "hero":
            scene.render.image_settings.file_format = "WEBP"
            scene.render.image_settings.quality = 86
            bpy.data.images["Render Result"].save_render(str(HERE / "previews" / "hero.webp"), scene=scene)


def main():
    for directory in ("sources", "sources/textures", "exports", "previews", "metadata", "reports"):
        (HERE / directory).mkdir(exist_ok=True)
    curves = seam_curves()
    if "--export-source" in sys.argv:
        bpy.ops.wm.open_mainfile(filepath=str(HERE / "sources" / (SLUG + ".blend")))
    else:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.context.preferences.filepaths.save_version = 0
        scene = bpy.context.scene
        scene.unit_settings.system = "METRIC"
        scene.unit_settings.scale_length = 1
        root = bpy.data.objects.new(ROOT, None)
        scene.collection.objects.link(root)
        root["units"] = "metres"
        root["front_axis"] = "Blender -Y / glTF +Z"
        root["up_axis"] = "Blender +Z / glTF +Y"
        root["size"] = "7"
        build(root)
        studio()
        bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "sources" / (SLUG + ".blend")), compress=True)
    if "--previews-only" in sys.argv:
        render_views()
        return
    measured = source_measurements(curves)
    (HERE / "reports" / "source-geometry.json").write_text(json.dumps(measured, indent=2) + "\n")
    export(HERE / "exports" / "optimized.glb")
    if "--skip-render" not in sys.argv:
        render_views()


if __name__ == "__main__":
    main()
