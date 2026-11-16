"""Small native orthographic rasterizer used only for optional reference refitting."""
import ctypes
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import numpy as np

def library():
    source=Path(__file__).with_suffix('.cpp')
    ext='.dylib' if sys.platform=='darwin' else '.so'
    lib=Path(tempfile.gettempdir())/('gjh-hair-raster-'+hashlib.sha256(source.read_bytes()).hexdigest()[:18]+ext)
    if not lib.exists():
        subprocess.run(['c++','-std=c++11','-O3','-fPIC','-shared',str(source),'-o',str(lib)],check=True)
    dll=ctypes.CDLL(str(lib));arr=np.ctypeslib.ndpointer
    dll.raster.argtypes=[arr('f8',flags='C'),arr('i4',flags='C'),ctypes.c_int,ctypes.c_int,ctypes.c_int,arr('f8',flags='C'),arr('i4',flags='C'),arr('f8',flags='C')]
    dll.raster.restype=None
    return dll
DLL=library()
def draw(points,faces,cam,scale=1):
    h,w=cam.mask.shape;h*=scale;w*=scale
    # Camera registration is rigid here; all dimensions are in original sheet pixels.
    x=points@cam.right+cam.cx-cam.left;y=505.-points[:,2]-48.;d=points@cam.eye
    vertices=np.ascontiguousarray(np.stack((x*scale,y*scale,d),axis=1),'f8')
    idx=np.ascontiguousarray(faces,'i4');z=np.empty((h,w));ids=np.empty((h,w),'i4');weights=np.zeros((h,w,3))
    DLL.raster(vertices,idx,len(idx),w,h,z,ids,weights)
    return z,ids,weights
