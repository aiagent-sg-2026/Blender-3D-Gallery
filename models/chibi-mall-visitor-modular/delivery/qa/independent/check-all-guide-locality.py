"""Exercise every saved guide and verify locality of named free-lock guides."""
from pathlib import Path
import bpy
import numpy as np
import hashlib, json, sys
from mathutils import Vector

candidate, output = map(Path, sys.argv[-2:])
sys.path.insert(0, str(candidate / "source"))
import guides

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
hair = bpy.data.objects["Swept_hair"]
collection = bpy.data.collections["Editable hair guides"]
def coords():
    flat = np.empty(len(hair.data.vertices)*3, dtype="f4")
    hair.data.vertices.foreach_get("co", flat)
    return flat.reshape(-1, 3)
base = coords()
named = {g.name[7:]: g.index for g in hair.vertex_groups if g.name.startswith("Lock | ")}
records = []
for guide in sorted(collection.objects, key=lambda obj: obj.name):
    points = guide.data.splines[0].points
    saved = [p.co.copy() for p in points]
    for pt in points:
        pt.co.x += .008
        pt.co.y += .004
    try:
        with guides.evaluated_hair(hair,collection):
            after = coords()
    finally:
        for pt,initial in zip(points, saved):
            pt.co = initial
    displacement = np.linalg.norm(after-base, axis=1)
    moved = np.flatnonzero(displacement > 1e-6)
    restored = np.array_equal(base,coords())
    name = guide.name
    lock = next((k for k in named if name in (k+" outer",k+" inner")), None)
    local = True
    if lock:
        slot = named[lock]
        local = all(any(g.group == slot for g in hair.data.vertices[int(i)].groups) for i in moved)
    records.append(dict(guide=name,lock=lock,movedVertices=len(moved),peakM=float(displacement.max()),restored=restored,withinLock=bool(local)))
ok=bool(len(records)>0 and len([r for r in records if r["lock"]])==2*(len(named)-1)
    and all(r["restored"] and r["movedVertices"]>0 and r["withinLock"] for r in records))
output.write_text(json.dumps(dict(masterSha256=sha(candidate/"visitor.blend"),glbSha256=sha(candidate/"visitor.glb"),
  method="Applied an in-memory offset to each whole guide with the same evaluated_hair context used by the real exporter. Recovered exact rest coordinates after each. Named inner/outer guides checked for exclusive membership in their lock. Formal build separately performs an actual edited-guide GLB export.",count=len(records),records=records,passed=ok),indent=2)+"\n")
print("ALL NATIVE GUIDES",len(records),"named",len([r for r in records if r["lock"]]),"pass",ok,flush=True)
if not ok: raise RuntimeError("One or more native editable guide contracts failed")
