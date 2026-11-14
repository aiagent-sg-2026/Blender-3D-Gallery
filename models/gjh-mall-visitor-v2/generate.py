"""Original reference-led visitor v2. Blender-only deterministic authoring; collection-local writes."""
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
skin=mat('Warm peach skin',(239,179,126));hair=mat('Swept chestnut hair',(65,43,28));dark=mat('Glasses and eyes',(27,29,25),.45);white=mat('Cream white',(239,237,217));mouth=mat('Warm smile',(164,55,35));green=mat('GJH emerald polo',(10,118,75));navy=mat('Navy denim',(32,58,78));cuff=mat('Denim cuff',(87,112,126));sole=mat('Sneaker sole',(203,209,200));watch=dark

def node(name,loc,parent=None):
 o=bpy.data.objects.new(name,None);scene.collection.objects.link(o);o.location=loc;o.parent=parent;return o
root=node('GJHMallVisitorV2',(0,0,0));body=node('Body',(0,0,.70),root)
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

# Rounded mascot proportions: broad friendly face, compact polo and short cuffed legs.
loft('Emerald polo',[(0,.19,.105,0),(.025,.205,.112,0),(.18,.20,.115,0),(.30,.17,.09,0),(.335,.085,.065,0)],green,body,20)
path('Polo lower hem',[(-.19,-.04,.012),(-.14,-.097,.012),(0,-.113,.012),(.14,-.097,.012),(.19,-.04,.012)],.004,green,body)
loft('Visible neck',[(.31,.064,.057,0),(.39,.066,.057,0)],skin,body,16)
for side in(-1,1):
 mesh('Cream pointed collar',[(side*.065,-.06,.34),(side*.105,-.075,.31),(side*.063,-.108,.265),(side*.012,-.089,.32)],[(0,1,2,3)],white,body)
path('Polo placket',[(0,-.114,.22),(0,-.10,.30)],.009,green,body)
for z in(.235,.268):ell('Cream polo button',(0,-.12,z),(.004,.002,.004),white,body,8,4)
# Original concept wordmark is converted to geometry, never an external font/image.
font=bpy.data.curves.new('GJH concept embroidery','FONT');font.body='GJH';font.size=.035;font.extrude=.0004;font.align_x='CENTER'
text=bpy.data.objects.new('GJH concept embroidery',font);scene.collection.objects.link(text);text.parent=body;text.location=(.105,-.109,.245);text.rotation_euler=(math.pi/2,0,0);font.materials.append(white)
bpy.context.view_layer.objects.active=text;text.select_set(True);bpy.ops.object.convert(target='MESH');text.select_set(False)
head=node('Head',(0,0,.35),body)
loft('Rounded face',[(0,.055,.065,-.005),(.025,.118,.101,-.007),(.065,.17,.128,0),(.125,.193,.143,.004),(.205,.197,.151,.006),(.27,.18,.145,.008),(.315,.145,.12,.012),(.345,.085,.08,.013),(.36,.015,.025,.013)],skin,head,24)
for side in(-1,1):
 ell('Rounded ear',(side*.194,.003,.15),(.036,.025,.05),skin,head,12,8)
 # Large black eyes remain clearly visible through open geometric lens rims.
 ell('Expressive black eye',(side*.080,-.143,.192),(.027,.015,.040),dark,head,16,10)
 ell('Eye highlight',(side*.073,-.157,.207),(.008,.002,.010),white,head,10,6)
 ell('Eye small highlight',(side*.088,-.157,.181),(.0035,.001,.0045),white,head,8,4)
 rim=[]
 for i in range(49):
  a=i*math.tau/48;rim.append((side*.081+.067*math.cos(a),-.16+.012*abs(math.cos(a)),.19+.069*math.sin(a)))
 path('Thin open round glasses',rim,.0045,dark,head,6)
 path('Glasses temple',[(side*.148,-.149,.20),(side*.188,-.085,.208),(side*.198,.015,.20)],.0045,dark,head,6)
 path('Friendly curved eyebrow',[(side*.035,-.133,.275),(side*.070,-.145,.286),(side*.105,-.138,.282),(side*.124,-.126,.272)],.009,hair,head,6)
path('Glasses bridge',[(-.014,-.16,.204),(0,-.169,.211),(.014,-.16,.204)],.0045,dark,head,6)
ell('Soft projecting nose',(0,-.146,.143),(.020,.024,.025),skin,head,12,8)
# Open smile, curved lower edge and small tongue; mouth geometry follows face surface.
ell('Happy smile opening',(0,-.126,.085),(.049,.009,.024),dark,head,16,8)
ell('Smile tongue',(0,-.134,.075),(.029,.003,.010),mouth,head,12,6)
path('Smile upper curve',[(-.043,-.132,.096),(0,-.137,.093),(.043,-.132,.096)],.004,skin,head,6)
# Hair extends over back of skull; asymmetrical broad locks sweep to one side.
loft('Rounded back hair',[(.16,.18,.12,.045),(.23,.205,.15,.035),(.30,.195,.16,.025),(.36,.16,.13,.02),(.40,.09,.085,.015),(.416,.008,.012,.005)],hair,head,24)
for name,loc,scale,rot in [
 ('Swept fringe left',(-.11,-.102,.315),(.128,.073,.062),-.35),
 ('Swept fringe centre',(-.045,-.106,.35),(.137,.070,.064),-.30),
 ('Parted right lock',(.12,-.095,.318),(.075,.067,.081),.35),
 ('Top lifted sweep',(-.015,-.015,.405),(.16,.075,.060),-.16),
 ('Back crown',(0,.085,.35),(.17,.085,.075),0)]:
 o=ell(name,loc,scale,hair,head,20,10);o.rotation_euler.y=rot
# Alternate cropped hairstyle is a separate skinned component for runtime selection.
ell('Alternate hair cap',(0,.025,.335),(.188,.150,.075),hair,head,20,10)
for side in (-1,1):
 ell('Alternate hair side',(side*.16,.025,.27),(.035,.115,.075),hair,head,16,8)
ell('Alternate hair fringe',(0,-.115,.295),(.14,.045,.035),hair,head,20,10)
# Articulated limbs: short polo sleeves, bare forearms, navy denim and white sneakers.
limbs={}
for side,label in[(-1,'Left'),(1,'Right')]:
 arm=node(label+'Shoulder',(side*.173,0,.27),body);arm.rotation_euler.y=-side*.18
 loft(label+'Polo sleeve',[(.065,.015,.016,0),(.05,.045,.047,0),(.02,.062,.064,0),(-.035,.067,.067,0),(-.105,.061,.061,0)],green,arm,16)
 loft(label+'Cream sleeve edging',[(-.095,.062,.062,0),(-.116,.058,.059,0)],white,arm,16)
 loft(label+'Upper arm',[(-.108,.048,.047,0),(-.21,.044,.044,0)],skin,arm,12)
 elbow=node(label+'Elbow',(0,0,-.20),arm)
 ell(label+'Elbow contour',(0,0,0),(.044,.044,.045),skin,elbow,12,8)
 loft(label+'Forearm',[(0,.044,.044,0),(-.13,.038,.038,0)],skin,elbow,12)
 ell(label+'Rounded hand',(0,-.005,-.16),(.043,.035,.060),skin,elbow,12,8)
 ell(label+'Thumb',(-side*.033,-.025,-.143),(.017,.021,.031),skin,elbow,10,6)
 if label=='Right':
  loft('Dark wristwatch band',[(-.098,.041,.042,0),(-.126,.04,.041,0)],dark,elbow,12)
  ell('Watch face',(0,-.043,-.111),(.027,.010,.024),dark,elbow,12,6)
 hip=node(label+'Hip',(side*.097,0,-.015),body)
 loft(label+'Denim thigh',[(.02,.087,.094,0),(-.12,.083,.087,0),(-.24,.072,.075,0)],navy,hip,16)
 knee=node(label+'Knee',(0,0,-.23),hip)
 ell(label+'Denim knee',(0,0,0),(.072,.075,.055),navy,knee,12,8)
 loft(label+'Straight tapered jeans',[(0,.072,.075,0),(-.15,.067,.07,0),(-.25,.063,.066,0)],navy,knee,16)
 loft(label+'Turned denim cuff',[(-.215,.067,.07,0),(-.282,.067,.07,0)],cuff,knee,16)
 foot=node(label+'Foot',(0,-.022,-.306),knee)
 ell(label+'White sneaker sole',(0,-.026,-.024),(.078,.125,.027),white,foot,16,8)
 ell(label+'White sneaker upper',(0,-.025,.008),(.074,.119,.046),white,foot,16,8)
 ell(label+'Sneaker tongue',(0,-.008,.042),(.041,.057,.022),white,foot,12,6)
 for j in range(3):path(label+'Sneaker lace',[(-.041,-.017-j*.019,.056),(.041,-.017-j*.019,.056)],.003,white,foot,5)
 limbs[label]=(arm,elbow,hip,knee,foot)
# Replace segmented limbs with continuous weighted surfaces to avoid visible joint bands.
for label in ('Left','Right'):
 arm,elbow,hip,knee,foot=limbs[label]
 for suffix in ('Upper arm','Elbow contour','Forearm','Denim thigh','Denim knee','Straight tapered jeans'):
  obj=bpy.data.objects.get(label+suffix)
  if obj:bpy.data.objects.remove(obj,do_unlink=True)
 loft(label+'Arm skin',[(-.108,.048,.047,0),(-.16,.046,.046,0),(-.20,.044,.044,0),(-.24,.043,.043,0),(-.33,.038,.038,0)],skin,arm,16)
 loft(label+'Jeans',[ (.02,.087,.094,0),(-.12,.083,.087,0),(-.19,.076,.079,0),(-.23,.072,.075,0),(-.27,.071,.074,0),(-.38,.067,.070,0),(-.48,.063,.066,0)],navy,hip,20)
# Alternate hooded top is separate from the default polo; pants remain reusable.
hoodie=mat('Hoodie slate',(108,116,120))
loft('Alternate hoodie torso',[(0,.192,.108,0),(.025,.207,.116,0),(.18,.202,.118,0),(.30,.173,.096,0),(.335,.088,.068,0)],hoodie,body,20)
ell('Alternate hoodie hood',(0,.065,.325),(.095,.055,.085),hoodie,body,16,10)
for side,label in [(-1,'Left'),(1,'Right')]:
 arm=limbs[label][0]
 loft('Alternate hoodie '+label+' sleeve',[(.065,.015,.016,0),(.05,.046,.048,0),(.02,.063,.065,0),(-.035,.068,.068,0),(-.105,.063,.063,0)],hoodie,arm,16)
# Add a distinct, editable backpack and individual fingers.
backpack=mat('Backpack charcoal',(35,40,43))
trim=mat('Backpack trim',(81,89,86))
ell('Backpack shell',(0,.150,.175),(.155,.074,.19),backpack,body,20,12)
ell('Backpack front pocket',(0,.219,.105),(.13,.018,.085),trim,body,16,10)
for side in (-1,1):
 path('Backpack shoulder strap',[(side*.105,.10,.32),(side*.155,-.015,.31),(side*.14,-.11,.22),(side*.13,-.111,.08)],.014,backpack,body,8)
for side,label in [(-1,'Left'),(1,'Right')]:
 elbow=limbs[label][1]
 old=bpy.data.objects.get(label+'Rounded hand')
 if old:bpy.data.objects.remove(old,do_unlink=True)
 ell(label+' Palm',(0,-.005,-.155),(.043,.032,.039),skin,elbow,12,8)
 for finger in range(4):
  x=(finger-1.5)*.020
  ell(label+' Finger '+str(finger),(x,-.008,-.195-abs(finger-1.5)*.003),(.010,.014,.038-abs(finger-1.5)*.004),skin,elbow,10,8)
# Normalize mesh face winding before export.
for o in scene.objects:
 if o.type=='MESH':
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
# Normalize measured rest geometry to exactly 1.72m with a floor-centred root.
bpy.context.view_layer.update()
points=[o.matrix_world@v.co for o in scene.objects if o.type=='MESH' for v in o.data.vertices]
low=min(p.z for p in points);high=max(p.z for p in points);factor=1.72/(high-low)
body.location.z-=low;root.scale=(factor,factor,factor)
# Build the skinned armature and authored clips in a separate module.
import sys
sys.path.insert(0,str(ROOT))
from rig import build_rig, render_and_export
rig=build_rig(scene,root,body,head,limbs)
render_and_export(scene,rig,ROOT,mat)
