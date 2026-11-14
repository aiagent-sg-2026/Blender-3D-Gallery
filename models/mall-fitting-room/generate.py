"""Original modular fitting-room study. Blender4.0.2, metric, no third-party art."""
from pathlib import Path
import bpy,math,sys
from mathutils import Vector
HERE=Path(__file__).resolve().parent; SLUG='mall-fitting-room'; ROOT='ASSET_MallFittingRoom'
def mat(name,rgb,metal=0,rough=.5):
    m=bpy.data.materials.new(name);m.use_nodes=True
    c=tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb)+(1,)
    p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=c;p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;m.diffuse_color=c;return m
def empty(name,loc=(0,0,0),parent=None):
    o=bpy.data.objects.new(name,None);bpy.context.scene.collection.objects.link(o);o.location=loc;o.parent=parent;return o
def finish(o,name,m,parent,bevel=.003):
    o.name=name;o.data.materials.append(m);o.parent=parent
    if bevel:
        b=o.modifiers.new('Soft manufactured edge','BEVEL');b.width=bevel;b.segments=2;o.modifiers.new('Corner normals','WEIGHTED_NORMAL')
    return o
def box(name,loc,dims,m,parent,bevel=.003):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,name,m,parent,bevel)
def rod(name,a,b,r,m,parent):
    a,b=Vector(a),Vector(b);d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return finish(o,name,m,parent,.001)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def build(root):
    wall=mat('Warm ivory opaque laminate',(.83,.81,.74));jade=mat('Deep teal door and trim',(.14,.31,.29),.05,.4);wood=mat('Light ash furniture',(.72,.56,.37));metal=mat('Brushed warm hardware',(.56,.47,.32),.65,.3);floor=mat('Matte inset floor',(.29,.32,.29),0,.7)
    root['units']='metres';root['front_axis']='Blender -Y / glTF +Z';root['scope']='Original illustrative fitting-room module; no accessibility, building-code or safety certification'
    box('FLOOR_Module',(0,0,.015),(1.60,1.50,.03),floor,root,.004)
    box('WALL_Back',(0,.72,1.115),(1.60,.06,2.17),wall,root)
    for side,x in [('Left',-.77),('Right',.77)]:
        box('WALL_'+side,(x,0,1.115),(.06,1.50,2.17),wall,root)
        box('FRONT_'+side,(-.65 if x<0 else .65,-.75,1.115),(.24,.06,2.17),wall,root)
        box('FRAME_'+side,(-.50 if x<0 else .50,-.75,1.115),(.06,.06,2.17),jade,root)
    box('FRAME_Header',(0,-.75,2.15),(.94,.06,.10),jade,root)
    # No ceiling: independently reusable partitions and visible interior from above.
    furniture=empty('EDITABLE_InteriorFurniture',parent=root)
    box('BENCH_Seat',(0,.47,.46),(1.10,.36,.05),wood,furniture,.009)
    for x in [-.46,.46]:
        for y in [.35,.59]:box('BENCH_Leg',(x,y,.2325),(.045,.045,.405),jade,furniture)
    box('SHELF_PersonalItems',(.43,.55,1.30),(.44,.26,.028),wood,furniture,.005)
    for x in [.28,.58]:rod('SHELF_Bracket',(x,.68,1.27),(x,.49,1.27),.012,metal,furniture)
    for i,y in enumerate([-.10,.20],1):
        box('HOOK_Plate_%02d'%i,(-.732,y,1.62),(.012,.055,.09),jade,furniture)
        rod('HOOK_Arm_%02d'%i,(-.72,y,1.61),(-.64,y,1.61),.008,metal,furniture)
        rod('HOOK_Stop_%02d'%i,(-.64,y,1.61),(-.64,y,1.65),.008,metal,furniture)
    # Right hinge placed in front of frame; positive Z rotation swings into -Y.
    door=empty('MOVABLE_Door',(.46,-.81,0),root);door['opening_degrees']=105
    box('DOOR_Leaf',(-.46,0,1.07),(.90,.035,2.06),jade,door,.006)
    # Both handles are separated editable solids. Interior handle remains in doorway when shut.
    for side,y in [('Outer',-.055),('Inner',.055)]:
        rod('DOOR_Handle_'+side,(-.79,y,.94),(-.79,y,1.13),.012,metal,door)
        for z in [.94,1.13]:rod('DOOR_HandleMount_'+side,(-.79,-.0175 if y<0 else .0175,z),(-.79,y,z),.009,metal,door)
    for z in [.38,1.72]:
        rod('HINGE_Pin',(.0,.008,z-.07),(.0,.008,z+.07),.012,metal,door)
        box('HINGE_FixedPlate',(.48,-.78,z),(.04,.018,.15),metal,root,.001)
    box('SIGN_Panel',(0,-.785,2.15),(.34,.012,.075),wood,root,.003)
    for frame,angle in [(1,0),(30,105),(60,0)]:
        door.rotation_euler.z=math.radians(angle);door.keyframe_insert(data_path='rotation_euler',index=2,frame=frame)
    door.animation_data.action.name='DoorOpenClose';bpy.context.scene.frame_set(1)
def studio():
    s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=False;s.render.resolution_x=s.render.resolution_y=768;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
    s.world=bpy.data.worlds.new('Neutral retail studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.13,.15,.16,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6;s.view_settings.look='AgX - Medium High Contrast'
    for n,loc,p in [('Key',(-3,-4,4.5),1100),('Fill',(3,-3,3),850),('Top',(0,.1,4.5),1100)]:
        bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name='STUDIO_'+n;o.data.energy=p;o.data.size=4;aim(o,(0,0,1))
    bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.name='STUDIO_Camera';s.camera.data.type='ORTHO'
def export(path=None):
    bpy.ops.object.select_all(action='DESELECT');r=bpy.data.objects[ROOT];r.select_set(True)
    for o in r.children_recursive:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(path or HERE/'exports/optimized.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_animations=True,export_texcoords=False,export_extras=True,export_cameras=False,export_lights=False)
def render_views():
    s=bpy.context.scene
    for name,delta,frame in [('hero',(2,-3,1.5),1),('front',(0,-3,1),1),('rear',(2,3,1.3),1),('side',(3,-1,1.2),1),('open',(-1.8,-3,1.8),30),('interior',(-.8,-3,2.6),30)]:
        s.frame_set(frame);target=Vector((0,-.35,1.05));s.camera.location=target+Vector(delta);s.camera.data.ortho_scale=3.7 if frame==30 else 3.2;aim(s.camera,target);s.render.filepath=str(HERE/'previews'/(name+'.png'));bpy.ops.render.render(write_still=True)
def main():
    for d in ['sources','exports','previews','reports','metadata']:(HERE/d).mkdir(exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;s=bpy.context.scene;s.render.fps=24;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
    build(empty(ROOT));studio();bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'sources'/(SLUG+'.blend')),compress=True);export()
    if '--skip-render' not in sys.argv:render_views()
if __name__=='__main__':main()
