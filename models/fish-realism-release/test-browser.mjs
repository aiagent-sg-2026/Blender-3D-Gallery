import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {chromium,webkit} from 'playwright';
import {serveBuild, launchOptions} from '../../scripts/browser-test-utils.mjs';
const manifest=JSON.parse(await fs.readFile('models/fish-realism-release/releases.json'));
const server=process.env.FISH_LIVE_URL?{url:process.env.FISH_LIVE_URL,close:async()=>{}}:await serveBuild();
const results=[];
for(const engine of (process.env.FISH_ENGINE?[process.env.FISH_ENGINE]:['chromium','webkit'])) {
 const browser=await ({chromium,webkit}[engine]).launch(engine==='chromium'?launchOptions:{headless:true});
 try { for(const slug of Object.keys(manifest.models)) {
 const asset=path.resolve(`models/fish-realism-release/${slug}/model.glb`);
 const artifactHash=crypto.createHash('sha256').update(await fs.readFile(asset)).digest('hex');
const directory=`output/playwright/fish-realism-release/${process.env.FISH_LIVE_URL?'live':'local'}/${engine}/${slug}`;await fs.mkdir(directory,{recursive:true});

for(const width of [1440,390]) {
  const errors=[],nativeSelectWarnings=[];let served=0;
  const context=await browser.newContext({viewport:{width,height:900},isMobile:width===390,hasTouch:width===390,reducedMotion:'reduce',serviceWorkers:'block'});
  context.on('response',async response=>{
    if(!new URL(response.url()).pathname.endsWith('.glb'))return;
    try { const body=await response.body(); if(crypto.createHash('sha256').update(body).digest('hex')===artifactHash)served++; } catch {}
  });
  const page=await context.newPage();await page.addInitScript(()=>{window.fishCsp=[];document.addEventListener('securitypolicyviolation',e=>window.fishCsp.push({directive:e.effectiveDirective,target:e.target?.id,capture:window.fishCapture===true}));});page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error'){if(engine==='webkit'&&m.text()==="Refused to apply a stylesheet because its hash, its nonce, or 'unsafe-inline' does not appear in the style-src directive of the Content Security Policy.")nativeSelectWarnings.push(m.text());else errors.push(m.text());}});
  await page.goto(server.url+`?model=fish-${slug}`);
  const button=page.locator('[data-fish-playback]');await button.waitFor({timeout:60000});await page.waitForFunction(()=>document.querySelector('#viewport canvas')&&document.querySelector('#viewer-status')?.textContent==='',{timeout:60000});await page.waitForTimeout(150);assert.ok(served>0,'Expected released GLB bytes were not loaded');
  assert.equal(await button.getAttribute('aria-pressed'),'false');await page.waitForTimeout(250);
  const canvas=page.locator('#viewport canvas');
  // WebKit's Playwright screenshot preparation injects `body {}` to sync
  // animation. Production CSP correctly blocks it; scope this known harness
  // event to captures rather than weakening the site's policy.
  const capture=async locator=>{await page.evaluate(()=>window.fishCapture=true);try{return await locator.screenshot({caret:'initial'});}finally{await page.waitForTimeout(50);await page.evaluate(()=>window.fishCapture=false);}};
const still=await capture(canvas);await page.waitForTimeout(150);assert.ok(still.equals(await capture(canvas)),'Paused canvas drifted');
  await button.click();await page.waitForTimeout(500);await button.click();await page.waitForTimeout(100);const moved=await capture(canvas);assert.ok(!still.equals(moved),'Swimming did not visibly change the real canvas');await page.waitForTimeout(150);assert.ok(moved.equals(await capture(canvas)),'Pause failed');
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);assert.deepEqual(errors,[]);const csp=await page.evaluate(()=>window.fishCsp);assert.ok(csp.every(v=>engine==='webkit'&&((v.directive==='style-src-elem'&&v.capture&&!v.target)||(v.directive==='style-src-attr'&&['model-theme','model-category','model-collection','model-feature','demo-category'].includes(v.target)))),JSON.stringify(csp));
  const screenshot=`${directory}/${width===1440?'desktop':'mobile'}.png`;await page.screenshot({path:screenshot,caret:'initial'});
  await page.keyboard.press('Escape');assert.equal(await page.locator('[data-fish-playback]').count(),0);
  results.push({slug,engine,width,height:900,loaded_release_sha256:artifactHash,native_select_csp_warnings:nativeSelectWarnings.length,csp_events:csp,paused_stable:true,visible_swim_change:true,resumed_then_paused:true,no_horizontal_overflow:true,no_page_errors:true,viewer_disposed:true,screenshot});await context.close();
 }
 console.log('PASS release',engine,slug);
 } } finally {await browser.close();}
}
await fs.writeFile(`models/fish-realism-release/${process.env.FISH_LIVE_URL?'live':'local'}-${process.env.FISH_ENGINE||'all'}-browser-verification.json`,JSON.stringify({mode:'actual_catalog_no_substitution',mobile:'emulated viewport, not physical hardware',results},null,2)+'\n');
await server.close();
