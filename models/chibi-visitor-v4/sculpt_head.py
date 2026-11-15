"""Sculpt-workflow head study for Chibi Visitor v4.

Runs inside the connected Blender through the MCP `execute_blender_code` tool (needs a VIEW_3D area).
Workflow: even quad sphere -> block the cranium/jaw with a few proportional edits ->
real Blender sculpt brush strokes (Draw / Clay Strips / Inflate / Smooth / Pinch) -> render.
Everything lives in the scene "CV4 Sculpt"; the production scene is not touched.
"""
import bpy, bmesh, math as m, os
from mathutils import Vector, Euler
from bpy_extras import view3d_utils

SC = "CV4 Sculpt"
OUT = os.environ.get("CV4_SCULPT_OUT", "/tmp")
HC = Vector((0.0, 0.028, 0.757))     # skull centre, character faces -Y


def setup():
    old = bpy.data.scenes.get(SC)
    if old:
        for o in list(old.objects):
            bpy.data.objects.remove(o)
        bpy.data.scenes.remove(old)
    sc = bpy.data.scenes.new(SC)
    win = bpy.context.window_manager.windows[0]
    win.scene = sc
    return sc, win


def quad_sphere(levels=5):
    bpy.ops.mesh.primitive_cube_add(size=2)
    ob = bpy.context.active_object
    ob.name = "HeadSculpt"
    sub = ob.modifiers.new("s", "SUBSURF")
    sub.levels = sub.render_levels = levels
    bpy.ops.object.modifier_apply(modifier="s")
    me = ob.data
    for v in me.vertices:
        v.co = v.co.normalized()
    return ob


def sp(v, e):
    return m.copysign(abs(v) ** e, v)


def sstep(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


HB, HV, HTOP, HEXP = 0.172, 0.188, 0.150, 4.2


def head_shape(d):
    """Skull point (relative to HC) for unit direction d. Same silhouette as the generator's head,
    which was matched row by row against the sheet in front, side and back views."""
    cu = max(-1.0, min(1.0, d.z))
    su, a = m.sqrt(1 - cu * cu), m.atan2(d.y, d.x)
    if cu >= 0:
        h, z = su, HTOP * cu
    else:
        ex = 2.3 + (HEXP - 2.3) * sstep(0.45, -0.15, m.sin(a))      # square jaw in front, round nape
        h, z = sp(su, 2 / ex), HV * sp(cu, 2 / ex)
    wide = 0.151 + 0.031 * sstep(-0.125, 0.05, z)                  # wide cranium, narrow cheeks
    box = 2 / (2.0 + 0.9 * sstep(0.02, -0.08, z))                  # flat face plane below the brow
    return Vector((wide * h * sp(m.cos(a), box), HB * h * sp(m.sin(a), box), z))


def relax(me, pick, iters):
    """Laplacian relax of the vertices selected by pick(co)."""
    nb = [[] for _ in me.vertices]
    for e in me.edges:
        a, b = e.vertices
        nb[a].append(b)
        nb[b].append(a)
    ids = [v.index for v in me.vertices if pick(v.co)]
    for _ in range(iters):
        new = {i: sum((me.vertices[j].co for j in nb[i]), Vector()) / len(nb[i]) for i in ids}
        for i, c in new.items():
            me.vertices[i].co = me.vertices[i].co.lerp(c, 0.6)


def block_out(ob):
    for v in ob.data.vertices:
        v.co = head_shape(v.co.normalized())
    relax(ob.data, lambda p: p.z < -0.10, 8)          # melt the superellipse pole crease at jaw/nape
    ob.location = HC
    bpy.ops.object.shade_smooth()


class Brush:
    def __init__(self, win, area, region, ob):
        self.win, self.area, self.region, self.ob = win, area, region, ob
        self.r3d = area.spaces[0].region_3d
        self.cur = None

    def view(self, name):
        rot = {"front": Euler((m.pi / 2, 0, 0)), "side": Euler((m.pi / 2, 0, m.pi / 2)),
               "back": Euler((m.pi / 2, 0, m.pi)), "top": Euler((0, 0, 0))}[name]
        self.r3d.view_perspective = "ORTHO"
        self.r3d.view_rotation = rot.to_quaternion()
        self.r3d.view_location = HC
        self.r3d.view_distance = 0.9

    def px(self, world):
        return view3d_utils.location_3d_to_region_2d(self.region, self.r3d, world)

    def pick(self, name):
        if self.cur == name:
            return
        bpy.ops.brush.asset_activate(asset_library_type="ESSENTIALS",
                                     relative_asset_identifier=f"brushes/essentials_brushes-mesh_sculpt.blend/Brush/{name}")
        self.cur = name

    def dab(self, brush, p, radius, strength=0.5, invert=False, n=3, view="front"):
        """One stroke at world point p, world-space radius, repeated n times."""
        self.view(view)
        a = self.px(Vector(p))
        b = self.px(Vector(p) + Vector((radius, 0, 0)) if view == "front" else Vector(p) + Vector((0, radius, 0)))
        rpx = max(4.0, (a - b).length) if a and b else 40.0
        with bpy.context.temp_override(window=self.win, area=self.area, region=self.region,
                                       active_object=self.ob, object=self.ob):
            if self.ob.mode != "SCULPT":
                bpy.ops.object.mode_set(mode="SCULPT")
            self.pick(brush)
            br = bpy.context.tool_settings.sculpt.brush
            ups = bpy.context.tool_settings.sculpt.unified_paint_settings
            ups.use_unified_size = False
            ups.use_unified_strength = False
            br.size = int(rpx)
            br.strength = strength
            pts = [{"name": "s", "location": tuple(Vector(p) - self.ob.location), "mouse": (a.x, a.y), "mouse_event": (a.x, a.y),
                    "pressure": 1.0, "size": int(rpx), "x_tilt": 0, "y_tilt": 0, "time": i * 0.01, "is_start": i == 0}
                   for i in range(n)]
            bpy.ops.sculpt.brush_stroke(stroke=pts, mode="INVERT" if invert else "NORMAL")

    def done(self):
        with bpy.context.temp_override(window=self.win, area=self.area, region=self.region,
                                       active_object=self.ob, object=self.ob):
            bpy.ops.object.mode_set(mode="OBJECT")


def run():
    sc, win = setup()
    area = next(a for a in win.screen.areas if a.type == "VIEW_3D")
    region = next(r for r in area.regions if r.type == "WINDOW")
    ob = quad_sphere(5)
    block_out(ob)
    b = Brush(win, area, region, ob)
    wp = lambda x, y, z: HC + Vector((x, y, z))
    # --- sculpt passes (front is -Y). Broad soft forms first, then smooth, like a real sculpt ---
    for sx in (-1, 1):
        b.dab("Inflate/Deflate", wp(sx * 0.098, -0.125, -0.110), 0.070, 0.6, n=4)     # cheek pads
        b.dab("Draw", wp(sx * 0.068, -0.150, -0.050), 0.060, 0.6, invert=True, n=4)   # eye socket (broad, shallow)
        b.dab("Clay Strips", wp(sx * 0.070, -0.160, -0.003), 0.050, 0.5, n=3)         # brow ridge
    b.dab("Smooth", wp(0, -0.16, -0.06), 0.13, 0.6, n=6)
    b.dab("Draw", wp(0, -0.160, -0.085), 0.030, 0.7, n=4)                            # nose bridge/tip mass
    b.dab("Draw", wp(0, -0.166, -0.170), 0.040, 0.6, invert=True, n=3)               # mouth area dip
    b.dab("Draw", wp(0, -0.150, -0.230), 0.045, 0.5, n=3)                            # chin
    b.dab("Smooth", wp(0, -0.16, -0.12), 0.09, 0.5, n=4)
    b.done()
    return ob, b


def bake(ob, path):
    """Write the sculpted skull (world coordinates, quads) for generate.py to load."""
    import json
    me = ob.data
    data = {"note": "Sculpted skull from sculpt_head.py (Blender 5.1.2 sculpt brushes). World metres, faces -Y.",
            "verts": [[round(c, 6) for c in (ob.matrix_world @ v.co)] for v in me.vertices],
            "faces": [list(p.vertices) for p in me.polygons]}
    with open(path, "w") as f:
        json.dump(data, f, separators=(",", ":"))
    return len(data["verts"]), len(data["faces"])


if __name__ == "__main__":
    run()
