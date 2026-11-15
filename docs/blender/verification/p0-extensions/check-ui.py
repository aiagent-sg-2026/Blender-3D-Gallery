"""Run through Blender MCP in a real window, using only a disposable scene."""
import hashlib
import importlib.util
import json
from pathlib import Path

import bpy


def snapshot():
    objects = []
    for obj in sorted(bpy.data.objects, key=lambda item: item.name):
        item = {"name": obj.name, "type": obj.type, "matrix": [list(row) for row in obj.matrix_world],
                "selected": obj.select_get(), "mode": obj.mode}
        if obj.type == "MESH":
            mesh = obj.data
            item["mesh"] = {"name": mesh.name, "vertices": [list(v.co) for v in mesh.vertices],
                            "edges": [list(e.vertices) for e in mesh.edges],
                            "faces": [list(p.vertices) for p in mesh.polygons],
                            "uv": [[list(loop.uv) for loop in layer.data] for layer in mesh.uv_layers],
                            "materials": [m.name if m else None for m in mesh.materials]}
        objects.append(item)
    state = {"file": bpy.data.filepath, "objects": objects,
             "meshes": sorted(bpy.data.meshes.keys()), "scenes": sorted(bpy.data.scenes.keys()),
             "node_groups": sorted(bpy.data.node_groups.keys()),
             "collections": [{"name": c.name, "objects": sorted(c.objects.keys()), "children": sorted(c.children.keys())}
                             for c in sorted(bpy.data.collections, key=lambda item: item.name)],
             "windows": [{"scene": w.scene.name, "active": w.view_layer.objects.active.name if w.view_layer.objects.active else None,
                          "areas": [(a.type, a.ui_type) for a in w.screen.areas]} for w in bpy.context.window_manager.windows]}
    return {"geometrySelectionLayoutSha256": hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest(),
            "file": bpy.data.filepath, "objects": len(objects), "scenes": len(bpy.data.scenes),
            "dirtyFlag": bpy.data.is_dirty}


def run(output_path):
    assert not bpy.app.background, "A real editor is required to test the vendor setter"
    here = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location("p0_owned_fixture_checks", here / "probe.py")
    probe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(probe)
    window, area = next((w, a) for w in bpy.context.window_manager.windows
                        for a in w.screen.areas if a.type == "VIEW_3D")
    before = snapshot()
    original_scene, original_type, original_ui_type = window.scene, area.type, area.ui_type
    owned = bpy.data.scenes.new("P0_DisposableExtensionVerification")
    try:
        window.scene = owned
        region = next(r for r in area.regions if r.type == "WINDOW")
        with bpy.context.temp_override(window=window, area=area, region=region):
            observations = probe.run_checks(owned, ui_set=True)
    finally:
        if window.scene == owned:
            with bpy.context.temp_override(window=window):
                if bpy.context.object and bpy.context.object.mode != "OBJECT":
                    bpy.ops.object.mode_set(mode="OBJECT")
        window.scene = original_scene
        area.type, area.ui_type = original_type, original_ui_type
        for obj in list(owned.objects):
            mesh = obj.data if obj.type == "MESH" else None
            bpy.data.objects.remove(obj, do_unlink=True)
            if mesh and mesh.users == 0:
                bpy.data.meshes.remove(mesh)
        bpy.data.scenes.remove(owned)
    after = snapshot()
    assert before["geometrySelectionLayoutSha256"] == after["geometrySelectionLayoutSha256"], (before, after)
    result = {"status": "PASS", "before": before, "after": after, "observations": observations,
              "scope": "Real window/editor Python calls on a temporary scene, removed afterwards. Original geometry, selection and editor types match the recorded hash; no source scene is saved."}
    Path(output_path).write_text(json.dumps(result, indent=2) + "\n")
    return result
