"""Original modular chibi visitor v2. Blender 5.2+, no third-party artwork."""
import bpy, math, os, json
from mathutils import Vector
from math import sin,cos,pi,sqrt
HERE=os.path.dirname(os.path.abspath(__file__))
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for coll in list(bpy.data.collections):
    if coll.name not in ('Collection',):
        if not coll.objects: bpy.data.collections.remove(coll)

def col(c):
    c=c.lstrip('#'); ch=[int(c[i:i+2],16)/255 for i in (0,2,4)]
    return tuple(v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4 for v in ch)
def material(name,hex,rough=.7,metal=0):
    c=col(hex); m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    return m
M={
 'skin':material('Warm natural skin','#EBA77E'),
 'inner-ear':material('Ear warm tint','#D98776'),
 'blush':material('Soft blush','#EB958B'),
 'hair':material('Dark espresso hair','#2B2023',.75),
 'hair-highlight':material('Chestnut hair accents','#493038',.72),
 'eye-white':material('Warm eye highlights','#FFF8EA',.43),
 'iris':material('Deep brown iris','#23191F',.28),
 'specular':material('Eye catchlight','#FFFFFF',.24),
 'brow':material('Brow and smile','#533038',.7),
 'shirt':material('Ivory cotton jersey','#F4F0E7',.89),
 'shirt-shadow':material('Sleeve and collar seams','#D2D9D4',.87),
 'emblem':material('Forest green embroidered moon','#187261',.8),
 'jeans':material('Indigo blue denim','#315A83',.92),
 'jeans-seam':material('Denim seam thread','#8EB2C6',.84),
 'shoe':material('Sneaker porcelain white','#F5F4EF',.76),
 'sole':material('Sneaker rubber sole','#D3DAD8',.84),
 'shoe-detail':material('Laces and accents','#7B9B9B',.73),
}
root=bpy.data.objects.new('GJH_Chibi_Visitor_V2',None);bpy.context.collection.objects.link(root)
modules={}
for name in ('HEAD','HAIR','FACE','TOP','ARMS','JEANS','SHOES','ACCESSORY'):
    g=bpy.data.objects.new('MOD_'+name,None);bpy.context.collection.objects.link(g);g.parent=root;modules[name]=g
objects=[]
def attach(o,name,module,mat):
    o.name=name;o.parent=modules[module];o.data.materials.append(mat)
    for p in o.data.polygons: p.use_smooth=True
    objects.append(o);return o

def uv(name, xyz, size, material_key, module,seg=24,rings=14,rot=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,location=xyz)
    o=bpy.context.object;o.scale=size
    if rot:o.rotation_euler=rot
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return attach(o,name,module,M[material_key])

def poly_mesh(name,verts,faces,material_key,module):
    mesh=bpy.data.meshes.new(name+'_mesh');mesh.from_pydata(verts,[],faces);mesh.update()
    o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o)
    return attach(o,name,module,M[material_key])

def tube(name,points,thickness,material_key,module,cyc=False):
    curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.resolution_u=12;curve.bevel_depth=thickness;curve.bevel_resolution=3
    spline=curve.splines.new('BEZIER');spline.bezier_points.add(len(points)-1);spline.use_cyclic_u=cyc
    for p,co in zip(spline.bezier_points,points):
        p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,curve);bpy.context.collection.objects.link(o)
    bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o=bpy.context.object;o.select_set(False)
    return attach(o,name,module,M[material_key])

# Hand-sculpted chibi skull by rings: soft cheeks, subtly tapered jaw, wide forehead.
rv=[];rf=[];n=40;k=24;hz=1.365;rx=.423;ry=.353;rz=.407
for j in range(k+1):
    t=pi*j/k;ct=cos(t);st=max(.00001,sin(t));jaw=max(0,-ct)
    for i in range(n):
        a=2*pi*i/n;w=1-.18*jaw**2
        x=rx*w*st*cos(a);y=ry*(1-.07*jaw)*st*sin(a)
        z=hz+rz*ct
        rv.append((x,y,z))
for j in range(k):
    for i in range(n):
        a=j*n+i;b=j*n+(i+1)%n;c=(j+1)*n+(i+1)%n;d=(j+1)*n+i
        rf.append((a,b,c,d))
head=poly_mesh('Soft-cheek_sculpted_head',rv,rf,'skin','HEAD')
# slightly fitted ears and warm indents
for side,x in [('L',-.424),('R',.424)]:
    uv('Ear_'+side,(x,.005,1.338),(.093,.090,.130),'skin','HEAD')
    uv('Ear_cavity_'+side,(x+(.025 if x<0 else -.025),-.073,1.332),(.053,.017,.076),'inner-ear','HEAD',20,10)
uv('Neck',(0,.0,1.017),(.12,.12,.117),'skin','HEAD')
# Scalp-shell cap: lower at rear, hairline higher at front.
verts=[];faces=[];N=48;K=16
for j in range(K+1):
    u=max(.00004,j/K)
    for i in range(N):
        a=2*pi*i/N;back=max(0,sin(a));front=max(0,-sin(a))
        edge=1.22+back*.44-front*.04
        t=edge*u;x=.437*sin(t)*cos(a)
        y=.369*sin(t)*sin(a)+.010
        z=1.391+.413*cos(t)
        verts.append((x,y,z))
for j in range(K):
    for i in range(N):
        a=j*N+i;b=j*N+(i+1)%N;c=(j+1)*N+(i+1)%N;d=(j+1)*N+i
        faces.append((a,b,c,d))
poly_mesh('Sculpted_hair_cap',verts,faces,'hair','HAIR')
# Eight coherent blunt locks, not pom-pom spheres or spiky shingles.
for i,(x0,x1,ztip,thick) in enumerate([(-.28,-.30,1.567,.054),(-.20,-.22,1.510,.062),(-.105,-.155,1.525,.065),(.004,-.035,1.533,.064),(.115,.095,1.515,.064),(.235,.260,1.556,.057)]):
    o=tube('Blunt_swept_fringe_%02d'%(i+1),[(x0*.77,-.118,1.726),(x0-.025,-.325,1.630),(x1,-.361,ztip)],thick,'hair','HAIR')
    # each strand has a smooth blunt end from the tubular curve
for side in (-1,1):
    tube(('Left' if side<0 else 'Right')+'_temple_lock',[(side*.329,-.255,1.63),(side*.402,-.265,1.52),(side*.400,-.235,1.412)],.061,'hair','HAIR')
# The hair cap has a clean back: do not add floating highlighted locks.

def front(x,z,offset=.012):
    # underside surface based on sculpted head, plus small outward offset
    u=max(.0,1-(x/.421)**2-((z-hz)/rz)**2)
    return -.353*sqrt(u)-offset

def face_patch(name,cx,cz,sx,sz,mkey,depth=.027,module='FACE',N=32):
    verts=[(cx,front(cx,cz,depth),cz)]
    for i in range(N):
        a=2*pi*i/N;x=cx+sx*cos(a);z=cz+sz*sin(a)
        verts.append((x,front(x,z,depth),z))
    faces=[(0,i+1,(i+1)%N+1) for i in range(N)]
    return poly_mesh(name,verts,faces,mkey,module)

# Front-facing curved eye patches + intentional eye glints and expressive brows.
for side,x in [('L',-.152),('R',.152)]:
    face_patch('Eye_sclera_'+side,x,1.393,.086,.117,'eye-white',.012)
    face_patch('Iris_'+side,x,1.389,.061,.095,'iris',.019)
    face_patch('Catchlight_'+side,x-.019,1.433,.024,.029,'specular',.026)
    face_patch('Lower_glint_'+side,x+.029,1.360,.011,.011,'specular',.025)
    face_patch('Soft_blush_'+side,x*1.80,1.248,.078,.037,'blush',.012)
    tube('Brow_'+side,[(x-.064,front(x-.064,1.559,.018),1.559),(x,front(x,1.575,.018),1.575),(x+.067,front(x+.067,1.56,.018),1.56)],.013,'brow','FACE')
# Subtle nose and upward curved smile; geometry follows head surface.
uv('Nose',(0,front(0,1.315,.017),1.315),(.031,.019,.026),'skin','FACE',16,10)
tube('Warm_smile',[(-.082,front(-.082,1.203,.017),1.203),(0,front(0,1.176,.018),1.176),(.082,front(.082,1.203,.017),1.203)],.010,'brow','FACE')
# Shirts with tailored silhouette, hems, ribbed collar.
def loft(name,rings,mkey,module,N=28):
    verts=[];faces=[]
    for z,xx,yy,yo in rings:
        for i in range(N):
            a=2*pi*i/N;verts.append((xx*cos(a),yo+yy*sin(a),z))
    for j in range(len(rings)-1):
        for i in range(N):faces.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
    return poly_mesh(name,verts,faces,mkey,module)
loft('Tailored_cotton_tee',[(.655,.253,.202,0),(.72,.276,.206,0),(.84,.295,.210,0),(.975,.300,.213,0),(1.055,.245,.18,0),(1.088,.112,.12,0)],'shirt','TOP')
tube('Cotton_hem_seam',[(.248*cos(2*pi*i/24),.201*sin(2*pi*i/24),.683) for i in range(25)],.008,'shirt-shadow','TOP',False)
uv('Cotton_rib_collar',(0,0,1.093),(.148,.137,.042),'shirt-shadow','TOP',32,12)
uv('Collar_opening',(0,-.024,1.114),(.105,.097,.025),'skin','TOP',32,12)
for side in (-1,1):
    uv('Rounded_short_sleeve_'+('L' if side<0 else 'R'),(side*.307,0,.962),(.150,.183,.165),'shirt','TOP',24,14,rot=(0,side*.13,0))
    uv('Forearm_'+('L' if side<0 else 'R'),(side*.387,-.003,.779),(.105,.107,.200),'skin','ARMS',24,16,rot=(0,side*.10,0))
    uv('Soft_hand_'+('L' if side<0 else 'R'),(side*.408,-.012,.607),(.112,.101,.100),'skin','ARMS',24,14)
    uv('Thumb_'+('L' if side<0 else 'R'),(side*.333,-.057,.598),(.046,.060,.060),'skin','ARMS',16,12)
# Minimal chest emblem: green moon, independent small garment detail
uv('Embroidered_green_circle',(.113,-.211,.914),(.060,.015,.057),'emblem','ACCESSORY',24,12)
uv('Embroidered_moon_cutout',(.125,-.224,.932),(.043,.007,.045),'shirt','ACCESSORY',24,12)
# Jeans shape and construction details.
uv('Denim_waist',(0,0,.657),(.259,.203,.147),'jeans','JEANS',28,16)
for side in (-1,1):
    s='L' if side<0 else 'R';x=side*.137
    uv('Tapered_jean_leg_'+s,(x,.008,.365),(.127,.162,.276),'jeans','JEANS',28,18,rot=(0,side*.035,0))
    uv('Turned_denim_cuff_'+s,(x,-.006,.174),(.133,.163,.058),'jeans-seam','JEANS',24,12)
    uv('Dark_jean_cuff_'+s,(x,-.012,.189),(.132,.165,.042),'jeans','JEANS',24,12)
    # No floating leg seams; fitted garment details remain embedded in cloth.
    uv('Chunky_sneaker_'+s,(x,-.095,.128),(.171,.265,.128),'shoe','SHOES',28,16)
    uv('Soft_rubber_sole_'+s,(x,-.106,.061),(.186,.277,.048),'sole','SHOES',28,14)
    uv('Sneaker_toe_patch_'+s,(x,-.294,.126),(.135,.062,.071),'shirt','SHOES',24,12)
    for k in range(3):
        y=-.159-.042*k
        tube('Laces_'+s+'_'+str(k),[(x-.050,y,.225-.016*k),(x,y-.004,.237-.016*k),(x+.050,y,.225-.016*k)],.009,'shoe-detail','SHOES')
# Optimize the web GLB: one mesh per module and material, but keep module hierarchy.
# Individual islands remain editable in .blend and original authoring recipe is kept.
for module_name,module in modules.items():
    groups={}
    for mesh_obj in list(module.children):
        if mesh_obj.type=='MESH':
            key=mesh_obj.data.materials[0].name
            groups.setdefault(key,[]).append(mesh_obj)
    for mname,parts in groups.items():
        if len(parts)<2: continue
        bpy.ops.object.select_all(action='DESELECT')
        for item in parts:item.select_set(True)
        bpy.context.view_layer.objects.active=parts[0]
        bpy.ops.object.join()
        merged=bpy.context.view_layer.objects.active
        merged.name='Module_'+module_name+'_'+mname.replace(' ','_')
        merged.parent=module

# compact modular parts list, keep explicit modules and original editable meshes
bpy.ops.object.select_all(action='DESELECT')
root.select_set(True)
for o in bpy.data.objects:
    if o.parent in modules.values() or o in modules.values():o.select_set(True)
bpy.context.view_layer.objects.active=root
os.makedirs(os.path.join(HERE,'exports'),exist_ok=True)
bpy.ops.export_scene.gltf(filepath=os.path.join(HERE,'exports','chibi-visitor-v2.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_materials='EXPORT')
# source retains authored modular layers and separate preview rig
scene=bpy.context.scene
world=bpy.data.worlds.new('Soft studio world') if not scene.world else scene.world;scene.world=world;world.use_nodes=True
world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.65,.73,.77,1)
world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.6
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.015));floor=bpy.context.object;floor.name='RENDER_ONLY_ground';floor.data.materials.append(material('Studio ivory floor','#EEEFEA',.98))
bpy.ops.object.light_add(type='AREA',location=(2.8,-4,5));key=bpy.context.object;key.data.energy=470;key.data.shape='DISK';key.data.size=3.2
bpy.ops.object.light_add(type='AREA',location=(-3,-.5,2.3));fill=bpy.context.object;fill.data.energy=280;fill.data.shape='DISK';fill.data.size=2.8
bpy.ops.object.light_add(type='AREA',location=(0,3,3));rim=bpy.context.object;rim.data.energy=480;rim.data.shape='DISK';rim.data.size=2.8
scene.render.engine='CYCLES';scene.cycles.samples=28;scene.render.resolution_x=640;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=False
scene.view_settings.view_transform='AgX';scene.render.filepath=os.path.join(HERE,'previews','front.png')
# cameras: front -Y, rear +Y, profile +X, hero three quarters
for label,xyz in [('front',(0,-4.3,2.06)),('side',(4.2,0,2.06)),('back',(0,4.3,2.06)),('three-quarter',(2.7,-3.65,2.13))]:
    bpy.ops.object.camera_add(location=xyz);camera=bpy.context.object;camera.name='PREVIEW_'+label
    camera.rotation_euler=(Vector((0,0,.91))-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type='ORTHO';camera.data.ortho_scale=2.25;scene.camera=camera
    scene.render.filepath=os.path.join(HERE,'previews',label+'.png')
    bpy.ops.render.render(write_still=True)
scene.camera=bpy.data.objects.get('PREVIEW_three-quarter')
scene.render.filepath=os.path.join(HERE,'previews','three-quarter.png')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE,'chibi-visitor-v2.blend'))
print('CHIBI_V2_EXPORT_OK',len([o for o in bpy.data.objects if o.type=='MESH' and o.parent in modules.values()]),len(M),flush=True)
