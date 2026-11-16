import fs from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import validator from 'gltf-validator';
import { validateMetadata } from '../../../scripts/catalog.mjs';
const project = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const meta = JSON.parse(fs.readFileSync(path.join(project,'metadata.json')));
validateMetadata(meta, 'chibi-visitor-v2');
const native=path.join(project,'exports/chibi-visitor-v2.glb');
const candidates=[native,...process.argv.slice(2)];
for (const file of candidates) {
  const raw=fs.readFileSync(file);
  const json=JSON.parse(raw.subarray(20,20+raw.readUInt32LE(12)).toString('utf8'));
  const result=await validator.validateBytes(new Uint8Array(raw),{uri:path.basename(file),maxIssues:250});
  const {numErrors,numWarnings}=result.issues;
  const root=(json.scenes[json.scene||0].nodes||[]).map(index=>json.nodes[index].name);
  const triangles=(json.meshes||[]).reduce((sum,mesh)=>sum+mesh.primitives.reduce((v,p)=>v+json.accessors[p.indices??p.attributes.POSITION].count/3,0),0);
  const report={file:path.basename(file),bytes:raw.length,sha256:createHash('sha256').update(raw).digest('hex'),errors:numErrors,warnings:numWarnings,meshes:json.meshes?.length,materials:json.materials?.length,triangles,roots:root,animations:json.animations?.length||0};
  console.log('CHIBI_V2_KHRONOS_QA='+JSON.stringify(report));
  if(numErrors || numWarnings || raw.length>5*1024*1024 || triangles>40000 || (json.meshes?.length||0)>25 || (json.materials?.length||0)>20 || root.length!==1)process.exitCode=1;
  if(file===native && (root[0]!=='GJH_Chibi_Visitor_V2'||report.sha256!==meta.metrics.glb_sha256||report.triangles!==meta.metrics.triangles))process.exitCode=1;
}
const source=fs.readFileSync(path.join(project,'chibi-visitor-v2.blend'));
if(createHash('sha256').update(source).digest('hex')!==meta.metrics.source_sha256)process.exitCode=1;
if(!process.exitCode)console.log('CHIBI_V2_KHRONOS_PASS');
