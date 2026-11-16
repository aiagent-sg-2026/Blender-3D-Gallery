"""Blender-side QA checks: measurements, overlaps, weights, deformation and motion.

Each function returns plain data; build.py turns it into gate results.
"""
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

import config as C


def check(name, value, limit, ok, note=None):
    out = {"name": name, "value": value, "limit": limit, "pass": bool(ok)}
    if note:
        out["note"] = note
    return out


def evaluated_world_coords(obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    mesh = eval_obj.to_mesh()
    coords = [eval_obj.matrix_world @ v.co for v in mesh.vertices]
    tris = [tuple(t.vertices) for t in mesh.loop_triangles] if mesh.loop_triangles else None
    if tris is None:
        mesh.calc_loop_triangles()
        tris = [tuple(t.vertices) for t in mesh.loop_triangles]
    eval_obj.to_mesh_clear()
    return coords, tris


# ------------------------------------------------------------------ measurements
def measure(objects):
    coords = {name: evaluated_world_coords(obj)[0] for name, obj in objects.items()}
    all_z = [v.z for vs in coords.values() for v in vs]
    tris = sum(sum(len(p.vertices) - 2 for p in obj.data.polygons) for obj in objects.values())
    draws = sum(len({p.material_index for p in obj.data.polygons}) for obj in objects.values())
    hair = coords["Hair"]
    tee = [v for v in coords["Tee"] if 0.66 <= v.z <= 0.72]
    return {
        "height_m": round(max(all_z), 4),
        "lowest_z_m": round(min(all_z), 4),
        "hair_half_width_m": round(max(abs(v.x) for v in hair), 4),
        "hair_back_m": round(max(v.y for v in hair), 4),
        "shoulder_half_width_m": round(max(abs(v.x) for v in tee), 4) if tee else None,
        "triangles": tris,
        "draw_calls": draws,
        "objects": {name: sum(len(p.vertices) - 2 for p in obj.data.polygons) for name, obj in objects.items()},
    }


# ------------------------------------------------------------------ overlaps
def bvh(obj):
    coords, tris = evaluated_world_coords(obj)
    return BVHTree.FromPolygons([tuple(v) for v in coords], tris, all_triangles=True)


def overlaps(objects, pairs):
    trees = {name: bvh(obj) for name, obj in objects.items()}
    return {f"{a}|{b}": len(trees[a].overlap(trees[b])) for a, b in pairs}


def decal_clearance(face, body):
    """Face decal triangles crossing the skin, per static expression (basis and
    each key at full strength). Transitions pass through the skin by design."""
    from head import EXPRESSIONS
    keys = face.data.shape_keys.key_blocks
    skin = bvh(body)
    out = {}
    for name in ["basis"] + EXPRESSIONS:
        for other in EXPRESSIONS:
            keys[other].value = 1.0 if other == name else 0.0
        bpy.context.view_layer.update()
        out[name] = len(bvh(face).overlap(skin))
    for other in EXPRESSIONS:
        keys[other].value = 0.0
    bpy.context.view_layer.update()
    return out


# ------------------------------------------------------------------ weights
def weight_stats(objects):
    unweighted, over_four, total = 0, 0, 0
    for obj in objects.values():
        names = {g.index: g.name for g in obj.vertex_groups}
        for v in obj.data.vertices:
            total += 1
            groups = [g for g in v.groups if g.weight > 1e-4 and g.group in names]
            if not groups:
                unweighted += 1
            if len(groups) > 4:
                over_four += 1
    return {"vertices": total, "unweighted": unweighted, "over_four_influences": over_four}


# ------------------------------------------------------------------ deformation
def triangle_areas(coords, tris):
    out = []
    for a, b, c in tris:
        out.append(((coords[b] - coords[a]).cross(coords[c] - coords[a])).length * 0.5)
    return out


def deformation(objects, rig, clips, step=4, collapse=0.2, stretch=3.0):
    """Across sampled frames of every clip, count triangles that collapse or stretch."""
    from export import rest_pose, set_clip
    face = objects["Face"]
    rest_pose(rig, face)
    rest, rest_coords, samples = {}, {}, {}
    for name, obj in objects.items():
        coords, tris = evaluated_world_coords(obj)
        rest[name] = (tris, triangle_areas(coords, tris))
        rest_coords[name] = coords
    worst = {}
    bad_total = 0
    for clip_name, action in clips:
        for frame in range(int(action.frame_start), int(action.frame_end) + 1, step):
            set_clip(rig, face, clip_name, frame)
            for name, obj in objects.items():
                if name == "Face":
                    continue          # hidden face pieces collapse by design
                coords, tris = evaluated_world_coords(obj)
                areas = triangle_areas(coords, rest[name][0])
                bad = 0
                for t_index, (a0, a1) in enumerate(zip(rest[name][1], areas)):
                    if a0 < 1e-9:
                        continue
                    ratio = a1 / a0
                    if ratio < collapse or ratio > stretch:
                        bad += 1
                        where = samples.setdefault(f"{clip_name}:{name}", [])
                        if len(where) < 4:
                            tri = rest[name][0][t_index]
                            c = sum((rest_coords[name][i] for i in tri), Vector()) / 3.0
                            where.append({"frame": frame, "ratio": round(ratio, 3),
                                          "rest_centroid": [round(c.x, 3), round(c.y, 3), round(c.z, 3)]})
                if bad:
                    bad_total += bad
                    key = f"{clip_name}:{name}"
                    worst[key] = max(worst.get(key, 0), bad)
    rest_pose(rig, face)
    return {"bad_triangles_total": bad_total, "worst": worst, "samples": samples}


def clip_clearance(objects, rig, clips, step=3):
    """Per clip, the worst number of extra triangle overlaps (beyond the rest
    pose) for: arms vs hair, arms vs face decals, jeans vs the outer tee hem."""
    from export import rest_pose, set_clip
    face = objects["Face"]
    from clothes import tee_section
    rest = {name: [v.co.copy() for v in obj.data.vertices] for name, obj in objects.items()}
    arm = lambda c: abs(c.x) > 0.12 and c.z < 0.72

    def hem(c):
        """Visible outer surface of the tee below 0.5 m (not the hidden inner lip)."""
        if c.z >= 0.50:
            return False
        hw, yf, yb, power = tee_section(c.z)
        yc, ry = (yf + yb) / 2.0, (yb - yf) / 2.0
        return (abs(c.x / hw) ** power + abs((c.y - yc) / ry) ** power) ** (1.0 / power) >= 0.965
    tests = {"arms|hair": ("Body", "Hair", arm, None), "arms|face": ("Body", "Face", arm, None),
             "jeans|tee hem": ("Jeans", "Tee", None, hem)}

    def count(a, b, keep_a, keep_b):
        ca, ta = evaluated_world_coords(objects[a])
        cb, tb = evaluated_world_coords(objects[b])
        tree_a = BVHTree.FromPolygons([tuple(v) for v in ca], ta, all_triangles=True)
        tree_b = BVHTree.FromPolygons([tuple(v) for v in cb], tb, all_triangles=True)
        n = 0
        for i, j in tree_a.overlap(tree_b):
            ra = sum((rest[a][k] for k in ta[i]), Vector()) / 3.0
            rb = sum((rest[b][k] for k in tb[j]), Vector()) / 3.0
            if (keep_a is None or keep_a(ra)) and (keep_b is None or keep_b(rb)):
                n += 1
        return n

    rest_pose(rig, face)
    base = {name: count(*spec) for name, spec in tests.items()}
    result = {name: {} for name in tests}
    for clip_name, action in clips:
        for frame in range(int(action.frame_start), int(action.frame_end) + 1, step):
            set_clip(rig, face, clip_name, frame)
            for name, spec in tests.items():
                extra = max(0, count(*spec) - base[name])
                if extra > result[name].get(clip_name, (0, 0))[0]:
                    result[name][clip_name] = (extra, frame)
    rest_pose(rig, face)
    return {"rest": base, "extra": result}


# ------------------------------------------------------------------ motion
def bone_world(rig, name):
    return rig.matrix_world @ rig.pose.bones[name].head


def pose_snapshot(rig):
    return {pb.name: (rig.matrix_world @ pb.head, rig.matrix_world @ pb.tail) for pb in rig.pose.bones}


def motion(objects, rig, clips, gaits):
    from export import rest_pose, set_clip
    face = objects["Face"]
    shoes = objects["Shoes"]
    result = {"loops": {}, "lowest_shoe_z": {}, "lowest_any_z": {}, "stance_error_m": {}}
    for name, action in clips:
        start, end = int(action.frame_start), int(action.frame_end)
        lowest, lowest_any = 1.0, 1.0
        for frame in range(start, end + 1, 2):
            set_clip(rig, face, name, frame)
            for obj_name, obj in objects.items():
                coords, _ = evaluated_world_coords(obj)
                low = min(v.z for v in coords)
                lowest_any = min(lowest_any, low)
                if obj is shoes:
                    lowest = min(lowest, low)
        result["lowest_shoe_z"][name] = round(lowest, 4)
        result["lowest_any_z"][name] = round(lowest_any, 4)
        if action.use_cyclic:
            set_clip(rig, face, name, start)
            a = pose_snapshot(rig)
            set_clip(rig, face, name, end)
            b = pose_snapshot(rig)
            result["loops"][name] = round(max(max((a[k][0] - b[k][0]).length, (a[k][1] - b[k][1]).length) for k in a), 6)
    # Stance tracking: the planted ankle must follow the ideal straight line.
    for name, (frames, stride, stance) in gaits.items():
        err = 0.0
        for side, offset in (("L", 0.0), ("R", 0.5)):
            for frame in range(0, frames + 1):
                phase = (frame / frames + offset) % 1.0
                if phase >= stance * 0.95 or phase < stance * 0.25:
                    continue          # skip heel-strike and toe-off where pitch lifts the ankle
                set_clip(rig, face, name, frame)
                ankle = bone_world(rig, f"foot.{side}")
                ideal_y = C.RIG_ANKLE[1] - stride / 2 + stride * phase / stance
                err = max(err, abs(ankle.y - ideal_y))
        result["stance_error_m"][name] = round(err, 5)
    rest_pose(rig, face)
    return result
