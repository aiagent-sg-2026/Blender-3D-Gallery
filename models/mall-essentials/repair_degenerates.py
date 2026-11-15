"""Compatibility entry point for staged repairs of the mall essentials sources."""
from pathlib import Path
import runpy
import sys

here = Path(__file__).resolve().parent
assert '--generator' not in sys.argv, 'This entry point selects its own reviewed generator'
sys.argv.extend(['--generator', str(here / 'generate.py')])
runpy.run_path(str(here.parents[1] / 'scripts/repair-static-blender-source.py'), run_name='__main__')
