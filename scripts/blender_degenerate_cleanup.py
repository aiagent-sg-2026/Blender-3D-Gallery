"""Non-destructive evaluated triangle cleanup for explicitly reviewed parts."""
import hashlib
import json

import bpy

MODIFIER_NAME = 'Degenerate face cleanup'
GROUP_NAME = 'Triangle cleanup - 0.1 micrometre weld'
FINGERPRINT_SCHEMA = 'authored-state-v2-packed-images'


def add_cleanup(obj, ngon_method='Beauty', preserve_loop_triangles=False):
    """Keep authoring data editable; remove collapsed evaluated triangles."""
    assert obj.type in {'MESH', 'FONT', 'CURVE'}, obj.name
    assert all(abs(value - 1) < 1e-6 for value in obj.matrix_world.to_scale()), obj.name
    assert ngon_method in {'Beauty', 'Clip'}
    group_name = GROUP_NAME if ngon_method == 'Beauty' else GROUP_NAME + ' / ear clip'
    if preserve_loop_triangles:
        assert obj.type == 'MESH'
        assert all(m.name == MODIFIER_NAME for m in obj.modifiers), 'Loop-face mapping requires unmodified source topology'
        mesh = obj.data
        mesh.calc_loop_triangles()
        triangles = {}
        for triangle in mesh.loop_triangles:
            triangles.setdefault(triangle.polygon_index, []).append(set(triangle.vertices))
        attribute = mesh.attributes.get('cleanup_alternate_quad')
        if attribute is None:
            attribute = mesh.attributes.new('cleanup_alternate_quad', 'BOOLEAN', 'FACE')
        assert attribute.data_type == 'BOOLEAN' and attribute.domain == 'FACE'
        for polygon in mesh.polygons:
            assert len(polygon.vertices) in {3, 4}, 'Review N-gon topology separately'
            alternate = False
            if len(polygon.vertices) == 4:
                pair = triangles[polygon.index]
                assert len(pair) == 2
                diagonal = pair[0] & pair[1]
                a, b, c, d = polygon.vertices
                assert diagonal in ({a, c}, {b, d})
                alternate = diagonal == {b, d}
            attribute.data[polygon.index].value = alternate
        mesh.update()
        group_name = 'Triangle cleanup - source loop diagonals / no weld'
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
        incoming = inp.outputs['Geometry']
        if preserve_loop_triangles:
            alternate = nodes.new('GeometryNodeTriangulate')
            alternate.inputs['Quad Method'].default_value = 'Fixed Alternate'
            selection = nodes.new('GeometryNodeInputNamedAttribute')
            selection.data_type = 'BOOLEAN'
            selection.inputs['Name'].default_value = 'cleanup_alternate_quad'
            links.new(incoming, alternate.inputs['Mesh'])
            links.new(selection.outputs['Attribute'], alternate.inputs['Selection'])
            incoming = alternate.outputs['Mesh']
        tri = nodes.new('GeometryNodeTriangulate'); tri.location = (-400, 160)
        # Match Blender's loop-triangle quad diagonal before topology changes.
        tri.inputs['Quad Method'].default_value = 'Fixed'
        # Cylinder caps can require ear clipping to retain their original
        # loop-triangle diagonals; keep the default for previously reviewed parts.
        tri.inputs['N-gon Method'].default_value = ngon_method
        if not preserve_loop_triangles:
            merge = nodes.new('GeometryNodeMergeByDistance'); merge.location = (-200, 160)
            merge.inputs['Distance'].default_value = 1e-7
        area = nodes.new('GeometryNodeInputMeshFaceArea'); area.location = (-400, -160)
        positive = nodes.new('ShaderNodeMath'); positive.location = (-200, -160)
        positive.operation = 'GREATER_THAN'; positive.inputs[1].default_value = 0
        inverse = nodes.new('FunctionNodeBooleanMath'); inverse.location = (0, -160)
        inverse.operation = 'NOT'
        delete = nodes.new('GeometryNodeDeleteGeometry'); delete.location = (200, 160)
        delete.domain = 'FACE'
        links.new(incoming, tri.inputs['Mesh'])
        if preserve_loop_triangles:
            # Coincident radial poles need no weld. Averaging their Float32
            # heights can create slivers, so retain original vertex positions.
            links.new(tri.outputs['Mesh'], delete.inputs['Geometry'])
        else:
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

    def modifier_state(modifier):
        # Writable scalar settings include bevel width/segments and visibility;
        # exclude active/expanded UI state and read-only evaluation statistics.
        settings = {p.identifier: serial(getattr(modifier, p.identifier))
                    for p in modifier.bl_rna.properties
                    if p.type in {'BOOLEAN', 'INT', 'FLOAT', 'STRING', 'ENUM'} and not p.is_readonly
                    and p.identifier not in {'is_active', 'show_expanded'}}
        return modifier.name, modifier.type, settings

    objects = []
    for obj in sorted(bpy.data.objects, key=lambda value: value.name):
        record = {'name': obj.name, 'type': obj.type, 'matrix': [list(row) for row in obj.matrix_world],
                  'parent': obj.parent.name if obj.parent else None, 'selected': obj.select_get(),
                  'properties': {k: serial(v) for k, v in obj.items()},
                  'modifiers': [modifier_state(m) for m in obj.modifiers if m.name != MODIFIER_NAME]}
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
                nodes.append((node.name, node.type, node.image.name if getattr(node, 'image', None) else None,
                              [(s.identifier, serial(s.default_value))
                              for s in node.inputs if hasattr(s, 'default_value')]))
            links = [(l.from_node.name, l.from_socket.identifier, l.to_node.name, l.to_socket.identifier)
                     for l in material.node_tree.links]
        materials.append((material.name, list(material.diffuse_color), nodes, links))
    scene = bpy.context.scene
    collections = [{'name': c.name, 'objects': sorted(o.name for o in c.objects),
                    'children': sorted(child.name for child in c.children),
                    'properties': {k: serial(v) for k, v in c.items()}}
                   for c in sorted(bpy.data.collections, key=lambda value: value.name)]
    images = [{'name': im.name, 'source': im.source, 'filepath': im.filepath,
               'colorspace': im.colorspace_settings.name,
               'packed_sha256': hashlib.sha256(bytes(im.packed_file.data)).hexdigest() if im.packed_file else None}
              for im in sorted(bpy.data.images, key=lambda value: value.name)]
    data = {'schema': FINGERPRINT_SCHEMA, 'objects': objects, 'materials': materials, 'images': images,
            'collections': collections, 'cursor': list(scene.cursor.location),
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
