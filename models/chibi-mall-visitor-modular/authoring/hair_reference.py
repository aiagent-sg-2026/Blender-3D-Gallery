"""Registered panel coordinates, matte extraction, and cranial section tracings."""
import numpy as np
from scipy import ndimage as nd

VIEWS = {
    "front": (289, 490, 390.5, 0.),
    "profile": (758, 964, 856.5, 90.),
    "back": (977, 1183, 1080.5, 180.),
    "quarter": (39, 247, 136., -37.),
}
TRIM = {
    "front": [[(351,151),(357,142),(362,133),(367,125),(369,135),(374,142)],
              [(408,114),(416,115),(423,117),(430,121),(434,128),(436,140),(437,151)]],
    "profile": [[(788,141),(794,130),(799,120),(804,136),(809,149)]],
    "quarter": [[(139,152),(146,143),(153,131),(161,126),(165,139)],
                [(192,115),(198,118),(204,123),(210,134),(213,147)]]
}


class Study:
    def __init__(self, image, name):
        self.left,right,self.cx,self.deg=VIEWS[name]
        red,green,blue=image[49:233,self.left:right].astype(float).transpose(2,0,1)
        dark=(red<167)&(green<145)&(blue<148)&(red-green<42)
        labels,_=nd.label(dark)
        mask=nd.binary_fill_holes(labels==(np.argmax(np.bincount(labels.ravel())[1:])+1))
        y,x=np.indices(mask.shape)
        x+=self.left;y+=49
        for trace in TRIM.get(name,[]):
            sx,sy=np.array(trace).T
            mask &= ~((x>=sx[0])&(x<=sx[-1])&(y>np.interp(x,sx,sy)))
        self.mask=mask
        self.sdf=nd.distance_transform_edt(mask)-nd.distance_transform_edt(~mask)

LEVELS=np.array([54,60,68,80,95,113,132,152,170,186,200,213,222,228,233])
AXES=[[1,26,39,54,69,81,85,83,75,63,48,33,18,9,4],
      [1,25,39,56,73,86,89,87,78,66,52,34,20,10,5],
      [-6,-5,-4,-3,-1,0,0,0,0,0,0,0,0,0,0],[-8,-6,-4,-1,1,3,4,5,6,6,4,2,0,0,0]]

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

