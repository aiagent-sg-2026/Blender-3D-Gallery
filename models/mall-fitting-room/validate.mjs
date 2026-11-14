import assert from 'node:assert/strict';import fs from 'node:fs';import{fileURLToPath}from'node:url';import{createHash}from'node:crypto';
import{Box3,Vector3,AnimationMixer,LoopOnce}from'three';import{OBB}from'three/addons/math/OBB.js';import{GLTFLoader}from'three/addons/loaders/GLTFLoader.js';import validator from'gltf-validator';
const dir=fileURLToPath(new URL('.',import.meta.url)),spec=JSON.parse(fs.readFileSync(dir+'backlog.json')),bytes=fs.readFileSync(dir+'exports/optimized.glb');
const json=JSON.parse(bytes.subarray(20,20+bytes.readUInt32LE(12))),g=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'');
const validation=await validator.validateBytes(new Uint8Array(bytes));assert.equal(validation.issues.numErrors,0);assert.equal(validation.issues.numWarnings,0);
assert.ok(json.buffers.every(b=>!b.uri));assert.ok(!json.images?.length&&!json.textures?.length&&!json.extensions?.KHR_lights_punctual);
const scene=g.scene;scene.updateMatrixWorld(true);assert.equal(scene.getObjectByName(spec.root)?.userData.units,'metres');for(const n of spec.required_nodes)assert.ok(scene.getObjectByName(n),n);
let triangles=0,vertices=0,primitives=0;scene.traverse(o=>{if(o.isMesh){primitives++;const p=o.geometry.attributes.position;assert.ok(o.geometry.attributes.normal);assert.ok([...p.array].every(Number.isFinite));vertices+=p.count;triangles+=(o.geometry.index?.count??p.count)/3;assert.ok(!o.material.transparent&&o.material.opacity===1,'all surfaces opaque');}});
assert.ok(bytes.length<=spec.budget.bytes&&triangles<=spec.budget.triangles&&primitives<=spec.budget.mesh_primitives);
const bounds=new Box3().setFromObject(scene),dimensions=bounds.getSize(new Vector3()).toArray();dimensions.forEach((x,i)=>assert.ok(Math.abs(x-spec.expected_dimensions_m[i])<.002,'dimension '+i+':'+x));assert.ok(Math.abs(bounds.min.y)<.001);
assert.equal(g.animations.length,1);assert.equal(g.animations[0].name,'DoorOpenClose');assert.ok(Math.abs(g.animations[0].duration-2.5)<.0001);
const door=scene.getObjectByName('MOVABLE_Door'),closed=door.quaternion.clone(),position=door.position.clone(),mixer=new AnimationMixer(scene),action=mixer.clipAction(g.animations[0]);action.setLoop(LoopOnce,1);action.clampWhenFinished=true;
const sample=t=>{action.reset().play();mixer.setTime(t);scene.updateMatrixWorld(true);};
sample(1.25);assert.ok(Math.abs(door.quaternion.angleTo(closed)-spec.door_degrees*Math.PI/180)<.001);
sample(2.5);assert.ok(door.quaternion.angleTo(closed)<.0001&&door.position.distanceTo(position)<.0001);
const fixed=[];scene.traverse(o=>{if(o.isMesh&&/^(WALL_|FRONT_|FRAME_|FLOOR_|BENCH_|SHELF_|HOOK_)/.test(o.name))fixed.push(o);});
const moving=[];door.traverse(o=>{if(o.isMesh&&o.name.startsWith('DOOR_'))moving.push(o);});
assert.equal(moving.length,7,'leaf plus six handle components');assert.equal(fixed.length,23,'all fixed wall and furniture components');
const obb=o=>{o.geometry.computeBoundingBox();return new OBB().fromBox3(o.geometry.boundingBox).applyMatrix4(o.matrixWorld);};
let peak=0;for(let f=1;f<=60;f++){
 sample(f/24);const angle=door.quaternion.angleTo(closed);peak=Math.max(peak,angle);if(f===30)assert.ok(angle>100*Math.PI/180,'sweep must inspect actual open midpoint');
 for(const a of moving)for(const b of fixed)assert.ok(!obb(a).intersectsOBB(obb(b),1e-9),'collision frame '+f+': '+a.name+' / '+b.name);
}
assert.ok(peak>100*Math.PI/180);sample(1/24);
const report={result:'PASS',id:spec.title,backlog_id:spec.id,sha256:createHash('sha256').update(bytes).digest('hex'),glb_bytes:bytes.length,triangles,vertices,primitives,materials:json.materials.length,textures:0,animations:1,dimensions,bounds:{min:bounds.min.toArray(),max:bounds.max.toArray()},budget:spec.budget,animation:{frames:60,opening_degrees:peak*180/Math.PI,collision_method:'World OBB conservative boxes, moving leaf/handles vs fixed walls/frame/floor/furniture; designed hinge attachment excluded',moving_meshes:moving.length,fixed_meshes:fixed.length},validation:{errors:0,warnings:0,validator:validation.validatorVersion}};
fs.writeFileSync(dir+'reports/assets.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
