"""Small knowledge experiments; run only in a fresh background Blender process."""
from pathlib import Path
import bpy
import bmesh
import json
import sys

out = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
out.mkdir(parents=True, exist_ok=True)
assert bpy.app.background, 'Never run this fixture in an interactive user scene'
bpy.ops.wm.read_factory_settings(use_empty=True)
observations = {
    'blender': bpy.app.version_string,
    'python': sys.version.split()[0],
    'background': bpy.app.background,
    'view3d_poll': bpy.ops.view3d.view_selected.poll(),
    'primitive_poll': bpy.ops.mesh.primitive_cube_add.poll(),
}

# Object.copy keeps the same mesh until a separate data copy is assigned.
bpy.ops.mesh.primitive_cube_add(size=1)
original = bpy.context.object
linked = original.copy()
bpy.context.scene.collection.objects.link(linked)
observations['object_copy_shares_mesh'] = linked.data is original.data
before = original.data.vertices[0].co.x
linked.data.vertices[0].co.x += .125
observations['linked_edit_changes_original'] = abs(original.data.vertices[0].co.x - before - .125) < 1e-6
linked.data = original.data.copy()
before = original.data.vertices[0].co.x
linked.data.vertices[0].co.x += .25
observations['data_copy_isolates_edit'] = abs(original.data.vertices[0].co.x - before) < 1e-6

# Use one known object to make an independent export oracle straightforward.
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1
bpy.ops.mesh.primitive_cube_add(size=1, location=(4, -5, 6))
cube = bpy.context.object
cube.name = 'KnowledgeProbe'
cube.dimensions = (1, 2, 3)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
for polygon in cube.data.polygons:
    polygon.use_smooth = True
mesh = bmesh.new()
mesh.from_mesh(cube.data)
observations['source_vertices'] = len(mesh.verts)
observations['source_faces'] = len(mesh.faces)
observations['source_manifold'] = all(edge.is_manifold for edge in mesh.edges)
observations['source_volume_m3'] = mesh.calc_volume(signed=True)
mesh.free()
material = bpy.data.materials.new('KnowledgePBR')
material.use_nodes = True
bsdf = material.node_tree.nodes.get('Principled BSDF')
bsdf.inputs['Base Color'].default_value = (.1, .2, .3, 1)
bsdf.inputs['Metallic'].default_value = .15
bsdf.inputs['Roughness'].default_value = .42
cube.data.materials.append(material)
observations['principled_inputs'] = [i.name for i in bsdf.inputs if i.name in
                                    ('Base Color', 'Metallic', 'Roughness', 'Coat Weight', 'Clearcoat')]
rna = bpy.ops.export_scene.gltf.get_rna_type()
observations['export_properties'] = {}
for key in ('export_yup', 'export_apply', 'export_gpu_instances', 'export_animation_mode'):
    prop = rna.properties.get(key)
    observations['export_properties'][key] = None if prop is None else {
        'type': prop.type, 'default': prop.default,
        'enum': [v.identifier for v in prop.enum_items] if prop.type == 'ENUM' else None,
    }


def export(name, animations=False):
    kwargs = {'filepath': str(out / name), 'export_format': 'GLB', 'use_selection': True,
              'export_yup': True, 'export_animations': animations, 'export_apply': False}
    if animations:
        kwargs['export_animation_mode'] = 'ACTIONS'
    bpy.ops.export_scene.gltf(**kwargs)


export('cube-uv.glb')
while cube.data.uv_layers:
    cube.data.uv_layers.remove(cube.data.uv_layers[0])
export('cube-no-uv.glb')
scene.unit_settings.scale_length = .01
export('cube-unit-scale-001.glb')
scene.unit_settings.scale_length = 1
scene.render.fps = 10
scene.frame_start, scene.frame_end = 1, 11
cube.location.x = 4
cube.keyframe_insert(data_path='location', frame=1)
cube.location.x = 5
cube.keyframe_insert(data_path='location', frame=11)
action = cube.animation_data.action
action.name = 'probe_move'
observations['action_slots'] = len(action.slots) if hasattr(action, 'slots') else None
scene.frame_set(1)
export('cube-animated.glb', animations=True)
(out / 'observations.json').write_text(json.dumps(observations, indent=2) + '\n')
print('KNOWLEDGE_PROBE_COMPLETE')
