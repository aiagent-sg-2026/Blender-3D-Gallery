"""Create an original 1.2 m mall wall and export its editable source to GLB.

Run with Blender 5.1.2. Existing source is never overwritten without --rebuild;
--export-source exports a saved source while preserving edits.
"""
from pathlib import Path
import sys
import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
NAME = 'mall-solid-wall'
ROOT = 'ASSET_MallSolidWall'
SOURCE = HERE / 'sources' / f'{NAME}.blend'
EXPORT = HERE / 'exports' / f'{NAME}.glb'

def material(name, rgb, roughness=0.7, metallic=0):
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    rgba = tuple((v/255 / 12.92 if v/255 <= .04045 else ((v/255 + .055)/1.055)**2.4) for v in rgb) + (1,)
    result.diffuse_color = rgba
    principled = result.node_tree.nodes.get('Principled BSDF')
    principled.inputs['Base Color'].default_value = rgba
    principled.inputs['Roughness'].default_value = roughness
    principled.inputs['Metallic'].default_value = metallic
    return result

def box(name, location, dimensions, mat, parent, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Soft manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
    if parent:
        world = obj.matrix_world.copy()
        obj.parent = parent
        obj.matrix_world = world
    return obj

def point_at(obj, point):
    obj.rotation_euler = (Vector(point) - obj.location).to_track_quat('-Z', 'Y').to_euler()

def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1
    root = bpy.data.objects.new(ROOT, None)
    scene.collection.objects.link(root)
    root['units'] = 'metres'
    root['pitch_m'] = 1.2
    root['assembly'] = 'Floor centre origin. Connect x=-0.6 / +0.6 m on 1.2 m pitch; front Blender -Y / glTF +Z.'
    root['scope'] = 'Visual wall module only; no structural, fire, acoustic or construction certification.'
    wall = material('Warm ivory wall', (216, 211, 195), .78)
    panels = material('Limestone wall panels', (231, 226, 212), .76)
    metal = material('Dark bronze skirting', (74, 76, 68), .38, .35)
    box('WALL_Core', (0,.005,1.5), (1.2,.11,3), wall, root)
    # Inset panel gaps add depth while leaving the full-width core continuous.
    for i,x in enumerate((-.4,0,.4), start=1):
        box(f'PANEL_{i}', (x,-.055,1.55), (.392,.01,2.75), panels, root, .001)
    box('TRIM_Base', (0,-.055,.06), (1.2,.01,.12), metal, root)
    box('TRIM_Top', (0,-.055,2.965), (1.2,.01,.07), metal, root)
    for name,x in [('Left',-.6),('Right',.6)]:
        connector = bpy.data.objects.new('CONNECTOR_'+name,None)
        scene.collection.objects.link(connector)
        connector.parent = root
        connector.location = (x,0,0)
        connector['pitch_m'] = 1.2
    # Studio elements are deliberately outside the exported root.
    floor = material('STUDIO floor', (222,225,218), .9)
    box('STUDIO_Floor', (0,0,-.035), (20,20,.07), floor, None)
    for name,position,power,size in [('Key',(-4,-5,6),700,5),('Fill',(4,-3,3),350,5),('Back',(1,4,5),500,4)]:
        bpy.ops.object.light_add(type='AREA',location=position)
        light=bpy.context.object; light.name='STUDIO_'+name; light.data.energy=power; light.data.size=size
        point_at(light,(0,0,1.4))
    bpy.ops.object.camera_add(location=(4,-7,3.1))
    scene.camera=bpy.context.object;scene.camera.name='STUDIO_Camera';scene.camera.data.type='ORTHO';scene.camera.data.ortho_scale=3.7
    point_at(scene.camera,(0,0,1.5))
    scene.world=bpy.data.worlds.new('Studio');scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.35,.39,.36,1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
    scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
    scene.render.resolution_x=720;scene.render.resolution_y=720;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE),compress=True)
    return root

def main():
    if '--export-source' in sys.argv:
        bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False)
        root = bpy.data.objects[ROOT]
    else:
        if SOURCE.exists() and '--rebuild' not in sys.argv:
            raise RuntimeError('Source exists; use --export-source or explicitly pass --rebuild')
        root = build()
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    for obj in root.children_recursive:
        obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(EXPORT),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_animations=False,export_extras=True,export_cameras=False,export_lights=False)
    if '--skip-render' not in sys.argv:
        bpy.context.scene.render.filepath=str(HERE/'previews'/f'{NAME}.png')
        bpy.ops.render.render(write_still=True)

if __name__ == '__main__':
    main()
