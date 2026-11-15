import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import validator from 'gltf-validator';
const root='models/fish-realism-release';
const manifest=JSON.parse(await fs.readFile(`${root}/releases.json`));
const motion=JSON.parse(await fs.readFile(`${root}/motion-verification.json`));
const hash=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const results=[];
for(const [slug,item] of Object.entries(manifest.models)){
 const bytes=await fs.readFile(`${root}/${slug}/model.glb`);
 assert.equal(hash(bytes),item.glb_sha256);assert.equal(hash(await fs.readFile(item.source)),item.source_sha256);
 assert.equal(motion.find(r=>r.slug===slug)?.sha256,item.glb_sha256);
 const report=await validator.validateBytes(new Uint8Array(bytes),{uri:`${slug}/model.glb`});
 assert.equal(report.issues.numErrors,0);assert.equal(report.issues.numWarnings,0);
 results.push({slug,sha256:item.glb_sha256,bytes:bytes.length,issues:report.issues});
}
const guard=JSON.parse(await fs.readFile('models/fish-realism-qa/preserved-models.json'));
for(const [file,expected]of Object.entries(guard))assert.equal(hash(await fs.readFile(file)),expected,file);
await fs.writeFile(`${root}/artifact-verification.json`,JSON.stringify({preserved_files:Object.keys(guard).length,results},null,2)+'\n');
console.log('PASS delivery assets, source binding, deformation receipt and preservation');
