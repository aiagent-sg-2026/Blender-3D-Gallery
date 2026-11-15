import assert from 'node:assert/strict';
import { chromium } from 'playwright';
import { serveBuild, launchOptions } from './browser-test-utils.mjs';

const server = await serveBuild();
const browser = await chromium.launch(launchOptions);
try {
  for (const [width, height] of [[1440, 900], [390, 844]]) {
    const context = await browser.newContext({ viewport: { width, height }, serviceWorkers: 'block' });
    await context.addInitScript(() => {
      window.clockDraws = 0;
      for (const type of [WebGLRenderingContext, WebGL2RenderingContext]) {
        for (const method of ['drawArrays', 'drawElements', 'drawArraysInstanced', 'drawElementsInstanced']) {
          const original = type.prototype[method];
          if (original) type.prototype[method] = function (...args) { window.clockDraws++; return original.apply(this, args); };
        }
      }
    });
    const page = await context.newPage();
    const errors = [], glbs = [];
    page.on('pageerror', error => { errors.push(error.message); console.error('PAGEERROR', error.message); });
    page.on('console', msg => { if (msg.type() === 'error') { errors.push(msg.text()); console.error('CONSOLE', msg.text()); } });
    page.on('response', response => { if (response.status() >= 400) console.error('HTTP', response.status(), response.url()); });
    page.on('request', request => { if (new URL(request.url()).pathname.endsWith('.glb')) glbs.push(request.url()); });
    await page.goto(server.url, { waitUntil: 'domcontentloaded' });
    await page.locator('#catalog .asset-card').first().waitFor({ state: 'attached', timeout: 90000 });
    await page.locator('#model-search').fill('New Year Countdown Clock');
    const card = page.locator('[data-asset-id="new-year-countdown-clock"]').first();
    await card.waitFor();
    assert.equal(await page.locator('canvas').count(), 0);
    assert.equal(glbs.length, 0, 'the catalog must not load 3D assets');
    await card.click();
    await page.waitForFunction(() => document.querySelector('#viewport canvas') && document.querySelector('#viewer-status')?.textContent === '' && window.clockDraws > 0, null, { timeout: 90000 });
    assert.equal(await page.locator('#viewer-title').innerText(), 'New Year Countdown Clock');
    assert.equal(new URL(page.url()).searchParams.get('model'), 'new-year-countdown-clock');
    assert.equal(glbs.length, 1);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
    const canvas = page.locator('#viewport canvas');
    const box = await canvas.boundingBox();
    assert.ok(box.width > 0 && box.height > 0);
    const before = await page.evaluate(() => window.clockDraws);
    await page.mouse.move(box.x + box.width * .45, box.y + box.height * .5);
    await page.mouse.down();
    await page.mouse.move(box.x + box.width * .65, box.y + box.height * .5, { steps: 5 });
    await page.mouse.up();
    await page.waitForFunction(n => window.clockDraws > n, before, { timeout: 30000 });
    await page.locator('#reset-view').click();
    await page.screenshot({ path: `/tmp/f03-browser-${width}.png` });
    await page.locator('#close-viewer').click();
    assert.equal(await page.locator('#viewport canvas').count(), 0);
    assert.deepEqual(errors, []);
    console.log(`PASS New Year countdown clock gallery viewer ${width}x${height}`);
    await context.close();
  }
  // The direct link must preserve a useful poster when the GLB fails and recover.
  server.setFault(({ relative }) => relative.includes('new-year-countdown-clock') && relative.endsWith('.glb') ? { status: 503 } : null);
  const context = await browser.newContext({ viewport: { width: 1024, height: 768 }, serviceWorkers: 'block' });
  const page = await context.newPage();
  await page.goto(server.url + '?model=new-year-countdown-clock', { waitUntil: 'domcontentloaded' });
  await page.getByRole('button', { name: /retry/i }).waitFor({ timeout: 90000 });
  assert.match(await page.locator('#viewer-status').innerText(), /3D view unavailable/i);
  assert.equal(await page.locator('#viewer-poster').isVisible(), true);
  assert.equal(await page.locator('#viewer-poster').getAttribute('alt'), 'New Year Countdown Clock reference preview');
  server.setFault(null);
  await page.getByRole('button', { name: /retry/i }).click();
  await page.waitForFunction(() => document.querySelector('#viewport canvas') && document.querySelector('#viewer-status')?.textContent === '', null, { timeout: 90000 });
  assert.equal(await page.locator('#viewer-poster').isVisible(), false);
  await context.close();
  console.log('PASS New Year countdown clock direct-link fallback and retry');
} finally {
  await browser.close();
  await server.close();
}
