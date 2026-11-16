import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const $ = id => document.getElementById(id);
const canvas = document.querySelector('canvas');
const options = new URLSearchParams(location.search);
const testing = options.has('qa');

async function openVisitor() {
  const renderer = new THREE.WebGLRenderer({canvas, antialias:true, preserveDrawingBuffer:testing, alpha:false});
  renderer.setPixelRatio(testing ? 1 : Math.min(devicePixelRatio,2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFShadowMap;
  renderer.toneMapping = THREE.NeutralToneMapping;
  renderer.toneMappingExposure = .99;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf0edf5);
  const env = new RoomEnvironment();
  const pmrem = new THREE.PMREMGenerator(renderer);
  const envTarget = pmrem.fromScene(env, .035);
  scene.environment = envTarget.texture;
  scene.environmentIntensity = .32;
  env.dispose(); pmrem.dispose();
  const camera = new THREE.OrthographicCamera(-.6,.6,.8,-.8,.02,20);
  const orbit = new OrbitControls(camera,canvas);
  orbit.minZoom=.55; orbit.maxZoom=4; orbit.enablePan=true;
  const hemi = new THREE.HemisphereLight(0xfff8f4,0xb8a6b7,.81);
  scene.add(hemi);
  function light(color,intensity,x,y,z) {
    const l=new THREE.DirectionalLight(color,intensity); l.position.set(x,y,z);
    l.target.position.set(0,.68,0); scene.add(l,l.target); return l;
  }
  const key=light(0xffebd8,2.15,-2.6,4.0,3.7);
  key.castShadow=true; key.shadow.mapSize.set(1024,1024);
  Object.assign(key.shadow.camera,{left:-1,right:1,top:1,bottom:-1,near:.1,far:10});
  key.shadow.normalBias=.0018; key.shadow.bias=-.00022;
  light(0xcddcff,.54,2.4,1.8,2.3); light(0xffdfd2,1.1,1.9,3,-2.6);
  const ground=new THREE.Mesh(new THREE.PlaneGeometry(200,200),
    new THREE.ShadowMaterial({color:0x64556d,opacity:.16,depthWrite:false}));
  ground.rotation.x=-Math.PI/2; ground.position.y=-.002; ground.receiveShadow=true;scene.add(ground);
  const contactCanvas=document.createElement('canvas');contactCanvas.width=128;contactCanvas.height=128;
  const ctx=contactCanvas.getContext('2d'),grad=ctx.createRadialGradient(64,64,4,64,64,64);
  grad.addColorStop(0,'rgba(87,67,83,.29)');grad.addColorStop(.53,'rgba(90,73,90,.12)');grad.addColorStop(1,'rgba(90,73,90,0)');
  ctx.fillStyle=grad;ctx.fillRect(0,0,128,128);
  const softShadow=new THREE.Mesh(new THREE.PlaneGeometry(.67,.39),new THREE.MeshBasicMaterial({map:new THREE.CanvasTexture(contactCanvas),transparent:true,depthWrite:false}));
  softShadow.rotation.x=-Math.PI/2;softShadow.position.set(.007,-.001,.012);scene.add(softShadow);
  const loader=new GLTFLoader();
  const payload=$('asset');
  let gltf;
  if(payload) {
    const bytes=Uint8Array.from(atob(payload.textContent.trim()), c=>c.charCodeAt(0));
    gltf=await loader.parseAsync(bytes.buffer,'');
  } else {
    gltf=await loader.loadAsync(options.get('glb') || '../delivery/visitor.glb');
  }
  const model=gltf.scene;scene.add(model); model.updateMatrixWorld(true);
  const meshes=[],bones=[],byName={},rest=new Map(),morphs=[],materials=new Map();
  model.traverse(o=>{
    byName[o.name]=o;
    if(o.isMesh){meshes.push(o);o.castShadow=true;o.receiveShadow=true;materials.set(o,o.material);}
    if(o.isBone){bones.push(o);rest.set(o,{local:o.quaternion.clone(),world:o.getWorldQuaternion(new THREE.Quaternion()),pos:o.position.clone()});}
    if(o.morphTargetDictionary)morphs.push(o);
  });
  const presets=model.userData.expressionPresets;const contracts=model.userData.clipInfo;
  const clips=new Map(gltf.animations.map(c=>[c.name,c]));
  const mixer=new THREE.AnimationMixer(model);
  const oldMorph=new Map(morphs.map(o=>[o,Array(o.morphTargetInfluences.length).fill(0)]));
  let expression='default',action=null,active='',playing=false,last=0,span=1.52,measuring=false,dirty=true;
  const cameraTarget=new THREE.Vector3();
  function size(){
    const {width,height}=canvas.getBoundingClientRect();const aspect=width/height;
    renderer.setSize(width,height,false);
    Object.assign(camera,{left:-span*aspect/2,right:span*aspect/2,top:span/2,bottom:-span/2});
    camera.updateProjectionMatrix();
  }
  function view(deg=22,scale=1.52,height=.655,pitch=.045) {
    const a=deg*Math.PI/180, dist=3;
    span=scale; camera.zoom=1; cameraTarget.set(0,height,0);
    camera.position.set(dist*Math.sin(a),height+dist*Math.sin(pitch),dist*Math.cos(a));
    orbit.target.copy(cameraTarget); orbit.update(); size();
  }
  function resetBones(){for(const b of bones){b.position.copy(rest.get(b).pos);b.quaternion.copy(rest.get(b).local);}}
  function thinking(){
    const pose=model.userData.thinkingPose;
    for(const b of bones){
      const q=pose[b.userData.name ?? b.name] ?? pose[b.name.replace(/([LR])$/,'.$1')];
      if(!q)continue;
      const w=new THREE.Quaternion().fromArray(q).multiply(rest.get(b).world);
      b.quaternion.copy(b.parent.getWorldQuaternion(new THREE.Quaternion()).invert().multiply(w));
      b.updateWorldMatrix(false,true);
    }
  }
  function motion(name,play=false){
    mixer.stopAllAction();resetBones();active=name;action=null;playing=play;
    for(const o of morphs){o.morphTargetInfluences.fill(0);oldMorph.get(o).fill(0);}
    if(name){
      action=mixer.clipAction(clips.get(name));action.reset();
      action.setLoop(contracts[name].loop?THREE.LoopRepeat:THREE.LoopOnce,contracts[name].loop?Infinity:1);
      action.clampWhenFinished=!contracts[name].loop;action.play();mixer.update(0);
    }
    $('motion').value=name;draw();
  }
  function face(name){expression=name;$('face').value=name;draw();}
  function draw(dt=0){
    for(const o of morphs)o.morphTargetInfluences.splice(0,Infinity,...oldMorph.get(o));
    if(action)mixer.update(dt);
    if(!action){resetBones();if(expression==='thinking')thinking();}
    for(const o of morphs){
      const values=o.morphTargetInfluences;oldMorph.set(o,values.slice());
      for(const [name,amount] of Object.entries(presets[expression] ?? {})){
        const i=o.morphTargetDictionary[name];if(i!==undefined)values[i]=Math.max(values[i],amount);
      }
    }
    orbit.update();model.updateMatrixWorld(true);if(!measuring)renderer.render(scene,camera);
  }
  function sample(name,frame){
    motion(name);if(action){action.time=frame/contracts[name].fps;}
    draw();
  }
  function slot(id,visible){for(const m of meshes)if(m.userData.partSlot===id)m.visible=visible;draw();}
  const clay=new THREE.MeshStandardMaterial({color:0xbab4bb,roughness:.78});
  function grey(enabled){for(const m of meshes)m.material=enabled?clay:materials.get(m);draw();}
  for(const name of clips.keys())$('motion').add(new Option(name.replaceAll('_',' '),name));
  for(const name of Object.keys(presets))$('face').add(new Option(name,name));
  $('motion').onchange=e=>motion(e.target.value,true);
  $('face').onchange=e=>face(e.target.value);
  $('pack').onchange=e=>slot('Backpack',e.target.checked);$('watch').onchange=e=>slot('Watch',e.target.checked);
  $('play').onclick=()=>{if(!active && clips.has('idle'))motion('idle',true);else if(action?.paused)motion(active,true);else playing=!playing;};
  $('reset').onclick=()=>{motion('');face('default');for(const [id,s] of [['pack','Backpack'],['watch','Watch']]){$(id).checked=true;slot(s,true);}view();draw();};
  $('state').textContent='';
  view();face('default');
  new ResizeObserver(()=>{size();draw();}).observe(canvas.parentElement);
  function measure(fn){measuring=true;try{return fn();}finally{measuring=false;draw();}}
  orbit.addEventListener('change',()=>{dirty=true;});
  if(!testing){
    renderer.setAnimationLoop(time=>{const dt=Math.min(.075,(time-last)/1000);last=time;
      if(playing||dirty){dirty=false;draw(playing?dt:0);}});
  }
  return {THREE,scene,model,meshes,bones,renderer,clips,contracts,presets,byName,motion,sample,face,slot,grey,view,draw,camera,ground,measure,
          isPlaying:()=>playing, frame:()=>action?.time??0};
}
window.visitorReady=openVisitor().catch(error=>{$('state').textContent='Unable to load the model. '+error.message;
  console.error(error);throw error;});

