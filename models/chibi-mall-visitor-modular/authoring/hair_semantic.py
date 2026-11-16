"""Sculpt the rounded lock bodies and their overlapping lips at registered instance boundaries."""
from pathlib import Path
import numpy as np
from scipy import ndimage as nd,sparse
from hair_raster import draw
from hair_envelope import vertex_normals
from hair_relief import extend
from reconstruct_hair import S,norm,sm,sample

def rounded_regions(cam,observations):
    labels=observations[cam.name]
    order={'front':[9,10,8,4,3,7,5,6,2,1,0,11],'profile':[11,10,9,7,6,5,8,3,4,0,1,2],'back':[12,11,10,9,8,7,5,6,4,3,2,0,1]}[cam.name]
    Y,X=np.indices(cam.mask.shape);flow=np.zeros(cam.mask.shape);crown=np.zeros(cam.mask.shape)
    seam=np.full(cam.mask.shape,50.);signal=np.zeros(cam.mask.shape)
    for index in order:
        a=labels[index].copy()
        a=nd.binary_opening(a,iterations=1);a=nd.binary_closing(a,iterations=2)
        cc,n=nd.label(a)
        if n==0:continue
        sizes=np.bincount(cc.ravel());sizes[0]=0
        a=nd.binary_fill_holes(cc==sizes.argmax())
        d=nd.distance_transform_edt(a)-nd.distance_transform_edt(~a)
        d=nd.gaussian_filter(d,1.15)
        # Local width measured on the medial ridge. Outside the silhouette the
        # short negative band records its underlapping side.
        diam=nd.maximum_filter(np.maximum(d,0),19)
        w=np.clip(diam,3,16);q=np.clip(d/w,0,1)
        nmap=cam.neural_normal
        # The principal form has a plump transverse shoulder, a rolled terminal
        # edge and an occlusion valley independently located by mask boundaries.
        height=np.sqrt(q*(2-q))*(.61*w+2.8)
        height+=1.6*sm(d,-.6,1.2)
        lip=-3.7*np.exp(-.5*((d+.25)/1.6)**2)
        visibility=sm(d,-2.3,.9)
        flow=flow*(1-visibility)+visibility*height+lip*(1-visibility*.45)
        seam=np.minimum(seam,np.abs(d))
        signal=np.maximum(signal,sm(d,-4,0))
    # Keep the lobes' true bulk while anchoring the large cranial envelope.
    flow-=nd.gaussian_filter(flow,12)*.63+1.2
    return nd.gaussian_filter(flow,.64),seam

def smooth_coordinates(p,f,steps):
    a=np.r_[f[:,0],f[:,1],f[:,2]];b=np.r_[f[:,1],f[:,2],f[:,0]]
    edges=sparse.coo_matrix((np.ones(len(a)*2),(np.r_[a,b],np.r_[b,a])),shape=(len(p),len(p))).tocsr()
    edges.data[:]=1.;degree=np.array(edges.sum(axis=1)).ravel()
    A=sparse.diags(1/np.maximum(degree,1.))@edges
    q=p.copy()
    for i in range(steps):q+=.57*(A@q-q)
    return q

def sculpt(views,seed,skin,mattefile):
    old=seed['xyz'].astype(float)*S;f=seed['triangles'];smoothed=smooth_coordinates(old,f,37)
    p=.67*smoothed+.33*old;geo=vertex_normals(p,f);rad=norm(p-[0,2,366])
    numerator=np.zeros(len(p));den=np.zeros(len(p));N=np.zeros_like(p);C=np.zeros_like(p);cn=np.zeros(len(p))
    obs=np.load(mattefile)
    for v in views:
        base,ids,_=draw(p,f,v);base=extend(base,ids>=0)
        x=p@v.right+v.cx-v.left;y=505-p[:,2]-48
        m=sample(v.sdf,x,y);local=sample(v.neural_normal,x,y)
        dep=sample(nd.gaussian_filter(base,.9),x,y)-p@v.eye;depth=np.maximum(0,dep)
        inc=np.maximum(0,geo@v.eye);region=np.maximum(0,rad@v.eye)
        weight=(.008+.91*region**8+.09*inc**5)*np.exp(-.5*(depth/4.8)**2)*sm(m,-3,2.5)
        w=weight*(.48 if v.name=='quarter' else 1.)
        n=norm(local[:,0:1]*v.right+local[:,1:2]*v.top+local[:,2:3]*v.eye)
        N+=w[:,None]*n
        receive=.67+.62*np.maximum(0,local@norm(np.array([-.40,.73,.56])))
        C+=w[:,None]*np.clip((sample(v.rgb,x,y)+5)/receive[:,None]**.44,16,142);cn+=w
        if v.name=='quarter':continue
        relief,edge=rounded_regions(v,obs)
        imprint=sample(relief,x,y)
        # Interior adjustment is largest under the actual major rolls. Retain
        # a small part of the measured profile around a grazing silhouette.
        w=weight*sm(geo@v.eye,-.34,.26)
        numerator+=w*imprint;den+=w
    strength=sm(den,.004,.085);D=numerator/np.maximum(den,1e-9)
    # This is a radial displacement of the real sculpture, including lower
    # ear-side, rear-quarter, and nape tiers seen when lighting is removed.
    p+=rad*(1.42*D*strength)[:,None]
    geo=vertex_normals(p,f)
    conf=sm(cn,.006,.08)[:,None]
    normal=norm(.77*conf*norm(N)+(1-.77*conf)*geo);pig=conf*C/np.maximum(cn[:,None],1e-8)+(1-conf)*np.array([53.,43,43.])
    height=p[:,2];height+=(451-height.max())*sm(height,417,446)
    print('instance-constraint physical relief',np.percentile(D,[1,15,50,85,99]),flush=True)
    return dict(xyz=(p/S).astype('f4'),triangles=f,normals=normal.astype('f4'),pigment=np.uint8(np.clip(np.rint(pig),0,255)),fit=seed['fit'])
