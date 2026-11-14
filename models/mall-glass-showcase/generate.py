"""Original metric mall retail showcase. Blender 4.0.2, no external assets."""
from pathlib import Path
import bpy, math, sys
from mathutils import Vector

HERE=Path(__file__).resolve().parent; SLUG='mall-glass-showcase'; ROOT='ASSET_MallGlassShowcase'
def mat(name,rgb,metal=0.0,rough=.4,alpha=1.0):
    m=bpy.data.materials.new(name); m.use_nodes=True; c=tuple(rgb)+(alpha,); p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=c; p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; p.inputs['Alpha'].default_value=alpha; m.diffuse_color=c
    if alpha<1: m.blend_method='BLEND'
    return m
def empty(name,loc=(0,0,0),parent=None):
    o=bpy.data.objects.new(name,None); bpy.context.scene.collection.objects.link(o); o.location=loc; o.parent=parent; return o
def box(name,loc,dims,material,parent,bevel=.002):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=dims; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(material); o.parent=parent
    if bevel: b=o.modifiers.new('Manufactured edge','BEVEL'); b.width=bevel; b.segments=2; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o
def rod(name,a,b,r,material,parent):
    a,b=Vector(a),Vector(b); d=b-a; bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=r,depth=d.length,location=(a+b)/2); o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(material); o.parent=parent; return o
def aim(o,p): o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def slide_or_swing(o):
    o.rotation_euler.z=0; o.keyframe_insert('rotation_euler',index=2,frame=1); o.keyframe_insert('rotation_euler',index=2,frame=60)
    o.rotation_euler.z=math.radians(105); o.keyframe_insert('rotation_euler',index=2,frame=30); bpy.context.scene.frame_set(1)
def build(root):
    steel=mat('Neutral aluminium',(.48,.53,.56),.78,.25); dark=mat('Plinth rubber',(.08,.09,.10),.15,.5); shelfmat=mat('Shelf aluminium',(.63,.67,.68),.72,.3); glass=mat('Clear architectural glass',(.48,.72,.78),.0,.12,.16); handlemat=mat('Handle steel',(.25,.29,.30),.85,.2)
    root['units']='metres'; root['front_axis']='Blender -Y / glTF +Z'; root['scope']='Original unbranded illustrative display tower; no merchandise or certification'
    box('PLINTH',(0,0,.055),(.75,.50,.11),dark,root,.012)
    box('PLINTH_Cap',(0,0,.125),(.70,.46,.03),steel,root,.006)
    # structural uprights and top/bottom rails leave a genuinely hollow interior
    for x in (-.36,.36):
        rod('FRAME_Left' if x<0 else 'FRAME_Right',(x,-.21,.14),(x,-.21,1.77),.014,steel,root)
        rod('FRAME_Rear_Left' if x<0 else 'FRAME_Rear_Right',(x,.21,.14),(x,.21,1.77),.014,steel,root)
    for z,n in ((.14,'FRAME_BaseRail'),(1.7825,'FRAME_TopRail')): box(n,(0,0,z),(.75,.46,.035),steel,root,.006)
    box('GLASS_Side_Left',(-.365,0,.95),(.012,.42,1.58),glass,root,.002); box('GLASS_Side_Right',(.365,0,.95),(.012,.42,1.58),glass,root,.002)
    box('GLASS_Back',(0,.215,.95),(.70,.012,1.58),glass,root,.002)
    for i,z in enumerate((.47,.91,1.35),1): box(f'SHELF_{i:02d}',(0,-.005,z),(.67,.39,.018),glass,root,.003)
    # Door is a separate pivoted assembly, hinged on the right with actual front clearance.
    pivot=empty('MOVABLE_Door',(.345,-.235,.95),root); pivot['hinge_clearance_m']=.011
    box('DOOR_Glass',(-.345,0,0),(.68,.012,1.58),glass,pivot,.002)
    box('DOOR_TopRail',(-.345,0,.77),(.70,.025,.025),steel,pivot,.003); box('DOOR_BottomRail',(-.345,0,-.77),(.70,.025,.025),steel,pivot,.003)
    rod('DOOR_HingeUpper',(.0,.015,.55),(.0,.015,.72),.009,handlemat,pivot); rod('DOOR_HingeLower',(.0,.015,-.72),(.0,.015,-.55),.009,handlemat,pivot)
    rod('DOOR_Handle',(-.62,-.035,-.18),(-.62,-.035,.18),.012,handlemat,pivot)
    slide_or_swing(pivot); pivot.animation_data.action.name='DoorOpenClose'
def studio():
    s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.samples=48; s.cycles.use_denoising=False; s.render.resolution_x=s.render.resolution_y=640; s.render.resolution_percentage=100; s.render.image_settings.file_format='PNG'; s.world=bpy.data.worlds.new('Neutral studio'); s.world.use_nodes=True; s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.06,.08,.10,1); s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
    for n,loc,p in [('Key',(-3,-4,4),850),('Fill',(3,-2,2.5),600),('Rim',(1,3,4),900)]: bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.name='STUDIO_'+n; o.data.energy=p; o.data.shape='DISK'; o.data.size=3; aim(o,(0,0,.9))
    bpy.ops.object.camera_add(); s.camera=bpy.context.object; s.camera.data.type='ORTHO'; s.camera.data.ortho_scale=2.2
def export(path=None):
    bpy.ops.object.select_all(action='DESELECT'); r=bpy.data.objects[ROOT]; r.select_set(True); [o.select_set(True) for o in r.children_recursive]
    bpy.ops.export_scene.gltf(filepath=str(path or HERE/'exports/optimized.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_animations=True,export_texcoords=False,export_extras=True,export_cameras=False,export_lights=False)
def render_views():
    s=bpy.context.scene
    for n,d,f in [('hero',(1.15,-1.8,.95),1),('front',(0,-2.4,.85),1),('rear',(1.15,1.8,.95),1),('side',(2.1,-.1,.9),1),('open',(1.05,-1.8,.95),30)]:
        s.frame_set(f); target=(.12,-.16,.9) if n=='open' else (0,0,.9); s.camera.data.ortho_scale=2.6 if n=='open' else 2.2; s.camera.location=Vector(target)+Vector(d); aim(s.camera,target); s.render.filepath=str(HERE/'previews'/(n+'.png')); bpy.ops.render.render(write_still=True)
def main():
    for d in ('sources','exports','previews','reports','metadata'): (HERE/d).mkdir(exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True); s=bpy.context.scene; bpy.context.preferences.filepaths.save_version=0; s.unit_settings.system='METRIC'; s.unit_settings.scale_length=1; root=empty(ROOT); build(root); studio(); bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'sources'/f'{SLUG}.blend'),compress=True); export();
    if '--skip-render' not in sys.argv: render_views()
if __name__=='__main__': main()
