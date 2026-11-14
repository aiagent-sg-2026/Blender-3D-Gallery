import fs from 'node:fs';
import {validateBytes} from 'gltf-validator';
const here=new URL('./',import.meta.url);
const slugs=['mall-shopfront-fascia-210','mall-shopfront-fascia-120','mall-column-ceiling-collar'];
const reports=[];
for(const slug of slugs){
 const b=fs.readFileSync(new URL(`exports/${slug}.glb`,here));
 const doc=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)).toString());
 const validation=await validateBytes(new Uint8Array(b),{uri:`${slug}.glb`,maxIssues:50});
 let triangles=0; for(const m of doc.meshes??[])for(const p of m.primitives)triangles+=(doc.accessors[p.indices]?.count??0)/3;
 const external=[...(doc.buffers??[]),...(doc.images??[])].some(x=>x.uri);
 const pass=validation.issues.numErrors===0&&validation.issues.numWarnings===0&&b.length<50000&&triangles<300&&!external&&!(doc.animations?.length)&&!(doc.cameras?.length);
 reports.push({slug,bytes:b.length,triangles,meshes:doc.meshes.length,materials:doc.materials.length,external,issues:validation.issues,pass});
}
fs.writeFileSync(new URL('reports/glb-validation.json',here),JSON.stringify(reports,null,2)+'\n');
for(const r of reports)console.log(r.slug,r.bytes,r.triangles,'triangles',r.issues.numErrors,'errors',r.issues.numWarnings,'warnings',r.pass?'PASS':'FAIL');
if(reports.some(r=>!r.pass))process.exitCode=1;
