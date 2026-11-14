import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {report} from './qa-utils.mjs';

const here = path.dirname(new URL(import.meta.url).pathname);
const root = process.env.MALL_BASELINE_DIR;
assert.ok(root, 'Set MALL_BASELINE_DIR to the pinned source checkout');
const revision = execFileSync('git', ['rev-parse', 'HEAD'], {cwd: root, encoding: 'utf8'}).trim();
const manifest = JSON.parse(await fs.readFile(path.join(here, 'whitebox/runtime/source-manifest.json')));
assert.equal(revision, manifest.source_revision);
const hash = data => createHash('sha256').update(data).digest('hex');
const entry = 'demos/corporate/gjh/v11/';
for (const file of manifest.files) {
  const original = await fs.readFile(path.join(root, entry, file.path));
  assert.equal(hash(original), file.sha256, file.path);
}
const base = 'https://yapweijun1996.github.io/Webpage-Design-Gallery/' + entry;
const files = [];
for (const file of ['index.html', 'script.js', 'assets/player.js', 'assets/modes.js']) {
  const response = await fetch(base + file, {redirect: 'error', signal: AbortSignal.timeout(20000)});
  assert.equal(response.status, 200);
  assert.equal(response.url, base + file);
  const remote = Buffer.from(await response.arrayBuffer());
  const local = await fs.readFile(path.join(root, entry, file));
  files.push({path: file, finalUrl: response.url, status: response.status,
    remoteSha256: hash(remote), baselineSha256: hash(local), matches: hash(remote) === hash(local)});
}
const deployment = JSON.parse(execFileSync('gh', ['api', 'repos/yapweijun1996/Webpage-Design-Gallery/actions/runs/43611657406'], {encoding: 'utf8'}));
assert.equal(deployment.head_sha, revision);
assert.equal(deployment.conclusion, 'success');
await report(path.join(here, 'reports/baseline-identity.json'), {
  status: files.every(f => f.matches) ? 'PASS' : 'LIVE_DRIFT', checkedAt: new Date().toISOString(),
  revision, applicationVersion: manifest.application_version, sourceCopiesVerified: manifest.files.length,
  liveEntry: base, liveFiles: files,
  deployment: {url: deployment.html_url, revision: deployment.head_sha, conclusion: deployment.conclusion},
  note: 'Four live files are sampled; this does not claim byte identity of the entire deployment.',
});
console.log(files.every(f => f.matches) ? 'PASS: source copies and sampled live files match the deployed baseline' : 'LIVE_DRIFT: keep pinned source baseline; review live-file differences');
