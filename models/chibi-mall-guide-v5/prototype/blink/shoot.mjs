// Serve the repo root, open view.html in headless Chromium and screenshot each key. Usage: node shoot.mjs GLB_DIR OUT_DIR [lid|eyes]
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
import { chromium } from 'playwright';
const [glbDir, outDir, mode = 'lid'] = process.argv.slice(2); fs.mkdirSync(outDir, { recursive: true });
const root = process.cwd(); const types = { '.js': 'text/javascript', '.html': 'text/html', '.glb': 'model/gltf-binary', '.mjs': 'text/javascript' };
const server = http.createServer((req, res) => {
  const u = decodeURIComponent(req.url.split('?')[0]);
  const f = u.startsWith('/out/') ? path.join(glbDir, u.slice(5)) : path.join(root, u);
  if (!fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'content-type': types[path.extname(f)] ?? 'application/octet-stream' }); fs.createReadStream(f).pipe(res);
}).listen(0);
const port = server.address().port;
const browser = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 640, height: 640 } });
const logs = []; page.on('console', (m) => logs.push(m.type() + ': ' + m.text())); page.on('pageerror', (e) => logs.push('pageerror: ' + e.message));
const cases = { neutral: {}, blink: { blink: 1 }, 'blink-half': { blink: 0.5 }, smile: { smile: 1 }, surprised: { surprised: 1 } };
const report = { port, logs, shots: {} };
for (const az of [0, 35]) {
  await page.goto(`http://localhost:${port}/models/chibi-mall-guide-v5/prototype/blink/view.html?az=${az}&glb=/out/blink-prototype-${mode}.glb`);
  await page.waitForFunction('window.__ready === true', null, { timeout: 30000 });
  report.info = await page.evaluate('window.__info');
  for (const [name, v] of Object.entries(cases)) {
    await page.evaluate((x) => window.setKeys(x), v);
    const file = path.join(outDir, `${mode}-${name}-az${az}.png`); await page.screenshot({ path: file }); report.shots[`${mode}-${name}-az${az}`] = file;
  }
}
await browser.close(); server.close();
fs.writeFileSync(path.join(outDir, `shoot-report-${mode}.json`), JSON.stringify(report, null, 1));
console.log(JSON.stringify({ info: report.info, errors: logs.filter((l) => /error/i.test(l)), shots: Object.keys(report.shots).length }));
