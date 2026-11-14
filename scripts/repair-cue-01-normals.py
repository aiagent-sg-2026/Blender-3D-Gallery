"""One-time guarded CUE-001 migration; preserve the recorded baseline first."""
import runpy
import sys
from pathlib import Path

repair = runpy.run_path(str(Path(__file__).with_name('cue-normal-migration.py')))['repair_cue_normals']
repair('ASSET_Cue_01', '95f940fe5f10fb8d2dcd9d5ca6db04eaaf1690017e3b69929bfea1af110c97bf', 'CUE-001', sys.argv[sys.argv.index('--') + 1])
