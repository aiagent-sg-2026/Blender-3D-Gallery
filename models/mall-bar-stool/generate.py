"""Original modular swivel bar stool. Blender4.0.2, metric, no third-party art."""
from pathlib import Path
import bpy,math,sys
from mathutils import Vector
HERE=Path(__file__).resolve().parent; SLUG='mall-bar-stool'; ROOT='ASSET_MallBarStool'
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
def cylinder(name,loc,radius,depth,m,parent):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=radius,depth=depth,location=loc);return finish(bpy.context.object,name,m,parent,.003)
def build(root):
    metal=mat('Graphite powdercoat',(.18,.21,.22),.65,.34);wood=mat('Ash seat shell',(.64,.43,.25));fabric=mat('Deep teal upholstery',(.15,.37,.35),0,.82);rubber=mat('Dark base bumper',(.075,.085,.08),0,.9)
    root['units']='metres';root['front_axis']='Blender -Y / glTF +Z';root['scope']='Original illustrative bar stool; no load, safety or accessibility certification'
    cylinder('FIXED_BaseBumper',(0,0,.004),.235,.008,rubber,root)
    cylinder('FIXED_Base',(0,0,.022),.24,.028,metal,root)
    cylinder('FIXED_Column',(0,0,.368),.035,.664,metal,root)
    cylinder('FIXED_Bearing',(0,0,.706),.052,.012,metal,root)
    bpy.ops.mesh.primitive_torus_add(major_segments=48,minor_segments=8,location=(0,0,.29),major_radius=.19,minor_radius=.012)
    finish(bpy.context.object,'FIXED_FootrestRing',metal,root,0)
    for i,(x,y) in enumerate([(.18,0),(-.18,0),(0,.18),(0,-.18)]):rod('FIXED_FootrestSpoke_%02d'%i,(0,0,.29),(x,y,.29),.009,metal,root)
    swivel=empty('MOVABLE_Swivel',(0,0,.72),root)
    cylinder('SEAT_Shell',(0,0,.014),.22,.028,wood,swivel)
    cylinder('SEAT_Cushion',(0,0,.043),.21,.030,fabric,swivel)
    for i,x in enumerate([-.15,.15]):rod('BACK_Support_%02d'%i,(x,.15,0),(x,.18,.22),.012,metal,swivel)
    box('BACK_Shell',(0,.19,.22),(.40,.035,.20),wood,swivel,.012)
    box('BACK_Cushion',(0,.165,.22),(.375,.020,.18),fabric,swivel,.009)
    for frame,angle in [(1,0),(30,90),(60,0)]:
        swivel.rotation_euler.z=math.radians(angle);swivel.keyframe_insert(data_path='rotation_euler',index=2,frame=frame)
    swivel.animation_data.action.name='SeatSwivel';bpy.context.scene.frame_set(1)
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
    for name,delta,frame in [('hero',(1.5,-2,1.15),1),('front',(0,-2,1),1),('rear',(1.5,2,1.1),1),('side',(2,0,1),1),('swivel',(1.5,-2,1.15),30)]:
        s.frame_set(frame);target=Vector((0,0,.52));s.camera.location=target+Vector(delta);s.camera.data.ortho_scale=1.4;aim(s.camera,target);s.render.filepath=str(HERE/'previews'/(name+'.png'));bpy.ops.render.render(write_still=True)

def main():
    for d in ['sources','exports','previews','reports','metadata']:(HERE/d).mkdir(exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;s=bpy.context.scene;s.render.fps=24;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
    build(empty(ROOT));studio();bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'sources'/(SLUG+'.blend')),compress=True);export()
    if '--skip-render' not in sys.argv:render_views()
if __name__=='__main__':main()
