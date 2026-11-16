"""Resume actual-catalog live QA serially with bounded Pages rate-limit backoff.

The unchanged browser harness owns all assertions. Intermediate checkpoints may
cover a selected subset; only the final all-manifest pass establishes completion.
"""
import datetime
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.error
import urllib.request

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
os.chdir(REPO)
manifest = json.loads((HERE / 'releases.json').read_text())['models']
base = os.environ['FISH_LIVE_URL']
batch = os.environ.get('FISH_BATCH', 'final-60')
assert os.environ.get('FISH_DEPLOY_SHA'), 'Bind live evidence to a deployment commit'
interval = int(os.environ.get('FISH_INTERVAL_SECONDS', '25'))
assert 20 <= interval <= 120
engines = ['chromium', 'webkit']
events = HERE / f'live-{batch}-pacing-events.jsonl'


def record(**data):
    data['at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with events.open('a') as output:
        output.write(json.dumps(data) + '\n')
    print(json.dumps(data), flush=True)


def ready():
    for attempt in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(base, method='HEAD'), timeout=30) as response:
                assert response.status == 200
            return
        except urllib.error.HTTPError as error:
            if error.code != 429:
                raise
            record(event='pages_rate_limited', attempt=attempt + 1)
            if attempt == 5:
                raise
            time.sleep(60)
    raise AssertionError('Unreachable')


def run(engine, slug=None):
    env = {**os.environ, 'FISH_ENGINE': engine, 'FISH_BATCH': batch, 'FISH_RESUME': '1'}
    if slug:
        env['FISH_SLUGS'] = slug
    else:
        env.pop('FISH_SLUGS', None)
    log = Path('/tmp') / f'fish-{batch}-paced-{engine}.log'
    with log.open('a') as output:
        result = subprocess.run(['node', str(HERE / 'test-browser.mjs')], env=env, stdout=output, stderr=subprocess.STDOUT)
    record(event='harness_finished', engine=engine, slug=slug, exit_code=result.returncode, log=str(log))
    if result.returncode:
        raise SystemExit(result.returncode)


for slug, item in manifest.items():
    for engine in engines:
        receipt = HERE / f'live-{engine}-{batch}-browser-verification.json'
        prior = json.loads(receipt.read_text())['results'] if receipt.exists() else []
        matching = {row['width'] for row in prior if row['slug'] == slug and row['engine'] == engine and row['loaded_release_sha256'] == item['glb_sha256']}
        if matching == {1440, 390}:
            continue
        ready()
        run(engine, slug)
        time.sleep(interval)

# Both full-scope passes revalidate every retained row with the original harness.
for engine in engines:
    run(engine)
    receipt = json.loads((HERE / f'live-{engine}-{batch}-browser-verification.json').read_text())
    assert receipt['completed'] is True and len(receipt['results']) == len(manifest) * 2
record(event='all_live_cases_passed', entries=len(manifest), cases=len(manifest) * 4, interval_seconds=interval)
