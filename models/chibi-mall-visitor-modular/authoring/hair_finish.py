"""Resolve crown lift and occluding ear/fringe boundaries against the physical head."""
import numpy as np
from scipy import ndimage as nd
from scipy.interpolate import CubicSpline, PchipInterpolator
from skimage.measure import marching_cubes
from hair_solid import raster_volume
from hair_raster import draw
from hair_envelope import vertex_normals
from reconstruct_hair import S, norm, sample, sm

# Each row locates one 3D point by corresponding front x, profile x, reference row,
# along-scalp radius, and outward radius, all in original reference pixels.
CREST=[(415,851,79,3,2.2),(411,846,69,7,4.9),(401,840,62.5,10,6.0),(386,836,60.4,12,6.6),
       (371,840,63.2,12,5.8),(354,849,70,10.5,5.0),(337,860,77.3,9,4.1),(326,867,80.4,6,3.3),(317,870,78.2,.65,.6)]
RETURN=[(417,849,84,2.2,2),(418,857,75,6,4.7),(425,866,70.5,8.7,5.7),(432,877,72.5,8.3,5.1),
        (440,887,79,7.6,4.6),(449,895,89.5,6.1,3.8),(458,901,101,2.5,2),(465,901,110,.6,.6)]
FRONT_FAN=[(415,800,88,4.2,2.4),(409,804,77,8.1,4.7),(397,804,71,10.4,5.3),(382,800,72,12,5.2),(366,795,81,12.3,5.6),
           (351,795,94,11.5,5.6),(335,798,108,11.5,5.5),(319,810,118.5,8.5,4.4),(305,829,121.6,4.9,3.1),(295,844,118.6,.6,.6)]

def sweep(data,count=101):
    v=np.array(data,float);raw=np.column_stack((v[:,0]-390.5,v[:,1]-856.5,505-v[:,2]))
    curve=np.r_[0,np.cumsum(np.linalg.norm(np.diff(raw,axis=0),axis=1))]
    t=np.linspace(0,curve[-1],count);spl=CubicSpline(curve,raw,axis=0,bc_type='natural')
    center=spl(t);axis=norm(spl(t,1))
    outward=norm(center-[0,2,366]);outer=norm(outward-axis*np.sum(axis*outward,axis=1,keepdims=True))
    side=norm(np.cross(axis,outer));a=PchipInterpolator(curve,v[:,3])(t);b=PchipInterpolator(curve,v[:,4])(t)
    theta=np.linspace(0,2*np.pi,30,endpoint=False)
    p=center[:,None,:]+side[:,None,:]*a[:,None,None]*np.cos(theta)[None,:,None]+outer[:,None,:]*b[:,None,None]*np.sin(theta)[None,:,None]
    faces=[];m=len(theta)
    for i in range(len(t)-1):
        for j in range(m):
            l=i*m+j;r=i*m+(j+1)%m
            faces.extend(((l,r,l+m),(r,r+m,l+m)))
    for j in range(1,m-1):faces.extend(((0,j+1,j),((count-1)*m,(count-1)*m+j,(count-1)*m+j+1)))
    return p.reshape(-1,3),np.array(faces,'i4')

def finish(views,seed,skin):
    p=seed['xyz']*S;f=seed['triangles']
    origin=np.array([-114,-114,261.]);h=.75;origin=np.round(origin/h)*h;shape=(305,310,265)
    volume=np.zeros(shape,bool);raster_volume(p,f,volume,origin,h)
    field=(nd.distance_transform_edt(volume)-nd.distance_transform_edt(~volume)).astype('f4')*h
    xx=origin[0]+np.arange(shape[0])*h;yy=origin[1]+np.arange(shape[1])*h
    x,y=np.meshgrid(xx,yy,indexing='ij')
    for i in range(shape[2]):
        row=505-origin[2]-h*i
        if row<92:
            dome=62.2+.00275*(x+3)**2+.00265*(y-4)**2
            # The general crown recedes into a convex scalp under the main tuft.
            # A tapered transition retains the measured frontal and occipital arches.
            field[:,:,i]=np.minimum(field[:,:,i],row-dome+31*sm(row,68,91))
    for curve in (CREST,RETURN,FRONT_FAN):
        mask=np.zeros(shape,bool);pp,ff=sweep(curve)
        raster_volume(pp,ff,mask,origin,h)
        sd=(nd.distance_transform_edt(mask)-nd.distance_transform_edt(~mask)).astype('f4')*h
        delta=np.maximum(0,2.1-np.abs(field-sd))
        field=np.maximum(field,sd)+delta*delta/(4*2.1)
    inputs=[]
    for v in views[:4]:
        old,ids,_=draw(p,f,v);sk,_,_=draw(*skin,v)
        observed=(ids>=0)&(old>=sk)
        diff=v.mask&~observed
        expand=nd.gaussian_filter(nd.maximum_filter(diff.astype(float),9),1.8)
        known=(ids>=0)&v.mask
        nearest=nd.distance_transform_edt(~known,return_distances=False,return_indices=True)
        smooth=nd.gaussian_filter(np.clip(old[tuple(nearest)],-110,130),2.1)
        d=.49*np.clip(smooth,v.dhair-8.,v.dhair+8.)+.51*v.dhair
        # All fringe/ear-side tips must lie in front of the physical head when
        # visible against the skin. The rear nape is naturally occluded by the ear.
        valid=sk>-200.
        lift=np.where(v.mask&valid,np.maximum(0,sk+3.3-d),0.)
        d+=nd.gaussian_filter(nd.maximum_filter(lift,5),1.3)
        inputs.append((v,sk,d,expand))
    for iz in range(shape[2]):
        row=505-origin[2]-h*iz
        if row<86 or row>228:continue
        sup=np.full(x.shape,-100.);cut=np.full(x.shape,100.)
        for index,(v,sk,d,ex) in enumerate(inputs):
            u=v.right[0]*x+v.right[1]*y+v.cx-v.left;vv=row-48.;dep=v.eye[0]*x+v.eye[1]*y
            m=sample(v.sdf,u,vv);skinD=sample(sk,u,vv);observed=sample(d,u,vv)
            rf=sm(row,105,142)
            # Corrections are strongest on the face side of a grazing temple and
            # at the nape; the four views need not have identical hidden anatomy.
            extent=sample(ex,u,vv)
            if index==0:
                zone=(sm(row,102,124)*(1-sm(row,190,202)))*(1-sm(np.abs(u+v.left-390.5),93,101))
            elif index in (1,3):zone=sm(row,106,129)
            else:zone=sm(row,155,184)
            near=observed-dep
            local=np.minimum.reduce((m*.86+.15,near,8.8+.62*np.maximum(m,0)-near,extent*19.-2+np.zeros_like(x)))
            sup=np.maximum(sup,local-55*(1-zone))
            # Carve the observed negative space (ear opening, temple, nape and outside contour).
            # Hair lying behind the real surface of the head stays in the volume.
            allowance=.85+2.5*(1-rf)
            limit=np.maximum(m+allowance,skinD-dep-1.35)
            cut=np.minimum(cut,limit+24*(1-zone))
        field[:,:,iz]=np.minimum(np.maximum(field[:,:,iz],sup),cut)
    field=nd.gaussian_filter(field,1.48)
    lab,num=nd.label(field>0);cnt=np.bincount(lab.ravel());cnt[0]=0
    field[(lab!=0)&(lab!=cnt.argmax())]=-1
    P,F,_,_=marching_cubes(field,0,spacing=(h,h,h),allow_degenerate=False);P+=origin
    geo=vertex_normals(P,F);rad=norm(P-[0,2,366])
    if np.median(np.sum(rad*geo,axis=1))<0:F=F[:,::-1].copy();geo=-geo
    rgb=np.zeros_like(P);N=np.zeros_like(P);score=np.zeros(len(P))
    for v in views:
        dep,ix,_=draw(P,F,v);u=P@v.right+v.cx-v.left;vv=505-P[:,2]-48
        m=sample(v.sdf,u,vv);depth=sample(nd.maximum_filter(dep,3),u,vv)-P@v.eye
        facing=np.maximum(0,rad@v.eye);inc=np.maximum(0,geo@v.eye)
        w=(.002+.90*facing**6+.10*inc**5)*np.exp(-.5*(np.maximum(0,depth)/4.)**2)*sm(m,-2,3)
        if v.name=='quarter':w*=.48
        n=sample(v.neural_normal,u,vv);obs=norm(n[:,0:1]*v.right+n[:,1:2]*v.top+n[:,2:3]*v.eye)
        N+=w[:,None]*obs
        lum=.67+.62*np.maximum(0,n@norm(np.array([-.40,.73,.56])))
        rgb+=w[:,None]*np.clip((sample(v.rgb,u,vv)+5)/lum[:,None]**.44,16,146);score+=w
    conf=sm(score,.005,.075)[:,None];normal=norm(.89*conf*norm(N)+(1-.89*conf)*geo)
    pigment=conf*rgb/np.maximum(score[:,None],1e-8)+(1-conf)*np.array([53,44,43])
    height=P[:,2];height+=(451-height.max())*sm(height,420,447)
    print('finished solid',len(P),len(F),P.min(axis=0),P.max(axis=0),flush=True)
    return dict(xyz=(P/S).astype('f4'),triangles=F.astype('i4'),normals=normal.astype('f4'),pigment=np.uint8(np.clip(np.rint(pigment),0,255)),fit=seed['fit'])
