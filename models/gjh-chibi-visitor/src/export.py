"""GLB export, source .blend, and preview renders (turntable, expressions, clips)."""
import math
import os

import bpy
from mathutils import Vector

import render
from head import EXPRESSIONS


def export_glb(path, objects, rig):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in list(objects.values()) + [rig]:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = rig
    enable_tracks(rig, objects["Face"])
    for pb in rig.pose.bones:
        pb.location = (0.0, 0.0, 0.0)
        pb.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
    bpy.ops.export_scene.gltf(
        filepath=path,
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_apply=False,
        export_texcoords=True,
        export_normals=True,
        export_tangents=False,
        export_materials="EXPORT",
        export_image_format="AUTO",
        export_cameras=False,
        export_lights=False,
        export_extras=False,
        export_skins=True,
        export_def_bones=False,
        export_influence_nb=4,
        export_morph=True,
        export_morph_normal=False,
        export_morph_animation=True,
        export_animations=True,
        export_animation_mode="NLA_TRACKS",
        export_force_sampling=True,
        export_optimize_animation_size=True,
        export_reset_pose_bones=True,
        export_rest_position_armature=True,
        export_anim_single_armature=True,
    )
    return path


def save_blend(path):
    bpy.context.preferences.filepaths.save_version = 0     # no .blend1 backup next to the source
    bpy.ops.wm.save_as_mainfile(filepath=path, compress=True, copy=True)
    return path


# ------------------------------------------------------------------ previews
def set_clip(rig, face, name, frame):
    """Show one clip at one frame by making its action the active one.

    NLA evaluation is switched off while inspecting: muting tracks does not
    re-tag the depsgraph reliably, which made pose reads lag a clip behind.
    """
    action = bpy.data.actions[name]
    for idb, kind in ((rig, "OBJECT"), (face.data.shape_keys, "KEY")):
        data = idb.animation_data
        data.use_nla = False
        data.action = action
        data.action_slot = next(s for s in action.slots if s.target_id_type == kind)
    bpy.context.scene.frame_set(frame)


def rest_pose(rig, face):
    for idb in (rig, face.data.shape_keys):
        if idb.animation_data:
            idb.animation_data.action = None
            idb.animation_data.use_nla = False
    bpy.context.scene.frame_set(0)
    for pb in rig.pose.bones:
        pb.location = (0.0, 0.0, 0.0)
        pb.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
    for name in EXPRESSIONS:
        face.data.shape_keys.key_blocks[name].value = 0.0
    bpy.context.view_layer.update()


def enable_tracks(rig, face):
    """Before export: no active action, NLA tracks on (one per clip)."""
    for idb in (rig, face.data.shape_keys):
        idb.animation_data.action = None
        idb.animation_data.use_nla = True
        for track in idb.animation_data.nla_tracks:
            track.mute = False


def turntable(out_dir, size=(520, 720), steps=8):
    render.setup_studio()
    paths = []
    for i in range(steps):
        angle = 2 * math.pi * i / steps
        loc = Vector((math.sin(angle) * 3.6, -math.cos(angle) * 3.6, 1.05))
        render.camera("QA_Camera", loc, render.look_at_rotation(loc, (0.0, 0.0, 0.64)), lens=62.0)
        paths.append(render.render(os.path.join(out_dir, f"turntable-{i * 45:03d}.png"), "BLENDER_EEVEE", size))
    return paths


def expression_shots(out_dir, face, size=(420, 420)):
    render.setup_studio()
    paths = []
    loc = Vector((0.0, -2.2, 1.0))
    render.camera("QA_Camera", loc, render.look_at_rotation(loc, (0.0, 0.0, 1.0)), lens=120.0)
    keys = face.data.shape_keys.key_blocks
    for name in ["default"] + EXPRESSIONS:
        for other in EXPRESSIONS:
            keys[other].value = 1.0 if other == name else 0.0
        paths.append(render.render(os.path.join(out_dir, f"expression-{name}.png"), "BLENDER_EEVEE", size))
    for other in EXPRESSIONS:
        keys[other].value = 0.0
    return paths


def clip_shots(out_dir, rig, face, clips, size=(420, 560)):
    render.setup_studio()
    paths = []
    # A more side-on three-quarter camera shows strides, reaches and leans.
    loc = Vector((-2.75, -2.45, 1.0))
    render.camera("QA_Camera", loc, render.look_at_rotation(loc, (0.0, 0.0, 0.62)), lens=62.0)
    for name, action in clips:
        mid = int((action.frame_start + action.frame_end) / 2)
        frame = {"Walk": 0, "Run": 7, "Wave": 19, "Cheer": 12, "PickUp": 16, "Sit": 40, "Inspect": 30,
                 "Point": 20, "ShopBrowse": 26, "Nod": 7}.get(name, mid)
        set_clip(rig, face, name, frame)
        paths.append(render.render(os.path.join(out_dir, f"clip-{name}.png"), "BLENDER_EEVEE", size))
    rest_pose(rig, face)
    return paths


def thumbnail(path, size=(640, 800)):
    render.setup_studio()
    loc = Vector((-1.25, -3.05, 1.10))
    render.camera("QA_Camera", loc, render.look_at_rotation(loc, (0.0, 0.0, 0.66)), lens=80.0)
    return render.render(path, "BLENDER_EEVEE", size, samples=64)
