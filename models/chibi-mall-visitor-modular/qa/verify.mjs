import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import validator from 'gltf-validator';
import {inspectHairAtlas} from './hair-atlas.mjs';

const [folder,...variants]=process.argv.slice(2);
const names='idle walk run talk browse sit wave pick_up inspect point nod cheer'.split(' ');
const faces='default happy wink surprised thinking excited'.split(' ');
const expectedSlots='Head Eyes Mouth Hair Body Hands Shirt Jeans Shoes Backpack Watch'.split(' ');
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const members=(a,b)=>same([...a].sort(),[...b].sort());
const hash=data=>createHash('sha256').update(data).digest('hex');

async function inspect(file){
  const glb=await fs.readFile(file);
  if(glb.readUInt32LE(0)!==0x46546c67||glb.readUInt32LE(4)!==2)throw Error('Invalid GLB header');
  const len=glb.readUInt32LE(12),j=JSON.parse(glb.subarray(20,20+len));
  const data=glb.subarray(28+len);
  const readFloats=index=>{
    const a=j.accessors[index],view=j.bufferViews[a.bufferView];
    if(a.type!=='VEC4'||a.componentType!==5126)throw Error('Expected floating point skin weights');
    const result=[];const base=(view.byteOffset||0)+(a.byteOffset||0);
    for(let i=0;i<a.count;i++)result.push(Array.from({length:4},(_,k)=>data.readFloatLE(base+i*(view.byteStride||16)+4*k)));
    return result;
  };
  const nodes=j.nodes.filter(n=>n.mesh!==undefined);
  const scene=j.scenes[j.scene||0],skin=j.skins[0];
  const validation=await validator.validateBytes(new Uint8Array(glb),{maxIssues:100});
  const parts={},morphs={},meshHashes={},bounds=[Infinity,-Infinity];let primitives=0,storedVertices=0,maxWeightError=0,maxInfluences=0;
  const digest=createHash('sha256');
  for(const n of [...nodes].sort((a,b)=>a.name.localeCompare(b.name))){
    const m=j.meshes[n.mesh];let tri=0;const piece=createHash('sha256');
    for(const p of m.primitives){
      if((p.mode??4)!==4||p.indices===undefined)throw Error('Expected indexed triangles in '+m.name);
      const positions=j.accessors[p.attributes.POSITION];
      bounds[0]=Math.min(bounds[0],positions.min[1]);bounds[1]=Math.max(bounds[1],positions.max[1]);
      tri+=j.accessors[p.indices].count/3;storedVertices+=positions.count;primitives++;
      for(const w of readFloats(p.attributes.WEIGHTS_0)){
        maxWeightError=Math.max(maxWeightError,Math.abs(1-w.reduce((a,b)=>a+b,0)));
        maxInfluences=Math.max(maxInfluences,w.filter(k=>k>0).length);
      }
      // Stronger replay evidence where encodings coincide; counts and names are checked independently.
      for(const a of [p.indices,p.attributes.POSITION,p.attributes.NORMAL,p.attributes.TEXCOORD_0,p.attributes.JOINTS_0,p.attributes.WEIGHTS_0,...(p.targets||[]).map(t=>t.POSITION)]){
        const access=j.accessors[a];
        digest.update(JSON.stringify([access.type,access.componentType,access.count,access.sparse?.count??0]));
        for(const block of [access,access.sparse?.indices,access.sparse?.values]){
          if(block?.bufferView===undefined)continue;
          const view=j.bufferViews[block.bufferView];
          const region=data.subarray(view.byteOffset||0,(view.byteOffset||0)+view.byteLength);
          digest.update(region);piece.update(region);
        }
      }
    }
    meshHashes[n.name]=piece.digest('hex');
    parts[n.name]={slot:n.extras?.partSlot,triangles:tri};
    if(m.extras?.targetNames)morphs[n.name]=m.extras.targetNames;
  }
  const triangles=Object.values(parts).reduce((s,p)=>s+p.triangles,0);
  const materials=j.materials.map(m=>m.name).sort(), clips=j.animations.map(a=>a.name).sort();
  const channels=j.animations.reduce((obj,a)=>({...obj,[a.name]:a.channels.length}),{});
  const img=j.images[0],imageView=j.bufferViews[img.bufferView],imgStart=imageView.byteOffset||0;
  const width=data.readUInt32BE(imgStart+16),height=data.readUInt32BE(imgStart+20);
  const joints=skin.joints.map(i=>j.nodes[i].name);
  const onlyCharacter=j.nodes.every(n=>n.mesh!==undefined||n.skin!==undefined||n.name==='Visitor_Rig'||joints.includes(n.name)||n.name.startsWith('Socket_'));
  const keys=new Set(Object.values(morphs).flat());
  const textures=j.images.map(image=>{
    const view=j.bufferViews[image.bufferView];
    const start=view?.byteOffset||0;
    return {name:image.name,embedded:!image.uri&&view!==undefined,mimeType:image.mimeType,
      width:view?data.readUInt32BE(start+16):0,height:view?data.readUInt32BE(start+20):0};
  });
  const colorSources=new Set(j.materials.map(m=>j.textures[m.pbrMetallicRoughness.baseColorTexture.index].source));
  const mapped=j.materials.filter(m=>m.normalTexture!==undefined);
  const normalSources=new Set(mapped.map(m=>j.textures[m.normalTexture.index].source));
  const expectsNormals=scene.extras.surfaceMaps?.includes('normal')||mapped.length>0;
  const normalContract=expectsNormals
    ? mapped.length===j.materials.length&&normalSources.size===1&&[...normalSources].every(i=>!colorSources.has(i))
    : mapped.length===0;
  const resourceContract=textures.length===(expectsNormals?2:1)&&colorSources.size===1&&normalContract
    &&j.buffers.every(b=>!b.uri)&&textures.every(i=>i.embedded&&i.mimeType==='image/png'&&i.width===1024&&i.height===1024);
  const hairAtlas=expectsNormals?inspectHairAtlas(j,data):null;
  const checks={validator:validation.issues.numErrors===0&&validation.issues.numWarnings===0,
    triangles:triangles>=3000&&triangles<=8000,dimensions:Math.abs(bounds[1]-bounds[0]-1.30)<=.01&&Math.abs(bounds[0])<=.002,
    resources:resourceContract,hairUv:hairAtlas===null||hairAtlas.pass,
    characterNodes:onlyCharacter&&!(j.cameras?.length)&&!j.extensionsRequired?.length,
    skeleton:j.skins.length===1&&joints.length===20&&nodes.every(n=>n.skin===0),
    weights:maxWeightError<1e-4&&maxInfluences<=4&&maxInfluences>1,
    slots:members(new Set(Object.values(parts).map(p=>p.slot)),expectedSlots),
    faces:members(Object.keys(scene.extras.expressionPresets),faces)&&Object.values(scene.extras.expressionPresets).every(p=>Object.keys(p).every(k=>keys.has(k))),
    clips:members(clips,names)&&members(Object.keys(scene.extras.clipInfo),names)&&Object.values(channels).every(c=>c>0)};
  return {sha256:hash(glb),geometrySha256:digest.digest('hex'),bytes:glb.length,triangles,primitives,storedVertices,boundsYM:bounds,
    parts,meshHashes,morphs,joints,materials,clips,channels,maxInfluences,maxWeightError,texture:[width,height],textures,hairAtlas,checks,
    validator:{version:validation.validatorVersion,errors:validation.issues.numErrors,warnings:validation.issues.numWarnings,
      infos:validation.issues.numInfos,messages:validation.issues.messages}};
}
const main=await inspect(path.join(folder,'visitor.glb')),replays={};
for(const v of variants){
  const run=await inspect(v),id=path.basename(path.dirname(v));
  const contractKeys=['triangles','primitives','parts','storedVertices','materials','morphs','joints','clips','channels','texture','textures'];
  const stable=contractKeys.every(k=>same(main[k],run[k]))&&main.boundsYM.every((x,i)=>Math.abs(x-run.boundsYM[i])<1e-5);
  if(id==='edited-guide'){
    const changed=Object.keys(main.meshHashes).filter(n=>main.meshHashes[n]!==run.meshHashes[n]);
    replays[id]={changed,interfaceMatches:stable,validator:run.validator,pass:stable&&same(changed,['Swept_hair'])&&Object.values(run.checks).every(Boolean)};
    continue;
  }
  replays[id]={sha256:run.sha256,identicalBytes:main.sha256===run.sha256,identicalGeometry:main.geometrySha256===run.geometrySha256,
    interfaceMatches:stable,validator:run.validator,pass:stable&&Object.values(run.checks).every(Boolean)};
}
const pass=Object.values(main.checks).every(Boolean)&&Object.values(replays).every(r=>r.pass);
await fs.mkdir(path.join(folder,'qa'),{recursive:true});
await fs.writeFile(path.join(folder,'qa','geometry.json'),JSON.stringify({...main,replays,pass},null,2)+'\n');
console.log(JSON.stringify({triangles:main.triangles,checks:main.checks,replays,pass}));
if(!pass)process.exitCode=1;

