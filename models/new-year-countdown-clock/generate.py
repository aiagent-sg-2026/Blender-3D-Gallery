"""Create a year-independent New Year clock display in Blender 5.1."""
import bpy
import math
from mathutils import Vector
from pathlib import Path

BASE = Path(__file__).resolve().parent
for directory in ('sources', 'exports', 'previews'):
    (BASE / directory).mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)


def material(name, color, metallic=0, roughness=.4):
    result = bpy.data.materials.new(name)
    result.diffuse_color = (*color, 1)
    result.use_nodes = True
    shader = result.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Roughness'].default_value = roughness
    return result


gold = material('Polished gold', (.83, .48, .075), .75, .23)
dark_gold = material('Antique gold', (.40, .20, .035), .65, .32)
midnight = material('Midnight enamel', (.015, .035, .055), .4, .3)
ivory = material('Warm ivory clock face', (.85, .77, .60), .05, .45)
red = material('Festive ruby', (.42, .015, .025), .45, .27)
root = bpy.data.objects.new('ASSET_NewYearCountdownClock', None)
bpy.context.collection.objects.link(root)


def attach(obj, name, mat):
    obj.name = name
    obj.parent = root
    obj.data.materials.append(mat)
    return obj


def box(name, position, size, mat, bevel=.01):
    bpy.ops.mesh.primitive_cube_add(size=1, location=position)
    obj = attach(bpy.context.object, name, mat)
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        modifier = obj.modifiers.new('Soft edges', 'BEVEL')
        modifier.width = bevel
        modifier.segments = 3
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj


def cylinder(name, position, radius, depth, mat, vertices=96, front=False):
    rotation = (math.pi/2, 0, 0) if front else (0, 0, 0)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=position, rotation=rotation)
    obj = attach(bpy.context.object, name, mat)
    bevel = obj.modifiers.new('Rounded edge', 'BEVEL')
    bevel.width = .012
    bevel.segments = 3
    obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj


def ring(name, position, major, minor, mat):
    bpy.ops.mesh.primitive_torus_add(major_segments=96, minor_segments=12, location=position, rotation=(math.pi/2,0,0), major_radius=major, minor_radius=minor)
    return attach(bpy.context.object, name, mat)


def star(name, x, z, radius, y, thickness, mat):
    points=[]
    for i in range(10):
        angle = math.pi/2 + i*math.pi/5
        r = radius if i%2==0 else radius*.43
        points.append((x+r*math.cos(angle), z+r*math.sin(angle)))
    verts=[(px, yy, pz) for yy in (y-thickness/2, y+thickness/2) for px,pz in points]
    faces=[tuple(range(9,-1,-1)),tuple(range(10,20))]
    faces.extend((i,(i+1)%10,(i+1)%10+10,i+10) for i in range(10))
    mesh=bpy.data.meshes.new(name+' mesh');mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);attach(obj,name,mat)
    modifier=obj.modifiers.new('Soft star edges','BEVEL');modifier.width=.006;modifier.segments=2
    obj.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return obj


def rod(name, start, end, radius, mat):
    middle=(Vector(start)+Vector(end))/2
    direction=Vector(end)-Vector(start)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=radius, depth=direction.length, location=middle)
    obj=attach(bpy.context.object,name,mat)
    obj.rotation_euler=direction.to_track_quat('Z','Y').to_euler()
    return obj


def label(text, x, z):
    bpy.ops.object.text_add(location=(x,-.168,z),rotation=(math.pi/2,0,0))
    obj=bpy.context.object
    obj.name='Clock number '+text
    obj.data.body=text;obj.data.align_x='CENTER';obj.data.align_y='CENTER';obj.data.size=.15;obj.data.extrude=.001
    obj.data.materials.append(midnight);obj.parent=root
    bpy.context.view_layer.objects.active=obj
    bpy.ops.object.convert(target='MESH')


# A low stepped stand supports the clock and framing stars.
box('Midnight base', (0,0,.075), (2.05,.53,.15), midnight, .035)
box('Gold base trim', (0,0,.155), (1.94,.49,.035), gold, .012)
box('Raised upper base', (0,0,.205), (1.75,.39,.07), midnight, .02)
box('Central clock stand', (0,.01,.32), (.26,.20,.22), gold, .025)
center = 1.11
# Front is -Y: warm face inset in a deep gold case with concentric bezel rings.
cylinder('Clock case', (0,0,center), .72,.18, dark_gold, front=True)
cylinder('Clock face', (0,-.108,center), .645,.03, ivory, front=True)
ring('Outer gold bezel', (0,-.113,center), .682,.035,gold)
ring('Inner decorative ring', (0,-.132,center), .565,.008,dark_gold)
for i in range(12):
    a=i*math.tau/12
    marker=box('Hour marker %02d'%i, (.592*math.sin(a),-.151,center+.592*math.cos(a)), (.025,.013,.06 if i%3 else .08), gold, .003)
    marker.rotation_euler[1]=a
for text,x,z in [('12',0,center+.43),('3',.43,center),('6',0,center-.43),('9',-.43,center)]:
    label(text,x,z)
# A static 11:55 face suggests the final minutes before midnight.
def hand(name, length, width, angle, material):
    direction=Vector((math.sin(angle),0,math.cos(angle)))
    perpendicular=Vector((math.cos(angle),0,-math.sin(angle)))
    origin=Vector((0,-.185,center))
    points=[origin-direction*.075-perpendicular*width,origin+direction*length,origin-direction*.075+perpendicular*width]
    verts=[tuple(p+Vector((0,offset,0))) for offset in (-.009,.009) for p in points]
    mesh=bpy.data.meshes.new(name+' mesh');mesh.from_pydata(verts,[],[(2,1,0),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);attach(obj,name,material)
hand('Minute hand near eleven', .40,.022,-math.pi/6,midnight)
hand('Hour hand near twelve', .28,.03,-math.pi/72,red)
cylinder('Central clock pin', (0,-.21,center), .038,.035,gold,32,front=True)
# Symmetric stars and fireworks-like rays frame the dial without using a year.
for side in (-1,1):
    sx=side*.86; sz=1.40
    rod('Star support '+str(side),(side*.73,.055,.23),(sx,.055,sz-.14),.016,gold)
    star('Framing star '+str(side),sx,sz,.15,-.015,.05,gold)
    for j in range(3):
        angle=side*(.35+j*.31)
        start=(side*.79,.055,.35+j*.10)
        end=(side*(1.02+.06*j),.055,.72+j*.17)
        rod('Celebration ray %s %s'%(side,j),start,end,.008,dark_gold)
        star('Small sparkle %s %s'%(side,j),end[0],end[2],.045,-.015,.025,gold)
star('Top sparkle',0,1.95,.075,.02,.035,gold)

# Save independent editable source; batch evaluated meshes by material for GLB.
bpy.ops.object.select_all(action='DESELECT')
for obj in [root]+list(root.children_recursive): obj.select_set(True)
bpy.context.view_layer.objects.active=root
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'sources/new-year-countdown-clock.blend'))
bpy.ops.object.select_all(action='DESELECT')
for obj in root.children_recursive:
    if obj.type == 'MESH': obj.select_set(True)
bpy.context.view_layer.objects.active=next(obj for obj in root.children_recursive if obj.type=='MESH')
bpy.ops.object.convert(target='MESH')
for surface in (gold,dark_gold,midnight,ivory,red):
    group=[obj for obj in root.children_recursive if obj.type=='MESH' and obj.data.materials and obj.data.materials[0]==surface]
    if not group: continue
    bpy.ops.object.select_all(action='DESELECT')
    for obj in group: obj.select_set(True)
    bpy.context.view_layer.objects.active=group[0]
    if len(group)>1: bpy.ops.object.join()
    bpy.context.view_layer.objects.active.name='Export batch '+surface.name
bpy.ops.object.select_all(action='DESELECT')
for obj in [root]+list(root.children_recursive): obj.select_set(True)
bpy.context.view_layer.objects.active=root
bpy.ops.export_scene.gltf(filepath=str(BASE/'exports/new-year-countdown-clock.glb'),export_format='GLB',use_selection=True,export_apply=True)
print('F03_EXPORT_COMPLETE')
