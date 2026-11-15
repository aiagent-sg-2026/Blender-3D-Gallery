import fs from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import { chromium } from 'playwright';
const out=new URL('./',import.meta.url);
const commit='65e56ac20802cd8969fac3d9de9131e87319b96a';
const specs=JSON.parse(execFileSync('git',['show',commit+':models/singapore-fish/species.json'],{encoding:'utf8'}));
if(specs.length!==60)throw new Error('Expected exactly 60 release fish');
const base='https://yapweijun1996.github.io/Blender-3D-Gallery/';
const browser=await chromium.launch({headless:true,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const report={checkedAt:new Date().toISOString(),url:base,expectedCommit:commit,coverage:[],errors:[],verdict:'unverified'};
try{
 for(const device of [{name:'desktop',viewport:{width:1440,height:900},isMobile:false,hasTouch:false},{name:'mobile',viewport:{width:390,height:844},isMobile:true,hasTouch:true}]){
  const context=await browser.newContext({...device,deviceScaleFactor:1,serviceWorkers:'block'});const page=await context.newPage();
  page.on('pageerror',e=>report.errors.push({device:device.name,type:'page',message:e.message}));
  page.on('response',r=>{if(r.status()>=400)report.errors.push({device:device.name,type:'http',status:r.status(),url:r.url()})});
  await page.goto(base+'?model=fish-'+specs[0][0],{waitUntil:'networkidle'});
  await page.locator('#model-collection').waitFor();
  const state=await page.evaluate(async()=>({build:await fetch('./build-info.json',{cache:'no-store'}).then(r=>r.json()),totalCards:document.querySelectorAll('#catalog .asset-card').length,fishCards:document.querySelectorAll('#catalog [data-asset-id^="fish-"]').length,fishCollectionPresent:!!document.querySelector('#model-collection option[value="singapore-fish"]'),overflow:document.documentElement.scrollWidth>innerWidth}));
  const rows=[];
  for(const [i,spec]of specs.entries()){
   const id='fish-'+spec[0];
   // Exercise the production SPA's actual route handler for each requested ID.
   await page.evaluate(id=>{history.pushState({},'',`?model=${id}`);dispatchEvent(new PopStateEvent('popstate'));},id);
   await page.waitForFunction(()=>document.querySelector('#viewer')?.open||(!document.querySelector('#route-notice')?.hidden&&document.querySelector('#route-notice')?.textContent.includes('could not be found')));
   const result=await page.evaluate(()=>({notice:document.querySelector('#route-notice')?.textContent,viewerOpen:document.querySelector('#viewer')?.open,swimControls:document.querySelectorAll('[data-fish-playback]').length,canvasCount:document.querySelectorAll('#viewport canvas').length}));
   rows.push({fishId:`FISH-${String(i+1).padStart(3,'0')}`,id,english:spec[2],status:result.viewerOpen?'available_needs_animation_test':'not_published',...result});
  }
  await page.screenshot({path:new URL(`${device.name}-live.png`,out).pathname});
  report.coverage.push({device:device.name,viewport:device.viewport,state,results:rows});
  console.log(device.name,rows.length,'routes;',rows.filter(r=>r.status==='not_published').length,'not published');
  await context.close();
 }
 report.verdict=report.coverage.every(c=>c.results.every(r=>r.status==='not_published'))?'blocked_release_not_published':'needs_animation_testing';
}finally{await fs.writeFile(new URL('results.json',out),JSON.stringify(report,null,2)+'\n');await browser.close();}
console.log('VERDICT',report.verdict);
