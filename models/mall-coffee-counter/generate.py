"""Original modular cafe coffee counter. Blender4.0.2, metric, no third-party art."""
from pathlib import Path
import bpy,math,sys
from mathutils import Vector
HERE=Path(__file__).resolve().parent; SLUG='mall-coffee-counter'; ROOT='ASSET_MallCoffeeCounter'
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
    wood=mat('Warm oak counter panels',(.61,.43,.28));teal=mat('Deep teal storage fronts',(.15,.32,.30));stone=mat('Warm pale solid worktop',(.80,.78,.71),0,.32);metal=mat('Brushed brass hardware',(.55,.45,.28),.7,.3);dark=mat('Dark recessed plinth',(.13,.15,.14),0,.8)
    root['units']='metres';root['front_axis']='Blender -Y / glTF +Z';root['scope']='Original cafe furniture study; no appliance, plumbing, electrical or certification claims'
    box('FIXED_Plinth',(0,.02,.05),(1.66,.54,.10),dark,root,.005)
    box('FIXED_StorageBottom',(0,.02,.135),(1.74,.64,.03),wood,root)
    box('FIXED_CustomerPanel',(0,-.31,.575),(1.8,.06,1.05),wood,root,.006)
    for i in range(11):box('FIXED_FrontRib_%02d'%i,(-.80+i*.16,-.35,.57),(.025,.02,.91),wood,root,.003)
    for name,x in [('Left',-.87),('Right',.87)]:box('FIXED_Side_'+name,(x,.02,.54),(.06,.64,.78),teal,root)
    box('FIXED_StorageDivider',(.02,.02,.54),(.03,.62,.78),wood,root)
    box('FIXED_ShelfLeft',(-.42,.00,.49),(.81,.58,.025),wood,root)
    box('FIXED_ShelfRight',(.45,.00,.49),(.81,.58,.025),wood,root)
    box('FIXED_StaffWorktop',(0,.04,.95),(1.80,.64,.04),stone,root,.008)
    box('FIXED_HandoffLedge',(0,-.30,1.12),(1.84,.32,.04),stone,root,.008)
    door=empty('MOVABLE_Door',(-.84,.40,0),root)
    box('DOOR_Leaf',(.40,0,.52),(.78,.025,.70),teal,door,.005)
    rod('DOOR_Handle',(.67,.055,.45),(.67,.055,.60),.009,metal,door)
    for z in [.45,.60]:rod('DOOR_HandleMount',(.67,.0125,z),(.67,.055,z),.007,metal,door)
    for z in [.26,.78]:
        rod('HINGE_Pin',(.0,0,z-.035),(.0,0,z+.035),.010,metal,door)
        box('HINGE_FixedBracket',(-.845,.365,z),(.025,.07,.04),metal,root,.002)
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
    for name,delta,frame in [('hero',(2,-3,1.8),1),('front',(0,-3,1.1),1),('rear',(2,3,1.5),1),('side',(3,0,1.3),1),('rear-open',(1.4,3,1.7),30)]:
        if '--view' in sys.argv and name!=sys.argv[sys.argv.index('--view')+1]:continue
        s.frame_set(frame);target=Vector((-.05,.28,.57)) if name=='rear-open' else Vector((0,0,.57));s.camera.location=target+Vector(delta);s.camera.data.ortho_scale=3.2 if name=='rear-open' else 2.6;aim(s.camera,target);s.render.filepath=str(HERE/'previews'/(name+'.png'));bpy.ops.render.render(write_still=True)

def main():
    for d in ['sources','exports','previews','reports','metadata']:(HERE/d).mkdir(exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;s=bpy.context.scene;s.render.fps=24;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
    build(empty(ROOT));studio();bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'sources'/(SLUG+'.blend')),compress=True);export()
    if '--skip-render' not in sys.argv:render_views()
if __name__=='__main__':main()
