"""Retopologize the reference volume in scalp coordinates with a rolled, varying hairline."""
import numpy as np
from scipy import ndimage as nd
from reconstruct_hair import S, norm, sm, sample, fit_surface_normals

CENTER=np.array([0.,2.,366.]);AXES=np.array([89.,94.,85.])
def polar(p):
    v=(p-CENTER)/AXES
    r=np.linalg.norm(v,axis=-1)
    return np.arctan2(v[...,0],-v[...,1]),np.arccos(np.clip(v[...,2]/np.maximum(r,.001),-1,1)),r

def rings_mesh(rows,cols):
    f=[]
    for i in range(rows-1):
        for j in range(cols):
            a=i*cols+j;b=i*cols+(j+1)%cols;c=a+cols;d=b+cols
            f.extend(((a,c,b),(b,c,d)) if (i+j)%2 else ((a,c,d),(a,d,b)))
    return f

def vertex_normals(p,f):
    face=np.cross(p[f[:,1]]-p[f[:,0]],p[f[:,2]]-p[f[:,0]]);n=np.zeros_like(p)
    for v in f.T:np.add.at(n,v,face)
    return norm(n)

def coordinates(a,b):
    return np.stack(np.broadcast_arrays(np.sin(a)*np.sin(b),-np.cos(a)*np.sin(b),np.cos(b)),axis=-1)

def sculpt(views,seed):
    old=seed['xyz'].astype(float)*S
    angles,betas,radii=polar(old)
    n=288;nl=173
    theta=np.linspace(-np.pi,np.pi,n,endpoint=False)
    angular=np.mod(np.rint((angles+np.pi)*n/(2*np.pi)).astype(int),n)
    axial=np.clip(np.rint(betas*(nl-1)/np.pi).astype(int),0,nl-1)
    field=np.zeros((nl,n));np.maximum.at(field,(axial,angular),radii)
    padded=np.tile(field,(1,3))
    near=nd.distance_transform_edt(padded==0,return_distances=False,return_indices=True)
    padded=padded[tuple(near)]
    padded=nd.gaussian_filter(nd.median_filter(padded,size=(5,5)),(2.1,2))
    field=padded[:,n:2*n]
    def pos(a,b):
        ix=(a+np.pi)*n/(2*np.pi);iz=b*(nl-1)/np.pi
        r=nd.map_coordinates(np.tile(field,(1,3)),[iz,ix+n],order=1,mode='nearest',prefilter=False)
        return CENTER+AXES*r[...,None]*coordinates(a,b)
    ext=np.zeros(n)
    for i,th in enumerate(theta):
        mask=(np.abs((angles-th+np.pi)%(2*np.pi)-np.pi)<.026)&(radii>.73)&(np.hypot(old[:,0],old[:,1]-2)>21)
        ext[i]=np.percentile(betas[mask],99.5) if mask.any() else np.pi*.63
    ext=np.clip(ext,.88,np.deg2rad(163))
    ext=nd.gaussian_filter1d(nd.median_filter(ext,3,mode='wrap'),1,mode='wrap')
    measured={}
    for c in views[:3]:
        # Lowest reference hair pixel at each sheet column. Brows and eyes have
        # already been excluded. A linear extension is used only outside the trace.
        y,x=np.where(c.mask);low=np.full(c.mask.shape[1],-1.);np.maximum.at(low,x,y+48)
        good=np.flatnonzero(low>0);measured[c.name]=np.interp(np.arange(len(low)),good,low[good])
    original=ext.copy()
    for _ in range(7):
        p=pos(theta,ext);row=505-p[:,2]
        tar=np.zeros(n);w=np.zeros(n)
        for v in views[:4]:
            x,_,_=v.projection(p);direction=coordinates(theta,np.ones(n)*np.pi/2)@v.eye
            confidence=sm(direction,.25,.95)**2
            if v.name=='profile':confidence*=1.9
            lo=measured[v.name];goal=np.interp(x,np.arange(len(lo)),lo)
            tar+=confidence*goal;w+=confidence
        desired=tar/np.maximum(w,1e-8)
        delta=np.clip((desired-row)/np.maximum(20.,76*np.sin(ext)),-.09,.09)
        ext+=.62*delta
        ext=np.clip(ext,original-.34,original+.34)
        ext=np.clip(ext,.84,np.deg2rad(165))
        ext=nd.gaussian_filter1d(ext,.60,mode='wrap')
    t=np.linspace(0,1,112)
    a=np.tile(theta,(len(t),1));b=.011+(ext-.011)*t[:,None]
    p=pos(a,b)
    # The lowest visible edge curves under toward the head instead of becoming an
    # open cut plane; the underside and top pole belong to the same surface mesh.
    outward=norm(p-CENTER)
    edge=p[-1];out=outward[-1];down=norm(p[-1]-p[-2])
    for offset,drop in [(1.25,.75),(3.,1.05),(5.5,0),(8.2,-1.8)]:
        p=np.concatenate((p,(edge-offset*out+drop*down)[None]),axis=0)
    nr=len(p);p=p.reshape(-1,3);f=rings_mesh(nr,n)
    top=len(p);pole=p[:n].mean(axis=0);pole[2]=max(pole[2],450.7)
    bottom=np.mean(p[(nr-1)*n:nr*n],axis=0);bottom[2]=360.
    p=np.vstack((p,pole,bottom))
    for j in range(n):
        k=(j+1)%n;f.extend(((top,j,k),((nr-1)*n+j,top+1,(nr-1)*n+k)))
    f=np.asarray(f,dtype=np.int32)
    geom=vertex_normals(p,f);rad=norm(p-CENTER)
    if np.median(np.sum(geom*rad,axis=-1))<0:f=f[:,::-1].copy();geom=-geom
    inner=np.arange(len(p))>=(len(t)+2)*n;edgehold=np.zeros(len(p))
    edgehold[(len(t)-3)*n:(len(t)+2)*n]=.75;edgehold[inner]=1
    def attributes(p,geom):
        radial=norm(p-CENTER);N=np.zeros_like(p);colour=np.zeros_like(p);total=np.zeros(len(p))
        for v in views:
            x,y,d=v.projection(p);m=sample(v.sdf,x,y)
            distance=sample(v.dhair,x,y)-d
            alignment=np.maximum(0,radial@v.eye);local=sample(v.neural_normal,x,y)
            # A front/side/back registration is strongest near the respective
            # meridian. Smooth angular transitions keep diagonal views coherent.
            w=(.003+alignment**5)*sm(geom@v.eye,-.3,.34)*sm(m,-2,3)*np.exp(-.5*(distance/23.)**2)
            if v.name=='quarter':w*=.56
            normal=norm(local[:,0:1]*v.right+local[:,1:2]*v.top+local[:,2:3]*v.eye)
            N+=w[:,None]*normal
            shade=.67+.62*np.maximum(0,local@norm(np.array([-.40,.73,.56])))
            colour+=w[:,None]*np.clip((sample(v.rgb,x,y)+5)/shade[:,None]**.44,16,140)
            total+=w
        conf=sm(total,.006,.09)[:,None]
        target=norm(.94*conf*norm(N)+(1-.94*conf)*geom)
        pig=conf*colour/np.maximum(total[:,None],1e-8)+(1-conf)*np.array([53.,43.,42.])
        return target,pig,conf[:,0]
    for it in range(3):
        target,pig,conf=attributes(p,geom)
        p=fit_surface_normals(p,f,geom,target,conf*(1-edgehold),1.8)
        geom=vertex_normals(p,f)
    target,pig,conf=attributes(p,geom)
    # The top is uniquely anchored by the 1.30 m hair-tip datum.
    z=p[:,2];z+=(451.-z.max())*sm(z,414.,450.)
    print("parametric sculpt",len(p),len(f),p.min(axis=0),p.max(axis=0),flush=True)
    return dict(xyz=(p/S).astype('f4'),triangles=f,normals=target.astype('f4'),pigment=np.uint8(np.clip(np.rint(pig),0,255)),fit=np.array([v.fit for v in views]))
