import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
const status=document.querySelector('#status');
const renderer=new THREE.WebGLRenderer({antialias:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2)); renderer.setClearColor(0x657078); renderer.outputColorSpace=THREE.SRGBColorSpace; document.body.append(renderer.domElement);
const scene=new THREE.Scene(); scene.add(new THREE.HemisphereLight(0xffffff,0x535b53,2));
const light=new THREE.DirectionalLight(0xffffff,2.1); light.position.set(4,7,5); scene.add(light);
const camera=new THREE.PerspectiveCamera(35,1,0.01,100); camera.position.set(7,5,9);
const controls=new OrbitControls(camera,renderer.domElement); controls.target.set(0,1.35,0); controls.enableDamping=true;
controls.update(); window.fitCamera=camera;
function resize(){const height=innerHeight-document.querySelector('header').offsetHeight;renderer.setSize(innerWidth,height,false); camera.aspect=innerWidth/height;camera.updateProjectionMatrix()} addEventListener('resize',resize);resize();
try {
 const gltf=await new GLTFLoader().loadAsync('./fit-study.glb'); scene.add(gltf.scene); gltf.scene.updateMatrixWorld(true);
 const records={}; gltf.scene.traverse(o=>{if(/^(Floor_|Ceiling_|Column$|Partition_Left$|Partition_Right$|Door$|Fascia_|Ceiling_Collar$)/.test(o.name)){let b=new THREE.Box3().setFromObject(o); if(!b.isEmpty()) records[o.name]={min:b.min.toArray(),max:b.max.toArray()};}});
 const full=new THREE.Box3().setFromObject(gltf.scene);
 window.fitView=(view)=>{
  controls.enableDamping=false;controls.update();
  if(view==='collar'){controls.target.set(-1.8,3,0);camera.position.set(-3.3,1,-2.4);}
  else if(view==='underside'){controls.target.set(-.2,2.25,.3);camera.position.set(5,1.3,8);}
  else {
   const sphere=full.getBoundingSphere(new THREE.Sphere());
   const v=THREE.MathUtils.degToRad(camera.fov/2); const h=Math.atan(Math.tan(v)*camera.aspect);
   const distance=sphere.radius/Math.sin(Math.min(v,h))*1.08;
   controls.target.copy(sphere.center);camera.position.copy(sphere.center).add(new THREE.Vector3(7,3.65,9).normalize().multiplyScalar(distance));
  }controls.update();controls.enableDamping=true;
 };
 window.fitView('front');
 document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>window.fitView(b.dataset.view)));
 window.fitStudy={records,full:{min:full.min.toArray(),max:full.max.toArray()},meshCount:0}; gltf.scene.traverse(o=>{if(o.isMesh)window.fitStudy.meshCount++});
 status.textContent=`Loaded ${Object.keys(records).length} assemblies; drag to orbit`; status.dataset.ready='true';
} catch(e){status.textContent=`Load failed: ${e.message}`; status.dataset.ready='false'; console.error(e)}
renderer.setAnimationLoop(()=>{controls.update();renderer.render(scene,camera)});
