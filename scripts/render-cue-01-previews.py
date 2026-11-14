"""Refresh Cue 01 and its assembled preview without saving source."""
import runpy
from pathlib import Path
render = runpy.run_path(str(Path(__file__).with_name('cue-previews.py')))['render_previews']
render('ASSET_Cue_01', '/tmp/model-0002-previews')
