import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {createCollisionWorld} from './collision.js';
import {createVisitor} from './visitor.js';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
const host=document.querySelector('#view'),status=document.querySelector('#status');
const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setClearColor(0x657078);renderer.outputColorSpace=THREE.SRGBColorSpace;host.append(renderer.domElement);
const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(45,1,.01,100),controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;
scene.add(new THREE.HemisphereLight(0xffffff,0x858e78,2.4));const key=new THREE.DirectionalLight(0xffffff,2.1);key.position.set(4,8,5);scene.add(key);
const fill=new THREE.DirectionalLight(0xffffff,1);fill.position.set(-4,1,-3);scene.add(fill);
new ResizeObserver(()=>{const {clientWidth:w,clientHeight:h}=host;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix()}).observe(host);
let visitor=null,lastFrame=performance.now();
try{
 const gltf=await new GLTFLoader().loadAsync('./corridor.glb');scene.add(gltf.scene);gltf.scene.updateMatrixWorld(true);
 const doors=[],ceilings=[];gltf.scene.traverse(o=>{if(/^Door_[AB]$/.test(o.name))doors.push(o);if(/^Ceiling_\d+$/.test(o.name))ceilings.push(o)});
 const bounds=new THREE.Box3().setFromObject(gltf.scene),records={};
 const layout=await (await fetch('./layout.json')).json();for(const r of layout.objects){const o=gltf.scene.getObjectByName(r.name.replaceAll('.',''));if(o){const b=new THREE.Box3().setFromObject(o);records[r.name]={min:b.min.toArray(),max:b.max.toArray()}}}
 window.corridorStudy={records,doors:doors.length,angle:0,ceilingVisible:true};window.corridorCamera=camera;
 // Static opaque surfaces share material batches. Door parts and transparent
 // surfaces retain their hierarchy and independent sorting/articulation.
 const batches=[],groups=new Map();
 gltf.scene.traverse(o=>{
  if(!o.isMesh||Array.isArray(o.material)||o.material.transparent)return;
  let moving=false,ceiling=false;
  for(let p=o;p;p=p.parent){if(/^Door_[AB]$/.test(p.name))moving=true;if(/^Ceiling_\d+$/.test(p.name))ceiling=true}
  if(moving)return;
  const key=o.material.uuid+ceiling;
  if(!groups.has(key))groups.set(key,{objects:[],ceiling});groups.get(key).objects.push(o);
 });
 for(const {objects,ceiling} of groups.values()){
  if(objects.length<2)continue;
  const geometries=objects.map(o=>{
   let g=o.geometry.clone();g.applyMatrix4(o.matrixWorld);if(g.index)g=g.toNonIndexed();
   for(const a of Object.keys(g.attributes))if(!['position','normal','uv'].includes(a))g.deleteAttribute(a);
   if(!g.attributes.normal)g.computeVertexNormals();
   if(!g.attributes.uv)g.setAttribute('uv',new THREE.BufferAttribute(new Float32Array(g.attributes.position.count*2),2));
   o.visible=false;return g;
  });
  const merged=mergeGeometries(geometries);if(!merged)throw Error('Static batch failed');
  const batch=new THREE.Mesh(merged,objects[0].material);scene.add(batch);batches.push({mesh:batch,ceiling});for(const g of geometries)g.dispose();
 }
 window.corridorStudy.staticBatches=batches.length;
 const world=createCollisionWorld(gltf.scene);
 const applyDoorAngle=(angle)=>{for(const d of doors)d.traverse(o=>{if(o.name.startsWith('HINGE_Left'))o.rotation.y=-angle*Math.PI/180;if(o.name.startsWith('HINGE_Right'))o.rotation.y=angle*Math.PI/180});gltf.scene.updateMatrixWorld(true)};
 window.corridorSetDoors=(angle)=>{
  visitor?.clearInput();
  if(visitor&&!world.doorTransition(window.corridorStudy.angle,angle,visitor.visual.position,applyDoorAngle)){status.textContent='Door path occupied — move away before moving the door';return false}
  if(!visitor){applyDoorAngle(angle);world.refresh()}
  window.corridorStudy.angle=angle;document.querySelector('#doors').textContent=angle?'Close doors':'Open doors';status.textContent='3.6 m corridor · two neutral shops';return true;
 };
 window.corridorView=view=>{
  visitor?.setWalking(false);document.querySelector('#views').open=false;
  controls.enableDamping=false;controls.update();
  camera.fov=(view==='A'||view==='B')&&camera.aspect<.8?60:45;camera.updateProjectionMatrix();
  if(view==='arrival'){camera.position.set(0,1.7,3.3);controls.target.set(0,1.6,0)}
  else if(view==='A'||view==='B'){window.corridorSetDoors(90);const sign=view==='A'?-1:1;camera.position.set(sign*2.2,1.7,.15);controls.target.set(sign*4.7,1.2,0)}
  else {const sphere=bounds.getBoundingSphere(new THREE.Sphere());const v=THREE.MathUtils.degToRad(camera.fov/2),h=Math.atan(Math.tan(v)*camera.aspect);camera.position.copy(sphere.center).add(new THREE.Vector3(12,9,14).normalize().multiplyScalar(sphere.radius/Math.sin(Math.min(v,h))*1.07));controls.target.copy(sphere.center)}
  controls.update();controls.enableDamping=true;window.corridorStudy.view=view;
 };
 visitor=await createVisitor({scene,world,camera,controls,canvas:renderer.domElement,onInspect:()=>{controls.target.copy(visitor.visual.position).add(new THREE.Vector3(0,1,0));controls.update()},onMessage:message=>{status.textContent=message}});
 window.corridorVisitor=visitor;
 Object.defineProperty(window.corridorStudy,'visitor',{get:()=>visitor.state});
 window.corridorView('overview');
 for(const id of ['walk','doors','reset-visitor'])document.querySelector('#'+id).disabled=false;
 document.querySelector('#views summary').addEventListener('click',()=>{if(!document.querySelector('#views').open)visitor.setWalking(false)});
 document.querySelector('#views').addEventListener('toggle',()=>{if(document.querySelector('#views').open)visitor.setWalking(false)});
 document.addEventListener('keydown',e=>{if(e.key==='Escape'&&document.querySelector('#views').open){document.querySelector('#views').open=false;document.querySelector('#views summary').focus();e.preventDefault()}},true);
 document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>window.corridorView(b.dataset.view));
 document.querySelector('#doors').onclick=()=>{window.corridorSetDoors(window.corridorStudy.angle?0:90);if(visitor.state.walking)renderer.domElement.focus({preventScroll:true})};
 document.querySelector('#ceiling').onclick=()=>{window.corridorStudy.ceilingVisible=!window.corridorStudy.ceilingVisible;for(const c of ceilings)c.visible=window.corridorStudy.ceilingVisible;for(const b of batches)if(b.ceiling)b.mesh.visible=window.corridorStudy.ceilingVisible;document.querySelector('#ceiling').textContent=window.corridorStudy.ceilingVisible?'Hide ceiling':'Show ceiling'};
 status.textContent='3.6 m corridor · two neutral shops · visitor ready';status.dataset.ready='true';
}catch(e){status.textContent=e.message;status.dataset.ready='false';console.error(e)}
renderer.setAnimationLoop(()=>{const now=performance.now();if(document.hidden){lastFrame=now;return}if(now-lastFrame<1000/30)return;const dt=(now-lastFrame)/1000;lastFrame=now;if(visitor)visitor.update(dt);if(!visitor?.state.walking)controls.update();renderer.render(scene,camera);if(window.corridorStudy){window.corridorStudy.drawCalls=renderer.info.render.calls}});
