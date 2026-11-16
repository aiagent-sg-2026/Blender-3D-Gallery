"""Sculpt the visible lock shoulders in depth while preserving adjacent registered outlines."""
import numpy as np
from scipy import ndimage as nd, sparse
from scipy.sparse.linalg import spsolve
from hair_raster import draw
from hair_envelope import vertex_normals
from hair_fit import LOCKS
from hair_strands import OUTER, SIDE_BOTTOM, REAR_LEFT, REAR_RIGHT
from reconstruct_hair import norm, sm, sample, S

def extend(image,mask):
    idx=nd.distance_transform_edt(~mask,return_distances=False,return_indices=True)
    return image[tuple(idx)]

def ramp(cam):
    yy,xx=np.indices(cam.mask.shape);xx=xx+cam.left;yy=yy+48
    height=np.zeros(cam.mask.shape,float)
    if cam.name=='front':
        paths=[LOCKS['front'][i] for i in (9,10,8,4)]+[OUTER]+[LOCKS['front'][i] for i in (3,7,5,2,1,6,0)]
    elif cam.name=='profile':
        paths=[LOCKS['profile'][i] for i in (11,9,10,7,6,8,5)]+[SIDE_BOTTOM]+[LOCKS['profile'][i] for i in (3,4,2,1,0)]
    elif cam.name=='back':
        paths=[LOCKS['back'][i] for i in (12,11,10,8,9,5,6,7)]+[REAR_LEFT,REAR_RIGHT]+[LOCKS['back'][i] for i in (3,4,2,0,1)]
    else:return height
    for path in paths:
        best=np.full_like(height,30);radii=np.zeros_like(height);along=np.zeros_like(height)
        marks=np.r_[0,np.cumsum(np.linalg.norm(np.diff(np.array(path)[:,:2],axis=0),axis=1))]
        for i,(pt,end) in enumerate(zip(path,path[1:])):
            x,y,r=pt;dx,dy,dr=np.array(end)-pt
            u=np.clip(((xx-x)*dx+(yy-y)*dy)/(dx*dx+dy*dy),0,1)
            radius=r+u*dr;d=np.hypot(xx-x-u*dx,yy-y-u*dy)/np.maximum(1.,radius)
            use=d<best;best[use]=d[use];radii[use]=radius[use];along[use]=(marks[i]+u[use]*(marks[i+1]-marks[i]))/marks[-1]
        amplitude=np.clip(.77*radii,1.1,11.8)*(.70+.30*sm(along,0,.22))
        body=(.38+.91*np.sqrt(np.maximum(0,1-best**2)))*amplitude
        valley=-.5*amplitude*np.exp(-((best-1.095)/.105)**2)
        coverage=(1-sm(best,.945,1.09))*sm(along,0,.11)
        height=(1-coverage)*height+coverage*body+(1-coverage)*valley
    return nd.gaussian_filter(height,.82)

def target_depth(base,cam,mask,pattern):
    ind=np.full(mask.shape,-1,int);ind[mask]=np.arange(mask.sum());N=cam.neural_normal
    x0=base[mask];n=len(x0);edge=np.maximum(0,nd.distance_transform_edt(mask)-1)
    weights=[];ii=[];jj=[];gg=[]
    for dim,sl in [(1,-N[...,0]),(0,N[...,1])]:
        src=(slice(None),slice(None,-1)) if dim==1 else (slice(None,-1),slice(None))
        dst=(slice(None),slice(1,None)) if dim==1 else (slice(1,None),slice(None))
        use=mask[src]&mask[dst];si=ind[src][use];sj=ind[dst][use]
        grad=sl/np.maximum(.23,N[...,2]);slope=np.clip(.5*(grad[src]+grad[dst])[use],-3.8,3.8)
        similarity=(N[src]*N[dst]).sum(axis=-1)[use]
        sharp=1-sm(similarity,.77,.97);mono=(cam.d[dst]-cam.d[src])[use]
        g=(1-.67*sharp)*slope+.67*sharp*np.clip(mono,-7,7)
        ii.append(si);jj.append(sj);weights.append(1-.38*sharp);gg.append(g)
    i=np.concatenate(ii);j=np.concatenate(jj);w=np.concatenate(weights);g=np.concatenate(gg)
    anchor=.0016+.094*np.exp(-np.minimum(edge[mask],40)/2.7)
    final=x0.copy()
    diag=np.bincount(np.r_[i,j],weights=np.r_[w,w],minlength=n)+anchor;off=-w
    A=sparse.coo_matrix((np.r_[diag,off,off],(np.r_[np.arange(n),i,j],np.r_[np.arange(n),j,i])),shape=(n,n)).tocsr()
    rhs=anchor*x0+np.bincount(np.r_[i,j],weights=np.r_[-w*g,w*g],minlength=n)
    final=spsolve(A,rhs)
    d=base.copy();d[mask]=final
    residual=d-base
    # Dark seams on either side of a traced lobe guide its shallow rolled lip.
    # The footprint and normal measurements independently locate the convex body.
    pigment=cam.rgb@np.array([.24,.64,.12]);detail=pigment-nd.gaussian_filter(pigment,6)
    var=pattern-nd.gaussian_filter(pattern,12)
    extra=.91*var+.050*np.clip(detail,-25,32)
    return extend(np.clip(residual+.84*extra,-14.5,15.8),mask)

def sculpt(views,seed,skin):
    p=seed['xyz'].astype(float)*S;f=seed['triangles'];rad=norm(p-[0,2,366])
    start=p.copy();maps=[ramp(v) for v in views]
    skinDepth=[draw(*skin,v)[0] for v in views]
    for repeat,gain in enumerate((.69,.48)):
        delta=np.zeros_like(p);ws=np.zeros_like(p);geo=vertex_normals(p,f)
        # Horizontal profile/back outlines protect the nearby geometry that is
        # actually visible from those directions during the depth solve.
        outline=np.zeros_like(p)
        for v in views[:4]:
            xx=p@v.right+v.cx-v.left;yy=505-p[:,2]-48
            m=sample(v.sdf,xx,yy)
            outline+=np.exp(-.5*(m/2.7)**2)[:,None]*(v.right**2)
        for k,v in enumerate(views):
            z,ids,_=draw(p,f,v);seen=ids>=0
            interest=(v.sdf>-.75)&seen&(z>skinDepth[k]-.6)
            if interest.sum()<60:continue
            base=extend(z,seen)
            change=target_depth(base,v,interest,maps[k])
            xx=p@v.right+v.cx-v.left;yy=505-p[:,2]-48;dep=p@v.eye
            measured=sample(change,xx,yy);deltaZ=sample(nd.gaussian_filter(base,.80),xx,yy)-dep
            mask=sample(v.sdf,xx,yy);face=np.maximum(0,rad@v.eye)
            visibility=np.exp(-.5*(np.maximum(0,deltaZ)/4.6)**2)
            weight=(.018+1.4*face**3.2)*sm(mask,-.8,3.3)*visibility*sm(geo@v.eye,-.65,.24)
            if v.name=='quarter':weight*=.16
            delta+=measured[:,None]*v.eye*weight[:,None];ws+=v.eye**2*weight[:,None]
        move=delta/(.21+ws)*gain*np.exp(-2.3*outline)
        # This smooth bounded deformation is applied to every member of an
        # intersecting neighborhood, including the underside of a visible roll.
        p+=move;rad=norm(p-[0,2,366])
        print('solid depth change px',repeat,np.percentile(np.linalg.norm(move,axis=1),[40,75,95,99]).round(2),flush=True)
    geo=vertex_normals(p,f);b=np.zeros(len(p));N=np.zeros_like(p);C=np.zeros_like(p)
    for v in views:
        z,ids,_=draw(p,f,v);seen=ids>=0;base=extend(z,seen)
        x=p@v.right+v.cx-v.left;y=505-p[:,2]-48;m=sample(v.sdf,x,y)
        distance=np.maximum(0,sample(nd.gaussian_filter(base,.85),x,y)-p@v.eye)
        align=np.maximum(0,rad@v.eye);inc=np.maximum(0,geo@v.eye)
        w=(.003+.92*align**6+.08*inc**4)*np.exp(-.5*(distance/4.)**2)*sm(m,-2,2.8)
        if v.name=='quarter':w*=.52
        n=sample(v.neural_normal,x,y);g=norm(n[:,0:1]*v.right+n[:,1:2]*v.top+n[:,2:3]*v.eye);N+=w[:,None]*g
        light=.67+.62*np.maximum(0,n@norm(np.array([-.40,.73,.56])))
        C+=w[:,None]*np.clip((sample(v.rgb,x,y)+4)/light[:,None]**.44,16,143);b+=w
    conf=sm(b,.005,.072)[:,None]
    N=norm(.83*conf*norm(N)+(1-.83*conf)*geo);C=conf*C/np.maximum(b[:,None],1e-8)+(1-conf)*np.array([53,44,43])
    height=p[:,2];height+=(451-height.max())*sm(height,420,446)
    print('normal-constrained sculpt',p.min(axis=0),p.max(axis=0),flush=True)
    return dict(xyz=(p/S).astype('f4'),triangles=f,normals=N.astype('f4'),pigment=np.uint8(np.clip(np.rint(C),0,255)),fit=seed['fit'])
