import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

function pack(json, bin) {
  const text = Buffer.from(JSON.stringify(json)), padded = Buffer.alloc(Math.ceil(text.length/4)*4,32);text.copy(padded);
  const output = Buffer.alloc(28+padded.length+bin.length);
  output.writeUInt32LE(0x46546c67,0);output.writeUInt32LE(2,4);output.writeUInt32LE(output.length,8);
  output.writeUInt32LE(padded.length,12);output.writeUInt32LE(0x4e4f534a,16);padded.copy(output,20);
  output.writeUInt32LE(bin.length,20+padded.length);output.writeUInt32LE(0x004e4942,24+padded.length);bin.copy(output,28+padded.length);
  return output;
}
function fixture(indices, reverseNormals = false, xShift = 0, residuePoints = null) {
  const points = [0,0,0, 1,0,0, 0,1,0, 0,0,0, 0,0,0, 1,0,0,
    .1,.1,0, .11,.1,0, .105,.10000001,0, .2,.2,0, .20001,.2,0, .2,.20001,0];
  if (residuePoints) points.splice(18, 9, ...residuePoints.flat());
  const shift = Array.isArray(xShift) ? xShift : [xShift,0,0];
  const positions = Buffer.from(new Float32Array(points.map((v, i) => v + shift[i % 3])).buffer);
  const values = new Float32Array(positions.buffer,positions.byteOffset,points.length);
  const min = [0,1,2].map(axis => Math.min(...values.filter((_,i) => i % 3 === axis)));
  const max = [0,1,2].map(axis => Math.max(...values.filter((_,i) => i % 3 === axis)));
  const normals = Buffer.from(new Float32Array(Array.from({length:12}, () => [0,0,reverseNormals ? -1 : 1]).flat()).buffer);
  const indexData = Buffer.from(new Uint16Array(indices).buffer);
  const bin = Buffer.concat([positions, normals, indexData, Buffer.alloc((4 - indexData.length % 4) % 4)]);
  const json = {asset:{version:'2.0'},scene:0,scenes:[{nodes:[0]}],nodes:[{name:'ASSET_Fixture',mesh:0}],
    materials:[{name:'Fixture'}],meshes:[{primitives:[{attributes:{POSITION:0,NORMAL:1},indices:2,material:0}]}],
    buffers:[{byteLength:bin.length}],bufferViews:[{buffer:0,byteOffset:0,byteLength:positions.length,target:34962},
      {buffer:0,byteOffset:positions.length,byteLength:normals.length,target:34962},
      {buffer:0,byteOffset:positions.length+normals.length,byteLength:indexData.length,target:34963}],
    accessors:[{bufferView:0,componentType:5126,count:12,type:'VEC3',min,max},
      {bufferView:1,componentType:5126,count:12,type:'VEC3'},
      {bufferView:2,componentType:5123,count:indices.length,type:'SCALAR',min:[Math.min(...indices)],max:[Math.max(...indices)]}]};
  return pack(json,bin);
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
  const shifted = path.join(dir,'submicrometre-shift.glb');
  await fs.writeFile(shifted,fixture([0,1,2,9,10,11],false,7.5e-7));
  const tolerance = run('scripts/check-degenerate-repair.mjs',[before,shifted,path.join(dir,'shifted.json')]);
  assert.equal(tolerance.status,0,'Coordinates within 1 micrometre must match even across quantization boundaries: '+tolerance.stderr);
  const diagonalBefore = path.join(dir,'diagonal-before.glb'), diagonalAfter = path.join(dir,'diagonal-after.glb');
  await fs.writeFile(diagonalBefore,fixture(Array.from({length:12},(_,i)=>i),false,[-4.9e-7,-4.9e-7,0]));
  await fs.writeFile(diagonalAfter,fixture([0,1,2,9,10,11],false,[4.9e-7,4.9e-7,0]));
  const displacement = run('scripts/check-degenerate-repair.mjs',[diagonalBefore,diagonalAfter,path.join(dir,'too-far.json')]);
  assert.notEqual(displacement.status,0,'A shared quantization cell must not excuse Euclidean displacement above 1 micrometre');
  assert.match(displacement.stderr,/displacement exceeds tolerance|surfaces added/);
});

test('shared index accessors are repaired once when every instance has the same cleanup mask', async context => {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(),'glb-shared-index-test-'));
  context.after(() => fs.rm(dir,{recursive:true,force:true}));
  const duplicate = bytes => {
    const json = JSON.parse(bytes.toString('utf8',20,20+bytes.readUInt32LE(12)));
    json.nodes.push({name:'FixtureCopy',mesh:0}); json.scenes[0].nodes.push(1);
    return pack(json,bytes.subarray(28+bytes.readUInt32LE(12)));
  };
  const before = path.join(dir,'before.glb'), clean = path.join(dir,'clean.glb'), comparison = path.join(dir,'comparison.json');
  await fs.writeFile(before,duplicate(fixture(Array.from({length:12},(_,i)=>i))));
  await fs.writeFile(clean,duplicate(fixture([0,1,2,9,10,11])));
  const compare = run('scripts/check-degenerate-repair.mjs',[before,clean,comparison]);assert.equal(compare.status,0,compare.stderr);
  const repaired = path.join(dir,'repaired.glb'), evidence = path.join(dir,'repair.json');
  const repair = run('scripts/repair-glb-degenerates.mjs',[before,repaired,evidence,comparison]);
  assert.equal(repair.status,0,repair.stderr);
  const receipt = JSON.parse(await fs.readFile(evidence));
  assert.equal(receipt.zeroRemoved,2); assert.equal(receipt.residueRemoved,2);
  const actual = run('scripts/check-degenerate-repair.mjs',[before,repaired,path.join(dir,'actual.json')]);
  assert.equal(actual.status,0,actual.stderr);
});

test('shared indices with different per-mesh cleanup masks are rejected without writing output', async context => {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(),'glb-shared-mask-test-'));
  context.after(() => fs.rm(dir,{recursive:true,force:true}));
  const all = Array.from({length:12},(_,i)=>i);
  const shared = clean => {
    const bytes=fixture(clean?[0,1,2,6,7,8,9,10,11]:all);
    const json=JSON.parse(bytes.toString('utf8',20,20+bytes.readUInt32LE(12)));
    let bin=Buffer.from(bytes.subarray(28+bytes.readUInt32LE(12)));
    const positions=Buffer.from(bin.subarray(0,144));
    // Indices 3/4/5 collapse in the first mesh but form a real face here.
    positions.writeFloatLE(.1,4*3*4);positions.writeFloatLE(.1,(5*3+1)*4);
    const view=json.bufferViews.length;json.bufferViews.push({buffer:0,byteOffset:bin.length,byteLength:144,target:34962});
    const accessor=json.accessors.length;json.accessors.push({bufferView:view,componentType:5126,count:12,type:'VEC3',min:[0,0,0],max:[1,1,0]});
    bin=Buffer.concat([bin,positions]);
    const primitive={attributes:{POSITION:accessor,NORMAL:1},indices:2,material:0};
    if(clean){
      const indexData=Buffer.from(new Uint16Array(all).buffer),indexView=json.bufferViews.length;
      json.bufferViews.push({buffer:0,byteOffset:bin.length,byteLength:indexData.length,target:34963});
      primitive.indices=json.accessors.length;json.accessors.push({bufferView:indexView,componentType:5123,count:12,type:'SCALAR',min:[0],max:[11]});
      bin=Buffer.concat([bin,indexData]);
    }
    json.meshes.push({primitives:[primitive]});json.nodes.push({name:'DifferentMesh',mesh:1});json.scenes[0].nodes.push(1);
    json.buffers[0].byteLength=bin.length;return pack(json,bin);
  };
  const before=path.join(dir,'before.glb'),clean=path.join(dir,'clean.glb'),comparison=path.join(dir,'comparison.json');
  await fs.writeFile(before,shared(false));await fs.writeFile(clean,shared(true));
  const check=run('scripts/check-degenerate-repair.mjs',[before,clean,comparison]);assert.equal(check.status,0,check.stderr);
  const output=path.join(dir,'must-not-exist.glb');
  const repair=run('scripts/repair-glb-degenerates.mjs',[before,output,path.join(dir,'receipt.json'),comparison]);
  assert.notEqual(repair.status,0);assert.match(repair.stderr,/Shared index accessor requires identical retained indices/);
  await assert.rejects(fs.access(output),{code:'ENOENT'});
  const split=path.join(dir,'split.glb'),splitReceipt=path.join(dir,'split.json');
  const allowed=run('scripts/repair-glb-degenerates.mjs',[before,split,splitReceipt,comparison,'--split-shared-indices']);
  assert.equal(allowed.status,0,allowed.stderr);
  assert.equal(JSON.parse(await fs.readFile(splitReceipt)).splitIndexAccessors.length,1);
  const verified=run('scripts/check-degenerate-repair.mjs',[before,split,path.join(dir,'split-comparison.json')]);
  assert.equal(verified.status,0,verified.stderr);
  const oldBytes=await fs.readFile(before),newBytes=await fs.readFile(split);
  assert.deepEqual(newBytes.subarray(28+newBytes.readUInt32LE(12),28+newBytes.readUInt32LE(12)+144),oldBytes.subarray(28+oldBytes.readUInt32LE(12),28+oldBytes.readUInt32LE(12)+144));
});

test('reviewed radial-line calibration preserves defaults and rejects a real one-nanometre face', async context => {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), 'glb-line-precision-test-'));
  context.after(() => fs.rm(dir, { recursive: true, force: true }));
  // Frozen real Blender 5.2.3 radial-pole residue: grid rounding makes this
  // mathematically radial triplet non-collinear at 1 um; actual error is 0.064 nm.
  const radial = [[4.888098718814468e-19, .054999999701976776, -3.2038291630744244e-20],
    [-.007931559346616268, .054999999701976776, .0010442095808684826],
    [.3093307912349701, .054999999701976776, -.040724173188209534]];
  const before = path.join(dir, 'before.glb'), control = path.join(dir, 'control.glb');
  const removed = path.join(dir, 'removed.glb'), evidence = path.join(dir, 'control.json');
  await fs.writeFile(before, fixture(Array.from({ length: 12 }, (_, i) => i), false, 0, radial));
  await fs.writeFile(control, fixture([0,1,2,6,7,8,9,10,11], false, 0, radial));
  await fs.writeFile(removed, fixture([0,1,2,9,10,11], false, 0, radial));
  const strict = run('scripts/check-degenerate-repair.mjs', [before, removed, path.join(dir, 'strict.json')]);
  assert.notEqual(strict.status, 0, 'Default checks must still reject non-grid-collinear deletion');
  const flag = '--precision-line-tolerance-m=2e-10';
  const check = run('scripts/check-degenerate-repair.mjs', [before, control, evidence, flag]);
  assert.equal(check.status, 0, check.stderr);
  const report = JSON.parse(await fs.readFile(evidence));
  assert.equal(report.linePrecisionResidues.length, 1);
  assert.equal(report.linePrecisionResidues[0].quantizedCollinear, false);
  const output = path.join(dir, 'repaired.glb');
  const denied = run('scripts/repair-glb-degenerates.mjs', [before, output, path.join(dir, 'denied.json'), evidence]);
  assert.notEqual(denied.status, 0);
  await assert.rejects(fs.access(output), { code: 'ENOENT' });
  const repair = run('scripts/repair-glb-degenerates.mjs', [before, output, path.join(dir, 'repair.json'), evidence, flag]);
  assert.equal(repair.status, 0, repair.stderr);
  const actual = run('scripts/check-degenerate-repair.mjs', [before, output, path.join(dir, 'actual.json'), flag]);
  assert.equal(actual.status, 0, actual.stderr);
  assert.equal(JSON.parse(await fs.readFile(path.join(dir, 'actual.json'))).after.triangles, 2,
    'The ordinary face and genuine 10 um face must remain');
  const real = radial.map(p => [p[0], p[2], 0]);
  real[1][2] = 1e-9;
  const tinyBefore = path.join(dir, 'real-tiny-before.glb'), tinyRemoved = path.join(dir, 'real-tiny-removed.glb');
  await fs.writeFile(tinyBefore, fixture(Array.from({ length: 12 }, (_, i) => i), false, 0, real));
  await fs.writeFile(tinyRemoved, fixture([0,1,2,9,10,11], false, 0, real));
  const reject = run('scripts/check-degenerate-repair.mjs', [tinyBefore, tinyRemoved, path.join(dir, 'tiny-fail.json'), flag]);
  assert.notEqual(reject.status, 0, 'A real 1 nm face exceeds the calibrated 0.2 nm line error and must not disappear');
  assert.match(reject.stderr, /Meaningful original surfaces removed/);
});

test('equivalent texture aliases compare semantically while pixel and material changes are rejected', async context => {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), 'glb-material-alias-test-'));
  context.after(() => fs.rm(dir, { recursive: true, force: true }));
  const white = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVR4nGP4DwQACfsD/fteaysAAAAASUVORK5CYII=', 'base64');
  const black = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGNgYGD4DwABBAEAX+XDSwAAAABJRU5ErkJggg==', 'base64');
  const textured = (clean, changedPixels = false, distinctNames = false) => {
    const b = fixture(clean ? [0,1,2,9,10,11] : Array.from({ length: 12 }, (_, i) => i));
    const j = JSON.parse(b.toString('utf8', 20, 20 + b.readUInt32LE(12)));
    let bin = Buffer.from(b.subarray(28 + b.readUInt32LE(12)));
    const image = changedPixels ? black : white, imageView = j.bufferViews.length;
    j.bufferViews.push({ buffer: 0, byteOffset: bin.length, byteLength: image.length });
    bin = Buffer.concat([bin, image, Buffer.alloc((4 - image.length % 4) % 4)]);
    const uv = Buffer.alloc(12 * 2 * 4), uvView = j.bufferViews.length;
    j.bufferViews.push({ buffer: 0, byteOffset: bin.length, byteLength: uv.length, target: 34962 });
    const uvAccessor = j.accessors.length;
    j.accessors.push({ bufferView: uvView, componentType: 5126, count: 12, type: 'VEC2' });
    bin = Buffer.concat([bin, uv]);j.buffers[0].byteLength = bin.length;
    j.images = [{ bufferView: imageView, mimeType: 'image/png', name: 'FixturePixel' }];
    j.samplers = [{ magFilter: 9729, minFilter: 9987 }];
    j.textures = [{ source: 0, sampler: 0 }];
    j.materials = [{ name: 'Fixture', pbrMetallicRoughness: { baseColorTexture: { index: 0 }, roughnessFactor: .5 } }];
    j.meshes[0].primitives[0].attributes.TEXCOORD_0 = uvAccessor;
    j.meshes.push(structuredClone(j.meshes[0]));
    j.nodes.push({ name: 'TextureAliasInstance', mesh: 1, translation: [2,0,0] });j.scenes[0].nodes.push(1);
    if (!clean) {
      j.textures.push({ source: 0, sampler: 0 });
      j.materials.push({ name: 'Fixture', pbrMetallicRoughness: { baseColorTexture: { index: 1 }, roughnessFactor: distinctNames ? .7 : .5 } });
      j.meshes[1].primitives[0].material = 1;
    }
    return pack(j, bin);
  };
  const before = path.join(dir, 'before.glb'), control = path.join(dir, 'control.glb');
  const comparison = path.join(dir, 'comparison.json');
  await fs.writeFile(before, textured(false));await fs.writeFile(control, textured(true));
  const good = run('scripts/check-degenerate-repair.mjs', [before, control, comparison]);
  assert.equal(good.status, 0, good.stderr);
  const repaired = path.join(dir, 'repaired.glb');
  const repair = run('scripts/repair-glb-degenerates.mjs', [before, repaired, path.join(dir, 'index.json'), comparison]);
  assert.equal(repair.status, 0, repair.stderr);
  const actual = run('scripts/check-degenerate-repair.mjs', [before, repaired, path.join(dir, 'actual.json')]);
  assert.equal(actual.status, 0, actual.stderr);
  const changed = path.join(dir, 'changed-pixels.glb');await fs.writeFile(changed, textured(true, true));
  const pixels = run('scripts/check-degenerate-repair.mjs', [before, changed, path.join(dir, 'pixels.json')]);
  assert.notEqual(pixels.status, 0);assert.match(pixels.stderr, /embedded texture payloads changed/);
  const ambiguous = path.join(dir, 'distinct-same-name.glb');await fs.writeFile(ambiguous, textured(false, false, true));
  const names = run('scripts/check-degenerate-repair.mjs', [ambiguous, control, path.join(dir, 'names.json')]);
  assert.notEqual(names.status, 0);assert.match(names.stderr, /Distinct same-name materials/);
});

test('rigid-container opt-in preserves clips and refuses animated meshes or ancestors', async context => {
  const dir=await fs.mkdtemp(path.join(os.tmpdir(),'glb-rigid-static-'));
  context.after(()=>fs.rm(dir,{recursive:true,force:true}));
  const animated=(indices,mode='sibling',end=1)=>{
    const bytes=fixture(indices),json=JSON.parse(bytes.subarray(20,20+bytes.readUInt32LE(12)));
    const binary=bytes.subarray(28+bytes.readUInt32LE(12));
    const time=Buffer.from(new Float32Array([0,1]).buffer),value=Buffer.from(new Float32Array([0,0,0,end,0,0]).buffer);
    const input=json.accessors.length,output=input+1,view=json.bufferViews.length;
    json.bufferViews.push({buffer:0,byteOffset:binary.length,byteLength:time.length},{buffer:0,byteOffset:binary.length+time.length,byteLength:value.length});
    json.accessors.push({bufferView:view,componentType:5126,count:2,type:'SCALAR',min:[0],max:[1]},
      {bufferView:view+1,componentType:5126,count:2,type:'VEC3'});
    json.nodes.push({name:'MovingSibling'});json.scenes[0].nodes.push(1);
    if(mode==='ancestor'){json.nodes[1].children=[0];json.scenes[0].nodes=[1];}
    json.animations=[{name:'Move',channels:[{sampler:0,target:{node:mode==='self'?0:1,path:'translation'}}],samplers:[{input,output,interpolation:'LINEAR'}]}];
    const bin=Buffer.concat([binary,time,value]);json.buffers[0].byteLength=bin.length;
    return pack(json,bin);
  };
  const flag='--static-meshes-in-rigid-container';
  for(const mode of ['sibling','self','ancestor']){
    const before=path.join(dir,mode+'-before.glb'),clean=path.join(dir,mode+'-source.glb'),comparison=path.join(dir,mode+'-comparison.json'),output=path.join(dir,mode+'-output.glb');
    await fs.writeFile(before,animated(Array.from({length:12},(_,i)=>i),mode));
    await fs.writeFile(clean,animated([0,1,2,9,10,11],mode));
    const rejectedDefault=run('scripts/check-degenerate-repair.mjs',[before,clean,comparison]);
    assert.notEqual(rejectedDefault.status,0,'Animated assets remain rejected without explicit scope');
    const source=run('scripts/check-degenerate-repair.mjs',[before,clean,comparison,flag,'--allow-normal-drift']);
    assert.equal(source.status,0,source.stderr);
    const repair=run('scripts/repair-glb-degenerates.mjs',[before,output,path.join(dir,mode+'-repair.json'),comparison,flag]);
    if(mode!=='sibling'){
      assert.notEqual(repair.status,0);assert.match(repair.stderr,/mesh or ancestor is animated/);
      await assert.rejects(fs.stat(output));continue;
    }
    assert.equal(repair.status,0,repair.stderr);
    const delivery=run('scripts/check-degenerate-repair.mjs',[before,output,path.join(dir,'delivery.json'),flag]);
    assert.equal(delivery.status,0,delivery.stderr);
    const changedClip=path.join(dir,'changed-clip.glb');await fs.writeFile(changedClip,animated([0,1,2,9,10,11],mode,1.001));
    const drift=run('scripts/check-degenerate-repair.mjs',[before,changedClip,path.join(dir,'bad-clip.json'),flag,'--allow-normal-drift']);
    assert.notEqual(drift.status,0);assert.match(drift.stderr,/animation drift/);
  }
  const {rigidScope}=await import('../scripts/rigid-container-qa.mjs');
  const json=JSON.parse(animated([0,1,2]).subarray(20,20+animated([0,1,2]).readUInt32LE(12)));
  assert.throws(()=>rigidScope({...json,skins:[{}]}),/Skinned/);
  const morph=structuredClone(json);morph.meshes[0].primitives[0].targets=[{POSITION:0}];
  assert.throws(()=>rigidScope(morph),/Morph/);
});

test('analytic line scope preserves an identical tiny face on an unreviewed node', async context => {
 const dir=await fs.mkdtemp(path.join(os.tmpdir(),'glb-line-node-scope-'));
 context.after(()=>fs.rm(dir,{recursive:true,force:true}));
 const radial=[[4.888098718814468e-19,.054999999701976776,-3.2038291630744244e-20],[-.007931559346616268,.054999999701976776,.0010442095808684826],[.3093307912349701,.054999999701976776,-.040724173188209534]];
 function twoNodes(clean){
  const indices=clean?[0,1,2,6,7,8,9,10,11]:Array.from({length:12},(_,i)=>i);
  const b=fixture(indices,false,0,radial),j=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)));
  const bin=b.subarray(28+b.readUInt32LE(12)),copy=Buffer.from(new Uint16Array(indices).buffer);
  j.bufferViews.push({buffer:0,byteOffset:bin.length,byteLength:copy.length,target:34963});
  j.accessors.push({...j.accessors[2],bufferView:3});
  j.meshes.push({primitives:[{...j.meshes[0].primitives[0],indices:3}]});
  j.nodes.push({name:'ProtectedTiny',mesh:1});j.scenes[0].nodes.push(1);
  const binary=Buffer.concat([bin,copy,Buffer.alloc((4-copy.length%4)%4)]);j.buffers[0].byteLength=binary.length;
  return pack(j,binary);
 }
 const before=path.join(dir,'before.glb'),native=path.join(dir,'native.glb'),comparison=path.join(dir,'comparison.json'),output=path.join(dir,'output.glb');
 await fs.writeFile(before,twoNodes(false));await fs.writeFile(native,twoNodes(true));
 const flags=['--precision-line-tolerance-m=2e-10','--precision-line-nodes=ASSET_Fixture'];
 const check=run('scripts/check-degenerate-repair.mjs',[before,native,comparison,...flags]);assert.equal(check.status,0,check.stderr);
 const missingScope=run('scripts/repair-glb-degenerates.mjs',[before,output,path.join(dir,'denied.json'),comparison,flags[0]]);assert.notEqual(missingScope.status,0);
 const repair=run('scripts/repair-glb-degenerates.mjs',[before,output,path.join(dir,'repair.json'),comparison,...flags]);assert.equal(repair.status,0,repair.stderr);
 const {readGlb}=await import('../scripts/node-glb-structure.mjs');const glb=await readGlb(output);
 assert.equal(glb.scene.getObjectByName('ASSET_Fixture').geometry.index.count/3,2);
 assert.equal(glb.scene.getObjectByName('ProtectedTiny').geometry.index.count/3,3,'The unreviewed identical tiny face must remain');
});
