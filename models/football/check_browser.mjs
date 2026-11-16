import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { chromium } from 'playwright';
import { serveBuild, launchOptions } from '../../scripts/browser-test-utils.mjs';

const dir = new URL('.', import.meta.url);
async function main() {
const measured = JSON.parse(await fs.readFile(new URL('reports/assets.json', dir), 'utf8'));
const server = await serveBuild();
const browser = await chromium.launch(launchOptions);
const errors = [], failedRequests = [];
const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, serviceWorkers: 'block' });
await context.addInitScript(() => {
  window.footballQA = { totalDraws: 0, frameDraws: 0, frameTriangles: 0 };
  for (const prototype of [WebGLRenderingContext.prototype, WebGL2RenderingContext.prototype]) {
    const clear = prototype.clear;
    prototype.clear = function (...args) {
      window.footballQA.frameDraws = 0;
      window.footballQA.frameTriangles = 0;
      return clear.apply(this, args);
    };
    for (const name of ['drawArrays', 'drawElements', 'drawArraysInstanced', 'drawElementsInstanced']) {
      const draw = prototype[name];
      if (!draw) continue;
      prototype[name] = function (...args) {
        window.footballQA.totalDraws++;
        window.footballQA.frameDraws++;
        if (args[0] === this.TRIANGLES) {
          const count = name.startsWith('drawElements') ? args[1] : args[2];
          const instances = name.endsWith('Instanced') ? args.at(-1) : 1;
          window.footballQA.frameTriangles += count / 3 * instances;
        }
        return draw.apply(this, args);
      };
    }
  }
});
const page = await context.newPage();
page.on('pageerror', error => errors.push(error.message));
page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
page.on('requestfailed', request => failedRequests.push(request.failure()?.errorText + ' ' + request.url()));
try {
  const responsePromise = page.waitForResponse(response => new URL(response.url()).pathname.endsWith('.glb'));
  await page.goto(server.url + '?model=football', { waitUntil: 'domcontentloaded' });
  const response = await responsePromise;
  assert.equal(response.status(), 200);
  const loaded = await response.body();
  assert.equal(createHash('sha256').update(loaded).digest('hex'), measured.sha256, 'browser received the validated GLB');
  await page.waitForFunction(() => document.querySelector('#viewer')?.open &&
    document.querySelector('#viewport canvas') && document.querySelector('#viewer-status')?.textContent === '' &&
    window.footballQA.frameDraws === 2, null, { timeout: 60000 });
  const canvas = page.locator('#viewport canvas');
  await canvas.focus();
  const before = await page.evaluate(() => ({ ...window.footballQA }));
  assert.equal(before.frameTriangles, measured.triangles);
  const output = new URL('reports/browser.png', dir).pathname;
  await fs.mkdir(path.dirname(output), { recursive: true });
  await page.screenshot({ path: output });
  const initialPixels = await canvas.screenshot();
  await page.keyboard.press('ArrowRight');
  await page.keyboard.press('+');
  await page.waitForFunction(draws => window.footballQA.totalDraws > draws, before.totalDraws);
  const afterPixels = await canvas.screenshot();
  assert.notDeepEqual(initialPixels, afterPixels, 'orbit/zoom visibly changes the real rendered model');
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
  const after = await page.evaluate(() => ({ ...window.footballQA }));
  assert.equal(after.frameDraws, 2);
  assert.equal(after.frameTriangles, measured.triangles);
  await page.keyboard.press('Escape');
  await page.waitForFunction(() => !document.querySelector('#viewer').open && !document.querySelector('#viewport canvas'));
  assert.deepEqual(errors, []);
  assert.deepEqual(failedRequests, []);
  const report = { result: 'PASS', browser: browser.version(), viewport: [1440, 900],
    renderer: 'headless Chromium / SwiftShader', loaded_glb_sha256: measured.sha256,
    frame_draw_calls: after.frameDraws, frame_triangles: after.frameTriangles,
    orbit_zoom_pixel_change: true, close_disposes_canvas: true,
    console_page_errors: errors, failed_requests: failedRequests, screenshot: output,
    unverified: ['physical mobile devices', 'GPU performance on target hardware'] };
  await fs.writeFile(new URL('reports/browser.json', dir), JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify(report, null, 2));
} finally {
  await context.close();
  await browser.close();
  await server.close();
}

}
main().catch(async error => {
  const report = {result: 'BLOCKED', command: 'node models/football/check_browser.mjs',
    error: String(error.stack ?? error), verified: false};
  await fs.writeFile(new URL('reports/browser.json', dir), JSON.stringify(report,null,2)+'\n');
  console.error(error); process.exitCode=1;
});
process.on('uncaughtException', async error => {
  await fs.writeFile(new URL('reports/browser.json', dir), JSON.stringify({result:'BLOCKED',
    command:'node models/football/check_browser.mjs',error:String(error.stack ?? error),
    verified:false,unverified:['GLB rendering in gallery','orbit and zoom','physical mobile devices','target GPU performance']},null,2)+'\n');
  console.error(error); process.exitCode=1;
});
