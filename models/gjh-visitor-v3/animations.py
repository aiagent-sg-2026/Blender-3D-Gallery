"""Author the 12 contract actions on the shared humanoid armature."""
import math
import bpy
from mathutils import Vector

# (name, frames, loops)
CLIPS = [('idle', 60, True), ('walk', 30, True), ('run', 22, True), ('turn_left', 30, False),
         ('turn_right', 30, False), ('sit_down', 30, False), ('stand_up', 30, False),
         ('pick_up', 36, False), ('carry', 30, True), ('wave', 60, False),
         ('point', 36, False), ('push_cart', 30, True)]
GROUNDED = {'walk', 'run', 'push_cart', 'sit_down', 'stand_up', 'pick_up', 'turn_left', 'turn_right'}


def smooth(t):
    return t * t * (3 - 2 * t)


def pose(clip, frame, duration, bones):
    """Set rotations for one frame; returns bone names to key."""
    phase = (frame - 1) / duration * math.tau
    p = (frame - 1) / duration
    keyed = {'Body'}
    for b in bones:
        b.rotation_mode = 'XYZ'
        b.rotation_euler = (0, 0, 0)
        b.location = (0, 0, 0)
    arms = {s: (bones[s + 'Shoulder'], bones[s + 'Elbow']) for s in ('Left', 'Right')}
    legs = {s: (bones[s + 'Hip'], bones[s + 'Knee']) for s in ('Left', 'Right')}
    for s in ('Left', 'Right'):
        keyed.update({s + n for n in ('Shoulder', 'Elbow', 'Hip', 'Knee')})
    if clip == 'idle':
        for s, (sh, el) in arms.items():
            sh.rotation_euler.x = .025 * math.sin(phase)
        bones['Spine'].rotation_euler.x = .015 * math.sin(phase)
        keyed.add('Spine')
    elif clip in ('walk', 'run', 'push_cart'):
        speed = {'walk': .36, 'run': .66, 'push_cart': .22}[clip]
        for s, sign in (('Left', 1), ('Right', -1)):
            swing = math.sin(phase) * sign
            sh, el = arms[s]
            hip, knee = legs[s]
            hip.rotation_euler.x = swing * speed
            knee.rotation_euler.x = max(0, -swing) * speed * 1.1
            sh.rotation_euler.x = -swing * speed if clip != 'push_cart' else -.85
            el.rotation_euler.x = -.2 if clip == 'walk' else (-.9 if clip == 'run' else -.75)
        if clip == 'run':
            bones['Spine'].rotation_euler.x = .12
            keyed.add('Spine')
    elif clip in ('turn_left', 'turn_right'):
        sign = 1 if clip == 'turn_left' else -1
        bones['Body'].rotation_euler.y = sign * smooth(p) * math.pi / 2
        step = math.sin(p * math.tau * 2) * .25 * math.sin(math.pi * p)
        legs['Left'][0].rotation_euler.x = step
        legs['Right'][0].rotation_euler.x = -step
        legs['Left'][1].rotation_euler.x = max(0, -step)
        legs['Right'][1].rotation_euler.x = max(0, step)
    elif clip in ('sit_down', 'stand_up'):
        a = smooth(p) if clip == 'sit_down' else 1 - smooth(p)
        for s in ('Left', 'Right'):
            legs[s][0].rotation_euler.x = -1.2 * a
            legs[s][1].rotation_euler.x = 1.15 * a
            arms[s][0].rotation_euler.x = -.25 * a
        bones['Spine'].rotation_euler.x = .05 * a
        keyed.add('Spine')
    elif clip == 'pick_up':
        a = math.sin(math.pi * p) ** .7
        bones['Spine'].rotation_euler.x = .75 * a
        keyed.add('Spine')
        for s in ('Left', 'Right'):
            legs[s][0].rotation_euler.x = -.55 * a
            legs[s][1].rotation_euler.x = .8 * a
        arms['Right'][0].rotation_euler.x = -.9 * a
        arms['Right'][1].rotation_euler.x = -.3 * a
        for i in range(4):
            bones['RightFinger' + str(i)].rotation_euler.x = .55 * a
            keyed.add('RightFinger' + str(i))
    elif clip == 'carry':
        for s, (sh, el) in arms.items():
            sh.rotation_euler.x = -.75
            el.rotation_euler.x = -1.25
        bones['Spine'].rotation_euler.x = .03 * math.sin(phase)
        keyed.add('Spine')
        for s in ('Left', 'Right'):
            for i in range(4):
                bones[s + 'Finger' + str(i)].rotation_euler.x = .6
                keyed.add(s + 'Finger' + str(i))
    elif clip == 'wave':
        a = min(1, math.sin(math.pi * p) * 2.5)
        arms['Right'][0].rotation_euler.x = -2.4 * a
        arms['Right'][1].rotation_euler.x = (-.5 + .45 * math.sin(phase * 3)) * a
    elif clip == 'point':
        a = min(1, math.sin(math.pi * p) * 2.2)
        arms['Right'][0].rotation_euler.x = -1.5 * a
        arms['Right'][1].rotation_euler.x = -.1 * a
        for i in (1, 2, 3):
            bones['RightFinger' + str(i)].rotation_euler.x = 1.1 * a
            keyed.add('RightFinger' + str(i))
        bones['Spine'].rotation_euler.y = -.15 * a
        keyed.add('Spine')
    return keyed


def build_animations(scene, rig, shoes):
    rig.animation_data_create()
    bones = rig.pose.bones
    scene.render.fps = 30
    for clip, duration, loops in CLIPS:
        for track in rig.animation_data.nla_tracks:
            track.mute = True
        action = bpy.data.actions.new(clip)
        rig.animation_data.action = action
        frames = list(range(1, duration + 1, 3)) + [duration + 1]
        if clip in GROUNDED:
            frames = list(range(1, duration + 2))
        for frame in frames:
            keyed = pose(clip, frame, duration, bones)
            for name in keyed:
                bones[name].keyframe_insert(data_path='rotation_euler', frame=frame)
        if clip in GROUNDED:
            # Pin the lowest evaluated shoe vertex to the floor on every frame.
            for frame in range(1, duration + 2):
                scene.frame_set(frame)
                depsgraph = bpy.context.evaluated_depsgraph_get()
                floor = math.inf
                for obj in shoes:
                    evaluated = obj.evaluated_get(depsgraph)
                    mesh = evaluated.to_mesh()
                    floor = min(floor, min((evaluated.matrix_world @ v.co).z for v in mesh.vertices))
                    evaluated.to_mesh_clear()
                body = bones['Body']
                body.location += body.bone.matrix_local.to_3x3().inverted() @ Vector((0, 0, -floor))
                body.keyframe_insert(data_path='location', frame=frame)
        rig.animation_data.action = None
        track = rig.animation_data.nla_tracks.new()
        track.name = clip
        track.strips.new(clip, 1, action)
    for track in rig.animation_data.nla_tracks:
        track.mute = track.name != 'idle'
    scene.frame_set(1)
