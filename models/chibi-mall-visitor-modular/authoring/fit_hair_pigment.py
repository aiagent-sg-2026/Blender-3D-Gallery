"""Fit a single static pigment correction to true exported UVs in registered views."""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage as nd
from hair_reference import Study

def fit(reference,folder,previous=None):
    sheet=np.array(Image.open(reference).convert('RGB'))
    meta=json.loads((folder/'manifest.json').read_text())
    numerator=np.zeros((512,512,3));mass=np.zeros((512,512))
    for name,angle,cx in meta['views']:
        if name=='quarter':continue  # retain the diagonal as a held-out view
        srcname='profile' if name=='opposite' else name
        matte=Study(sheet,srcname)
        w,h=meta['viewport'];s=meta['pixelsPerReferencePixel']
        yy,xx=np.indices((h,w));x=cx+(xx+.5-w/2)/s;y=meta['viewCenterY']+(yy+.5-h/2)/s
        if name=='opposite':x=cx-(xx+.5-w/2)/s
        sr=np.stack([nd.map_coordinates(sheet[:,:,i].astype(float),(y,x),order=1,prefilter=False) for i in range(3)],axis=-1)
        mask=np.array(Image.open(folder/(name+'-mask.png')).convert('L'))>251
        refdist=nd.map_coordinates(matte.sdf,(y-49,x-matte.left),order=1,mode='constant',cval=-10)
        keep=nd.distance_transform_edt(mask)>3.1;keep&=refdist>2.1
        rgb=np.array(Image.open(folder/(name+'-rgb.png')).convert('RGB')).astype(float)
        # Use the low/medium spatial frequency component. This estimates stationary
        # pigment and ambient contact tones, preserving view-dependent PBR highlights.
        delta=nd.gaussian_filter(sr-rgb,(3.5,3.5,0))
        uv=np.array(Image.open(folder/(name+'-uv.png')).convert('RGB'),dtype=np.int32)
        code=uv[:,:,0]+256*uv[:,:,1]+65536*uv[:,:,2]-1
        keep&=(code>=0)&(code<512**2)
        ax=code%512;ay=code//512
        for pix in (ax,ay):
            med=nd.median_filter(pix,3)
            keep&=abs(med-pix)<6
        base=np.clip(refdist/9.,.13,1.)
        src=np.clip(rgb.mean(axis=-1),14,145)
        # In the scene's dark diffuse range, one sRGB atlas unit has a smaller
        # screen response than one display unit.
        delta=np.clip(delta*(1.19+9/(src+5))[:,:,None],-35,40)
        ids=(ay[keep],ax[keep]);np.add.at(mass,ids,base[keep])
        for k in range(3):np.add.at(numerator[:,:,k],ids,base[keep]*delta[:,:,k][keep])
    den=nd.gaussian_filter(mass,1.05);num=nd.gaussian_filter(numerator,(1.05,1.05,0))
    observed=den>.035
    correction=num/np.maximum(den,.025)[:,:,None]
    near=nd.distance_transform_edt(~observed,return_distances=False,return_indices=True)
    dist=nd.distance_transform_edt(~observed)
    correction=correction[tuple(near)]*np.exp(-(dist/8)**2)[:,:,None]
    if previous is not None:correction+=previous
    return np.clip(correction,-47,50).astype('f4')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('reference',type=Path);parser.add_argument('folder',type=Path);parser.add_argument('out',type=Path);parser.add_argument('--previous',type=Path);opt=parser.parse_args()
    old=np.load(opt.previous)['delta'] if opt.previous else None
    data=fit(opt.reference,opt.folder,old)
    np.savez_compressed(opt.out,delta=np.round(data*16).astype('i2')/np.float32(16))
