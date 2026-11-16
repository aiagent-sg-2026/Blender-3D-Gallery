// Focused production-page smoke check, using the repository browser harness.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {createHash} from 'node:crypto';
import {chromium} from 'playwright';
import {serveBuild, launchOptions} from '../../scripts/browser-test-utils.mjs';

const server = await serveBuild();
const browser = await chromium.launch(launchOptions);
const context = await browser.newContext({viewport: {width: 1440, height: 900}, serviceWorkers: 'block'});
const page = await context.newPage();
const errors = [], failures = [], consumed = [], glbUrls = [];
const screenshot = path.join(os.homedir(), 'Documents/MallQueue/reports/arched-gateway-sign-page.png');
const sourceBytes = await fs.readFile(new URL('exports/optimized.glb', import.meta.url));
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
page.on('pageerror', e => errors.push(e.message));
page.on('console', m => {if (m.type() === 'error') errors.push(m.text());});
page.on('response', r => {
  if (r.status() >= 400) failures.push(`${r.status()} ${r.url()}`);
  // Vite fingerprints the production asset URL; identify the actual response bytes.
  if (new URL(r.url()).pathname.endsWith('.glb')) {
    glbUrls.push(new URL(r.url()).pathname);
    consumed.push(r.body().then(sha));
  }
});
await page.addInitScript(() => {
  window.assetFrames = [];
  const requestFrame = window.requestAnimationFrame.bind(window);
  let calls = 0;
  for (const type of [WebGLRenderingContext, WebGL2RenderingContext]) {
    for (const name of ['drawArrays', 'drawElements', 'drawArraysInstanced', 'drawElementsInstanced']) {
      const draw = type.prototype[name];
      if (draw) type.prototype[name] = function(...args) {calls++; return draw.apply(this, args);};
    }
  }
  window.requestAnimationFrame = callback => requestFrame(time => {
    const before = calls;
    try { callback(time); }
    finally { if (calls > before) window.assetFrames.push(calls - before); }
  });
});
try {
  await page.goto(server.url + '?model=arched-gateway-sign');
  await page.waitForFunction(() => document.querySelector('#viewport canvas') &&
    document.querySelector('#viewer-status')?.textContent === '' && window.assetFrames.some(n => n === 3),
  null, {timeout: 60000});
  assert.equal(await page.locator('#viewer-title').textContent(), 'Arched Gateway Sign');
  assert.equal(await page.locator('#viewport canvas').count(), 1);
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
  const frameCount = await page.evaluate(() => window.assetFrames.length);
  await page.locator('#viewport canvas').focus();
  await page.keyboard.press('ArrowLeft');
  await page.waitForFunction(n => window.assetFrames.length > n, frameCount);
  for (let i = 0; i < 2; i++) {
    const previous = await page.evaluate(() => window.assetFrames.length);
    await page.keyboard.press('+');
    await page.waitForFunction(n => window.assetFrames.length > n, previous);
  }
  await fs.mkdir(path.dirname(screenshot), {recursive: true});
  await page.screenshot({path: screenshot});
  const hashes = await Promise.all(consumed);
  assert.deepEqual(hashes, [sha(sourceBytes)], 'browser consumed the delivered GLB');
  const drawCalls = await page.evaluate(n => window.assetFrames.slice(n), frameCount);
  assert.ok(drawCalls.length && drawCalls.every(n => n > 0 && n <= 6));
  assert.deepEqual(errors, []);
  assert.deepEqual(failures, []);
  const report = {result: 'PASS', viewport: [1440, 900], browser: browser.version(),
    renderer: 'Chromium headless / SwiftShader', glb_sha256: hashes[0],
    glb_urls: glbUrls, draw_calls_per_frame: drawCalls, screenshot, errors, failed_responses: failures,
    limits: 'Desktop software renderer only; physical devices, complete mall and sustained performance NOT TESTED.'};
  await fs.writeFile(new URL('reports/browser.json', import.meta.url), JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify(report, null, 2));
} finally {
  await context.close();
  await browser.close();
  await server.close();
}
