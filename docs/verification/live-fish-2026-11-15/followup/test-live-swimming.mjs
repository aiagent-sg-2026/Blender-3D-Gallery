import fs from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {chromium,webkit} from 'playwright';
const NATIVE_SELECT_WARNING="Refused to apply a stylesheet because its hash, its nonce, or 'unsafe-inline' does not appear in the style-src directive of the Content Security Policy.";
const NATIVE_SELECT_IDS=new Set(['model-theme','model-category','model-collection','demo-category']);
const OUT=new URL('./',import.meta.url);
const SMOKE=process.env.FISH_QA_SMOKE==='1';
const BASE=SMOKE?process.env.FISH_QA_SITE:'https://yapweijun1996.github.io/Blender-3D-Gallery/';
assert.ok(BASE);
const SHA='65e56ac20802cd8969fac3d9de9131e87319b96a';
const source=path=>execFileSync('git',['show',`${SHA}:${path}`],{maxBuffer:5000000});
const species=JSON.parse(source('models/singapore-fish/species.json'));
assert.equal(species.length,60);
const hash=b=>createHash('sha256').update(b).digest('hex');
const expected=new Map(species.map(([slug])=>[slug,hash(source(`models/singapore-fish/${slug}/exports/model.glb`))]));
const selected=SMOKE?species.slice(0,1):species;
const report={smoke:SMOKE,startedAt:new Date().toISOString(),site:BASE,expectedCommit:SHA,devices:[],cases:[],errors:[],warnings:[],verdict:'running'};
const save=()=>fs.writeFile(new URL(SMOKE?'smoke-animation-results.json':'animation-results.json',OUT),JSON.stringify(report,null,2)+'\n');
let caseName='preflight';
try{
 for(const config of [{name:'chromium-desktop',engine:chromium,viewport:{width:1440,height:900},mobile:false},{name:'chromium-mobile',engine:chromium,viewport:{width:390,height:844},mobile:true},{name:'webkit-mobile',engine:webkit,viewport:{width:390,height:844},mobile:true}]){
  const browser=await config.engine.launch(config.engine===chromium?{headless:true,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']}:{headless:true});
  const context=await browser.newContext({viewport:config.viewport,isMobile:config.mobile,hasTouch:config.mobile,deviceScaleFactor:1,reducedMotion:'no-preference',serviceWorkers:'block'});
  const page=await context.newPage();page.setDefaultTimeout(30000);caseName=config.name+'/preflight';
  const bodies=new Map();
  page.on('response',async r=>{if(r.url().endsWith('.glb'))bodies.set(r.url(),r.status());if(r.status()>=400)report.errors.push({case:caseName,type:'http',status:r.status(),url:r.url()});});
  page.on('pageerror',e=>report.errors.push({case:caseName,type:'page',message:e.message}));
  page.on('console',m=>{if(m.type()==='error'&&config.engine===webkit&&m.text()===NATIVE_SELECT_WARNING)report.warnings.push({case:caseName,type:'webkit-csp-classified-by-violation',message:m.text()});else if(m.type()==='error')report.errors.push({case:caseName,type:'console',message:m.text()});else if(m.type()==='warning')report.warnings.push({case:caseName,type:'console',message:m.text()});});
  await page.addInitScript(()=>{window.liveFishContexts=[];const getContext=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(type,...args){const gl=getContext.call(this,type,...args);if(gl&&/webgl/.test(type)&&!window.liveFishContexts.includes(gl))window.liveFishContexts.push(gl);return gl;};window.harnessSnapshots=0;window.liveFishCsp=[];addEventListener('securitypolicyviolation',e=>window.liveFishCsp.push({directive:e.effectiveDirective,target:e.target?.id,blocked:e.blockedURI,screenshotSequence:window.harnessSnapshots}));window.liveFishFrames=0;const raf=requestAnimationFrame;window.requestAnimationFrame=callback=>raf(t=>{window.liveFishFrames++;callback(t)});});
  const verifyCsp=async()=>{const entries=await page.evaluate(()=>window.liveFishCsp);for(const v of entries)assert.ok(config.engine===webkit&&v.blocked==='inline'&&((v.directive==='style-src-attr'&&NATIVE_SELECT_IDS.has(v.target))||(v.directive==='style-src-elem'&&v.screenshotSequence>0)),'Unexpected CSP violation '+JSON.stringify(v));assert.ok(entries.filter(v=>v.directive==='style-src-elem').length<=await page.evaluate(()=>window.harnessSnapshots),'More blocked styles than tool screenshot injections');return entries;};
  const snapshot=async options=>{await page.evaluate(()=>window.harnessSnapshots++);return page.screenshot(options);};
  try{
   await page.goto(BASE,{waitUntil:'networkidle'});await page.bringToFront();
   const buildStart=await page.evaluate(()=>fetch('./build-info.json',{cache:'no-store'}).then(r=>r.json()));
   assert.equal(await page.locator('#model-collection option[value="singapore-fish"]').count(),1,'Fish release is not live');
   await page.locator('#model-collection').selectOption('singapore-fish');
   assert.equal(await page.locator('#catalog .asset-card').count(),60);
   assert.equal(bodies.size,0,'Index eagerly downloaded GLBs');
   report.devices.push({name:config.name,viewport:config.viewport,mobileTouch:config.mobile,buildStart,fishCards:60,indexLazy:true,indexCsp:await verifyCsp()});
   const activate=async locator=>config.mobile?locator.tap():locator.click();
   const cdp=config.engine===chromium&&config.mobile?await context.newCDPSession(page):null;
   for(const [index,[slug]]of selected.entries()){
    caseName=`${config.name}/${slug}`;const result={device:config.name,fishId:`FISH-${String(index+1).padStart(3,'0')}`,slug,status:'running'};report.cases.push(result);
    const errorCount=report.errors.length;await save();
    try{
     await activate(page.locator(`a[data-asset-id="fish-${slug}"]`).first());
     const button=page.locator('[data-fish-playback]');await button.waitFor();
     await page.waitForFunction(()=>document.querySelector('#viewport canvas')&&document.querySelector('#viewer-status')?.textContent==='');
     assert.equal(await button.getAttribute('aria-pressed'),'true','Default autoplay disabled');
     result.stage='autoplay-snapshot';await save();const canvas=page.locator('#viewport canvas');const capture=async()=>{await canvas.evaluate(e=>e.scrollIntoView({behavior:'instant',block:'center'}));const box=await canvas.boundingBox();assert.ok(box);return snapshot({clip:box,animations:'disabled',timeout:15000});};const autoFrame=await capture();const startFrames=await page.evaluate(()=>window.liveFishFrames);await page.waitForTimeout(350);
     const file=await page.locator('#viewer-download').getAttribute('href');const url=new URL(file,page.url()).href;
     assert.equal(bodies.get(url),200,'Browser GLB request did not succeed');result.stage='verify-deployed-asset';await save();const verifiedResponse=await fetch(url,{signal:AbortSignal.timeout(30000)});assert.equal(verifiedResponse.status,200);const bytes=Buffer.from(await verifiedResponse.arrayBuffer());assert.ok(bytes.length>1000,'Missing deployed GLB bytes');assert.equal(hash(bytes),expected.get(slug),'Live GLB differs from verified release');result.glbSha256=hash(bytes);
     await activate(button);await page.waitForTimeout(120);assert.equal(await button.getAttribute('aria-pressed'),'false');
     const before=await capture();assert.ok(!autoFrame.equals(before),'Autoplay did not visibly change the pose');result.autoplay=true;result.rafCallbacksDuringAutoplay=await page.evaluate(n=>window.liveFishFrames-n,startFrames);await save();
     await activate(button);await page.waitForTimeout(430);await activate(button);await page.waitForTimeout(120);const after=await capture();
     assert.ok(!before.equals(after),'No visible swimming pose change');result.visibleSwimming=true;
     const frozen=await page.evaluate(()=>window.liveFishFrames);await page.waitForTimeout(250);assert.ok(after.equals(await capture()),'Paused pose is unstable');
     result.pausedRafCallbacks=await page.evaluate(n=>window.liveFishFrames-n,frozen);result.pauseStable=true;
     assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'Horizontal document overflow');
     if(config.mobile){const box=await button.boundingBox();assert.ok(box&&box.width>=44&&box.height>=44,'Playback touch target too small');result.touchPlayback=true;}
     if(cdp&&['barramundi','stingray','betta','swamp-eel'].includes(slug)){
      await canvas.scrollIntoViewIfNeeded();const box=await canvas.boundingBox();const x=box.x+box.width*.5,y=box.y+box.height*.5;
      const pre=await capture();await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x,y,id:1}]});
      for(let j=1;j<=6;j++)await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:x+10*j,y:y+2*j,id:1}]});
      await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await page.waitForTimeout(350);assert.ok(!pre.equals(await capture()),'Touch orbit did not change the view');result.touchOrbit=true;
      await activate(page.locator('#reset-view'));await page.waitForTimeout(350);
     }
     if(['barramundi','stingray','betta','swamp-eel','reef-shark'].includes(slug)){
      await fs.writeFile(new URL(`${config.name}-${slug}-pose-a.png`,OUT),before);await fs.writeFile(new URL(`${config.name}-${slug}-pose-b.png`,OUT),after);
      await snapshot({path:new URL(`${config.name}-${slug}.png`,OUT).pathname});
     }
     await activate(page.locator('#close-viewer'));assert.equal(await page.locator('[data-fish-playback]').count(),0);assert.equal(await page.locator('#viewport canvas').count(),0);await page.waitForFunction(()=>window.liveFishContexts.length===1&&!window.liveFishContexts[0].isContextLost()&&window.liveFishContexts[0].drawingBufferWidth<=2&&window.liveFishContexts[0].drawingBufferHeight<=2,null,{timeout:3000});result.closedCleanly=true;result.oneReusableContext=true;result.idleFramebufferTiny=true;
     result.csp=await verifyCsp();assert.equal(report.errors.length,errorCount,'Runtime errors recorded during this case');result.stage='complete';result.status='pass';
    }catch(e){result.status='fail';result.error=e.message;await snapshot({path:new URL(`${config.name}-${slug}-failure.png`,OUT).pathname}).catch(()=>{});if(await page.locator('#viewer').evaluate(e=>e.open).catch(()=>false))await page.locator('#close-viewer').click().catch(()=>{});}
    console.log(result.status,caseName);await save();
   }
   caseName=`${config.name}/reduced-motion`;
   await page.emulateMedia({reducedMotion:'reduce'});await page.goto(BASE+'?model=fish-barramundi');const b=page.locator('[data-fish-playback]');await b.waitFor();assert.equal(await b.getAttribute('aria-pressed'),'false');
   await activate(b);assert.equal(await b.getAttribute('aria-pressed'),'true');await activate(b);
   await page.emulateMedia({reducedMotion:'no-preference'});await page.waitForFunction(()=>document.querySelector('[data-fish-playback]')?.getAttribute('aria-pressed')==='true');
   await page.emulateMedia({reducedMotion:'reduce'});await page.waitForFunction(()=>document.querySelector('[data-fish-playback]')?.getAttribute('aria-pressed')==='false');
   const device=report.devices.at(-1);device.reducedMotion=true;device.finalCsp=await verifyCsp();device.buildEnd=await page.evaluate(()=>fetch('./build-info.json',{cache:'no-store'}).then(r=>r.json()));assert.deepEqual(device.buildStart,device.buildEnd,'Site changed during this device run');
  }finally{await context.close();await browser.close();}
 }
 assert.equal(report.cases.length,selected.length*3);assert.equal(report.cases.filter(c=>c.status==='pass').length,selected.length*3);assert.deepEqual(report.errors,[]);report.verdict='pass';
}catch(e){report.verdict='fail';report.failure={case:caseName,message:e.message};process.exitCode=1;}
finally{report.completedAt=new Date().toISOString();await save();console.log('FINAL',report.verdict,report.cases.filter(c=>c.status==='pass').length+'/'+report.cases.length);}
