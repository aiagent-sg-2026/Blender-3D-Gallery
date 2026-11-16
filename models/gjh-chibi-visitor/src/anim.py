"""Twelve in-place clips. Each clip is one Blender action with two slots
(armature bones and face shape keys) pushed to same-named NLA tracks, which the
glTF exporter merges into one animation per clip.

Rotations are authored in the rest-pose armature axes, relative to the parent
bone, then conjugated into each bone's local space. Axis conventions (Blender):
  Rot(X, +a) tips an upward bone forward (nod down / lean forward);
  Rot(X, -a) swings a downward bone forward (arm or thigh raise);
  Rot(Z, +a) turns the head towards the character's left (+X);
  arm abduction: Rot(Y, -a) for the left arm, Rot(Y, +a) for the right arm.
"""
import math

import bpy
from mathutils import Quaternion, Vector

import config as C
import rig as R
from head import EXPRESSIONS

D = math.radians
X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))


def rot(axis, deg):
    return Quaternion(axis, D(deg))


def clamp(v, lo=-1.0, hi=1.0):
    return max(lo, min(hi, v))


def smooth(t):
    t = clamp(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


class Pose:
    def __init__(self):
        self.q = {}
        self.hips = Vector((0.0, 0.0, 0.0))

    def add(self, bone, q):
        self.q[bone] = q @ self.q.get(bone, Quaternion())
        return self


class Animator:
    def __init__(self, rig, face):
        self.rig = rig
        self.face_keys = face.data.shape_keys
        self.rest = {pb.name: pb.bone.matrix_local.to_quaternion() for pb in rig.pose.bones}
        self.rest3 = {pb.name: pb.bone.matrix_local.to_3x3() for pb in rig.pose.bones}
        hip0, knee0, ankle0 = (Vector(v) for v in (C.RIG_HIP_JOINT, C.RIG_KNEE, C.RIG_ANKLE))
        self.L1 = (knee0 - hip0).length
        self.L2 = (ankle0 - knee0).length
        self.t0 = math.atan2(-(knee0.y - hip0.y), -(knee0.z - hip0.z))
        self.s0 = math.atan2(-(ankle0.y - knee0.y), -(ankle0.z - knee0.z))
        self.clips = []

    # ------------------------------------------------------------ pose building
    def leg(self, pose, side, ankle_target, pitch_deg=0.0):
        """Two-bone IK in the sagittal plane; the foot keeps `pitch` to the ground."""
        f = 1.0 if side == "L" else -1.0
        hip = Vector(C.RIG_HIP_JOINT)
        hip.x *= f
        hip = hip + pose.hips
        tf = -(ankle_target.y - hip.y)
        td = -(ankle_target.z - hip.z)
        dist = min(math.hypot(tf, td), self.L1 + self.L2 - 1e-4)
        g = math.atan2(tf, td)
        a1 = math.acos(clamp((self.L1 ** 2 + dist ** 2 - self.L2 ** 2) / (2 * self.L1 * dist)))
        a2 = math.acos(clamp((self.L1 ** 2 + self.L2 ** 2 - dist ** 2) / (2 * self.L1 * self.L2)))
        thigh = g + a1
        shin = thigh - (math.pi - a2)
        # Sideways lean keeps the ankle over its target when the hips shift in x.
        rest_dx = (C.RIG_ANKLE[0] - C.RIG_HIP_JOINT[0]) * f
        lean = math.atan2((ankle_target.x - hip.x) - rest_dx, td)
        q_thigh = Quaternion(Y, -lean) @ Quaternion(X, -(thigh - self.t0))
        q_shin = Quaternion(X, -((shin - thigh) - (self.s0 - self.t0)))
        # The foot cancels everything above it so its world pitch is exact.
        q_foot = (q_thigh @ q_shin).inverted() @ Quaternion(X, D(pitch_deg))
        pose.add(f"thigh.{side}", q_thigh)
        pose.add(f"shin.{side}", q_shin)
        pose.add(f"foot.{side}", q_foot)
        return pose

    def ankle_lift(self, pitch_deg):
        """Ankle height needed so heel and toe stay above the floor at this pitch."""
        p = D(pitch_deg)
        ankle = Vector(C.RIG_ANKLE)
        heel = Vector((0.0, C.SHOE_CENTER_Y + C.SHOE_LENGTH / 2 - ankle.y, -ankle.z))
        toe = Vector((0.0, C.SHOE_CENTER_Y - C.SHOE_LENGTH / 2 - ankle.y, -ankle.z))
        low = min(pt.y * math.sin(p) + pt.z * math.cos(p) for pt in (heel, toe))
        return max(0.0, -(low + ankle.z))

    def planted(self, pose, side, dy=0.0, lift=0.0, pitch=0.0):
        f = 1.0 if side == "L" else -1.0
        ankle = Vector(C.RIG_ANKLE)
        target = Vector((ankle.x * f, ankle.y + dy, ankle.z + lift + self.ankle_lift(pitch)))
        return self.leg(pose, side, target, pitch)

    @staticmethod
    def arm(pose, side, forward=0.0, out=0.0, elbow=0.0, wave=0.0, wrist=0.0, twist=0.0, ftwist=0.0, htwist=0.0):
        sgn = -1.0 if side == "L" else 1.0
        # Raising an arm past 60 degrees also lifts the shoulder (clavicle).
        lift = 0.22 * max(0.0, out - 60.0) + 0.10 * max(0.0, forward - 60.0)
        if lift:
            pose.add(f"shoulder.{side}", rot(Y, lift * sgn))
            out -= lift
        pose.add(f"upper_arm.{side}", rot(Y, out * sgn) @ rot(X, -forward) @ rot(Z, twist * sgn))
        # wave bends the forearm in the body plane; ftwist turns it about its own axis.
        pose.add(f"forearm.{side}", rot(Y, wave * sgn) @ rot(X, -elbow) @ rot(Z, ftwist * sgn))
        pose.add(f"hand.{side}", rot(X, -wrist) @ rot(Z, htwist * sgn))
        return pose

    def base(self, hips=(0.0, 0.0, 0.0)):
        pose = Pose()
        pose.hips = Vector(hips)
        self.planted(pose, "L")
        self.planted(pose, "R")
        return pose

    # ------------------------------------------------------------ keying
    def apply(self, pose):
        for pb in self.rig.pose.bones:
            q = pose.q.get(pb.name)
            if q is None:
                pb.rotation_quaternion = Quaternion()
            else:
                r = self.rest[pb.name]
                pb.rotation_quaternion = r.inverted() @ q @ r
            pb.location = (0.0, 0.0, 0.0)
        self.rig.pose.bones["hips"].location = self.rest3["hips"].inverted() @ pose.hips

    def key_pose(self, frame, pose):
        self.apply(pose)
        for name in R.DEFORM:
            self.rig.pose.bones[name].keyframe_insert("rotation_quaternion", frame=frame)
        self.rig.pose.bones["hips"].keyframe_insert("location", frame=frame)

    def key_face(self, frame, values=None):
        values = values or {}
        for name in EXPRESSIONS:
            block = self.face_keys.key_blocks[name]
            block.value = values.get(name, 0.0)
            block.keyframe_insert("value", frame=frame)

    def clip(self, name, poses, faces, cyclic=False):
        """poses: [(frame, Pose)], faces: [(frame, {expression: value})]."""
        action = bpy.data.actions.new(name)
        action.use_fake_user = True
        self.rig.animation_data_create()
        self.face_keys.animation_data_create()
        self.rig.animation_data.action = action
        self.face_keys.animation_data.action = action
        for frame, pose in poses:
            self.key_pose(frame, pose)
        for frame, values in faces:
            self.key_face(frame, values)
        action.use_frame_range = True
        action.frame_start = poses[0][0]
        action.frame_end = poses[-1][0]
        action.use_cyclic = cyclic
        self.clips.append((name, action))
        self.rig.animation_data.action = None
        self.face_keys.animation_data.action = None
        return action

    def push_tracks(self):
        """One NLA track per clip on both the rig and the face keys (same name)."""
        for name, action in self.clips:
            for idb, kind in ((self.rig, "OBJECT"), (self.face_keys, "KEY")):
                slot = next(s for s in action.slots if s.target_id_type == kind)
                track = idb.animation_data.nla_tracks.new()
                track.name = name
                strip = track.strips.new(name, int(action.frame_start), action)
                strip.action_slot = slot


# ---------------------------------------------------------------- clips
def sampled(keys, build, step=1):
    """Interpolate parameter tuples between keyed frames (smoothstep) and build
    a pose for every `step` frames, so IK targets hold between keys."""
    poses = []
    first, last = keys[0][0], keys[-1][0]
    for frame in range(first, last + 1, step):
        for (f0, p0), (f1, p1) in zip(keys, keys[1:]):
            if f0 <= frame <= f1:
                t = smooth((frame - f0) / (f1 - f0)) if f1 > f0 else 0.0
                params = tuple(a + (b - a) * t for a, b in zip(p0, p1))
                break
        poses.append((frame, build(*params)))
    if poses[-1][0] != last:
        poses.append((last, build(*keys[-1][1])))
    return poses



def gait(anim, name, frames, stride, stance, lift, hips_z, bob, lean, arm_swing, elbow, face, step=1):
    poses = []
    for frame in range(0, frames + 1, step):
        t = frame / frames
        pose = Pose()
        # The hips only bob; twist lives in the spine so the IK feet stay exact.
        pose.hips = Vector((0.0, 0.0, hips_z - bob * math.cos(4 * math.pi * t)))
        # Most of the lean sits in the chest, so the tee does not fold onto the waistband.
        pose.add("spine", rot(X, lean * 0.25) @ rot(Z, 4.0 * math.sin(2 * math.pi * t)))
        pose.add("chest", rot(X, lean * 0.75) @ rot(Z, -6.0 * math.sin(2 * math.pi * t)))
        pose.add("head", rot(X, -lean * 0.3))
        for side, phase in (("L", t), ("R", (t + 0.5) % 1.0)):
            if phase < stance:
                s = phase / stance
                dy = -stride / 2 + stride * s                     # forward -> back at constant speed
                pitch = -8.0 * (1 - smooth(s / 0.2)) + 14.0 * smooth((s - 0.75) / 0.25)
                anim.planted(pose, side, dy=dy, pitch=pitch)
            else:
                u = (phase - stance) / (1 - stance)
                dy = stride / 2 - stride * smooth(u)
                pitch = 14.0 * (1 - smooth(u / 0.4)) - 8.0 * smooth((u - 0.6) / 0.4)
                anim.planted(pose, side, dy=dy, lift=lift * math.sin(math.pi * u), pitch=pitch)
            swing = -arm_swing * math.cos(2 * math.pi * phase)
            anim.arm(pose, side, forward=swing, out=6.0, elbow=elbow + max(0.0, swing) * 0.6)
        poses.append((frame, pose))
    return anim.clip(name, poses, [(0, face), (frames, face)], cyclic=True)


def build_clips(rig, face):
    anim = Animator(rig, face)
    rest = anim.base

    # Idle: breathing, weight shift, a glance and one blink.
    def idle_pose(breath, shift, look):
        p = rest((shift, 0.0, -0.003 * breath))
        p.add("spine", rot(X, -0.8 * breath))
        p.add("chest", rot(X, -1.4 * breath))
        p.add("head", rot(Z, look) @ rot(X, 1.5 * breath))
        anim.arm(p, "L", forward=1.5 * breath, out=1.0, elbow=4.0)
        anim.arm(p, "R", forward=1.5 * breath, out=1.0, elbow=4.0)
        return p
    anim.clip("Idle", sampled([(0, (0, 0, 0)), (22, (1, 0.004, 2)), (45, (0, 0.006, 6)), (68, (1, 0.002, 2)),
                               (90, (0, 0, 0))], idle_pose, step=3),
              [(0, {}), (56, {}), (59, {"blink": 1.0}), (63, {}), (90, {})], cyclic=True)

    gait(anim, "Walk", 32, stride=0.20, stance=0.56, lift=0.050, hips_z=-0.032, bob=0.008, lean=5.0,
         arm_swing=24.0, elbow=16.0, face={})
    gait(anim, "Run", 20, stride=0.30, stance=0.40, lift=0.090, hips_z=-0.058, bob=0.016, lean=20.0,
         arm_swing=55.0, elbow=80.0, face={})

    # Sit: lower onto a seat with the feet forward on the floor, then hold.
    def sit_pose(t):
        p = Pose()
        p.hips = Vector((0.0, 0.07 * t, -0.12 * t))
        ankle = Vector(C.RIG_ANKLE)
        for side, f in (("L", 1.0), ("R", -1.0)):
            anim.leg(p, side, Vector((ankle.x * f, ankle.y - 0.11 * t, ankle.z)))
        p.add("spine", rot(X, 6.0 * t))
        p.add("head", rot(X, -4.0 * t))
        anim.arm(p, "L", forward=38.0 * t, out=6.0 * t, elbow=34.0 * t)
        anim.arm(p, "R", forward=38.0 * t, out=6.0 * t, elbow=34.0 * t)
        return p
    anim.clip("Sit", sampled([(0, (0.0,)), (30, (1.0,)), (40, (1.0,))], sit_pose, step=2),
              [(0, {}), (40, {})])

    # Wave: upper arm out to the side, forearm up, palm forward, three waves.
    def wave_pose(up, wave):
        p = rest()
        p.add("chest", rot(Y, 3.0 * up))
        p.add("head", rot(Z, -4.0 * up) @ rot(Y, -4.0 * up))
        # Palm turned forward: the 90-degree turn is split between forearm and hand.
        # Upper arm well out to the side so the raised hand stays clear of the wide hair.
        anim.arm(p, "R", forward=38.0 * up, out=108.0 * up, elbow=6.0 * up, wave=(34.0 + wave) * up,
                 ftwist=-45.0 * up, htwist=-45.0 * up)
        anim.arm(p, "L", out=3.0, elbow=5.0)
        return p
    waves = [(0, wave_pose(0, 0)), (9, wave_pose(1, 0))]
    for i, frame in enumerate(range(14, 39, 5)):
        waves.append((frame, wave_pose(1, 10.0 if i % 2 == 0 else -22.0)))
    waves += [(41, wave_pose(1, 0)), (48, wave_pose(0, 0))]
    anim.clip("Wave", waves, [(0, {}), (7, {"happy": 1.0}), (42, {"happy": 1.0}), (48, {})])

    # Talk: small nods and a gesturing right hand, mouth cycling.
    def talk_pose(k):
        p = rest()
        p.add("head", rot(X, 3.0 * math.sin(k)) @ rot(Z, 4.0 * math.sin(k * 0.5)))
        p.add("chest", rot(Z, 2.0 * math.sin(k * 0.5)))
        anim.arm(p, "R", forward=22.0 + 8.0 * math.sin(k), out=8.0, elbow=58.0 + 12.0 * math.sin(k * 1.5))
        anim.arm(p, "L", forward=2.0, out=3.0, elbow=6.0)
        return p
    talk_faces = [(f, {"talk": v}) for f, v in ((0, 0.0), (6, 0.8), (12, 0.2), (18, 0.9), (24, 0.1), (30, 0.7),
                                                 (36, 0.0), (42, 0.85), (48, 0.25), (54, 0.6), (60, 0.0))]
    anim.clip("Talk", [(f, talk_pose(2 * math.pi * f / 60.0 * 2)) for f in range(0, 61, 10)], talk_faces,
              cyclic=True)

    # Shop / Browse: turn to one shelf and reach for an item, then the other side.
    def browse_pose(look, lean, reach_l, reach_r):
        p = rest((0.0, 0.0, -0.004 * lean))
        p.add("spine", rot(X, 6.0 * lean))
        p.add("chest", rot(Z, look * 0.35))
        p.add("head", rot(Z, look * 0.65) @ rot(X, 5.0 * lean))
        anim.arm(p, "L", forward=4.0 + 52.0 * reach_l, out=3.0 + 22.0 * reach_l, elbow=10.0 + 40.0 * reach_l)
        anim.arm(p, "R", forward=4.0 + 52.0 * reach_r, out=3.0 + 22.0 * reach_r, elbow=10.0 + 40.0 * reach_r)
        return p
    anim.clip("ShopBrowse", sampled([(0, (0, 0, 0, 0)), (16, (35, 1, 0, 0)), (26, (35, 1, 1, 0)), (36, (35, 1, 0, 0)),
                                     (52, (-35, 1, 0, 0)), (62, (-35, 1, 0, 1)), (72, (-35, 1, 0, 0)),
                                     (90, (0, 0, 0, 0))], browse_pose, step=2),
              [(0, {}), (40, {}), (43, {"blink": 1.0}), (46, {}), (90, {})], cyclic=True)

    # Pick Up: crouch, reach to the floor with the right hand, stand up holding it.
    def pick_pose(crouch, reach, hold):
        p = Pose()
        p.hips = Vector((0.0, 0.04 * crouch, -0.17 * crouch))
        anim.planted(p, "L")
        anim.planted(p, "R")
        p.add("spine", rot(X, 32.0 * crouch))
        p.add("chest", rot(X, 20.0 * crouch))
        p.add("head", rot(X, -10.0 * crouch))          # keep the chin up, eyes on the item
        anim.arm(p, "R", forward=40.0 * reach + 44.0 * hold, out=8.0, elbow=6.0 * reach + 72.0 * hold)
        anim.arm(p, "L", forward=20.0 * crouch, out=10.0 * crouch, elbow=20.0 * crouch)
        return p
    anim.clip("PickUp", sampled([(0, (0, 0, 0)), (14, (1, 1, 0)), (22, (1, 1, 0)), (36, (0.1, 0, 1)),
                                 (50, (0, 0, 0))], pick_pose, step=2),
              [(0, {}), (12, {}), (18, {"surprised": 1.0}), (26, {}), (34, {"happy": 1.0}), (44, {"happy": 1.0}),
               (50, {})])

    # Inspect: bring the held item up to the face and turn it over, thinking.
    def inspect_pose(up, turn):
        p = rest()
        p.add("head", rot(X, 10.0 * up) @ rot(Z, -12.0 * up))
        # The item is held up in front of the face, a forearm's length away.
        anim.arm(p, "R", forward=75.0 * up, out=6.0 * up, elbow=60.0 * up, wrist=turn, twist=turn * 0.5)
        anim.arm(p, "L", out=3.0, elbow=6.0)
        return p
    anim.clip("Inspect", [(0, inspect_pose(0, 0)), (15, inspect_pose(1, 0)), (30, inspect_pose(1, 25)),
                          (45, inspect_pose(1, -20)), (58, inspect_pose(1, 0)), (70, inspect_pose(0, 0))],
              [(0, {}), (14, {"thinking": 1.0}), (58, {"thinking": 1.0}), (70, {})])

    # Point: right arm straight out in front.
    def point_pose(t):
        p = rest()
        p.add("chest", rot(Z, 5.0 * t))
        p.add("head", rot(Z, -8.0 * t) @ rot(X, -3.0 * t))      # look along the pointing arm
        p.add("spine", rot(Z, 4.0 * t))
        anim.arm(p, "R", forward=88.0 * t, out=14.0 * t, elbow=2.0 * t, wrist=-4.0 * t)
        anim.arm(p, "L", out=3.0, elbow=6.0)
        return p
    anim.clip("Point", [(0, point_pose(0)), (10, point_pose(1)), (30, point_pose(1)), (40, point_pose(0))],
              [(0, {}), (8, {"surprised": 1.0}), (32, {"surprised": 1.0}), (40, {})])

    # Nod: two nods with a friendly face.
    def nod_pose(a):
        p = rest()
        p.add("neck", rot(X, a * 0.4))
        p.add("head", rot(X, a * 0.6))
        return p
    anim.clip("Nod", [(0, nod_pose(0)), (7, nod_pose(14)), (14, nod_pose(0)), (21, nod_pose(14)),
                      (30, nod_pose(0))], [(0, {}), (5, {"happy": 1.0}), (24, {"happy": 1.0}), (30, {})])

    # Cheer: both arms up with a little bounce, excited face.
    def cheer_pose(up, bounce):
        p = rest((0.0, 0.0, -0.025 * bounce))
        p.add("chest", rot(X, -4.0 * up))
        p.add("head", rot(X, -6.0 * up))
        for side in ("L", "R"):
            # A wide V: chibi arms are too short to clear the hair straight overhead.
            anim.arm(p, side, forward=20.0 * up, out=125.0 * up, elbow=15.0 * up, wave=20.0 * up)
        return p
    anim.clip("Cheer", sampled([(0, (0, 0)), (6, (0.3, 1)), (12, (1, 0)), (18, (0.85, 1)), (24, (1, 0)),
                                (32, (0.4, 0.5)), (40, (0, 0))], cheer_pose, step=2),
              [(0, {}), (8, {"excited": 1.0}), (30, {"excited": 1.0}), (40, {})])

    anim.push_tracks()
    return anim
