"""Fit a stationary, sculptable hair surface to the sheet in world space.

Optional preprocessing, outside Blender: numpy, scipy, Pillow. The saved field is
the editable rebuild input. No color or photographic cutout is projected at runtime.
"""
import argparse
from pathlib import Path
import hashlib
import numpy as np
from PIL import Image
from scipy import ndimage as nd
from scipy.interpolate import PchipInterpolator

S = 451 / 1.30
TOP = 54.
# The profile picture has its nose to the left. Both sides use its depth convention.
VIEWS = {
    "front": (289, 490, 390.5, 0.),
    "profile": (758, 964, 856.5, 90.),
    "back": (977, 1183, 1080.5, 180.),
    "quarter": (39, 247, 136., -37.),
}
# Natural seams and the turn of their broad shoulders. Radii are half-widths
# in the matching orthographic study, not widths measured on an unfolded scalp.
LOCKS = {
    "front": [
        [(414,86,3),(412,75,6),(399,67,9),(383,68,10),(366,77,10),(349,93,9),(331,110,7),(311,121,4),(296,119,1)],
        [(414,104,4),(411,89,8),(401,85,11),(389,93,10),(382,108,10),(380,126,9),(383,144,4),(385,150,1)],
        [(407,94,5),(398,95,7),(392,106,7),(390,122,7),(391,137,4),(394,145,1)],
        [(396,88,6),(381,93,9),(365,107,12),(357,124,12),(346,143,10),(335,156,5),(323,161,1)],
        [(365,94,4),(346,107,7),(332,124,11),(320,143,10),(310,153,6),(296,155,1)],
        [(414,82,3),(424,76,6),(442,81,8),(455,94,8),(466,110,5),(470,112,1)],
        [(416,104,5),(429,97,9),(442,105,12),(448,120,13),(447,136,10),(440,151,2)],
        [(424,88,3),(440,91,7),(457,104,8),(467,119,9),(477,135,5),(484,136,1)],
        [(454,118,5),(458,139,10),(463,153,8),(472,163,2)],
        [(322,147,4),(326,160,7),(329,175,5),(335,187,1)],
        [(457,148,4),(453,162,7),(450,179,5),(446,187,1)],
    ],
    "profile": [
        [(838,64,4),(831,69,8),(830,82,10),(837,99,12),(849,112,10),(859,119,4),(867,120,1)],
        [(850,66,4),(850,78,9),(856,91,10),(867,105,10),(881,115,7),(892,119,1)],
        [(862,64,4),(879,71,9),(889,87,10),(896,103,4),(900,108,1)],
        [(827,83,4),(816,88,8),(811,101,9),(813,116,11),(823,131,12),(837,142,9),(848,146,1)],
        [(834,90,3),(831,104,7),(838,118,10),(851,129,9),(862,132,5),(869,131,1)],
        [(852,108,4),(859,123,10),(874,136,10),(892,145,7),(899,145,1)],
        [(900,80,3),(914,98,11),(923,123,13),(934,146,11),(941,150,2)],
        [(934,105,3),(942,127,8),(943,147,9),(947,162,6),(946,174,1)],
        [(813,128,5),(823,149,7),(829,162,8),(831,180,5),(830,186,1)],
        [(907,148,5),(910,164,11),(902,184,11),(887,204,7),(875,217,1)],
        [(928,159,4),(927,174,9),(915,194,10),(907,204,3),(900,211,1)],
        [(884,153,4),(882,168,11),(878,187,10),(871,207,8),(867,220,1)],
    ],
    "back": [
        [(1075,74,4),(1066,73,9),(1053,79,13),(1044,92,14),(1040,108,12),(1042,124,8),(1051,137,1)],
        [(1074,79,5),(1083,86,13),(1088,105,14),(1084,124,13),(1074,142,8),(1064,152,1)],
        [(1080,73,5),(1095,76,11),(1108,87,13),(1114,104,13),(1110,120,11),(1096,136,1)],
        [(1052,76,4),(1036,81,9),(1024,93,10),(1018,109,10),(1012,127,7),(1004,139,1)],
        [(1120,82,5),(1134,96,10),(1143,113,10),(1151,129,8),(1158,139,1)],
        [(1024,103,4),(1017,120,8),(1016,136,10),(1019,150,9),(1028,159,1)],
        [(1126,109,6),(1131,128,12),(1127,146,11),(1118,158,1)],
        [(1046,118,3),(1040,137,9),(1045,154,10),(1057,175,9),(1061,181,1)],
        [(1080,141,4),(1090,149,10),(1090,166,12),(1083,186,11),(1077,198,1)],
        [(1111,141,5),(1116,160,10),(1109,178,11),(1096,195,8),(1085,212,1)],
        [(1150,142,4),(1145,159,9),(1137,180,8),(1120,197,5),(1112,204,1)],
        [(1011,148,3),(1018,169,7),(1032,189,8),(1045,201,3),(1050,206,1)],
        [(1051,177,3),(1056,193,7),(1067,209,7),(1078,224,1)],
    ],
}
# Remove the two skin-side brows where their dark pixels touch the hair in projection.
TRIM = {
    "front": [[(351,151),(357,142),(362,133),(367,125),(369,135),(374,142)],
              [(408,114),(416,115),(423,117),(430,121),(434,128),(436,140),(437,151)]],
    "profile": [[(788,141),(794,130),(799,120),(804,136),(809,149)]],
    "quarter": [[(139,152),(146,143),(153,131),(161,126),(165,139)],
                [(192,115),(198,118),(204,123),(210,134),(213,147)]]
}

def smooth(x, a, b):
    t=np.clip((x-a)/(b-a),0,1)
    return t*t*(3-2*t)

def interp_image(a,x,y):
    return nd.map_coordinates(a,[y-49.,x],order=1,mode="nearest",prefilter=False)

class Study:
    def __init__(self, im, name):
        self.left,right,self.cx,self.deg=VIEWS[name]
        rgb=im[49:233,self.left:right].astype(float)
        r,g,b=rgb.transpose(2,0,1)
        mask=(r<167)&(g<145)&(b<148)&((r-g)<42)
        label,_=nd.label(mask)
        mask=label==(1+np.bincount(label.ravel())[1:].argmax())
        mask=nd.binary_fill_holes(mask)
        yy,xx=np.indices(mask.shape);px=xx+self.left;py=yy+49
        for line in TRIM.get(name,[]):
            xp,yp=np.array(line).T
            mask &= ~((px>=xp[0])&(px<=xp[-1])&(py>np.interp(px,xp,yp)))
        # Foreground colour enters only as a scalar estimate of convex relief and occlusion.
        # Extend mask edges before filtering so the white page never cuts grooves in the sculpt.
        lum=.23*r+.64*g+.13*b
        nearest=nd.distance_transform_edt(~mask,return_distances=False,return_indices=True)
        intensity=nd.gaussian_filter(lum[tuple(nearest)],.72)
        medium=nd.gaussian_filter(intensity,6)
        broad=nd.gaussian_filter(intensity,19)
        residual=intensity-medium
        self.depth=.00053*residual+.00032*(medium-broad)
        self.occlusion=np.clip(.74*(intensity-broad)+.22*(broad-44),-31,41)
        self.mask=mask
        self.sdf=nd.distance_transform_edt(mask)-nd.distance_transform_edt(~mask)
        # A wide changing-width stroke is modelled as a rounded cross-section.
        shape=np.zeros_like(lum)
        for path in LOCKS.get(name,[]):
            for p,q in zip(path,path[1:]):
                ax,ay,ar=p;bx,by,br=q;dx,dy=bx-ax,by-ay
                t=np.clip(((px-ax)*dx+(py-ay)*dy)/(dx*dx+dy*dy),0,1)
                d=np.hypot(px-ax-t*dx,py-ay-t*dy)
                radius=(1-t)*ar+t*br
                arch=np.maximum(0,1-(d/np.maximum(radius,1))**2)**1.65
                shape=np.maximum(shape,.00128*radius*arch)
        self.depth+=nd.gaussian_filter(shape,1.3)
        lo=[];hi=[]
        for row in mask:
            col=np.flatnonzero(row)+self.left
            lo.append(float(col[0]) if len(col) else np.nan)
            hi.append(float(col[-1]) if len(col) else np.nan)
        self.extent=[]
        for edge in [lo,hi]:
            v=np.array(edge);good=np.where(np.isfinite(v))[0]
            self.extent.append(np.interp(np.arange(len(v)),good,v[good]))
    def sample(self,values,px,py):
        return interp_image(values,px-self.left,py)
    def edge(self,index,py,blur=0):
        v=self.extent[index]
        return np.interp(py-49,np.arange(len(v)),nd.gaussian_filter1d(v,blur) if blur else v)

def fit(im):
    f,s,b,q=(Study(im,k) for k in ("front","profile","back","quarter"))
    # Fit the cranium with smooth sections; a single outward flick occupies only a
    # small arc of a section and must never stretch a complete latitude into a shelf.
    levels=np.array([54,57,61,68,78,93,110,126,142,157,171,188,202,215,225,231])
    measures=[
        [-6,-6,-6,-4,-2,0,0,0,0,0,0,0,0,0,0,0],
        [-9,-9,-6,-3,0,2,4,4,4,5,7,12,16,18,18,18],
        [0,16,27,40,55,70,82,88,89,86,79,64,50,34,17,8],
        [0,17,30,47,64,79,88,94,93,90,85,75,64,47,28,14]]
    profiles=[PchipInterpolator(levels,v) for v in measures]
    def shape(a,row):
        xc,yc,rx,ry=(curve(np.clip(row,54,231)) for curve in profiles)
        return np.stack(((xc+rx*np.sin(a))/S,(yc-ry*np.cos(a))/S,(505-row)/S),axis=-1)
    def projection(p,st):
        if st is s:return s.cx+p[...,1]*S
        a=np.deg2rad(st.deg)
        return st.cx+S*(p[...,0]*np.cos(a)+p[...,1]*np.sin(a))
    def weights(a):
        # A fixed atlas chart in rest space. Front, near profile and rear observations
        # meet across overlaps. The opposite profile uses the observed ear depth.
        deg=np.rad2deg(a)
        scores=np.stack([np.cos(np.deg2rad(deg-st.deg)) for st in (f,s,b,q)])
        scores[1]=np.abs(np.sin(a))
        scores=np.maximum(scores,0)**11
        scores[3]*=.93
        return scores/(np.sum(scores,axis=0)+1e-16)
    def fields(a,row):
        p=shape(a,row); w=weights(a)
        ds=[];occ=[];ins=[]
        for st in (f,s,b,q):
            px=projection(p,st)
            ds.append(st.sample(st.depth,px,row));occ.append(st.sample(st.occlusion,px,row))
            ins.append(st.sample(st.sdf,px,row))
        return p,np.sum(w*np.array(ds),axis=0),np.sum(w*np.array(occ),axis=0),np.sum(w*np.array(ins),axis=0)
    # Ask each meridian where the outer surface first crosses the visible hairline.
    n=760;h=220
    az=np.linspace(-np.pi,np.pi,n,endpoint=False)
    av,rv=np.meshgrid(az,np.linspace(54.1,230,465))
    pp,ds,co,mask=fields(av,rv)
    # The first few rows at the very top can be outside another view's crown.
    # Keep the connected hair from row 100 down to the forehead, ears and nape.
    rim=np.full(n,226.)
    for j in range(n):
        start=np.searchsorted(rv[:,0],100)
        miss=np.where(mask[start:,j]<0)[0]
        if len(miss):
            k=start+miss[0]
            u=mask[k-1,j]/max(mask[k-1,j]-mask[k,j],1e-9)
            rim[j]=rv[k-1,j]*(1-u)+rv[k,j]*u
    rim=nd.gaussian_filter1d(rim,2.2,mode="wrap")
    # Separate root and tip measurements around the ear. The frontal hairline has a
    # double-valued projection there; the sideburn in front of the ear is a separate lock.
    degrees=np.rad2deg(az)
    nape=np.interp(np.abs(degrees),[75,86,96,104,115,130,150,180],[169,169,172,185,204,216,223,226])
    weight=smooth(np.abs(degrees),70,94)
    rim=(1-weight)*rim+weight*nape
    t=np.linspace(0,1,h);a,v=np.meshgrid(az,t)
    row=TOP+(rim[None,:]-TOP)*(1-np.sin(v*np.pi*.5))
    p,d,ink,_=fields(a,row)
    # Per-view relief runs along depth, which preserves the reference silhouettes.
    # On the crown it gradually dies into the smooth top section.
    w=weights(a)
    direction=np.stack((w[1]*np.sign(np.sin(a))+w[3]*np.sin(np.deg2rad(q.deg)),
                        -w[0]+w[2]-w[3]*np.cos(np.deg2rad(q.deg)),np.zeros_like(a)),axis=-1)
    depth=nd.gaussian_filter(d,(1.65,2.4),mode=("nearest","wrap"))
    p+=direction*(.53*(depth-.003)*smooth(row,60,78))[...,None]
    # Short, local outward turns at the ends of the outer tiers; crown latitude
    # and the opposite side of the section keep their original contours.
    for side in (-1,1):
        for angle,level,width,amount in [(74,80,5,7),(76,119,6,8),(89,139,6,6),(81,155,5,6)]:
            zone=np.exp(-((np.rad2deg(a)-side*angle)/17)**2-((row-level)/width)**2)
            p[...,0]+=side*amount*zone/S
    p[-1,:]=(-6/S,-9/S,1.30)
    return p.astype('f4'),ink.astype('f4'),rim.astype('f4')

def main():
    import sys
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference",type=Path);parser.add_argument("output",type=Path)
    args=parser.parse_args()
    data=args.reference.read_bytes()
    if hashlib.sha256(data).hexdigest()!="0915b9e7b41d35177cb890580935b9c1db355539a1183861b2387c936f110f6f":
        sys.exit("Use the supplied GJH character sheet with these tracing coordinates.")
    xyz,cavity,rim=fit(np.array(Image.open(args.reference).convert("RGB")))
    np.savez_compressed(args.output,xyz=xyz,cavity=cavity,rim=rim)
    print("Saved fitted surface",xyz.shape,"range",xyz.reshape(-1,3).min(axis=0),xyz.reshape(-1,3).max(axis=0))

if __name__=="__main__":main()
