"""Render MODEL-0004 previews without changing the saved scene."""
import runpy, sys
from pathlib import Path

output=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else '/tmp/model-0004-previews'
runpy.run_path(str(Path(__file__).with_name('cue-previews.py')))['render_previews']('ASSET_Triangle_Rack',output)
