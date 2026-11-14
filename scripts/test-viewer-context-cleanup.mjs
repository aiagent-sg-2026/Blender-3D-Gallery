import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {chromium,webkit} from 'playwright';
import {serveBuild,launchOptions} from './browser-test-utils.mjs';
const catalog=JSON.parse(await fs.readFile('models/catalog.json','utf8'));
const fish=catalog.collections.find(c=>c.id==='singapore-fish').assets.map(a=>a.id);
const species=JSON.parse(await fs.readFile('models/singapore-fish/species.json','utf8'));
assert.ok(species.length>0,'Fish authoring registry must not be empty');
assert.deepEqual(fish,species.map(([slug])=>'fish-'+slug),'Runtime fish must match the authoring registry');
const ids=['pool-table','proton-saga-1985',...fish];const results=[];
const server=await serveBuild();
try{
 for(const [name,engine]of [['chromium',chromium],['webkit',webkit]]){
  const browser=await engine.launch(name==='chromium'?launchOptions:{headless:true});
  const context=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,serviceWorkers:'block'});
  const page=await context.newPage();const errors=[],cspWarnings=[];
  page.on('pageerror',e=>errors.push(e.message));
  page.on('console',m=>{if(m.type()!=='error')return;if(name==='webkit'&&m.text()==="Refused to apply a stylesheet because its hash, its nonce, or 'unsafe-inline' does not appear in the style-src directive of the Content Security Policy.")cspWarnings.push(m.text());else errors.push(m.text());});
  // Hold native handles so the resource budget cannot pass merely because GC ran.
  await page.addInitScript(()=>{window.viewerContexts=[];const original=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(type,...args){const gl=original.call(this,type,...args);if(gl&&/webgl/.test(type)&&!window.viewerContexts.includes(gl)){window.viewerContexts.push(gl);window.viewerGPU={};for(const kind of ['Buffer','Texture','Program','Framebuffer','Renderbuffer','VertexArray']){const create='create'+kind,remove='delete'+kind;if(!gl[create])continue;const objects=new Set();window.viewerGPU[kind]=objects;const make=gl[create].bind(gl),drop=gl[remove].bind(gl);gl[create]=(...a)=>{const o=make(...a);if(o)objects.add(o);return o;};gl[remove]=(o,...a)=>{objects.delete(o);return drop(o,...a);};}}return gl;};});
  try{
   await page.goto(server.url);await page.bringToFront();
   let warmedGPU;const gpuSnapshots=[];
   for(const id of ids){
    console.log('OPEN',name,id);
    await page.locator(`a[data-asset-id="${id}"]`).first().tap();
    await page.waitForFunction(()=>document.querySelector('#viewport canvas')&&document.querySelector('#viewer-status')?.textContent==='').catch(async error=>{console.log('FAILED_STATE',name,id,await page.locator('#viewer-status').textContent(),errors);throw error;});
    assert.equal(await page.evaluate(()=>window.viewerContexts.length),1,'Repeated model opens must reuse one native context');
    assert.ok(await page.evaluate(()=>!window.viewerContexts[0].isContextLost()),'Opened model needs a live native context');
    await page.locator('#close-viewer').tap();
    await page.waitForFunction(()=>window.viewerContexts.length===1&&window.viewerContexts[0].drawingBufferWidth<=2&&window.viewerContexts[0].drawingBufferHeight<=2,null,{timeout:3000});
    // Stay below WebKit's history mutation rate limit while stress-switching.
    await page.waitForTimeout(500);
    assert.equal(await page.locator('#viewport canvas').count(),0);
    const gpu=await page.evaluate(()=>Object.fromEntries(Object.entries(window.viewerGPU).map(([kind,objects])=>[kind,objects.size])));gpuSnapshots.push({id,...gpu});
    if(id===fish[0])warmedGPU=gpu;
    if(warmedGPU)for(const kind of Object.keys(gpu))assert.ok(gpu[kind]<=warmedGPU[kind],`${name} ${id} retains ${kind}: ${gpu[kind]} > ${warmedGPU[kind]}`);
   }
   assert.deepEqual(errors,[]);const count=await page.evaluate(()=>window.viewerContexts.length);assert.equal(count,1);
   results.push({engine:name,models:ids.length,contexts:count,oneReusableContext:true,idleFramebufferPixelsAtMost:4,errors,cspWarnings:cspWarnings.length,gpuSnapshots});console.log(`PASS ${name}: ${ids.length} models reuse one native context; idle framebuffer shrinks; no context-limit errors`);
  }finally{await context.close();await browser.close();}
 }
 await fs.writeFile('docs/verification/viewer-context-cleanup.json',JSON.stringify(results,null,2)+'\n');
}finally{await server.close();}
