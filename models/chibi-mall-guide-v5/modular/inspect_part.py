"""Print the size, orientation hints, triangles and texture of a reconstructed part GLB.
Run: blender --background --factory-startup --python inspect_part.py -- PART.glb"""
import bpy, sys, numpy as np
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=sys.argv[sys.argv.index('--') + 1])
ms = [o for o in bpy.data.objects if o.type == 'MESH']
for o in ms:
    P = np.array([(o.matrix_world @ v.co)[:] for v in o.data.vertices]); mat = o.data.materials[0]
    img = [n.image for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE'] if mat and mat.node_tree else []
    print('PART', o.name, 'tris', len(o.data.polygons), 'verts', len(P), 'bbox', P.min(0).round(3), P.max(0).round(3), 'size', (P.max(0) - P.min(0)).round(3), 'tex', img[0].size[:] if img else None)
