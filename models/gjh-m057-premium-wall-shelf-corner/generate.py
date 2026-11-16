"""Original GJH-M057 reference-inspired wall shelf; no brand art. Blender5.1+, metric, no third-party art."""
from pathlib import Path
import bpy,math,sys
from mathutils import Vector
LOD=0
HERE=Path(__file__).resolve().parent; SLUG='gjh-m057-premium-wall-shelf-corner'; ROOT='ASSET_GJHM057'
if bpy.app.version < (5, 1, 0):
    raise RuntimeError('The repaired M057 source requires Blender 5.1+; do not downgrade it')
sys.path.insert(0, str(HERE.parents[1] / 'scripts'))
from blender_degenerate_cleanup import add_cleanup
CLEANUP_PARTS = {SLUG: ('trim_crown_lip',)}

def prepare_source_lod(root, level):
    """Derive the documented quality levels from the saved editable LOD0."""
    global LOD
    assert level in (0, 1, 2), 'LOD3 is unchanged and generated without bevels'
    LOD = level
    root['lod'] = level
    for obj in root.children_recursive:
        for modifier in obj.modifiers:
            if modifier.type == 'BEVEL':
                modifier.segments = (4, 2, 1)[level]

def prepare_asset_geometry(slug, objects):
    for obj in objects:
        if obj.name in CLEANUP_PARTS.get(slug, ()) and any(m.type == 'BEVEL' for m in obj.modifiers):
            add_cleanup(obj, ngon_method='Clip')

def export_asset(slug, root, objects, destination=None):
    export(destination)

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
def lsolid(name,z,height,m,parent,inset=0):
    lo=-.6+inset;hi=.6-inset;cx=-.05-inset;cy=.05+inset
    poly=[(lo,lo),(cx,lo),(cx,cy),(hi,cy),(hi,hi),(lo,hi)]
    verts=[(x,y,z-height/2) for x,y in poly]+[(x,y,z+height/2) for x,y in poly]
    faces=[tuple(reversed(range(6))),tuple(range(6,12))]+[(i,(i+1)%6,(i+1)%6+6,i+6) for i in range(6)]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o)
    uv=mesh.uv_layers.new(name='UVMap')
    for face in mesh.polygons:
        axis=max(range(3),key=lambda i:abs(face.normal[i]));dims=[i for i in range(3) if i!=axis]
        for li in face.loop_indices:
            v=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(v[dims[0]]+.6,v[dims[1]]+.6)
    return finish(o,name,m,parent,.008 if inset else .014)
def build(root):
    emerald=mat('Emerald lacquer',(.035,.20,.15),.15,.26);gold=mat('Champagne gold',(.69,.57,.34),.8,.27);wood=texture_mat('Warm wood baked grain','wood');stone=texture_mat('Dark stone baked veins','stone');led=mat('Warm LED diffuser',(.98,.76,.43),0,.35)
    bs=led.node_tree.nodes['Principled BSDF'];bs.inputs['Emission Color'].default_value=(1,.56,.22,1);bs.inputs['Emission Strength'].default_value=2.5
    root['units']='metres';root['front_axis']='Blender -Y / glTF +Z';root['gjh_model_id']='GJH-M057';root['lod']=LOD;root['design_interpretation']='90 degree L; each arm1.2m, nominal depth.55m; outer1.2x1.2x2.4m, not original repeated2.4x.55 table dimensions'
    cabinet=empty('cabinet',parent=root);trim=empty('trim',parent=root)
    lsolid('cabinet_stone_base',.17,.28,stone,cabinet,.015);lsolid('trim_base_plinth',.025,.05,gold,trim);lsolid('trim_base_top',.335,.05,gold,trim)
    box('cabinet_back_A',(.02,.58,1.325),(1.16,.04,1.93),wood,cabinet,.004)
    box('cabinet_back_B',(-.58,-.02,1.325),(.04,1.16,1.93),wood,cabinet,.004)
    box('cabinet_corner_spine',(-.58,.58,1.325),(.04,.04,1.93),wood,cabinet,0)
    box('cabinet_end_A',(.57,.325,1.325),(.06,.55,1.93),emerald,cabinet,.015)
    box('cabinet_end_B',(-.325,-.57,1.325),(.55,.06,1.93),emerald,cabinet,.015)
    box('trim_front_A',(.57,.065,1.325),(.06,.025,1.93),gold,trim,.006)
    box('trim_front_B',(-.065,-.57,1.325),(.025,.06,1.93),gold,trim,.006)
    lsolid('cabinet_crown',2.35,.10,emerald,cabinet);lsolid('trim_crown_lip',2.29,.02,gold,trim)
    header=empty('brand_header',parent=root)
    # Headers sit on the front edge of their supporting canopy, not behind deep end panels.
    box('brand_header_front_panel',(.255,.0925,2.04),(.55,.045,.40),emerald,header,.012)
    box('brand_header_side_panel',(-.0925,-.255,2.04),(.045,.55,.40),emerald,header,.012)
    for side in ['front','side']:
        for name,z in [('top',2.252),('bottom',1.828)]:
            box('header_trim_'+side+'_'+name,(.255,.063,z) if side=='front' else (-.063,-.255,z),(.575,.02,.024) if side=='front' else (.02,.575,.024),gold,header,.005)
        for name,c in [('near',-.02),('far',.53)]:
            box('header_trim_'+side+'_'+name,(c,.063,2.04) if side=='front' else (-.063,-c,2.04),(.024,.02,.40) if side=='front' else (.02,.024,.40),gold,header,.005)
    lsolid('brand_header_light_canopy',1.825,.03,wood,header,.02)
    front=empty('header_surface_front',(.255,.068,2.04),header);front.rotation_euler.z=0
    side=empty('header_surface_side',(-.068,-.255,2.04),header);side.rotation_euler.z=math.pi/2
    for o in [front,side]:o['label_width_m']=.44;o['label_height_m']=.36;o['convention']='local+Z outward/local+Y upward'
    for row,z in enumerate([.43,.97,1.51],1):
        lsolid('shelf_%d'%row,z,.04,wood,root,.02)
        rails=empty('price_rail_%d'%row,parent=root)
        box('price_rail_%d_A'%row,(.255,.062,z+.015),(.65,.016,.065),gold,rails,.004)
        box('price_rail_%d_B'%row,(-.062,-.325,z+.015),(.016,.51,.065),gold,rails,.004)
        box('LED_%d_A'%row,(.255,.10,z-.025),(.59,.016,.010),led,root,.002)
        box('LED_%d_B'%row,(-.10,-.25,z-.025),(.016,.60,.010),led,root,.002)
        ar=empty('product_anchor_row_%d'%row,parent=root);ar['capacity']=8
        slots=[(x,.32) for x in [-.40,-.12,.16,.44]]+[(-.32,y) for y in [-.49,-.35,-.21,-.07]]
        for i,(x,y) in enumerate(slots,1):
            o=empty('product_anchor_row_%d_slot_%02d'%(row,i),(x,y,z+.021),ar);o['role']='external_product_anchor';o['row']=row;o['slot']=i
    for name,z in [('header',1.805),('base',.061)]:
        box('LED_'+name+'_A',(.255,.10 if name=='header' else .043,z),(.59,.016,.010),led,root,.002)
        box('LED_'+name+'_B',(-.10 if name=='header' else -.043,-.25,z),(.016,.60,.010),led,root,.002)
    collision=empty('collision',parent=root);collision['shape']='concave L static proxy';collision['outer_size_m']=[1.2,1.2,2.4];collision['asset']='exports/collision.glb'
def studio():
    s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=128;s.cycles.use_denoising=False;s.render.resolution_x=s.render.resolution_y=768;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
    s.world=bpy.data.worlds.new('Neutral retail studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.13,.15,.16,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6;s.view_settings.look='AgX - Medium High Contrast'
    for n,loc,p in [('Key',(-3,-4,4.5),1100),('Fill',(3,-3,3),850),('Top',(0,.1,4.5),1100)]:
        bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name='STUDIO_'+n;o.data.energy=p;o.data.size=4;aim(o,(0,0,1))
    bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.name='STUDIO_Camera';s.camera.data.type='ORTHO'
def export(path=None):
    bpy.ops.object.select_all(action='DESELECT');r=bpy.data.objects[ROOT];r.select_set(True)
    prepare_asset_geometry(SLUG, list(r.children_recursive))
    for o in r.children_recursive:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(path or HERE/'exports/optimized.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_yup=True,export_animations=True,export_texcoords=True,export_extras=True,export_cameras=False,export_lights=False)
def render_views():
    s=bpy.context.scene
    for name,delta,target,scale in [('hero',(3,-3,1.8),(0,0,1.2),3.1),('front',(1,-4,1.0),(0,0,1.2),2.9),('rear',(-3,3,1.8),(0,0,1.2),3.1),('side',(4,-1,1.0),(0,0,1.2),2.9),('detail',(2,-2,1.0),(-.05,.05,1.1),1.55)]:
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
            s.camera.location=(3,-3,3);aim(s.camera,(0,0,1.2));s.camera.data.ortho_scale=3.1;s.render.filepath=str(HERE/'previews'/('lod%d.png'%level));bpy.ops.render.render(write_still=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);r=empty(ROOT);lsolid('collision',1.2,2.4,mat('Collider debug',(.5,.2,.2)),r);export(HERE/'exports/collision.glb')
if __name__=='__main__':main()
