"""Refresh both review views from a finalized packed scene without editing it."""
import bpy,sys
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;slug=sys.argv[sys.argv.index('--')+1];OUT=HERE/slug
bpy.ops.wm.open_mainfile(filepath=str(OUT/(slug+'.blend')));s=bpy.context.scene;s.frame_set(13);s.render.filepath=str(OUT/'preview.png');bpy.ops.render.render(write_still=True);s.camera.location=(-1.15,-7,.55);s.camera.rotation_euler=(Vector((-1.03,0,.02))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=1.65;s.render.filepath=str(OUT/'head-detail.png');bpy.ops.render.render(write_still=True)
