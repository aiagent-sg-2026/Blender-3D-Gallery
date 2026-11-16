"""Sculpt overlapping, lens-shaped locks from traced axes and measured depths."""
import numpy as np
from scipy import ndimage as nd
from scipy.interpolate import PchipInterpolator, CubicSpline
from reconstruct_hair import S, sample, norm, sm
from hair_envelope import vertex_normals
from hair_visibility import visible_faces
from hair_fit import LOCKS

# Ends on the sheet with a visible lift must have a broad shoulder behind the tip.
CROWN=[(417,79,1.4),(412,68,5.1),(401,61,6.5),(385,59,6.6),(366,63,5.2),(349,72,4.7),(333,79,4.3),(325,81,3.5),(318,78,0.65)]
OUTER=[(397,82,3),(378,88,7),(360,102,9),(350,120,11),(337,142,12),(324,155,9),(313,161,5),(304,162,1)]
SIDE_BOTTOM=[(819,107,3),(815,120,8),(817,134,11),(825,143,10),(837,149,8),(848,151,4),(855,147,.7)]
REAR_TOP=[(1086,75,1.1),(1083,65,5),(1089,58,6),(1101,57,6),(1114,59,5),(1127,66,3),(1134,76,.7)]
REAR_LEFT=[(1027,92,2),(1017,95,7),(1009,107,9),(1004,122,8),(998,135,6),(990,140,4),(984,139,.6)]
REAR_RIGHT=[(1136,99,2),(1145,111,8),(1150,126,9),(1157,139,7),(1165,149,5),(1172,154,2.6),(1175,151,.6)]
SIDE_SMALL=[(930,112,1.3),(939,124,7),(944,142,7),(949,154,5),(949,164,2.9),(946,170,.65)]

def zbuffer(p,c):
    xx,yy,d=c.projection(p);x=np.clip(np.rint(xx).astype(int),0,c.mask.shape[1]-1);y=np.clip(np.rint(yy).astype(int),0,c.mask.shape[0]-1)
    depth=np.full(c.mask.shape,-200.);np.maximum.at(depth,(y,x),d)
    nearest=nd.distance_transform_edt(depth<-190,return_distances=False,return_indices=True)
    return nd.gaussian_filter(nd.median_filter(depth[tuple(nearest)],3),1.4)

def build(views,base,skin):
    shell=base['xyz']*S;surf=base['triangles'];G=vertex_normals(shell,surf)
    # Recess the carrier under the contact edges, retaining a closed cap at the scalp.
    radial=norm(shell-[0,2,366]);factor=.48+.55*sm(shell[:,2],357,420)
    p=[shell-radial*factor[:,None]];f=[surf];Ns=[base['normals']];Cs=[base['pigment']]
    piece=[np.zeros(len(surf),'i2')];names=['Scalp']
    from scipy.spatial import cKDTree
    import fast_simplification
    high_shell=p[0]
    carrier,cf=fast_simplification.simplify(high_shell.astype(float),surf,target_count=594,agg=5.)
    L=[carrier];LF=[cf];LP=[np.zeros(len(cf),'i2')]
    LN=[G[cKDTree(high_shell).query(carrier)[1]]]
    physical={"Crest":9,"High swept fan":10,"Low swept fan":9,"Broad overhang":8,"C forelock":9,
              "Inner forelock":6,"Short parted curl":8,"Temple return":8,"Low temple return":6,
              "Crown fan":7,"Upper ear fan":7,"Lower ear fan":7,"Rear side flow":8,
              "Rear crown crest":7,"Crown hook L":8,"Central hook":9,"Crown hook R":8,
              "Left outer tier":6,"Right outer tier":6,"Lower right tier":7}
    buffers=[zbuffer(shell,v) for v in views]
    def lock(cam_id,name,trace,raise_by=2.,width=1.,roundness=.68):
        cam=views[cam_id]
        raw=np.asarray(trace,float)
        arcl=np.r_[0,np.cumsum(np.linalg.norm(np.diff(raw[:,:2],axis=0),axis=1))]
        u=np.linspace(0,arcl[-1],max(25,int(arcl[-1]/1.05)));t=u/arcl[-1]
        curve=CubicSpline(arcl,raw[:,:2],axis=0,bc_type='natural');uv=curve(u)
        tangent=norm(curve(u,1));side=np.stack((-tangent[:,1],tangent[:,0]),axis=1)
        r=np.maximum(.26,PchipInterpolator(arcl,raw[:,2])(u))*width
        C=uv.copy();C[:,0]-=cam.left;C[:,1]-=48
        def depth_at(coords):
            a,b=coords.T
            sd=sample(cam.sdf,a,b)
            reference=sample(cam.dhair,a,b);carrier=sample(buffers[cam_id],a,b)
            return .48*reference+.52*np.clip(carrier,reference-9.,reference+12.)
        d0=depth_at(C);d0=nd.gaussian_filter1d(d0,2.4)
        off=np.maximum(2.6,r*.74)[:,None]*side
        dp=(depth_at(C+off)-depth_at(C-off))/(2*np.maximum(2.6,r*.74))
        dp=nd.gaussian_filter1d(np.clip(dp,-2.1,2.1),2.)
        lift=raise_by*(.16+.61*np.sin(np.pi*t)**.49)
        # The tip remains a closed solid. This also lets it turn away from the
        # viewer in the adjacent profile instead of reading as a cut-off paddle.
        h=np.minimum(8.8,np.maximum(.42,r*roundness))
        theta=np.linspace(0,np.pi*2,22,endpoint=False)
        w=r[:,None]*np.cos(theta)
        coord=uv[:,None,:]+side[:,None,:]*w[...,None]
        d=d0[:,None]+lift[:,None]+dp[:,None]*w+h[:,None]*(np.sin(theta)-.14)
        xyz=(coord[...,0:1]-cam.cx)*cam.right+(505-coord[...,1:2])*cam.top+d[...,None]*cam.eye
        q=xyz.reshape(-1,3);nc=len(theta);nr=len(t);idx=[]
        for i in range(nr-1):
            for j in range(nc):
                k=(j+1)%nc;a=i*nc+j;b=i*nc+k;c=a+nc;e=b+nc
                idx.extend(((a,b,c),(b,e,c)))
        for j in range(1,nc-1):
            idx.append((0,j+1,j));o=(nr-1)*nc;idx.append((o,o+j,o+j+1))
        idx=np.array(idx,'i4');normal=vertex_normals(q,idx)
        outer=np.tile(np.sin(theta)>0,nr)
        if np.mean(normal[outer]@cam.eye)<0:idx=idx[:,::-1].copy();normal=-normal
        source=coord.reshape(-1,2);cx=source[:,0]-cam.left;cy=source[:,1]-48
        local=sample(cam.neural_normal,cx,cy)
        learned=norm(local[:,0:1]*cam.right+local[:,1:2]*cam.top+local[:,2:3]*cam.eye)
        blend=.70*sm(normal@cam.eye,-.04,.64)*sm(np.sum(learned*normal,axis=1),-.06,.65)
        N=norm(normal*(1-blend[:,None])+learned*blend[:,None])
        rgb=sample(cam.rgb,cx,cy);lighting=.67+.62*np.maximum(0,local@norm(np.array([-.40,.73,.56])))
        pig=np.clip((rgb+5)/lighting[:,None]**.44,17,140)
        offset=sum(map(len,p));p.append(q);f.append(idx+offset);Ns.append(N);Cs.append(pig)
        pid=len(names)
        piece.append(np.full(len(idx),pid,'i2'));names.append(name)
        short=name.split(' ',1)[1] if name.startswith(('1 ','3 ')) else name
        segments=physical.get(short)
        if not segments:return
        # Use a consistent six-sided rolled section and place sparse rings along
        # arclength. A visible tip ends in a single vertex; QEM never shreds it.
        sections=np.round(np.linspace(0,nr-1,segments+1)).astype(int)
        ringids=np.array([0,3,6,8,11,16])
        v=[];ng=[];fi=[]
        for row in sections[:-1]:
            ix=row*nc+ringids
            v.extend(q[ix]);ng.extend(normal[ix])
        last=xyz[-1].mean(axis=0);v.append(last)
        ng.append(norm((last-xyz[-2].mean(axis=0))[None])[0])
        k=len(ringids);nrings=len(sections)-1
        for level in range(nrings-1):
            for j in range(k):
                a=level*k+j;b=level*k+(j+1)%k;c=a+k;d=b+k
                fi.extend(((a,b,c),(b,d,c)))
        for j in range(k):
            o=(nrings-1)*k
            fi.append((o+j,o+(j+1)%k,nrings*k))
        for j in range(1,k-1):fi.append((0,j+1,j))
        v=np.array(v);ng=np.array(ng);fi=np.array(fi,'i4')
        if np.mean(np.sum(vertex_normals(v,fi)*ng,axis=1))<0:fi=fi[:,::-1].copy()
        il=sum(map(len,L));L.append(v);LF.append(fi+il);LN.append(ng);LP.append(np.full(len(fi),pid,'i2'))
    # In each panel use generous convex shoulders and shortened tips on the lower tier.
    front=LOCKS['front'];side=LOCKS['profile'];rear=LOCKS['back']
    for name,trace,lift,width in [('Crest',CROWN,2.8,1.),('High swept fan',front[0],3.0,1.05),('Temple fan',front[4],2.3,1.05),('Low swept fan',OUTER,2.8,1.02),('Broad overhang',front[3],4.2,1.12),('C forelock',front[1],5.4,1.02),('Inner forelock',front[2],4.1,.94),('Short parted curl',front[6],3.2,1.02),('Parted upper shoulder',front[5],2.4,1.),('Temple return',front[7],2.7,1.),('Low temple return',front[8],2.5,1.)]:
        lock(0,name,trace,lift,width)
    for ci in (1,3):
        for name,trace,lift,width in [('Top curl',side[1],2,1.04),('Crown fan',side[0],3.5,.98),('Upper ear fan',side[3],3.1,1.03),('Lower ear fan',SIDE_BOTTOM,3.7,1.02),('Side crown layer',side[2],2.4,1.),('Rear side flow',side[9],2.3,1.08),('Outer side tip',SIDE_SMALL,2,1.)]:
            lock(ci,str(ci)+' '+name,trace,lift,width)
    for name,trace,lift,width in [('Rear crown crest',REAR_TOP,2.5,1.),('Crown hook L',rear[0],4.2,1.12),('Central hook',rear[1],4.4,1.05),('Crown hook R',rear[2],4.3,1.03),('Left outer tier',REAR_LEFT,2.6,1.),('Right outer tier',REAR_RIGHT,2.6,1.),('Low inner body',rear[8],2.7,1.11),('Lower right tier',rear[9],2.6,1.06)]:
        lock(2,name,trace,lift,width)
    P=np.vstack(p);F=np.vstack(f)
    Z=P[:,2];Z+=(451.-Z.max())*sm(Z,413,449)
    low=np.vstack(L);low[:,2]+=(451.-max(np.vstack(p)[:,2]))*sm(low[:,2],413,449)
    keep=np.arange(len(F),dtype='i4')
    print('explicit runtime triangles',sum(map(len,LF)),flush=True)
    print('individual locks',len(names)-1,'faces',len(F),'visible',len(keep),flush=True)
    return dict(xyz=(P/S).astype('f4'),triangles=F,normals=np.vstack(Ns).astype('f4'),pigment=np.uint8(np.clip(np.rint(np.vstack(Cs)),0,255)),runtimeXYZ=(low/S).astype('f4'),runtimeNormals=np.vstack(LN).astype('f4'),runtimeTriangles=np.vstack(LF).astype('i4'),runtimePiece=np.concatenate(LP),piece=np.concatenate(piece),names=np.array(names),fit=base['fit'])
