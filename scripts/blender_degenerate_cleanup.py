"""Non-destructive evaluated triangle cleanup for explicitly reviewed parts."""
import hashlib
import json

import bpy

MODIFIER_NAME = 'Degenerate face cleanup'
GROUP_NAME = 'Triangle cleanup - 0.1 micrometre weld'


def add_cleanup(obj, ngon_method='Beauty'):
    """Keep authoring data editable; remove collapsed evaluated triangles."""
    assert obj.type in {'MESH', 'FONT', 'CURVE'}, obj.name
    assert all(abs(value - 1) < 1e-6 for value in obj.matrix_world.to_scale()), obj.name
    assert ngon_method in {'Beauty', 'Clip'}
    group_name = GROUP_NAME if ngon_method == 'Beauty' else GROUP_NAME + ' / ear clip'
    existing = obj.modifiers.get(MODIFIER_NAME)
    if existing:
        assert existing.type == 'NODES' and existing.node_group.name == group_name
        return
    group = bpy.data.node_groups.get(group_name)
    if group is None:
        group = bpy.data.node_groups.new(group_name, 'GeometryNodeTree')
        group.interface.new_socket(name='Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
        group.interface.new_socket(name='Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
        nodes, links = group.nodes, group.links
        inp = nodes.new('NodeGroupInput'); inp.location = (-600, 160)
        out = nodes.new('NodeGroupOutput'); out.location = (400, 160)
        tri = nodes.new('GeometryNodeTriangulate'); tri.location = (-400, 160)
        # Match Blender's loop-triangle quad diagonal before topology changes.
        tri.inputs['Quad Method'].default_value = 'Fixed'
        # Cylinder caps can require ear clipping to retain their original
        # loop-triangle diagonals; keep the default for previously reviewed parts.
        tri.inputs['N-gon Method'].default_value = ngon_method
        merge = nodes.new('GeometryNodeMergeByDistance'); merge.location = (-200, 160)
        merge.inputs['Distance'].default_value = 1e-7
        area = nodes.new('GeometryNodeInputMeshFaceArea'); area.location = (-400, -160)
        positive = nodes.new('ShaderNodeMath'); positive.location = (-200, -160)
        positive.operation = 'GREATER_THAN'; positive.inputs[1].default_value = 0
        inverse = nodes.new('FunctionNodeBooleanMath'); inverse.location = (0, -160)
        inverse.operation = 'NOT'
        delete = nodes.new('GeometryNodeDeleteGeometry'); delete.location = (200, 160)
        delete.domain = 'FACE'
        links.new(inp.outputs['Geometry'], tri.inputs['Mesh'])
        links.new(tri.outputs['Mesh'], merge.inputs['Geometry'])
        links.new(merge.outputs['Geometry'], delete.inputs['Geometry'])
        links.new(area.outputs['Area'], positive.inputs[0])
        links.new(positive.outputs[0], inverse.inputs[0])
        links.new(inverse.outputs[0], delete.inputs['Selection'])
        links.new(delete.outputs['Geometry'], out.inputs['Geometry'])
    modifier = obj.modifiers.new(MODIFIER_NAME, 'NODES')
    modifier.node_group = group


def source_fingerprint():
    """Fingerprint authored data and scene semantics, excluding this new modifier."""
    def serial(value):
        if value is None or isinstance(value, (str, bool, int, float)):
            return value
        if hasattr(value, 'name'):
            return value.name
        return [serial(item) for item in value]

    objects = []
    for obj in sorted(bpy.data.objects, key=lambda value: value.name):
        record = {'name': obj.name, 'type': obj.type, 'matrix': [list(row) for row in obj.matrix_world],
                  'parent': obj.parent.name if obj.parent else None, 'selected': obj.select_get(),
                  'properties': {k: serial(v) for k, v in obj.items()},
                  'modifiers': [(m.name, m.type) for m in obj.modifiers if m.name != MODIFIER_NAME]}
        if obj.type in {'MESH', 'FONT', 'CURVE'}:
            record['materials'] = [m.name if m else None for m in obj.data.materials]
        if obj.type == 'MESH':
            mesh = obj.data
            record['mesh'] = {'vertices': [list(v.co) for v in mesh.vertices],
                              'edges': [list(e.vertices) for e in mesh.edges],
                              'polygons': [(list(p.vertices), p.material_index, p.use_smooth) for p in mesh.polygons],
                              'uv': [[list(d.uv) for d in layer.data] for layer in mesh.uv_layers]}
        if obj.type == 'FONT':
            record['text'] = {k: serial(getattr(obj.data, k)) for k in
                              ['body', 'font', 'size', 'extrude', 'bevel_depth', 'resolution_u', 'align_x', 'align_y']}
        if obj.type == 'CURVE':
            record['curve_settings'] = {k: serial(getattr(obj.data, k)) for k in
                                        ['dimensions', 'resolution_u', 'bevel_depth', 'bevel_resolution', 'extrude', 'use_fill_caps']}
            record['splines'] = [{'type': spline.type, 'cyclic': spline.use_cyclic_u,
                                  'points': [list(point.co) for point in spline.points],
                                  'bezier': [(list(point.co), list(point.handle_left), list(point.handle_right))
                                             for point in spline.bezier_points]}
                                 for spline in obj.data.splines]
        objects.append(record)
    materials = []
    for material in sorted(bpy.data.materials, key=lambda value: value.name):
        nodes, links = [], []
        if material.use_nodes:
            for node in material.node_tree.nodes:
                nodes.append((node.name, node.type, [(s.identifier, serial(s.default_value))
                              for s in node.inputs if hasattr(s, 'default_value')]))
            links = [(l.from_node.name, l.from_socket.identifier, l.to_node.name, l.to_socket.identifier)
                     for l in material.node_tree.links]
        materials.append((material.name, list(material.diffuse_color), nodes, links))
    scene = bpy.context.scene
    collections = [{'name': c.name, 'objects': sorted(o.name for o in c.objects),
                    'children': sorted(child.name for child in c.children),
                    'properties': {k: serial(v) for k, v in c.items()}}
                   for c in sorted(bpy.data.collections, key=lambda value: value.name)]
    data = {'objects': objects, 'materials': materials, 'collections': collections, 'cursor': list(scene.cursor.location),
            'active': bpy.context.view_layer.objects.active.name if bpy.context.view_layer.objects.active else None,
            'units': [scene.unit_settings.system, scene.unit_settings.scale_length],
            'camera': scene.camera.name if scene.camera else None, 'frame': scene.frame_current}
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def geometry_counts(objects):
    results = []
    for obj in objects:
        if obj.type not in {'MESH', 'FONT', 'CURVE'}:
            continue
        evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        mesh = evaluated.to_mesh(); mesh.transform(obj.matrix_world); mesh.calc_loop_triangles()
        results.append({'name': obj.name, 'source_type': obj.type,
                        'triangles': len(mesh.loop_triangles),
                        'zero_area_triangles': sum(t.area == 0 for t in mesh.loop_triangles)})
        evaluated.to_mesh_clear()
    return results
