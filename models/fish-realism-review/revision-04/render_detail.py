"""Render the final source eye/skin detail without changing the saved scene."""
import bpy
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent/'stingray'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'stingray-review.blend'));s=bpy.context.scene;s.frame_set(13);c=s.camera;c.location=(-2.2,-3.3,2.4);c.rotation_euler=(Vector((-.52,-.20,.15))-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=1.20;s.render.filepath=str(OUT/'eye-skin-detail.png');bpy.ops.render.render(write_still=True)
