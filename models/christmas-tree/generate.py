import bpy, math, random, os
from mathutils import Vector
from pathlib import Path

BASE = Path(__file__).resolve().parent
random.seed(41)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for p in ('sources','exports','previews'):
    (BASE / p).mkdir(parents=True, exist_ok=True)

def mat(name, color, metal=0, rough=.45, emission=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Metallic'].default_value=metal; bs.inputs['Roughness'].default_value=rough
    if emission: bs.inputs['Emission Color'].default_value=(*color,1); bs.inputs['Emission Strength'].default_value=emission
    return m
pine=[mat('Pine forest',(.018,.13,.063)),mat('Pine emerald',(.025,.20,.085)),mat('Pine tips',(.045,.27,.12))]
gold=mat('Warm polished gold',(.86,.49,.08),.68,.24); red=mat('Cranberry red',(.54,.018,.025),.35,.22); ivory=mat('Warm ivory',(.90,.76,.52),.20,.32); trunk=mat('Tree trunk',(.17,.065,.025)); skirt=mat('Tree skirt cranberry fabric',(.38,.012,.02),.05,.65); bulb=mat('Warm fairy lights',(1,.56,.12),.1,.3,1.8)
root=bpy.data.objects.new('ASSET_ChristmasTree',None); bpy.context.collection.objects.link(root)
def add(obj, name, material):
    obj.name=name; obj.data.materials.append(material); obj.parent=root; return obj

def cone(name, loc, r1,r2,depth,material,vertices=32):
    bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=r1,radius2=r2,depth=depth,location=loc);return add(bpy.context.object,name,material)
def sphere(name, loc, radius, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=radius,location=loc);o=add(bpy.context.object,name,material)
    for p in o.data.polygons:p.use_smooth=True
    return o

def foliage(layer,z,rad,height,material):
    n=40; verts=[]
    # Undulating pointed lower rim and several tapered rings create branch-like layers.
    for j,(fraction,rf) in enumerate([(0,1),(.10,.83),(.45,.59),(1,.045)]):
        for i in range(n):
            a=2*math.pi*i/n; ripple=(1.0 if i%2==0 else .86) if j==0 else (1+.035*math.sin(i*3+layer))
            rr=rad*rf*ripple; zz=z+height*fraction+(.025*math.cos(a*5+layer) if j==0 else 0)
            verts.append((rr*math.cos(a),rr*math.sin(a),zz))
    faces=[]
    faces.append(tuple(reversed(range(n))))
    for j in range(3):
        for i in range(n):a=j*n+i;b=j*n+(i+1)%n;faces.append((a,b,b+n,a+n))
    faces.append(tuple(range(3*n,4*n)))
    mesh=bpy.data.meshes.new('Foliage layer mesh');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new('Foliage tier %02d'%layer,mesh);bpy.context.collection.objects.link(o);add(o,o.name,material)

def star():
    points=[]
    for i in range(10):
        a=math.pi/2+2*math.pi*i/10; r=.21 if i%2==0 else .092; points.append((r*math.cos(a),r*math.sin(a)))
    verts=[(x,y,z+2.81) for y in (-.042,.042) for x,z in points];faces=[tuple(range(9,-1,-1)),tuple(range(10,20))]
    faces += [(i,(i+1)%10,(i+1)%10+10,i+10) for i in range(10)]
    mesh=bpy.data.meshes.new('Five point star mesh');mesh.from_pydata(verts,[],faces);mesh.update();obj=bpy.data.objects.new('Gold five point star',mesh);bpy.context.collection.objects.link(obj);add(obj,obj.name,gold)
    mod=obj.modifiers.new('Soft edge','BEVEL');mod.width=.008;mod.segments=2;obj.modifiers.new('Weighted normals','WEIGHTED_NORMAL')

def cable(name,points,material,radius):
    curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.resolution_u=1;curve.bevel_depth=radius;curve.bevel_resolution=2
    spl=curve.splines.new('POLY');spl.points.add(len(points)-1)
    for p,co in zip(spl.points,points):p.co=(*co,1)
    ob=bpy.data.objects.new(name,curve);bpy.context.collection.objects.link(ob);add(ob,name,material)
    return ob

# Base is low and broad so the complete tree has a stable ground reference.
cone('Skirt scalloped base',(0,0,.055),.68,.18,.11,skirt,48)
cone('Trunk',(0,0,.27),.10,.095,.42,trunk)
for k in range(7):
    z=.35+k*.29; rad=.78-k*.09; foliage(k,z,rad,.56,pine[k%3])
# Spiral garland follows the outside of the tiers. Shape uses the same taper as the foliage.
points=[]
for i in range(330):
    t=i/329; z=.46+t*1.88; angle=t*2*math.pi*5.2; k=min(6,max(0,int((z-.35)/.29))); local=(z-(.35+k*.29))/.56
    r=(.78-k*.09)*(1-.62*local)+.022;points.append((r*math.cos(angle),r*math.sin(angle),z))
cable('Gold garland',points,gold,.012)
for i in range(72):
    t=(i+.4)/72;z=.44+t*1.87; ang=i*2.399963; k=min(6,max(0,int((z-.35)/.29)));local=(z-(.35+k*.29))/.56
    r=(.78-k*.09)*(1-.60*local)+.025
    sphere('Bauble %02d'%i,(r*math.cos(ang),r*math.sin(ang),z),.048 if k<4 else .037,[red,gold,ivory][i%3])
for i in range(0,len(points),7):sphere('Fairy light %03d'%i,points[i],.018,bulb)
star()
# Export only the asset hierarchy; Blender cameras/lights are preview-only.
bpy.ops.object.select_all(action='DESELECT')
for ob in [root]+list(root.children_recursive):ob.select_set(True)
bpy.context.view_layer.objects.active=root
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'sources/christmas-tree.blend'))
# Keep the saved source editable, but batch ornaments by material in the export
# to avoid a separate browser draw call for every sphere.
for material in (red, gold, ivory, bulb):
    group=[o for o in root.children if o.type == 'MESH' and (o.name.startswith('Bauble ') or o.name.startswith('Fairy light ')) and o.data.materials[0] == material]
    if len(group) > 1:
        bpy.ops.object.select_all(action='DESELECT')
        for ob in group: ob.select_set(True)
        bpy.context.view_layer.objects.active=group[0]
        bpy.ops.object.join()
bpy.ops.object.select_all(action='DESELECT')
for ob in [root]+list(root.children_recursive): ob.select_set(True)
bpy.context.view_layer.objects.active=root
bpy.ops.export_scene.gltf(filepath=str(BASE/'exports/christmas-tree.glb'),export_format='GLB',use_selection=True,export_apply=True)
print('F01_EXPORT_COMPLETE')
