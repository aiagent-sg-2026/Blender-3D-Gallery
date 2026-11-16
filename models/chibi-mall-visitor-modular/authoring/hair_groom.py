"""A solid, swept haircut with independent crescent-shaped locks on a recessed scalp."""
import numpy as np
from scipy import ndimage as nd
from scipy.interpolate import CubicSpline, PchipInterpolator, UnivariateSpline
from scipy.spatial import cKDTree
import fast_simplification
from hair_envelope import vertex_normals
from hair_raster import draw
from hair_finish import CREST
from hair_strands import OUTER,REAR_LEFT,REAR_RIGHT
from hair_fit import LOCKS
from reconstruct_hair import norm, sm, sample, S

def filled(z,mask,blur):
    nearest=nd.distance_transform_edt(~mask,return_distances=False,return_indices=True)
    return nd.gaussian_filter(z[tuple(nearest)],blur)

# The taper stays broad up to the terminal turn, as on the sheet.
LOW_FRONT=[(375,87,2.5),(360,96,7),(346,111,10),(332,129,13),(320,145,12),(310,153,8),(300,156,4.5),(294,153,.65)]
MIDDLE_FRONT=[(391,84,3),(376,93,8),(363,111,12),(355,132,14),(343,150,12),(330,159,10),(316,164,5.5),(307,162,.72)]
SIDE_EAR=[(811,109,2),(811,124,6),(817,142,9),(826,155,10),(831,168,8),(832,180,4.5),(830,187,.62)]
SIDE_NAPE=[(925,126,2.1),(924,143,8),(917,165,12.7),(908,182,13),(897,197,10),(885,209,7),(876,216,3.5),(871,218,.68)]
SIDE_NAPE_BACK=[(942,128,2),(942,145,6),(938,163,9.5),(930,180,10),(921,193,8),(911,202,4.3),(904,207,.66)]
REAR_NAPE=[(1115,144,2),(1120,155,8.5),(1116,172,11.5),(1109,189,10.7),(1100,203,8.4),(1092,213,5),(1085,220,1)]
SIDE_SHOULDER=[(831,78,2.2),(820,84,6.6),(815,96,11),(815,112,12.5),(823,130,12.2),(838,142,9.8),(849,146,5.2),(855,145,.75)]

def groom(views,seed,skin):
    P=seed['xyz'].astype(float)*S;F=seed['triangles']
    carrier=P.copy();G=vertex_normals(P,F);C=seed['pigment'].copy();N=seed['normals'].copy()
    radial=norm(P-[0,2,366])
    maps=[]
    for v in views:
        z,idx,_=draw(P,F,v);sk,_,_=draw(*skin,v)
        maps.append((filled(z,idx>=0,3.5),sk))
    # Depths in the second orthographic study pair the endpoint with its
    # other visible role in the sheet. The same physical outward flip appears in
    # the front, profile and back, so it is constructed only once.
    other={
      "Outer high left":[803,804,803,800,795,797,805,820,842],
      "Low left flick":[798,798,801,809,822,835,846,860],
      "Middle left curl":[800,797,798,802,809,817,828,840],
      "C forelock":[798,798,794,785,777,776,778,782],
      "Outer right return":[805,804,807,813,822,842,866],
      "Lower right return":[802,806,813,826,847],
      "Posterior hook left":[901,909,915,924,939,947,947],
      "Posterior hook right":[903,908,919,931,943,946,939],
      "Nape overlap":[939,943,940,931,917,904,886],
    }
    pieces=[]
    def add(view,name,path,steps,rise=.54,deep=4.8,prod=1.,world=False):
        cam=views[view];raw=np.asarray(path,float)
        if world:
            coords=np.column_stack((raw[:,0]-390.5,raw[:,1]-856.5,505-raw[:,2]))
            width=raw[:,3];thick=raw[:,4];coords[:,2]-=2.2
        else:
            u=raw[:,0]-cam.left;v=raw[:,1]-48;w=raw[:,2]
            surf=sample(maps[view][0],u,v);meas=sample(cam.dhair,u,v)
            z=.66*surf+.34*np.clip(meas,surf-11,surf+11)
            if name in other:
                paired=np.interp(np.linspace(0,1,len(z)),np.linspace(0,1,len(other[name])),other[name])-856.5
                paired=paired if view==2 else -paired
                z=.81*paired+.19*np.clip(surf,paired-9,paired+9)
            if name.startswith("Ear shoulder"):
                # Profile + front/back constrain the broad body over the ear.
                lateral=np.interp(np.linspace(0,1,len(z)),[0,.18,.38,.58,.78,1],[51,60,70,79,85,84])
                z=.62*lateral+.38*np.clip(surf,lateral-9,lateral+9)
            if name.startswith("Lower nape"):
                lateral=np.interp(np.linspace(0,1,len(z)),[0,.17,.38,.60,.79,1],[53,55,58,57,43,24])
                z=.65*lateral+.35*np.clip(surf,lateral-9,lateral+9)
            if name.startswith("Outer nape"):
                lateral=np.interp(np.linspace(0,1,len(z)),[0,.20,.42,.65,.83,1],[48,51,53,47,36,29])
                z=.62*lateral+.38*np.clip(surf,lateral-9,lateral+9)
            coords=(raw[:,0:1]-cam.cx)*cam.right+(505-raw[:,1:2])*cam.top+z[:,None]*cam.eye
            width=w*prod;thick=np.maximum(.42,w*rise)
        length=np.r_[0,np.cumsum(np.linalg.norm(np.diff(coords,axis=0),axis=1))]
        u=np.linspace(0,length[-1],max(50,int(length[-1]*1.2)));t=u/length[-1]
        # Registered centerline samples are sparse. Fair the depth coordinate
        # before the parallel cross-sections are laid across it.
        curve=CubicSpline(length,coords,axis=0,bc_type='natural')
        center=curve(u);tangent=norm(curve(u,1))
        exterior=norm(center-[0,2,366]);outer=norm(exterior-tangent*np.sum(tangent*exterior,axis=1,keepdims=True))
        lateral=norm(np.cross(tangent,outer))
        w=PchipInterpolator(length,width)(u);h=PchipInterpolator(length,thick)(u)
        contact=sm(t,0,.19);end=sm(t,.70,1)
        if not world:
            center+=outer*((-.45+2.8*contact-.5*end))[:,None]
        phi=np.linspace(0,2*np.pi,36,endpoint=False);c=np.cos(phi);s=np.sin(phi)
        X=center[:,None,:]+lateral[:,None,:]*(w[:,None,None]*c[None,:,None])+outer[:,None,:]*(h[:,None,None]*s[None,:,None])
        nr,nc=X.shape[:2]
        low_rows=np.unique(np.rint(np.linspace(0,nr-1,steps+1)).astype(int))
        ids=np.arange(nr)
        def topo(rows,cross,tip):
            vs=X[rows[:,None],cross[None,:]].reshape(-1,3);nrings=len(rows);k=len(cross)
            idx=[]
            for i in range(nrings-1):
                for j in range(k):
                    a=i*k+j;b=i*k+(j+1)%k;idx.extend(((a,b,a+k),(b,b+k,a+k)))
            for j in range(1,k-1):idx.append((0,j+1,j))
            o=(nrings-1)*k
            if tip:
                endpoint=center[-1];vs=np.vstack((vs,endpoint));last=len(vs)-1
                for j in range(k):idx.append((o+j,o+(j+1)%k,last))
            else:
                for j in range(1,k-1):idx.append((o,o+j,o+j+1))
            idx=np.asarray(idx,'i4')
            g=vertex_normals(vs,idx)
            should=outer[rows[len(rows)//2]]
            cidx=int(np.argmin(abs(cross-9)))
            if g[(len(rows)//2)*k+cidx]@(should if world else cam.eye)<0:idx=idx[:,::-1].copy()
            return vs,idx
        Q,H=topo(ids,np.arange(nc),False);geom=vertex_normals(Q,H)
        q,lf=topo(low_rows[:-1],np.array([0,5,9,13,18,27]),True)
        ix=cKDTree(Q).query(q)[1];ln=geom[ix]
        x=Q@cam.right+cam.cx-cam.left;y=505-Q[:,2]-48;n=sample(cam.neural_normal,x,y)
        obs=norm(n[:,0:1]*cam.right+n[:,1:2]*cam.top+n[:,2:3]*cam.eye)
        blend=.45*sm(geom@cam.eye,.14,.82)*sm(np.sum(geom*obs,axis=1),.15,.85)
        normal=norm(geom*(1-.52*blend[:,None])+obs*(.52*blend[:,None]))
        lamp=.67+.62*np.maximum(0,n@norm(np.array([-.40,.73,.56])))
        pigment=np.clip((sample(cam.rgb,x,y)+5)/lamp[:,None]**.44,16,143)
        pigment=pigment.reshape(nr,nc,3)
        mean=nd.gaussian_filter1d(np.mean(pigment,axis=1),5.,axis=0)
        pigment=(.28*pigment+.37*mean[:,None,:]+.35*np.array([57,46,46])).reshape(-1,3)
        pieces.append((name,Q,H,normal,pigment,q,lf,ln))
        # Excavate a narrow root bed under the convex strand. The outer roll
        # remains a real silhouette; neighboring locks have space to overlap.
        dist,i=cKDTree(center).query(P);delta=P-center[i]
        side=(delta*lateral[i]).sum(axis=1);above=(delta*outer[i]).sum(axis=1);axial=(delta*tangent[i]).sum(axis=1)
        cover=(1-sm(np.abs(side)/(np.maximum(w[i],2)+1.3),.64,1.32))*np.exp(-.5*(axial/5.)**2)*np.exp(-.5*(above/13.)**2)*sm(t[i],0,.13)
        return cover*deep*.73
    excavation=np.zeros(len(P))
    def strand(*args,**kw):
        nonlocal excavation
        excavation=np.maximum(excavation,add(*args,**kw))
    fr=LOCKS['front'];back=LOCKS['back'];side=LOCKS['profile']
    strand(0,'Crown crest',CREST,10,world=True,deep=1.5)
    strand(0,'Outer high left',fr[0],9,.57,5.4,1.08)
    strand(0,'Low left flick',LOW_FRONT,8,.65,6.3,1.1)
    strand(0,'Middle left curl',MIDDLE_FRONT,9,.67,7.6,1.1)
    strand(0,'C forelock',fr[1],8,.70,6.,1.05)
    strand(0,'Outer right return',fr[7],9,.62,5.5,1.03)
    strand(0,'Lower right return',fr[8],7,.61,5.3,1.02)
    for i,suf in ((1,'L'),(3,'R')):
        strand(i,'Ear shoulder '+suf,SIDE_SHOULDER,8,.66,7.5,1.03)
        strand(i,'Lower nape '+suf,SIDE_NAPE,8,.68,8.1,1.08)
        strand(i,'Outer nape '+suf,SIDE_NAPE_BACK,7,.64,7.5,1.)
    strand(2,'Posterior hook left',back[0],8,.68,6.9,1.05)
    strand(2,'Posterior hook right',back[2],8,.71,7.2,1.10)
    strand(2,'Nape overlap',REAR_NAPE,8,.70,7.1,1.02)
    g=vertex_normals(carrier,F)
    carrier-=radial*excavation[:,None]
    # QEM is applied only to the carrier, in unit-sized coordinates. Each styled
    # strand above already owns its evenly spaced, editable runtime topology.
    rest=2390-sum(len(part[6]) for part in pieces)
    low,lf=fast_simplification.simplify(np.asarray(carrier/S,dtype=float),F,target_count=rest,agg=8)
    low*=S;lg=vertex_normals(carrier,F)[cKDTree(carrier).query(low)[1]]
    positions=[carrier];faces=[F];normals=[N];colors=[C];lp=[low];lfs=[lf];ln=[lg]
    piece=[np.zeros(len(F),'i2')];lpid=[np.zeros(len(lf),'i2')];names=['Fitted scalp']
    for name,Q,H,no,co,q,ff,ng in pieces:
        pid=len(names);names.append(name)
        faces.append(H+sum(map(len,positions)));positions.append(Q);colors.append(co);normals.append(no);piece.append(np.full(len(H),pid,'i2'))
        lfs.append(ff+sum(map(len,lp)));lp.append(q);ln.append(ng);lpid.append(np.full(len(ff),pid,'i2'))
    hp=np.vstack(positions);low=np.vstack(lp);dist=451.-low[:,2].max()
    hp[:,2]+=dist*sm(hp[:,2],419,446);low[:,2]+=dist*sm(low[:,2],419,446)
    print('groom carrier/locks',len(lf),[len(part[6]) for part in pieces],sum(map(len,lfs)),flush=True)
    return dict(xyz=(hp/S).astype('f4'),triangles=np.vstack(faces).astype('i4'),normals=np.vstack(normals).astype('f4'),pigment=np.uint8(np.clip(np.rint(np.vstack(colors)),0,255)),piece=np.concatenate(piece),names=np.array(names),runtimeXYZ=(low/S).astype('f4'),runtimeTriangles=np.vstack(lfs).astype('i4'),runtimeNormals=np.vstack(ln).astype('f4'),runtimePiece=np.concatenate(lpid),fit=seed['fit'])
