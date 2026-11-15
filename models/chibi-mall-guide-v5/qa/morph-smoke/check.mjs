import fs from 'node:fs';
const root=process.cwd(); // run from the repository root
const THREE = await import(root+'/node_modules/three/build/three.module.js');
const { GLTFLoader } = await import(root+'/node_modules/three/examples/jsm/loaders/GLTFLoader.js');
const validator = await import(root+'/node_modules/gltf-validator/index.js');
const buf = fs.readFileSync(process.argv[2]);
const ab = buf.buffer.slice(buf.byteOffset, buf.byteOffset+buf.byteLength);
const v = await validator.default.validateBytes(new Uint8Array(buf));
console.log('validator', JSON.stringify(v.issues.numErrors), JSON.stringify(v.issues.numWarnings), JSON.stringify(v.issues.messages.slice(0,5).map(m=>m.code)));
const gltf = await new GLTFLoader().parseAsync(ab, '');
let mesh; gltf.scene.traverse(o=>{ if(o.isMesh||o.isSkinnedMesh) mesh=o; });
console.log('type', mesh.type, 'dict', JSON.stringify(mesh.morphTargetDictionary), 'infl', mesh.morphTargetInfluences?.length);
const pos = mesh.geometry.attributes.position;
const base = Float32Array.from(pos.array);
console.log('morphAttrs', Object.keys(mesh.geometry.morphAttributes), mesh.geometry.morphAttributes.position?.length);
// effect check: morphed position computed by three's rule (relative targets)
mesh.morphTargetInfluences[mesh.morphTargetDictionary.smile]=1;
let maxd=0; const m0=mesh.geometry.morphAttributes.position[mesh.morphTargetDictionary.smile];
for(let i=0;i<m0.count;i++) maxd=Math.max(maxd,Math.abs(m0.getX(i)),Math.abs(m0.getY(i)),Math.abs(m0.getZ(i)));
console.log('smile max delta (any axis)', maxd.toFixed(3), 'relative', mesh.geometry.morphTargetsRelative);
console.log('clips', gltf.animations.map(a=>a.name+':'+a.tracks.map(t=>t.name).join(',')));
const mixer=new THREE.AnimationMixer(gltf.scene); mixer.clipAction(gltf.animations[0]).play(); mixer.setTime(0.2);
console.log('smile influence after mixer 0.2s', mesh.morphTargetInfluences[mesh.morphTargetDictionary.smile].toFixed(3));
console.log('skeleton bones', mesh.skeleton?.bones.map(b=>b.name));
