"""Known material/UV fixtures for the read-only scanner, never production assets."""
from pathlib import Path
import sys
import bpy

assert bpy.app.background
folder = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
folder.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
collection = bpy.data.collections.new('QA_FixtureRoot')
bpy.context.scene.collection.children.link(collection)
mesh = bpy.data.meshes.new('TwoMaterialPatches')
mesh.from_pydata([(0,0,0),(1,0,0),(1,1,0),(0,1,0),(2,0,0),(3,0,0),(3,1,0),(2,1,0)], [], [(0,1,2,3),(4,5,6,7)])
layer = mesh.uv_layers.new(name='UVMap')
for loop, uv in zip(layer.data, [(0,0),(1,0),(1,1),(0,1),(.25,.25),(.75,.25),(.75,.75),(.25,.75)], strict=True):
    loop.uv = uv
obj = bpy.data.objects.new(mesh.name, mesh); collection.objects.link(obj)
for index, size in enumerate([64, 256]):
    image = bpy.data.images.new('KnownImage' + str(size), width=size, height=size)
    image.generated_color = (.2, .5, .7, 1); image.pack()
    material = bpy.data.materials.new('KnownMaterial' + str(size)); material.use_nodes = True
    node = material.node_tree.nodes.new('ShaderNodeTexImage'); node.image = image
    material.node_tree.links.new(node.outputs['Color'], material.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
    mesh.materials.append(material); mesh.polygons[index].material_index = index
bpy.ops.mesh.primitive_plane_add(size=1, location=(4,0,0))
plain = bpy.context.object; plain.name = 'NoImagePatch'
for owner in list(plain.users_collection): owner.objects.unlink(plain)
collection.objects.link(plain)
bpy.ops.wm.save_as_mainfile(filepath=str(folder / 'fixture.blend'))
root = bpy.data.objects.new('QA_FixtureRoot', None)
bpy.context.scene.collection.objects.link(root)
for part in collection.all_objects: part.parent = root
bpy.ops.object.select_all(action='SELECT')
assert bpy.ops.export_scene.gltf(filepath=str(folder / 'fixture.glb'), export_format='GLB', use_selection=True, use_active_scene=True) == {'FINISHED'}
