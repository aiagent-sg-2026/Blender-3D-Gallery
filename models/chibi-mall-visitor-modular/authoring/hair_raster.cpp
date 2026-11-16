// Orthographic z-buffer for reference-space silhouette and true source UV visibility.
#include <algorithm>
#include <cmath>
#include <limits>
extern "C" void raster(const double* vertex,const int* tris,int count,int width,int height,double* z,int* face,double* bary){
  std::fill(z,z+width*height,-1e6);
  std::fill(face,face+width*height,-1);
  for(int i=0;i<count;++i){
    const double* a=vertex+3*tris[3*i];const double* b=vertex+3*tris[3*i+1];const double* c=vertex+3*tris[3*i+2];
    double ux=b[0]-a[0],uy=b[1]-a[1],vx=c[0]-a[0],vy=c[1]-a[1],det=ux*vy-uy*vx;
    if(std::abs(det)<1e-12)continue;
    int x0=std::max(0,(int)std::ceil(std::min({a[0],b[0],c[0]}))),x1=std::min(width-1,(int)std::floor(std::max({a[0],b[0],c[0]})));
    int y0=std::max(0,(int)std::ceil(std::min({a[1],b[1],c[1]}))),y1=std::min(height-1,(int)std::floor(std::max({a[1],b[1],c[1]})));
    for(int y=y0;y<=y1;++y)for(int x=x0;x<=x1;++x){
      double dx=x-a[0],dy=y-a[1],s=(dx*vy-dy*vx)/det,t=(ux*dy-uy*dx)/det,r=1.-s-t;
      if(std::min({r,s,t})<-.00001)continue;
      int cell=y*width+x;double d=r*a[2]+s*b[2]+t*c[2];
      if(d>z[cell]){z[cell]=d;face[cell]=i;bary[cell*3]=r;bary[cell*3+1]=s;bary[cell*3+2]=t;}
    }
  }
}
