"""Create an original stylized Chinese New Year kumquat tree (Blender 5.1)."""
import bpy
import math
import random
from mathutils import Vector
from pathlib import Path

BASE=Path(__file__).resolve().parent
for directory in ('sources','exports','previews'):
    (BASE/directory).mkdir(parents=True,exist_ok=True)
random.seed(509)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)


def material(name,color,metallic=0,roughness=.4):
    result=bpy.data.materials.new(name);result.diffuse_color=(*color,1);result.use_nodes=True
    shader=result.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value=(*color,1)
    shader.inputs['Metallic'].default_value=metallic;shader.inputs['Roughness'].default_value=roughness
    return result

porcelain=material('Ivory glazed porcelain',(.88,.85,.72),.12,.22)
cobalt=material('Cobalt blue glaze',(.018,.08,.28),.18,.24)
gold=material('Warm metallic gold',(.86,.46,.045),.62,.25)
red=material('Vermilion red packet',(.67,.014,.022),.14,.33)
wood=material('Warm brown branches',(.16,.065,.022),.02,.73)
soil=material('Dark potting soil',(.045,.028,.014),0,.94)
leafdark=material('Deep evergreen leaves',(.018,.13,.035),.04,.48)
leafmid=material('Jade green leaves',(.035,.25,.065),.04,.43)
leaflight=material('Fresh green leaves',(.08,.34,.09),.04,.43)
orange=material('Kumquat orange',(.98,.25,.01),.10,.3)
root=bpy.data.objects.new('ASSET_ChineseNewYearKumquatTree',None);bpy.context.collection.objects.link(root)


def attach(obj,name,mat):
    obj.name=name;obj.parent=root;obj.data.materials.append(mat);return obj


def ellipsoid(name,position,scale,mat,segments=16,rings=8):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,location=position)
    obj=attach(bpy.context.object,name,mat);obj.scale=scale
    for poly in obj.data.polygons:poly.use_smooth=True
    return obj


def rod(name,start,end,r1,r2,mat,vertices=12):
    start,end=Vector(start),Vector(end);delta=end-start
    bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=r1,radius2=r2,depth=delta.length,location=(start+end)/2)
    obj=attach(bpy.context.object,name,mat);obj.rotation_euler=delta.to_track_quat('Z','Y').to_euler()
    return obj


def box(name,location,dimensions,mat,bevel=.005):
    bpy.ops.mesh.primitive_cube_add(size=1,location=location);obj=attach(bpy.context.object,name,mat);obj.dimensions=dimensions
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        b=obj.modifiers.new('Soft edges','BEVEL');b.width=bevel;b.segments=2
        obj.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return obj


def lathe(name,profile,mat):
    n=64;verts=[]
    for radius,z in profile:
        for i in range(n):
            a=math.tau*i/n;verts.append((radius*math.cos(a),radius*math.sin(a),z))
    faces=[]
    for row in range(len(profile)-1):
        for i in range(n):
            a=row*n+i;b=row*n+(i+1)%n;faces.append((a,b,b+n,a+n))
    # Leave the top open so the separate soil and trunk remain visible.
    faces.append(tuple(reversed(range(n))))
    mesh=bpy.data.meshes.new(name+' mesh');mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);attach(obj,name,mat)
    for poly in mesh.polygons:poly.use_smooth=True
    bevel=obj.modifiers.new('Ceramic edge','BEVEL');bevel.width=.006;bevel.segments=2
    obj.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return obj


def ring(name,r,z,tube,mat):
    bpy.ops.mesh.primitive_torus_add(major_segments=64,minor_segments=8,major_radius=r,minor_radius=tube,location=(0,0,z))
    return attach(bpy.context.object,name,mat)

# Ceramic pot with painted blue and gold bands and visible dark soil.
lathe('Porcelain flower pot',[(.21,.035),(.26,.07),(.31,.19),(.33,.31),(.30,.40),(.305,.44),(.27,.44)],porcelain)
ring('Lower blue ceramic band',.275,.11,.009,cobalt)
ring('Upper blue ceramic band',.303,.397,.012,cobalt)
ring('Gold rim',.295,.438,.009,gold)
ring('Gold foot line',.242,.061,.006,gold)
bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.268,depth=.012,location=(0,0,.43))
attach(bpy.context.object,'Potting soil',soil)
# Ornamental red diamond has no text or copied cultural motif.
diamond=box('Pot red diamond',(0,-.316,.255),(.12,.012,.12),red,.006);diamond.rotation_euler[1]=math.pi/4
inner=box('Pot gold diamond',(0,-.325,.255),(.06,.012,.06),gold,.004);inner.rotation_euler[1]=math.pi/4
# Rising woody trunk with independent, naturally fanning branch assemblies.
rod('Main trunk',(0,0,.435),(.025,0,1.20),.07,.038,wood,18)
ends=[]
for b in range(12):
    angle=b*math.tau/12+.18
    start=(.01,0,.85+(b%4)*.07)
    middle=(.25*math.cos(angle),.20*math.sin(angle),1.22+(b%3)*.11)
    end=(.48*math.cos(angle),.38*math.sin(angle),1.35+(b%4)*.12)
    rod('Main branch %02d'%b,start,middle,.033,.020,wood)
    rod('Outer branch %02d'%b,middle,end,.020,.009,wood)
    for j in range(3):
        a=angle+(j-1)*.29
        tip=(end[0]+.10*math.cos(a),end[1]+.09*math.sin(a),end[2]+(j-1)*.15)
        rod('Twig %02d %d'%(b,j),end,tip,.009,.004,wood,8)
        ends.append((tip,a,b,j))
        for k in range(4):
            phi=a+(k-1.5)*.58
            direction=Vector((.70*math.cos(phi),.70*math.sin(phi),(-.2+.25*k))).normalized()
            location=Vector(tip)+direction*(.048+.028*(k%2))
            leaf=ellipsoid('Leaf %02d %d %d'%(b,j,k),location,(.038,.024,.125),[leafdark,leafmid,leaflight][(b+j+k)%3],12,8)
            leaf.rotation_euler=direction.to_track_quat('Z','Y').to_euler()
# Extra central leaves fill the crown while leaving branches and fruit visible.
for k in range(80):
    a=k*2.399963;z=1.08+(k%9)*.10;r=.16+.05*(k%5)
    direction=Vector((math.cos(a),math.sin(a),.22+(k%3)*.18)).normalized()
    leaf=ellipsoid('Inner leaf %02d'%k,(r*math.cos(a),r*math.sin(a),z),(.039,.024,.12),[leafmid,leaflight,leafdark][k%3],12,8)
    leaf.rotation_euler=direction.to_track_quat('Z','Y').to_euler()
# Oval fruit is integrated around the crown; stems remain individually editable.
for i in range(36):
    z=1.06+(i%7)*.13;fraction=(z-1.45)/.58;scale=max(.25,1-fraction*fraction)**.5
    a=i*2.399963;rad=.47*scale
    x=rad*math.cos(a);y=.80*rad*math.sin(a)
    rod('Fruit stem %02d'%i,(x,y,z+.055),(x*.93,y*.93,z+.095),.007,.004,wood,8)
    ellipsoid('Kumquat %02d'%i,(x,y,z),(.052,.05,.068),orange,16,8)
# Distinct hanging red packets with gold string and diamond decoration.
for i,(x,y,z) in enumerate([(-.38,-.36,1.20),(-.11,-.44,1.34),(.22,-.42,1.40),(.43,-.27,1.18),(.06,-.32,1.75),(-.35,.22,1.52),(.30,.28,1.65)]):
    rod('Packet string %02d'%i,(x,y,z+.14),(x,y,z+.055),.003,.003,gold,8)
    box('Red packet %02d'%i,(x,y,z-.005),(.105,.018,.15),red,.006)
    detail=box('Packet gold diamond %02d'%i,(x,y-.011,z),(.038,.006,.038),gold,.002);detail.rotation_euler[1]=math.pi/4
    ellipsoid('Packet gold bead %02d'%i,(x,y,z-.09),(.012,.012,.012),gold,12,6)

# Source remains artist-editable. Merge evaluated export meshes by material.
bpy.ops.object.select_all(action='DESELECT')
for obj in [root]+list(root.children_recursive):obj.select_set(True)
bpy.context.view_layer.objects.active=root
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'sources/chinese-new-year-kumquat-tree.blend'))
bpy.ops.object.select_all(action='DESELECT')
for obj in root.children_recursive:
    if obj.type=='MESH':obj.select_set(True)
bpy.context.view_layer.objects.active=next(obj for obj in root.children_recursive if obj.type=='MESH')
bpy.ops.object.convert(target='MESH')
for surface in (porcelain,cobalt,gold,red,wood,soil,leafdark,leafmid,leaflight,orange):
    group=[obj for obj in root.children_recursive if obj.type=='MESH' and obj.data.materials and obj.data.materials[0]==surface]
    if not group:continue
    bpy.ops.object.select_all(action='DESELECT')
    for obj in group:obj.select_set(True)
    bpy.context.view_layer.objects.active=group[0]
    if len(group)>1:bpy.ops.object.join()
    bpy.context.view_layer.objects.active.name='Export batch '+surface.name
bpy.ops.object.select_all(action='DESELECT')
for obj in [root]+list(root.children_recursive):obj.select_set(True)
bpy.context.view_layer.objects.active=root
bpy.ops.export_scene.gltf(filepath=str(BASE/'exports/chinese-new-year-kumquat-tree.glb'),export_format='GLB',use_selection=True,export_apply=True)
print('F05_EXPORT_COMPLETE')
