"""Prepare scoped checks for pure upstream additions after the full base run."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

root = Path(__file__).resolve().parents[3]
plan = json.loads((Path(__file__).parent / 'upstream-sync.json').read_text())
assert plan['all_existing_assets_identical']
assert plan['existing_collection_fields_and_order_unchanged']
assert plan['app_dependencies_and_billiards_unchanged']
catalog = json.loads((root / 'models/catalog.json').read_text())
assets = {a['id']: a for c in catalog['collections'] for a in c['assets']}
assert len(assets) == plan['current_catalog_entries']
out = root / 'output/model-qa/MODEL-0009/upstream-delta'
assert not out.exists(), 'Preserve any earlier attempt before preparing another'
(out / 'screens').mkdir(parents=True)
rows = []


def replace_once(source, before, after):
    assert source.count(before) == 1, before
    return source.replace(before, after)


for asset_id in plan['new_ids']:
    assert re.fullmatch(r'[a-z0-9-]+', asset_id)
    relative = 'scripts/test-' + asset_id + '-browser.mjs'
    original = subprocess.check_output(
        ['git', 'show', plan['head'] + ':' + relative], cwd=root).decode()
    glb = root / ('models/' + asset_id + '/exports/' + asset_id + '.glb')
    assert assets[asset_id]['file'] == str(glb.relative_to(root))
    assert glb.is_file() and not glb.is_symlink()
    expected = hashlib.sha256(glb.read_bytes()).hexdigest()
    source = replace_once(original, "import assert from 'node:assert/strict';",
                          "import assert from 'node:assert/strict';\nimport { createHash } from 'node:crypto';")
    source = replace_once(source, "'./browser-test-utils.mjs'",
                          json.dumps((root / 'scripts/browser-test-utils.mjs').as_uri()))
    # Respect the campaign's desktop/tablet scope; keep every original assertion.
    source = replace_once(source, '[[1440, 900], [390, 844]]',
                          '[[1440, 900], [768, 1024]]')
    anchor = "    await page.locator('#catalog .asset-card').first().waitFor({ state: 'attached', timeout: 90000 });"
    source = replace_once(source, anchor, anchor + '\n    assert.equal(await page.locator(\'#catalog .asset-card\').count(), ' + str(len(assets)) + ');')
    anchor = '    assert.equal(glbs.length, 1);'
    extra = "\n    const qaHref = await page.getAttribute('#viewer-download', 'href');\n    const qaDownload = await page.request.get(new URL(qaHref, server.url).href);\n    assert.equal(qaDownload.status(), 200);\n    const qaBytes = await qaDownload.body();\n    assert.equal(qaBytes.subarray(0, 4).toString(), 'glTF');\n    assert.equal(createHash('sha256').update(qaBytes).digest('hex'), '" + expected + "');"
    source = replace_once(source, anchor, anchor + extra)
    pattern = r"await page\.screenshot\(\{ path: `/tmp/f\d+-browser-\$\{width\}\.png` \}\);"
    assert len(re.findall(pattern, source)) == 1
    replacement = 'await page.screenshot({ path: ' + json.dumps(str(out / 'screens' / (asset_id + '-'))) + " + width + '.png' });"
    source = re.sub(pattern, lambda _: replacement, source)
    target = out / (asset_id + '.mjs')
    target.write_text(source)
    rows.append(dict(asset_id=asset_id, source_script=relative,
                     original_sha256=hashlib.sha256(original.encode()).hexdigest(),
                     adapted_sha256=hashlib.sha256(source.encode()).hexdigest(),
                     expected_glb_sha256=expected,
                     local_script=str(target.relative_to(root))))

assert len(rows) == len(plan['new_ids']) > 0
(out / 'setup.json').write_text(json.dumps(dict(
    source_head=plan['head'], catalog_entries=len(assets),
    viewports=[[1440, 900], [768, 1024]],
    changes='Retain all original assertions/timeouts; adapt imports/artifact paths and approved viewport scope; add full card count and exact download hash checks.',
    scripts=rows), indent=2) + '\n')
print('Prepared', len(rows), 'upstream-only integration checks; individual model QA remains pending')
