"""Fit the free-lock assembly to the hair silhouette in three measured panels."""
import numpy as np


def ease(value,low,high):
    phase=np.clip((value-low)/(high-low),0,1)
    return phase**2*(3-2*phase)


def temple(points,layer):
    x,y,z=points.T;row=505-z
    angle=np.radians(-28.);right=np.array([np.cos(angle),np.sin(angle),0.])
    u=points@right
    # A continuous inset behind the large temple curl separates two silhouette
    # tiers. Only the proximal shoulder follows the inset on the hooked lock.
    outside=ease(-u,63,92)
    upper=8.4*np.exp(-((row-94)/19)**2)
    notch=5.3*np.exp(-((row-126)/7.3)**2)
    offset=(upper+notch)*outside
    if layer=='hook':offset=upper*.22*outside*(1-ease(row,103,114))
    if layer=='lower':offset-=3.5*outside*np.exp(-((row-154)/8.)**2)
    return points+offset[:,None]*right


def apply(points,normals,transform):
    # Transport sculpt normals by the local inverse transpose. The same spatial
    # fit acts on every physical shell, its guide curves and the dense bake donor.
    transformed=transform(points);e=.18
    dx=(transform(points+[e,0,0])-transformed)/e
    dy=(transform(points+[0,e,0])-transformed)/e
    dz=(transform(points+[0,0,e])-transformed)/e
    n=np.cross(dy,dz)*normals[:,0,None]+np.cross(dz,dx)*normals[:,1,None]+np.cross(dx,dy)*normals[:,2,None]
    n/=np.maximum(1e-10,np.linalg.norm(n,axis=1,keepdims=True))
    return transformed,n
