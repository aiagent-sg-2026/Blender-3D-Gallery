import assert from 'node:assert/strict';import fs from 'node:fs';import {createHash} from 'node:crypto';
import {Vector3,AnimationMixer} from 'three';import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {readGlb} from '../../../models/mall-shopfront-door/glb.mjs';import {createCollisionWorld,BODY} from './collision.js';
const {scene}=await readGlb('docs/verification/mall-corridor/corridor.glb');const world=createCollisionWorld(scene);const checks=[];
const run=(name,fn)=>{fn();checks.push({name,passed:true});console.log('PASS',name)};
const pose=angle=>{scene.traverse(o=>{if(o.name.startsWith('HINGE_Left'))o.rotation.y=-angle*Math.PI/180;if(o.name.startsWith('HINGE_Right'))o.rotation.y=angle*Math.PI/180});scene.updateMatrixWorld(true)};
run('spawn has full floor support and no obstacle',()=>assert.equal(world.obstruction({x:0,z:3}),null));
run('large movement cannot tunnel through closed door',()=>{const p={x:0,z:0};world.move(p,-10,0);assert.ok(p.x>-1.4&&p.x<-.7);assert.equal(world.obstruction(p),null)});
run('opening both doors is clear with visitor in centre',()=>assert.equal(world.doorTransition(0,90,{x:0,z:0},pose),true));
run('actual walk-radius route reaches both stores and returns',()=>{
 const p={x:0,z:3};for(const [x,z] of [[0,0],[-3.6,0],[0,0],[3.6,0],[0,0],[0,3]]){world.move(p,x-p.x,z-p.z);assert.ok(Math.hypot(p.x-x,p.z-z)<1e-5);assert.equal(world.obstruction(p),null)}
});
run('door closing refuses occupied doorway and restores pose',()=>{assert.equal(world.obstruction({x:-1.8,z:0}),null);assert.equal(world.doorTransition(90,0,{x:-1.8,z:0},pose),false);assert.ok(Math.abs(scene.getObjectByName('Door_A').getObjectByProperty('name','HINGE_Left').rotation.y+Math.PI/2)<1e-6);assert.equal(world.obstruction({x:-1.8,z:0}),null)});
run('wall sliding preserves free tangential movement',()=>{const p={x:-3.3,z:1.4};world.move(p,-.4,1.6);assert.ok(p.x<-3.6&&p.z<2);assert.equal(world.obstruction(p),null)});
run('full footprint cannot leave floor edge',()=>{const p={x:0,z:3};world.move(p,0,10);assert.ok(p.z<3.05);assert.equal(world.obstruction(p),null)});
// Character proof uses actual exported clips and transformed vertices, independent of runtime state labels.
const bytes=fs.readFileSync('models/gjh-mall-visitor/exports/gjh-mall-visitor.glb');const gltf=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'');const mixer=new AnimationMixer(gltf.scene),clips=[];
for(const clip of gltf.animations.filter(c=>['idle','walk'].includes(c.name))){mixer.stopAllAction();mixer.clipAction(clip).play();let maxRadius=0,maxY=0,minY=Infinity;for(let sample=0;sample<=120;sample++){mixer.setTime(sample/120*clip.duration);gltf.scene.updateMatrixWorld(true);gltf.scene.traverse(o=>{if(o.isMesh){const a=o.geometry.attributes.position;for(let i=0;i<a.count;i++){const v=new Vector3().fromBufferAttribute(a,i).applyMatrix4(o.matrixWorld);maxRadius=Math.max(maxRadius,Math.hypot(v.x,v.z));maxY=Math.max(maxY,v.y);minY=Math.min(minY,v.y)}}})}assert.ok(maxRadius<BODY.radius&&maxY<BODY.height&&minY>-.002);clips.push({name:clip.name,samples:121,maxRadius,maxY,minY,passed:true})}
assert.equal(clips.length,2);
fs.writeFileSync('docs/verification/mall-corridor/movement-results.json',JSON.stringify({body:BODY,checks,character:{path:'models/gjh-mall-visitor/exports/gjh-mall-visitor.glb',sha256:createHash('sha256').update(bytes).digest('hex'),clips},limits:'Conservative flat-floor cylinder against projected component boxes; fixed substeps, sampled character poses. No stairs, gravity, or continuous-time exact mesh collision.'},null,2)+'\n');
