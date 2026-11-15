import bpy, json, sys
from pathlib import Path
root = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(root.parents[1] / 'scripts'))
from blender_degenerate_cleanup import geometry_counts
bpy.ops.wm.open_mainfile(filepath=str(root / 'sources/mall-event-booth.blend'))
scene_root = bpy.data.collections.get('ASSET_MallEventBooth')
assert scene_root and {'BoothStructure', 'PosterPanel', 'DisplayContent'} <= {c.name for c in scene_root.children}
poster = scene_root.children.get('PosterPanel'); display = scene_root.children.get('DisplayContent')
assert poster and display and len(poster.objects) >= 5 and len(display.objects) >= 5
assert any(o.type == 'FONT' and o.data.body == 'YOUR STORY' for o in poster.objects)
assert any(o.type == 'FONT' and o.data.body == 'EDITABLE DISPLAY' for o in display.objects)
zero = sum(item['zero_area_triangles'] for item in geometry_counts(list(scene_root.all_objects)))
assert zero == 0
result = {'zero_area_triangles': zero, 'editable_parts': len(scene_root.all_objects), 'id': 'mall-event-booth', 'source_reopened': 'PASS', 'collections': [c.name for c in scene_root.children], 'poster_objects': len(poster.objects), 'display_objects': len(display.objects), 'blender_version': bpy.app.version_string, 'floor_origin': scene_root['origin']}
(root / 'reports').mkdir(exist_ok=True); (root / 'reports/sources.json').write_text(json.dumps(result, indent=2) + '\n'); print(json.dumps(result))
