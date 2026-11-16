"""Non-destructive replay fixture. Move one authored fringe handle and export a temporary binary."""
import sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"authoring"))
from scene import export
out=Path(sys.argv[-1])
guide=bpy.data.objects["Falling fringe outer"]
guide.data.splines[0].points[4].co.x-=.012
out.mkdir(exist_ok=True);export(out/"visitor.glb")

