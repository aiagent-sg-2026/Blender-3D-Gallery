// Usage (repo root): node models/chibi-mall-guide-v5/trellis-trial/shoot-glb.mjs GLB_FILE OUT_PNG
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path'; import { chromium } from 'playwright';
const [glb, outPng] = process.argv.slice(2); const root = process.cwd();
const types = { '.js': 'text/javascript', '.html': 'text/html', '.glb': 'model/gltf-binary', '.mjs': 'text/javascript' };
const server = http.createServer((req, res) => {
  const u = decodeURIComponent(req.url.split('?')[0]); const f = u === '/model.glb' ? glb : path.join(root, u);
  if (!fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'content-type': types[path.extname(f)] ?? 'application/octet-stream' }); fs.createReadStream(f).pipe(res);
}).listen(0); const port = server.address().port;
const browser = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 2240, height: 560 } }); const logs = [];
page.on('console', (m) => logs.push(m.type() + ': ' + m.text())); page.on('pageerror', (e) => logs.push('pageerror: ' + e.message));
await page.goto(`http://localhost:${port}/models/chibi-mall-guide-v5/trellis-trial/view-glb.html?glb=/model.glb`);
await page.waitForFunction('window.__ready === true', null, { timeout: 60000 });
const info = await page.evaluate('window.__info'); await page.screenshot({ path: outPng });
await browser.close(); server.close(); console.log(JSON.stringify({ info, errors: logs.filter((l) => /error/i.test(l)) }));
