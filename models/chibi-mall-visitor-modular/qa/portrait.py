"""Render the final binary through Blender's glTF importer and Cycles."""
import sys
import json
import struct
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"authoring"))
from studio import setup

args=sys.argv[sys.argv.index("--")+1:];source,out=map(Path,args[:2])
expression=args[2] if len(args)>2 else "portrait"

if source.suffix.lower()==".blend":
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    presets=bpy.context.scene["expressionPresets"].to_dict()
    for c in bpy.data.collections:
        if c.name=="Portrait studio":c.hide_render=True
else:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(source))
    data=source.read_bytes();document=json.loads(data[20:20+struct.unpack_from("<I",data,12)[0]])
    presets=document["scenes"][document.get("scene",0)]["extras"]["expressionPresets"]
weights=presets[expression] if expression!="portrait" else {k:v for k,v in presets["happy"].items() if not k.startswith("blink_")}
sc=bpy.context.scene
# Start from the imported bind pose; the portrait uses the open-eyed smile in the large quarter view.
for obj in sc.objects:
    if obj.animation_data:
        obj.animation_data.action=None
        for track in obj.animation_data.nla_tracks:track.mute=True
    if obj.type=="ARMATURE":
        from mathutils import Matrix
        for b in obj.pose.bones:b.matrix_basis=Matrix.Identity(4)
    if obj.type=="MESH" and obj.data.shape_keys:
        sk=obj.data.shape_keys
        if sk.animation_data:
            sk.animation_data.action=None
            for track in sk.animation_data.nla_tracks:track.mute=True
        for key in sk.key_blocks:
            key.value=weights.get(key.name,0.)
if expression=="thinking":
    from motion import make_pose,BIND,IDENT
    pose=make_pose("thinking",1)
    arm=next(o for o in sc.objects if o.type=="ARMATURE")
    for b in arm.pose.bones:
        n=b.name;parent=BIND[n][2]
        bind=(arm.matrix_world@b.bone.matrix_local).to_quaternion()
        b.rotation_quaternion=bind.inverted()@pose.rotation.get(parent,IDENT).inverted()@pose.rotation[n]@bind
coll=bpy.data.collections.new("Portrait studio");sc.collection.children.link(coll)
setup(sc,coll)
sc.render.filepath=str(out);bpy.ops.render.render(write_still=True)

