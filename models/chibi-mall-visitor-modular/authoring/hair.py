"""Assemble the fitted scalp sculpt, runtime retopology and editable curve controls."""
from pathlib import Path
from functools import lru_cache
import math
import bpy
import bmesh
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from meshkit import MATERIALS, reduce_surface, spline
from head import skull
from fringe import OUTLINES, SIDE_OUTLINES, BACK_OUTLINES

@lru_cache(maxsize=1)
def fields():
    with np.load(Path(__file__).with_name("hair-sculpt.npz"),allow_pickle=False) as d:
        data={k:d[k] for k in d.files}
    if "loftXYZ" in data:
        from swept_locks import assemble
        return assemble(data)
    return data

def make_mesh(name,coords,indices):
    mesh=bpy.data.meshes.new(name)
    mesh.vertices.add(len(coords));mesh.vertices.foreach_set("co",np.asarray(coords,dtype="f4").ravel())
    mesh.loops.add(3*len(indices));mesh.loops.foreach_set("vertex_index",np.ascontiguousarray(indices,dtype="i4").ravel())
    mesh.polygons.add(len(indices));mesh.polygons.foreach_set("loop_start",np.arange(0,len(indices)*3,3,dtype="i4"))
    mesh.polygons.foreach_set("use_smooth",np.ones(len(indices),dtype=bool));mesh.update(calc_edges=True)
    return mesh

def attach(obj,rig):
    obj.parent=rig
    g=obj.vertex_groups.new(name="head");g.add(list(range(len(obj.data.vertices))),1.,"REPLACE")
    skin=obj.modifiers.new("Head skin","ARMATURE");skin.object=rig

def create(collection,rig,guides):
    d=fields();p=d["xyz"];faces=d["triangles"]
    dense=make_mesh("Fitted crown sculpt",p,faces)
    sculpt=bpy.data.objects.new("Hair high resolution source",dense);collection.objects.link(sculpt)
    sculpt["sourceOnly"]=True;sculpt.hide_render=True;sculpt.hide_set(True)
    dense.normals_split_custom_set_from_vertices(d["normals"].tolist())
    attribute=dense.color_attributes.new(name="Measured pigment",type="BYTE_COLOR",domain="POINT")
    colors=np.ones((len(p),4),dtype="f4");colors[:,:3]=d["pigment"]/255
    attribute.data.foreach_set("color_srgb",colors.ravel())
    mat=bpy.data.materials.new("Editable sculpt pigment");mat.use_nodes=True
    dye=mat.node_tree.nodes.new("ShaderNodeVertexColor");dye.layer_name=attribute.name
    mat.node_tree.links.new(dye.outputs["Color"],mat.node_tree.nodes.get("Principled BSDF").inputs["Base Color"])
    dense.materials.append(mat);attach(sculpt,rig)
    if "runtimeXYZ" in d:
        mesh=make_mesh("Hair runtime surface",d["runtimeXYZ"],d["runtimeTriangles"])
        mesh.normals_split_custom_set_from_vertices(d["runtimeNormals"].tolist())
        parts=mesh.attributes.new("Sculpt piece","INT","FACE")
        parts.data.foreach_set("value",np.ascontiguousarray(d["runtimePiece"],dtype="i4"))
    else:
        heights=np.linspace(.777,1.305,320)
        profiles=np.array([skull(z) for z in heights]);rx,ry,cy=[np.interp(p[:,2],heights,profiles[:,i]) for i in range(3)]
        inside=(np.abs(p[:,0])/rx)**2.32+(np.abs(p[:,1]-cy)/ry)**2.32<.952
        eligible=faces[d["visibleFaces"]] if "visibleFaces" in d else faces
        keep=eligible[~np.all(inside[eligible],axis=1)]
        unique,inverse=np.unique(keep,return_inverse=True)
        mesh=make_mesh("Hair runtime surface",p[unique],inverse.reshape(-1,3))
    obj=bpy.data.objects.new("Swept_hair",mesh);collection.objects.link(obj);obj["partSlot"]="Hair"
    obj["sculptSource"]=sculpt.name;mesh.materials.append(MATERIALS["Hair"])
    attach(obj,rig)
    if "runtimeXYZ" not in d:
        reduce_surface(obj,2380)
        bm=bmesh.new();bm.from_mesh(obj.data)
        bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.000012)
        bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>3])
        bm.to_mesh(obj.data);bm.free();obj.data.validate(clean_customdata=False);obj.data.update()
    if "lockNames" in d:
        obj["lockNames"]=d["lockNames"]
        for label,name in enumerate(d["lockNames"]):
            ids=np.unique(d["runtimeTriangles"][d["runtimePiece"]==label])
            group=obj.vertex_groups.new(name="Lock | "+name);group.add(ids.tolist(),1.,"REPLACE")
    add_guides(obj,guides)
    return obj,sculpt

EXTRA_GUIDES={
    "Over crown crest":(0,[(378,55),(391,56),(400,60),(408,67),(413,79)]),
    "Crown curl":(1,[(1078,59),(1089,55),(1103,58),(1112,63),(1117,70)]),
    "Left crown shoulder":(1,[(1078,77),(1064,73),(1051,82),(1043,102),(1046,128)]),
    "Right crown shoulder":(1,[(1081,77),(1096,77),(1109,88),(1114,108),(1103,130)]),
    "Right lower flick":(-2,[(842,129),(849,136),(856,142),(864,147),(871,147)]),
    "Left lower flick":(2,[(842,129),(849,136),(856,142),(864,147),(871,147)]),
    "Right sideburn":(0,[(323,150),(325,158),(328,167),(331,176),(335,187)]),
    "Left sideburn":(0,[(454,149),(454,159),(451,168),(448,179),(446,187)])}

def add_guides(obj,collection):
    obj.data.calc_loop_triangles()
    tree=BVHTree.FromPolygons([v.co for v in obj.data.vertices],[t.vertices[:] for t in obj.data.loop_triangles],all_triangles=True)
    xyz=np.array([v.co[:] for v in obj.data.vertices])
    def place(px,view):
        s=451/1.3;z=(505-px[1])/s
        if view==0:org=Vector(((px[0]-390.5)/s,-1.,z));ray=Vector((0,1,0))
        elif view==1:org=Vector(((1080.5-px[0])/s,1.,z));ray=Vector((0,-1,0))
        else:
            sign=1 if view>0 else -1
            org=Vector((sign,(px[0]-856.5)/s,z));ray=Vector((-sign,0,0))
        hit=tree.ray_cast(org,ray,2)[0]
        if hit is not None:return hit
        # A study's two silhouettes can disagree at a grazing ray. Snap to the nearest
        # near-side surface on that ray's image plane rather than binding a buried vertex.
        axis=0 if abs(view)==2 else 1;other=1-axis
        costs=(xyz[:,other]-org[other])**2+(xyz[:,2]-z)**2+.0007*(xyz[:,axis]-org[axis])**2
        return Vector(xyz[np.argmin(costs)])
    def add(name,trace,view):
        fitted=fields().get("lockBindings",{}).get(name)
        controls=[Vector(co) for co in fitted[0]] if fitted else [place(px,view) for px in trace]
        curve=bpy.data.curves.new(name,"CURVE");curve.dimensions="3D"
        sp=curve.splines.new("POLY");sp.points.add(len(controls)-1)
        for pt,pos in zip(sp.points,controls):pt.co=(*pos,1.)
        g=bpy.data.objects.new(name,curve);collection.objects.link(g);g.hide_render=True
        # Every curve is bound directly on the retained surface. The small falloff
        # across a seam remains editable even where two original outlines overlap.
        if fitted:
            g["surfaceIndices"]=fitted[1].tolist();g["surfaceParameters"]=fitted[2].tolist();g["surfaceWeights"]=fitted[3].tolist()
            return
        distances=np.full(len(xyz),np.inf);params=np.zeros(len(xyz))
        count=max(41,8*len(controls))
        for i in range(count):
            t=i/(count-1);center=np.array(spline(controls,t))
            d=np.linalg.norm(xyz-center,axis=1);better=d<distances
            distances[better]=d[better];params[better]=t
        radius=.052
        indices=np.flatnonzero(distances<radius)
        if not len(indices):raise ValueError("No surface under "+name)
        w=np.cos(np.minimum(1,distances[indices]/radius)*math.pi/2)**2
        g["surfaceIndices"]=indices.tolist();g["surfaceWeights"]=w.tolist()
        g["surfaceParameters"]=params[indices].tolist()
    for view,name,paths in [(0,"",OUTLINES),(1,"",BACK_OUTLINES),(2,"Left ",SIDE_OUTLINES),(-2,"Right ",SIDE_OUTLINES)]:
        for label,edges in paths.items():
            for suffix,points in zip((" outer"," inner"),edges):add(name+label+suffix,points,view)
    for name,(view,trace) in EXTRA_GUIDES.items():add("Guide • "+name,trace,view)
    for name in fields().get("lockBindings",{}):
        if collection.objects.get(name) is None:add(name,[],0)

