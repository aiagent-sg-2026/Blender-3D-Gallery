"""Rig the TRELLIS-based body: armature (about 20 bones), skinning, animation clips, GLB export. Mesh-agnostic apart from the landmark table.
Run (repo root): blender --background --factory-startup --python-exit-code 1 --python models/chibi-mall-guide-v5/base-rig/rig_base.py -- BODY_PREP.glb OUT_DIR
Input: a GLB from trellis-trial/prepare_base.py (feet on z = 0, character faces -Y in Blender, about 1.00 m tall, sign already split off).
Landmarks (m) are fractions of the body height and of the body's measured width, so a different TRELLIS result needs only a visual check."""
import bpy, bmesh, sys, os, json, math
import numpy as np
from mathutils import Vector, Euler
glb, OUT = sys.argv[sys.argv.index('--') + 1:][:2]; os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=glb)
body = [o for o in bpy.data.objects if o.type == 'MESH'][0]; body.name = 'Body'
bpy.ops.object.select_all(action='DESELECT'); body.select_set(True); bpy.context.view_layer.objects.active = body
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
for o in [o for o in bpy.data.objects if o.type != 'MESH']: bpy.data.objects.remove(o)
# the glTF importer splits vertices per face normal; weld them so bone heat sees a connected surface (UVs live on the loops and are kept)
bm = bmesh.new(); bm.from_mesh(body.data); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5); bm.to_mesh(body.data); bm.free()
bpy.ops.object.shade_smooth()
P = np.array([v.co[:] for v in body.data.vertices]); H = P[:, 2].max()
# ---- landmark table (Blender space: +X = character's left, -Y = front) ----
LM = json.load(open(os.environ.get('LANDMARKS', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'landmarks.json'))))
def pt(name): x, y, z = LM[name]; return Vector((x, y, z * H))
bones = [  # name, head, tail, parent
    ('root', 'root_h', 'root_t', None), ('hips', 'hips_h', 'hips_t', 'root'), ('spine', 'spine_h', 'spine_t', 'hips'), ('chest', 'chest_h', 'chest_t', 'spine'),
    ('neck', 'neck_h', 'neck_t', 'chest'), ('head', 'head_h', 'head_t', 'neck'),
    ('shoulder.L', 'shL_h', 'shL_t', 'chest'), ('upper_arm.L', 'shL_t', 'elL', 'shoulder.L'), ('forearm.L', 'elL', 'wrL', 'upper_arm.L'), ('hand.L', 'wrL', 'haL', 'forearm.L'),
    ('shoulder.R', 'shR_h', 'shR_t', 'chest'), ('upper_arm.R', 'shR_t', 'elR', 'shoulder.R'), ('forearm.R', 'elR', 'wrR', 'upper_arm.R'), ('hand.R', 'wrR', 'haR', 'forearm.R'),
    ('thigh.L', 'hpL', 'knL', 'hips'), ('shin.L', 'knL', 'anL', 'thigh.L'), ('foot.L', 'anL', 'toL', 'shin.L'),
    ('thigh.R', 'hpR', 'knR', 'hips'), ('shin.R', 'knR', 'anR', 'thigh.R'), ('foot.R', 'anR', 'toR', 'shin.R')]
arm_d = bpy.data.armatures.new('Rig'); rig = bpy.data.objects.new('Rig', arm_d); bpy.context.scene.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig; bpy.ops.object.mode_set(mode='EDIT')
for name, h, t, par in bones:
    b = arm_d.edit_bones.new(name); b.head = pt(h); b.tail = pt(t)
    if (b.tail - b.head).length < 0.01: b.tail = b.head + Vector((0, 0, 0.03))
    if par: b.parent = arm_d.edit_bones[par]; b.use_connect = (par != 'root' and (arm_d.edit_bones[par].tail - b.head).length < 1e-4)
bpy.ops.object.mode_set(mode='OBJECT')
# ---- skinning: bone heat, fall back to nearest-bone weights for vertices it leaves empty ----
bpy.ops.object.select_all(action='DESELECT'); body.select_set(True); rig.select_set(True); bpy.context.view_layer.objects.active = rig
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
me = body.data; groups = {g.index: g.name for g in body.vertex_groups}
def seg_dist(p, a, b):
    ab = b - a; t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-12))); return (p - (a + ab * t)).length
bone_segs = {n: (rig.data.bones[n].head_local.copy(), rig.data.bones[n].tail_local.copy()) for n, *_ in bones}
empty = 0
for v in me.vertices:
    if not any(g.weight > 0.01 for g in v.groups):
        empty += 1; ds = sorted((seg_dist(v.co, *bone_segs[n]), n) for n in bone_segs if n in body.vertex_groups)[:2]
        for d, n in ds: body.vertex_groups[n].add([v.index], 1.0 / (1e-3 + d), 'REPLACE')
json.dump({'vertices': len(me.vertices), 'fallback_vertices': empty, 'groups': len(body.vertex_groups)}, open(os.path.join(OUT, 'skin-report.json'), 'w'))
# ---- weight clean-up: bone heat lets the arms grab nearby shorts and torso vertices; arm bones may only own vertices outside the trunk ----
ARM = ('shoulder', 'upper_arm', 'forearm', 'hand')
arm_groups = [g for g in body.vertex_groups if g.name.startswith(ARM)]; fixed = 0
for v in me.vertices:
    x, y, z = v.co
    in_trunk = (z < 0.31 and abs(x) < 0.135) or (0.31 <= z < 0.48 and abs(x) < 0.10)
    if not in_trunk: continue
    for g in arm_groups:
        try:
            g.remove([v.index]); fixed += 1
        except RuntimeError: pass
    if not any(g.weight > 0.01 for g in v.groups): body.vertex_groups['hips' if z < 0.31 else 'chest'].add([v.index], 1.0, 'REPLACE')
json.dump({'vertices': len(me.vertices), 'fallback_vertices': empty, 'groups': len(body.vertex_groups), 'arm_weights_removed_in_trunk': fixed}, open(os.path.join(OUT, 'skin-report.json'), 'w'))
# ---- animation: every rotation is given about the ARMATURE axes (X = pitch, Y = roll to the side, Z = turn) in degrees and converted to each bone's local frame ----
bpy.context.view_layer.objects.active = rig; bpy.ops.object.mode_set(mode='POSE'); pb = rig.pose.bones
for b in pb: b.rotation_mode = 'QUATERNION'
FPS = 30; sc = bpy.context.scene; sc.render.fps = FPS
from mathutils import Matrix
REST = {b.name: b.matrix_local.to_3x3() for b in rig.data.bones}
def glob_q(rx, ry, rz): return (Euler((math.radians(rx), math.radians(ry), math.radians(rz)), 'XYZ')).to_matrix()
def pose(frame, rots=None, locs=None):
    for name, (rx, ry, rz) in (rots or {}).items():
        R = REST[name]; local = R.inverted() @ glob_q(rx, ry, rz) @ R
        pb[name].rotation_quaternion = local.to_quaternion(); pb[name].keyframe_insert('rotation_quaternion', frame=frame)
    for name, (x, y, z) in (locs or {}).items():
        R = REST[name]; v = R.inverted() @ Vector((x, y, z)); pb[name].location = v; pb[name].keyframe_insert('location', frame=frame)
def reset():
    for b in pb: b.rotation_quaternion = (1, 0, 0, 0); b.location = (0, 0, 0)
actions = {}
def new_action(name, frames):
    reset(); act = bpy.data.actions.new(name); rig.animation_data_create(); rig.animation_data.action = act; actions[name] = act
    # a rest pose key on every bone at both ends, so unused bones hold still and the clip loops
    for f in (1, frames + 1): pose(f, {b.name: (0, 0, 0) for b in pb}, {'hips': (0, 0, 0)})
def idle():
    n = 60; new_action('idle', n)
    for f in range(n + 1):
        t = f / n; s = math.sin(2 * math.pi * t)
        pose(f + 1, {'chest': (1.8 * s, 0, 0), 'head': (-1.2 * s, 0, 0), 'upper_arm.L': (0, 2 * s, 0)}, {'hips': (0, 0, 0.004 * s)})
def walk(name, n, swing, bounce, arm, sway):
    new_action(name, n)
    for f in range(n + 1):
        a = 2 * math.pi * f / n; s = math.sin(a); k = math.sin(a + math.pi / 2)
        pose(f + 1, {'thigh.L': (-swing * s, 0, 0), 'thigh.R': (swing * s, 0, 0), 'shin.L': (max(0, swing * 1.1 * k), 0, 0), 'shin.R': (max(0, -swing * 1.1 * k), 0, 0),
                     'upper_arm.L': (arm * s, 0, 0), 'hips': (0, 0, sway * s), 'chest': (0, 0, -sway * 0.6 * s), 'head': (0, 0, sway * 0.4 * s)},
             {'hips': (0, 0, bounce * abs(math.sin(a)))})
def wave():
    n = 45; new_action('wave', n)
    for f in range(n + 1):
        t = f / n; up = min(1, t * 4, (1 - t) * 4); w = math.sin(t * 2 * math.pi * 3)
        # the arm hugs the trunk in this mesh, so the wave bends the elbow (forearm up and forward) instead of lifting the whole arm
        pose(f + 1, {'upper_arm.L': (0, -30 * up, 0), 'forearm.L': (-105 * up, 25 * w * up, 0), 'head': (0, 0, 5 * up)})
def point():
    n = 36; new_action('point', n)
    for f in range(n + 1):
        t = f / n; up = min(1, t * 3, (1 - t) * 3); s = math.sin(t * 2 * math.pi)
        pose(f + 1, {'upper_arm.R': (-55 * up, 0, 0), 'forearm.R': (-20 * up + 4 * s * up, 0, 0), 'chest': (0, 0, -6 * up)})
idle(); walk('walk_calm', 36, 22, 0.0, 14, 3); walk('walk_bouncy', 24, 28, 0.0, 20, 5); point()
if os.environ.get('WAVE') == '1': wave()   # off by default: the arm hugs the trunk in this mesh and a raised arm tears it
# ---- foot contact: for every walk frame the hips are lifted so the lowest vertex of the body sits exactly on the floor (z = 0); the bouncy walk adds a small hop on top ----
GROUND = {}
def ground_clip(name, n, hop):
    act = actions[name]; rig.animation_data.action = act; dg = bpy.context.evaluated_depsgraph_get(); lows = []
    for f in range(1, n + 2):
        pb['hips'].location = (0, 0, 0); pb['hips'].keyframe_insert('location', frame=f); sc.frame_set(f); dg.update()
        ev = body.evaluated_get(dg); m = ev.to_mesh(); minz = min(v.co.z for v in m.vertices); ev.to_mesh_clear(); lows.append(minz)
        a_ = 2 * math.pi * (f - 1) / n; pose(f, None, {'hips': (0, 0, -minz + hop * abs(math.sin(a_)))})
    GROUND[name] = dict(frames=n, lowest_z_before_correction_mm=[round(z * 1000, 1) for z in (min(lows), max(lows))], hop_m=hop)
bpy.ops.object.mode_set(mode='POSE')
ground_clip('walk_calm', 36, 0.0); ground_clip('walk_bouncy', 24, 0.012)
json.dump(GROUND, open(os.path.join(OUT, 'ground-report.json'), 'w'), indent=1)
reset(); bpy.ops.object.mode_set(mode='OBJECT')
# push every action to the NLA so the exporter writes one clip each
for name, act in actions.items():
    tr = rig.animation_data.nla_tracks.new(); tr.name = name; st = tr.strips.new(name, 1, act); st.name = name
rig.animation_data.action = None
# keep the skinned mesh a scene root (parenting it under the armature gives the validator warning NODE_SKINNED_MESH_NON_ROOT); the armature modifier keeps the skin
bpy.ops.object.select_all(action='DESELECT'); body.select_set(True); bpy.context.view_layer.objects.active = body; bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, 'guide-rigged.glb'), export_format='GLB', export_yup=True, export_animations=True, export_animation_mode='NLA_TRACKS', export_skins=True, export_apply=False)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'guide-rigged.blend'))
print('RIGGED', len(bones), 'bones', empty, 'fallback verts', list(actions))
