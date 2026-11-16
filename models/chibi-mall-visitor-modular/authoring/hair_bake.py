"""Bake the fitted sculpt's pigment and normals to the game's shared atlas."""
import hashlib
import math
from pathlib import Path
import bpy
from mathutils.bvhtree import BVHTree
import numpy as np
from atlas import write_png
from hair import fields

def unit(v):
    return v/np.maximum(np.linalg.norm(v,axis=-1,keepdims=True),1e-10)

def place_tile(image,path,tile):
    # Blender byte image pixels expose the encoded bytes here. Preserve every other tile.
    a=np.empty(1024*1024*4,dtype=np.float32);image.pixels.foreach_get(a)
    result=np.uint8(np.clip(np.rint(a.reshape(1024,1024,4)[...,:3]*255),0,255))
    result[512:,512:]=np.uint8(np.clip(np.rint(tile),0,255))
    write_png(path,result[::-1])
    if image.packed_file:image.unpack(method="REMOVE")
    image.filepath=str(path);image.reload();image.pack()

def unwrap(target):
    mesh=target.data
    charts=fields().get("runtimeUV")
    if charts is None:
        bpy.ops.object.select_all(action="DESELECT");target.select_set(True)
        bpy.context.view_layer.objects.active=target
        bpy.ops.object.mode_set(mode="EDIT");bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project(angle_limit=math.radians(62),island_margin=.026,correct_aspect=False)
        bpy.ops.object.mode_set(mode="OBJECT")
        layer=mesh.uv_layers.active.data
    else:
        if charts.shape!=(len(mesh.polygons),3,2) or not np.isfinite(charts).all():
            raise ValueError("The fitted hair UV charts do not match the runtime triangles")
        layer=mesh.uv_layers.new(name="Atlas").data
        layer.foreach_set("uv",np.ascontiguousarray(charts,dtype="f4").ravel())
    for corner in layer:corner.uv=(.024+.952*corner.uv.x,.024+.952*corner.uv.y)
    count=0
    for f in mesh.polygons:
        a,b,c=[layer[i].uv.copy() for i in f.loop_indices]
        if abs((b-a).cross(c-a))>2e-8:continue
        x=.003+.005*(count%4);y=.003+.005*(count//4)
        for i,uv in zip(f.loop_indices,((x,y),(x+.003,y),(x,y+.003))):layer[i].uv=uv
        count+=1
    for corner in layer:
        u,v=corner.uv;corner.uv=(.5+.5*u,.5+.5*v)
    return count

def lock_texels(grid, across, along):
    """Bilinear sample with a periodic circumference and two shared tip poles."""
    height,width = grid.shape[:2]
    col = np.mod(across,1.0)*width
    row = np.clip(along,0.,1.)*(height-1)
    x = np.floor(col).astype(int)%width
    y = np.floor(row).astype(int)
    u = (col-np.floor(col))[:,None]
    v = (row-y)[:,None]
    y1 = np.minimum(y+1,height-1)
    x1 = (x+1)%width
    return (1-v)*((1-u)*grid[y,x]+u*grid[y,x1])+v*((1-u)*grid[y1,x]+u*grid[y1,x1])

def bake(target,sculpt,normal_image,path,colour_image):
    micro=unwrap(target)
    mesh=target.data;mesh.calc_tangents(uvmap=mesh.uv_layers.active.name)
    layer=mesh.uv_layers.active.data
    mesh.calc_loop_triangles()
    d=fields();p=d["xyz"].astype(float);f=d["triangles"];sn=d["normals"].astype(float);pig=d["pigment"].astype(float)
    lock_normals=[]
    if "loftXYZ" in d:
        from hair_temple_fit import temple,apply
        for name,grid,n in zip(d['lockNames'][1:],d['loftXYZ'],d['loftNormals']):
            kind='hook' if name=='Long outer sweep' else ('lower' if name=='Outer lower sweep' else 'base')
            _,changed=apply(grid.reshape(-1,3),n.reshape(-1,3),lambda x:temple(x,kind))
            lock_normals.append(changed.reshape(n.shape))
    trees={}
    if "runtimePiece" in d:
        for label in ([0] if lock_normals else np.unique(d["runtimePiece"])):
            indexes=np.flatnonzero(d["piece"]==label)
            vs,local=np.unique(f[indexes],return_inverse=True)
            trees[int(label)]=(BVHTree.FromPolygons(p[vs].tolist(),local.reshape(-1,3).tolist(),all_triangles=True),indexes)
    else:
        trees[0]=(BVHTree.FromPolygons(p.tolist(),f.tolist(),all_triangles=True),np.arange(len(f)))
    out=np.zeros((512,512,3),float);out[:]=(0,0,1)
    colour=np.zeros(out.shape,float);colour[:]=(53,45,42);hit=np.zeros(out.shape[:2],bool)
    xyz=np.array([v.co[:] for v in mesh.vertices]);loops=mesh.loops
    for tri in mesh.loop_triangles:
        ids=list(tri.loops);points=xyz[list(tri.vertices)]
        uv=np.array([layer[i].uv[:] for i in ids])*1024-512.5;a,b,c=uv
        lo=np.maximum(np.floor(uv.min(axis=0)).astype(int),0);hi=np.minimum(np.ceil(uv.max(axis=0)).astype(int),511)
        if (lo>hi).any():continue
        y,x=np.mgrid[lo[1]:hi[1]+1,lo[0]:hi[0]+1];delta=np.stack((x-a[0],y-a[1]),axis=-1)
        m=np.array([b-a,c-a]).T
        if abs(np.linalg.det(m))<1e-8:continue
        bc=delta@np.linalg.inv(m).T
        w=np.stack((1-bc.sum(axis=-1),bc[...,0],bc[...,1]),axis=-1)
        inside=w.min(axis=-1)>=-.001
        if not inside.any():continue
        yy=y[inside];xx=x[inside];bary=w[inside]
        normal=unit(bary@np.array([mesh.corner_normals[i].vector[:] for i in ids]))
        tangent=unit(bary@np.array([loops[i].tangent[:] for i in ids]))
        tangent=unit(tangent-normal*np.sum(normal*tangent,axis=-1,keepdims=True))
        bitangent=unit(np.cross(normal,tangent))*loops[ids[0]].bitangent_sign
        samples=bary@points
        piece=int(d["runtimePiece"][tri.polygon_index]) if "runtimePiece" in d else 0
        if piece and lock_normals:
            # An undercut can place the opposite side closer than this texel's
            # own side. The signed circumference identifies the correct side.
            index=piece-1
            rows=math.ceil(len(lock_normals)/6)
            u=(((xx+.5)/512-.024)/.952-(.648+(index%6)*(.348/6)+.0045))/(.348/6-.008)
            v=(((yy+.5)/512-.024)/.952-(.004+(index//6)*(.992/rows)+.0085))/(.992/rows-.017)
            source=unit(lock_texels(lock_normals[index],u,v))
            shade=lock_texels(d['loftDye'][index],u,v)
        else:
            tree,face_ids=trees[piece]
            nearest=[tree.find_nearest(pt) for pt in samples]
            at=np.array([entry[0][:] for entry in nearest]);ix=np.array([entry[2] for entry in nearest])
            verts=f[face_ids[ix]];surf=p[verts]
            d0=surf[:,1]-surf[:,0];d1=surf[:,2]-surf[:,0];dv=at-surf[:,0]
            aa=np.einsum('ij,ij->i',d0,d0);bb=np.einsum('ij,ij->i',d1,d1);ab=np.einsum('ij,ij->i',d0,d1)
            ac=np.einsum('ij,ij->i',d0,dv);bc=np.einsum('ij,ij->i',d1,dv)
            det=np.maximum(aa*bb-ab**2,1e-22)
            vv=(bb*ac-ab*bc)/det;ww=(aa*bc-ab*ac)/det
            hw=np.clip(np.stack((1-vv-ww,vv,ww),axis=-1),0,1);hw/=np.maximum(hw.sum(axis=1,keepdims=True),.001)
            source=unit(np.einsum('ij,ijk->ik',hw,sn[verts]))
            shade=np.einsum('ij,ijk->ik',hw,pig[verts])
        val=np.stack([np.sum(axis*source,axis=-1) for axis in (tangent,bitangent,normal)],axis=-1)
        if piece and lock_normals:
            lock_name=d['lockNames'][piece]
            # The fine, singly tipped runtime roll already carries its analytic
            # normals. A large tangent residual on its grazing return produces
            # a transverse band absent from the high-resolution surface.
            transition=None
            if lock_name=='Long outer sweep':transition=(.55,.77)
            elif lock_name.endswith(('Lower cascade','Ear sweep')):transition=(.16,.39)
            if transition:
                x=np.clip((v-transition[0])/(transition[1]-transition[0]),0.,1.)
                retain=1-x*x*(3-2*x)
                val[:,:2]*=retain[:,None]
                val[:,2]=val[:,2]*retain+1-retain
        val[:,2]=np.maximum(val[:,2],.18)
        out[yy,xx]=unit(val)
        # Use the character's warm umber palette for broad pigment, retaining the
        # measured intra-lock structure with restrained chroma and contrast.
        lum=shade@np.array([.24,.64,.12])
        rear=np.clip((samples[:,1]+.13)/.34,0,1)
        mid=(.85*lum+16.+34.*rear)[:,None]
        colour[yy,xx]=shade if d.get("intrinsicPigment",False) else mid+np.array((9.0,4.0,2.0))+.50*(shade-lum[:,None])
        hit[yy,xx]=True
    for _ in range(5):
        count=np.zeros(hit.shape);ns=np.zeros_like(out);cs=np.zeros_like(colour)
        for dy,dx in ((0,1),(0,-1),(1,0),(-1,0)):
            mask=np.roll(hit,(dy,dx),axis=(0,1));count+=mask
            ns+=np.roll(out,(dy,dx),axis=(0,1))*mask[...,None];cs+=np.roll(colour,(dy,dx),axis=(0,1))*mask[...,None]
        border=~hit&(count>0);out[border]=unit(ns[border]);colour[border]=cs[border]/count[border,None];hit|=border
    calibration=Path(__file__).with_name("hair-pigment-fit.npz")
    if calibration.is_file():
        with np.load(calibration,allow_pickle=False) as fit:
            sculpt_file=calibration.with_name("hair-sculpt.npz")
            if str(fit["sculptSha256"])!=hashlib.sha256(sculpt_file.read_bytes()).hexdigest():
                raise ValueError("The hair reflectance calibration belongs to a different sculpt and UV layout")
            # glTF UV.y is top-down; this image is still in Blender row order.
            colour+=fit["delta"][::-1]
            if "normalDelta" in fit:
                perturbation=fit["normalDelta"][::-1]
                if perturbation.shape!=out[:,:,:2].shape or not np.all(np.isfinite(perturbation)):
                    raise ValueError("Invalid measured tangent-normal adjustment")
                out[:,:,:2]+=perturbation
                out=unit(out)
    place_tile(normal_image,path,(out*.5+.5)*255)
    place_tile(colour_image,path.with_name("visitor-atlas.png"),colour)
    bpy.context.scene["hairBake"]={"source":sculpt.name,"resolution":[512,512],"method":"Closest surface pigment and normal to per-loop MikkTSpace","microUvCharts":micro,"atlasRectangle":[512,0,1024,512]}
