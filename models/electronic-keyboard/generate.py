"""Original deterministic 61-key keyboard; Blender 5.2.3, metres, no external assets."""
from pathlib import Path
import json
import math
import sys

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
SLUG = "electronic-keyboard"
ROOT = "ASSET_ElectronicKeyboard"
TARGET = Vector((0, 0, 0.53))
MATERIAL_NAMES = ("Graphite", "Ivory keys", "Satin blue-grey metal")


def material(name, rgb, metal=0, roughness=0.4):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    color = tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb) + (1,)
    shader = mat.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Metallic"].default_value = metal
    shader.inputs["Roughness"].default_value = roughness
    mat.diffuse_color = color
    return mat


def finish(obj, name, mat, root, bevel=0.001, segments=2):
    obj.name = name
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    obj.parent = root
    if bevel:
        modifier = obj.modifiers.new("Soft manufactured edge", "BEVEL")
        modifier.width = min(bevel, min(obj.dimensions) * 0.45)
        modifier.segments = segments
        obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return obj


def box(name, location, dimensions, mat, root, bevel=0.001):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, mat, root, bevel)


def rod(name, a, b, radius, mat, root, vertices=12):
    start, end = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=(end - start).length, location=(start + end) / 2)
    obj = bpy.context.object
    obj.rotation_euler = (end - start).to_track_quat("Z", "Y").to_euler()
    return finish(obj, name, mat, root, 0.001)


def white_key(name, left, right, left_notch, right_notch, mat, root):
    # Rear cutouts leave physical clearance around the raised black keys.
    outline = [(left, -0.178), (right, -0.178), (right, -0.071),
               (right - right_notch, -0.071), (right - right_notch, 0.047),
               (left + left_notch, 0.047), (left + left_notch, -0.071), (left, -0.071)]
    outline = [p for i, p in enumerate(outline) if p != outline[i - 1]]
    count = len(outline)
    vertices = [(x, y, z) for z in (0.763, 0.781) for x, y in outline]
    faces = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
    faces += [(i, (i + 1) % count, (i + 1) % count + count, i + count) for i in range(count)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return finish(obj, name, mat, root, 0.0005, segments=1)


def build(root):
    dark = material(MATERIAL_NAMES[0], (0.125, 0.145, 0.16), roughness=0.33)
    ivory = material(MATERIAL_NAMES[1], (0.94, 0.935, 0.89), roughness=0.27)
    metal = material(MATERIAL_NAMES[2], (0.43, 0.52, 0.55), metal=0.55, roughness=0.35)
    box("BODY_LowerShell", (0, 0, 0.71), (0.996, 0.396, 0.09), dark, root, 0.012)
    box("BODY_Keybed", (0, -0.066, 0.758), (0.872, 0.248, 0.008), dark, root, 0.002)
    box("BODY_FrontLip", (0, -0.193, 0.75), (0.89, 0.014, 0.014), dark, root, 0.003)
    for sign in (-1, 1):
        box("BODY_EndCheek_%s" % sign, (sign * 0.467, 0, 0.757), (0.066, 0.4, 0.056), dark, root, 0.008)
        box("BODY_CheekInlay_%s" % sign, (sign * 0.473, -0.038, 0.7855), (0.012, 0.23, 0.002), metal, root, 0.0006)
    box("CONTROL_Deck", (0, 0.127, 0.766), (0.866, 0.132, 0.022), dark, root, 0.004)

    naturals = [midi for midi in range(36, 97) if midi % 12 in (0, 2, 4, 5, 7, 9, 11)]
    for index, midi in enumerate(naturals):
        has_left = index > 0 and midi - naturals[index - 1] == 2
        has_right = index < len(naturals) - 1 and naturals[index + 1] - midi == 2
        left = -0.432 + index * 0.024 + 0.00045
        obj = white_key("KEY_White_%02d_MIDI_%d" % (index + 1, midi), left, left + 0.0231,
                        0.0074 if has_left else 0, 0.0074 if has_right else 0, ivory, root)
        obj["midi_note"] = midi
        obj["key_color"] = "white"
        if has_right:
            black = box("KEY_Black_MIDI_%d" % (midi + 1), (-0.432 + (index + 1) * 0.024, -0.0095, 0.78),
                        (0.0144, 0.119, 0.038), dark, root, 0.0012)
            black["midi_note"] = midi + 1
            black["key_color"] = "black"

    # Abstract, blank controls and open speaker ribs; no fonts, textures or logos.
    for sign in (-1, 1):
        for index in range(16):
            box("CONTROL_SpeakerRib_%s_%02d" % (sign, index), (sign * 0.335, 0.083 + index * 0.005, 0.778),
                (0.153, 0.0019, 0.002), metal, root, 0.0004)
    box("CONTROL_DisplayBezel", (0, 0.129, 0.779), (0.112, 0.065, 0.004), metal, root, 0.003)
    box("CONTROL_BlankDisplay", (0, 0.128, 0.7815), (0.1, 0.053, 0.002), dark, root, 0.002)
    for index, x in enumerate((-0.207, -0.16, -0.113)):
        rod("CONTROL_Knob_%d" % index, (x, 0.132, 0.778), (x, 0.132, 0.794), 0.012, metal, root, 16)
        box("CONTROL_KnobPointer_%d" % index, (x, 0.126, 0.7945), (0.002, 0.009, 0.001), dark, root, 0.0002)
    for row in range(2):
        for column in range(5):
            box("CONTROL_Button_%d_%d" % (row, column), (0.097 + column * 0.028, 0.108 + row * 0.034, 0.781),
                (0.018, 0.014, 0.006), metal, root, 0.002)

    # Paired X bars occupy parallel depth planes; the pivot joins them.
    for index, y in enumerate((-0.035, 0.035)):
        sign = 1 if index == 0 else -1
        rod("STAND_XBar_%d" % index, (-0.335 * sign, y, 0.041), (0.335 * sign, y, 0.638), 0.017, metal, root)
    rod("STAND_PivotAxle", (0, -0.061, 0.3395), (0, 0.061, 0.3395), 0.028, dark, root, 20)
    rod("STAND_PivotCap", (0, -0.066, 0.3395), (0, -0.06, 0.3395), 0.019, metal, root, 20)
    rod("STAND_LockKnob", (0, 0.06, 0.3395), (0, 0.08, 0.3395), 0.022, dark, root, 16)
    for sign in (-1, 1):
        rod("STAND_Foot_%s" % sign, (sign * 0.335, -0.22, 0.022), (sign * 0.335, 0.22, 0.022), 0.018, metal, root)
        rod("STAND_TopSupport_%s" % sign, (sign * 0.335, -0.175, 0.642), (sign * 0.335, 0.175, 0.642), 0.017, metal, root)
        for depth_sign in (-1, 1):
            rod("STAND_RubberFoot_%s_%s" % (sign, depth_sign),
                (sign * 0.335, depth_sign * 0.19, 0.022), (sign * 0.335, depth_sign * 0.23, 0.022), 0.022, dark, root)
            box("STAND_SupportPad_%s_%s" % (sign, depth_sign), (sign * 0.335, depth_sign * 0.135, 0.662),
                (0.05, 0.06, 0.008), dark, root, 0.002)

    # Small open music rest: tilted rails with a retaining ledge and two stems.
    for sign in (-1, 1):
        rod("MUSIC_Mount_%s" % sign, (sign * 0.142, 0.178, 0.774), (sign * 0.142, 0.188, 0.838), 0.006, dark, root)
    rest = bpy.data.objects.new("MUSIC_RestFrame", None)
    bpy.context.scene.collection.objects.link(rest)
    rest.parent = root
    rest.location = (0, 0.172, 0.827)
    rest.rotation_euler.x = math.radians(-12)
    box("MUSIC_BottomRail", (0, 0, 0.009), (0.4, 0.009, 0.018), metal, rest, 0.003)
    box("MUSIC_TopRail", (0, 0, 0.196), (0.4, 0.009, 0.016), metal, rest, 0.003)
    for x in (-0.192, 0.192, -0.068, 0.068):
        box("MUSIC_Upright_%s" % x, (x, 0, 0.101), (0.014, 0.009, 0.19), metal, rest, 0.002)
    box("MUSIC_Tray", (0, -0.02, 0), (0.4, 0.054, 0.008), dark, rest, 0.003)
    box("MUSIC_RetainingLip", (0, -0.044, 0.009), (0.4, 0.007, 0.019), dark, rest, 0.002)


def aim(obj, point):
    obj.rotation_euler = (Vector(point) - obj.location).to_track_quat("-Z", "Y").to_euler()


def studio():
    scene = bpy.context.scene
    scene.world = bpy.data.worlds.new("Slate studio")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.12, 0.16, 0.2, 1)
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.45
    for name, location, energy, size in (("Key", (-2, -3, 4), 430, 3), ("Fill", (3, -1, 2.5), 290, 3), ("Rim", (0, 3, 3), 500, 2)):
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
    scene.camera.data.ortho_scale = 1.43
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 32
    scene.cycles.seed = 0
    scene.cycles.use_denoising = True
    scene.render.resolution_x = scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = "AgX"


def evaluated_vertices(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    vertices = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
    evaluated.to_mesh_clear()
    return vertices


def source_measurements(root):
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    keys = []
    for obj in sorted(root.children_recursive, key=lambda obj: obj.name):
        if "midi_note" in obj:
            vertices = evaluated_vertices(obj, depsgraph)
            # Convert the actual evaluated source to the exported coordinate convention.
            positions = [[round(v.x, 7), round(v.z, 7), round(-v.y, 7)] for v in vertices]
            keys.append({"name": obj.name, "midi": obj["midi_note"], "color": obj["key_color"], "positions": positions})
    return {"blender_version": bpy.app.version_string, "key_count": len(keys), "keys": keys,
            "editable_meshes": sum(obj.type == "MESH" for obj in root.children_recursive)}


def export(path):
    """Export merged evaluated copies; keep the saved authoring objects editable."""
    root = bpy.data.objects[ROOT]
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    originals = [obj for obj in root.children_recursive if obj.type == "MESH"]
    try:
        for material_name in MATERIAL_NAMES:
            group = []
            for original in originals:
                if original.data.materials[0].name != material_name:
                    continue
                mesh = bpy.data.meshes.new_from_object(original.evaluated_get(depsgraph), depsgraph=depsgraph)
                copy = bpy.data.objects.new("EXPORT_Part", mesh)
                bpy.context.scene.collection.objects.link(copy)
                copy.matrix_world = original.matrix_world.copy()
                group.append(copy)
            bpy.ops.object.select_all(action="DESELECT")
            for obj in group:
                obj.select_set(True)
            bpy.context.view_layer.objects.active = group[0]
            bpy.ops.object.join()
            merged = bpy.context.object
            merged.name = "MESH_" + material_name.replace(" ", "_").replace("-", "_")
            merged.parent = root
        bpy.ops.object.select_all(action="DESELECT")
        root.select_set(True)
        for obj in root.children:
            if obj.name.startswith("MESH_"):
                obj.select_set(True)
        bpy.ops.export_scene.gltf(filepath=str(path), export_format="GLB", use_selection=True,
                                  export_yup=True, export_animations=False, export_extras=True,
                                  export_texcoords=False, export_cameras=False, export_lights=False)
    finally:
        for obj in list(root.children):
            if obj.name.startswith("MESH_"):
                mesh = obj.data
                bpy.data.objects.remove(obj, do_unlink=True)
                bpy.data.meshes.remove(mesh)


def render_views():
    scene = bpy.context.scene
    for name, delta in (("hero", (1.1, -1.8, 1.16)), ("front", (0, -2.5, 0.14)),
                        ("side", (2.5, 0, 0.28)), ("3q", (-1.35, -1.8, 1.45))):
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
    for directory in ("sources", "exports", "previews", "metadata", "reports"):
        (HERE / directory).mkdir(exist_ok=True)
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
        build(root)
        studio()
        bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "sources" / (SLUG + ".blend")), compress=True)
    if "--previews-only" in sys.argv:
        render_views()
        return
    measured = source_measurements(bpy.data.objects[ROOT])
    (HERE / "reports" / "source-geometry.json").write_text(json.dumps(measured, indent=2) + "\n")
    export(HERE / "exports" / "optimized.glb")
    if "--skip-render" not in sys.argv:
        render_views()


if __name__ == "__main__":
    main()
