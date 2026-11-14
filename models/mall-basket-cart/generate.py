"""Create the reference-inspired interactive wire cart with Blender 5.1.

Outputs only this model's source, self-contained GLB, and preview renders.
"""
from pathlib import Path
import math
import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = 'ASSET_InteractiveShoppingCart'

def material(name, color, metallic=0.0, roughness=0.4):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    return m

def empty(name, position=(0, 0, 0), parent=None):
    o = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(o)
    o.location = position
    o.parent = parent
    return o

def box(name, position, size, material, parent, bevel=0.006):
    bpy.ops.mesh.primitive_cube_add(size=1, location=position)
    o = bpy.context.object
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    o.parent = parent
    if bevel:
        mod = o.modifiers.new('Rounded edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        o.modifiers.new('Corner normals', 'WEIGHTED_NORMAL')
    return o

def rod(name, a, b, radius, material, parent, vertices=12):
    a, b = Vector(a), Vector(b)
    delta = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=delta.length, location=(a+b)/2)
    o = bpy.context.object
    o.name = name
    o.rotation_euler = delta.to_track_quat('Z', 'Y').to_euler()
    o.data.materials.append(material)
    o.parent = parent
    for poly in o.data.polygons: poly.use_smooth = True
    return o

def poly_tube(name, points, radius, material, parent):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 8
    curve.bevel_depth = radius
    curve.bevel_resolution = 3
    spline = curve.splines.new('POLY')
    spline.points.add(len(points)-1)
    for p, xyz in zip(spline.points, points): p.co = (*xyz, 1)
    o = bpy.data.objects.new(name, curve)
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(material)
    o.parent = parent
    return o

def local_parent(o, parent, local_position):
    o.parent = parent
    o.location = local_position

def wheel(name, x, y, steel, rubber, orange, parent, steerable):
    swivel = empty('Steer_'+name, (x,y,0.12), parent)
    fork = box('Fork_'+name, (0,0,0), (0.09,0.095,0.105), steel, swivel, 0.012)
    fork.location = (0,0,0.03)
    axle = empty('Wheel_'+name, (0,0,-0.04), swivel)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.079, depth=0.048)
    tire=bpy.context.object; tire.name='Rubber_'+name
    tire.rotation_euler[1]=math.pi/2
    tire.data.materials.append(rubber);local_parent(tire,axle,(0,0,0))
    bevel=tire.modifiers.new('Rounded tire edge','BEVEL');bevel.width=.006;bevel.segments=3
    for poly in tire.data.polygons: poly.use_smooth=True
    bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=.034,depth=.050)
    hub=bpy.context.object;hub.name='OrangeHub_'+name;hub.rotation_euler[1]=math.pi/2;hub.data.materials.append(orange);local_parent(hub,axle,(0,0,0))
    axle.rotation_euler.x=0;axle.keyframe_insert(data_path='rotation_euler',frame=1,index=0)
    axle.rotation_euler.x=2*math.pi;axle.keyframe_insert(data_path='rotation_euler',frame=49,index=0)
    axle.animation_data.action.name='Roll_'+name
    if steerable:
        for frame, angle in [(1,0),(25,math.radians(35)),(49,0)]:
            swivel.rotation_euler.z=angle;swivel.keyframe_insert(data_path='rotation_euler',frame=frame,index=2)
        swivel.animation_data.action.name='Steer_'+name
    return axle

def aim(o, target):
    o.rotation_euler = (Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene
    scene.unit_settings.system='METRIC';scene.render.fps=24
    scene.frame_start=1;scene.frame_end=49
    bpy.context.preferences.filepaths.save_version=0
    steel=material('Satin stainless steel',(.56,.60,.62),.8,.28)
    dark=material('Dark coated steel',(.055,.065,.067),.45,.36)
    rubber=material('Wheel rubber',(.035,.039,.04),0,.72)
    orange=material('Orange molded plastic',(.95,.24,.025),0,.32)
    cream=material('Sample package',(.83,.75,.53),0,.55)
    root=empty(ROOT);root['units']='metres';root['front_axis']='Blender -Y / glTF +Z'
    cart=empty('CartMotion',parent=root)
    # Frame maximum length 1.05 m, width 0.60 m, height 1.00 m.
    for x in (-.255,.255):
        poly_tube('FrameSide',[(x,-.52,.19),(x,-.48,.16),(x,.44,.16),(x,.50,.20),(x,.50,.94),(x,.47,.98)],.016,dark,cart)
        rod('UnderBasketRail',(x,-.41,.25),(x,.39,.25),.010,dark,cart)
    for y in (-.46,.39): rod('FrameCross',(-.255,y,.17),(.255,y,.17),.015,dark,cart)
    rod('OrangeHandle',(-.265,.47,.98),(.265,.47,.98),.025,orange,cart,20)
    for z,xw,y0,y1 in [(.46,.225,-.34,.28),(.90,.275,-.41,.34)]:
        for x in (-xw,xw): rod('BasketRimSide',(x,y0,z),(x,y1,z),.009,steel,cart)
        for y in (y0,y1): rod('BasketRimEnd',(-xw,y,z),(xw,y,z),.009,steel,cart)
    # Vertical wire lattice tapers towards the bottom; horizontal wires tie it together.
    for t in [i/8 for i in range(9)]:
        y0=-.34+t*.62; y1=-.41+t*.75
        for side in (-1,1): rod('BasketSideWire',(side*.225,y0,.47),(side*.275,y1,.89),.0035,steel,cart,8)
    for t in [i/6 for i in range(7)]:
        x0=-.225+t*.45; x1=-.275+t*.55
        for y0,y1 in [(-.34,-.41),(.28,.34)]: rod('BasketEndWire',(x0,y0,.47),(x1,y1,.89),.0035,steel,cart,8)
        rod('BasketFloorWire',(x0,-.34,.47),(x0,.28,.47),.0035,steel,cart,8)
    for t in (.25,.50,.75):
        z=.46+.44*t;xw=.225+.05*t;y0=-.34-.07*t;y1=.28+.06*t
        for x in (-xw,xw): rod('BasketHorizontal',(x,y0,z),(x,y1,z),.0035,steel,cart,8)
        for y in (y0,y1): rod('BasketHorizontal',(-xw,y,z),(xw,y,z),.0035,steel,cart,8)
    for y in (-.30,-.15,0,.15,.27): rod('BasketFloorCross',(-.225,y,.46),(.225,y,.46),.0035,steel,cart,8)
    # Orange plastic protects the rim and connects the reference image's palette.
    for x in (-.278,.278): rod('OrangeRim', (x,-.41,.91),(x,.34,.91),.010,orange,cart)
    for y in (-.41,.34): rod('OrangeRim',(-.278,y,.91),(.278,y,.91),.010,orange,cart)
    for name,x,y,steer in [('FrontLeft',-.255,-.40,True),('FrontRight',.255,-.40,True),('RearLeft',-.255,.38,False),('RearRight',.255,.38,False)]: wheel(name,x,y,dark,rubber,orange,cart,steer)
    item=empty('BasketItem',(0,0,.57),cart)
    pkg=box('SampleItem',(0,0,0),(.115,.10,.16),cream,item,.009);pkg.location=(0,0,0)
    band=box('SampleItemBand',(0,0,0),(.118,.103,.025),orange,item,.003);band.location=(0,0,.015)
    for frame,z in [(1,.57),(2,1.24),(30,.57)]: item.location.z=z;item.keyframe_insert(data_path='location',frame=frame)
    item.animation_data.action.name='PlaceItem'
    scene.frame_set(1)
    # Save editable source before exporting only the asset hierarchy.
    world=bpy.data.worlds.new('Studio world');scene.world=world;world.use_nodes=True
    world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.65,.65,1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
    for name,loc,power,size in [('Key',(3,-4,6),700,4),('Fill',(-4,-1,3),400,4),('Rim',(0,4,5),650,3)]:
        bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name='STUDIO_'+name;o.data.energy=power;o.data.size=size;aim(o,(0,0,.55))
    bpy.ops.object.camera_add(location=(2,-3,2));scene.camera=bpy.context.object;scene.camera.name='STUDIO_Camera';scene.camera.data.type='ORTHO';scene.camera.data.ortho_scale=1.8;aim(scene.camera,(0,0,.5))
    scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.render.resolution_x=scene.render.resolution_y=768;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'sources/interactive-shopping-cart.blend'),compress=True)
    bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
    for o in root.children_recursive:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(HERE/'exports/interactive-shopping-cart.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_animations=True,export_texcoords=False,export_extras=True,export_cameras=False,export_lights=False)
    for name,loc in [('hero',(2,-3,2)),('rear',(2,3,2)),('side',(3,0,1.4))]:
        scene.camera.location=loc;aim(scene.camera,(0,0,.5));scene.render.filepath=str(HERE/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True)

if __name__ == '__main__': main()
