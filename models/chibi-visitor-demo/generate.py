import bpy, math, os
from mathutils import Vector
ROOT=os.path.dirname(os.path.abspath(__file__))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(name,c,rough=.78):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;return m
skin=mat('Warm skin',(0.78,.47,.31));white=mat('Ivory white shirt',(.91,.91,.87));blue=mat('Denim blue',(.10,.25,.48));shoe=mat('Sneaker white',(.92,.93,.96));hair=mat('Dark chocolate hair',(.075,.042,.034));eye=mat('Dark eyes',(.018,.025,.033),.25);pink=mat('Cheek blush',(.88,.36,.38));sole=mat('Shoe soles',(.55,.60,.65));
root=bpy.data.objects.new('GJH_Chibi_Visitor_Demo',None);bpy.context.collection.objects.link(root)
def uv(name,loc,scale,material,seg=24,rings=12):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(material);o.parent=root;bpy.ops.object.shade_smooth();return o
def cylinder(name,loc,radius,depth,material,vertices=16):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc);o=bpy.context.object;o.name=name;o.data.materials.append(material);o.parent=root; bevel=o.modifiers.new('Soft edges','BEVEL');bevel.width=.055;bevel.segments=2;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');return o
# dimensions ~1.85m, oversized head and compact body
uv('Head',(0,0,1.40),(.47,.39,.48),skin,40,24)
uv('Hair cap',(0,.015,1.68),(.485,.405,.275),hair,40,20)
for i,x in enumerate([-.32,-.15,.05,.25]):uv('Hair tuft %d'%i,(x,-.295,1.73+(.03 if i%2 else 0)),(.16,.15,.13),hair)
for x,side in [(-.48,'L'),(.48,'R')]:uv('Ear '+side,(x,0,1.38),(.085,.095,.135),skin)
for x,side in [(-.19,'L'),(.19,'R')]:
 uv('Eye '+side,(x,-.358,1.43),(.055,.035,.075),eye,20,12)
 uv('Cheek '+side,(x*1.48,-.335,1.27),(.095,.012,.045),pink,20,12)
uv('Nose',(0,-.397,1.34),(.035,.03,.032),skin,16,8)
uv('Torso',(0,0,.83),(.29,.205,.39),white,32,18)
uv('Neck',(0,0,1.085),(.115,.11,.10),skin)
for x,side in [(-1,'L'),(1,'R')]:
 uv('Sleeve '+side,(x*.31,0,.98),(.13,.16,.16),white)
 uv('Arm '+side,(x*.39,-.005,.78),(.10,.11,.21),skin)
 uv('Hand '+side,(x*.405,-.008,.59),(.11,.105,.11),skin)
 uv('Jeans leg '+side,(x*.145,0,.40),(.13,.17,.25),blue)
 uv('Sneaker '+side,(x*.15,-.105,.135),(.17,.265,.12),shoe)
 uv('Sole '+side,(x*.15,-.11,.065),(.18,.27,.045),sole)
uv('Jeans waist',(0,0,.60),(.27,.20,.13),blue)
# GLB export selected root and descendants
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
 if o==root or o.parent==root:o.select_set(True)
bpy.context.view_layer.objects.active=root
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'chibi-visitor-demo.blend'))
bpy.ops.export_scene.gltf(filepath=os.path.join(ROOT,'exports','chibi-visitor-demo.glb'),export_format='GLB',use_selection=True,export_apply=True)
# render faithful thumbnail
world=bpy.context.scene.world;world.color=(.6,.6,.6)
bpy.ops.object.camera_add(location=(2.7,-4.8,2.2));cam=bpy.context.object;direction=Vector((0,0,1.0))-cam.location;cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.5;bpy.context.scene.camera=cam
for loc,power,size in [((1,-3,4),550,3),((-3,-2,2),330,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=os.path.join(ROOT,'previews','front.png');scene.render.film_transparent=True;bpy.ops.render.render(write_still=True)
print('CHIBI_EXPORT_OK')
