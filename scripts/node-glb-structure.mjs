import assert from 'node:assert/strict';
import fs from 'node:fs';
import { createHash } from 'node:crypto';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
// Node structural loader: PNG dimensions are checked here, not rendered. Actual
// decoded pixels require separate browser/visual verification.
globalThis.self ??= globalThis;
globalThis.createImageBitmap ??= async blob => {
 const b=Buffer.from(await blob.arrayBuffer());assert.equal(b.toString('hex',0,8),'89504e470d0a1a0a');
 return {width:b.readUInt32BE(16),height:b.readUInt32BE(20),close(){}};
};
export const near=(a,b)=>assert.ok(Math.abs(a-b)<1e-6,`${a} != ${b}`);
export async function readGlb(file){
 const bytes=fs.readFileSync(file),json=JSON.parse(bytes.subarray(20,20+bytes.readUInt32LE(12)));
 const gltf=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'');
 gltf.scene.updateMatrixWorld(true);return {bytes,json,scene:gltf.scene};
}

export function materialDefinitions(json, binary) {
 const texture = index => {
  const value=json.textures[index],image=json.images[value.source];
  assert.ok(Number.isInteger(image.bufferView),'Embedded texture payload required for material comparison');
  const view=json.bufferViews[image.bufferView];assert.equal(view.buffer,0);
  const bytes=binary.subarray(view.byteOffset??0,(view.byteOffset??0)+view.byteLength);
  return {...value,source:{mimeType:image.mimeType,sha256:createHash('sha256').update(bytes).digest('hex')},
   sampler:value.sampler===undefined?null:json.samplers[value.sampler]};
 };
 const normalize=(value,key='')=>{
  if(Array.isArray(value))return value.map(v=>normalize(v));
  if(!value||typeof value!=='object')return value;
  return Object.fromEntries(Object.entries(value).map(([k,v])=>[k,
   k==='index'&&key.endsWith('Texture')?texture(v):normalize(v,k)]));
 };
 const byName=new Map();
 for(const material of json.materials){
  const normalized=normalize(material);
  if(byName.has(material.name))assert.deepEqual(byName.get(material.name),normalized,
   'Distinct same-name materials require explicit binding review');
  else byName.set(material.name,normalized);
 }
 return [...byName.values()].sort((a,b)=>(a.name??'').localeCompare(b.name??''));
}
