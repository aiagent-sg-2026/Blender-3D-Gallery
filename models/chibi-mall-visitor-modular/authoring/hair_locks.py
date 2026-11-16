"""Hand-shaped, overlapping solid locks on a registered cranium.

Each control has screen X, screen Y and a half-width on the indicated study.
The complete cross-section is constructed in the reference projection, then given
a domed surface, an underside, root depth and a rolled taper in three dimensions.
"""
import math
import numpy as np

# Width and depth are independent: short crown hooks stay wide at the root.
# A lock's height above the construction scalp controls its overlap order.
FRONT=[
 ("Crown crest",9,1.6,[(418,78,3),(410,68,6),(397,60,6),(382,59,5),(366,63,5),(348,73,5),(331,82,5),(318,79,0)]),
 ("Left undercurl",6,-.7,[(353,98,7),(331,115,10),(316,136,10),(308,151,8),(294,155,0)]),
 ("Left temple fold",6,1,[(368,94,6),(346,109,11),(331,130,11),(320,151,8),(306,163,0)]),
 ("Upper swept curl",9,2.1,[(416,99,3),(410,82,7),(397,74,9),(380,75,9),(362,85,8),(344,101,8),(327,116,6),(307,124,4),(295,118,0)]),
 ("Deep fringe",7,1.7,[(405,88,7),(384,94,11),(367,111,12),(357,131,10),(346,148,6),(342,158,0)]),
 ("Falling lock",8,5.2,[(414,110,3),(409,95,8),(398,91,9),(386,101,10),(380,116,10),(378,132,7),(382,146,4),(385,150,0)]),
 ("Forehead curl",7,6.3,[(414,111,2),(408,102,5),(401,100,6),(395,109,6),(392,124,6),(392,138,4),(395,146,0)]),
 ("Right upper return",7,1.3,[(416,88,3),(427,77,5),(441,79,6),(455,89,6),(466,102,5),(472,110,0)]),
 ("Right upper flick",8,2.4,[(416,100,4),(426,90,8),(442,95,9),(455,107,9),(466,124,8),(477,137,5),(484,136,0)]),
 ("Right temple fold",7,.7,[(447,104,6),(455,118,9),(460,138,10),(465,154,7),(474,165,0)]),
 ("Part return",8,5.4,[(415,114,3),(423,102,7),(435,105,10),(444,119,11),(447,133,8),(443,146,6),(440,153,0)]),
 ("Right sideburn",6,.3,[(322,149,6),(326,158,8),(328,172,6),(331,182,4),(335,188,0)]),
 ("Left sideburn",6,.3,[(455,149,6),(454,158,8),(451,171,6),(448,182,4),(446,188,0)])]
SIDE=[
 ("Front side scallop",7,2.6,[(829,83,5),(818,90,8),(811,104,9),(812,120,9),(820,141,10),(834,155,7),(850,159,0)]),
 ("Middle side scallop",7,3.4,[(837,81,5),(832,90,8),(832,103,9),(840,117,9),(851,126,7),(865,129,0)]),
 ("Upper side scallop",7,4.3,[(847,73,4),(853,80,8),(861,93,10),(873,107,10),(885,117,7),(900,120,0)]),
 ("Rear side fold",7,1.0,[(863,69,6),(883,77,9),(899,95,10),(912,117,11),(921,140,8),(929,155,0)]),
 ("Low side scallop",6,1.5,[(858,110,5),(866,122,8),(878,139,9),(893,149,5),(898,150,0)]),
 ("Ear back turn",7,-.3,[(907,146,5),(902,164,9),(893,184,9),(879,203,7),(867,217,0)])]
BACK=[
 ("Lower left",6,-.2,[(1034,151,7),(1040,172,11),(1051,193,10),(1065,213,6),(1080,226,0)]),
 ("Lower right",6,.2,[(1127,146,7),(1121,170,11),(1107,193,11),(1091,211,7),(1079,225,0)]),
 ("Nape middle",6,.2,[(1074,137,6),(1080,154,11),(1083,174,11),(1079,191,7),(1077,202,0)]),
 ("Left outer step",6,.3,[(1037,87,5),(1023,100,9),(1012,121,10),(1002,137,7),(987,140,0)]),
 ("Right outer step",6,.5,[(1123,86,5),(1139,97,9),(1153,111,9),(1164,120,6),(1173,117,0)]),
 ("Left lower step",6,-.2,[(1012,118,6),(1005,136,8),(1004,153,8),(1008,166,5),(1015,172,0)]),
 ("Right lower step",6,-.2,[(1149,117,7),(1155,133,9),(1161,149,8),(1173,155,0)]),
 ("Left lower arc",7,.6,[(1030,116,7),(1023,135,10),(1025,152,11),(1031,168,8),(1035,185,0)]),
 ("Right lower arc",7,.8,[(1133,108,7),(1138,128,11),(1136,148,11),(1129,165,8),(1119,185,0)]),
 ("Left inner tier",7,1.2,[(1052,100,6),(1043,118,10),(1041,139,11),(1047,153,9),(1063,175,0)]),
 ("Right inner tier",7,1.6,[(1109,108,6),(1116,128,10),(1113,149,11),(1103,165,9),(1091,184,0)]),
 ("Left crown outer",7,1.8,[(1063,74,4),(1047,77,7),(1033,86,9),(1020,101,7),(1010,113,4),(994,109,0)]),
 ("Right crown outer",7,1.7,[(1094,73,4),(1111,80,8),(1127,90,10),(1143,108,10),(1151,123,7),(1160,129,0)]),
 ("Left hooked shoulder",8,4.6,[(1077,77,6),(1065,77,10),(1053,86,12),(1045,99,11),(1042,114,9),(1044,128,6),(1052,138,0)]),
 ("Right hooked shoulder",8,4.3,[(1076,76,5),(1092,77,11),(1106,84,13),(1116,98,12),(1117,113,10),(1109,127,7),(1097,136,0)]),
 ("Centre fall",8,3.8,[(1078,82,5),(1085,91,11),(1087,108,14),(1081,126,13),(1070,142,7),(1063,152,0)])]

def smooth_curve(points,t):
    p=np.asarray(points,dtype=float)
    t=np.clip(np.asarray(t,dtype=float),0,1)
    length=np.r_[0,np.cumsum(np.maximum(.01,np.linalg.norm(np.diff(p[:,:2],axis=0),axis=1)))]
    length/=length[-1]
    k=np.clip(np.searchsorted(length,t,side="right")-1,0,len(p)-2)
    delta=length[k+1]-length[k];v=(t-length[k])/delta
    slope=np.empty_like(p)
    slope[0]=(p[1]-p[0])/(length[1]-length[0]);slope[-1]=(p[-1]-p[-2])/(length[-1]-length[-2])
    slope[1:-1]=(p[2:]-p[:-2])/(length[2:,None]-length[:-2,None])
    v=v[...,None];delta=delta[...,None]
    return (2*v**3-3*v**2+1)*p[k]+(v**3-2*v**2+v)*delta*slope[k]+(-2*v**3+3*v**2)*p[k+1]+(v**3-v**2)*delta*slope[k+1]

LEVELS=np.array([54,60,68,80,95,113,132,152,170,186,200,213,222,228,233])
AXES=[[1,26,39,54,69,81,85,83,75,63,48,33,18,9,4],
      [1,25,39,56,73,86,89,87,78,66,52,34,20,10,5],
      [-6,-5,-4,-3,-1,0,0,0,0,0,0,0,0,0,0],[-8,-6,-4,-1,1,3,4,5,6,6,4,2,0,0,0]]

# This sampled skull profile is populated from the head's authoritative spline by
# the Blender builder. Keeping it optional also permits offline texture fitting.
HEAD=None
def head_axes(row):
    if HEAD is None:return None
    return tuple(np.interp(row,HEAD[:,0],HEAD[:,j]) for j in (1,2,3))

def section_curve(row,xp,values):
    xp=np.asarray(xp,dtype=float);values=np.asarray(values,dtype=float)
    r=np.clip(row,xp[0],xp[-1])
    i=np.clip(np.searchsorted(xp,r,side="right")-1,0,len(xp)-2)
    d=xp[i+1]-xp[i];t=(r-xp[i])/d
    slope=np.gradient(values,xp)
    return ((2*t**3-3*t*t+1)*values[i]+(t**3-2*t*t+t)*d*slope[i]+
            (-2*t**3+3*t*t)*values[i+1]+(t**3-t*t)*d*slope[i+1])

NAPE_LEVELS=[138,150,163,170,178,186,195,205,215,221,225,228]
NAPE_LEFT=[844,849,854,866,872,874,871,861,862,866,872,876]
NAPE_RIGHT=[946,952,951,950,947,936,928,918,899,888,879,876]
NAPE_WIDTH=[74,82,82,77,66,62,54,46,33,23,10,0]
def nape_section(row):
    left=section_curve(row,NAPE_LEVELS,NAPE_LEFT)-856.5
    right=section_curve(row,NAPE_LEVELS,NAPE_RIGHT)-856.5
    width=section_curve(row,NAPE_LEVELS,NAPE_WIDTH)
    return (left+right)*.5,(right-left)*.5,width

def depth(x,row,view):
    rx,ry,cx,cy=(section_curve(row,LEVELS,values) for values in AXES)
    if view in ('front','back'):
        offset=x-390.5 if view=='front' else 1080.5-x
        fraction=np.abs((offset-cx)/rx);radius=ry;center=-cy if view=='front' else cy
    else:
        offset=x-856.5
        fraction=np.abs((offset-cy)/ry);radius=rx;center=cx if view=='profile+' else -cx
    shoulder=np.sqrt(np.maximum(.2775,1-fraction**2))
    shoulder=np.where(fraction>.85,.055+(.52678-.055)*np.exp(-3.417*np.maximum(fraction-.85,0)),shoulder)
    estimate=center+radius*shoulder
    if view=="back":
        mid,half,wide=nape_section(row)
        nape=mid+half*np.sqrt(np.maximum(.02,1-(offset/np.maximum(wide,2))**2))
        f=np.clip((row-145)/35,0,1);f=f*f*(3-2*f)
        estimate=(1-f)*estimate+f*nape
    head=head_axes(row)
    if head is not None:
        hx,hy,dy=head
        if view in ('front','back'):
            d=np.abs(offset)/np.maximum(hx,.01)
            limit=(dy if view=='back' else -dy)+hy*np.maximum(0,1-d**2.32)**(1/2.32)
        else:
            d=np.abs(offset-dy)/np.maximum(hy,.01)
            limit=hx*np.maximum(0,1-d**2.32)**(1/2.32)
        # Carry the curve over the physical scalp at the front of the ear and temple.
        estimate=np.maximum(estimate,np.where(d<1,limit+2.4,-1000))
    return estimate

def surface(lock,t,phi):
    view,name,rows,rank,points=lock
    t,phi=np.broadcast_arrays(t,phi)
    c=smooth_curve(points,t);diff=smooth_curve(points,t+.001)-smooth_curve(points,t-.001)
    direction=diff[...,:2]/np.maximum(1e-9,np.linalg.norm(diff[...,:2],axis=-1,keepdims=True))
    width=np.maximum(0.,c[...,2]);w=width*np.cos(phi)
    ox=-direction[...,1]*w;oy=direction[...,0]*w
    sx=c[...,0]+ox;row=c[...,1]+oy
    # Each actual contour stays in its study's projection. Depth slope accounts
    # for wrapping a broad clump around the flank without twisting its drawn edges.
    carrier=depth(sx,row,view)
    h=np.sin(phi)
    body=width*(.81*np.maximum(h,0)-.60*np.maximum(-h,0))
    carrier+=rank+body-3.5*np.exp(-(t/.13)**2)+1.2*t**3
    if view=='front':x=sx-390.5;y=-carrier
    elif view=='back':x=1080.5-sx;y=carrier
    else:y=sx-856.5;x=(1 if view=='profile+' else -1)*carrier
    return np.stack((x,y,505-row),axis=-1)/(451/1.3)

def locks():
    parts=[]
    for view,items in [('front',FRONT),('back',BACK),('profile+',SIDE),('profile-',SIDE)]:
        for name,rows,rank,points in items:parts.append((view,name,rows,rank,points))
    return parts
