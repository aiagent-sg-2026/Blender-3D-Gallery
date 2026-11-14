"""Render one loop of representative editable source scenes for visual review."""
from pathlib import Path
import bpy
HERE=Path(__file__).resolve().parent
for slug in ['barramundi','stingray','swamp-eel','betta']:
 with bpy.data.libraries.load(str(HERE/slug/'sources'/f'{slug}.blend'),link=False) as (source,target):target.scenes=source.scenes
 scene=target.scenes[0];bpy.context.window.scene=scene
 scene.render.resolution_x=480;scene.render.resolution_y=360
 out=HERE/slug/'previews'/'motion';out.mkdir(exist_ok=True)
 for i in range(20):
  scene.frame_set(round(scene.frame_end*i/20));scene.render.filepath=str(out/f'{i:02}.png');bpy.ops.render.render(write_still=True)
 bpy.context.window.scene=bpy.data.scenes[0];bpy.data.scenes.remove(scene)
