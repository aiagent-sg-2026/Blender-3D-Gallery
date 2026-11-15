"""Original 60 mm mall floor corner trim. --rebuild replaces the saved source."""
from pathlib import Path
import sys
import bpy
from mathutils import Vector
HERE=Path(__file__).resolve().parent
NAME='mall-floor-corner-trim'
ROOT='ASSET_MallFloorCornerTrim'
SOURCE=HERE/'sources'/f'{NAME}.blend'
EXPORT=HERE/'exports'/f'{NAME}.glb'
def material(name,color,metallic,roughness):
    m=bpy.data.materials.new(name);m.use_nodes=True
    rgb=tuple((v/255/12.92 if v/255 <= .04045 else ((v/255+.055)/1.055)**2.4) for v in color)
    m.diffuse_color=(*rgb,1);p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Metallic'].default_value=metallic;p.inputs['Roughness'].default_value=roughness
    return m
def box(name,loc,dims,mat,parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
    if parent:
        world=o.matrix_world.copy();o.parent=parent;o.matrix_world=world
    return o
def point(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
def build():
    bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
    root=bpy.data.objects.new(ROOT,None);s.collection.objects.link(root)
    root['side_m']=.06;root['origin']='Top-centre, finished floor height';root['scope']='Visual floor trim only; no structural, slip, installation or safety certification.'
    base=material('Dark trim support',(75,78,70),.25,.55)
    cap=material('Brushed champagne trim',(164,152,126),.6,.38)
    box('TRIM_Body',(0,0,-.017),(.06,.06,.026),base,root)
    box('TRIM_Cap',(0,0,-.002),(.06,.06,.004),cap,root)
    for label,xy in [('Left',(-.03,0)),('Right',(.03,0)),('Front',(0,-.03)),('Back',(0,.03))]:
        o=bpy.data.objects.new('CONNECTOR_'+label,None);s.collection.objects.link(o);o.parent=root;o.location=(*xy,0)
    floor=material('STUDIO background',(215,220,211),0,.9)
    box('STUDIO_Floor',(0,0,-.035),(20,20,.01),floor)
    for name,loc,power,size in [('Key',(-2,-3,4),420,4),('Fill',(3,-1,2),210,3),('Back',(1,3,3),300,3)]:
        bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name='STUDIO_'+name;o.data.energy=power;o.data.size=size;point(o,(0,0,0))
    bpy.ops.object.camera_add(location=(.14,-.21,.18));s.camera=bpy.context.object;s.camera.name='STUDIO_Camera';s.camera.data.type='ORTHO';s.camera.data.ortho_scale=.13;point(s.camera,(0,0,0))
    s.world=bpy.data.worlds.new('Studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.3,.35,.31,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6
    s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX'
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE),compress=True)
    return root
def main():
    if '--export-source' in sys.argv:
        bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False);root=bpy.data.objects[ROOT]
    else:
        if SOURCE.exists() and '--rebuild' not in sys.argv:raise RuntimeError('Source exists; use --export-source or explicitly pass --rebuild')
        root=build()
    bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
    for obj in root.children_recursive:obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(EXPORT),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_animations=False,export_extras=True,export_cameras=False,export_lights=False)
    if '--skip-render' not in sys.argv:
        bpy.context.scene.render.filepath=str(HERE/'previews'/f'{NAME}.png');bpy.ops.render.render(write_still=True)
if __name__=='__main__':main()
