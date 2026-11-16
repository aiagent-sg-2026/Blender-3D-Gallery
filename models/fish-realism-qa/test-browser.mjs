import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {chromium} from 'playwright';
import {serveBuild} from '../../scripts/browser-test-utils.mjs';
import {fishLaunchOptions,fishBrowserRuntime} from './browser-runtime.mjs';
const slug=process.argv[2];assert.match(slug,/^[a-z0-9-]+$/);
const asset=path.resolve(`models/fish-realism-qa/${slug}/model.glb`);
const artifactHash=crypto.createHash('sha256').update(await fs.readFile(asset)).digest('hex');
const original=await fs.readFile(`models/singapore-fish/${slug}/exports/model.glb`);const originalHash=crypto.createHash('sha256').update(original).digest('hex');const matches=[];
for(const name of await fs.readdir('dist/assets')) {
 if(!name.endsWith('.glb'))continue;const file=`dist/assets/${name}`;if((await fs.stat(file)).size!==original.length)continue;
 if(crypto.createHash('sha256').update(await fs.readFile(file)).digest('hex')===originalHash)matches.push(name);
}
assert.equal(matches.length,1,'Cannot identify the built gallery asset by its exact original bytes');const compiledName=matches[0];
const directory=`output/playwright/fish-realism-qa/${slug}`;await fs.mkdir(directory,{recursive:true});
const server=await serveBuild();const browser=await chromium.launch(fishLaunchOptions);const results=[];
try {
 for(const width of [1440,390]) {
  const errors=[];let served=0;
  const context=await browser.newContext({viewport:{width,height:900},reducedMotion:'reduce',serviceWorkers:'block'});
  // Exercise the existing gallery viewer while substituting only this draft GLB.
  await context.route(`**/${compiledName}*`,async route=>{served++;await route.fulfill({path:asset,contentType:'model/gltf-binary'});});
  const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
  await page.goto(server.url+`?model=fish-${slug}`);
  const button=page.locator('[data-fish-playback]');await button.waitFor({timeout:60000});await page.waitForFunction(()=>document.querySelector('#viewport canvas')&&document.querySelector('#viewer-status')?.textContent==='',{timeout:60000});assert.ok(served>0,'Draft GLB was not requested');
  assert.equal(await button.getAttribute('aria-pressed'),'false');await page.waitForTimeout(250);
  const canvas=page.locator('#viewport canvas');const still=await canvas.screenshot();await page.waitForTimeout(150);assert.ok(still.equals(await canvas.screenshot()),'Paused canvas drifted');
  await button.click();await page.waitForTimeout(500);await button.click();await page.waitForTimeout(100);const moved=await canvas.screenshot();assert.ok(!still.equals(moved),'Swimming did not visibly change the real canvas');await page.waitForTimeout(150);assert.ok(moved.equals(await canvas.screenshot()),'Pause failed');
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);assert.deepEqual(errors,[]);
  const screenshot=`${directory}/${width===1440?'desktop':'mobile'}.png`;await page.screenshot({path:screenshot});
  await page.keyboard.press('Escape');assert.equal(await page.locator('[data-fish-playback]').count(),0);
  results.push({width,height:900,loaded_draft_sha256:artifactHash,paused_stable:true,visible_swim_change:true,resumed_then_paused:true,no_horizontal_overflow:true,no_page_errors:true,viewer_disposed:true,screenshot});await context.close();
 }
 await fs.writeFile(`models/fish-realism-qa/${slug}/browser-verification.json`,JSON.stringify({slug,mode:'existing_built_gallery_with_draft_glb_request_substitution',engine:'chromium',runtime:fishBrowserRuntime,production_files_changed:false,results},null,2)+'\n');console.log('PASS browser',slug,results.map(r=>r.width).join(','));
} finally {await browser.close();await server.close();}
