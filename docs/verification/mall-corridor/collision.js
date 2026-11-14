import {Box3,Vector3,Ray} from 'three';
import {OBB} from 'three/addons/math/OBB.js';
// The 0.56 m cylinder encloses the measured idle/walk turn footprint (max 0.543 m).
export const BODY={radius:.56,height:1.8,speed:.95,step:.025};
const cross=(a,b,c)=>(b.x-a.x)*(c.z-a.z)-(b.z-a.z)*(c.x-a.x);
function hull(points){
 const sorted=points.sort((a,b)=>a.x-b.x||a.z-b.z).filter((p,i,a)=>!i||Math.abs(p.x-a[i-1].x)>1e-8||Math.abs(p.z-a[i-1].z)>1e-8);
 const lower=[],upper=[];for(const p of sorted){while(lower.length>1&&cross(lower.at(-2),lower.at(-1),p)<=0)lower.pop();lower.push(p)}
 for(const p of [...sorted].reverse()){while(upper.length>1&&cross(upper.at(-2),upper.at(-1),p)<=0)upper.pop();upper.push(p)}return lower.slice(0,-1).concat(upper.slice(0,-1));
}
function circleHits(p,polygon,radius){
 if(polygon.length<3)return false;
 let inside=true,min=Infinity;
 for(let i=0;i<polygon.length;i++){
  const a=polygon[i],b=polygon[(i+1)%polygon.length];if(cross(a,b,p)<-1e-8)inside=false;
  const dx=b.x-a.x,dz=b.z-a.z,t=Math.max(0,Math.min(1,((p.x-a.x)*dx+(p.z-a.z)*dz)/(dx*dx+dz*dz)));
  min=Math.min(min,Math.hypot(p.x-a.x-t*dx,p.z-a.z-t*dz));
 }return inside||min<radius-1e-5;
}
export function createCollisionWorld(root){
 const floors=[],fixed=[],moving=[];root.updateMatrixWorld(true);
 root.traverse(o=>{
  if(/^Floor_\d+$/.test(o.name))floors.push(new Box3().setFromObject(o));
  if(!o.isMesh)return;
  let isFloor=false,isMoving=false;for(let p=o;p;p=p.parent){if(/^Floor_\d+$/.test(p.name))isFloor=true;if(p.name.startsWith('HINGE_Left')||p.name.startsWith('HINGE_Right'))isMoving=true}
  if(isFloor)return;
  o.geometry.computeBoundingBox();const box=o.geometry.boundingBox;
  const item={object:o,local:box.clone(),name:o.name};(isMoving?moving:fixed).push(item);
 });
 if(!floors.length)throw Error('Walking needs the actual floor-cell union');
 function update(item){
  const b=item.local.clone().applyMatrix4(item.object.matrixWorld);item.minY=b.min.y;item.maxY=b.max.y;
  item.obb=new OBB(item.local.getCenter(new Vector3()),item.local.getSize(new Vector3()).multiplyScalar(.5)).applyMatrix4(item.object.matrixWorld);
  const points=[];for(const x of [item.local.min.x,item.local.max.x])for(const y of [item.local.min.y,item.local.max.y])for(const z of [item.local.min.z,item.local.max.z])points.push(new Vector3(x,y,z).applyMatrix4(item.object.matrixWorld));item.polygon=hull(points);
 }
 for(const item of fixed)update(item);
 const refresh=()=>{root.updateMatrixWorld(true);for(const item of moving)update(item)};refresh();
 const inFloor=p=>floors.some(f=>p.x>=f.min.x-1e-5&&p.x<=f.max.x+1e-5&&p.z>=f.min.z-1e-5&&p.z<=f.max.z+1e-5);
 function obstruction(p){
  if(!Number.isFinite(p.x)||!Number.isFinite(p.z))return 'Invalid position';
  // Corners/outer edges are bounded by the body footprint, not just its centre.
  if(!inFloor(p))return 'Floor edge';
  for(let i=0;i<24;i++){const a=i*Math.PI/12;if(!inFloor({x:p.x+Math.cos(a)*BODY.radius,z:p.z+Math.sin(a)*BODY.radius}))return 'Floor edge'}
  for(const item of [...fixed,...moving])if(item.maxY>.01&&item.minY<BODY.height&&circleHits(p,item.polygon,BODY.radius))return item.name;
  return null;
 }
 function move(p,dx,dz){
  const steps=Math.max(1,Math.ceil(Math.hypot(dx,dz)/BODY.step));let blocked=null;
  for(let i=0;i<steps;i++){
   const full={x:p.x+dx/steps,z:p.z+dz/steps};const hit=obstruction(full);
   if(!hit){p.x=full.x;p.z=full.z;continue}
   blocked=hit;
   const x={x:p.x+dx/steps,z:p.z};if(!obstruction(x))p.x=x.x;
   const z={x:p.x,z:p.z+dz/steps};if(!obstruction(z))p.z=z.z;
  }return blocked;
 }
 function doorTransition(from,to,p,apply){
  if(!Number.isFinite(to)||to<0||to>90)return false;
  const steps=Math.max(1,Math.ceil(Math.abs(to-from))); // One-degree sweep, same bound as scene QA.
  for(let i=1;i<=steps;i++){apply(from+(to-from)*i/steps);refresh();if(obstruction(p)){apply(from);refresh();return false}}
  apply(to);refresh();return true;
 }
 function cameraPosition(target,desired){
  const direction=desired.clone().sub(target),distance=direction.length();direction.normalize();const ray=new Ray(target,direction);let safe=distance;
  for(const item of [...fixed,...moving]){const hit=item.obb.intersectRay(ray,new Vector3());if(hit)safe=Math.min(safe,Math.max(.18,target.distanceTo(hit)-.12))}
  return target.clone().addScaledVector(direction,safe);
 }
 return {floors,refresh,obstruction,move,doorTransition,cameraPosition,obstacleCount:fixed.length+moving.length};
}
