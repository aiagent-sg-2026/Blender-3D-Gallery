import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

// Preparation only: this script never calls KB-MCP or changes remote knowledge.
const directory = dirname(fileURLToPath(import.meta.url));
const root = resolve(directory, '..');
const kbId = '297a8d22-c6cd-4487-a8c3-cab43e583687';
const sha256 = value => createHash('sha256').update(value).digest('hex');
const manual = 'https://docs.blender.org/manual/en/5.1/';
const chapters = [
  ['blender.overview', '9b434d45-3a45-415d-8297-2c37649721df', 'README.md', ['https://docs.blender.org/api/current/bpy.ops.html']],
  ['blender.python', 'a829ec15-cef5-4a99-80ef-5f319b33c9fa', 'python-mcp.md', ['https://docs.blender.org/api/current/bpy.ops.html', `${manual}advanced/command_line/arguments.html`]],
  ['blender.architecture', 'd057765b-4b9f-4679-a1e0-7d7bcfec78f3', 'architecture.md', [`${manual}modeling/modifiers/generate/booleans.html`]],
  ['blender.materials', 'dfa13110-b887-48f1-9f37-7a296569e6a9', 'materials-uv.md', [`${manual}addons/import_export/scene_gltf2.html`]],
  ['blender.character', 'd19c2cf3-7827-4849-a7f1-e0542cc85012', 'characters-animation.md', [`${manual}animation/actions.html`]],
  ['blender.glb', 'e3cbf7d3-30a6-4029-bc90-a7a021fb8911', 'gltf-runtime.md', ['https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html']],
  ['blender.qa', '07d791a3-15d6-47bd-a5ca-d6f33ff23db6', 'quality-delivery.md', ['https://github.com/KhronosGroup/glTF-Validator']],
  ['blender.extensions', '5e6c4c27-5722-415d-9ba2-d3f4d7cf6c65', 'extensions.md', ['https://docs.blender.org/manual/zh-hans/5.1/advanced/extensions/getting_started.html']],
  ['blender.assets', '9bf52af8-73e9-4021-b94a-4b7ce7f00278', 'asset-contract.md', [`${manual}addons/import_export/scene_gltf2.html`]],
  ['blender.roadmap', '0330b65c-c5c8-4053-9e10-63d27ffc8c9b', 'roadmap.md', ['https://docs.blender.org/manual/id/5.1/advanced/scripting/introduction.html']],
];
const updates = [];
for (const [kbcid, itemId, file, sources] of chapters) {
  const document = await readFile(resolve(root, file), 'utf8');
  const matches = [...document.matchAll(/<!-- KB-SUMMARY-START -->\s*([\s\S]*?)\s*<!-- KB-SUMMARY-END -->/g)];
  assert.equal(matches.length, 1, `${file}: one owned summary`);
  const content = `${matches[0][1].trim()}\n\nReviewed 2026-11-15; edition 1.1.0. Full chapter: docs/blender/${file}.\nPrimary references:\n${sources.join('\n')}`;
  assert.ok(content.length <= 1800, `${file}: bounded canonical reference`);
  updates.push({
    kb_id: kbId, item_id: itemId, kbcid, content,
    source: `workspace-document:docs/blender/${file}#sha256=${sha256(document)}`,
    research: {
      edition: '1.1.0', reviewed_on: '2026-11-15', timezone: 'Asia/Singapore',
      scope: 'cross-project Blender knowledge; project dimensions and status excluded',
      chapter: `docs/blender/${file}`, chapter_sha256: sha256(document), content_sha256: sha256(content),
      official_sources: sources, evidence: 'source-backed reference and engineering guidance; bounded native experiments identified separately',
      native_calibration_version: '5.1.2', calibration_receipt: 'docs/blender/verification/probe-results.json',
      source_register: 'docs/blender/sources.md',
      limits: 'No extension installation/operation, humanoid deformation, textured browser appearance, physical-phone or FPS acceptance established by this research.',
    },
  });
}
const extensionDocument = await readFile(resolve(root, 'extensions.md'), 'utf8');
const catalog = extensionDocument.slice(extensionDocument.indexOf('## Dated catalog'), extensionDocument.indexOf('## Admission procedure')).trim();
assert.ok(catalog.includes('## Verification scope') && catalog.includes('5.1.2'));
const calibration = await readFile(resolve(root, 'calibration.md'), 'utf8');
const definitions = [
  ['Blender extension catalog — 2026-11-15', 'blender.extension-catalog', 'blender.extensions', catalog, 'extensions.md'],
  ['Blender 5.1.2 calibration — bounded native and GLB observations', 'blender.calibration', 'blender.qa', calibration, 'calibration.md'],
];
const documents = [];
for (const [title, kbcid, canonicalTopic, content, file] of definitions) {
  const fullDocument = await readFile(resolve(root, file), 'utf8');
  documents.push({
    kb_id: kbId, title, kbcid, content, auto_chunk: true, max_chars: 1300, overlap: 150,
    idempotency_key: `blender-research-20261115:${kbcid}:${sha256(content)}`,
    share_level: 'user', source: `workspace-document:docs/blender/${file}#sha256=${sha256(fullDocument)}`,
    metadata: {
      kind: 'reference', domain: 'blender', version: '1.1.0', reviewed_on: '2026-11-15',
      canonical_topic_ref: `${kbId}:${updates.find(item => item.kbcid === canonicalTopic).item_id}`,
      chapter: `docs/blender/${file}`, chapter_sha256: sha256(fullDocument), content_sha256: sha256(content),
      scope: 'cross-project; dated catalog or bounded experiment detail',
      evidence: kbcid === 'blender.calibration' ? 'bounded native experiment' : 'official listing excerpts; not installation or source audit',
    },
  });
}
const plan = {
  kbid: 'blender', kb_id: kbId, edition: '1.1.0', reviewed_on: '2026-11-15',
  instructions: 'Read fresh metadata before each PATCH and preserve unrelated fields and user visibility. Do not replay an already confirmed ingest. Verify stored bodies and retrieval; no Git release is performed here.',
  updates, documents,
};
await writeFile(resolve(directory, 'kb-plan.json'), `${JSON.stringify(plan, null, 2)}\n`);
console.log(JSON.stringify({ updates: updates.map(item => ({ kbcid: item.kbcid, chars: item.content.length })), documents: documents.map(item => ({ kbcid: item.kbcid, chars: item.content.length })) }));
