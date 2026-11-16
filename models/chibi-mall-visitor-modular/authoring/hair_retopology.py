"""Construct a scalp chart and direction-aligned low-poly topology from physical hair relief."""
import numpy as np
from scipy import ndimage as nd
from scipy.spatial import cKDTree, Delaunay
from skimage.measure import find_contours
from hair_raster import DLL,draw
from reconstruct_hair import sm,norm,S,sample
from hair_envelope import vertex_normals
from hair_relief import extend
from hair_fit import LOCKS

CENTER=np.array([0.,2.,368.]);H=280;W=640
def sphere(p):
    q=p-CENTER;r=np.linalg.norm(q,axis=1);bearing=np.arctan2(q[:,0],-q[:,1]);pol=np.arccos(np.clip(q[:,2]/np.maximum(r,1e-6),-1,1))
    return (bearing+np.pi)*W/(np.pi*2),pol*(H-1)/np.pi,r

def radial_map(p,f):
    u,v,r=sphere(p);ang=u[f].copy();cut=ang.ptp(axis=1)>W/2 if hasattr(ang,'ptp') else np.ptp(ang,axis=1)>W/2
    ang[cut]=np.where(ang[cut]<W/2,ang[cut]+W,ang[cut])
    coords=np.stack((ang,v[f],r[f]),axis=-1)
    coords=np.vstack((coords,coords[cut]-[W,0,0]))
    points=np.ascontiguousarray(coords.reshape(-1,3),'f8');faces=np.arange(len(points),dtype='i4').reshape(-1,3)
    z=np.empty((H,W));idx=np.empty((H,W),'i4');b=np.empty((H,W,3));DLL.raster(points,faces,len(faces),W,H,z,idx,b)
    good=idx>=0
    return z,good
def sample_wrap(image,u,v):
    return nd.map_coordinates(np.tile(image,(1,3)),[np.clip(v,0,H-1.001),np.mod(u,W)+W],order=1,mode='nearest',prefilter=False)
def between(p,f,skin,neutral,views,matte):
    r,hit=radial_map(p,f);r0,good=radial_map(neutral,f);rs,sk=radial_map(*skin)
    ugrid,vgrid=np.meshgrid(np.arange(W),np.arange(H));ang=ugrid*(2*np.pi/W)-np.pi
    # The face/head is always opaque. A locked lower hairline separates the
    # frontal fringe from the posterior taper; no projection can pull an upper
    # crown vertex through the underlying head between two shoulders.
    ext=good&(r0>rs+.1)
    ext[:34]=True
    ext=nd.binary_closing(np.tile(ext,(1,3)),iterations=3)[:,W:2*W]
    limits=np.zeros(W)
    for i in range(W):
        theta=ang[0,i];top=160 if abs(theta)<.84 else 185 if abs(theta)<1.55 else 249
        b=np.flatnonzero(ext[:top,i]);limits[i]=b[-1] if len(b) else 90
    limits=nd.gaussian_filter1d(nd.median_filter(limits,7,mode='wrap'),1.4,mode='wrap')
    # Extend an unobserved boundary from its nearest measured neighbor before
    # filtering. The lower edge is rolled in three dimensions during assembly.
    def clean(a,m):
        b=np.tile(a,(1,3));mask=np.tile(m,(1,3))
        nx=nd.distance_transform_edt(~mask,return_distances=False,return_indices=True)
        return nd.gaussian_filter(nd.median_filter(b[tuple(nx)],size=(3,3)),(.79,.82))[:,W:2*W]
    r=clean(r,hit);r0=clean(r0,good)
    field=.66*r+.34*r0
    cyl=np.sqrt(np.maximum(0,1-np.cos(vgrid*np.pi/(H-1))**2))
    silhouette=np.maximum(np.abs(np.cos(ang)),np.abs(np.sin(ang)))
    # Where neighboring angles view the lock edge-on its historic silhouette
    # constrains the relief; broad bodies are free to retain the entire curvature.
    edge=np.clip((vgrid-limits[None,:]+7)/8,0,1)
    protect=sm(np.abs(np.sin(ang*2)),.0,.19)
    field=r0+(field-r0)*(1-.50*edge)
    # Genuine scalp and ear surfaces are taken from the neutral character,
    # with a small local allowance only inside its existing hair footprint.
    field=np.where(sk&ext,np.maximum(field,rs+1.25),field)
    field=nd.gaussian_filter(np.tile(field,(1,3)),(.77,.65))[:,W:2*W]
    def pos(uv,depth=0.):
        aa,tt=uv.T
        m=np.interp(np.mod(aa,W),np.r_[np.arange(W),W],np.r_[limits,limits[0]])
        beta=(1.1+tt*(m-1.1))*np.pi/(H-1);theta=aa*(2*np.pi/W)-np.pi
        radius=sample_wrap(field,aa,beta*(H-1)/np.pi)-depth
        return CENTER+radius[:,None]*np.stack((np.sin(beta)*np.sin(theta),-np.sin(beta)*np.cos(theta),np.cos(beta)),axis=1)
    def param(world):
        a,b,r=sphere(world);m=np.interp(np.mod(a,W),np.r_[np.arange(W),W],np.r_[limits,limits[0]])
        return np.stack((a,(b-1.1)/np.maximum(1,m-1.1)),axis=1)
    return pos,param,limits

def retopo(views,seed,foundation,skin,mattes):
    source=seed['xyz'].astype(float)*S;f=seed['triangles'];prior=foundation['xyz'].astype(float)*S
    pos,uv_of,limits=between(source,f,skin,prior,views,mattes)
    # The dense master and low topology evaluate the same continuous field.
    cols,rows=350,139
    u,t=np.meshgrid(np.arange(cols)*W/cols,np.linspace(0,1,rows));uv=np.stack((u,t),axis=-1).reshape(-1,2);P=pos(uv)
    faces=[]
    for j in range(rows-1):
        a=j*cols+np.arange(cols);b=j*cols+(np.arange(cols)+1)%cols;c=a+cols;d=b+cols
        faces.extend(np.stack((a,c,b),axis=-1));faces.extend(np.stack((b,c,d),axis=-1))
    top=P[:cols].mean(axis=0);top[2]=max(P[:cols,2].max(),top[2]);topid=len(P)
    P=np.vstack((P,top));faces.extend((topid,j,(j+1)%cols) for j in range(cols))
    def roll(P,faces,ring):
        ring=np.asarray(ring);edge=P[ring].copy();out=norm(edge-CENTER)
        for width,drop in [(1.5,.65),(4.1,1.0),(8.0,-1.7)]:
            new=len(P)+np.arange(len(ring));strip=edge-width*out;strip[:,2]-=drop;P=np.vstack((P,strip))
            for i in range(len(ring)):
                k=(i+1)%len(ring);faces.extend(((ring[i],new[i],ring[k]),(ring[k],new[i],new[k])))
            ring=new
        anchor=P[ring].mean(axis=0);anchor[2]=365.;idx=len(P);P=np.vstack((P,anchor))
        faces.extend((ring[i],idx,ring[(i+1)%len(ring)]) for i in range(len(ring)))
        return P,np.asarray(faces,dtype='i4')
    P,F=roll(P,faces,np.arange((rows-1)*cols,rows*cols))
    geo=vertex_normals(P,F);rad=norm(P-CENTER)
    if np.median((geo*rad).sum(axis=1))<0:F=F[:,::-1].copy();geo=-geo
    samples=[]
    def insert(uvs):
        for a,t in uvs:
            if not .024<t<.976:continue
            # Place two or more rings around major rims, using true world-space
            # separation to avoid repeated samples from adjacent source views.
            point=pos(np.array([[a,t]]))[0]
            if samples and np.min(np.linalg.norm(np.array([v[2] for v in samples])-point,axis=1))<2.9:continue
            samples.append((float(a%W),float(t),point))
    # A quasi-uniform base preserves forehead and side silhouettes between traces.
    for row in range(1,14):
        t=row/14;number=max(6,round(36*np.sin(t*2.35)))
        aa=(np.arange(number)+.5*(row%2))*W/number;insert(np.column_stack((aa,np.zeros(number)+t)))
    for k,cam in enumerate(views[:4]):
        z,ids,bar=draw(P,F,cam);z=extend(z,ids>=0)
        for j,mask in enumerate(mattes[cam.name]):
            cc,num=nd.label(nd.binary_closing(nd.binary_opening(mask),iterations=2))
            if not num:continue
            count=np.bincount(cc.ravel());count[0]=0;chosen=nd.binary_fill_holes(cc==count.argmax())
            curves=find_contours(nd.gaussian_filter(chosen.astype(float),1.45),.5)
            if not curves:continue
            line=max(curves,key=len);cent=np.mean(line,axis=0)
            # Sample at roughly nine reference pixels along the true lock edge.
            dist=np.r_[0,np.cumsum(np.linalg.norm(np.diff(line,axis=0),axis=1))]
            for inset in (.99,.78):
                step=10.5 if inset>.9 else 18.5
                at=np.arange(0,dist[-1],step)
                pix=np.stack([np.interp(at,dist,line[:,dim]) for dim in (0,1)],axis=-1)
                pix=cent+(pix-cent)*inset;y,x=pix.T;d=sample(z,x,y)
                world=(x+cam.left-cam.cx)[:,None]*cam.right+(505-48-y)[:,None]*cam.top+d[:,None]*cam.eye
                normal=norm(world-CENTER);active=(normal@cam.eye)>.49
                insert(uv_of(world[active]))
    U=np.array([(v[0],v[1]) for v in samples])
    # Remove the nearest redundant detail samples to keep a fixed triangle budget.
    budget=944
    if len(U)>budget:
        sel=np.ones(len(U),bool);xyz=pos(U)
        while sel.sum()>budget:
            active=np.flatnonzero(sel);tree=cKDTree(xyz[active]);dist,idx=tree.query(xyz[active],k=3)
            # Keep the more isolated of neighboring points. The quasi-uniform
            # beginning of the list is reserved for otherwise unobserved angles.
            score=dist[:,1]+.42*dist[:,2];score[active<220]+=4.1
            sel[active[np.argmin(score)]]=False
        U=U[sel]
    nb=56
    for j in range(budget-len(U)):
        # Deterministic largest-gap fill on the same spherical field.
        pool=uv[::29];tree=cKDTree(pos(U));d=tree.query(pos(pool))[0];d[(pool[:,1]<.023)|(pool[:,1]>.976)]=-1;U=np.vstack((U,pool[np.argmax(d)]))
    top_ring=np.column_stack((np.arange(12)*W/12,np.zeros(12)));edge_ring=np.column_stack((np.arange(nb)*W/nb,np.ones(nb)))
    U=np.vstack((top_ring,U,edge_ring));n=len(U)
    cp=np.vstack((U+[-W,0],U,U+[W,0]));projected=cp.copy();projected[:,1]*=190
    tri=Delaunay(projected).simplices;mean=cp[tri,0].mean(axis=1)
    tri=tri[(mean>=0)&(mean<W)]%n;tri=tri[np.array([len(set(row))==3 for row in tri])]
    low=pos(U);lf=tri.tolist();tid=len(low);low=np.vstack((low,top))
    lf.extend((tid,j,(j+1)%12) for j in range(12))
    low,lf=roll(low,lf,np.arange(n-nb,n));lg=vertex_normals(low,lf)
    dot=(lg[:n]*norm(low[:n]-CENTER)).sum(axis=1)
    # Orient every surface strip consistently, including Blender's glTF backface behavior.
    fn=np.cross(low[lf[:,1]]-low[lf[:,0]],low[lf[:,2]]-low[lf[:,0]])
    hi=cKDTree(P).query(low[lf].mean(axis=1))[1]
    flip=np.sum(fn*geo[hi],axis=1)<0;lf[flip]=lf[flip,::-1]
    pnorm=geo[cKDTree(P).query(low)[1]]
    N=np.zeros_like(P);C=np.zeros_like(P);scores=np.zeros(len(P))
    for v in views:
        z,ids,_=draw(P,F,v);z=extend(z,ids>=0);x=P@v.right+v.cx-v.left;y=505-P[:,2]-48;m=sample(v.sdf,x,y)
        dz=np.maximum(0,sample(nd.gaussian_filter(z,.7),x,y)-P@v.eye)
        a=np.maximum(0,rad@v.eye);b=np.maximum(0,geo@v.eye)
        w=(.001+.9*a**6+.1*b**4)*np.exp(-.5*(dz/4)**2)*sm(m,-2,3)
        if v.name=='quarter':w*=.48
        local=sample(v.neural_normal,x,y);n=norm(local[:,0:1]*v.right+local[:,1:2]*v.top+local[:,2:3]*v.eye)
        N+=w[:,None]*n
        soft=.67+.62*np.maximum(0,local@norm(np.array([-.4,.73,.56])))
        C+=w[:,None]*np.clip((sample(v.rgb,x,y)+5)/soft[:,None]**.44,16,143);scores+=w
    conf=sm(scores,.005,.08)[:,None];N=norm(.78*conf*norm(N)+(1-.78*conf)*geo)
    C=conf*C/np.maximum(scores[:,None],1e-8)+(1-conf)*np.array([53.,44.,43.])
    dz=451.-low[:,2].max()
    for p in (P,low):p[:,2]+=dz*sm(p[:,2],417,447)
    print('trace-conforming retopology',len(P),len(F),len(low),len(lf),flush=True)
    return dict(xyz=(P/S).astype('f4'),triangles=F.astype('i4'),normals=N.astype('f4'),pigment=np.uint8(np.clip(np.rint(C),0,255)),piece=np.zeros(len(F),'i2'),runtimeXYZ=(low/S).astype('f4'),runtimeTriangles=lf.astype('i4'),runtimeNormals=pnorm.astype('f4'),runtimePiece=np.zeros(len(lf),'i2'),fit=seed['fit'])
