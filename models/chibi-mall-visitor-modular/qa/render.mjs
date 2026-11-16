/* Render the actual standalone preview in Chromium. Every tile comes from the delivered GLB. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import {chromium} from 'playwright';
import {inspectRuntime} from './runtime-check.mjs';

const playAll=process.argv.includes('--play-all');
const [directory,reference,blockoutPreview]=process.argv.slice(2).filter(a=>a!=='--play-all');
const out=path.resolve(directory);
const qa=path.join(out,'qa');await fs.mkdir(qa,{recursive:true});
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const artifactSha256=sha(await fs.readFile(path.join(out,'visitor.glb')));
const previewBytes=await fs.readFile(path.join(out,'preview.html'));
const embedded=previewBytes.toString().match(/id="asset">([^<]+)<\/script>/);
if(!embedded||sha(Buffer.from(embedded[1],'base64'))!==artifactSha256)throw Error('Preview/export mismatch');
const captures=[];
const artifacts=new Map();
let captureArtifactSha256=artifactSha256,capturePreviewSha256=sha(previewBytes);
const browser=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const page=await browser.newPage({viewport:{width:640,height:740},deviceScaleFactor:1});
const errors=[],warnings=[],requests=[];
page.on('pageerror',e=>errors.push(e.message));
page.on('console',m=>{if(m.type()==='error')errors.push(m.text());if(m.type()==='warning')warnings.push(m.text());});
page.on('requestfailed',r=>requests.push(r.url().slice(0,140)));
async function open(file,source=path.join(out,'visitor.glb')){
  const preview=await fs.readFile(file);
  const payload=preview.toString().match(/id="asset">([^<]+)<\/script>/);
  captureArtifactSha256=sha(await fs.readFile(source));capturePreviewSha256=sha(preview);
  if(!payload||sha(Buffer.from(payload[1],'base64'))!==captureArtifactSha256)throw Error('Capture preview/export mismatch');
  artifacts.set(captureArtifactSha256,{file:path.relative(out,source),sha256:captureArtifactSha256,previewSha256:capturePreviewSha256});
  await page.goto(pathToFileURL(file).href+'?qa=1');
  await page.addStyleTag({content:'main{display:block}aside{display:none}#stage{width:100vw;height:100vh}'});
  await page.evaluate(async()=>{window.v=await window.visitorReady;});
}
async function saveFile(name,url,settings={}){
  const bytes=Buffer.from(url.split(',')[1],'base64');
  await fs.writeFile(path.join(qa,name+'.png'),bytes);
  captures.push({file:name+'.png',sha256:sha(bytes),artifactSha256:captureArtifactSha256,
    previewSha256:capturePreviewSha256,...settings});
}
async function sheet(name,title,tiles,columns,width,height){
  await page.setViewportSize({width,height});
  const data=await page.evaluate(async({title,tiles,columns,width,height})=>{
    const {view,draw,slot,grey,motion,sample,face,renderer,contracts}=v;
    const pad=12, label=36, heading=55;
    const sheet=document.createElement('canvas');sheet.width=pad+(width+pad)*columns;
    sheet.height=heading+pad+Math.ceil(tiles.length/columns)*(height+label+pad);
    const ctx=sheet.getContext('2d');ctx.fillStyle='#f6f4f8';ctx.fillRect(0,0,sheet.width,sheet.height);
    ctx.fillStyle='#272331';ctx.font='600 23px -apple-system, sans-serif';ctx.fillText(title,18,36);
    for(let i=0;i<tiles.length;i++){
      const t=tiles[i];
      slot('Backpack',t.bag!==false);slot('Watch',t.watch!==false);slot('Hair',t.hair!==false);grey(!!t.clay);
      face(t.expression||'default');
      if(t.clip)sample(t.clip,t.frame??contracts[t.clip].reviewFrame);else motion('');
      v.ground.visible=t.floor!==false;
      let fixture;
      if(t.fixture==='item'||t.fixture==='seat'){
        const seat=t.fixture==='seat', {THREE}=v;
        fixture=new THREE.Mesh(new THREE.BoxGeometry(...(seat?[.34,.025,v.contracts.sit.seatDepthM]:contracts.pick_up.testProductSizeM)),
          new THREE.MeshStandardMaterial({color:seat?0x968375:0xd3a26d,roughness:.85}));
        if(seat)fixture.position.set(0,v.contracts.sit.seatHeightM-.0125,v.contracts.sit.seatCenterZ);
        else {
          const info=contracts.pick_up, frame=t.frame??info.reviewFrame;
          fixture.position.fromArray(info.target);
          if(frame>info.contactFrame){
            const socket=v.model.getObjectByName(info.contactSocket);
            sample('pick_up',info.contactFrame);
            const gripSpace=socket.matrixWorld.clone().invert();
            fixture.updateMatrix();gripSpace.multiply(fixture.matrix);
            sample('pick_up',frame);
            socket.matrixWorld.clone().multiply(gripSpace).decompose(fixture.position,fixture.quaternion,fixture.scale);
          }
        }
        fixture.castShadow=true;fixture.receiveShadow=true;v.scene.add(fixture);
      }
      view(t.deg??0,t.span??1.44,t.y??.644,t.pitch??.032);draw();
      if(t.focus==='item'){
        view(t.deg,t.span,fixture.position.y,t.pitch??.08);draw();
        v.camera.position.x+=fixture.position.x;v.camera.position.z+=fixture.position.z;
        v.camera.updateMatrixWorld();renderer.render(v.scene,v.camera);
      }
      const x=pad+(i%columns)*(width+pad),y=heading+pad+Math.floor(i/columns)*(height+label+pad);
      ctx.drawImage(renderer.domElement,x,y,width,height);
      ctx.fillStyle='#373141';ctx.font='500 16px -apple-system, sans-serif';ctx.fillText(t.label,x+3,y+height+24);
      if(fixture){v.scene.remove(fixture);fixture.geometry.dispose();fixture.material.dispose();}
    }
    v.ground.visible=true;slot('Hair',true);grey(false);return sheet.toDataURL();
  },{title,tiles,columns,width,height});
  await saveFile(name,data,{title,tiles,columns,viewport:{width,height}});
}
try{
  await open(path.join(out,'preview.html'));
  await page.setViewportSize({width:740,height:830});
  await page.evaluate(()=>{v.view(-22,1.47,.645,.043);v.sample('talk',6);v.draw();});
  await saveFile('portrait',await page.evaluate(()=>v.renderer.domElement.toDataURL()));
  await sheet('turntable','GJH Mall Visitor · Turntable',Array.from({length:8},(_,i)=>({label:i*45+'°',deg:i*45})),4,250,332);
  await sheet('expressions','Facial expressions',Object.keys(await page.evaluate(()=>v.presets)).map(name=>({
    label:name[0].toUpperCase()+name.slice(1),expression:name,deg:-8,span:.61,y:1.044,pitch:0,floor:false})),3,315,305);
  await sheet('head','Head and hair',[{label:'Face cage',hair:false,deg:0},{label:'Front',deg:0},{label:'Three-quarter',deg:-35},
    {label:'Profile',deg:90},{label:'Rear three-quarter',deg:135},{label:'Nape',deg:180}].map(t=>({...t,span:.64,y:1.044,pitch:0,floor:false})),3,315,305);
  await sheet('accessories','Equipment combinations',[{label:'Backpack + watch'},{label:'Watch only',bag:false},
    {label:'Backpack only',watch:false},{label:'No accessories',bag:false,watch:false}].map(t=>({...t,deg:138})),4,225,320);
  const c=await page.evaluate(()=>v.contracts);
  await sheet('actions','Motion library · Sampled poses',Object.keys(c).map(clip=>({clip,label:clip.replace('_',' '),
    deg:['pick_up','sit','inspect','point'].includes(clip)?-55:-16,fixture:clip==='sit'?'seat':clip==='pick_up'?'item':null})),4,225,288);
  await sheet('contacts','Deformation and contacts',[
    {clip:'walk',frame:0,deg:85,label:'Walk · heel contact'},{clip:'walk',frame:8,deg:85,label:'Walk · passing'},
    {clip:'run',frame:0,deg:85,label:'Run · contact'},{clip:'run',frame:5,deg:85,label:'Run · passing'},
    {clip:'sit',deg:78,fixture:'seat',label:'Seated hold'},{clip:'pick_up',deg:-48,fixture:'item',label:'Pickup · frame 36'},
    {expression:'thinking',deg:-35,label:'Hand to chin'},{clip:'wave',expression:'wink',deg:-15,label:'Wink during wave'}],4,230,295);
  await sheet('pickup-grasp','Right-hand pickup · test product',[
    {deg:-50,frame:32,label:'Approach · frame 32'}, {deg:0,frame:36,label:'Contact · front'},
    {deg:48,frame:36,label:'Contact · palm side'}, {deg:-50,frame:36,label:'Contact · outer side'},
    {deg:35,frame:48,label:'Lift · frame 48'}, {deg:25,frame:63,label:'Carry · frame 63'}
  ].map(t=>({...t,clip:'pick_up',fixture:'item',focus:'item',span:.19})),3,250,225);
  for(const clip of Object.keys(c)){
    const frames=c[clip].frames;
    await sheet('clip-'+clip,clip.replaceAll('_',' ')+' · timeline',Array.from({length:12},(_,i)=>({
      clip,frame:frames*i/11,label:(frames*i/11/c[clip].fps).toFixed(2)+' s',
      deg:['sit','pick_up','inspect','point'].includes(clip)?-55:-18,
      fixture:clip==='sit'?'seat':clip==='pick_up'?'item':null})),4,225,288);
  }
  await sheet('details','Wardrobe details',[
    {label:'Collar and straps',deg:16,span:.40,y:.649},{label:'Pocket and pull',deg:164,span:.39,y:.58},
    {label:'Left wrist',deg:35,span:.43,y:.50},{label:'Denim, front',deg:0,span:.42,y:.315},
    {label:'Denim, back',deg:168,span:.45,y:.36},{label:'Low-top sneakers',deg:-27,span:.41,y:.115,pitch:.18}],3,292,260);
  await sheet('shoes','Sneaker construction',[
    {label:'Original review angle',deg:-27,pitch:.18},
    {label:'Elevated front',deg:0,pitch:.55},
    {label:'Elevated quarter',deg:-30,pitch:.55},
    {label:'Outer profile',deg:90,pitch:.12}].map(t=>({...t,span:.38,y:.11})),2,420,320);
  if(reference){
    const ref=await fs.readFile(reference);
    await page.setViewportSize({width:320,height:505});
    const overlay=await page.evaluate(async b64=>{
      const img=new Image();img.src='data:image/png;base64,'+b64;await img.decode();
      // Only the main front view is a registration target. Crown at y=28, ground at y=479.
      if(img.naturalWidth!==1536||img.naturalHeight!==1024)throw Error('Reference overlay expects the supplied 1536 × 1024 sheet.');
      const c=document.createElement('canvas');c.width=990;c.height=568;const ctx=c.getContext('2d');
      const refCrop=document.createElement('canvas');refCrop.width=320;refCrop.height=505;
      refCrop.getContext('2d').drawImage(img,286,42,208,475,56,16,208,475);
      v.motion('');v.face('default');v.slot('Backpack',true);v.slot('Watch',true);v.view(0,1.3*505/451,.65,0);v.draw();
      ctx.fillStyle='#f5f3f8';ctx.fillRect(0,0,990,568);ctx.drawImage(refCrop,5,12);ctx.drawImage(v.renderer.domElement,335,12);
      ctx.drawImage(refCrop,665,12);ctx.globalAlpha=.5;ctx.drawImage(v.renderer.domElement,665,12);ctx.globalAlpha=1;
      for(const [i,label] of ['Reference','Exported GLB','50% overlay'].entries()){
        const x=5+330*i;ctx.fillStyle='#312c3a';ctx.font='18px sans-serif';ctx.fillText(label,x+18,553);
        ctx.strokeStyle='rgba(67,105,112,.52)';ctx.lineWidth=1;ctx.setLineDash([3,4]);
        for(const y of [54,173,228,349,505]){const yy=y-26+12;ctx.beginPath();ctx.moveTo(x+42,yy);ctx.lineTo(x+280,yy);ctx.stroke();}
      }
      return c.toDataURL();
    },ref.toString('base64'));
    await saveFile('reference-overlay',overlay);
  }
  const report=await page.evaluate(inspectRuntime);
  // Exercise the actual labelled controls, including independent accessories and replay.
  const live=await browser.newPage({viewport:{width:1000,height:760}});
  live.on('pageerror',e=>errors.push(e.message));
  await live.goto(pathToFileURL(path.join(out,'preview.html')).href);
  await live.evaluate(async()=>{window.v=await window.visitorReady;});
  const defaultSettings=await live.evaluate(()=>({cameraPosition:v.camera.position.toArray(),
    projectionMatrix:v.camera.projectionMatrix.toArray(),expression:document.querySelector('#face').value,
    motion:document.querySelector('#motion').value}));
  const defaultBytes=await live.screenshot();
  await fs.writeFile(path.join(qa,'default-view.png'),defaultBytes);
  captures.push({file:'default-view.png',sha256:sha(defaultBytes),artifactSha256,
    viewport:{width:1000,height:760},...defaultSettings});
  await live.locator('#motion').selectOption('wave');await live.locator('#face').selectOption('wink');
  await live.locator('#pack').uncheck();await live.locator('#watch').uncheck();
  report.controls=await live.evaluate(()=>({waveSelected:document.querySelector('#motion').value==='wave',
    winkSelected:document.querySelector('#face').value==='wink',accessoriesHidden:v.meshes.filter(m=>['Backpack','Watch'].includes(m.userData.partSlot)).every(m=>!m.visible)}));
  await live.locator('#reset').click();report.controls.reset=await live.evaluate(()=>v.meshes.every(m=>m.visible)&&document.querySelector('#face').value==='default');
  await live.locator('#motion').selectOption('walk');
  await live.waitForFunction(()=>v.frame()>.13);
  await live.locator('#play').click();
  const held=await live.evaluate(()=>v.frame());
  await live.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  report.controls.pause=await live.evaluate(t=>Math.abs(v.frame()-t)<.002,held);
  await live.locator('#play').click();await live.waitForFunction(t=>Math.abs(v.frame()-t)>.03,held);
  report.controls.resume=true;
  if(playAll){
    report.continuousPlayback=[];
    await live.locator('#face').selectOption('default');
    for(const clip of Object.keys(c)){
      await live.locator('#motion').selectOption(clip);
      const duration=await live.evaluate(name=>v.clips.get(name).duration,clip);
      await live.waitForFunction(d=>v.frame()>=d*.8,duration,{timeout:90000});
      const frame=await live.evaluate(()=>v.frame());
      const bytes=await live.screenshot();
      const file='play-'+clip+'.png';await fs.writeFile(path.join(qa,file),bytes);
      captures.push({file,sha256:sha(bytes),artifactSha256,clip,frameSeconds:frame,
        automaticPlayback:true,viewport:{width:1000,height:760}});
      if(c[clip].loop){
        await live.waitForFunction(d=>v.frame()<d*.3,duration,{timeout:90000});
        const wrapped=await live.evaluate(()=>v.frame());
        report.continuousPlayback.push({clip,duration,observedLateFrame:frame,wrappedFrame:wrapped,
          pass:frame>=duration*.8&&wrapped<duration*.3});
      }else{
        await live.waitForFunction(d=>v.frame()>=d*.999,duration,{timeout:90000});
        const end=await live.evaluate(()=>v.frame());
        await live.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
        const heldEnd=await live.evaluate(()=>v.frame());
        report.continuousPlayback.push({clip,duration,observedLateFrame:frame,end,heldEnd,
          pass:Math.abs(end-duration)<.002&&Math.abs(heldEnd-end)<.002});
      }
    }
    report.checks.continuousPlayback=report.continuousPlayback.length===12&&report.continuousPlayback.every(c=>c.pass);
  }
  await live.setViewportSize({width:390,height:844});
  report.controls.mobile=await live.evaluate(()=>document.body.scrollWidth<=innerWidth&&document.querySelector('canvas').getBoundingClientRect().height>240);
  await live.close();
  if(blockoutPreview){
    await open(blockoutPreview,path.join(out,'checkpoints/01-blockout.glb'));
    await sheet('blockout','Proportion blockout',[0,35,90,180].map(deg=>({label:deg+'°',deg,clay:true})),4,225,320);
  }
  report.artifactSha256=artifactSha256;
  report.browser=browser.version();report.consoleErrors=errors;report.consoleWarnings=[...new Set(warnings)];report.failedRequests=requests;
  report.pass=Object.values(report.checks).every(Boolean)&&Object.values(report.controls).every(Boolean)&&!errors.length&&!requests.length;
  await fs.writeFile(path.join(qa,'runtime.json'),JSON.stringify(report,null,2)+'\n');
  await fs.writeFile(path.join(qa,'captures.json'),JSON.stringify({artifactSha256,
    previewSha256:sha(previewBytes),browser:browser.version(),rendererSourceSha256:sha(await fs.readFile(new URL('../preview/viewer.js',import.meta.url))),
    rendererSource:'preview/viewer.js',captureSource:'qa/render.mjs',
    captureSourceSha256:sha(await fs.readFile(new URL('./render.mjs',import.meta.url))),
    lighting:'Pinned viewer.js source, unchanged between baseline and revised captures',
    referenceProjection:'Reconstructed orthographic front alignment from sole/crown; original camera unknown',
    referenceSha256:reference?sha(await fs.readFile(reference)):null,
    artifacts:[...artifacts.values()],captures},null,2)+'\n');
  console.log(JSON.stringify({pass:report.pass,checks:report.checks,controls:report.controls,
    continuousPlayback:report.continuousPlayback??'NOT_RUN',warnings:report.consoleWarnings}));
  if(!report.pass)process.exitCode=1;
}finally{await browser.close();}

