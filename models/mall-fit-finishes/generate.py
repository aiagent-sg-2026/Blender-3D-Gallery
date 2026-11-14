"""Original fit-study finishes. Rebuilds only this directory's three assets.
--export-source exports saved .blend edits without rebuilding geometry.
"""
from pathlib import Path
import bpy, json, sys
from mathutils import Vector
HERE = Path(__file__).resolve().parent
SPECS = {'mall-shopfront-fascia-210': 2.1, 'mall-shopfront-fascia-120': 1.2,
         'mall-column-ceiling-collar': None}

def material(name, color, roughness=.5, metallic=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = roughness
    p.inputs['Metallic'].default_value = metallic
    m.diffuse_color = (*color, 1)
    return m

def box(name, lo, hi, mat, parent):
    dims = [hi[i]-lo[i] for i in range(3)]
    assert min(dims) > 0
    bpy.ops.mesh.primitive_cube_add(size=1, location=[(lo[i]+hi[i])/2 for i in range(3)])
    o = bpy.context.object; o.name = name; o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat); o.parent = parent
    # Keep contact faces exact; smoothing/bevels would open thin visual seams.
    return o

def anchor(name, loc, root):
    o = bpy.data.objects.new(name, None); bpy.context.scene.collection.objects.link(o)
    o.parent = root; o.location = loc; o.empty_display_size = .035

def build(slug, width):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene; scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1
    root = bpy.data.objects.new('ASSET_'+slug.replace('-', '_'), None); scene.collection.objects.link(root)
    root['units']='metres'; root['source_up']='Z'; root['export_up']='Y'
    if width is not None:
        frame = material('Satin charcoal aluminium',(.0528606474,.0742135718,.078187421),.32,.55)
        panel = material('Warm ivory infill',(.58407843,.56471151,.47932017),.72)
        sign = material('REPLACEABLE unbranded sign face',(.64447969,.67244315,.63075715),.48)
        w=width/2; rail=.03
        box('FRAME_Bottom',(-w,-.03,0),(w,.03,rail),frame,root)
        box('FRAME_Top',(-w,-.03,.57),(w,.03,.6),frame,root)
        box('FRAME_Left',(-w,-.03,rail),(-w+rail,.03,.57),frame,root)
        box('FRAME_Right',(w-rail,-.03,rail),(w,.03,.57),frame,root)
        box('PANEL_Infill',(-w+rail,-.02,rail),(w-rail,.02,.57),panel,root)
        box('SIGN_ReplaceableFace',(-w+.07,-.028,.07),(w-.07,-.02,.53),sign,root)
        for name,loc in [('Base',(0,0,0)),('Top',(0,0,.6)),('Left',(-w,0,0)),('Right',(w,0,0))]:anchor('CONNECTOR_'+name,loc,root)
        root['origin']='bottom centre; front -Y'; root['width_m']=width; root['height_m']=.6
        root['placement']='Z=2.4 at existing door/partition; top=3.0 ceiling-grid underside; recessed panel gap 8 mm'
    else:
        grid=material('Powder-coated ivory T grid',(.64447969,.67244315,.63075715),.42)
        panel=material('Smooth ivory ceiling closure',(.58407843,.56471151,.47932017),.82)
        # Four exact, non-overlapping perimeter pieces and four inner trim pieces.
        for name,lo,hi in [
          ('Outer_N',(-.6,.588,0),(.6,.6,.032)),('Outer_S',(-.6,-.6,0),(.6,-.588,.032)),
          ('Outer_E',(.588,-.588,0),(.6,.588,.032)),('Outer_W',(-.6,-.588,0),(-.588,.588,.032)),
          ('Inner_N',(-.312,.3,0),(.312,.312,.032)),('Inner_S',(-.312,-.312,0),(.312,-.3,.032)),
          ('Inner_E',(.3,-.3,0),(.312,.3,.032)),('Inner_W',(-.312,-.3,0),(-.3,.3,.032))]:box('TRIM_'+name,lo,hi,grid,root)
        for name,lo,hi in [
          ('N',(-.588,.312,.008),(.588,.588,.024)),('S',(-.588,-.588,.008),(.588,-.312,.024)),
          ('E',(.312,-.312,.008),(.588,.312,.024)),('W',(-.588,-.312,.008),(-.312,.312,.024))]:box('CLOSURE_'+name,lo,hi,panel,root)
        for name,loc in [('XP',(.6,0,0)),('XN',(-.6,0,0)),('YP',(0,.6,0)),('YN',(0,-.6,0))]:anchor('CONNECTOR_'+name,loc,root)
        root['origin']='centre of visible trim underside';root['outer_width_m']=1.2;root['clear_hole_m']=.6
        root['placement']='Z=3.0, column centre; inner trim touches 0.6 m cap envelope, no fabricated clearance'
    return root

def export(root, slug):
    bpy.ops.object.select_all(action='DESELECT'); root.select_set(True)
    for o in root.children_recursive: o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(HERE/'exports'/(slug+'.glb')), export_format='GLB',
      use_selection=True,export_apply=True,export_yup=True,export_animations=False,
      export_extras=True,export_cameras=False,export_lights=False,export_texcoords=False)

def preview(root,slug,width):
    scene=bpy.context.scene
    target=(0,0,.30 if width else .015)
    for name,loc,power in [('Key',(-2,-3,4),500),('Fill',(3,-2,-3),400)]:
        bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name='STUDIO_'+name;o.data.energy=power;o.data.size=4
        o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.camera_add(location=(1.6,-2.5,1.6) if width else (1.4,-1.8,-1.6))
    scene.camera=bpy.context.object;scene.camera.name='STUDIO_Camera';scene.camera.rotation_euler=(Vector(target)-scene.camera.location).to_track_quat('-Z','Y').to_euler()
    scene.camera.data.type='ORTHO';scene.camera.data.ortho_scale=2.5 if width else 1.8
    scene.world=bpy.data.worlds.new('Studio');scene.world.color=(.25,.3,.32)
    scene.render.engine='CYCLES';scene.cycles.samples=24;scene.render.resolution_x=1000;scene.render.resolution_y=700;scene.render.resolution_percentage=100
    scene.render.filepath=str(HERE/'previews'/(slug+'.png'));bpy.ops.render.render(write_still=True)

for d in ['sources','exports','previews','reports']:(HERE/d).mkdir(exist_ok=True)
for slug,width in SPECS.items():
    if '--export-source' in sys.argv:
        bpy.ops.wm.open_mainfile(filepath=str(HERE/'sources'/(slug+'.blend')))
        root=bpy.data.objects['ASSET_'+slug.replace('-','_')]
    else:root=build(slug,width)
    export(root,slug)
    if '--skip-render' not in sys.argv: preview(root,slug,width)
    if '--export-source' not in sys.argv:bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'sources'/(slug+'.blend')),compress=True)
print('FINISHES_GENERATED',len(SPECS))
