"""Join rooted curl shoulders to the fitted scalp and fair their rolled boundaries."""
import numpy as np
from scipy import ndimage as nd
from skimage.measure import marching_cubes
import trimesh
from hair_raster import draw
from hair_envelope import vertex_normals
from reconstruct_hair import S, norm, sample, sm

def raster_volume(p,f,vol,origin,pitch):
    grid=trimesh.Trimesh(vertices=p,faces=f,process=False).voxelized(pitch=pitch,method='subdivide')
    occ=grid.matrix
    # Voxelize each closed piece separately so its underside cannot open another lock.
    occ=nd.binary_fill_holes(occ)
    m=np.rint((grid.transform[:3,3]-origin)/pitch).astype(int)
    sl=tuple(slice(start,start+sz) for start,sz in zip(m,occ.shape))
    vol[sl]|=occ

def attach(views,carrier,parts,face):
    base=carrier['xyz'].astype(float)*S;bf=carrier['triangles']
    origin=np.array([-114,-114,261.]);h=.78
    origin=np.round(origin/h)*h
    vol=np.zeros((297,302,258),bool)
    raster_volume(base,bf,vol,origin,h)
    maps=[]
    for v in views:
        z,ids,_=draw(base,bf,v);inside=ids>=0
        ids=nd.distance_transform_edt(~inside,return_distances=False,return_indices=True)
        z=z[tuple(ids)];maps.append(nd.gaussian_filter(z,4.0))
    colors=('Crest','High swept fan','Low swept fan','Broad overhang','C forelock','Inner forelock','Short parted curl','Temple return','Low temple return',
            'Crown fan','Upper ear fan','Lower ear fan','Rear side flow','Outer side tip',
            'Rear crown crest','Crown hook L','Central hook','Crown hook R','Left outer tier','Right outer tier','Low inner body','Lower right tier')
    old=parts['xyz'].astype(float)*S;pf=parts['triangles'];piece=parts['piece']
    for pid,name in enumerate(parts['names'][1:],1):
        label=str(name)
        ci=int(label[0]) if label.startswith(('1 ','3 ')) else 2 if pid>=26 else 0
        key=label.split(' ',1)[1] if ci in (1,3) else label
        if key not in colors:continue
        faces=pf[piece==pid];verts,inv=np.unique(faces,return_inverse=True);idx=inv.reshape(-1,3)
        V=old[verts];n=len(V)//22
        cam=views[ci]
        xy=np.stack((V@cam.right+cam.cx,505.-V[:,2]),axis=-1).reshape(n,22,2)
        # Each ring follows the smoothed physical shell from edge to edge, including
        # its radial roll. This joins a side lock to its actual temple on both sides.
        u=xy[...,0]-cam.left;v=xy[...,1]-48.
        depth=sample(maps[ci],u,v)
        center=xy.mean(axis=1);radius=np.linalg.norm(xy[:,0]-xy[:,11],axis=1)*.5
        t=np.linspace(0,1,n);cross=np.sin(np.arange(22)*np.pi/11)
        wear=sm(t,0,.13)
        lift=(np.clip(radius*.78,1.5,9.0)*(.6+.40*wear))[:,None]*cross[None,:]-1.9
        if key in ('Crest','Rear crown crest'):lift=lift*.85
        surface=(xy[...,0:1]-cam.cx)*cam.right+(505-xy[...,1:2])*cam.top+depth[...,None]*cam.eye
        radial=norm(surface-[0,2,366])
        vector=norm(.60*radial+.40*cam.eye)
        pos=surface+vector*lift[...,None]
        raster_volume(pos.reshape(-1,3),idx,vol,origin,h)
    # A narrow rolled boundary survives. Isolated slivers, intersecting planes and
    # paper-thin edges caused by multi-view estimation are removed in world space.
    d=nd.distance_transform_edt(vol).astype('f4')-nd.distance_transform_edt(~vol).astype('f4')
    d=nd.grey_closing(d,size=(5,5,5))
    d=nd.grey_opening(d,size=(5,5,5))
    d=nd.gaussian_filter(d,1.52)
    lab,num=nd.label(d>0);counts=np.bincount(lab.ravel());counts[0]=0
    extra=(lab!=0)&(lab!=counts.argmax());d[extra]=-1.
    p,f,_,_=marching_cubes(d,0,spacing=(h,h,h),allow_degenerate=False)
    p+=origin;geom=vertex_normals(p,f)
    radial=norm(p-[0,2,366])
    if np.median(np.sum(radial*geom,axis=1))<0:f=f[:,::-1].copy();geom=-geom
    N=np.zeros_like(p);C=np.zeros_like(p);W=np.zeros(len(p))
    for v in views:
        z,ids,_=draw(p,f,v);x=p@v.right+v.cx-v.left;y=505-p[:,2]-48;m=sample(v.sdf,x,y)
        surf=nd.maximum_filter(z,3)
        dist=np.maximum(0,sample(surf,x,y)-p@v.eye)
        position=np.maximum(0,radial@v.eye);cos=np.maximum(0,geom@v.eye)
        w=(.001+.93*position**6+.07*cos**4)*np.exp(-.5*(dist/4.)**2)*sm(m,-2.,2.8)
        if v.name=='quarter':w*=.57
        local=sample(v.neural_normal,x,y)
        ns=norm(local[:,0:1]*v.right+local[:,1:2]*v.top+local[:,2:3]*v.eye)
        N+=w[:,None]*ns
        lum=.67+.62*np.maximum(0,local@norm(np.array([-.40,.73,.56])))
        C+=w[:,None]*np.clip((sample(v.rgb,x,y)+5)/lum[:,None]**.44,16,146);W+=w
    conf=sm(W,.005,.072)[:,None]
    target=norm(.90*conf*norm(N)+(1-.90*conf)*geom)
    pig=conf*C/np.maximum(W[:,None],1e-8)+(1-conf)*np.array([51,44,44])
    height=p[:,2];height+=(451-height.max())*sm(height,421,449)
    print("closed curl sculpt",len(p),len(f),p.min(axis=0),p.max(axis=0),flush=True)
    return dict(xyz=(p/S).astype('f4'),triangles=f.astype('i4'),normals=target.astype('f4'),pigment=np.uint8(np.clip(np.rint(pig),0,255)),fit=carrier['fit'])
