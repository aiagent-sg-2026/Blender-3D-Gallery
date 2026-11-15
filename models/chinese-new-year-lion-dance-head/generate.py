"""Create an original stylized southern Chinese lion dance head in Blender 5.1."""
import bpy
import math
from mathutils import Vector
from pathlib import Path

BASE=Path(__file__).resolve().parent
for directory in ('sources','exports','previews'):
    (BASE/directory).mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)


def material(name,color,metallic=0,roughness=.4):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    shader=m.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value=(*color,1)
    shader.inputs['Metallic'].default_value=metallic;shader.inputs['Roughness'].default_value=roughness
    return m

red=material('Vermilion lacquer',(.62,.018,.025),.18,.29)
darkred=material('Deep red fabric',(.32,.008,.014),.03,.53)
gold=material('Gold ornament',(.88,.48,.045),.64,.24)
cream=material('Ivory fur and teeth',(.92,.82,.62),.02,.68)
white=material('Warm white eyes',(.96,.93,.82),.04,.3)
black=material('Black lacquer',(.012,.014,.018),.18,.28)
turquoise=material('Jade painted detail',(.018,.31,.25),.20,.31)
root=bpy.data.objects.new('ASSET_ChineseNewYearLionDanceHead',None);bpy.context.collection.objects.link(root)


def attach(obj,name,mat):
    obj.name=name;obj.parent=root;obj.data.materials.append(mat);return obj


def ellipsoid(name,position,scale,mat,segments=24,rings=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,location=position)
    obj=attach(bpy.context.object,name,mat);obj.scale=scale
    for poly in obj.data.polygons:poly.use_smooth=True
    return obj


def torus(name,position,major,minor,mat,scale=(1,1,1)):
    bpy.ops.mesh.primitive_torus_add(major_segments=48,minor_segments=8,major_radius=major,minor_radius=minor,location=position,rotation=(math.pi/2,0,0))
    obj=attach(bpy.context.object,name,mat);obj.scale=scale
    return obj


def path(name,points,radius,mat):
    curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.resolution_u=2;curve.bevel_depth=radius;curve.bevel_resolution=3
    spline=curve.splines.new('POLY');spline.points.add(len(points)-1)
    for point,co in zip(spline.points,points):point.co=(*co,1)
    obj=bpy.data.objects.new(name,curve);bpy.context.collection.objects.link(obj);attach(obj,name,mat)
    return obj


def box(name,position,dimensions,mat,bevel=.01):
    bpy.ops.mesh.primitive_cube_add(size=1,location=position);obj=attach(bpy.context.object,name,mat);obj.dimensions=dimensions
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        modifier=obj.modifiers.new('Soft edge','BEVEL');modifier.width=bevel;modifier.segments=2
        obj.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return obj


def tuft(name,start,end,radius,mat):
    midpoint=(Vector(start)+Vector(end))/2;direction=Vector(end)-Vector(start)
    obj=ellipsoid(name,midpoint,(radius,radius,direction.length*.55),mat,16,8)
    obj.rotation_euler=direction.to_track_quat('Z','Y').to_euler()
    return obj

# The shell, ear panels and flowing rear skirt establish a full 3D silhouette.
ellipsoid('Red lacquer head shell',(0,.02,1.03),(.70,.43,.63),red,48,24)
ellipsoid('Rear draped fabric',(0,.29,.68),(.64,.34,.35),darkred,32,16)
for side in (-1,1):
    x=side*.66
    ellipsoid('Ear base '+str(side),(x,-.06,1.48),(.24,.12,.24),red)
    ellipsoid('Ear inner '+str(side),(x,-.18,1.48),(.16,.035,.16),gold)
    ellipsoid('Ear center '+str(side),(x,-.22,1.48),(.09,.025,.09),turquoise)
    # Each eye has raised painted rings, protruding eyeball and pupil.
    ex=side*.37
    ellipsoid('Eye rim '+str(side),(ex,-.38,1.25),(.255,.14,.25),gold)
    ellipsoid('White eyeball '+str(side),(ex,-.51,1.25),(.204,.095,.20),white)
    torus('Eye dark outline '+str(side),(ex,-.58,1.25),.177,.018,black)
    torus('Eye jade ring '+str(side),(ex,-.599,1.25),.125,.014,turquoise)
    ellipsoid('Pupil '+str(side),(ex,-.61,1.25),(.09,.04,.09),black)
    ellipsoid('Eye highlight '+str(side),(ex-side*.023,-.65,1.28),(.024,.012,.024),white,16,8)
    points=[]
    for i in range(19):
        a=math.pi*i/18
        points.append((ex+.235*math.cos(a),-.49,1.31+.16*math.sin(a)))
    path('Curved ivory eyebrow '+str(side),points,.037,cream)
    # Sculptural fur locks surround the outside edge rather than using images.
    for i in range(11):
        a=-.20+i*(math.pi*.77)/10
        px=side*(.63+.11*math.sin(a));pz=.73+i*.084
        tuft('Side mane %s %02d'%(side,i),(px,-.10,pz),(px+side*.13,-.13,pz+.025),.065,cream)
# Curved forehead ornaments, horn and a round mirror-like disc.
for side in (-1,1):
    path('Gold forehead swirl '+str(side),[(side*(.07+.29*i/24),-.39,1.54+.09*math.sin(math.pi*i/24)) for i in range(25)],.018,gold)
    for i in range(4):
        x=side*(.13+.11*i)
        ellipsoid('Forehead bead %s %d'%(side,i),(x,-.43,1.50+(.045 if i<2 else 0)),(.035,.025,.035),gold,16,8)
ellipsoid('Forehead ornament',(0,-.40,1.55),(.13,.06,.13),gold)
ellipsoid('Forehead mirror',(0,-.46,1.55),(.08,.025,.08),white)
ellipsoid('Crown horn',(0,-.02,1.72),(.12,.10,.19),gold)
ellipsoid('Horn red tip',(0,-.035,1.88),(.065,.06,.07),red)
# Dark mouth cavity is surrounded by a red and gold lower jaw, with separate teeth.
ellipsoid('Open mouth cavity',(0,-.41,.75),(.48,.12,.23),black,32,16)
points=[(.49*math.cos(math.pi+i*math.pi/32),-.48,.77+.23*math.sin(math.pi+i*math.pi/32)) for i in range(33)]
path('Red lower jaw',points,.07,red)
path('Gold lower jaw trim',[(x,y-.065,z) for x,y,z in points],.015,gold)
for i in range(7):
    x=(i-3)*.105
    tooth=box('Ivory tooth %d'%i,(x,-.535,.697),(.075,.035,.065),white,.012)
    tooth.rotation_euler[1]=-.09*(i-3)
# Broad muzzle, red nose, nostrils and cheeks.
ellipsoid('Upper muzzle',(0,-.51,.91),(.43,.18,.18),red,32,16)
ellipsoid('Round red nose',(0,-.68,1.00),(.14,.12,.105),red)
for side in (-1,1):
    ellipsoid('Nostril '+str(side),(side*.09,-.677,1.03),(.035,.023,.025),black,16,8)
    ellipsoid('Cheek scroll '+str(side),(side*.36,-.50,.89),(.13,.075,.13),gold)
    ellipsoid('Cheek red center '+str(side),(side*.36,-.565,.89),(.065,.03,.065),red)
    # Whiskers sweep from the cheeks across the sides.
    for j in range(3):
        path('Whisker %s %d'%(side,j),[(side*(.37+.34*i/16),-.57+.06*i/16,.92+j*.035+.065*math.sin(math.pi*i/16)) for i in range(17)],.009,cream)
# The long cream beard hangs under the jaw with visible gaps between locks.
for i in range(13):
    x=(i-6)*.055;length=.27+.12*(1-abs(i-6)/6)
    tuft('Beard lock %02d'%i,(x,-.44,.56),(x*1.18,-.48,.56-length),.029,cream)
for i in range(9):
    x=(i-4)*.13
    tuft('Crown fur %02d'%i,(x,-.035,1.55),(x*1.1,-.03,1.70-abs(i-4)*.025),.045,cream)

# Save separate artist-editable objects before batching materials for runtime.
bpy.ops.object.select_all(action='DESELECT')
for obj in [root]+list(root.children_recursive):obj.select_set(True)
bpy.context.view_layer.objects.active=root
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'sources/chinese-new-year-lion-dance-head.blend'))
bpy.ops.object.select_all(action='DESELECT')
for obj in root.children_recursive:
    if obj.type in {'MESH','CURVE'}:obj.select_set(True)
bpy.context.view_layer.objects.active=next(obj for obj in root.children_recursive if obj.type=='MESH')
bpy.ops.object.convert(target='MESH')
for surface in (red,darkred,gold,cream,white,black,turquoise):
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
bpy.ops.export_scene.gltf(filepath=str(BASE/'exports/chinese-new-year-lion-dance-head.glb'),export_format='GLB',use_selection=True,export_apply=True)
print('F04_EXPORT_COMPLETE')
