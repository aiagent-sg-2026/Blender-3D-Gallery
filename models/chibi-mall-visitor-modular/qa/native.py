"""Read back the native source, and compare the rendered interchange result to that source."""
import json
import sys
from pathlib import Path
import bpy
import numpy as np

folder=Path(sys.argv[-1]).resolve()
sc=bpy.context.scene
rig=bpy.data.objects["Visitor_Rig"]
objects=[o for o in sc.objects if o.type=="MESH" and o.get("partSlot")]
geometry={}
mesh_integrity={}
for o in objects:
    o.data.calc_loop_triangles()
    geometry[o.name]=len(o.data.loop_triangles)
    copy=o.data.copy()
    try:
        changed=copy.validate(verbose=True,clean_customdata=False)
        mesh_integrity[o.name]={"requiresRepair":bool(changed),
            "nonFiniteVertices":sum(not np.isfinite(tuple(v.co)).all() for v in o.data.vertices),
            "zeroAreaTriangles":sum(t.area<=1e-14 for t in o.data.loop_triangles)}
    finally:bpy.data.meshes.remove(copy)
export=json.loads((folder/"qa/geometry.json").read_text())
export_topology={name:count==export["parts"].get(name,{}).get("triangles") for name,count in geometry.items()}
def islands(o):
    adj=[set() for _ in o.data.vertices]
    for e in o.data.edges:
        a,b=e.vertices;adj[a].add(b);adj[b].add(a)
    remaining=set(i for i,a in enumerate(adj) if a)
    count=0
    while remaining:
        queue=[remaining.pop()];count+=1
        while queue:
            found=adj[queue.pop()]&remaining;queue.extend(found);remaining-=found
    return count
jersey=islands(bpy.data.objects["Crewneck_shirt"])
denim=islands(bpy.data.objects["Straight_denim"])
def pixels(name):
    image=bpy.data.images.load(str(folder/"qa"/name))
    ar=np.empty(len(image.pixels),dtype=np.float32);image.pixels.foreach_get(ar)
    return ar.reshape(image.size[1],image.size[0],4)[:,:,:3]
source=pixels("source-portrait.png");reimport=pixels("studio-portrait.png")
diff=np.abs(source-reimport)
shape=len([o for o in objects if o.data.shape_keys])
atlas=bpy.data.images.get("Visitor colour atlas")
normal=bpy.data.images.get("Visitor normal atlas")
expects_normal="normal" in sc.get("surfaceMaps",[])
tracks=[t.name for t in rig.animation_data.nla_tracks]
guides=len(bpy.data.collections["Editable hair guides"].objects)
report={"blender":bpy.app.version_string,"triangles":sum(geometry.values()),"meshes":geometry,"bones":len(rig.data.bones),
        "meshIntegrity":mesh_integrity,"sourceExportTriangleAgreement":export_topology,
        "shirtConnectedComponents":jersey,"jeansWithTwoCuffsComponents":denim,
        "shapeKeyMeshes":shape,"actions":tracks,"guideCurves":guides,"atlasPacked":bool(atlas and atlas.packed_file),
        "normalAtlasPacked":bool(normal and normal.packed_file) if expects_normal else None,
        "sourceToGlbRenderMeanAbsoluteLinearRgb":float(diff.mean()),
        "sourceToGlbRenderP99AbsoluteLinearRgb":float(np.percentile(diff,99))}
report["pass"]=bool(report["atlasPacked"] and len(tracks)==12 and len(rig.data.bones)==20 and shape>=4
                and all(not v["requiresRepair"] and not v["nonFiniteVertices"] and not v["zeroAreaTriangles"] for v in mesh_integrity.values())
                and all(export_topology.values())
                and (not expects_normal or report["normalAtlasPacked"])
                and jersey==1 and denim==3 and guides>=12 and diff.mean()<.027 and np.percentile(diff,99)<.17)
(folder/"qa/native.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({k:v for k,v in report.items() if k!="meshes"}))
if not report["pass"]:raise RuntimeError("Native source acceptance failed")

