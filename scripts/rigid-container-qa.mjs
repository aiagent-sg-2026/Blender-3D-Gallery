// Opt-in scope: static meshes inside a container with rigid node animations.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
export const RIGID_FLAG='--static-meshes-in-rigid-container';
export function rigidScope(json){
 assert.ok((json.animations?.length??0)>0,'Rigid-container opt-in requires actual clips');
 assert.equal(json.skins?.length??0,0,'Skinned geometry is outside this repair scope');
 assert.ok(json.meshes.every(m=>m.primitives.every(p=>!(p.targets?.length))),'Morph geometry is outside this repair scope');
 const animated=new Set();
 for(const a of json.animations)for(const c of a.channels){
  assert.ok(Number.isInteger(c.target.node)&&['translation','rotation','scale'].includes(c.target.path),'Only rigid node transform channels are supported');
  animated.add(c.target.node);
 }
 const parents=new Map();
 json.nodes.forEach((n,i)=>(n.children??[]).forEach(child=>{assert.ok(!parents.has(child),'Multiple node parents require separate review');parents.set(child,i);}));
 const blocked=node=>{const seen=new Set();for(let i=node;i!==undefined;i=parents.get(i)){assert.ok(!seen.has(i),'Cyclic node graph');seen.add(i);if(animated.has(i))return true;}return false;};
 return {assertStaticMesh(mesh){
  const uses=json.nodes.flatMap((n,i)=>n.mesh===mesh?[i]:[]);assert.ok(uses.length,'Mesh must belong to a scene node');
  assert.ok(uses.every(n=>!blocked(n)),'A changed mesh or ancestor is animated');
  return uses.map(n=>json.nodes[n].name??String(n));
 },clips:json.animations.length};
}
export function animationPayload(json,binary){
 const digest=createHash('sha256');
 digest.update(JSON.stringify(json.animations));
 const accessors=new Set(json.animations.flatMap(a=>a.samplers.flatMap(s=>[s.input,s.output])));
 for(const i of [...accessors].sort((a,b)=>a-b)){
  const a=json.accessors[i];assert.ok(!a.sparse&&Number.isInteger(a.bufferView),'Sparse animation accessors require separate review');
  const v=json.bufferViews[a.bufferView];assert.equal(v.buffer,0);
  digest.update(JSON.stringify({i,accessor:a,view:v}));
  digest.update(binary.subarray(v.byteOffset??0,(v.byteOffset??0)+v.byteLength));
 }
 return {clips:json.animations.length,accessors:accessors.size,sha256:digest.digest('hex')};
}
export function compareNativeClips(before,after,tolerance=1e-6){
 const clips=value=>new Map(value.map(a=>[a.name,a]));const a=clips(before),b=clips(after);
 assert.equal(a.size,before.length,'Duplicate native clip names require review');assert.equal(b.size,after.length,'Duplicate native clip names require review');
 assert.equal(a.size,b.size,'Native clip count changed');assert.deepEqual([...a.keys()].sort(),[...b.keys()].sort(),'Native clip names changed');
 let maxTimeDelta=0,maxValueDelta=0,tracks=0;
 for(const [name,clip]of a){
  const x=new Map(clip.tracks.map(t=>[t.name,t])),y=new Map(b.get(name).tracks.map(t=>[t.name,t]));
  assert.equal(x.size,clip.tracks.length);assert.equal(y.size,b.get(name).tracks.length);
  assert.deepEqual([...x.keys()].sort(),[...y.keys()].sort(),'Native tracks changed: '+name);
  for(const [key,t]of x){const u=y.get(key);assert.equal(t.getInterpolation(),u.getInterpolation());
   assert.equal(t.times.length,u.times.length);assert.equal(t.values.length,u.values.length);
   for(let i=0;i<t.times.length;i++)maxTimeDelta=Math.max(maxTimeDelta,Math.abs(t.times[i]-u.times[i]));
   for(let i=0;i<t.values.length;i++)maxValueDelta=Math.max(maxValueDelta,Math.abs(t.values[i]-u.values[i]));
   tracks++;
  }
 }
 assert.ok(maxTimeDelta<=tolerance&&maxValueDelta<=tolerance,'Native animation drift exceeds reviewed tolerance');
 return {clips:a.size,tracks,maxTimeDelta,maxValueDelta,tolerance};
}
