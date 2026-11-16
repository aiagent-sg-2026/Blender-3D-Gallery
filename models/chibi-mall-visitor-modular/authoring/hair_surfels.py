"""Reconstruct a smooth, closed haircut from consistent oriented samples around the head."""
import numpy as np
from scipy import ndimage as nd
from scipy.spatial import cKDTree
import pymeshlab as ml
from reconstruct_hair import norm, sample, sm, S


def geometric_normals(points, faces):
    face_normals=np.cross(points[faces[:,1]]-points[faces[:,0]],points[faces[:,2]]-points[faces[:,0]])
    normal=np.zeros_like(points)
    for col in faces.T:np.add.at(normal,col,face_normals)
    return norm(normal)


def visible(points, cam, shape):
    x,y,d=cam.projection(points)
    x=np.clip(np.rint(x).astype(int),0,shape[1]-1);y=np.clip(np.rint(y).astype(int),0,shape[0]-1)
    image=np.full(shape,-180.)
    np.maximum.at(image,(y,x),d)
    covered=image>-179
    near=nd.distance_transform_edt(~covered,return_distances=False,return_indices=True)
    return nd.median_filter(image[tuple(near)],3)


def surfels(views,seed):
    points=[]; normals=[]; pigment=[]
    # Supply only the unobserved crown, undersides, and inner surfaces from the
    # geometric envelope. The measured outer lobes will replace it.
    base=seed["xyz"].astype(float)*S;indices=seed["triangles"]
    bn=geometric_normals(base,indices);radial=norm(base-[0,1,368])
    accuracy=np.zeros(len(base))
    for cam in views:
        a,b,d=cam.projection(base)
        accuracy=np.maximum(accuracy,sm(sample(cam.sdf,a,b),-1,4)*sm(radial@cam.eye,.18,.66)*sm(bn@cam.eye,-.08,.45)*np.exp(-.5*((sample(cam.dhair,a,b)-d)/15.)**2))
    rng=np.random.default_rng(1013)
    ids=np.where(rng.random(len(base))<(.012+.16*(1-accuracy)**2))[0]
    points.append(base[ids]);normals.append(bn[ids])
    for cam in views:
        rows,cols=np.indices(cam.mask.shape);row=rows+48
        roof=nd.gaussian_filter(nd.maximum_filter(cam.skin,9),2)
        # A soft margin against the real face prevents a distant estimated lock
        # root from dissolving into the forehead during multi-view fusion.
        deficit=np.where(cam.mask&(cam.skin>-150),np.maximum(0,cam.skin+3.5-cam.dhair),0)
        lift=nd.gaussian_filter(nd.maximum_filter(deficit,5),1.7)
        depth=cam.dhair+lift
        xy=cols+cam.left-cam.cx
        tip=sm(row,155,178)*(1-sm(row,189,200))
        if cam.name=="profile":xy-=5.*tip*np.exp(-((cols+cam.left-829)/17)**2)
        if cam.name=="front":xy+=3.5*tip*np.sign(xy)*np.exp(-((np.abs(xy)-58)/14)**2)
        P=xy[...,None]*cam.right+depth[...,None]*cam.eye+(505-row)[...,None]*cam.top
        local=cam.neural_normal
        neural=norm(local[...,0:1]*cam.right+local[...,1:2]*cam.top+local[...,2:3]*cam.eye)
        derivatives=norm(np.cross(np.gradient(P,axis=0),np.gradient(P,axis=1)))*cam.mirror
        oriented=norm(.78*neural+.22*derivatives)
        direction=norm(P-[0,1,367])@cam.eye
        rate=.12+.80*sm(direction,.12,.68)
        if cam.name=="quarter":rate*=.28
        # Conflicting grazing reconstructions have lower sample density. Keep
        # silhouette turns and the convex lip at the edge of the forehead.
        weight=rate
        keep=cam.mask&(rng.random(cam.mask.shape)<weight)
        points.append(P[keep]);normals.append(oriented[keep])
        boundary=cam.mask&(cam.sdf<2.1)
        gy,gx=np.gradient(nd.gaussian_filter(cam.sdf,1.05))
        edge_dir=norm(-gx[...,None]*cam.right+gy[...,None]*cam.top)
        use=boundary&(rng.random(cam.mask.shape)<(.52 if cam.name!="quarter" else .14))
        for depth_offset,facing in [(1.2,.35),(3.5,.04),(6.,-.36)]:
            back=P-depth_offset*cam.eye+edge_dir*(1.2*np.sin(depth_offset/6*np.pi))
            points.append(back[use]);normals.append(norm(edge_dir+facing*cam.eye)[use])
    points=np.ascontiguousarray(np.vstack(points),dtype=float)
    normals=np.ascontiguousarray(norm(np.vstack(normals)),dtype=float)
    print("oriented samples",len(points),flush=True)
    ms=ml.MeshSet();ms.add_mesh(ml.Mesh(vertex_matrix=points,v_normals_matrix=normals))
    ms.generate_surface_reconstruction_screened_poisson(depth=8,fulldepth=5,pointweight=4.0,samplespernode=1.35,iters=9,threads=7,scale=1.06)
    model=ms.current_mesh();p=model.vertex_matrix().copy();f=model.face_matrix().copy().astype('i4')
    geom=geometric_normals(p,f)
    radial=norm(p-[0,2,368])
    if np.median((radial*geom).sum(axis=-1))<0:f=f[:,::-1].copy();geom=-geom
    score=np.zeros(len(p));N=np.zeros_like(p);colour=np.zeros_like(p)
    for cam in views:
        xx,yy,proj=cam.projection(p);m=sample(cam.sdf,xx,yy)
        view_depth=visible(p,cam,cam.mask.shape)
        z=sample(view_depth,xx,yy)-proj
        measured=sample(cam.dhair,xx,yy)-proj
        radial_factor=np.maximum(0,radial@cam.eye)
        incidence=np.maximum(0,geom@cam.eye)
        weight=(.01+.69*radial_factor**5+.30*incidence**5)*np.exp(-.5*(np.maximum(0,z)/3.3)**2)*np.exp(-.5*(measured/15)**2)*sm(m,-2,3)
        if cam.name=='quarter':weight*=.44
        local=sample(cam.neural_normal,xx,yy)
        observed=norm(local[:,0:1]*cam.right+local[:,1:2]*cam.top+local[:,2:3]*cam.eye)
        N+=weight[:,None]*observed
        C=sample(cam.rgb,xx,yy);shade=.67+.62*np.maximum(0,local@norm(np.array([-.40,.73,.56])))
        colour+=weight[:,None]*np.clip((C+5)/shade[:,None]**.44,16,138)
        score+=weight
    conf=sm(score,.012,.13)[:,None]
    colour=conf*colour/np.maximum(score[:,None],1e-8)+(1-conf)*np.array([55.,45.,44.])
    normal=norm(.86*conf*norm(N)+(1-.86*conf)*geom)
    print("reconstruction",len(p),len(f),"bounds",p.min(axis=0),p.max(axis=0),flush=True)
    return dict(xyz=(p/S).astype('f4'),triangles=f,normals=normal.astype('f4'),pigment=np.uint8(np.clip(np.rint(colour),0,255)),fit=np.array([v.fit for v in views]))
