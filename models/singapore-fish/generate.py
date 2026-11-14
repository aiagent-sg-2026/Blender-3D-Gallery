"""Original deterministic fish studies. Run with Blender --background --python this_file.
No downloads. X is length (head negative), Z is up. Sizes are authoring examples,
not species maximums. Each fish has an independent scene and editable components.
"""
import bpy, math, json, random, sys
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from swim import rig_swim, export_swim
SPECS=json.loads((HERE/'species.json').read_text())
PALETTE={'silver':(.56,.66,.70),'red':(.75,.12,.09),'brown':(.30,.22,.13),'gold':(.80,.58,.16),'charcoal':(.17,.22,.24),'teal':(.13,.40,.42),'pink':(.88,.37,.35),'olive':(.34,.38,.18),'bronze':(.55,.35,.14),'orange':(.95,.29,.035),'aqua':(.04,.65,.52),'yellow':(.95,.76,.08),'blue':(.06,.19,.65),'white':(.85,.86,.80)}
def material(name,c,metal=.15):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True
 p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in c),1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=.36
 return m
def mesh(name,vs,fs,mat):
 m=bpy.data.meshes.new(name);m.from_pydata(vs,[],fs);m.update();o=bpy.data.objects.new(name,m);bpy.context.scene.collection.objects.link(o);o.parent=ROOT;o.data.materials.append(mat)
 for p in m.polygons:p.use_smooth=True
 return o
def ellipsoid(name,pos,scale,mat):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=pos);o=bpy.context.object;o.name=name;o.scale=scale;o.parent=ROOT;o.data.materials.append(mat)
 for p in o.data.polygons:p.use_smooth=True
 return o
def line(name,points,r,mat):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=1;s=c.splines.new('POLY');s.points.add(len(points)-1)
 for p,v in zip(s.points,points):p.co=(*v,1)
 o=bpy.data.objects.new(name,c);bpy.context.scene.collection.objects.link(o);o.parent=ROOT;o.data.materials.append(mat)
 # Curves must be meshes to remain present in GLB exports.
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
 return bpy.context.object
def fin(name,points,mat,rays=True):
 # Thin closed wedge rather than invisible single-sided polygons.
 n=len(points);eps=.002
 vs=[(x,y-eps,z) for x,y,z in points]+[(x,y+eps,z) for x,y,z in points]
 fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 mesh(name,vs,fs,mat)
 if rays:
  origin=Vector(points[0])
  for i,p in enumerate(points[1:-1]):line(name+'_Ray%02d'%i,[origin,Vector(p)],.0015,FINRAY)
def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
for index,spec in enumerate(SPECS,1):
 slug,cn,en,priority,kind,color,pattern,length=spec
 if '--' in sys.argv and slug not in sys.argv[sys.argv.index('--')+1:]:continue
 folder=HERE/slug
 for sub in ['exports','previews','sources','metadata']:(folder/sub).mkdir(parents=True,exist_ok=True)
 # New isolated scene: never edit an existing user's scene or source.
 scene=bpy.data.scenes.new('FISH-%03d_%s'%(index,slug));bpy.context.window.scene=scene
 ROOT=bpy.data.objects.new('ASSET_'+slug.replace('-','_'),None);scene.collection.objects.link(ROOT);ROOT.scale=(length,)*3
 ROOT['fish_id']='FISH-%03d'%index;ROOT['priority']=priority;ROOT['authoring_length_m']=length;ROOT['style']='Stylized reference study, not taxonomic identification'
 rgb=PALETTE[color];BODY=material(slug+'_Skin',rgb,.25);BELLY=material(slug+'_Belly',tuple(min(.95,v*.5+.42) for v in rgb));BACK=material(slug+'_Back',tuple(v*.53 for v in rgb));DARK=material(slug+'_Markings',(.035,.045,.05));WHITE=material(slug+'_Ivory',(.93,.91,.79));GOLD=material(slug+'_FinGold',(.88,.63,.12));RED=material(slug+'_FinRed',(.72,.12,.06));FIN=RED if 'redfins' in pattern else GOLD if color in ['gold','yellow'] or pattern=='yellowtail' else BODY;FINRAY=material(slug+'_FinRays',tuple(min(1,v*.65+.18) for v in rgb))
 rng=random.Random(index)
 h,w=.17,.09
 if kind in ['disc','diamond']:h,w=.32,.055
 if kind=='deep':h,w=.23,.10
 if kind=='bass':h,w=.19,.135
 if kind in ['long','arowana','snake','catlong','ribbon','eel']:h,w=.10,.065
 if kind=='ribbon':h,w=.085,.018
 if kind=='eel':h,w=.045,.04
 if kind=='goby':h,w=.13,.13
 if kind=='shark':h,w=.10,.13
 if kind=='puffer':h,w=.34,.27
 if kind=='round':h,w=.26,.17
 if kind in ['fancy','guppy']:h,w=.14,.065
 if kind=='ray':h,w=.045,.40
 # Ring profile gives a blunt head, broad shoulders and narrow caudal peduncle.
 rings=36;segments=32;vs=[];fs=[];fractions=[]
 for i in range(rings+1):
  t=i/rings;x=-.48+.89*t
  profile=max(.008,math.sin(math.pi*t)**.65)*(1.16-.48*t)
  if kind in ['eel','ribbon']:profile=max(.006,(1-t)**.6)*(.55+.45*math.sin(math.pi*t))
  if kind=='ray':profile=max(.006,t/.4 if t<.4 else (1-t)/.6)
  bend=.018*math.sin(t*math.pi*2) if kind in ['eel','ribbon','snake'] else 0
  for j in range(segments):
   a=2*math.pi*j/segments;vs.append((x,w*profile*math.cos(a)+bend,h*profile*math.sin(a)))
 for i in range(rings):
  for j in range(segments):fs.append((i*segments+j,i*segments+(j+1)%segments,(i+1)*segments+(j+1)%segments,(i+1)*segments+j))
 fs.extend([tuple(range(segments-1,-1,-1)),tuple(rings*segments+j for j in range(segments))]);body=mesh('BODY_Profile',vs,fs,BODY)
 for m in [BELLY,BACK,DARK,WHITE,RED]:body.data.materials.append(m)
 for p in body.data.polygons:
  c=p.center;x=c.x;t=(x+.48)/.89
  p.material_index=0 if kind=='ray' else 1 if c.z<-.045 else 2 if c.z>h*.62 else 0
  if pattern in ['bars','tiger','angelfish'] and int(t*(7 if pattern=='bars' else 5))%2==0:p.material_index=4 if pattern=='angelfish' else 3
  if pattern=='clown' and any(abs(t-a)<.045 for a in [.20,.49,.77]):p.material_index=4
  if pattern in ['stripe','stripes'] and abs(c.z-h*.2)<h*.10:p.material_index=3
  if pattern=='eyeband' and .12<t<.23:p.material_index=3
  if pattern=='saddle' and .48<t<.61:p.material_index=3
  if pattern=='koi':
   v=math.sin(x*32+c.z*19)+math.cos(c.y*40-x*14)
   p.material_index=5 if v>.15 else 3 if v<-.95 else 4
  if pattern=='marble' and math.sin(x*50+c.z*57)*math.cos(c.y*69-x*23)>.15:p.material_index=3
 # Distinct lip volume for big-mouthed fish and a parrotfish beak.
 if kind in ['bass','goby']:
  ellipsoid('MOUTH_LowerJaw',(-.423,0,-h*.22),(.070,w*.57,h*.22),BELLY)
 if slug=='parrotfish':ellipsoid('MOUTH_Beak',(-.455,0,-.015),(.04,.045,.055),WHITE)
 # Lateral eye pair, iris and pupils.
 for side in [-1,1]:
  ex=-.34;ey=side*w*.75;ez=h*.30
  if kind=='ray':ex=-.22;ey=side*.07;ez=.03
  eye_scale=.014 if kind=='eel' else .023 if kind not in ['snapper','puffer'] else .029
  ellipsoid('EYE_Socket', (ex,ey,ez),(eye_scale*1.2,eye_scale*.30,eye_scale*1.2),DARK)
  ellipsoid('EYE_Iris',(ex,ey+side*.006,ez),(eye_scale,.006,eye_scale),GOLD)
  ellipsoid('EYE_Pupil',(ex,ey+side*.011,ez),(eye_scale*.55,.004,eye_scale*.65),DARK)
  if kind!='ray':
   line('GILL_Cover', [(-.23,side*w*.91,h*.48),(-.20,side*w*1.01,0),(-.25,side*w*.84,-h*.53)],.0028,BACK)
   line('MOUTH_Opening',[(-.468,side*w*.19,-h*.05),(-.40,side*w*.58,-h*.16),(-.32 if kind in ['bass','goby'] else -.40,side*w*.65,-h*.08)],.003,DARK)
 if kind=='ray':
  line('TAIL_LongWhip',[(.33,0,0),(.65,0,-.015),(.99,.04,-.035),(1.15,.10,-.04)],.009,BACK)

 elif kind=='eel':
  line('TAIL_Eel',[(.37,0,0),(.48,.014,.007),(.56,.022,.025)],.012,BODY)
 else:
  fork=kind in ['stream','long','deep','disc','shark','cat','arowana'] and pattern not in ['clown','tiger']
  tailheight=.18 if kind not in ['fancy','guppy','round'] else .30
  if kind=='shark':tailheight=.28
  tail=[(.34,0,0),(.62,0,tailheight),(.55,0,.055 if fork else .13),(.45 if fork else .57,0,0),(.55,0,-.055 if fork else -.13),(.62,0,-tailheight)]
  if kind=='shark':tail=[(.34,0,0),(.69,0,.32),(.59,0,.09),(.46,0,.015),(.59,0,-.16),(.47,0,-.12)]
  fin('CAUDAL_Tail',tail,FIN)
  if kind in ['fancy','guppy','round']:
   fin('CAUDAL_Fan',[ (.32,0,0),(.58,0,.29),(.72,0,.23),(.77,0,0),(.72,0,-.23),(.58,0,-.29)],RED if kind!='fancy' else BODY)
  dorsal_top=.42 if kind=='shark' else h*1.9 if kind in ['snapper','lion'] else h*1.5
  if kind in ['snake','catlong','ribbon','arowana']:start,end=-.21,.33
  else:start,end=-.17,.24
  points=[(start,0,h*.65)]
  for j in range(11):
   t=j/10;x=start+(end-start)*t;z=h*.75+(dorsal_top-h*.75)*math.sin(math.pi*(t*.85+.07))
   if kind in ['snapper','lion','deep'] and j%2==0:z+=.035 if kind!='lion' else .12
   points.append((x,0,z))
  points.append((end,0,h*.34))
  if kind=='shark':points=[(-.13,0,.08),(-.025,0,.33),(.16,0,.075)]
  if kind=='fancy':points=[(-.18,0,.10),(-.08,0,.31),(.24,0,.32),(.36,0,.12)]
  fin('DORSAL_Fin',points,FIN)
  fin('ANAL_Fin',[(.02,0,-h*.8),(.13,0,-h*1.4),(.34,0,-h*.55)],FIN)
  for side in [-1,1]:
   fin('PECTORAL_Fin', [(-.20,side*w*.8,0),(.02,side*(w+.13),-.07),(.07,side*w*.8,-.075)],FIN)
   if kind=='shark':fin('PECTORAL_Shark', [(-.21,side*w*.5,-.02),(.12,side*.36,-.12),(.02,side*w,-.06)],BODY)
   if pattern in ['threads','fourthreads']:
    for j in range(4 if pattern=='fourthreads' else 5):line('PECTORAL_FreeThread_%d'%j,[(-.17,side*w,-.04),(-.05,side*(w+.05+j*.015),-.17-j*.025),(.16,side*(w+.05+j*.02),-.21-j*.03)],.0015,WHITE)
   if 'barbels' in pattern or kind in ['cat','catlong'] or pattern=='arowana':
    count=1 if pattern=='arowana' else 3
    for j in range(count):line('MOUTH_Barbel_%d'%j,[(-.46,side*.02,-.015),(-.56,side*(.06+j*.025),-.035),(-.48 if count>1 else -.62,side*(.13+j*.04),-.08-j*.015)],.0025,BELLY)
   if kind=='shark':
    for j in range(5):line('GILL_Slit_%d'%j,[(-.21+j*.025,side*w*.94,.05),(-.19+j*.025,side*w,-.06)],.0025,DARK)
   if kind=='lion':
    for j in range(9):line('PECTORAL_RadiatingSpine_%d'%j,[(-.17,side*w,0),(-.18+j*.052,side*(.18+.17*math.sin(j/8*math.pi)),.15-.3*j/8)],.004,WHITE)
 # Physical scale tiles or skin spots, merged into one editable mesh.
 if 'scales' in pattern or pattern in ['arowana','spots','whalespots','threespots']:
  sv=[];sf=[]
  for i in range(5,30):
   t=i/rings;profile=math.sin(math.pi*t)**.65*(1.16-.48*t);x=-.48+.89*t
   for j in range(16):
    a=2*math.pi*(j+(i%2)*.5)/16
    if 'spots' in pattern and rng.random()>.28:continue
    if pattern=='threespots' and i not in [12,22]:continue
    y=w*profile*math.cos(a);z=h*profile*math.sin(a)
    n=Vector((0,math.cos(a)/w,math.sin(a)/h)).normalized();center=Vector((x,y,z))+n*.001
    r=.010 if 'spots' in pattern else .016
    tangent=Vector((0,-math.sin(a),math.cos(a)));base=len(sv)
    sv.append(tuple(center+n*.002))
    for k in range(6):sv.append(tuple(center+Vector((math.cos(k*math.pi/3)*r,0,0))+tangent*math.sin(k*math.pi/3)*r*.7))
    sf.extend([(base,base+1+k,base+1+(k+1)%6) for k in range(6)])
  mesh('SKIN_ScaleTiles' if 'scales' in pattern or pattern=='arowana' else 'SKIN_Spots',sv,sf,WHITE if pattern=='whalespots' else DARK if 'spots' in pattern else FINRAY)
 rig=rig_swim(ROOT,kind,slug,h,w)
 bpy.context.view_layer.update()
 bpy.ops.object.select_all(action='DESELECT');ROOT.select_set(True)
 for o in ROOT.children_recursive:o.select_set(True)
 export_swim(ROOT,folder/'exports/model.glb')
 # Lightweight material-color Blender studio thumbnails.
 bpy.ops.object.camera_add(location=(length*.18,-length*2.8,length*.75));camera=bpy.context.object;camera.name='STUDIO_Camera';scene.camera=camera
 if kind=='ray':camera.location=(length*.25,-length*1.3,length*2.6)
 aim(camera,(length*(.33 if kind=='ray' else .08),0,0));camera.data.type='ORTHO';camera.data.ortho_scale=length*(1.9 if kind=='ray' else 1.45)
 scene.world=bpy.data.worlds.new(slug+'_World');scene.world.color=(.035,.055,.075)
 scene.render.engine='BLENDER_WORKBENCH';sh=scene.display.shading;sh.light='STUDIO';sh.color_type='MATERIAL';sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD'
 scene.render.resolution_x=640;scene.render.resolution_y=480;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
 scene.render.filepath=str(folder/'previews/hero.png');bpy.ops.render.render(write_still=True)
 # Each .blend contains only its own scene and referenced data.
 bpy.data.libraries.write(str(folder/'sources'/f'{slug}.blend'),{scene},fake_user=True)
 metadata={'id':'fish-'+slug,'display':{'previewRotationY':0,'previewCameraDirection':([.12,1,.5] if kind=='ray' else [.12,.28,1]),'studioEnvironment':True,'environmentIntensity':.3,'previewLighting':{'hemisphereIntensity':.8,'directionalIntensity':1.4}},'accuracy_notes':'Original stylized study based on the requested silhouette and markings. Common names are supplied aliases and may overlap across species; not a taxonomic or scale identification reference. Looping skeletal swim with tail and fin motion; no inflation or trajectory simulation. Length is an illustrative authoring size.','attribution':[{'credit':'Original procedural geometry and materials created in Blender; no third-party assets.'}],'fish_id':'FISH-%03d'%index,'priority':priority,'authoring_length_m':length,'source':f'models/singapore-fish/{slug}/sources/{slug}.blend'}
 (folder/'metadata/model.json').write_text(json.dumps(metadata,indent=2)+'\n')
 # Release each completed scene to keep a large batch bounded in memory.
 bpy.context.window.scene=bpy.data.scenes[0];bpy.data.scenes.remove(scene)
 for o in list(bpy.data.objects):
  if not o.users:bpy.data.objects.remove(o)
 print('FISH_DONE',index,slug,flush=True)
