"""Original 90-degree modular wall corner; --rebuild replaces saved source."""
from pathlib import Path
import sys, math
import bpy
from mathutils import Vector, Matrix
HERE=Path(__file__).resolve().parent
NAME='mall-wall-corner'
ROOT='ASSET_MallWallCorner'
SOURCE=HERE/'sources'/f'{NAME}.blend'
EXPORT=HERE/'exports'/f'{NAME}.glb'
def material(name,color,metallic=0,roughness=.7):
    m=bpy.data.materials.new(name);m.use_nodes=True
    rgb=tuple((v/255/12.92 if v/255 <= .04045 else ((v/255+.055)/1.055)**2.4) for v in color)
    m.diffuse_color=(*rgb,1);p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Metallic'].default_value=metallic;p.inputs['Roughness'].default_value=roughness
    return m
def box(name,loc,dims,mat,parent=None,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
    if bevel:
        m=o.modifiers.new('Soft manufactured edges','BEVEL');m.width=bevel;m.segments=2
    if parent:
        world=o.matrix_world.copy();o.parent=parent;o.matrix_world=world
    return o
def point(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
def build():
    bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
    root=bpy.data.objects.new(ROOT,None);s.collection.objects.link(root)
    root['assembly']='Corner centreline origin. Ends at x=-1.2m and y=-1.2m in Blender, 3m height.'
    root['scope']='Visual mall wall only; no structural, acoustic, fire or safety certification.'
    core=material('Warm ivory wall',(216,211,195),0,.78);panels=material('Limestone wall panels',(231,226,212),0,.76);metal=material('Dark bronze skirting',(74,76,68),.35,.38)
    arm=[]
    arm.append(box('ARM_X_Core',(-.63,.005,1.5),(1.14,.11,3),core,root))
    for i,x in enumerate((-.25,-.63,-1.01),1):arm.append(box(f'ARM_X_Panel_{i}',(x,-.055,1.55),(.372,.01,2.75),panels,root,.001))
    arm.append(box('ARM_X_Base',(-.63,-.055,.06),(1.14,.01,.12),metal,root))
    arm.append(box('ARM_X_Top',(-.63,-.055,2.965),(1.14,.01,.07),metal,root))
    bpy.context.view_layer.update();rotation=Matrix.Rotation(math.pi/2,4,'Z')
    for obj in arm:
        copy=obj.copy();copy.data=obj.data.copy();s.collection.objects.link(copy);copy.name=obj.name.replace('ARM_X_','ARM_Y_');copy.parent=root;copy.matrix_world=rotation @ obj.matrix_world
        # Both finished faces point into the corner (negative X / negative Y).
        copy.location.x = .005 if obj.name == 'ARM_X_Core' else -.055
    box('CORNER_Core',(.005,.005,1.5),(.11,.11,3),core,root)
    # Two external finish faces meet without occupying the same volume.
    for face,loc,dims in [('X',(-.055,0,1.55),(.01,.12,2.75)),('Y',(0,-.055,1.55),(.1,.01,2.75))]: box('CORNER_Panel_'+face,loc,dims,panels,root)
    for label,z,height in [('Base',.06,.12),('Top',2.965,.07)]:
        box('CORNER_'+label+'_X',(-.055,0,z),(.01,.12,height),metal,root)
        box('CORNER_'+label+'_Y',(0,-.055,z),(.1,.01,height),metal,root)
    for label,loc in [('X',(-1.2,0,0)),('Y',(0,-1.2,0))]:
        o=bpy.data.objects.new('CONNECTOR_'+label,None);s.collection.objects.link(o);o.parent=root;o.location=loc
    floor=material('STUDIO floor',(222,225,218),0,.9);box('STUDIO_Floor',(0,0,-.035),(20,20,.07),floor)
    for name,loc,power,size in [('Key',(-4,-5,6),700,5),('Fill',(4,-3,3),350,5),('Back',(1,4,5),500,4)]:
        bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name='STUDIO_'+name;o.data.energy=power;o.data.size=size;point(o,(-.45,-.45,1.4))
    bpy.ops.object.camera_add(location=(-4,-6,3.3));s.camera=bpy.context.object;s.camera.name='STUDIO_Camera';s.camera.data.type='ORTHO';s.camera.data.ortho_scale=4.0;point(s.camera,(-.5,-.5,1.5))
    s.world=bpy.data.worlds.new('Studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.35,.39,.36,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
    s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX'
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE),compress=True);return root
def main():
    if '--export-source' in sys.argv:
        bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False);root=bpy.data.objects[ROOT]
    else:
        if SOURCE.exists() and '--rebuild' not in sys.argv:raise RuntimeError('Source exists; use --export-source or explicitly pass --rebuild')
        root=build()
    bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
    for o in root.children_recursive:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(EXPORT),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_animations=False,export_extras=True,export_cameras=False,export_lights=False)
    if '--skip-render' not in sys.argv:
        bpy.context.scene.render.filepath=str(HERE/'previews'/f'{NAME}.png');bpy.ops.render.render(write_still=True)
if __name__=='__main__':main()
