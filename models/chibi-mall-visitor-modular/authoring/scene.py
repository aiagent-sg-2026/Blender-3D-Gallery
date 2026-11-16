"""Blender entry point, including export-only from an independently edited master."""
import argparse
import sys
from pathlib import Path
import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from config import HEIGHT, FPS, CLIPS, PRESETS, BUDGET, PICKUP_PRODUCT_SIZE
from meshkit import PARTS, init_materials, round_surface
import head, hair, hair_bake, wardrobe, accessories, atlas, motion, studio
import guides as guide_tools

def collection(name):
    c=bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c); return c

def export(path):
    bpy.ops.object.select_all(action="DESELECT")
    rig=bpy.data.objects["Visitor_Rig"]; rig.select_set(True)
    for o in bpy.data.objects:
        if o.get("partSlot") or o.get("attachment"):o.select_set(True)
    bpy.context.view_layer.objects.active=rig
    with guide_tools.evaluated_hair(bpy.data.objects["Swept_hair"],bpy.data.collections["Editable hair guides"]):
        bpy.ops.export_scene.gltf(filepath=str(path),export_format="GLB",use_selection=True,
        export_yup=True,export_extras=True,export_apply=False,export_skins=True,export_morph=True,
        export_morph_normal=False,export_tangents=True,export_animations=True,export_animation_mode="NLA_TRACKS",
        export_merge_animation="NLA_TRACK",export_force_sampling=True,export_anim_slide_to_zero=True,
        export_optimize_animation_size=True,export_armature_object_remove=True,
        export_cameras=False,export_lights=False,export_image_format="AUTO")

def generate(out,quick,checkpoints):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc=bpy.context.scene; sc.name="GJH Visitor"; sc.render.fps=FPS; sc.frame_start=0; sc.frame_end=96
    art=collection("Character"); guides=collection("Editable hair guides"); stage=collection("Portrait studio")
    guides.hide_viewport=True; guides.hide_render=True
    atlas.make_atlas(out/"visitor-atlas.png")
    atlas.make_normal_atlas(out/"visitor-normal.png")
    tex=bpy.data.images.load(str(out/"visitor-atlas.png")); tex.name="Visitor colour atlas"; tex.pack()
    normal=bpy.data.images.load(str(out/"visitor-normal.png"));normal.name="Visitor normal atlas"
    normal.colorspace_settings.name="Non-Color";normal.pack()
    init_materials(tex,normal)
    rig=motion.make_rig(art)
    studio.setup(sc,stage)
    bpy.context.preferences.filepaths.save_version=0
    groups={}
    def finish(parts):
        result=[]
        for p in parts:
            label={"Mouth":"Face details","Eyes":"Face details","Hands":"Body"}.get(p.slot,p.slot)
            if label not in groups:
                groups[label]=bpy.data.collections.new(label);art.children.link(groups[label])
            result.append(p.finish(groups[label],rig))
        return result
    head.build()
    objects=finish(PARTS)
    groups["Hair"]=bpy.data.collections.new("Hair");art.children.link(groups["Hair"])
    wig,sculpt=hair.create(groups["Hair"],rig,guides)
    objects.append(wig)
    guide_tools.record_rest(guides)
    hair_bake.bake(wig,sculpt,normal,out/"visitor-normal.png",tex)
    if checkpoints:
        (out/"checkpoints").mkdir(exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(out/"checkpoints/02-head.blend"),copy=True,compress=True)
    first=len(PARTS)
    wardrobe.body();wardrobe.shirt();wardrobe.jeans();wardrobe.shoes();accessories.build()
    objects.extend(finish(PARTS[first:]))
    for obj in objects:
        if obj.name.startswith("Lacing_"):continue
        if obj.get("partSlot") in ("Shirt","Jeans","Shoes","Backpack"):
            # Spend the recovered bevel triangles on the hair's silhouette
            # and the rounded section of the individual posterior locks.
            budgets={"Crewneck_shirt":575,"Straight_denim":775,
                     "Daypack_shell":330,"Shoulder_straps":220,
                     "Sneaker_L":260,"Sneaker_R":260}
            budget=budgets.get(obj.name,sum(len(face.vertices)-2 for face in obj.data.polygons))
            round_surface(obj,budget,levels=2 if obj.get("partSlot")=="Jeans" else 1)
            if obj.get("partSlot")=="Shoes":
                sole=min(vertex.co.z for vertex in obj.data.vertices)
                for vertex in obj.data.vertices:vertex.co.z-=sole
    wardrobe.fit_lacing(objects)
    if checkpoints:
        bpy.ops.wm.save_as_mainfile(filepath=str(out/"checkpoints/03-wardrobe.blend"),copy=True,compress=True)
    if not quick:motion.write_actions(rig,objects)
    meta={}
    for name,(count,loop,frame) in CLIPS.items():
        m={"frames":count,"loop":loop,"reviewFrame":frame,"fps":FPS}
        if name in motion.GAIT:
            stride,duty,*_=motion.GAIT[name]
            m.update({"speedMps":stride/(count/FPS*duty),"stanceFraction":duty})
        if name=="pick_up":m.update({"contactFrame":36,"contactSocket":"Socket_Palm_R","testProductSizeM":list(PICKUP_PRODUCT_SIZE),
                                     "target":[motion.PICK[0],motion.PICK[2],-motion.PICK[1]]})
        if name=="sit":m.update({"seatHeightM":.164,"seatCenterZ":-.127,"seatDepthM":.20})
        meta[name]=m
    sc["clipInfo"]=meta; sc["expressionPresets"]=PRESETS
    sc["fps"]=FPS;sc["triangleRange"]=list(BUDGET)
    sc["surfaceMaps"]=["baseColor","normal"]
    sc["thinkingPose"]={name:[q.x,q.z,-q.y,q.w] for name,q in motion.make_pose("thinking",1).rotation.items()
                        if abs(q.w)<.999999}
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=="VIEW_3D":
                area.spaces.active.region_3d.view_rotation=sc.camera.rotation_euler.to_quaternion()
                area.spaces.active.region_3d.view_distance=2.35; area.spaces.active.region_3d.view_location=(0,0,.65)
                area.spaces.active.shading.color_type="TEXTURE"; area.spaces.active.overlay.show_overlays=False
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.preferences.filepaths.save_version=0
    tex.filepath="//visitor-atlas.png"
    normal.filepath="//visitor-normal.png"
    bpy.ops.wm.save_as_mainfile(filepath=str(out/"visitor.blend"),compress=True)
    export(out/"visitor.glb")

def assemble_saved(source,out):
    """Append the named authoring collections and reassemble them in a fresh scene."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    dest=bpy.context.scene
    with bpy.data.libraries.load(str(source),link=False) as (available,requested):
        requested.scenes=["GJH Visitor"]
    authored=requested.scenes[0]
    if authored is None:raise ValueError("The master is missing the GJH Visitor scene")
    for c in list(authored.collection.children):
        dest.collection.children.link(c)
    for k in authored.keys():dest[k]=authored[k]
    dest.camera=authored.camera;dest.world=authored.world;dest.render.fps=authored.render.fps
    dest.frame_start=authored.frame_start;dest.frame_end=authored.frame_end
    bpy.data.scenes.remove(authored);dest.name="GJH Visitor"
    bpy.context.view_layer.update();dest.frame_set(0)
    export(out/"visitor.glb")

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--export-only",action="store_true");parser.add_argument("--quick",action="store_true")
    parser.add_argument("--assemble",type=Path);parser.add_argument("--checkpoints",action="store_true")
    args=parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    args.out=args.out.resolve();args.out.mkdir(parents=True,exist_ok=True)
    if args.assemble:assemble_saved(args.assemble.resolve(),args.out)
    elif args.export_only:export(args.out/"visitor.glb")
    else:generate(args.out,args.quick,args.checkpoints)
