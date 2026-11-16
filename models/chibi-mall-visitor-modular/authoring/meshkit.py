"""Mesh construction in rest-space metres. UVs live on corners so seams share vertices."""
import math
import bpy
import bmesh
from mathutils import Vector
from config import TILES

TAU = math.tau
PARTS = []
MATERIALS = {}


def clamp(x, lo=0., hi=1.):
    return min(max(x,lo),hi)


def mix(a,b,t):
    return a+(b-a)*t


def signed(x,e):
    return math.copysign(abs(x)**e,x)


def atlas_uv(tile,u,v):
    a,b,c,d = TILES[tile]
    return ((a+4.5+(c-a-9)*clamp(u))/1024, (1024-d+4.5+(d-b-9)*clamp(v))/1024)


def spline(points,t):
    """Centring the section frame on a smooth curve avoids ridges at guide joints."""
    t = clamp(t)*(len(points)-1)
    i = min(len(points)-2,int(t))
    f = t-i
    a,b,c,d = [Vector(points[min(max(j,0),len(points)-1)]) for j in (i-1,i,i+1,i+2)]
    return (b*2 + (-a+c)*f + (2*a-5*b+4*c-d)*f*f + (-a+3*b-3*c+d)*f**3)*.5


def init_materials(image,normal_image):
    for name,rough,metal in (("Skin",.60,0),("Hair",.51,0),("Eyes",.35,0),
                            ("Cloth",.82,0),("Leather",.61,0),("Hardware",.34,.15)):
        mat=bpy.data.materials.new(name)
        mat.use_nodes=True
        bsdf=mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Roughness"].default_value=rough
        bsdf.inputs["Metallic"].default_value=metal
        bsdf.inputs["IOR"].default_value=1.43 if name=="Hair" else 1.45
        if name=="Eyes":bsdf.inputs["Specular IOR Level"].default_value=.18
        if name=="Hair":bsdf.inputs["Specular IOR Level"].default_value=.26
        tex=mat.node_tree.nodes.new("ShaderNodeTexImage")
        tex.image=image
        mat.node_tree.links.new(tex.outputs["Color"],bsdf.inputs["Base Color"])
        relief=mat.node_tree.nodes.new("ShaderNodeTexImage");relief.image=normal_image
        normal=mat.node_tree.nodes.new("ShaderNodeNormalMap")
        if name=="Hair":
            normal.inputs["Strength"].default_value=.32
        mat.node_tree.links.new(relief.outputs["Color"],normal.inputs["Color"])
        mat.node_tree.links.new(normal.outputs["Normal"],bsdf.inputs["Normal"])
        MATERIALS[name]=mat


def round_surface(obj,triangles,levels=1):
    """Fair the control mesh before returning it to the object's runtime budget."""
    bpy.context.view_layer.objects.active=obj
    rounded=obj.modifiers.new("Rounded sculpt cage","SUBSURF");rounded.levels=levels
    bpy.ops.object.modifier_move_up(modifier=rounded.name)
    bpy.ops.object.modifier_apply(modifier=rounded.name)
    smooth_mesh=obj.data.copy()
    donor=bpy.data.objects.new("Surface normal source",smooth_mesh)
    obj.users_collection[0].objects.link(donor);donor.matrix_world=obj.matrix_world.copy()
    try:
        reduce_surface(obj,triangles)
        transfer=obj.modifiers.new("Smooth sculpt normals","DATA_TRANSFER")
        transfer.object=donor;transfer.use_loop_data=True
        transfer.data_types_loops={"CUSTOM_NORMAL"};transfer.loop_mapping="POLYINTERP_NEAREST"
        bpy.ops.object.modifier_move_up(modifier=transfer.name)
        bpy.ops.object.modifier_apply(modifier=transfer.name)
    finally:
        bpy.data.objects.remove(donor,do_unlink=True)
        bpy.data.meshes.remove(smooth_mesh)


def reduce_surface(obj,triangles):
    bpy.context.view_layer.objects.active=obj
    count=sum(len(face.vertices)-2 for face in obj.data.polygons)
    reduced=obj.modifiers.new("Runtime surface topology","DECIMATE");reduced.ratio=min(1.,triangles/count)
    bpy.ops.object.modifier_move_up(modifier=reduced.name)
    bpy.ops.object.modifier_apply(modifier=reduced.name)


class Part:
    def __init__(self,name,slot,material):
        self.name,self.slot,self.material=name,slot,material
        self.xyz,self.faces,self.uv,self.weights,self.keys,self.flat=[],[],[],[],{},set()
        PARTS.append(self)

    def vert(self,co,bone,keys=None):
        i=len(self.xyz)
        self.xyz.append(tuple(co))
        self.weights.append({bone:1.} if isinstance(bone,str) else bone)
        for key,delta in (keys or {}).items():
            if Vector(delta).length>1e-8:
                self.keys.setdefault(key,{})[i]=tuple(delta)
        return i

    def face(self,indices,tile,coords=None,flat=False):
        indices=tuple(indices)
        self.faces.append(indices)
        self.uv.extend(atlas_uv(tile,u,v) for u,v in (coords or [(.5,.5)]*len(indices)))
        if flat:
            self.flat.add(len(self.faces)-1)

    def finish(self,collection,rig):
        mesh=bpy.data.meshes.new(self.name)
        mesh.from_pydata(self.xyz,[],self.faces)
        mesh.update()
        obj=bpy.data.objects.new(self.name,mesh)
        collection.objects.link(obj)
        obj.parent=rig
        obj["partSlot"]=self.slot
        obj.data.materials.append(MATERIALS[self.material])
        uv=mesh.uv_layers.new(name="Atlas")
        uv.data.foreach_set("uv",[a for pair in self.uv for a in pair])
        for poly in mesh.polygons:
            poly.use_smooth=poly.index not in self.flat
        # MikkTSpace requires triangles/quads. Triangulate only cap ngons and retain UV corners.
        bm=bmesh.new();bm.from_mesh(mesh)
        bmesh.ops.triangulate(bm,faces=[face for face in bm.faces if len(face.verts)>4])
        bm.to_mesh(mesh);bm.free();mesh.update()
        if hasattr(self,"face_surface_count"):
            from head import skull,face_y
            normals=[]
            for loop in mesh.loops:
                i=loop.vertex_index; x,y,z=self.xyz[i]
                if i<self.face_surface_count and .807<z<1.22 and y<-.081 and abs(x)<.91*skull(z)[0]:
                    d=.0004
                    dx=(face_y(x+d,z)-face_y(x-d,z))/(2*d)
                    dz=(face_y(x,z+d)-face_y(x,z-d))/(2*d)
                    normals.append(Vector((dx,-1,dz)).normalized())
                else:normals.append((0,0,0))
            mesh.normals_split_custom_set(normals)
        groups={}
        for i,weights in enumerate(self.weights):
            for name,w in weights.items():
                if w<=.000001:
                    continue
                if name not in groups:
                    groups[name]=obj.vertex_groups.new(name=name)
                groups[name].add([i],w,"REPLACE")
        if hasattr(self,"fit_lifts"):
            fitted=obj.vertex_groups.new(name="Surface lift")
            for i,lift in self.fit_lifts.items():fitted.add([i],lift/.01,"REPLACE")
        if self.keys:
            obj.shape_key_add(name="Basis")
            for name,changes in self.keys.items():
                key=obj.shape_key_add(name=name,from_mix=False)
                for i,delta in changes.items():
                    key.data[i].co=Vector(self.xyz[i])+Vector(delta)
        mod=obj.modifiers.new("Visitor skin","ARMATURE")
        mod.object=rig
        return obj


def loft(p,rows,n,tile,bone,uv=None,tilt=0,offset=0,close=True,flat_caps=True,keys=None):
    """Rows are bottom-to-top (cx,cy,z,rx,ry[, superellipse exponent])."""
    rings=[]
    for i,row in enumerate(rows):
        cx,cy,z,rx,ry=row[:5]
        power=row[5] if len(row)>5 else 2.
        ring=[]
        for j in range(n):
            a=TAU*j/n+offset
            xx=rx*signed(math.sin(a),2/power)
            yy=-ry*signed(math.cos(a),2/power)
            co=(cx+xx,cy+yy,z+tilt*xx)
            w=bone(co,i,j) if callable(bone) else bone
            ring.append(p.vert(co,w,keys(co,i,j) if keys else None))
        rings.append(ring)
    for i,(lo,hi) in enumerate(zip(rings,rings[1:])):
        for j in range(n):
            k=(j+1)%n
            corners=[(i,j),(i,j+1),(i+1,j+1),(i+1,j)]
            if uv:
                tex,coords=uv(i,j,corners)
            else:
                tex,coords=tile,[(b/n,a/(len(rows)-1)) for a,b in corners]
            p.face((lo[j],lo[k],hi[k],hi[j]),tex,coords)
    if close:
        p.face(reversed(rings[0]),tile,flat=flat_caps)
        p.face(rings[-1],tile,flat=flat_caps)
    return rings


def ellipsoid(p,center,radii,tile,bone,n=12,lat=6,keys=None):
    cx,cy,cz=center
    rx,ry,rz=radii
    rows=[]
    for i in range(1,lat):
        phi=math.pi*i/lat
        rows.append((cx,cy,cz-rz*math.cos(phi),rx*math.sin(phi),ry*math.sin(phi)))
    rings=loft(p,rows,n,tile,bone,close=False,keys=keys)
    for top,ring,z in ((False,rings[0],cz-rz),(True,rings[-1],cz+rz)):
        co=(cx,cy,z)
        vert=p.vert(co,bone(co,0,0) if callable(bone) else bone,keys(co,0,0) if keys else None)
        for j in range(n):
            k=(j+1)%n
            p.face((ring[j],ring[k],vert) if top else (ring[k],ring[j],vert),tile)
    return rings


def section_tube(p,points,widths,depths,axis,tile,bone,n=8,keys=None,tip_extension=0):
    """Follow a path. Axis is the wide section direction, projected perpendicular to the tangent."""
    points=[Vector(v) for v in points]
    rings=[]
    for i,center in enumerate(points):
        tangent=(points[min(len(points)-1,i+1)]-points[max(0,i-1)]).normalized()
        guide=Vector(axis(i) if callable(axis) else axis)
        a=(guide-guide.dot(tangent)*tangent).normalized()
        b=tangent.cross(a).normalized()
        ring=[]
        for j in range(n):
            angle=TAU*j/n
            co=center+a*(widths[i]*math.cos(angle))+b*(depths[i]*math.sin(angle))
            weights=bone(co,i,j) if callable(bone) else bone
            ring.append(p.vert(co,weights,keys(co,i,j) if keys else None))
        rings.append(ring)
    for i in range(len(rings)-1):
        for j in range(n):
            k=(j+1)%n
            p.face((rings[i][j],rings[i][k],rings[i+1][k],rings[i+1][j]),tile,
                   [(j/n,i/(len(rings)-1)),((j+1)/n,i/(len(rings)-1)),
                    ((j+1)/n,(i+1)/(len(rings)-1)),(j/n,(i+1)/(len(rings)-1))])
    p.face(reversed(rings[0]),tile,flat=True)
    if tip_extension:
        tip=points[-1]+(points[-1]-points[-2]).normalized()*tip_extension
        i=len(points)-1
        weights=bone(tip,i,0) if callable(bone) else bone
        apex=p.vert(tip,weights,keys(tip,i,0) if keys else None)
        for j in range(n):
            p.face((rings[-1][j],rings[-1][(j+1)%n],apex),tile,
                   [(j/n,.94),((j+1)/n,.94),((j+.5)/n,1)])
    else:
        p.face(rings[-1],tile,flat=True)
    return rings


def joint(a,b,t):
    t=clamp(t)
    return {a:1-t,b:t}

