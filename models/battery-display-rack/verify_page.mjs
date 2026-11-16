import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { chromium } from 'playwright';
import { serveBuild, launchOptions } from '../../scripts/browser-test-utils.mjs';

const dir = new URL('.', import.meta.url);
const output = process.env.MALL_REPORT_DIR ?? path.join(os.homedir(), 'Documents/MallQueue/reports');
await fs.mkdir(output, { recursive: true });
const screenshot = path.join(output, 'battery-display-rack-page.png');
const expected = JSON.parse(await fs.readFile(new URL('reports/assets.json', dir), 'utf8'));
const server = await serveBuild();
const browser = await chromium.launch(launchOptions);
const errors = [], requests = [];
try {
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, serviceWorkers: 'block' });
  await context.addInitScript(() => {
    window.qaDrawCalls = 0;
    for (const type of [WebGLRenderingContext, WebGL2RenderingContext]) {
      for (const name of ['drawArrays', 'drawElements', 'drawArraysInstanced', 'drawElementsInstanced']) {
        const original = type.prototype[name];
        if (original) type.prototype[name] = function (...args) {
          window.qaDrawCalls++;
          return original.apply(this, args);
        };
      }
    }
  });
  const page = await context.newPage();
  page.on('requestfailed', request => errors.push(`${request.method()} ${request.url()} ${request.failure()?.errorText}`));
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
  page.on('response', response => { if (response.status() >= 400) errors.push(`${response.status()} ${response.url()}`); });
  page.on('request', request => { if (new URL(request.url()).pathname.endsWith('.glb')) requests.push(request.url()); });
  const responsePromise = page.waitForResponse(response => new URL(response.url()).pathname.endsWith('.glb'));
  await page.goto(server.url + '?model=battery-display-rack', { waitUntil: 'domcontentloaded' });
  const response = await responsePromise;
  const loadedHash = createHash('sha256').update(await response.body()).digest('hex');
  assert.equal(loadedHash, expected.sha256, 'Browser consumes the validated GLB');
  await page.waitForFunction(() => document.querySelector('#viewport canvas') &&
    document.querySelector('#viewer-status')?.textContent === '' && window.qaDrawCalls > 0 &&
    !document.querySelector('#reset-view').disabled, null, { timeout: 60000 });
  assert.equal(await page.locator('#viewer-title').textContent(), 'Battery Display Rack');
  assert.equal(await page.locator('#viewer').evaluate(node => node.open), true);
  assert.equal(await page.locator('#viewport canvas').count(), 1);
  assert.equal(await page.locator('#viewer-poster').isVisible(), false);
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
  const canvas = page.locator('#viewport canvas');
  const initial = await canvas.screenshot();
  await canvas.focus();
  await page.keyboard.press('ArrowRight');
  await page.keyboard.press('+');
  const orbited = await canvas.screenshot();
  assert.notDeepEqual(orbited, initial, 'Actual WebGL view responds to orbit and zoom');
  const drawsBeforeReset = await page.evaluate(() => window.qaDrawCalls);
  await page.locator('#reset-view').click();
  await page.waitForFunction(before => window.qaDrawCalls > before, drawsBeforeReset);
  await page.screenshot({ path: screenshot });
  assert.deepEqual(errors, []);
  assert.equal(requests.length, 1, 'Only the selected model is fetched');
  await page.keyboard.press('Escape');
  assert.equal(await page.locator('#viewport canvas').count(), 0, 'Viewer disposes on close');
  await page.goto(server.url + '?page=models&q=battery');
  assert.equal(await page.locator('#catalog .asset-card').count(), 1);
  assert.equal(await page.locator('#catalog .asset-card').evaluateAll(cards =>
    cards.map(card => card.querySelector('[data-asset-id]').dataset.assetId)).then(ids => ids[0]), 'battery-display-rack');
  const report = {
    result: 'PASS', viewport: [1440, 900], screenshot,
    glb_sha256: loadedHash, console_errors: errors, glb_requests: requests.length,
    checks: ['Direct model route', 'Validated GLB identity', 'Real WebGL draws', 'Orbit and zoom',
      'Reset redraw', 'Viewer disposal', 'Catalog search membership', 'No horizontal overflow'],
  };
  await fs.writeFile(new URL('reports/browser.json', dir), JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify(report, null, 2));
  await context.close();
} finally {
  await browser.close();
  await server.close();
}
