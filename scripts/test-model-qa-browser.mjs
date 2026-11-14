import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { chromium } from 'playwright';
import { launchOptions } from './browser-test-utils.mjs';

const url = process.env.MODEL_QA_URL || 'http://127.0.0.1:5178/';
const modelId = process.env.MODEL_QA_ID || 'pool-table';
const catalog = JSON.parse(await fs.readFile('models/catalog.json', 'utf8'));
const asset = catalog.collections.flatMap(c => c.assets).find(a => a.id === modelId);
assert.ok(asset, 'Model must be present in the local validated catalog');
const expectedBytes = await fs.readFile(asset.file);
const expectedSha256 = createHash('sha256').update(expectedBytes).digest('hex');
const out = path.resolve(process.env.MODEL_QA_OUTPUT || `output/playwright/model-qa/${modelId}`);
await fs.mkdir(out, { recursive: true });
const browser = await chromium.launch(launchOptions);
const results = [];
// Mobile testing is opt-in; the owner excluded it from this QA campaign.
const viewports = [[1440, 900], [768, 1024]];
if (process.env.MODEL_QA_INCLUDE_MOBILE === '1') viewports.push([390, 844]);
try {
  for (const [width, height] of viewports) {
    const context = await browser.newContext({ viewport: { width, height }, serviceWorkers: 'block', hasTouch: width === 390 });
    await context.addInitScript(() => {
      performance.setResourceTimingBufferSize(10000);
      window.modelQA = { draws: [], rafTime: 0 };
      const requestFrame = window.requestAnimationFrame.bind(window);
      window.requestAnimationFrame = callback => requestFrame(time => {
        window.modelQA.rafTime = time;
        callback(time);
      });
      for (const type of [WebGLRenderingContext, WebGL2RenderingContext]) {
        for (const method of ['drawElements', 'drawArrays']) {
          const original = type.prototype[method];
          type.prototype[method] = function (...args) {
            window.modelQA.draws.push({ method, mode: args[0], count: method === 'drawElements' ? args[1] : args[2], time: performance.now(), rafTime: window.modelQA.rafTime });
            return original.apply(this, args);
          };
        }
      }
    });
    const page = await context.newPage();
    const errors = [], warnings = [], networkErrors = [], modelResponses = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); if (message.type() === 'warning') warnings.push(message.text()); });
    page.on('response', response => {
      if (response.status() >= 400) networkErrors.push({ url: response.url(), status: response.status() });
      if (response.request().resourceType() === 'fetch' && new URL(response.url()).pathname.endsWith('.glb')) modelResponses.push(response);
    });
    const modelUrl = new URL(url);
    modelUrl.searchParams.set('model', modelId);
    await page.goto(modelUrl.href);
    await page.waitForFunction(() => document.querySelector('#viewport canvas') && document.querySelector('#viewer-status')?.textContent === '' && window.modelQA.draws.length > 0, null, { timeout: 60000 });
    const canvas = page.locator('#viewport canvas');
    const loadedImage = await canvas.screenshot({ path: path.join(out, `${width}-loaded.png`) });
    await canvas.focus();
    const original = await canvas.screenshot({ path: path.join(out, `${width}-baseline-focused.png`) });
    await page.keyboard.press('ArrowLeft');
    await page.waitForTimeout(300);
    const rotated = await canvas.screenshot();
    assert.ok(!original.equals(rotated), 'Keyboard rotation must change the visible model');
    await page.keyboard.press('+');
    await page.waitForTimeout(300);
    const zoomed = await canvas.screenshot();
    assert.ok(!rotated.equals(zoomed), 'Keyboard zoom must change the visible model');
    if (width === 390) {
      const touch = await context.newCDPSession(page);
      const box = await canvas.boundingBox();
      const x = box.x + box.width * .5, y = box.y + box.height * .5;
      await touch.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x, y }] });
      await touch.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: x + 55, y: y + 10 }] });
      await touch.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
      await touch.detach();
      await page.waitForTimeout(350);
      assert.ok(!zoomed.equals(await canvas.screenshot()), 'Emulated touch orbit must change the visible model');
    }
    await page.getByRole('button', { name: /Reset view/ }).click();
    await page.waitForTimeout(350);
    const resetImage = await canvas.screenshot({ path: path.join(out, `${width}-reset.png`) });
    // Both loaded and reset captures omit the canvas focus-visible outline.
    // Keyboard interaction captures remain focused to verify actual controls.
    assert.ok(loadedImage.equals(resetImage), 'Reset must restore the original static model view');
    const beforeDraws = await page.evaluate(() => window.modelQA.draws.length);
    const box = await canvas.boundingBox();
    await page.mouse.move(box.x + box.width * .45, box.y + box.height * .5);
    await page.mouse.down();
    for (let i = 1; i <= 60; i++) {
      await page.mouse.move(box.x + box.width * (.45 + .25 * Math.sin(i * .09)), box.y + box.height * .5);
    }
    await page.mouse.up();
    await page.waitForTimeout(350);
    const metrics = await page.evaluate(({ beforeDraws }) => {
      const draws = window.modelQA.draws.slice(beforeDraws);
      const frames = [];
      for (const draw of draws) {
        let frame = frames.at(-1);
        if (!frame || draw.rafTime !== frame.rafTime) frames.push(frame = { rafTime: draw.rafTime, start: draw.time, end: draw.time, calls: 0, triangles: 0 });
        frame.end = draw.time;
        frame.calls++;
        if (draw.mode === 4) frame.triangles += draw.count / 3;
      }
      const resources = performance.getEntriesByType('resource').filter(e => e.initiatorType === 'fetch' && new URL(e.name).pathname.endsWith('.glb'));
      const canvas = document.querySelector('#viewport canvas');
      const gl = canvas.getContext('webgl2');
      const ext = gl.getExtension('WEBGL_debug_renderer_info');
      return { width: innerWidth, height: innerHeight, canvasWidth: canvas.width, canvasHeight: canvas.height,
        resources: resources.map(r => ({ url: r.name, durationMs: r.duration, encodedBytes: r.encodedBodySize, decodedBytes: r.decodedBodySize, transferBytes: r.transferSize })),
        observedDraws: draws.length, measuredFrames: frames.length, maxDrawCallsPerObservedFrame: Math.max(0, ...frames.map(f => f.calls)),
        maxTrianglesPerObservedFrame: Math.max(0, ...frames.map(f => f.triangles)),
        renderer: ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : 'unavailable',
        contextLost: gl.isContextLost(), overflow: document.documentElement.scrollWidth > innerWidth };
    }, { beforeDraws });
    assert.ok(metrics.observedDraws > 0);
    assert.equal(metrics.resources.length, 1, 'The actual model fetch must be measured separately from Vite URL modules');
    // Compare decoded payloads; wire sizes may shrink under CDN compression.
    assert.equal(metrics.resources[0].decodedBytes, expectedBytes.length, 'Decoded GLB length must match the validated asset');
    const actualResponse = modelResponses.find(response => response.url() === metrics.resources[0].url);
    assert.ok(actualResponse, 'Capture the actual Viewer model response');
    const actualBytes = await actualResponse.body();
    assert.equal(actualBytes.length, expectedBytes.length);
    assert.equal(createHash('sha256').update(actualBytes).digest('hex'), expectedSha256, 'Viewer must fetch the exact validated candidate');
    assert.equal(metrics.contextLost, false);
    assert.equal(metrics.overflow, false);
    assert.deepEqual(errors, []);
    assert.deepEqual(networkErrors, []);
    await page.screenshot({ path: path.join(out, `${width}-page.png`) });
    results.push({ modelId, assetBytes: expectedBytes.length, assetSha256: expectedSha256, viewport: [width, height], status: 'PASS', rotation: 'PASS', zoom: 'PASS', reset: 'PASS exact pixel match; screenshot retained', metrics, errors, warnings, networkErrors,
      physicalMobilePerformance: 'NOT_TESTED; viewport emulation on desktop software WebGL is not physical-device FPS' });
    console.log('PASS', modelId, 'viewport', width, height);
    await context.close();
  }
} finally {
  await fs.writeFile(path.join(out, 'results.json'), JSON.stringify(results, null, 2) + '\n');
  await browser.close();
}
console.log(JSON.stringify(results, null, 2));
