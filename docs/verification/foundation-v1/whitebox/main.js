import * as T from './runtime/vendor/three.module.min.js';
import R from './runtime/vendor/rapier.mjs';
import {createPlayer} from './runtime/assets/player.js';
import {GLTFLoader} from './runtime/vendor/GLTFLoader.js';
const canvas=document.querySelector('#scene'),status=document.querySelector('#status');
const layout=await (await fetch('./layout.json')).json();
const started=performance.now();
try {
 await R.init();
 const physics=new R.World({x:0,y:-24,z:0});physics.timestep=1/60;
 const renderer=new T.WebGLRenderer({canvas,antialias:true});renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;
 const scene=new T.Scene();scene.background=new T.Color(0xa7b3b1);
 scene.add(new T.HemisphereLight(0xffffff,0x5a645c,2));const light=new T.DirectionalLight(0xffffff,2.2);light.position.set(8,15,5);scene.add(light);
 for(const part of layout.parts){if(part.collision)physics.createCollider(R.ColliderDesc.cuboid(...part.size.map(x=>x/2)).setTranslation(...part.center));}
 const model=(await new GLTFLoader().loadAsync('./foundation-v1.glb')).scene;let modelParts=0;model.traverse(o=>{if(o.isMesh)modelParts++;});if(modelParts!==layout.parts.length)throw Error('Whitebox export does not match layout part count');scene.add(model);
 const grid=new T.GridHelper(36,30,0x48635d,0x8d9e97);grid.position.y=.004;scene.add(grid);
 function label(text,position,scale=1){const c=document.createElement('canvas');c.width=512;c.height=96;const ctx=c.getContext('2d');ctx.fillStyle='#17382f';ctx.fillRect(0,0,c.width,c.height);ctx.font='bold 36px sans-serif';ctx.fillStyle='#fff7de';ctx.textAlign='center';ctx.fillText(text,256,60);const tex=new T.CanvasTexture(c);tex.colorSpace=T.SRGBColorSpace;const o=new T.Sprite(new T.SpriteMaterial({map:tex,depthTest:false}));o.position.set(...position);o.scale.set(3.3*scale,.62*scale,1);scene.add(o);return o;}
 label('NEW MOON',[-6,3.25,0]);label('SAMPLE STORE',[6,3.25,0]);label('ATRIUM',[0,3.25,13]);label('ENTRANCE',[0,3.25,18]);
 const player=await createPlayer(T,R,physics,scene,canvas,new T.MeshBasicMaterial({color:0x172c24,transparent:true,opacity:.12}),new T.PlaneGeometry(1,1),[]);
 const planCamera=new T.OrthographicCamera(-14,14,17,-17,.1,100);planCamera.position.set(0,40,3.6);planCamera.up.set(0,0,-1);planCamera.lookAt(0,0,3.6);
 let plan=false,manual=false,frame=0,accumulator=0,last=performance.now(),frames=0,ready=false;
 const STEP=1/60;
 function zone(){const p=player.state;for(const r of layout.regions){const [x1,x2,z1,z2]=r.bounds;if(p.x>=x1&&p.x<=x2&&p.z>=z1&&p.z<=z2)return r.id;}return 'outside';}
 function snapshot(){return {ready,zone:zone(),...player.state,camera:player.camera.position.toArray(),drawCalls:renderer.info.render.calls,frames,view:plan?'plan':'walk',engine:{three:T.REVISION,rapier:R.version()},layoutVersion:layout.version,geometry:'foundation-v1.glb',modelParts};}
 function render(){renderer.render(scene,plan?planCamera:player.camera);frames++;status.textContent=`${plan?'Plan view':'Walking'} · ${zone()} · ${renderer.info.render.calls} draw calls`;document.querySelector('#position').textContent=`X ${player.state.x.toFixed(2)} m · Z ${player.state.z.toFixed(2)} m · WASD / arrows walk · Q/E turn`;}
 function tick(){player.update(STEP);physics.step();player.sync();player.updateCamera(STEP);}
 function reset(){player.clearInput();player.setInput({forward:0,right:0,yaw:0,pitch:.25});const [x,y,z]=layout.spawn;player.body.setTranslation({x,y,z},true);player.body.setNextKinematicTranslation({x,y,z});physics.step();player.updateCamera(0,true);player.setInput(null);manual=false;plan=false;document.querySelector('#plan').textContent='Floor plan';render();}
 function resize(){const w=canvas.clientWidth,h=canvas.clientHeight;if(!w||!h)return;renderer.setPixelRatio(Math.min(devicePixelRatio,w<600?1.5:2));renderer.setSize(w,h,false);player.camera.aspect=w/h;player.camera.updateProjectionMatrix();const halfH=Math.max(17,11/(w/h));planCamera.left=-halfH*w/h;planCamera.right=halfH*w/h;planCamera.top=halfH;planCamera.bottom=-halfH;planCamera.updateProjectionMatrix();player.updateCamera(0,true);render();}
 player.setPaused(()=>plan||document.hidden);
 document.querySelector('#plan').onclick=()=>{plan=!plan;manual=false;player.clearInput();player.setInput(null);document.querySelector('#plan').textContent=plan?'Walkthrough':'Floor plan';render();};
 document.querySelector('#reset').onclick=()=>{reset();player.setInput(null);canvas.focus();};
 Object.defineProperty(window,'__whitebox',{value:Object.freeze({get ready(){return ready;},get state(){return snapshot();},setInput(input){manual=input!==null;player.setInput(input);},step(ms){if(document.hidden||plan)return snapshot();for(let i=0;i<Math.min(600,Math.max(0,Math.floor(ms/(STEP*1000))));i++)tick();render();return snapshot();},reset(){reset();},get layout(){return structuredClone(layout);}})});
 function animate(now){frame=0;if(document.hidden)return;const elapsed=Math.min(.1,Math.max(0,(now-last)/1000));last=now;if(!manual&&!plan){accumulator+=elapsed;while(accumulator>=STEP){tick();accumulator-=STEP;}render();}frame=requestAnimationFrame(animate);}
 document.addEventListener('visibilitychange',()=>{player.clearInput();cancelAnimationFrame(frame);frame=0;if(!document.hidden){last=performance.now();accumulator=0;frame=requestAnimationFrame(animate);}});
 new ResizeObserver(resize).observe(canvas);reset();ready=true;resize();frame=requestAnimationFrame(animate);window.__whiteboxStartupMs=performance.now()-started;
} catch(error){status.textContent='Whitebox failed to load: '+error.message;window.__whiteboxError=error.message;throw error;}
