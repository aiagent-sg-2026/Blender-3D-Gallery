import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import { chromium } from 'playwright';
import { serveBuild, launchOptions } from '../../scripts/browser-test-utils.mjs';
const server=await serveBuild();const browser=await chromium.launch(launchOptions);
const errors=[];const results=[];
try{
 for(const width of [1440,390]){
  const context=await browser.newContext({viewport:{width,height:900},reducedMotion:'reduce',serviceWorkers:'block'});const page=await context.newPage();
  page.on('console',message=>{if(message.type()==='error')errors.push(message.text())});
  page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)errors.push(`${r.status()} ${r.url()}`)});
  const slugs=width===1440?['barramundi','stingray','swamp-eel','reef-shark','pufferfish','betta','lionfish','guppy']:['stingray'];
  for(const slug of slugs){
   await page.goto(server.url+`?model=fish-${slug}`);
   const button=page.locator('[data-fish-playback]');await button.waitFor();
   await page.waitForFunction(()=>document.querySelector('#viewport canvas')&&document.querySelector('#viewer-status')?.textContent==='');
   assert.equal(await button.getAttribute('aria-pressed'),'false','Reduced motion must start paused');
   await page.waitForTimeout(250);
   const canvas=page.locator('#viewport canvas');const still=await canvas.screenshot();await page.waitForTimeout(200);assert.ok(still.equals(await canvas.screenshot()),'Paused skin changed');
   await button.click();assert.equal(await button.getAttribute('aria-pressed'),'true');await page.waitForTimeout(450);await button.click();await page.waitForTimeout(100);
   const moved=await canvas.screenshot();assert.ok(!still.equals(moved),`${slug} did not visibly animate`);
   await page.waitForTimeout(200);assert.ok(moved.equals(await canvas.screenshot()),'Pause did not stop motion');
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
   await page.screenshot({path:`models/singapore-fish/swim-${slug}-${width}.png`});
   await page.keyboard.press('Escape');assert.equal(await page.locator('[data-fish-playback]').count(),0,'Playback controls leaked');
   results.push({slug,width,paused_stable:true,resumed_skin_changed:true,closed_controls_removed:true});console.log('PASS swim',slug,width);
  }
  if(width===1440){
   await page.emulateMedia({reducedMotion:'no-preference'});await page.goto(server.url+'?model=fish-koi');await page.locator('[data-fish-playback]').waitFor();assert.equal(await page.locator('[data-fish-playback]').getAttribute('aria-pressed'),'true');
   await page.emulateMedia({reducedMotion:'reduce'});await page.waitForFunction(()=>document.querySelector('[data-fish-playback]')?.getAttribute('aria-pressed')==='false');
  }
  await context.close();
 }
 assert.deepEqual(errors,[]);await fs.writeFile('models/singapore-fish/swim-browser-validation.json',JSON.stringify({results,errors,default_autoplay:true,live_reduced_motion:true},null,2)+'\n');
 console.log('PASS: desktop/mobile visible swimming, pause/resume, reduced motion, autoplay and cleanup.');
}finally{await browser.close();await server.close();}
