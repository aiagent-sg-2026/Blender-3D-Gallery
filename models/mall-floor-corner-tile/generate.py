"""Create the P0 1.2 m corner tile and its 45-degree mitred trim pair.
Run in Blender background; refuses to overwrite existing source files.
"""
from pathlib import Path
import bpy
from mathutils import Vector

BASE = Path(__file__).resolve().parents[1]

def mat(name, rgb, metallic=0, roughness=.5):
    m = bpy.data.materials.new(name); m.use_nodes = True
    color = tuple((v/255/12.92 if v/255 <= .04045 else ((v/255+.055)/1.055)**2.4) for v in rgb)
    m.diffuse_color = (*color, 1)
    p = m.node_tree.nodes['Principled BSDF']; p.inputs['Base Color'].default_value = (*color,1)
    p.inputs['Metallic'].default_value = metallic; p.inputs['Roughness'].default_value = roughness
    return m

def box(name, loc, dims, material, parent):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True); o.data.materials.append(material); o.parent=parent
    return o

def prism(name, points, z0, z1, material, parent):
    n=len(points); verts=[(x,y,z0) for x,y in points]+[(x,y,z1) for x,y in points]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(obj);obj.data.materials.append(material);obj.parent=parent
    return obj

def point(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

def run(kind):
    folder=BASE/('mall-floor-corner-tile' if kind=='tile' else 'mall-floor-mitred-trim')
    slug=folder.name; source=folder/'sources'/f'{slug}.blend'
    if source.exists(): raise RuntimeError(f'Refusing to overwrite {source}')
    bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC'
    root=bpy.data.objects.new('ASSET_MallCornerFloorTile' if kind=='tile' else 'ASSET_MallMitredFloorTrim',None);s.collection.objects.link(root)
    support=mat('Warm grey grout',(125,126,115),roughness=.83); stone=mat('Ivory stone body',(211,205,187),roughness=.6)
    finish=mat('Honed ivory terrazzo original seed 421',(255,255,255),roughness=.32)
    image=bpy.data.images.load(str(BASE/'mall-floor-tile/textures/terrazzo-original.png'));image.pack()
    tex=finish.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image;finish.node_tree.links.new(tex.outputs['Color'],finish.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
    dark=mat('Dark trim support',(75,78,70),.25,.55);champagne=mat('Brushed champagne trim',(164,152,126),.6,.38)
    if kind=='tile':
        root['origin']='bottom centre';root['pitch_m']=1.2;root['corner']='outer edges +X and -Y (Blender)'
        box('Grout support',(0,0,.006),(1.2,1.2,.012),support,root)
        # Four independently editable slabs, with 4 mm centre grout and 2 mm outer grout.
        for x0,x1 in [(-.598,-.002),(.002,.58)]:
            for y0,y1 in [(-.58,-.002),(.002,.598)]:
                slab=box('Stone slab',((x0+x1)/2,(y0+y1)/2,.021),(x1-x0,y1-y0,.018),stone,root);slab.data.materials.append(finish)
                for poly in slab.data.polygons:
                    if poly.normal.z>.5: poly.material_index=1
                bevel=slab.modifiers.new('Eased edge','BEVEL');bevel.width=.0006;bevel.segments=2
        # Filled joints above the support; separate strips do not overlap the slabs.
        box('Centre grout X',(0,.009,.0205),(.004,1.178,.017),support,root)
        for xa,xb in [(-.598,-.002),(.002,.58)]:box('Centre grout Y',((xa+xb)/2,0,.0205),(xb-xa,.004,.017),support,root)
        box('Outer grout left',(-.599,.01,.0205),(.002,1.18,.017),support,root)
        box('Outer grout back',(-.009,.599,.0205),(1.178,.002,.017),support,root)
        box('Corner inlay right',(.59,.01,.021),(.02,1.18,.018),champagne,root)
        box('Corner inlay front',(0,-.59,.021),(1.2,.02,.018),champagne,root)
        target=(0,0,.015); scale=1.85; cam=(1.8,-2.2,2.4)
    else:
        root['origin']='top at finished floor height; centred on corner tile';root['corner']='outside +X and -Y; 45 degree join';root['width_m']=.06
        front=[(-.6,-.6),(-.6,-.66),(.66,-.66),(.6,-.6)]
        right=[(.6,.6),(.6,-.6),(.66,-.66),(.66,.6)]
        for label,pts in [('Front',front),('Right',right)]:
            prism(label+' support',pts,-.03,-.004,dark,root);prism(label+' cap',pts,-.004,0,champagne,root)
        target=(0,0,0); scale=2.15; cam=(1.9,-2.5,2.4)
    # Studio objects are excluded from the exported root.
    box('STUDIO floor',(0,0,-.041),(200,200,.02),mat('Studio background',(45,58,61),roughness=.9),None)
    for name,loc,energy in [('Key',(-2,-3,5),500),('Fill',(3,1,4),350),('Rim',(-1,3,4),250)]:
        bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name='STUDIO '+name;o.data.energy=energy;o.data.size=4;point(o,target)
    bpy.ops.object.camera_add(location=cam);s.camera=bpy.context.object;s.camera.data.type='ORTHO';s.camera.data.ortho_scale=scale;point(s.camera,target)
    s.world=bpy.data.worlds.new('Studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.4
    s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=s.render.resolution_y=720;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX'
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
    bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
    for obj in root.children_recursive:obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(folder/'exports'/f'{slug}.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_animations=False,export_extras=True,export_cameras=False,export_lights=False)
    s.render.filepath=str(folder/'previews'/f'{slug}.png');bpy.ops.render.render(write_still=True)

for k in ('tile','trim'):run(k)
