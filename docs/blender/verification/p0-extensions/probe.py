"""Exercise owned fixtures; never reset or save the connected user's scene."""
import argparse
import importlib
import json
import math
from pathlib import Path
import sys

import bpy


MODULES = (
    "bl_ext.user_default.texel_density_checker",
    "bl_ext.user_default.print3d_toolbox",
)


def finished(operator, **kwargs):
    assert operator.poll(), str(operator)
    result = operator(**kwargs)
    assert result == {"FINISHED"}, (str(operator), result)
    return sorted(result)


def select(scene, *objects, active=None):
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    for obj in scene.objects:
        obj.select_set(False)
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = active or (objects[0] if objects else None)
    bpy.context.view_layer.update()


def mesh_object(scene, name, vertices, faces, uv=None):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    if uv:
        layer = mesh.uv_layers.new(name="UVMap")
        for loop, value in zip(layer.data, uv, strict=True):
            loop.uv = value
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    return obj


def cube(scene, name, open_top=False):
    vertices = [(-.5, -.5, -.5), (.5, -.5, -.5), (.5, .5, -.5), (-.5, .5, -.5),
                (-.5, -.5, .5), (.5, -.5, .5), (.5, .5, .5), (-.5, .5, .5)]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
             (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return mesh_object(scene, name, vertices, faces[:1] + faces[2:] if open_top else faces)


def report_rows(scene):
    return [{**row._asdict(), "indices": list(row.indices) if row.indices is not None else None}
            for row in scene.print3d_toolbox.get_report()]


def value(rows, name):
    return next(row["value"] for row in rows if row["name"] == name)


def run_checks(scene, *, ui_set=False, export_path=None):
    assert scene == bpy.context.scene
    result = {"blender": bpy.app.version_string, "background": bpy.app.background,
              "area": bpy.context.area.type if bpy.context.area else None,
              "modules": [{"name": name, "file": importlib.import_module(name).__file__}
                          for name in MODULES]}
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "METERS"
    scene.unit_settings.scale_length = 1.0
    plane = mesh_object(scene, "P0_UnitPatch", [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)],
                        [(0, 1, 2, 3)], [(0, 0), (1, 0), (1, 1), (0, 1)])
    select(scene, plane)
    td = scene.td
    td.units = "1"  # px/m, independently checked against a 1 m² / 1 UV² fixture.
    td.texture_size = "1024"
    td.selected_faces = False
    td.set_method = "AVERAGE"
    td.rescale_anchor = "UV_CENTER"
    td.density_set = "512"
    finished(bpy.ops.object.texel_density_check)
    initial = float(td.density)
    assert math.isclose(initial, 1024.0, abs_tol=.002), initial
    plane.scale = (2, 2, 2)
    bpy.context.view_layer.update()
    finished(bpy.ops.object.texel_density_check)
    scaled = float(td.density)
    assert math.isclose(scaled, 512.0, abs_tol=.002), scaled
    plane.scale = (1, 1, 1)
    bpy.context.view_layer.update()
    td.texture_size = "CUSTOM"
    td.custom_width, td.custom_height = "1024", "2048"
    finished(bpy.ops.object.texel_density_check)
    rectangular = float(td.density)
    assert math.isclose(rectangular, math.sqrt(1024 * 2048), abs_tol=.002), rectangular
    td.texture_size = "1024"
    scene.unit_settings.scale_length = .01
    finished(bpy.ops.object.texel_density_check)
    unit_scaled = float(td.density)
    assert math.isclose(unit_scaled, 102400.0, abs_tol=.002), unit_scaled
    scene.unit_settings.scale_length = 1
    finished(bpy.ops.object.texel_density_check)
    result["texel"] = {"initial_px_per_m": initial, "object_scale_2_px_per_m": scaled,
                       "texture_1024x2048_px_per_m": rectangular,
                       "scene_scale_001_px_per_m": unit_scaled}
    if ui_set:
        assert not bpy.app.background and bpy.context.area is not None
        result["texel"]["set_status"] = finished(bpy.ops.object.texel_density_set)
        finished(bpy.ops.object.texel_density_check)
        measured = float(td.density)
        uv = [tuple(loop.uv) for loop in plane.data.uv_layers.active.data]
        assert math.isclose(measured, 512, abs_tol=.01), measured
        assert math.isclose(max(p[0] for p in uv) - min(p[0] for p in uv), .5, abs_tol=1e-5), uv
        result["texel"].update(set_px_per_m=measured, uv_after_set=uv)
    elif bpy.app.background:
        # The unmodified vendor setter accesses context.area.spaces. Exercise the
        # unsupported context once on a disposable mesh and retain the outcome.
        try:
            bpy.ops.object.texel_density_set()
        except (RuntimeError, AttributeError) as exc:
            message = str(exc)
            assert "NoneType" in message and "spaces" in message, message
            result["texel"]["background_set"] = {"status": "EXPECTED_CONTEXT_FAILURE", "error": message}
        else:
            raise AssertionError("Setter behavior changed; reassess background support")
        finally:
            select(scene, plane)
    select(scene)
    cancelled = bpy.ops.object.texel_density_check()
    assert cancelled == {"CANCELLED"}, cancelled
    result["texel"]["no_active_result"] = sorted(cancelled)

    solid = cube(scene, "P0_ClosedCube")
    select(scene, solid)
    finished(bpy.ops.mesh.print3d_check_all)
    closed_report = report_rows(scene)
    assert int(value(closed_report, "Non-manifold Edges")) == 0, closed_report
    assert int(value(closed_report, "Zero Faces")) == 0, closed_report
    assert int(value(closed_report, "Zero Edges")) == 0, closed_report
    assert int(value(closed_report, "Shells")) == 1, closed_report
    finished(bpy.ops.mesh.print3d_info_volume)
    volume = report_rows(scene)
    assert math.isclose(float(value(volume, "Volume").split()[0]), 1), volume
    finished(bpy.ops.mesh.print3d_info_area)
    area = report_rows(scene)
    assert math.isclose(float(value(area, "Area").split()[0]), 6), area
    opened = cube(scene, "P0_OpenCube", open_top=True)
    select(scene, solid, opened, active=opened)
    finished(bpy.ops.mesh.print3d_check_solid)
    open_report = report_rows(scene)
    assert int(value(open_report, "Non-manifold Edges")) == 4, open_report
    select(scene, solid, opened, active=solid)
    finished(bpy.ops.mesh.print3d_check_solid)
    active_solid_report = report_rows(scene)
    assert int(value(active_solid_report, "Non-manifold Edges")) == 0, active_solid_report
    flat = mesh_object(scene, "P0_Degenerate", [(0, 0, 0), (1, 0, 0), (2, 0, 0)], [(0, 1, 2)])
    select(scene, flat)
    finished(bpy.ops.mesh.print3d_check_degenerate)
    degenerate_report = report_rows(scene)
    assert int(value(degenerate_report, "Zero Faces")) == 1, degenerate_report
    result["print3d"] = {"closed_all": closed_report, "volume": volume, "area": area,
                         "open_cube_active_with_multiple_selected": open_report,
                         "closed_cube_active_with_multiple_selected": active_solid_report,
                         "degenerate": degenerate_report}
    if export_path:
        select(scene, solid)
        finished(bpy.ops.export_scene.gltf, filepath=str(export_path), export_format="GLB",
                 use_selection=True, use_active_scene=True)
        result["glb"] = str(export_path)
    result["status"] = "PASS"
    return result


def background_main():
    assert bpy.app.background, "Use run_checks in a disposable UI scene instead"
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--packages", nargs=2, type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    args.output.mkdir(parents=True, exist_ok=True)
    if args.packages:
        for package in args.packages:
            finished(bpy.ops.extensions.package_install_files, filepath=str(package.resolve()),
                     repo="user_default", enable_on_install=True)
    else:
        import addon_utils
        for name in MODULES:
            addon_utils.enable(name, default_set=True, persistent=True)
            assert addon_utils.check(name)[1], name
    scene = bpy.data.scenes.new("P0_ExtensionProbe")
    bpy.context.window.scene = scene
    observations = run_checks(scene, export_path=args.output / "closed-cube.glb")
    (args.output / "observations.json").write_text(json.dumps(observations, indent=2) + "\n")


if __name__ == "__main__":
    background_main()
