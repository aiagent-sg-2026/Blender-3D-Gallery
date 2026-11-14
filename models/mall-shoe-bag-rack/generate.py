"""Original deterministic Blender 4.0.2 modular shoe and handbag retail display."""
from pathlib import Path
import bpy, math, sys
from mathutils import Vector

HERE=Path(__file__).resolve().parent
SLUG='mall-shoe-bag-rack'; ROOT='ASSET_MallShoeBagRack'; TARGET=(0,0,.84); SCALE=2.1

def mat(name, rgb, metal=0.0, rough=.42):
    m=bpy.data.materials.new(name); m.use_nodes=True
    c=tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb)+(1,)
    p=m.node_tree.nodes['Principled BSDF']; p.inputs['Base Color'].default_value=c; p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; m.diffuse_color=c
    return m
def empty(name, loc=(0,0,0), parent=None):
    o=bpy.data.objects.new(name,None); bpy.context.scene.collection.objects.link(o); o.location=loc; o.parent=parent; return o
def finish(o,name,m,parent,bevel=.003):
    o.name=name; o.data.materials.append(m); o.parent=parent
    if bevel:
        b=o.modifiers.new('Manufactured edge','BEVEL'); b.width=bevel; b.segments=2
        o.modifiers.new('Corner normals','WEIGHTED_NORMAL')
    return o
def box(name,loc,dims,m,parent,bevel=.003):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.dimensions=dims; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); return finish(o,name,m,parent,bevel)
def rod(name,a,b,r,m,parent,vertices=16):
    a,b=Vector(a),Vector(b); d=b-a; bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=d.length,location=(a+b)/2); o=bpy.context.object; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); return finish(o,name,m,parent,.001)
def disc(name,loc,r,depth,m,parent,vertices=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc); return finish(bpy.context.object,name,m,parent,.001)
def aim(o,p): o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def slide(o, axis, distance):
    start=o.location[axis]
    for f,v in [(1,start),(30,start+distance),(60,start)]: o.location[axis]=v; o.keyframe_insert(data_path='location',frame=f)
    bpy.context.scene.frame_set(1)
def build(root):
    metal=mat('Jade powder coat',(.12,.29,.28),.25,.35)
    wood=mat('Natural ash shelf',(.72,.55,.34),0,.47)
    dark=mat('Inset plinth',(.08,.10,.10),.05,.55)
    brass=mat('Brass peg and pull',(.68,.48,.20),.7,.26)
    # A modular open retail rack, not an enclosed household shoe cabinet.
    box('BASE_Plinth',(0,0,.04),(1.20,.46,.08),dark,root,.012)
    box('BASE_Rear',(0,.21,.17),(1.16,.03,.18),metal,root)
    for x in [-.58,.58]:box('BASE_Side',(x,0,.17),(.04,.44,.18),metal,root)
    box('BASE_Cap',(0,0,.28),(1.20,.46,.04),wood,root,.008)
    for x in [-.57,.17,.57]:
        box('FRAME_Upright',(x,.17,.98),(.035,.035,1.36),metal,root,.005)
    box('FRAME_Header',(0,.17,1.65),(1.18,.06,.05),metal,root,.006)
    # Three shallow display shelves with raised front lips and exposed supports.
    for i,z in enumerate([.44,.83,1.22],1):
        g=empty('EDITABLE_ShoeShelf_%02d'%i,(-.20,-.015,z),root)
        g.rotation_euler.x=math.radians(6)
        box('SHOE_Shelf_%02d'%i,(0,0,0),(.70,.37,.024),wood,g,.004)
        box('SHOE_Lip_%02d'%i,(0,-.18,.025),(.70,.018,.045),metal,g,.003)
        for x in [-.30,.30]:rod('SHOE_Support_%02d'%i,(x,.16,-.02),(x,-.10,-.02),.012,metal,g)
    # Adjacent handbag bay: display pad below two forward pegs, each with end stop.
    box('BAG_DisplayPad',(.38,-.015,.46),(.34,.37,.028),wood,root,.005)
    for i,z in enumerate([.93,1.47],1):
        rod('BAG_Rail_%02d'%i,(.18,.17,z),(.57,.17,z),.013,metal,root)
        rod('BAG_Peg_%02d'%i,(.38,.17,z),(.38,-.14,z),.012,brass,root)
        rod('BAG_Stop_%02d'%i,(.38,-.14,z-.01),(.38,-.14,z+.045),.012,brass,root)
    # A shallow open-top storage drawer with walls and bottom, no solid volume.
    drawer=empty('MOVABLE_Drawer',(0,-.005,.17),root)
    box('DRAWER_Bottom',(0,0,-.065),(1.09,.36,.018),wood,drawer,.003)
    box('DRAWER_Front',(0,-.205,0),(1.12,.028,.16),metal,drawer,.006)
    box('DRAWER_Rear',(0,.17,0),(1.09,.02,.14),wood,drawer,.003)
    for x in [-.535,.535]:box('DRAWER_Side',(x,-.01,0),(.02,.36,.14),wood,drawer,.003)
    rod('DRAWER_Handle',(-.13,-.245,0),(.13,-.245,0),.012,brass,drawer)
    for x in [-.13,.13]:rod('DRAWER_HandleMount',(x,-.215,0),(x,-.245,0),.01,brass,drawer)
    slide(drawer,1,-.22);drawer.animation_data.action.name='DrawerOpenClose'
def studio():
    s=bpy.context.scene; s.world=bpy.data.worlds.new('Neutral corridor studio'); s.world.use_nodes=True; s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.12,.15,.17,1); s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
    for name,loc,power in [('Key',(-3,-4,4),900),('Fill',(3,-2,2.5),650),('Rim',(0,3,4),900)]:
        bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.name='STUDIO_'+name; o.data.energy=power; o.data.size=4; aim(o,TARGET)
    bpy.ops.object.camera_add(); s.camera=bpy.context.object; s.camera.name='STUDIO_Camera'; s.camera.data.type='ORTHO'; s.camera.data.ortho_scale=SCALE
    s.render.engine='CYCLES'; s.cycles.samples=32; s.cycles.use_denoising=False; s.render.resolution_x=s.render.resolution_y=768; s.render.resolution_percentage=100; s.render.image_settings.file_format='PNG'; s.view_settings.look='AgX - Medium High Contrast'
def render_views():
    s=bpy.context.scene
    for name,delta in [('hero',(1.15,-2.2,.75)),('front',(0,-3,.15)),('rear',(1.25,2,.7)),('side',(2.5,-.15,.55)),('open',(-1.05,-2.1,.65))]:
        s.frame_set(30 if name=='open' else 1); s.camera.location=Vector(TARGET)+Vector((1.3,-2,.9) if name=='open' else delta)*SCALE; aim(s.camera,TARGET); s.render.filepath=str(HERE/'previews'/(name+'.png')); bpy.ops.render.render(write_still=True)
def export(path):
    bpy.ops.object.select_all(action='DESELECT'); root=bpy.data.objects[ROOT]; root.select_set(True)
    for o in root.children_recursive: o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_animations=True,export_texcoords=False,export_extras=True,export_cameras=False,export_lights=False)
def main():
    for d in ['sources','exports','previews','reports','metadata']: (HERE/d).mkdir(exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.context.preferences.filepaths.save_version=0; s=bpy.context.scene; s.unit_settings.system='METRIC'; s.unit_settings.scale_length=1
    root=empty(ROOT); root['units']='metres'; root['front_axis']='Blender -Y / glTF +Z'; root['scope']='Original illustrative retail rack; no load rating or safety certification'
    build(root); studio(); bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'sources'/(SLUG+'.blend')),compress=True); export(HERE/'exports/optimized.glb')
    if '--skip-render' not in sys.argv: render_views()
if __name__=='__main__': main()
