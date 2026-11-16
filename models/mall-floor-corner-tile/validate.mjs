import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {Box3, Vector3, Raycaster} from 'three';
import {validateBytes} from 'gltf-validator';
import {readGlb} from '../mall-floor-tile/glb.mjs';
const root=new URL('../../',import.meta.url);
const paths={tile:'models/mall-floor-corner-tile/exports/mall-floor-corner-tile.glb',mitre:'models/mall-floor-mitred-trim/exports/mall-floor-mitred-trim.glb',floor:'models/mall-floor-tile/exports/mall-floor-tile-module.glb',edge:'models/mall-floor-edge-trim/exports/mall-floor-edge-trim.glb'};
const data={};for(const [key,path] of Object.entries(paths))data[key]=await readGlb(new URL(path,root).pathname);
const near=(a,b)=>assert.ok(Math.abs(a-b)<1e-6,`${a} != ${b}`);
const bb=o=>{o.updateMatrixWorld(true);return new Box3().setFromObject(o)};
const place=(scene,x,y,z,rotation=0)=>{let o=scene.clone(true);o.position.set(x,y,z);o.rotation.y=rotation;o.updateMatrixWorld(true);return o};
const models={};
for(const id of ['tile','mitre']){
 const d=data[id],v=await validateBytes(new Uint8Array(d.bytes),{uri:`${id}.glb`});
 assert.equal(v.issues.numErrors,0,`${id} errors`);assert.equal(v.issues.numWarnings,0,`${id} warnings`);
 assert.ok(![...(d.json.buffers??[]),...(d.json.images??[])].some(x=>x.uri));
 const bounds=bb(d.scene),size=bounds.getSize(new Vector3());const expected=id==='tile'?[1.2,.03,1.2]:[1.26,.03,1.26];
 expected.forEach((v,i)=>near(size.getComponent(i),v));
 let triangles=0;for(const mesh of d.json.meshes??[])for(const p of mesh.primitives)triangles+=(p.indices===undefined?d.json.accessors[p.attributes.POSITION].count:d.json.accessors[p.indices].count)/3;
 models[id]={bytes:d.bytes.length,triangles,sha256:crypto.createHash('sha256').update(d.bytes).digest('hex'),dimensions_m:size.toArray(),validator:{errors:v.issues.numErrors,warnings:v.issues.numWarnings,infos:v.issues.numInfos}};
}
const tile=place(data.tile.scene,0,-.03,0), floorX=place(data.floor.scene,-1.2,-.03,0),floorZ=place(data.floor.scene,0,-.03,-1.2);
const trim=place(data.mitre.scene,0,0,0), edgeX=place(data.edge.scene,-1.2,0,.63),edgeZ=place(data.edge.scene,.63,0,-1.2,Math.PI/2);
const [t,x,z,m,ex,ez]=[tile,floorX,floorZ,trim,edgeX,edgeZ].map(bb);
near(t.min.x,x.max.x);near(t.min.z,z.max.z);near(t.max.y,0);near(m.max.y,0);near(m.min.x,ex.max.x);near(m.min.z,ez.max.z);
// Probe the exported triangles on both sides of the diagonal. Each point must hit exactly one mitred cap.
const hits=[];
for(const [px,pz,expected] of [[.61,.64,'Front'],[.64,.61,'Right'],[.59,.63,'Front'],[.63,.59,'Right']]){
 const all=new Raycaster(new Vector3(px,1,pz),new Vector3(0,-1,0)).intersectObject(trim,true).filter(h=>Math.abs(h.point.y)<1e-6);
 const names=[...new Set(all.map(h=>h.object.name))];assert.equal(names.length,1,`${px},${pz}: ${names}`);assert.ok(names[0].includes(expected),`${px},${pz}: ${names}`);hits.push({x:px,z:pz,part:names[0]});
}
const report={result:'PASS',models,assembly:{tile:[0,-.03,0],mitre:[0,0,0],neighbourFloors:[[-1.2,-.03,0],[0,-.03,-1.2]],straightEdges:[[-1.2,0,.63],[.63,0,-1.2]],mitreTopRays:hits},limits:'One 90-degree outside configuration, bounding boxes and four top-surface ray samples. Does not prove full mesh intersection, other configurations or physical construction safety.'};
for(const id of ['mall-floor-corner-tile','mall-floor-mitred-trim'])fs.writeFileSync(new URL(`models/${id}/reports/validation.json`,root),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
