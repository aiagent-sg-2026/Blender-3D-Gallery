"""Author the 12 contract actions on the MPFB game_engine skeleton.

Rotations are written about armature-space anatomical axes (X = character's left, Y = back,
Z = up; the character faces -Y) and converted into each bone's rest frame, so the same pose
code works regardless of MPFB bone roll.
"""
import math
import bpy
from mathutils import Quaternion, Vector

# (name, frames, loops)
CLIPS = [('idle', 60, True), ('walk', 30, True), ('run', 22, True), ('turn_left', 30, False),
         ('turn_right', 30, False), ('sit_down', 30, False), ('stand_up', 30, False),
         ('pick_up', 36, False), ('carry', 30, True), ('wave', 60, False),
         ('point', 36, False), ('push_cart', 30, True)]
GROUNDED = {'walk', 'run', 'push_cart', 'sit_down', 'stand_up', 'pick_up', 'turn_left', 'turn_right'}
X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
FINGERS = ('index', 'middle', 'ring', 'pinky')
RELAX = .62      # brings the modelling A-pose arms down beside the body


def smooth(t):
    return t * t * (3 - 2 * t)


class Pose:
    def __init__(self, rig):
        self.rig = rig
        self.ops = {}
        self.curl_axis = {}
        bones = rig.data.bones
        for side in ('l', 'r'):
            hand = bones[f'hand_{side}']
            palm = bones[f'thumb_01_{side}'].head_local - hand.head_local
            axis_h = (hand.tail_local - hand.head_local).normalized()
            palm = (palm - axis_h * palm.dot(axis_h)).normalized()
            for f in FINGERS + ('thumb',):
                for j in ('01', '02', '03'):
                    b = bones[f'{f}_{j}_{side}']
                    a = b.matrix_local.to_3x3().col[0].normalized()
                    tip = b.tail_local - b.head_local
                    moved = Quaternion(a, .3) @ tip - tip
                    self.curl_axis[b.name] = a if moved.dot(palm) > 0 else -a

    def flex(self, side, angle):
        """Bend (positive) or straighten (negative) the elbow in its own rest hinge plane."""
        bones = self.rig.data.bones
        u = (bones[f'upperarm_{side}'].tail_local - bones[f'upperarm_{side}'].head_local).normalized()
        f = (bones[f'lowerarm_{side}'].tail_local - bones[f'lowerarm_{side}'].head_local).normalized()
        self.ops.setdefault(f'lowerarm_{side}', []).append((u.cross(f).normalized(), angle))

    def add(self, bone, axis, angle):
        self.ops.setdefault(bone, []).append((axis, angle))

    def curl(self, side, amount, fingers=FINGERS):
        for f in fingers:
            for j in ('01', '02', '03'):
                name = f'{f}_{j}_{side}'
                self.add(name, self.curl_axis[name], amount * (.8 if j == '01' else 1.0))

    def lean(self, angle, axis=X):
        for name, share in (('spine_01', .3), ('spine_02', .35), ('spine_03', .35)):
            self.add(name, axis, angle * share)

    def apply(self):
        for pb in self.rig.pose.bones:
            pb.rotation_mode = 'QUATERNION'
            pb.rotation_quaternion = (1, 0, 0, 0)
            pb.location = (0, 0, 0)
        for name, items in self.ops.items():
            pb = self.rig.pose.bones[name]
            to_local = pb.bone.matrix_local.to_3x3().inverted()
            q = Quaternion()
            for axis, angle in items:
                q = Quaternion((to_local @ axis).normalized(), angle) @ q
            pb.rotation_quaternion = q


STRAIGHTEN = .6  # the MPFB rest pose bends the elbows forward; relax them beside the body


def relax_arms(p, keep=()):
    for side, sign in (('l', 1), ('r', -1)):
        if side not in keep:
            p.add(f'upperarm_{side}', Y, sign * RELAX)
            p.flex(side, -STRAIGHTEN)


def gait(p, phase, speed, knee=1.1):
    for side, sign in (('l', 1), ('r', -1)):
        swing = math.sin(phase) * sign
        p.add(f'thigh_{side}', X, swing * speed)
        p.add(f'calf_{side}', X, max(0.0, -swing) * speed * knee + .05)


def pose(rig, clip, frame, duration):
    phase = (frame - 1) / duration * math.tau
    t = (frame - 1) / duration
    p = Pose(rig)
    if clip == 'idle':
        relax_arms(p)
        p.add('spine_03', X, .02 * math.sin(phase))
        p.add('neck_01', X, -.015 * math.sin(phase))
        for side in ('l', 'r'):
            p.flex(side, .12)
            p.curl(side, .25)
    elif clip in ('walk', 'run'):
        speed = .42 if clip == 'walk' else .75
        relax_arms(p)
        gait(p, phase, speed, 1.2 if clip == 'walk' else 1.6)
        for side, sign in (('l', 1), ('r', -1)):
            p.add(f'upperarm_{side}', X, -math.sin(phase) * sign * speed * .9)
            p.flex(side, .25 if clip == 'walk' else 1.2)
            p.curl(side, .35 if clip == 'walk' else .8)
        p.lean(.03 if clip == 'walk' else .16)
        p.add('pelvis', Z, .05 * math.sin(phase))
    elif clip == 'push_cart':
        gait(p, phase, .26)
        relax_arms(p)
        for side in ('l', 'r'):
            p.add(f'upperarm_{side}', X, -.95)
            p.flex(side, .55)
            p.curl(side, .9)
        p.lean(.14)
    elif clip in ('turn_left', 'turn_right'):
        sign = 1 if clip == 'turn_left' else -1
        relax_arms(p)
        p.add('Root', Z, sign * smooth(t) * math.pi / 2)
        step = math.sin(t * math.tau * 2) * .22 * math.sin(math.pi * t)
        for side, s in (('l', 1), ('r', -1)):
            p.add(f'thigh_{side}', X, s * step)
            p.add(f'calf_{side}', X, max(0.0, -s * step) * 1.4)
            p.curl(side, .25)
        p.add('spine_03', Z, sign * .12 * math.sin(math.pi * t))
    elif clip in ('sit_down', 'stand_up'):
        a = smooth(t) if clip == 'sit_down' else 1 - smooth(t)
        relax_arms(p)
        for side in ('l', 'r'):
            p.add(f'thigh_{side}', X, -1.45 * a)
            p.add(f'calf_{side}', X, 1.45 * a)
            p.add(f'foot_{side}', X, -.05 * a)
            p.add(f'upperarm_{side}', X, -.35 * a)
            p.flex(side, .5 * a)
            p.curl(side, .3)
        p.lean(.12 * a)
    elif clip == 'pick_up':
        a = math.sin(math.pi * t) ** .8
        relax_arms(p)
        p.lean(.85 * a)
        p.add('neck_01', X, -.25 * a)
        for side in ('l', 'r'):
            p.add(f'thigh_{side}', X, -.75 * a)
            p.add(f'calf_{side}', X, 1.2 * a)
            p.add(f'foot_{side}', X, -.35 * a)
        p.add('upperarm_r', X, -1.0 * a)
        p.flex('r', .2 * a)
        p.curl('r', .2 + 1.0 * max(0.0, (t - .35) / .3) if t < .65 else 1.2)
        p.add('upperarm_l', X, -.3 * a)
        p.curl('l', .3)
    elif clip == 'carry':
        relax_arms(p)
        for side in ('l', 'r'):
            p.add(f'upperarm_{side}', X, -.45)
            p.flex(side, 1.35)
            p.curl(side, .9)
        p.add('spine_03', X, .02 * math.sin(phase))
    elif clip == 'wave':
        a = min(1.0, math.sin(math.pi * t) * 2.5)
        relax_arms(p, keep=('r',))
        p.add('upperarm_r', Y, 2.2 * a)
        p.add('upperarm_r', X, -.25 * a)
        p.flex('r', .55 * a)
        p.add('lowerarm_r', Y, .38 * math.sin(phase * 3) * a)
        p.curl('l', .3)
        p.add('spine_03', Y, -.04 * a)
    elif clip == 'point':
        a = min(1.0, math.sin(math.pi * t) * 2.2)
        relax_arms(p)
        p.add('upperarm_r', X, -1.45 * a)
        p.add('upperarm_r', Z, .2 * a)
        p.flex('r', .05 * a)
        p.curl('r', 1.3 * a, fingers=('middle', 'ring', 'pinky'))
        p.curl('r', .5 * a, fingers=('thumb',))
        p.curl('l', .3)
        p.add('spine_03', Z, -.12 * a)
        p.add('head', Z, -.15 * a)
    p.apply()


def build_animations(scene, rig, shoes):
    rig.animation_data_create()
    bones = rig.pose.bones
    scene.render.fps = 30
    for clip, duration, loops in CLIPS:
        for track in rig.animation_data.nla_tracks:
            track.mute = True
        action = bpy.data.actions.new(clip)
        rig.animation_data.action = action
        frames = list(range(1, duration + 2)) if clip in GROUNDED else list(range(1, duration + 1, 2)) + [duration + 1]
        for frame in frames:
            pose(rig, clip, frame, duration)
            for pb in bones:
                pb.keyframe_insert(data_path='rotation_quaternion', frame=frame)
            bones['Root'].keyframe_insert(data_path='location', frame=frame)
        if clip in GROUNDED:
            # Pin the lowest evaluated shoe vertex to the floor on every frame.
            root = bones['Root']
            to_local = root.bone.matrix_local.to_3x3().inverted()
            for frame in frames:
                scene.frame_set(frame)
                depsgraph = bpy.context.evaluated_depsgraph_get()
                floor = math.inf
                for obj in shoes:
                    evaluated = obj.evaluated_get(depsgraph)
                    mesh = evaluated.to_mesh()
                    floor = min(floor, min((evaluated.matrix_world @ v.co).z for v in mesh.vertices))
                    evaluated.to_mesh_clear()
                root.location = root.location + to_local @ Vector((0, 0, -floor))
                root.keyframe_insert(data_path='location', frame=frame)
        rig.animation_data.action = None
        track = rig.animation_data.nla_tracks.new()
        track.name = clip
        track.strips.new(clip, 1, action)
    for track in rig.animation_data.nla_tracks:
        track.mute = track.name != 'idle'
    scene.frame_set(1)
