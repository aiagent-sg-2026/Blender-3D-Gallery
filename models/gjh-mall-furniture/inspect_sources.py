"""Reopen the editable Blender sources and verify their authoring roots."""
import bpy
import json
import sys
from pathlib import Path
root = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(root.parents[1] / 'scripts'))
from blender_degenerate_cleanup import geometry_counts
results = []
for name, expected in [('gjh-lounge-bench', 'ASSET_GJHLoungeBench'), ('gjh-areca-planter', 'ASSET_GJHArecaPlanter')]:
    bpy.ops.wm.open_mainfile(filepath=str(root / 'sources' / (name + '.blend')))
    source = bpy.data.objects.get(expected)
    assert source and len(source.children) > 10
    assert tuple(source.location) == (0, 0, 0)
    assert bpy.context.scene.unit_settings.scale_length == 1
    assert all(obj.data for obj in source.children)
    zero = sum(item['zero_area_triangles'] for item in geometry_counts(list(source.children_recursive)))
    if name == 'gjh-areca-planter': assert zero == 0
    results.append({'zero_area_triangles': zero, 'id': name, 'source_reopened': 'PASS', 'editable_parts': len(source.children), 'floor_origin': 'PASS', 'blender_version': bpy.app.version_string})
(root / 'reports' / 'sources.json').write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps(results))
