"""Original GJH-M061 reference-inspired wall shelf; no brand art. Blender4.0.2, metric, no third-party art."""
from pathlib import Path
import bpy,math,sys
from mathutils import Vector
LOD=0
HERE=Path(__file__).resolve().parent; SLUG='gjh-m061-premium-wall-shelf-low'; ROOT='ASSET_GJHM061'
def mat(name,rgb,metal=0,rough=.5):
    m=bpy.data.materials.new(name);m.use_nodes=True
    c=tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb)+(1,)
    p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=c;p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;m.diffuse_color=c;return m
def empty(name,loc=(0,0,0),parent=None):
    o=bpy.data.objects.new(name,None);bpy.context.scene.collection.objects.link(o);o.location=loc;o.parent=parent;return o
def finish(o,name,m,parent,bevel=.003):
    o.name=name;o.data.materials.append(m);o.parent=parent
    if bevel and LOD<3:
        b=o.modifiers.new('Soft manufactured edge','BEVEL');b.width=bevel;b.segments=[4,2,1,0][LOD];o.modifiers.new('Corner normals','WEIGHTED_NORMAL')
    return o
def box(name,loc,dims,m,parent,bevel=.003):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,name,m,parent,bevel)
def rod(name,a,b,r,m,parent):
    a,b=Vector(a),Vector(b);d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return finish(o,name,m,parent,.001)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def texture_mat(name,kind):
    m=mat(name,(.5,.4,.3),0,.42 if kind=='stone' else .5)
    n=256;im=bpy.data.images.new(name+' baked original',width=n,height=n,alpha=True);pix=[]
    for y in range(n):
        for x in range(n):
            u=x/n;v=y/n
            if kind=='wood':
                grain=math.sin(2*math.pi*(u*36+.17*math.sin(v*13)+.12*math.sin(v*31)))
                fine=math.sin(u*math.pi*190)*.018
                c=(.44+.055*grain+fine,.265+.035*grain+fine,.13+.018*grain+fine)
            else:
                vein=abs(math.sin(2*math.pi*(u*3+v*1.3+.12*math.sin(v*19)+.035*math.sin(u*50))))
                thin=max(0,1-vein/.045);cloud=.012*math.sin(u*43+v*31)
                c=(.055+cloud+.25*thin,.067+cloud+.19*thin,.06+cloud+.10*thin)
            pix.extend((*c,1))
    im.pixels.foreach_set(pix);im.filepath_raw=str(HERE/'textures'/(kind+'.png'));im.file_format='PNG';im.save();im.pack()
    node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=im;m.node_tree.links.new(node.outputs['Color'],m.node_tree.nodes['Principled BSDF'].inputs['Base Color']);return m
def build(root):
    emerald=mat('Emerald lacquer',(.035,.20,.15),.15,.26);gold=mat('Champagne gold',(.69,.57,.34),.8,.27);wood=texture_mat('Warm wood baked grain','wood');stone=texture_mat('Dark stone baked veins','stone');led=mat('Warm LED diffuser',(.98,.76,.43),0,.35)
    bs=led.node_tree.nodes['Principled BSDF'];bs.inputs['Emission Color'].default_value=(1,.56,.22,1);bs.inputs['Emission Strength'].default_value=2.5
    root['units']='metres';root['front_axis']='Blender -Y / glTF +Z';root['gjh_model_id']='GJH-M061';root['lod']=LOD;root['construction']='Two separate bays with solid middle upright; four independent shelves in two low display rows'
    cabinet=empty('cabinet',parent=root);trim=empty('trim',parent=root)
    box('cabinet_stone_base',(0,0,.17),(2.36,.51,.28),stone,cabinet,.025)
    box('trim_base_plinth',(0,0,.025),(2.4,.55,.05),gold,trim,.020)
    box('trim_base_top',(0,0,.335),(2.4,.55,.05),gold,trim,.020)
    box('cabinet_back',(0,.23,.745),(2.08,.04,.77),wood,cabinet,.004)
    for side,x in [('left',-1.12),('right',1.12)]:
        box('cabinet_'+side+'_pillar',(x,0,.745),(.16,.50,.77),emerald,cabinet,.012)
        box('trim_'+side+'_front',(x,-.255,.745),(.16,.02,.77),gold,trim,.006)
        box('trim_'+side+'_inner',(-1.038 if x<0 else 1.038,-.08,.745),(.004,.32,.77),gold,trim,.001)
    box('cabinet_middle_pillar',(0,-.02,.6375),(.10,.46,.555),emerald,cabinet,.008)
    box('trim_middle_front',(0,-.255,.6375),(.10,.02,.555),gold,trim,.004)
    for side,x in [('left',-.052),('right',.052)]:box('trim_middle_'+side+'_lining',(x,-.08,.6375),(.004,.32,.555),gold,trim,.001)
    box('cabinet_crown',(0,0,1.16),(2.4,.55,.08),emerald,cabinet,.025)
    box('trim_crown_lip',(0,0,1.13),(2.4,.53,.02),gold,trim,.006)
    header=empty('brand_header',parent=root);header['artwork']='Blank original continuous header; no branding'
    box('brand_header_panel',(0,-.195,1.03),(2.04,.045,.18),emerald,header,.012)
    for n,z in [('top',1.1275),('bottom',.9275)]:box('brand_header_trim_'+n,(0,-.23,z),(2.05,.025,.015),gold,header,.004)
    for n,x in [('left',-1.025),('right',1.025)]:box('brand_header_trim_'+n,(x,-.23,1.03),(.01,.025,.21),gold,header,.003)
    box('brand_header_light_canopy',(0,-.005,.9275),(2.072,.45,.025),wood,header,.004)
    label=empty('header_surface_front',(0,-.22,1.03),header);label['label_width_m']=1.92;label['label_height_m']=.16
    for row,z in enumerate([.43,.76],1):
        shelfgroup=empty('shelf_%d'%row,parent=root);shelfgroup['role']='row group with two independently editable bay boards'
        railgroup=empty('price_rail_%d'%row,parent=root)
        for side,x in [('left',-.545),('right',.545)]:
            box('shelf_%d_%s'%(row,side),(x,-.02,z),(.982,.46,.04),wood,shelfgroup,.006)
            box('price_rail_%d_%s'%(row,side),(x,-.257,z+.015),(.982,.018,.065),gold,railgroup,.004)
            box('LED_%d_%s'%(row,side),(x,-.19,z-.025),(.84,.016,.010),led,root,.002)
        ar=empty('product_anchor_row_%d'%row,parent=root);ar['capacity']=6
        for i,x in enumerate([-.86,-.545,-.23,.23,.545,.86],1):
            o=empty('product_anchor_row_%d_slot_%02d'%(row,i),(x,-.02,z+.021),ar);o['role']='external_product_anchor';o['row']=row;o['slot']=i;o['bay']='left' if x<0 else 'right';o['reference_product_footprint_m']=[.20,.22]
    box('LED_header',(0,-.18,.910),(1.96,.016,.010),led,root,.002)
    box('LED_base',(0,-.261,.061),(2.02,.012,.010),led,root,.002)
    collision=empty('collision',parent=root);collision['shape']='box';collision['size_m']=[2.4,.55,1.2];collision['center_blender_m']=[0,0,.6];collision['asset']='exports/collision.glb'
def studio():
    s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=128;s.cycles.use_denoising=False;s.render.resolution_x=s.render.resolution_y=768;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
    s.world=bpy.data.worlds.new('Neutral retail studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.13,.15,.16,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6;s.view_settings.look='AgX - Medium High Contrast'
    for n,loc,p in [('Key',(-3,-4,4.5),1100),('Fill',(3,-3,3),850),('Top',(0,.1,4.5),1100)]:
        bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name='STUDIO_'+n;o.data.energy=p;o.data.size=4;aim(o,(0,0,1))
    bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.name='STUDIO_Camera';s.camera.data.type='ORTHO'
def export(path=None):
    bpy.ops.object.select_all(action='DESELECT');r=bpy.data.objects[ROOT];r.select_set(True)
    for o in r.children_recursive:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(path or HERE/'exports/optimized.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_animations=True,export_texcoords=True,export_extras=True,export_cameras=False,export_lights=False)
def render_views():
    s=bpy.context.scene
    for name,delta,target,scale in [('hero',(3,-4,2),(0,0,.6),3.3),('front',(0,-4,1),(0,0,.6),3.0),('rear',(3,4,1.8),(0,0,.6),3.3),('side',(4,-1,1.3),(0,0,.6),3.0),('detail',(1,-3,1.1),(.45,-.14,.62),1.25)]:
        if '--view' in sys.argv and name!=sys.argv[sys.argv.index('--view')+1]:continue
        target=Vector(target);s.camera.location=target+Vector(delta);s.camera.data.ortho_scale=scale;aim(s.camera,target);s.render.filepath=str(HERE/'previews'/(name+'.png'));bpy.ops.render.render(write_still=True)
def main():
    global LOD
    for d in ['sources','exports','previews','reports','metadata','textures']:(HERE/d).mkdir(exist_ok=True)
    for level in range(4):
        LOD=level;bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;s=bpy.context.scene;s.render.fps=24;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
        build(empty(ROOT));studio();export(HERE/'exports'/('lod%d.glb'%level))
        if level==0:
            bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'sources'/(SLUG+'.blend')),compress=True)
            import shutil;shutil.copyfile(HERE/'exports/lod0.glb',HERE/'exports/optimized.glb')
            if '--skip-render' not in sys.argv:render_views()
        elif '--skip-render' not in sys.argv:
            s.camera.location=(3,-4,3);aim(s.camera,(0,0,.6));s.camera.data.ortho_scale=3.3;s.render.filepath=str(HERE/'previews'/('lod%d.png'%level));bpy.ops.render.render(write_still=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);r=empty(ROOT);box('collision',(0,0,.6),(2.4,.55,1.2),mat('Collider debug',(.5,.2,.2)),r,0);export(HERE/'exports/collision.glb')
if __name__=='__main__':main()
