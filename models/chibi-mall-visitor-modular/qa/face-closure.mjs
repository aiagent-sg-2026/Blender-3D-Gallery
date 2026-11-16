/* A closed neutral lip seam must occlude the teeth and tongue in the actual GLB. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
import {chromium} from 'playwright';

const folder = path.resolve(process.argv[2]);
const html = await fs.readFile(path.join(folder, 'preview.html'));
const glb = await fs.readFile(path.join(folder, 'visitor.glb'));
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const match = html.toString().match(/id="asset">([^<]+)<\/script>/);
if (!match || !glb.equals(Buffer.from(match[1], 'base64'))) throw Error('Unbound preview');
const browser = await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
try {
  const page = await browser.newPage({viewport:{width:520,height:380},deviceScaleFactor:1});
  await page.goto(pathToFileURL(path.join(folder,'preview.html')).href+'?qa=1');
  await page.addStyleTag({content:'main{display:block}aside{display:none}#stage{width:100vw;height:100vh}'});
  const measurements = await page.evaluate(async () => {
    const v = await window.visitorReady;
    const oral = v.meshes.find(m => m.name === 'Teeth_and_tongue');
    const output = [];
    const gl = v.renderer.getContext();
    function pixels() {
      v.draw();
      const data = new Uint8Array(gl.drawingBufferWidth * gl.drawingBufferHeight * 4);
      gl.readPixels(0,0,gl.drawingBufferWidth,gl.drawingBufferHeight,gl.RGBA,gl.UNSIGNED_BYTE,data);
      return data;
    }
    v.motion('');
    v.ground.visible = false;
    for (const degrees of [0,-32,32]) {
      v.view(degrees,.30,.886,0);
      for (const expression of ['default','happy','surprised','excited']) {
        v.face(expression);
        oral.visible = true;
        const withMouth = pixels();
        oral.visible = false;
        const hidden = pixels();
        let changed = 0;
        for (let i = 0; i < hidden.length; i += 4) {
          if (Math.max(...[0,1,2].map(k => Math.abs(withMouth[i+k]-hidden[i+k]))) > 2) changed++;
        }
        output.push({degrees,expression,changedPixels:changed});
      }
    }
    oral.visible = true;
    v.face('default');
    return output;
  });
  const pass = measurements.every(r => r.expression === 'default' ? r.changedPixels === 0 : r.changedPixels > 0);
  const report = {pass,glbSha256:hash(glb),previewSha256:hash(html),viewport:[520,380],
    method:'RGB readback with the oral surfaces shown/hidden at a fixed camera. Two code values disregard subpixel rounding.',measurements};
  await fs.mkdir(path.join(folder,'qa'),{recursive:true});
  await fs.writeFile(path.join(folder,'qa','face-closure.json'),JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report));
  if (!pass) process.exitCode = 1;
} finally {
  await browser.close();
}
