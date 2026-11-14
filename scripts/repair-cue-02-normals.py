"""One-time guarded CUE-002 migration; preserve the recorded baseline first."""
import runpy
import sys
from pathlib import Path

repair = runpy.run_path(str(Path(__file__).with_name('cue-normal-migration.py')))['repair_cue_normals']
repair('ASSET_Cue_02', '068b90033d5a1a535cb96853f23d8ebf577af79a4b793c3697e172df2e79ae8f', 'CUE-002', sys.argv[sys.argv.index('--') + 1])
