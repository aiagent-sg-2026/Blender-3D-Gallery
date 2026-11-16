"""Armature (20 deform bones + 3 sockets) and code-computed skin weights.

Weights are a function of each vertex's skin tag (set when the part was
built) and its rest position, so neighbouring parts (sleeve and arm, jeans
leg and cuff) get identical weights where they meet and move together.
"""
import bpy
from mathutils import Vector

import config as C
from mesh import smoothstep

DEFORM = [
    "root", "hips", "spine", "chest", "neck", "head",
    "shoulder.L", "upper_arm.L", "forearm.L", "hand.L",
    "shoulder.R", "upper_arm.R", "forearm.R", "hand.R",
    "thigh.L", "shin.L", "foot.L", "thigh.R", "shin.R", "foot.R",
]
SOCKETS = ["SOCKET_Back", "SOCKET_Wrist_L", "SOCKET_Hand_R"]


def joints():
    """Rest joint positions for the left side (mirrored for the right)."""
    sh, el, wr, tip = (Vector(p) for p in (C.SHOULDER_JOINT, C.ELBOW, C.WRIST, C.FINGER_TIP))
    return {
        "root": Vector((0.0, 0.0, 0.0)),
        "hips": Vector(C.RIG_HIPS),
        "spine": Vector(C.RIG_SPINE),
        "chest": Vector(C.RIG_CHEST),
        "neck": Vector(C.RIG_NECK),
        "head": Vector(C.RIG_HEAD),
        "head_end": Vector(C.RIG_HEAD_END),
        "clavicle": Vector(C.RIG_CLAVICLE),
        "shoulder": sh, "elbow": el, "wrist": wr, "hand_end": wr.lerp(tip, 0.75),
        "hip": Vector(C.RIG_HIP_JOINT), "knee": Vector(C.RIG_KNEE),
        "ankle": Vector(C.RIG_ANKLE), "toe": Vector(C.RIG_TOE),
    }


def mirror_x(v):
    return Vector((-v.x, v.y, v.z))


def build_armature(collection):
    data = bpy.data.armatures.new("GJHChibiVisitorRig")
    rig = bpy.data.objects.new("GJHChibiVisitorRig", data)
    collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    J = joints()
    eb = data.edit_bones

    def bone(name, head, tail, parent=None, connect=False, deform=True, roll=0.0):
        b = eb.new(name)
        b.head, b.tail = head, tail
        b.roll = roll
        if parent:
            b.parent = eb[parent]
            b.use_connect = connect
        b.use_deform = deform
        return b

    bone("root", J["root"], J["root"] + Vector((0.0, 0.0, 0.12)))
    bone("hips", J["hips"], J["spine"], "root")
    bone("spine", J["spine"], J["chest"], "hips", True)
    bone("chest", J["chest"], J["neck"], "spine", True)
    bone("neck", J["neck"], J["head"], "chest", True)
    bone("head", J["head"], J["head_end"], "neck", True)
    for side, f in (("L", lambda v: v), ("R", mirror_x)):
        bone(f"shoulder.{side}", f(J["clavicle"]), f(J["shoulder"]), "chest")
        bone(f"upper_arm.{side}", f(J["shoulder"]), f(J["elbow"]), f"shoulder.{side}", True)
        bone(f"forearm.{side}", f(J["elbow"]), f(J["wrist"]), f"upper_arm.{side}", True)
        bone(f"hand.{side}", f(J["wrist"]), f(J["hand_end"]), f"forearm.{side}", True)
        bone(f"thigh.{side}", f(J["hip"]), f(J["knee"]), "hips")
        bone(f"shin.{side}", f(J["knee"]), f(J["ankle"]), f"thigh.{side}", True)
        bone(f"foot.{side}", f(J["ankle"]), f(J["toe"]), f"shin.{side}", True)
    pack = Vector(C.PACK_CENTER)
    bone("SOCKET_Back", pack, pack + Vector((0.0, 0.08, 0.0)), "chest", deform=False)
    wrist = J["elbow"].lerp(J["wrist"], (C.WATCH_Z - J["elbow"].z) / (J["wrist"].z - J["elbow"].z))
    bone("SOCKET_Wrist_L", wrist, wrist + Vector((0.06, -0.045, 0.0)), "forearm.L", deform=False)
    palm = mirror_x(J["wrist"].lerp(J["hand_end"], 0.55))
    bone("SOCKET_Hand_R", palm, palm + Vector((0.0, -0.06, 0.0)), "hand.R", deform=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    for pb in rig.pose.bones:
        pb.rotation_mode = "QUATERNION"
    return rig


# ------------------------------------------------------------------ weights
def segment_t(p, a, b):
    ab = b - a
    return max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))


def blend(weights, a, b, t):
    """Split weight between bones a (t=0) and b (t=1)."""
    if t <= 0.0:
        weights[a] = weights.get(a, 0.0) + 1.0
    elif t >= 1.0:
        weights[b] = weights.get(b, 0.0) + 1.0
    else:
        weights[a] = weights.get(a, 0.0) + (1.0 - t)
        weights[b] = weights.get(b, 0.0) + t
    return weights


def chain_blend(z, names, bounds, widths):
    """Weights along a vertical chain: names[i] below bounds[i], blended across it."""
    for i, (b, w) in enumerate(zip(bounds, widths)):
        if z < b - w:
            return {names[i]: 1.0}
        if z <= b + w:
            return blend({}, names[i], names[i + 1], smoothstep(b - w, b + w, z))
    return {names[-1]: 1.0}


def spine_weights(p):
    """Torso chain by height, with the upper tee corners following the shoulders."""
    w = chain_blend(p.z, ["hips", "spine", "chest", "neck", "head"],
                    [C.RIG_SPINE[2], C.RIG_CHEST[2], C.RIG_NECK[2] + 0.01, C.RIG_HEAD[2] + 0.04],
                    [0.035, 0.035, 0.025, 0.02])
    side = "L" if p.x >= 0 else "R"
    # The front of the hem rests on the thighs, so sitting lifts it over the lap
    # instead of letting the jeans push through it.
    lap = smoothstep(0.48, 0.44, p.z) * smoothstep(-0.03, -0.09, p.y) * 0.6
    if lap > 0.0:
        # Shared smoothly between both thighs across the centre (no notch).
        left = 0.5 + 0.5 * max(-1.0, min(1.0, p.x / 0.05))
        w = {k: v * (1.0 - lap) for k, v in w.items()}
        w["thigh.L"] = w.get("thigh.L", 0.0) + lap * left
        w["thigh.R"] = w.get("thigh.R", 0.0) + lap * (1.0 - left)
    shoulder = smoothstep(0.06, 0.13, abs(p.x)) * smoothstep(0.61, 0.70, p.z) * 0.75
    if shoulder > 0.0:
        w = {k: v * (1.0 - shoulder) for k, v in w.items()}
        w[f"shoulder.{side}"] = w.get(f"shoulder.{side}", 0.0) + shoulder
    return w


def arm_weights(p, side):
    J = joints()
    f = (lambda v: v) if side == "L" else mirror_x
    sh, el, wr, he = f(J["shoulder"]), f(J["elbow"]), f(J["wrist"]), f(J["hand_end"])
    # Arc-length position along shoulder -> elbow -> wrist -> hand end.
    l1, l2 = (el - sh).length, (wr - el).length
    candidates = []
    for a, b, start, length in ((sh, el, 0.0, l1), (el, wr, l1, l2), (wr, he, l1 + l2, (he - wr).length)):
        t = segment_t(p, a, b)
        candidates.append(((p - a.lerp(b, t)).length, start + t * length))
    s = min(candidates)[1]
    # Around the shoulder joint (sleeve root, top of the arm) the shoulder and
    # upper arm share a wide 7 cm blend so raising the arm spreads the stretch.
    above = (p - sh).dot((sh - el).normalized())
    w = {}
    if above > -0.035:
        return blend(w, f"upper_arm.{side}", f"shoulder.{side}", smoothstep(-0.035, 0.035, above))
    if s < l1 + l2 - 0.012:
        return blend(w, f"upper_arm.{side}", f"forearm.{side}", smoothstep(l1 - 0.06, l1 + 0.045, s))
    return blend(w, f"forearm.{side}", f"hand.{side}", smoothstep(l1 + l2 - 0.012, l1 + l2 + 0.012, s))


def leg_weights(p, side):
    J = joints()
    f = (lambda v: v) if side == "L" else mirror_x
    knee_z = f(J["knee"]).z
    hip_z = f(J["hip"]).z
    w = blend({}, f"thigh.{side}", f"shin.{side}", smoothstep(knee_z + 0.07, knee_z - 0.07, p.z))
    top = smoothstep(hip_z - 0.07, hip_z, p.z)
    if top > 0.0:
        w = {k: v * (1.0 - top) for k, v in w.items()}
        w["hips"] = w.get("hips", 0.0) + top
    # The rolled cuff rests on the shoe: its lower edge partly follows the foot,
    # so a forward-tilted shin cannot push the cuff through the floor.
    low = smoothstep(C.CUFF[1], C.CUFF[0], p.z) * 0.5
    if low > 0.0:
        w = {k: v * (1.0 - low) for k, v in w.items()}
        w[f"foot.{side}"] = w.get(f"foot.{side}", 0.0) + low
    return w


def hips_weights(p):
    side = "L" if p.x >= 0 else "R"
    J = joints()
    leg = smoothstep(J["hip"].z - 0.01, J["hip"].z - 0.07, p.z) * smoothstep(0.0, 0.05, abs(p.x))
    return blend({}, "hips", f"thigh.{side}", leg * 0.5)


def foot_weights(p, side):
    J = joints()
    top = smoothstep(J["ankle"].z + 0.005, J["ankle"].z + 0.045, p.z)
    return blend({}, f"foot.{side}", f"shin.{side}", top * 0.5)


def strap_weights(p, side):
    J = joints()
    over = smoothstep(J["clavicle"].z - 0.02, J["shoulder"].z + 0.04, p.z) * smoothstep(0.05, 0.11, abs(p.x))
    return blend({}, "chest", f"shoulder.{side}", over * 0.35)


def weights_for(tag, p):
    if tag in ("head",):
        return {"head": 1.0}
    if tag == "spine":
        return spine_weights(p)
    if tag == "hips":
        return hips_weights(p)
    if tag == "chest":
        return {"chest": 1.0}
    name, _, side = tag.partition(".")
    if name == "arm":
        return arm_weights(p, side)
    if name == "leg":
        return leg_weights(p, side)
    if name == "foot":
        return foot_weights(p, side)
    if name == "foot_rigid":
        return {f"foot.{side}": 1.0}
    if name == "forearm":
        return {f"forearm.{side}": 1.0}
    if name == "strap":
        return strap_weights(p, side)
    raise ValueError(f"unknown skin tag {tag}")


def skin(obj, rig):
    tags = list(obj["skin_tags"])
    groups = {}
    for i, v in enumerate(obj.data.vertices):
        w = weights_for(tags[i], v.co)
        total = sum(w.values())
        top = sorted(w.items(), key=lambda kv: -kv[1])[:4]
        norm = sum(x for _, x in top) or total
        for bone_name, value in top:
            if value <= 1e-4:
                continue
            if bone_name not in groups:
                groups[bone_name] = obj.vertex_groups.new(name=bone_name)
            groups[bone_name].add([i], value / norm, "REPLACE")
    mod = obj.modifiers.new("Armature", "ARMATURE")
    mod.object = rig
    del obj["skin_tags"]
    return groups
