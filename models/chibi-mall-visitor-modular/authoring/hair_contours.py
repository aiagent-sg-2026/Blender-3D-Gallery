"""Register a continuous crown to the visible side/front/rear mattes of the actual head."""
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
from scipy import ndimage as nd
from hair_raster import draw
from reconstruct_hair import norm, sm, sample, S
from hair_envelope import vertex_normals
from hair_fit import LOCKS

def topology(p,f):
    edges=np.sort(np.vstack((f[:,(0,1)],f[:,(1,2)],f[:,(2,0)])),axis=1)
    e=np.unique(edges,axis=0);i,j=e.T
    lengths=np.linalg.norm(p[i]-p[j],axis=1)
    w=np.clip(1.7/np.maximum(.5,lengths),.10,2.0)
    return i,j,w

def graph(i,j,w,n):
    diagonal=np.bincount(np.r_[i,j],weights=np.r_[w,w],minlength=n)
    return sparse.coo_matrix((np.r_[diagonal,-w,-w],(np.r_[np.arange(n),i,j],np.r_[np.arange(n),j,i])),shape=(n,n)).tocsr()

def match_outline(p,f,views,skin,passes=10):
    N=len(p);ii,jj,ww=topology(p,f);L=graph(ii,jj,ww,N)
    skinZ=[draw(*skin,v)[0] for v in views]
    init=p.copy()
    for it in range(passes):
        rhs=np.zeros((N,3));strength=np.zeros((N,3))
        for index,v in enumerate(views):
            hair,ids,bary=draw(p,f,v);mask=(ids>=0)&(hair>skinZ[index]-.12)
            target=v.mask
            if index==4:continue
            # Compare corresponding horizontal/vertical extents. These pin the
            # tips to their observed row as well as the overhang to its column.
            def emit(xx,yy,diff,axis,weight):
                if not len(xx):return
                tri=f[ids[yy,xx]];b=bary[yy,xx]
                diff=np.clip(diff,-12,12)
                for k in range(3):
                    vt=tri[:,k];w=weight*b[:,k]
                    for dim in range(3):
                        if abs(axis[dim])<1e-4:continue
                        np.add.at(rhs[:,dim],vt,w*diff*axis[dim]);np.add.at(strength[:,dim],vt,w*axis[dim]**2)
            for transpose,axis in ((False,v.right),(True,-v.top)):
                m=mask.T if transpose else mask;t=target.T if transpose else target
                valid=m.any(axis=1)&t.any(axis=1);rows=np.flatnonzero(valid)
                for reverse in (False,True):
                    si=m[:,::-1] if reverse else m;ti=t[:,::-1] if reverse else t
                    src=np.argmax(si[rows],axis=1);dst=np.argmax(ti[rows],axis=1)
                    if reverse:src=m.shape[1]-1-src;dst=m.shape[1]-1-dst
                    diff=dst-src
                    xx,yy=(rows,src) if transpose else (src,rows)
                    # The plateaus near the top/bottom of a curve cannot provide
                    # sensible horizontal constraints; the orthogonal pass handles them.
                    keep=np.abs(diff)<(22 if it<4 else 16)
                    w=1.25 if transpose else .95
                    if index==3:w*=.82
                    emit(xx[keep],yy[keep],diff[keep],axis,w)
            # At the ear and part the apparent boundary can be caused by skin
            # occlusion. Gently bring the observed hair forward where it is hidden.
            holes=(target&~mask)&(ids>=0)&(hair<skinZ[index]+.2)&(hair>skinZ[index]-7)
            yy,xx=np.where(holes);yy=yy[::3];xx=xx[::3]
            shift=skinZ[index][yy,xx]-hair[yy,xx]+1.35
            emit(xx,yy,shift,v.eye,.70)
        anchor=.022 if it<6 else .035
        for dim in range(3):
            system=L*.82+sparse.diags(strength[:,dim]+anchor)
            move=spsolve(system,rhs[:,dim]+.008*(init[:,dim]-p[:,dim]))
            p[:,dim]+=.76*np.clip(move,-4.6,4.6)
    return p

def bump_map(cam):
    y,x=np.indices(cam.mask.shape);x=x+cam.left;y=y+48
    field=np.zeros_like(x,float)
    for path in LOCKS.get(cam.name,[]):
        best=np.full_like(field,20.);radius=np.zeros_like(field)
        for a,b in zip(path,path[1:]):
            u,v,r=a;dx,dy,dr=np.array(b)-a
            t=np.clip(((x-u)*dx+(y-v)*dy)/(dx*dx+dy*dy),0,1)
            w=r+dr*t
            d=np.hypot(x-u-t*dx,y-v-t*dy)/np.maximum(w,.5);take=d<best
            best[take]=d[take];radius[take]=w[take]
        # Lift the plump shoulder and form a shallow occlusion crease just beyond
        # its rolled edge. Both are added to the physical sculpt.
        h=np.sqrt(np.maximum(0,1-best**2))*np.minimum(radius*.78,8)
        field=np.maximum(field,h)
    return nd.gaussian_filter(field,.85)

def form(views,base,skin):
    p=base['xyz'].astype(float)*S;f=base['triangles']
    p=match_outline(p,f,views,skin,10)
    oc=[draw(*skin,v)[0] for v in views]
    bumps=[bump_map(v) for v in views]
    radial=norm(p-[0,2,366])
    def attributes(p):
        N=np.zeros_like(p);rgb=np.zeros_like(p);score=np.zeros(len(p));relief=np.zeros(len(p));geo=vertex_normals(p,f)
        for k,v in enumerate(views):
            z,_,_=draw(p,f,v);x=p@v.right+v.cx-v.left;y=505-p[:,2]-48;d=p@v.eye
            m=sample(v.sdf,x,y);vis=sample(z,x,y)
            error=np.maximum(0,vis-d)
            incidence=np.maximum(0,geo@v.eye);region=np.maximum(0,radial@v.eye)
            w=(.001+.92*region**6+.08*incidence**5)*np.exp(-.5*(error/3.5)**2)*sm(m,-2,3)
            if v.name=='quarter':w*=.50
            local=sample(v.neural_normal,x,y);normal=norm(local[:,0:1]*v.right+local[:,1:2]*v.top+local[:,2:3]*v.eye)
            N+=w[:,None]*normal;relief+=w*sample(bumps[k],x,y)
            illum=.67+.62*np.maximum(0,local@norm(np.array([-.40,.73,.56])))
            rgb+=w[:,None]*np.clip((sample(v.rgb,x,y)+5)/illum[:,None]**.44,15,142)
            score+=w
        conf=sm(score,.004,.065)
        N=norm(.95*conf[:,None]*norm(N)+(1-.95*conf[:,None])*geo)
        C=conf[:,None]*rgb/np.maximum(score[:,None],1e-8)+(1-conf[:,None])*np.array([57,45,43])
        return N,C,conf,relief/np.maximum(score,1e-8)
    N,C,conf,relief=attributes(p)
    # Keep a reference-shaped silhouette and put depth in the broad overlapping
    # locks on the surface. The unobserved undercut uses the fitted base.
    p+=radial*((relief-1.9)*conf*.83)[:,None]
    p=match_outline(p,f,views,skin,6)
    N,C,conf,_=attributes(p)
    z=p[:,2];z+=(451-z.max())*sm(z,421.,449.)
    print('registered contour surface',len(p),len(f),p.min(axis=0),p.max(axis=0),flush=True)
    return dict(xyz=(p/S).astype('f4'),triangles=f,normals=N.astype('f4'),pigment=np.uint8(np.clip(np.rint(C),0,255)),fit=base['fit'])
