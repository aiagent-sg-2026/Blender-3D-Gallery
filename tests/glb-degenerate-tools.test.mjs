import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

function fixture(indices, reverseNormals = false) {
  const points = [0,0,0, 1,0,0, 0,1,0, 0,0,0, 0,0,0, 1,0,0,
    .1,.1,0, .11,.1,0, .105,.10000001,0, .2,.2,0, .20001,.2,0, .2,.20001,0];
  const positions = Buffer.from(new Float32Array(points).buffer);
  const normals = Buffer.from(new Float32Array(Array.from({length:12}, () => [0,0,reverseNormals ? -1 : 1]).flat()).buffer);
  const indexData = Buffer.from(new Uint16Array(indices).buffer);
  const bin = Buffer.concat([positions, normals, indexData, Buffer.alloc((4 - indexData.length % 4) % 4)]);
  const json = {asset:{version:'2.0'},scene:0,scenes:[{nodes:[0]}],nodes:[{name:'ASSET_Fixture',mesh:0}],
    materials:[{name:'Fixture'}],meshes:[{primitives:[{attributes:{POSITION:0,NORMAL:1},indices:2,material:0}]}],
    buffers:[{byteLength:bin.length}],bufferViews:[{buffer:0,byteOffset:0,byteLength:positions.length,target:34962},
      {buffer:0,byteOffset:positions.length,byteLength:normals.length,target:34962},
      {buffer:0,byteOffset:positions.length+normals.length,byteLength:indexData.length,target:34963}],
    accessors:[{bufferView:0,componentType:5126,count:12,type:'VEC3',min:[0,0,0],max:[1,1,0]},
      {bufferView:1,componentType:5126,count:12,type:'VEC3'},
      {bufferView:2,componentType:5123,count:indices.length,type:'SCALAR',min:[Math.min(...indices)],max:[Math.max(...indices)]}]};
  const text = Buffer.from(JSON.stringify(json)), padded = Buffer.alloc(Math.ceil(text.length/4)*4,32);text.copy(padded);
  const output = Buffer.alloc(28+padded.length+bin.length);
  output.writeUInt32LE(0x46546c67,0);output.writeUInt32LE(2,4);output.writeUInt32LE(output.length,8);
  output.writeUInt32LE(padded.length,12);output.writeUInt32LE(0x4e4f534a,16);padded.copy(output,20);
  output.writeUInt32LE(bin.length,20+padded.length);output.writeUInt32LE(0x004e4942,24+padded.length);bin.copy(output,28+padded.length);
  return output;
}
const run = (script, args) => spawnSync(process.execPath, [script, ...args], {encoding:'utf8'});
test('GLB cleanup retains real tiny geometry and normals while removing reviewed collapse', async context => {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(),'glb-cleanup-test-'));
  context.after(() => fs.rm(dir,{recursive:true,force:true}));
  const before = path.join(dir,'before.glb'), clean = path.join(dir,'clean.glb'), report = path.join(dir,'comparison.json');
  await fs.writeFile(before,fixture(Array.from({length:12},(_,i)=>i)));
  await fs.writeFile(clean,fixture([0,1,2,9,10,11]));
  const valid = run('scripts/check-degenerate-repair.mjs',[before,clean,report]);
  assert.equal(valid.status,0,valid.stderr);
  const receipt = JSON.parse(await fs.readFile(report));
  assert.equal(receipt.removedPositiveAreaResidues.length,1);
  assert.ok(receipt.removedPositiveAreaResidues[0].altitude < 1e-7);
  const repaired = path.join(dir,'repaired.glb');
  const repair = run('scripts/repair-glb-degenerates.mjs',[before,repaired,path.join(dir,'repair.json'),report]);
  assert.equal(repair.status,0,repair.stderr);
  const compare = run('scripts/check-degenerate-repair.mjs',[before,repaired,path.join(dir,'delivered.json')]);
  assert.equal(compare.status,0,compare.stderr);
  const original = await fs.readFile(before), delivered = await fs.readFile(repaired);
  const originalBin = 28+original.readUInt32LE(12), deliveredBin = 28+delivered.readUInt32LE(12);
  assert.deepEqual(delivered.subarray(deliveredBin,deliveredBin+288),original.subarray(originalBin,originalBin+288),
    'Position and normal attribute bytes must remain identical');
  const missingRealFace = path.join(dir,'missing-real-face.glb');
  await fs.writeFile(missingRealFace,fixture([0,1,2]));
  const removed = run('scripts/check-degenerate-repair.mjs',[before,missingRealFace,path.join(dir,'bad-area.json')]);
  assert.notEqual(removed.status,0,'A genuine 10-micrometre face must not be excused by its tiny area');
  assert.match(removed.stderr,/Meaningful original surfaces removed/);
  const badNormals = path.join(dir,'bad-normals.glb');
  await fs.writeFile(badNormals,fixture([0,1,2,9,10,11],true));
  const normals = run('scripts/check-degenerate-repair.mjs',[before,badNormals,path.join(dir,'bad-normals.json')]);
  assert.notEqual(normals.status,0);
  assert.match(normals.stderr,/shading normals must be preserved/);
});
