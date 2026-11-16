// Usage (repo root): node models/chibi-mall-guide-v5/base-rig/check_glb.mjs GLB   Validates with glTF Validator and loads in Three.js (Node), lists clips, skeleton and size.
import fs from 'node:fs'; const root = process.cwd();
const validator = (await import(root + '/node_modules/gltf-validator/index.js')).default;
const THREE = await import(root + '/node_modules/three/build/three.module.js');
const { GLTFLoader } = await import(root + '/node_modules/three/examples/jsm/loaders/GLTFLoader.js');
const buf = fs.readFileSync(process.argv[2]); const v = await validator.validateBytes(new Uint8Array(buf));
const gltf = await new GLTFLoader().parseAsync(buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength), '');
let sk = null, tris = 0; gltf.scene.traverse((o) => { if (o.isSkinnedMesh) { sk = o; tris += (o.geometry.index ? o.geometry.index.count : o.geometry.attributes.position.count) / 3; } });
const box = new THREE.Box3().setFromObject(gltf.scene);
console.log(JSON.stringify({ validator: { errors: v.issues.numErrors, warnings: v.issues.numWarnings, infos: v.issues.numInfos, msgs: v.issues.messages.slice(0, 4).map((m) => m.code) },
  bytes: buf.length, triangles: tris, drawCalls: v.info.drawCallCount, materials: v.info.materialCount, bones: sk?.skeleton.bones.length, size: box.getSize(new THREE.Vector3()).toArray().map((x) => +x.toFixed(3)),
  clips: gltf.animations.map((a) => ({ name: a.name, seconds: +a.duration.toFixed(2), tracks: a.tracks.length })) }));
