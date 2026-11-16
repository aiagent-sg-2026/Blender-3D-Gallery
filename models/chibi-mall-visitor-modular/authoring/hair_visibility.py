"""Allocate runtime triangles to surfaces visible from around, above and below the haircut."""
import numpy as np
from scipy import ndimage as nd

def visible_faces(points,faces,skin):
    face=points[faces]
    centers=face.mean(axis=1)
    normal=np.cross(face[:,1]-face[:,0],face[:,2]-face[:,0])
    normal/=np.maximum(np.linalg.norm(normal,axis=1,keepdims=True),1e-12)
    # Subdivide the physical skin triangles for the depth test, including the
    # ears. Otherwise QEM spends geometry on invisible inner locks around a wrist-like opening.
    skin_points,skin_faces=skin
    sf=skin_points[skin_faces]
    skin_samples=[skin_points]
    for i in range(13):
        for j in range(13-i):
            u,v=i/12,j/12
            skin_samples.append(sf[:,0]*(1-u-v)+sf[:,1]*u+sf[:,2]*v)
    occluders=np.vstack((points,centers,np.vstack(skin_samples)))-[0,2,366]
    probes=centers-[0,2,366]
    retained=np.zeros(len(faces),bool)
    width=220
    for yaw,pitch in [(a,h) for h,step in [(0,15),(27,20),(-27,25),(60,30),(-60,40),(85,180),(-85,180)] for a in range(0,360,step)]:
        a,t=np.deg2rad([yaw,pitch]);cam=np.array([np.sin(a)*np.cos(t),-np.cos(a)*np.cos(t),np.sin(t)])
        right=np.array([np.cos(a),np.sin(a),0]);top=np.cross(cam,right)
        def screen(p):
            return (np.clip(np.rint(p@right+width/2).astype(int),0,width-1),np.clip(np.rint(p@top+width/2).astype(int),0,width-1),p@cam)
        x,y,z=screen(occluders)
        zbuffer=np.full((width,width),-200.);np.maximum.at(zbuffer,(y,x),z)
        zbuffer=nd.maximum_filter(zbuffer,3)
        x,y,z=screen(probes)
        retained|=(normal@cam>-.25)&(z>=zbuffer[y,x]-2.05)
    # Keep a band on both sides of every visible edge for animation and manual edits.
    for _ in range(2):
        shared=np.zeros(len(points),bool);shared[faces[retained].ravel()]=True
        retained|=shared[faces].any(axis=1)
    return np.flatnonzero(retained).astype('i4')
