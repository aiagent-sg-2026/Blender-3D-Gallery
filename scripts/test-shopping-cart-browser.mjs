import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import { chromium, webkit } from 'playwright';
import { serveBuild, launchOptions } from './browser-test-utils.mjs';

const server = await serveBuild();
const engine = process.env.CART_BROWSER === 'webkit' ? 'webkit' : 'chromium';
const browser = await (engine === 'webkit' ? webkit.launch({ headless: true }) : chromium.launch(launchOptions));
const dir = process.env.CART_QA_DIR || '/tmp/gallery-cart-qa';
await fs.mkdir(dir, { recursive: true });
const errors = [];
try {
  for (const width of [1440, 768, 390]) {
    const context = await browser.newContext({ viewport: { width, height: 900 }, serviceWorkers: 'block' });
    const page = await context.newPage();
    await page.addInitScript(() => {
      window.cartCspViolations = [];
      document.addEventListener('securitypolicyviolation', event => {
        window.cartCspViolations.push({ directive: event.effectiveDirective, target: event.target?.id });
      });
    });
    page.on('pageerror', error => errors.push(error.message));
    page.on('console', message => {
      if (message.type() !== 'error') return;
      // WebKit reports native select styling under the existing CSP on both the
      // baseline viewer and this demo. The actual violations are checked below.
      if (engine === 'webkit' && message.text() === "Refused to apply a stylesheet because its hash, its nonce, or 'unsafe-inline' does not appear in the style-src directive of the Content Security Policy.") return;
      errors.push(message.text());
    });
    await page.goto(server.url + '?model=interactive-shopping-cart');
    const controls = page.locator('.cart-demo');
    await controls.waitFor({ timeout: 30000 });
    assert.equal(await controls.getAttribute('data-state'), 'Idle');
    assert.ok(await page.locator('[data-cart-action="push"]').isDisabled());
    await page.locator('[data-cart-action="grab"]').click();
    await page.waitForFunction(() => Number(document.querySelector('.cart-demo')?.dataset.handGap) < .03);
    if (engine === 'chromium') await page.screenshot({ path: `${dir}/${engine}-grab-${width}.png` });
    await page.locator('[data-cart-action="add"]').click();
    await page.waitForFunction(() => document.querySelector('.cart-demo')?.dataset.item === 'present');
    assert.equal(await controls.getAttribute('data-item-visible'), 'true');
    await page.locator('[data-cart-action="remove"]').click();
    await page.waitForFunction(() => document.querySelector('.cart-demo')?.dataset.item === 'absent');
    assert.equal(await controls.getAttribute('data-item-visible'), 'false');
    await page.locator('[data-cart-action="right"]').click();
    await page.locator('[data-cart-action="push"]').click();
    await page.waitForFunction(() => Number(document.querySelector('.cart-demo')?.dataset.position) > .06, null, { timeout: 15000 });
    assert.ok(Math.abs(Number(await controls.getAttribute('data-heading'))) > .01);
    assert.ok(Number(await controls.getAttribute('data-wheel')) > .1);
    assert.ok(Number(await controls.getAttribute('data-steering')) > .5);
    assert.ok((await controls.getAttribute('data-wheels')).split(',').every(value => Number(value) > .1));
    assert.ok((await controls.getAttribute('data-front-steering')).split(',').every(value => Number(value) > .5));
    assert.ok(Number(await controls.getAttribute('data-hand-gap')) < .03);
    await page.locator('[data-cart-action="stop"]').click();
    await page.waitForFunction(() => Number(document.querySelector('.cart-demo')?.dataset.speed) === 0, null, { timeout: 15000 });
    await page.locator('[data-cart-action="release"]').click();
    assert.equal(await controls.getAttribute('data-state'), 'Release');
    await page.locator('[data-cart-action="reset"]').click();
    assert.equal(await controls.getAttribute('data-state'), 'Idle');
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
    if (width === 1440) {
      await page.locator('[data-cart-action="grab"]').click();
      await page.locator('[data-cart-action="push"]').click();
      await page.waitForFunction(() => document.querySelector('.cart-demo')?.dataset.state === 'Collision', null, { timeout: 25000 });
      assert.equal(Number(await controls.getAttribute('data-speed')), 0);
      assert.ok(await page.locator('[data-cart-action="push"]').isDisabled());
      if (engine === 'chromium') await page.screenshot({ path: `${dir}/${engine}-collision.png` });
    }
    await page.locator('#close-viewer').click();
    assert.equal(await page.locator('.cart-demo').count(), 0);
    assert.equal(await page.locator('#viewport canvas').count(), 0);
    const csp = await page.evaluate(() => window.cartCspViolations);
    assert.ok(csp.every(v => engine === 'webkit' && v.directive === 'style-src-attr' && ['model-theme', 'model-category', 'model-collection', 'demo-category'].includes(v.target)), JSON.stringify(csp));
    if (csp.length) console.log(`NOTE ${engine} ${width}px: ${csp.length} existing native-select CSP warnings`);
    await context.close();
    console.log(`PASS ${engine} ${width}px: grab, add/remove, turn, push, stop, release, reset${width === 1440 ? ', collision' : ''}`);
  }
  assert.deepEqual(errors, []);
} finally {
  await browser.close();
  await server.close();
}
