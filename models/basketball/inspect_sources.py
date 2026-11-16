"""Reopen the saved source and re-import the exported GLB in Blender; write reports/sources.json."""
from pathlib import Path
import hashlib
import json

import bpy

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "sources" / "basketball.blend"
GLB = HERE / "exports" / "optimized.glb"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


before = sha(SOURCE)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
root = bpy.data.objects["ASSET_Basketball"]
ball = bpy.data.objects["BALL_Shell"]
boolean = ball.modifiers["Recessed seam channels"]
image = bpy.data.images["T_Basketball_Pebble_Normal"]
assert boolean.type == "BOOLEAN" and boolean.object.name == "CUTTER_SeamChannels"
assert image.has_data or image.filepath_from_user()
source = {
    "editable_meshes": sorted(obj.name for obj in root.children_recursive if obj.type == "MESH"),
    "materials": sorted(m.name for m in bpy.data.materials if m.users),
    "boolean_solver": boolean.solver,
    "normal_map": {"name": image.name, "size": list(image.size), "filepath": image.filepath},
    "root_properties": {k: root[k] for k in root.keys()},
}

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(GLB))
meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
depsgraph = bpy.context.evaluated_depsgraph_get()
triangles = 0
for obj in meshes:
    mesh = obj.evaluated_get(depsgraph).to_mesh()
    mesh.calc_loop_triangles()
    triangles += len(mesh.loop_triangles)
    obj.evaluated_get(depsgraph).to_mesh_clear()
imported = {
    "objects": sorted(obj.name for obj in bpy.context.scene.objects),
    "mesh_objects": len(meshes),
    "triangles": triangles,
    "materials": sorted(m.name for m in bpy.data.materials if m.users),
    "images": sorted(i.name for i in bpy.data.images if i.users),
    "dimensions_m": [round(v, 5) for v in meshes[0].dimensions],
}
assert "ASSET_Basketball" in imported["objects"] and imported["triangles"] > 0
assert imported["images"], "normal map survived glTF round trip"
report = {
    "result": "PASS",
    "blender_version": bpy.app.version_string,
    "source_reopened": True,
    "source_sha256": before,
    "original_source_unchanged": sha(SOURCE) == before,
    "source": source,
    "glb_reimported": True,
    "glb_sha256": sha(GLB),
    "reimport": imported,
}
(HERE / "reports" / "sources.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
