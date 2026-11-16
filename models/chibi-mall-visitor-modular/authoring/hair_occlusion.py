"""Rasterize the real physical skin and ear geometry for camera-space visibility constraints."""
import json
import struct
from pathlib import Path
import numpy as np

def read_face(glb):
    b=Path(glb).read_bytes();size=struct.unpack_from('<I',b,12)[0]
    doc=json.loads(b[20:20+size]);binary=20+size+8
    def read(i):
        a=doc['accessors'][i];v=doc['bufferViews'][a['bufferView']]
        dtype={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']]
        cols={'VEC3':3,'SCALAR':1}[a['type']]
        values=np.frombuffer(b,dtype=dtype,count=a['count']*cols,offset=binary+v.get('byteOffset',0)+a.get('byteOffset',0))
        return values.reshape(-1,cols)
    index=next(n['mesh'] for n in doc['nodes'] if n.get('name')=='Face')
    p=[];f=[]
    for part in doc['meshes'][index]['primitives']:
        points=read(part['attributes']['POSITION']);ids=read(part['indices']).ravel().reshape(-1,3)
        f.append(ids+sum(map(len,p)));p.append(np.stack((points[:,0],-points[:,2],points[:,1]),axis=-1))
    return np.vstack(p)*451/1.3,np.vstack(f).astype('i4')

def depth_image(data,camera,shape):
    p,indices=data;xx,yy,dep=camera.projection(p);xy=np.stack((xx,yy),axis=1)
    out=np.full(shape,-180.,dtype=float)
    for ids in indices:
        a,b,c=xy[ids];bounds=xy[ids]
        lo=np.maximum(0,np.ceil(bounds.min(axis=0)).astype(int));hi=np.minimum([shape[1]-1,shape[0]-1],np.floor(bounds.max(axis=0)).astype(int))
        if (lo>hi).any():continue
        m=np.array((b-a,c-a)).T
        if abs(np.linalg.det(m))<1e-8:continue
        y,x=np.mgrid[lo[1]:hi[1]+1,lo[0]:hi[0]+1]
        v=np.stack((x-a[0],y-a[1]),axis=-1)@np.linalg.inv(m).T
        weights=np.stack((1-v.sum(axis=-1),v[...,0],v[...,1]),axis=-1)
        use=weights.min(axis=-1)>=-.0001
        dst=out[y[use],x[use]];out[y[use],x[use]]=np.maximum(dst,weights[use]@dep[ids])
    return out
