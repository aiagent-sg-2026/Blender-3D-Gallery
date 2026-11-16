/* The same physical scale, pose and orthographic camera for both exported assets. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {chromium} from 'playwright';

const [original, revision, reference] = process.argv.slice(2);
const hex = bytes => createHash('sha256').update(bytes).digest('hex');
const sheet = await fs.readFile(reference);
const refHash = hex(sheet);
async function read(folder) {
  const base = path.join(folder, 'qa', 'registration');
  const bytes = await fs.readFile(path.join(base, 'manifest.json'));
  const manifest = JSON.parse(bytes);
  const glb = await fs.readFile(path.join(folder, 'visitor.glb'));
  const html = await fs.readFile(path.join(folder, 'preview.html'));
  if (hex(glb) !== manifest.artifactSha256 || hex(html) !== manifest.previewSha256 ||
      refHash !== manifest.referenceSha256) throw Error('Registration does not match ' + folder);
  const frames = {};
  for (const [name] of manifest.views) {
    const file = name + '-rgb.png';
    const frame = await fs.readFile(path.join(base, file));
    if (hex(frame) !== manifest.files[file]) throw Error('Registration changed: ' + file);
    frames[name] = frame.toString('base64');
  }
  return {manifest, frames, hash: hex(bytes)};
}
const [before, after] = await Promise.all([read(original), read(revision)]);
for (const field of ['views', 'viewport', 'pixelsPerReferencePixel', 'referenceRowAtTop', 'viewCenterY', 'captureSha256', 'rendererSourceSha256']) {
  if (JSON.stringify(before.manifest[field]) !== JSON.stringify(after.manifest[field])) {
    throw Error('Capture settings differ: ' + field);
  }
}
const browser = await chromium.launch();
try {
  const page = await browser.newPage();
  const uri = await page.evaluate(async ({left, right, views, sheet}) => {
    async function decode(data) {
      const im = new Image();
      im.src = 'data:image/png;base64,' + data;
      await im.decode();
      return im;
    }
    const ref = await decode(sheet);
    const w = 288, h = 234, gap = 8, margin = 16, labelWidth = 75;
    const shown = [['front', 'Front'], ['quarter', '¾ front'], ['profile', 'Profile'], ['back', 'Back']];
    const canvas = document.createElement('canvas');
    canvas.width = margin * 2 + labelWidth + w * 3 + gap * 2;
    canvas.height = 48 + shown.length * (h + gap) + margin;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#f2f0f5';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#292431';
    ctx.font = '600 18px sans-serif';
    const x = col => margin + labelWidth + col * (w + gap);
    ['Character sheet', 'Before', 'After'].forEach((t, i) => ctx.fillText(t, x(i), 31));
    ctx.font = '15px sans-serif';
    for (const [index, [name, title]] of shown.entries()) {
      const y = 48 + index * (h + gap);
      ctx.fillText(title, margin, y + 23);
      const cx = views.find(v => v[0] === name)[2];
      ctx.drawImage(ref, cx - 120, 49, 240, 195, x(0), y, w, h);
      const [old, now] = await Promise.all([decode(left[name]), decode(right[name])]);
      ctx.drawImage(old, 0, 0, 480, 390, x(1), y, w, h);
      ctx.drawImage(now, 0, 0, 480, 390, x(2), y, w, h);
    }
    return canvas.toDataURL('image/png');
  }, {left: before.frames, right: after.frames, views: after.manifest.views, sheet: sheet.toString('base64')});
  const out = Buffer.from(uri.split(',')[1], 'base64');
  const qa = path.join(revision, 'qa');
  await fs.writeFile(path.join(qa, 'before-after-hair.png'), out);
  await fs.writeFile(path.join(qa, 'before-after-hair.json'), JSON.stringify({
    previousGlb: before.manifest.artifactSha256, revisedGlb: after.manifest.artifactSha256,
    referenceSha256: refHash, beforeRegistration: before.hash, afterRegistration: after.hash,
    outputSha256: hex(out), operations: 'Labels, crops and uniform scale. Fixed real-time material and lighting.',
    referenceProjection: 'The three principal panels constrain scale and direction. The original quarter camera is estimated.'
  }, null, 2) + '\n');
} finally {
  await browser.close();
}
