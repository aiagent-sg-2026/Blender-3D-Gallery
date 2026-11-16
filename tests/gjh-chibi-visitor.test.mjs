import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { loadCatalog } from '../scripts/catalog.mjs';

const root = 'models/gjh-chibi-visitor';
const variants = ['terra', 'sol', 'astra'];
const catalog = loadCatalog();
const collection = catalog.collections.find(item => item.id === 'gjh-chibi-visitor');
const visitorLicense = catalog.collections
  .flatMap(item => item.assets)
  .find(asset => asset.id === 'gjh-mall-visitor').license;

test('GJH Chibi Visitor comparison collection registers three Unity variants', () => {
  assert.ok(collection);
  assert.match(collection.name, /GJH Chibi Visitor/);
  assert.match(collection.description, /comparison set/i);
  assert.match(collection.description, /Unity/i);
  assert.match(collection.description, /AI models/i);
  assert.deepEqual(collection.assets.map(asset => asset.id), variants.map(variant => `gjh-chibi-visitor-${variant}`));
  assert.deepEqual(collection.assets.map(asset => asset.name), variants.map(variant => `GJH Chibi Visitor (${variant})`));
  for (const asset of collection.assets) {
    assert.equal(asset.category, 'Characters');
    assert.equal(asset.root, 'GJHChibiVisitor');
    assert.equal(asset.downloadable, false);
    assert.equal(asset.license, visitorLicense);
  }
  assert.equal(fs.existsSync(`${root}/catalog-entry.draft.json`), false);
});

for (const variant of variants) {
  const id = `gjh-chibi-visitor-${variant}`;
  const asset = collection.assets.find(item => item.id === id);
  const metadata = JSON.parse(fs.readFileSync(`${root}/${variant}/metadata.json`, 'utf8'));

  test(`${id}: paths, attribution, and measured metadata match the GLB`, () => {
    assert.equal(metadata.id, id);
    assert.equal(metadata.name, `GJH Chibi Visitor (${variant})`);
    assert.equal(metadata.category, 'Characters');
    assert.equal(metadata.status, 'validated');
    assert.equal(metadata.unity_version, '6000.0.85f2');
    assert.equal(metadata.gltfast_version, '6.21.0');
    assert.equal(metadata.author, `Yap Wei Jun project / ${variant} AI model`);
    assert.equal(metadata.rights, visitorLicense);
    assert.ok(metadata.accuracy_notes.includes('character-sheet image was not available'));
    assert.deepEqual(asset.details, metadata);
    assert.equal(metadata.metrics.glb_bytes, asset.bytes);
    assert.equal(metadata.metrics.triangles, asset.triangles);
    assert.equal(metadata.metrics.vertices, asset.vertices);
    assert.equal(metadata.metrics.animations, asset.animations);
    assert.equal(asset.animations, 0);
    assert.equal(metadata.validation.errors, 0);
    assert.equal(metadata.validation.warnings, 0);
    assert.equal(metadata.paths.glb, `exports/${id}.glb`);
    assert.equal(metadata.paths.source, 'source/ChibiBuilder.cs');
    assert.ok(fs.statSync(`${root}/${variant}/source/ChibiBuilder.cs`).size > 0);
    assert.equal(fs.existsSync(`${root}/${variant}/exports/${id}.glb`), true);
    for (const view of ['front', 'side', 'back', '3q']) {
      const previewPath = `${root}/${variant}/previews/${view}.webp`;
      const bytes = fs.readFileSync(previewPath);
      assert.equal(bytes.toString('ascii', 0, 4), 'RIFF');
      assert.equal(bytes.toString('ascii', 8, 12), 'WEBP');
    }
    assert.ok(fs.statSync(`${root}/${variant}/previews/front.webp`).size < 150 * 1024);
  });
}
