"""Inspect source and delivery copies in a disposable background Blender process."""
import argparse
import hashlib
import importlib
import json
import math
from pathlib import Path
import sys
import traceback

import addon_utils
import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[1]
MODULES = ('bl_ext.user_default.texel_density_checker', 'bl_ext.user_default.print3d_toolbox')


def save(path, data):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')
    temporary.replace(path)


def activate(obj):
    for old in bpy.context.selected_objects:
        old.select_set(False)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.context.view_layer.update()


def run_operator(operator):
    if not operator.poll():
        raise RuntimeError('Operator poll failed: ' + str(operator))
    result = operator()
    if result != {'FINISHED'}:
        raise RuntimeError(str(operator) + ': ' + str(result))


def image_uv(node, mesh):
    default = next((layer.name for layer in mesh.uv_layers if layer.active_render),
                   mesh.uv_layers.active.name if mesh.uv_layers.active else None)

    def resolve(socket, depth=0):
        if depth > 10:
            return None, 'vector graph depth exceeded'
        if not socket.is_linked:
            return default, 'implicit active render UV'
        link = socket.links[0]; source = link.from_node
        if source.type == 'UVMAP':
            return source.uv_map or default, 'explicit UV Map node'
        if source.type == 'TEX_COORD' and link.from_socket.name == 'UV':
            return default, 'Texture Coordinate UV'
        if source.type == 'MAPPING':
            neutral = all(abs(v) < 1e-8 for v in source.inputs['Location'].default_value)
            neutral &= all(abs(v) < 1e-8 for v in source.inputs['Rotation'].default_value)
            neutral &= all(abs(v - 1) < 1e-8 for v in source.inputs['Scale'].default_value)
            return resolve(source.inputs['Vector'], depth + 1) if neutral else (None, 'non-identity Mapping node; not measured')
        return None, 'unsupported vector source: ' + source.type
    return resolve(node.inputs['Vector'])


def uv_statistics(mesh, layer_name, width=1024, height=1024):
    layer = mesh.uv_layers.get(layer_name)
    if not layer:
        return None
    uv_area = [0.0] * len(mesh.polygons)
    mesh.calc_loop_triangles()
    for triangle in mesh.loop_triangles:
        a, b, c = [layer.data[i].uv for i in triangle.loops]
        uv_area[triangle.polygon_index] += abs((b.x-a.x)*(c.y-a.y) - (b.y-a.y)*(c.x-a.x)) * .5
    rows = []
    for polygon in mesh.polygons:
        area = uv_area[polygon.index]
        if area > 0 and polygon.area > 0:
            rows.append((math.sqrt(area * width * height / polygon.area), area))
    total = sum(weight for _, weight in rows)
    return {'min': min((value for value, _ in rows), default=None),
            'max': max((value for value, _ in rows), default=None),
            'uv_weighted_mean': sum(value*weight for value, weight in rows)/total if total else None,
            'positive_uv_area': total, 'zero_uv_faces': sum(a <= 1e-16 for a in uv_area),
            'nonfinite_uv_loops': sum(not all(math.isfinite(c) for c in item.uv) for item in layer.data)}


def density_for_material(probe, material_index, node, scene):
    image = node.image
    row = {'material': probe.data.materials[material_index].name, 'image': image.name if image else None}
    if not image:
        return {**row, 'status': 'MISSING_IMAGE'}
    try:
        sample = list(image.pixels[:4])
        width, height = image.size
        row.update(width=width, height=height, packed=bool(image.packed_file),
                   image_source=image.source, pixels_accessible=bool(sample), path=image.filepath)
        if not width or not height or not sample:
            return {**row, 'status': 'IMAGE_UNREADABLE'}
    except Exception as error:
        return {**row, 'status': 'IMAGE_UNREADABLE', 'error': str(error)}
    layer_name, reason = image_uv(node, probe.data)
    row.update(uv_layer=layer_name, mapping=reason)
    if not layer_name or not probe.data.uv_layers.get(layer_name):
        return {**row, 'status': 'NO_SUPPORTED_UV_MAPPING'}
    subset = probe.data.copy()
    bm = bmesh.new(); bm.from_mesh(subset)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index != material_index], context='FACES')
    bm.to_mesh(subset); bm.free(); subset.update()
    holder = bpy.data.objects.new('QA_DensitySubset', subset)
    scene.collection.objects.link(holder)
    try:
        if not len(subset.polygons):
            return {**row, 'status': 'NO_ASSIGNED_FACES'}
        subset.uv_layers.active_index = subset.uv_layers.find(layer_name)
        activate(holder)
        td = scene.td
        td.units = '1'; td.selected_faces = False; td.texture_size = 'CUSTOM'
        td.custom_width, td.custom_height = str(width), str(height)
        run_operator(bpy.ops.object.texel_density_check)
        observed = float(td.density)
        statistics = uv_statistics(subset, layer_name, width, height)
        expected = statistics['uv_weighted_mean']
        # The separate area oracle checks values; zero-area input is explicit.
        verified = expected is not None and math.isclose(observed, expected, rel_tol=.002, abs_tol=.01)
        return {**row, 'status': 'MEASURED' if verified else 'DEGENERATE_OR_ORACLE_MISMATCH',
                'density_px_per_m': observed, 'oracle': statistics,
                'method': 'Texel Density operator on assigned material faces; 1 world unit = 1 exported metre'}
    finally:
        bpy.data.objects.remove(holder, do_unlink=True)
        bpy.data.meshes.remove(subset)
        activate(probe)


def inspect_objects(objects, phase, scene):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    prepared = []
    for obj in objects:
        try:
            evaluated = obj.evaluated_get(depsgraph)
            mesh = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True, depsgraph=depsgraph)
            mesh.transform(obj.matrix_world)
            mesh.update()
            prepared.append((obj.name, obj.type, mesh, [m.type for m in obj.modifiers]))
        except Exception as error:
            prepared.append((obj.name, obj.type, None, str(error)))
    analysis = bpy.data.scenes.new('QA_AnalysisOnly')
    bpy.context.window.scene = analysis
    analysis.unit_settings.system = 'METRIC'
    analysis.unit_settings.scale_length = 1
    rows = []
    for name, source_type, mesh, modifiers in prepared:
        if mesh is None:
            rows.append({'name': name, 'status': 'EVALUATION_ERROR', 'error': modifiers}); continue
        probe = bpy.data.objects.new('QA_Probe', mesh)
        analysis.collection.objects.link(probe)
        activate(probe)
        try:
            mesh.calc_loop_triangles()
            bm = bmesh.new(); bm.from_mesh(mesh)
            topology = lambda: {'non_manifold_edges': sum(not e.is_manifold for e in bm.edges),
                                'boundary_edges': sum(e.is_boundary for e in bm.edges),
                                'loose_vertices': sum(not v.link_faces for v in bm.verts),
                                'inconsistent_winding_edges': sum(e.is_manifold and not e.is_contiguous for e in bm.edges)}
            raw = topology()
            if phase == 'glb':
                # Only a throwaway topology diagnostic is welded; UV seam splits
                # are not interpreted as holes in the delivered model.
                bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-7)
            welded = topology()
            bm.free()
            run_operator(bpy.ops.mesh.print3d_check_solid)
            solid = [{'name': r.name, 'value': r.value, 'indices_count': len(r.indices) if r.indices is not None else None}
                     for r in analysis.print3d_toolbox.get_report()]
            analysis.print3d_toolbox.threshold_zero = .0001
            run_operator(bpy.ops.mesh.print3d_check_degenerate)
            small = [{'name': r.name, 'value': r.value, 'indices_count': len(r.indices) if r.indices is not None else None}
                     for r in analysis.print3d_toolbox.get_report()]
            active_uv = mesh.uv_layers.active.name if mesh.uv_layers.active else None
            row = {'name': name, 'source_type': source_type, 'status': 'SCANNED', 'vertices': len(mesh.vertices),
                   'triangles': len(mesh.loop_triangles), 'exact_zero_area_triangles': sum(t.area == 0 for t in mesh.loop_triangles),
                   'nonfinite_vertices': sum(not all(math.isfinite(c) for c in v.co) for v in mesh.vertices),
                   'raw_topology': raw, 'position_weld_diagnostic': welded if phase == 'glb' else None,
                   'weld_tolerance_m': 1e-7 if phase == 'glb' else None,
                   'print3d_solid': solid, 'print3d_small_or_zero': small, 'small_length_threshold_m': .0001,
                   'uv_layers': [l.name for l in mesh.uv_layers],
                   'reference_1024_uv_statistics': uv_statistics(mesh, active_uv) if active_uv else None,
                   'modifiers_evaluated': modifiers, 'density': []}
            used = {p.material_index for p in mesh.polygons}
            for index, material in enumerate(mesh.materials):
                if index not in used or not material or not material.use_nodes:
                    continue
                for node in material.node_tree.nodes:
                    if node.type == 'TEX_IMAGE':
                        # GLSL appearance is out of scope. Source unused nodes are
                        # retained as source observations, not export-loss claims.
                        row['density'].append(density_for_material(probe, index, node, analysis))
            row['density_status'] = 'N_A_NO_IMAGE_TEXTURE' if not row['density'] else 'IMAGE_TEXTURE_OBSERVED'
            rows.append(row)
        finally:
            bpy.data.objects.remove(probe, do_unlink=True)
            bpy.data.meshes.remove(mesh)
    return rows


def root_objects(asset, phase):
    geometric = {'MESH', 'CURVE', 'FONT', 'SURFACE'}
    name = asset.get('root')
    if name and bpy.data.objects.get(name):
        root = bpy.data.objects[name]
        return [o for o in [root, *root.children_recursive] if o.type in geometric], {'method': 'exact catalog root', 'root': name}
    if name:
        return [], {'method': 'UNRESOLVED_SOURCE_ROOT', 'required_root': name}
    if phase == 'glb':
        return [o for o in bpy.context.scene.objects if o.type in geometric], {'method': 'all imported delivered geometry; no authoring studio imported'}
    candidates = [o for o in bpy.context.scene.objects if o.parent is None and o.type in {'EMPTY', 'ARMATURE'}
                  and any(c.type in geometric for c in o.children_recursive)]
    if len(candidates) == 1:
        root = candidates[0]
        return [o for o in [root, *root.children_recursive] if o.type in geometric], {'method': 'inferred unique geometry hierarchy; not equivalence proof', 'root': root.name}
    if len(bpy.data.scenes) == 1:
        return [o for o in bpy.context.scene.objects if o.type in geometric], {
            'method': 'rootless single-source-scene geometry; staging/variants may be included; not asset-equivalence proof'}
    return [], {'method': 'UNRESOLVED_SOURCE_ROOT', 'candidates': [o.name for o in candidates]}


def main():
    assert bpy.app.background, 'Never run this scanner in the connected UI'
    parser = argparse.ArgumentParser()
    parser.add_argument('--inventory', type=Path, required=True)
    parser.add_argument('--asset', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    inventory = json.loads(args.inventory.read_text())
    asset = next(a for a in inventory['assets'] if a['id'] == args.asset)
    for name in MODULES:
        addon_utils.enable(name, default_set=True, persistent=True)
        assert addon_utils.check(name)[1], name
    import tomllib
    versions = {}
    for name in MODULES:
        directory = Path(importlib.import_module(name).__file__).parent
        versions[name] = tomllib.loads((directory / 'blender_manifest.toml').read_text())['version']
    assert list(versions.values()) == ['2026.1.1', '1.5.0'], versions
    result = {'id': asset['id'], 'blender': bpy.app.version_string, 'modules': versions, 'phases': {}}
    for phase in ['source', 'glb']:
        try:
            if phase == 'source':
                if not asset.get('source'):
                    result['phases'][phase] = {'status': 'NO_SOURCE'}; continue
                bpy.ops.wm.open_mainfile(filepath=str(ROOT / asset['source']), load_ui=False, use_scripts=False)
            else:
                structural = json.loads((args.output / 'glb' / (args.asset + '.json')).read_text())
                if structural['status'] == 'HOLD_FORMAT':
                    result['phases'][phase] = {'status': 'HOLD_FORMAT'}; continue
                bpy.ops.wm.read_factory_settings(use_empty=True)
                for name in MODULES:
                    if not addon_utils.check(name)[1]: addon_utils.enable(name, default_set=True, persistent=True)
                run = bpy.ops.import_scene.gltf(filepath=str(ROOT / asset['file']))
                assert run == {'FINISHED'}, run
            original = bpy.context.scene
            bpy.context.view_layer.update()
            objects, mapping = root_objects(asset, phase)
            result['phases'][phase] = {'status': 'SCANNED' if objects else 'ROOT_UNRESOLVED', 'mapping': mapping,
                                      'file_version': list(bpy.data.version), 'declared_scene_scale': original.unit_settings.scale_length,
                                      'source_geometry_count': len(objects), 'meshes': inspect_objects(objects, phase, original) if objects else []}
        except Exception as error:
            result['phases'][phase] = {'status': 'SCAN_ERROR', 'error': str(error), 'traceback': traceback.format_exc()}
    result['status'] = 'SCANNED' if all(p['status'] == 'SCANNED' for p in result['phases'].values()) else 'PARTIAL'
    directory = args.output / 'blender'; directory.mkdir(exist_ok=True)
    save(directory / (args.asset + '.json'), result)
    print('MALL_QA', args.asset, result['status'], flush=True)


if __name__ == '__main__':
    main()
