// Additional negative/boundary coverage. Existing test-game-ux.mjs stays unchanged.
// CDP is used only to create gestures absent from Playwright's native tap API.
// All action buttons are activated through native Locator.tap()/keyboard input.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import { chromium } from 'playwright';
import { serveBuild, launchOptions, gameReady, readGame } from './browser-test-utils.mjs';
const out = process.env.TEST_ARTIFACT_DIR || 'output/game-power-touch-scope';
await fs.mkdir(out, { recursive: true });
const server = await serveBuild(), browser = await chromium.launch(launchOptions), results = [];
async function run(name, fn) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true, serviceWorkers: 'block' });
  const page = await context.newPage(), errors = [];
  page.on('pageerror', e => errors.push(e.message));
  const result = { name, status: 'FAIL' };
  try { await gameReady(page, server.url); await fn(page, context); assert.deepEqual(errors, []); result.status = 'PASS'; console.log('PASS', name); }
  catch (error) { result.error = error.stack; console.error('FAIL', name, error.message); await page.screenshot({ path: path.join(out, `${name}-failure.png`), fullPage: true }).catch(() => {}); }
  finally { result.pageErrors = errors; results.push(result); await context.close(); await fs.writeFile(path.join(out, 'results.json'), JSON.stringify({ browser: browser.version(), scope: 'Desktop Chromium touch emulation, not physical-device verification', results }, null, 2)); }
}
async function startAiming(page) {
  await page.locator('[data-action="new"]').first().tap();
  await page.waitForFunction(() => JSON.parse(window.render_game_to_text()).phase === 'placing');
  await page.locator('[data-action="place"]').tap();
  await page.waitForFunction(() => !document.querySelector('#power-handle').disabled);
}
try {
  await run('power-touch-scope-and-disposal', async page => {
    await startAiming(page);
    await page.evaluate(()=>{window.powerTouchScope=[];document.addEventListener('touchstart',e=>window.powerTouchScope.push({handle:!!e.target.closest('#power-handle'),prevented:e.defaultPrevented}),{passive:true});});
    const before=await readGame(page);await page.locator('#power-handle').tap();
    assert.equal((await readGame(page)).committedShots,before.committedShots,'native handle tap without pull never shoots');
    await page.locator('[data-action="aim-left"]').tap();
    const observations=await page.evaluate(()=>window.powerTouchScope);
    assert.ok(observations.some(x=>x.handle&&x.prevented),'actual handle touch cancels browser gesture');
    assert.ok(observations.some(x=>!x.handle&&!x.prevented),'ordinary button touch is not canceled');
    for(let cycle=0;cycle<3;cycle++){
      // Synthetic events verify only listener lifecycle, never activate controls.
      await page.evaluate(()=>{window.oldPowerHandle=document.querySelector('#power-handle');});
      assert.equal(await page.evaluate(()=>{const e=new Event('touchstart',{bubbles:true,cancelable:true});window.oldPowerHandle.querySelector('span').dispatchEvent(e);return e.defaultPrevented;}),true,'label descendant is covered');
      assert.equal(await page.evaluate(()=>{const e=new Event('touchstart',{bubbles:true,cancelable:false});window.oldPowerHandle.dispatchEvent(e);return e.defaultPrevented;}),false,'noncancelable event remains uncanceled');
      await page.locator('#demo-breadcrumb a[data-page="demos"]').click();
      await page.waitForFunction(()=>!document.querySelector('#demos-page').hidden);
      assert.equal(await page.evaluate(()=>{if(window.oldPowerHandle.isConnected)throw Error('old handle connected');const e=new Event('touchstart',{bubbles:true,cancelable:true});window.oldPowerHandle.dispatchEvent(e);return e.defaultPrevented;}),false,'AbortSignal releases old handle listener');
      await page.locator('.demo-card[data-demo-id="game"] a').first().click();
      await page.waitForFunction(()=>window.render_game_to_text&&JSON.parse(window.render_game_to_text()).ready);
    }
  });
} finally { await browser.close(); await server.close(); }
if(results.some(r=>r.status!=='PASS'))process.exitCode=1;
