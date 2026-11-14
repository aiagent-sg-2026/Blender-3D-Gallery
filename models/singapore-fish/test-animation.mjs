import assert from 'node:assert/strict';
import fs from 'node:fs';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { AnimationMixer, Vector3 } from 'three';
const specs=JSON.parse(fs.readFileSync(new URL('species.json',import.meta.url)));
const reports=[];
for(const [slug,,,,kind,,,length] of specs){
 const bytes=fs.readFileSync(new URL(`${slug}/exports/model.glb`,import.meta.url));
 const gltf=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.length),'');
 assert.equal(gltf.animations.length,1,slug);const clip=gltf.animations[0];assert.equal(clip.name,'Swim_Loop');assert.ok(clip.duration>=1.5&&clip.duration<=3.3);
 for(const track of clip.tracks){const n=track.getValueSize(),end=track.values.length-n;for(let j=0;j<n;j++)assert.ok(Math.abs(track.values[j]-track.values[end+j])<1e-5,`${slug} loop seam ${track.name}`);}
 const meshes=[];gltf.scene.traverse(o=>{if(o.isSkinnedMesh)meshes.push(o)});assert.ok(meshes.length>=6,slug);
 const mixer=new AnimationMixer(gltf.scene);mixer.clipAction(clip).play();
 function snapshot(t){mixer.setTime(t);gltf.scene.updateMatrixWorld(true);return meshes.map(m=>{const attr=m.geometry.attributes.position;const points=[];for(let i=0;i<attr.count;i++)points.push(m.applyBoneTransform(i,new Vector3().fromBufferAttribute(attr,i)));return points;});}
 const a=snapshot(clip.duration*.25),b=snapshot(clip.duration*.75);const moves={};
 meshes.forEach((m,j)=>{moves[m.name]=Math.max(...a[j].map((p,i)=>p.distanceTo(b[j][i])))/length;});
 const maxFor=prefix=>Math.max(0,...Object.entries(moves).filter(([n])=>n.startsWith(prefix)).map(([,v])=>v));
 const tail=Math.max(maxFor('CAUDAL'),maxFor('TAIL'));assert.ok(tail>.005,`${slug} tail does not deform: ${tail}`);
 const fins=kind==='ray'?maxFor('BODY'):kind==='eel'?tail:maxFor('PECTORAL');assert.ok(fins>.003,`${slug} fin does not deform: ${fins}`);
 if(!['ray','eel'].includes(kind))assert.ok(maxFor('DORSAL')>.003,`${slug} dorsal static`);
 reports.push({slug,clip:clip.name,duration_seconds:clip.duration,skinned_meshes:meshes.length,tail_displacement_body_lengths:tail,fin_displacement_body_lengths:fins});mixer.stopAllAction();mixer.uncacheRoot(gltf.scene);
}
fs.writeFileSync(new URL('animation-validation.json',import.meta.url),JSON.stringify(reports,null,2)+'\n');
console.log('PASS: 60 GLB clips have seamless endpoints and measurable skinned tail/fin movement.');
