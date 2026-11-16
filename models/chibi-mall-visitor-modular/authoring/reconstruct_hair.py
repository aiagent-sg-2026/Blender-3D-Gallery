"""Fuse registered depth/normal measurements from the supplied turnaround into a 3D hair sculpt.

This offline authoring step operates in reference pixels (451 px = 1.30 m).
The Blender entry point reads the frozen result, so the optional measurement
models, their weights and this fitting environment are not runtime dependencies.
"""
import argparse
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage as nd
from scipy.optimize import least_squares
from scipy import sparse
from scipy.sparse.linalg import spsolve, cg
from hair_occlusion import read_face,depth_image
from skimage.measure import marching_cubes
from hair_reference import Study
from skull_profile import skull
from hair_reference import LEVELS,AXES,section_curve,nape_section
S=451/1.3
REGIONS={'front':273,'profile':748,'back':969,'quarter':36}
CAMS=[('front',0,390.5,1),('profile',90,856.5,1),('back',180,1080.5,1),('profile',-90,856.5,-1),('quarter',-28,145.,1)]
def norm(x):
    return x/np.maximum(np.linalg.norm(x,axis=-1,keepdims=True),1e-8)
def sm(x,a,b):
    v=np.clip((x-a)/(b-a),0,1);return v*v*(3-2*v)
def sample(a,x,y):
    x,y=np.broadcast_arrays(x,y)
    ix=np.clip(x,0,a.shape[1]-1.00001);iy=np.clip(y,0,a.shape[0]-1.00001)
    j=iy.astype(np.int32);i=ix.astype(np.int32);fy=iy-j;fx=ix-i
    if a.ndim==3:fy=fy[...,None];fx=fx[...,None]
    return (a[j,i]*(1-fx)+a[j,i+1]*fx)*(1-fy)+(a[j+1,i]*(1-fx)+a[j+1,i+1]*fx)*fy

def integrate_normals(depth,normal,mask):
    """Screened integration of visible flow normals, preserving measured depth jumps."""
    ids=np.full(mask.shape,-1,int);ids[mask]=np.arange(mask.sum())
    ii=[];jj=[];weights=[];values=[]
    nz=np.maximum(.23,normal[...,2])
    for dim,slope in [(1,-normal[...,0]/nz),(0,normal[...,1]/nz)]:
        src=(slice(None),slice(None,-1)) if dim==1 else (slice(None,-1),slice(None))
        dst=(slice(None),slice(1,None)) if dim==1 else (slice(1,None),slice(None))
        both=mask[src]&mask[dst]
        i=ids[src][both];j=ids[dst][both]
        grad=(.5*(slope[src]+slope[dst]))[both]
        measured=(depth[dst]-depth[src])[both]
        similarity=np.sum(normal[src]*normal[dst],axis=-1)[both]
        hard=1-sm(similarity,.63,.94)
        desired=(1-hard)*np.clip(grad,-3.4,3.4)+hard*measured
        ii.append(i);jj.append(j);weights.append(1-.63*hard);values.append(desired)
    i=np.concatenate(ii);j=np.concatenate(jj);w=np.concatenate(weights);g=np.concatenate(values);n=int(mask.sum())
    lam=.011
    diag=np.bincount(np.r_[i,j],weights=np.r_[w,w],minlength=n)+lam
    L=sparse.coo_matrix((np.r_[diag,-w,-w],(np.r_[np.arange(n),i,j],np.r_[np.arange(n),j,i])),shape=(n,n)).tocsr()
    rhs=lam*depth[mask]+np.bincount(np.r_[i,j],weights=np.r_[-w*g,w*g],minlength=n)
    result=depth.copy();result[mask]=spsolve(L,rhs)
    return result

class Camera:
    def __init__(self,study,normal,depth,im,name,theta,cx,mirror):
        self.name=name;self.cx=cx;self.left=REGIONS[name];self.mirror=mirror
        a=np.deg2rad(theta)
        self.eye=np.array([np.sin(a),-np.cos(a),0]);self.right=np.array([np.cos(a),np.sin(a),0])*mirror
        self.top=np.array([0,0,1]);self.sdf=np.full(depth.shape,-80.,dtype='f4')
        oy=1;ox=study.left-self.left
        width=min(study.sdf.shape[1],self.sdf.shape[1]-ox)
        self.sdf[oy:oy+study.sdf.shape[0],ox:ox+width]=study.sdf[:,:width]
        self.mask=self.sdf>0
        fig=im[48:48+depth.shape[0],self.left:self.left+depth.shape[1]].astype(float)
        skin=(fig[...,0]-fig[...,1]>18)&(fig[...,0]>130)&(fig[...,2]<227)
        union=nd.binary_fill_holes(nd.binary_closing(self.mask|skin,iterations=2))
        lab,_=nd.label(union);union=lab==(np.argmax(np.bincount(lab.ravel())[1:])+1)
        self.whole=nd.distance_transform_edt(union)-nd.distance_transform_edt(~union)
        yp,xp=np.indices(depth.shape);row=yp+48;u=xp+self.left-cx
        rx,ry,xc,yc=(section_curve(row,LEVELS,data) for data in AXES)
        horiz=rx if name in ('front','back') else ry if name=='profile' else (rx+ry)/2
        depthradius=ry if name in ('front','back') else rx if name=='profile' else (rx+ry)/2
        offset=xc if name=='front' else -xc if name=='back' else yc if name=='profile' else xc*.8-yc*.57
        center=-yc if name=='front' else yc if name=='back' else 0.
        ref=center+depthradius*np.sqrt(np.clip(1-((u-offset)/horiz)**2,.035,1))
        if name=='back':
            mid,half,wide=nape_section(row)
            nape=mid+half*np.sqrt(np.maximum(.025,1-(u/np.maximum(wide,2))**2))
            f=sm(row,150,188);ref=(1-f)*ref+f*nape
        good=(self.sdf>2)&(row>58)&(row<222)&(depth>1.6)
        design=np.stack((depth,np.ones(depth.shape),u/85,(row-133)/80),axis=-1)
        X=design[good][::4];y=ref[good][::4]
        solution=least_squares(lambda b:X@b-y,[49,-130,0,0],loss="soft_l1",f_scale=7,bounds=([31,-260,-25,-27],[78,-40,25,27])).x
        self.d=(design@solution).astype('f4')
        nearest=nd.distance_transform_edt(~self.mask,return_distances=False,return_indices=True)
        # Extrapolate only hair attributes at an outline. Skin/background pixels are
        # separately used as visibility constraints and can never become hair pigment.
        integrated=integrate_normals(self.d,normal,self.mask)
        self.dhair=nd.gaussian_filter(integrated[tuple(nearest)],.48)
        rr=np.arange(depth.shape[0])+48
        axes=np.array([skull((505-r)/S) for r in rr])*S
        hx,hy,cy=axes[:,0:1],axes[:,1:2],axes[:,2:3]
        if name in ("front","back"):
            inner=np.abs(u)/hx
            skinfront=hy*np.maximum(0,1-inner**2.32)**(1/2.32)+(cy if name=="back" else -cy)
        elif name=="profile":
            inner=np.abs(u-cy)/hy;skinfront=hx*np.maximum(0,1-inner**2.32)**(1/2.32)
        else:
            # Ellipse in rotated screen coordinates; its positive ray intersection.
            ang=np.deg2rad(theta);ss,cc=np.sin(ang),np.cos(ang)
            u0=u-cy*ss
            aa=ss**2/hx**2+cc**2/hy**2
            bb=u0*ss*cc*(1/hx**2-1/hy**2)
            disc=bb**2-aa*(u0**2*(cc**2/hx**2+ss**2/hy**2)-1)
            inner=np.where(disc>=0,0,2)
            skinfront=(-bb+np.sqrt(np.maximum(0,disc)))/aa-cy*cc
        valid=(inner<.995)&(row>67)&(row<229)
        # Raise the entire local lock when necessary, retaining its measured relative
        # relief. The actual face mesh determines clearance at the part and behind the ears.
        need=np.where(valid&self.mask,np.maximum(0,skinfront+5.8-self.dhair),0.)
        lift=nd.gaussian_filter(nd.maximum_filter(need,9),2.4)
        self.dhair+=lift
        self.d=np.where(valid&~self.mask,np.maximum(self.d,skinfront+1.0),self.d)
        self.neural_normal=norm(nd.gaussian_filter(normal[tuple(nearest)],(.38,.38,0)))
        self.rgb=nd.gaussian_filter(fig[tuple(nearest)],(.64,.64,0))
        self.fit=solution
        print(name,theta,'metric fit',solution.round(2),flush=True)
    def project(self,x,y,row):
        u=self.cx+self.right[0]*x+self.right[1]*y
        # Align the reference's ear-side tips to their shared near-temple depth.
        tip=sm(row,155,178)*(1-sm(row,189,200))
        if self.name=="profile":u=u+5.*tip*np.exp(-((u-829)/17)**2)
        if self.name=="front":u=u-3.5*tip*np.sign(u-self.cx)*np.exp(-((np.abs(u-self.cx)-58)/14)**2)
        return u-self.left,row-48,self.eye[0]*x+self.eye[1]*y
    def projection(self,vertex):
        return self.project(vertex[:,0],vertex[:,1],505-vertex[:,2])

def fit_surface_normals(p,f,geom,target,strength,spacing):
    # Screened normal integration on the actual triangle edges. This puts curl
    # curvature into the editable mesh before any normal texture is produced.
    edges=np.sort(np.vstack((f[:,[0,1]],f[:,[1,2]],f[:,[2,0]])),axis=1)
    edges=np.unique(edges,axis=0);i,j=edges.T
    N=norm(target[i]+target[j]);alignment=geom[i]*N
    ai=np.clip(alignment.sum(axis=1),.32,1);aj=np.clip((geom[j]*N).sum(axis=1),.32,1)
    edge=p[j]-p[i];w=np.minimum(strength[i],strength[j])*np.clip(spacing/np.maximum(.24,np.linalg.norm(edge,axis=1)),.35,2.)
    b=-np.sum(edge*N,axis=1)
    k=.19
    diag=np.bincount(np.r_[i,j],weights=np.r_[w*ai**2+k,w*aj**2+k],minlength=len(p))+.013+(1-strength)**2*.8
    off=-w*ai*aj-k
    lhs=sparse.coo_matrix((np.r_[diag,off,off],(np.r_[np.arange(len(p)),i,j],np.r_[np.arange(len(p)),j,i])),shape=(len(p),len(p))).tocsr()
    rhs=np.bincount(np.r_[i,j],weights=np.r_[-ai*w*b,aj*w*b],minlength=len(p))
    shift,_=cg(lhs,rhs,x0=np.zeros(len(p)),rtol=.001,maxiter=130)
    shift=np.clip(shift,-4.7,6.2)*strength*.88
    print("fitted relief px",np.percentile(shift,[1,25,50,75,99]).round(2),flush=True)
    return p+geom*shift[:,None]

def solve(im,obs,step,face):
    views=[]
    for name,angle,cx,mirror in CAMS:
        st=Study(im,name);d=np.load(obs/(name+'-depth.npy'));n=np.load(obs/(name+'-normal.npy'))
        camera=Camera(st,n,d,im,name,angle,cx,mirror)
        camera.skin=depth_image(face,camera,d.shape)
        views.append(camera)
    axes=[np.arange(-105,105+step,step),np.arange(-109,112+step,step),np.arange(48,232+step,step)]
    x,y=np.meshgrid(axes[0],axes[1],indexing='ij');radius=np.sqrt(x*x+y*y+.01)
    volume=np.empty(tuple(len(a) for a in axes),'f4')
    for iz,row in enumerate(axes[2]):
        visibility=np.full(x.shape,170.);protect=np.full(x.shape,-120.);fill=np.full(x.shape,-120.);carve=np.full(x.shape,200.);wx=np.zeros_like(x);wd=np.zeros_like(x)
        for i,v in enumerate(views):
            xx,yy,d=v.project(x,y,row)
            m=sample(v.sdf,xx,yy);full=sample(v.whole,xx,yy)
            observed=sample(v.dhair,xx,yy);delta=observed-d
            facing=d/radius
            if v.name!="quarter":
                skin=sample(v.skin,xx,yy)
                # Anything in front of the actual opaque face must respect the hair
                # boundary observed from this view. The back volume remains behind it.
                margin=1.45 if v.name=="front" else 1.9
                clearance=np.maximum(m+margin,skin-d-1.8)
                visibility=np.minimum(visibility,clearance)
                visibility=np.minimum(visibility,full+2.5)
            # Union of thick visible patches supplies non-convex fringe tips; visibility
            # constraints remove material that would have hidden an observed face or ear.
            thickness=29 if v.name!='quarter' else 19
            patch=np.minimum.reduce([m*.83,delta,thickness-delta,(facing-.08)*80+5])
            if v.name=='quarter':patch-=2.0
            fill=np.maximum(fill,patch)
            # Preserve short hand-identified outward turns which another panel can
            # occlude by a few pixels. Each remains a measured solid, tapered in depth.
            spots={"front":[(317,80),(295,119),(295,155),(307,165),(484,136),(474,165)],
                   "back":[(994,109),(986,140),(1003,164),(1172,118),(1172,154)],
                   "profile":[(951,123),(947,164),(933,193)]}
            if v.name in spots:
                pattern=np.maximum.reduce([17-np.sqrt((xx+v.left-u)**2+(row-r)**2) for u,r in spots[v.name]])
                shell=np.minimum.reduce((m*.92,delta-.6,2.7+.8*np.maximum(m,0)-delta,pattern,(facing-.025)*75+3))
                protect=np.maximum(protect,shell)
            primary=np.maximum(facing,0)**3
            slack=2.4+8*(1-primary)+(3. if v.name=='quarter' else 0.)
            skinDepth=sample(v.d,xx,yy)
            constraint=np.maximum(m+(.8 if i==0 else 1.4),skinDepth-d-1.)
            # Far-side silhouettes differ by several pixels across the sheet. At an
            # observed frontal/side edge preserve the local view's trace.
            carve=np.minimum(carve,np.minimum(full+3.6+(3 if v.name=='quarter' else 0),constraint+slack*(1-primary)))
            carve=np.minimum(carve,delta+slack+np.maximum(-m,0)*2)
            weight=np.maximum(facing,0)**10*sm(m,-2,5)*(0.58 if v.name=='quarter' else 1.)
            wx+=weight;wd+=weight*delta
        outer=np.where(wx>.1,wd/np.maximum(wx,.001)+1.3,90.)
        field=np.minimum.reduce((fill,carve,outer))
        # The basal haircut fills the scalp underneath the overlapping locks. Its
        # boundary retreats above the forehead and forward of the visible ear.
        rx,ry,cy=np.array(skull((505-row)/S))*S
        radial=((np.abs(x)/(rx+4.5))**2.32+(np.abs(y-cy)/(ry+4.5))**2.32)**(1/2.32)
        angle=np.rad2deg(np.arctan2(x,-(y-cy)))
        hairline=np.interp(angle,[-180,-144,-119,-100,-89,-72,-52,-35,-21,-8,5,17,28,42,60,76,90,101,120,145,180],
                           [225,220,208,182,160,153,145,139,131,128,115,114,118,137,148,153,162,184,209,221,225])
        base=np.minimum((1-radial)*min(rx+4.5,ry+4.5),hairline-row)
        if 64<row<228:field=np.maximum(field,base)
        if 53<row<120:
            hr,hf,cx,cc=(float(section_curve(row,LEVELS,xs)) for xs in AXES)
            cr=((x-cx)/(hr*.91))**2+((y-cc)/(hf*.89))**2
            core=(1-np.sqrt(cr))*min(hr,hf)
            field=np.maximum(field,np.minimum(core,120-row))
        field=np.maximum(field,protect-.15)
        if row>142:
            mid,half,wide=nape_section(row)
            if min(half,wide)>.1:
                growth=sm(row,145,185)
                half=half*(.48+.48*growth);wide=wide*(.65+.31*growth);mid-=12*(1-growth)
                naper=((x/wide)**2+((y-mid)/half)**2)**.5
                field=np.maximum(field,np.minimum((1-naper)*min(half,wide),row-142))
        if row>159:
            front=views[0];side=views[1];fu,fy,_=front.project(x,y,row);pu,py,_=side.project(x,y,row)
            frontMask=sample(front.sdf,fu,fy);sideMask=sample(side.sdf,pu,py)
            temple=np.maximum.reduce((np.minimum(frontMask+2.8,sideMask+2.6),y+4,168-row+np.zeros_like(x)))
            field=np.minimum(field,temple)
        if row>190:
            mid,half,wide=nape_section(row)
            field=np.minimum(field,np.maximum(y-(mid-half-2),195-row))
        volume[:,:,iz]=np.minimum(field,visibility)
    volume=nd.gaussian_filter(volume,1.04)
    lab,n=nd.label(volume>0);counts=np.bincount(lab.ravel());counts[0]=0
    remove=(lab!=0)&(counts[lab]<80)
    volume[remove]=-1.2
    v,f,_,_=marching_cubes(volume,level=0.,spacing=(step,step,step),gradient_direction='ascent',allow_degenerate=False)
    world=v+np.array([a[0] for a in axes]);world[:,2]=505-world[:,2]
    # The row-to-height reflection changes winding. Orient against volume gradients.
    geom=np.zeros_like(world)
    fn=np.cross(world[f[:,1]]-world[f[:,0]],world[f[:,2]]-world[f[:,0]])
    for k in range(3):np.add.at(geom,f[:,k],fn)
    geom=norm(geom)
    radial=world-np.array([0,0,372])
    if np.median(np.sum(radial*geom,axis=-1))<0:
        f=f[:,::-1].copy();geom=-geom
    measure=np.zeros_like(world);tint=np.zeros_like(world);wtotal=np.zeros(len(world));edge_lock=np.zeros(len(world))
    for camera in views:
        xx,yy,dep=camera.projection(world);dist=sample(camera.dhair,xx,yy)-dep
        m=sample(camera.sdf,xx,yy)
        edge_lock=np.maximum(edge_lock,np.exp(-.5*(m/3.3)**2)*np.exp(-.5*(dist/12)**2))
        local=sample(camera.neural_normal,xx,yy)
        N=norm(local[:,0:1]*camera.right+local[:,1:2]*camera.top+local[:,2:3]*camera.eye)
        based=norm(radial);facing=np.maximum(0,based@camera.eye)
        facing=np.maximum(facing,.34*np.maximum(0,geom@camera.eye))
        weight=(.004+facing**6)*np.exp(-.5*(dist/11.)**2)*sm(m,-3,3)
        weight*=.65 if camera.name=='quarter' else 1.
        # A normal estimate is only meaningful on the genuinely visible side.
        weight*=sm(geom@camera.eye,-.32,.30)
        colour=sample(camera.rgb,xx,yy)
        key=norm(np.array([-.40,.73,.56]))
        received=.67+.62*np.maximum(0,local@key)
        # Recover sRGB pigment from estimated diffuse illumination. Gentle bounds
        # regularize the very darkest seams and specular highlights.
        albedo=np.clip((colour+5)/received[:,None]**.44,16,130)
        tint+=weight[:,None]*albedo
        measure+=weight[:,None]*N;wtotal+=weight
    confidence=sm(wtotal,.005,.085)
    neural=norm(measure)
    normals=norm((.86*confidence[:,None])*neural+(1-.86*confidence[:,None])*geom)
    world=fit_surface_normals(world,f,geom,normals,confidence*(1-.93*edge_lock),step)
    pigment=tint/np.maximum(wtotal[:,None],1e-8)
    pigment=confidence[:,None]*pigment+(1-confidence[:,None])*np.array([48.,40.,39.])
    pigment=.88*pigment+.12*np.array([59.,49.,46.])
    # All coordinates use the same world-height scale as the rest of the character.
    print('sculpt',len(world),len(f),'raw heights',world[:,2].min()/S,world[:,2].max()/S,flush=True)
    return dict(xyz=(world/S).astype('f4'),triangles=f.astype('i4'),normals=normals.astype('f4'),pigment=np.uint8(np.clip(np.rint(pigment),0,255)),fit=np.array([v.fit for v in views]))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('reference',type=Path);p.add_argument('measurements',type=Path);p.add_argument('destination',type=Path);p.add_argument('--step',type=float,default=.9);p.add_argument('--fit-head',type=Path,required=True)
    opts=p.parse_args()
    arrays=solve(np.array(Image.open(opts.reference).convert('RGB')),opts.measurements,opts.step,read_face(opts.fit_head))
    np.savez_compressed(opts.destination,**arrays)
