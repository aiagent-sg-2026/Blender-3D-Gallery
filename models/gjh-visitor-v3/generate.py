"""Original GJH mall visitor v3: a new, taller character. Blender-only deterministic authoring."""
from pathlib import Path
import math
import bpy
import bmesh
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1

def mat(name,rgb,rough=.65,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True
 def lin(v):
  v=v/255;return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
 color=(*map(lin,rgb),1);m.diffuse_color=color
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=color;p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 return m
skin=mat('Warm peach skin',(226,172,130));hair=mat('Black wavy hair',(30,27,30),.55);brow=mat('Brow',(26,24,26))
eye=mat('Eye dark',(30,22,20),.35);white=mat('Cream white',(240,238,230));smile=mat('Smile',(160,72,64))
hoodie=mat('Navy hoodie',(34,42,82),.85);tape=mat('Hoodie tape',(58,68,118),.7);tee=mat('White tee',(240,240,238),.8)
chino=mat('Khaki chino',(184,160,118),.85);sole=mat('Sneaker sole',(236,236,230));upper=mat('Sneaker upper',(246,246,242))
pack=mat('Backpack black',(28,30,32),.8);packtrim=mat('Backpack trim',(60,64,68),.7);watchm=mat('Watch steel',(150,154,160),.35,.6)
lanyard=mat('Lanyard blue',(30,90,200),.6);card=mat('Badge card',(238,240,244),.5)

def node(name,loc,parent=None):
 o=bpy.data.objects.new(name,None);scene.collection.objects.link(o);o.location=loc;o.parent=parent;return o
root=node('GJHVisitorV3',(0,0,0));body=node('Body',(0,0,.94),root)
def mesh(name,verts,faces,material,parent):
 d=bpy.data.meshes.new(name);d.from_pydata(verts,[],faces);d.update();o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.parent=parent;d.materials.append(material)
 for p in d.polygons:p.use_smooth=len(p.vertices)<=4
 return o
def ell(name,loc,scale,material,parent,seg=16,rings=10):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,location=(0,0,0));o=bpy.context.object;o.name=name;o.parent=parent;o.location=loc;o.scale=scale;o.data.materials.append(material)
 for p in o.data.polygons:p.use_smooth=True
 return o
def loft(name,rows,material,parent,n=20):
 # Rows are height, halfwidth, halfdepth, centreY. Closed smooth contour.
 v=[];f=[]
 for z,w,d,y in rows:
  for i in range(n):
   a=2*math.pi*i/n;v.append((w*math.cos(a),y+d*math.sin(a),z))
 for j in range(len(rows)-1):
  for i in range(n):a=j*n+i;b=j*n+(i+1)%n;f.append((a,b,b+n,a+n))
 f.extend([tuple(reversed(range(n))),tuple((len(rows)-1)*n+i for i in range(n))]);return mesh(name,v,f,material,parent)
def shell(name,rows,material,parent,a0,a1,n=24):
 v=[];f=[]
 for z,w,d,y in rows:
  for i in range(n+1):
   a=a0+(a1-a0)*i/n;v.append((w*math.cos(a),y+d*math.sin(a),z))
 for j in range(len(rows)-1):
  for i in range(n):a=j*(n+1)+i;f.append((a,a+1,a+n+2,a+n+1))
 return mesh(name,v,f,material,parent)
def box(name,c,sz,material,parent):
 x,y,z=c;a,b,d=[t/2 for t in sz]
 v=[(x+sx*a,y+sy*b,z+sz_*d) for sz_ in(-1,1) for sy in(-1,1) for sx in(-1,1)]
 f=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)];return mesh(name,v,f,material,parent)
def path(name,points,radius,material,parent,sides=6):
 v=[];f=[]
 for j,p in enumerate(points):
  p=Vector(p);direction=Vector(points[min(j+1,len(points)-1)])-Vector(points[max(0,j-1)])
  a=direction.normalized().cross(Vector((0,0,1)))
  if a.length<.01:a=Vector((1,0,0))
  a.normalize();b=direction.normalized().cross(a)
  for i in range(sides):v.append(p+radius*(math.cos(i*math.tau/sides)*a+math.sin(i*math.tau/sides)*b))
 for j in range(len(points)-1):
  for i in range(sides):a=j*sides+i;b=j*sides+(i+1)%sides;f.append((a,b,b+sides,a+sides))
 f.extend([tuple(reversed(range(sides))),tuple((len(points)-1)*sides+i for i in range(sides))]);return mesh(name,v,f,material,parent)
def ring(name,z,w,d,radius,material,parent,n=28):
 return path(name,[(w*math.cos(i*math.tau/n),d*math.sin(i*math.tau/n),z) for i in range(n+1)],radius,material,parent,6)

# Semi-realistic adult proportions (about six heads), A-pose reference per the v3 character sheet.
rows=[(0,.165,.095,0),(.2,.175,.10,0),(.4,.185,.098,0),(.5,.17,.09,0),(.57,.09,.065,0),(.59,.07,.055,0)]
loft('Tee torso',[(-.01,.15,.088,0),(.0,.155,.09,0),(.2,.16,.092,0),(.4,.168,.09,0),(.5,.155,.082,0),(.57,.085,.062,0),(.6,.062,.052,0)],tee,body,24)
ring('Tee crew neckline',.592,.056,.05,.008,tee,body,20)
loft('Chino pelvis',[(-.06,.12,.08,.004),(-.02,.165,.092,.004),(.02,.164,.092,.004)],chino,body,24)
# Open-front zip hoodie: shell leaves a front gap showing the tee.
gap=.3
shell('Hoodie shell',rows,hoodie,body,-math.pi/2+gap,3*math.pi/2-gap,28)
for side in(-1,1):
 path('Hoodie zip tape',[(side*w*math.sin(gap),-d*math.cos(gap),z) for z,w,d,y in rows],.007,tape,body,6)
 path('Hoodie drawstring',[(side*.04,-.088,.56),(side*.043,-.094,.47)],.0035,white,body,5)
ell('Hoodie hood',(0,.07,.585),(.105,.075,.065),hoodie,body,16,10)
loft('Visible neck',[(.5,.055,.052,0),(.68,.05,.048,0)],skin,body,16)
# Lanyard and ID card (separate removable accessory).
for side in(-1,1):
 path('Lanyard strap',[(side*.012,-.097,.345),(side*.045,-.09,.5),(side*.058,-.04,.585),(side*.05,.03,.6),(0,.052,.605)],.0065,lanyard,body,6)
box('ID badge card',(0,-.099,.30),(.048,.006,.068),card,body)
box('ID badge header',(0,-.1,.325),(.048,.0065,.016),lanyard,body)
# Black daypack with straps.
ell('Backpack shell',(0,.150,.22),(.16,.075,.22),pack,body,20,12)
ell('Backpack front pocket',(0,.218,.13),(.13,.018,.09),packtrim,body,16,10)
for side in(-1,1):
 path('Backpack shoulder strap',[(side*.11,.10,.50),(side*.125,.0,.575),(side*.125,-.078,.47),(side*.115,-.08,.30),(side*.10,-.02,.12)],.013,pack,body,8)

head=node('Head',(0,0,.62),body)
loft('Oval face',[(0,.035,.045,0),(.03,.075,.075,0),(.08,.1,.095,0),(.14,.108,.1,0),(.2,.106,.098,0),(.245,.085,.085,0),(.27,.04,.04,0),(.28,.01,.01,0)],skin,head,24)
for side in(-1,1):
 ell('Small ear',(side*.112,0,.125),(.016,.014,.03),skin,head,12,8)
 ell('Expressive eye',(side*.043,-.087,.152),(.014,.011,.012),eye,head,16,10)
 ell('Eye highlight',(side*.039,-.1,.16),(.004,.0015,.005),white,head,8,6)
 path('Straight brow',[(side*.022,-.092,.196),(side*.045,-.096,.202),(side*.07,-.092,.196)],.0048,brow,head,6)
ell('Small nose',(0,-.098,.108),(.014,.015,.02),skin,head,12,8)
path('Soft smile',[(-.028,-.087,.066),(0,-.093,.056),(.028,-.087,.066)],.0035,smile,head,6)
# Wavy espresso hair with a swept quiff; the cap sits behind the hairline so brows stay visible.
loft('Hair cap',[(.1,.096,.1,.035),(.16,.114,.118,.026),(.21,.12,.116,.022),(.255,.105,.1,.02),(.29,.06,.065,.015),(.305,.01,.012,.01)],hair,head,24)
ell('Hair quiff sweep',(.01,-.07,.285),(.1,.065,.04),hair,head,20,10).rotation_euler.y=-.2
f1=ell('Hair fringe lock',(-.04,-.085,.245),(.075,.03,.03),hair,head,16,8);f1.rotation_euler.y=.3
ell('Hair side fringe',(.075,-.08,.235),(.04,.03,.04),hair,head,14,8)
ell('Hair back wave',(0,.085,.12),(.1,.05,.08),hair,head,16,10)
# Alternate cropped hair is a separate component for runtime selection.
ell('Alternate hair cap',(0,.035,.2),(.118,.118,.11),hair,head,20,10)
ell('Alternate hair fringe',(0,-.087,.255),(.09,.03,.025),hair,head,16,8)

limbs={}
for side,label in[(-1,'Left'),(1,'Right')]:
 arm=node(label+'Shoulder',(side*.185,0,.50),body);arm.rotation_euler.y=-side*.45
 loft(label+' Tee sleeve',[(.06,.03,.03,0),(.04,.047,.047,0),(-.02,.052,.052,0),(-.12,.05,.05,0)],tee,arm,16)
 loft(label+' Hoodie Sleeve',[(.07,.03,.03,0),(.05,.05,.05,0),(0,.058,.058,0),(-.15,.052,.052,0),(-.28,.047,.047,0),(-.4,.043,.043,0),(-.5,.04,.04,0)],hoodie,arm,16)
 loft(label+' Arm skin',[(-.40,.036,.036,0),(-.46,.031,.031,0),(-.54,.029,.029,0)],skin,arm,16)
 elbow=node(label+'Elbow',(0,0,-.28),arm)
 ell(label+' Palm',(0,-.004,-.295),(.036,.026,.038),skin,elbow,12,8)
 ell(label+'Thumb',(-side*.034,-.012,-.27),(.012,.016,.028),skin,elbow,10,6)
 for finger in range(4):
  x=(finger-1.5)*.017
  ell(label+' Finger '+str(finger),(x,-.006,-.355-abs(finger-1.5)*.004),(.0085,.012,.036-abs(finger-1.5)*.004),skin,elbow,10,8)
 if label=='Left':
  loft('Smartwatch band',[(-.215,.039,.039,0),(-.25,.039,.039,0)],watchm,elbow,12)
  ell('Smartwatch face',(0,-.04,-.232),(.026,.01,.022),watchm,elbow,12,6)
 hip=node(label+'Hip',(side*.085,0,-.02),body)
 loft(label+' Chino Trousers',[(.07,.09,.10,0),(-.05,.093,.10,0),(-.2,.082,.09,0),(-.43,.066,.074,0),(-.6,.062,.07,0),(-.84,.056,.062,0)],chino,hip,20)
 knee=node(label+'Knee',(0,0,-.43),hip)
 foot=node(label+'Foot',(0,-.02,-.42),knee)
 ell(label+' Sneaker sole',(0,-.04,-.045),(.064,.14,.03),sole,foot,16,8)
 ell(label+' Sneaker upper',(0,-.04,-.005),(.06,.13,.05),upper,foot,16,8)
 ell(label+' Sneaker tongue',(0,-.015,.035),(.034,.06,.022),upper,foot,12,6)
 for j in range(3):path(label+' Sneaker lace',[(-.034,-.06-j*.022,.05),(.034,-.06-j*.022,.05)],.0028,white,foot,5)
 limbs[label]=(arm,elbow,hip,knee,foot)

for o in scene.objects:
 if o.type=='MESH':
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
# Normalize measured rest geometry to exactly 1.78 m with a floor-centred root.
bpy.context.view_layer.update()
points=[o.matrix_world@v.co for o in scene.objects if o.type=='MESH' for v in o.data.vertices]
low=min(p.z for p in points);high=max(p.z for p in points);factor=1.78/(high-low)
body.location.z-=low;root.scale=(factor,factor,factor)
import sys
sys.path.insert(0,str(ROOT))
from rig import build_rig
from animations import build_animations
from export import render_and_export
rig=build_rig(scene,root,body,head,limbs)
build_animations(scene,rig,[o for o in scene.objects if o.type=='MESH' and 'sneaker' in o.name.lower()])
render_and_export(scene,rig,ROOT,mat)
