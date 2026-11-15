import assert from 'node:assert/strict';
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {Vector3} from 'three';
import validator from 'gltf-validator';
import {readGlb, materialDefinitions} from '../../scripts/node-glb-structure.mjs';
const dir=fileURLToPath(new URL('.',import.meta.url));
const report=JSON.parse(fs.readFileSync(dir+'reports/sources.json'));
assert.equal(report.comparison_basis,'same-toolchain unchanged source control');
const hash=data=>createHash('sha256').update(data).digest('hex');
async function inspect(file){
  const glb=await readGlb(dir+file);
  const result=await validator.validateBytes(new Uint8Array(glb.bytes));
  assert.equal(result.issues.numErrors,0);assert.equal(result.issues.numWarnings,0);
  const meshes={},transforms={},uvs={};let zero=0;
  glb.scene.updateMatrixWorld(true);
  glb.scene.traverse(o=>{
    transforms[o.name]=o.matrixWorld.toArray();
    if(!o.isMesh)return;
    const g=o.geometry, attrs=Object.fromEntries(Object.entries(g.attributes).map(([k,a])=>[k,{itemSize:a.itemSize,values:[...a.array]}]));
    uvs[o.name]=attrs.uv.values;delete attrs.uv;
    meshes[o.name]=hash(JSON.stringify({attrs,indices:g.index?[...g.index.array]:null,material:o.material.name}));
    for(let i=0;i<(g.index?.count??g.attributes.position.count);i+=3){
      const p=[0,1,2].map(j=>new Vector3().fromBufferAttribute(g.attributes.position,g.index?g.index.getX(i+j):i+j).applyMatrix4(o.matrixWorld));
      if(p[1].clone().sub(p[0]).cross(p[2].clone().sub(p[0])).lengthSq()===0)zero++;
    }
  });
  assert.equal(zero,0,file);
  return {file,sha256:hash(glb.bytes),meshes,transforms,materials:materialDefinitions(glb.json,glb.bytes.subarray(28+glb.bytes.readUInt32LE(12))),errors:0,warnings:0,zero_area_triangles:zero,uvs};
}
const shipped=await inspect('exports/optimized.glb'),control=await inspect(report.control_glb),edited=await inspect(report.edited_glb);
assert.deepEqual(control.transforms,edited.transforms);
assert.equal(Object.keys(control.meshes).length,42);
const changed=Object.keys(control.meshes).filter(name=>control.meshes[name]!==edited.meshes[name]);
assert.deepEqual(changed,[report.edited_mesh]);
let maxSiblingUvDelta=0;
for(const name of Object.keys(control.meshes).filter(n=>n!==report.edited_mesh)){
 assert.equal(control.uvs[name].length,edited.uvs[name].length);
 maxSiblingUvDelta=Math.max(maxSiblingUvDelta,...control.uvs[name].map((v,i)=>Math.abs(v-edited.uvs[name][i])));
}
assert.ok(maxSiblingUvDelta<=1e-7,'Unrelated UV changes exceed float evaluation tolerance');
assert.deepEqual(Object.keys(control.meshes).sort(),Object.keys(edited.meshes).sort());
const expected=structuredClone(control.materials);
const led=expected.find(m=>m.name==='Warm LED diffuser');assert.ok(led);
assert.notEqual(led.pbrMetallicRoughness.roughnessFactor,.71);
led.pbrMetallicRoughness.roughnessFactor=edited.materials.find(m=>m.name===led.name).pbrMetallicRoughness.roughnessFactor;
assert.ok(Math.abs(led.pbrMetallicRoughness.roughnessFactor-.71)<1e-6);
assert.deepEqual(expected,edited.materials,'Only the intended shared LED roughness may change');
for(const [file,sha]of Object.entries(report.original_asset_hashes))assert.equal(hash(fs.readFileSync(dir+file)),sha,file);
delete shipped.uvs;delete control.uvs;delete edited.uvs;
const metadata=JSON.parse(fs.readFileSync(dir+'metadata/'+dir.split('/').at(-2)+'.json'));
assert.equal(metadata.metrics.sha256,shipped.sha256);assert.equal(metadata.source_sha256,report.source_sha256);
fs.writeFileSync(dir+'reports/source-edit-verification.json',JSON.stringify({status:'PASS',shipped,control,edited,changed_meshes:changed,unchanged_sibling_meshes:41,max_sibling_uv_delta:maxSiblingUvDelta,uv_tolerance:1e-7,material_edit:'Only shared Warm LED diffuser roughness changes to 0.71',original_assets_unchanged:true},null,2)+'\n');
console.log('PASS saved source edit: one geometry part, 41 unchanged siblings, shared LED roughness, original assets unchanged');
