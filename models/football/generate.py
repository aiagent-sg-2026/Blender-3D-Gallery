"""Original deterministic truncated-icosahedron football; metres, no external assets."""
from pathlib import Path
import json
import math
import sys

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
SLUG = "football"
ROOT = "ASSET_Football"
TARGET = Vector((0, 0, 0))
MATERIAL_NAMES = ("Black panels", "White panels")


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


def build(root):
    # Icosahedron from golden-ratio coordinates; directed edge thirds are the
    # 60 vertices of its exact truncation. No sphere texture or external mesh.
    from itertools import combinations
    phi = (1 + math.sqrt(5)) / 2
    ico = [Vector(v) for a in (-1, 1) for b in (-phi, phi)
           for v in ((0, a, b), (a, b, 0), (b, 0, a))]
    edges = {(i, j) for i, j in combinations(range(12), 2)
             if abs((ico[i] - ico[j]).length - 2) < 1e-5}
    adjacent = lambda i,j: tuple(sorted((i,j))) in edges
    faces = [f for f in combinations(range(12), 3)
             if all(adjacent(i,j) for i,j in combinations(f,2))]
    points = {(i,j): (ico[i]*2+ico[j])/3 for i,j in sorted(edges) for i,j in ((i,j),(j,i))}
    assert len(points) == 60 and len(faces) == 20
    panels = [[points[i,j] for j in range(12) if adjacent(i,j)] for i in range(12)]
    panels += [[points[i,j] for i in f for j in f if i != j] for f in faces]
    black = material(MATERIAL_NAMES[0], (.055,.06,.065), roughness=.48)
    white = material(MATERIAL_NAMES[1], (.91,.90,.87), roughness=.44)
    for n, polygon in enumerate(panels):
        center = sum(polygon, Vector())/len(polygon)
        normal = center.normalized()
        u = (polygon[0]-center).normalized()
        v = normal.cross(u)
        polygon.sort(key=lambda q: math.atan2((q-center).dot(v),(q-center).dot(u)))
        perimeter = [a.lerp(polygon[(i+1)%len(polygon)], k/8)
                     for i,a in enumerate(polygon) for k in range(8)]
        count = len(perimeter)
        verts = [normal*.11]
        # Curved panel top, rolling down 0.8 mm at the shared seam.
        for ring in range(1, 13):
            t = ring/12
            radius = .11 - .0008 * max(0,(t-.8)/.2)**2
            verts += [center.lerp(q,t).normalized()*radius for q in perimeter]
        polygons = [(0,1+i,1+(i+1)%count) for i in range(count)]
        for ring in range(11):
            a=1+ring*count; b=a+count
            polygons += [(a+i,b+i,b+(i+1)%count,a+(i+1)%count) for i in range(count)]
        # Closed inward backing per panel, invisible at normal viewing distances.
        back = len(verts)
        verts.append(normal*.106)
        a=1+11*count
        polygons += [(back,a+(i+1)%count,a+i) for i in range(count)]
        mesh=bpy.data.meshes.new('Panel geometry %02d'%n)
        mesh.from_pydata(verts,[],polygons); mesh.update()
        obj=bpy.data.objects.new(('PENTAGON_' if n<12 else 'HEXAGON_')+'%02d'%n,mesh)
        bpy.context.scene.collection.objects.link(obj); obj.parent=root
        mesh.materials.append(black if n<12 else white)
        obj['panel_sides']=len(polygon)
        for face in mesh.polygons: face.use_smooth=True
        # Backing must not pull the seam's top normals inward.
        normals=[Vector() for q in verts]
        for face in mesh.polygons:
            if back in face.vertices:
                continue
            for i in face.vertices:
                normals[i] += face.normal
        normals[back] = -normal
        mesh.normals_split_custom_set_from_vertices([tuple(q.normalized()) for q in normals])
    root['topology_vertices']=60
    root['pentagons']=12; root['hexagons']=20


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
    scene.camera.data.ortho_scale = .29
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
    panels = []
    for obj in sorted(root.children_recursive, key=lambda obj: obj.name):
        vertices = evaluated_vertices(obj, depsgraph)
        panels.append({"name": obj.name, "sides": obj["panel_sides"],
                       "material": obj.data.materials[0].name,
                       "positions": [[round(v.x,7),round(v.z,7),round(-v.y,7)] for v in vertices]})
    return {"blender_version": bpy.app.version_string, "topology_vertices": 60,
            "panels": panels, "editable_meshes": len(panels)}


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
