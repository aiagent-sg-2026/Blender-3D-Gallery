"""Rest-guide displacements refit the corresponding loft without changing hair topology."""
from contextlib import contextmanager
from mathutils import Vector
from meshkit import spline

def bind(curve, start, rows, cross_weights):
    curve["firstVertex"]=start
    curve["sampleRows"]=rows
    curve["sectionWeights"]=cross_weights

def record_rest(collection):
    for obj in collection.objects:
        obj["restControls"]=[v for p in obj.data.splines[0].points for v in p.co[:3]]

@contextmanager
def evaluated_hair(obj,collection):
    offsets={}
    inv=obj.matrix_world.inverted()
    for guide in collection.objects:
        if "restControls" not in guide:continue
        control=guide.data.splines[0].points
        saved=guide["restControls"]
        if len(saved)!=3*len(control):
            raise ValueError(f"{guide.name}: keep the control count when refitting this loft.")
        delta=[inv@(guide.matrix_world@Vector(p.co[:3]))-Vector(saved[3*i:3*i+3]) for i,p in enumerate(control)]
        if max(d.length for d in delta)<1e-7:continue
        if "surfaceIndices" in guide:
            for idx,t,weight in zip(guide["surfaceIndices"],guide["surfaceParameters"],guide["surfaceWeights"]):
                offsets[idx]=offsets.get(idx,Vector())+spline(delta,t)*weight
            continue
        rows=guide["sampleRows"];cross=guide["sectionWeights"];start=guide["firstVertex"]
        for row in range(rows):
            change=spline(delta,row/(rows-1))
            for col,weight in enumerate(cross):
                idx=start+row*len(cross)+col
                offsets[idx]=offsets.get(idx,Vector())+change*weight
    original={i:obj.data.vertices[i].co.copy() for i in offsets}
    try:
        for i,d in offsets.items():obj.data.vertices[i].co=original[i]+d
        if offsets:obj.data.update()
        yield
    finally:
        for i,co in original.items():obj.data.vertices[i].co=co
        if original:obj.data.update()

