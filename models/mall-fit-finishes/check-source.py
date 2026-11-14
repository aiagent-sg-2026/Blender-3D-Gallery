"""Reopen saved sources and prove mesh/material edits survive save and GLB export.
All edited copies and re-exported GLBs stay in an automatically removed temp directory.
"""
from pathlib import Path
import bpy, json, hashlib, tempfile
from mathutils import Vector
P=Path(__file__).resolve().parent
slugs=['mall-shopfront-fascia-210','mall-shopfront-fascia-120','mall-column-ceiling-collar']
results=[]
def mesh_center(o):
    return sum((o.matrix_world@v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
for slug in slugs:
    source=P/'sources'/(slug+'.blend');canonical=hashlib.sha256(source.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(source));root=bpy.data.objects['ASSET_'+slug.replace('-','_')]
    parts=[o for o in root.children_recursive if o.type=='MESH']
    for part in parts:
        edges={}
        for face in part.data.polygons:
            for edge in face.edge_keys:edges[edge]=edges.get(edge,0)+1
        assert edges and all(v==2 for v in edges.values()),part.name
        part.data.calc_loop_triangles()
        volume=sum(part.data.vertices[t.vertices[0]].co.dot(part.data.vertices[t.vertices[1]].co.cross(part.data.vertices[t.vertices[2]].co))/6 for t in part.data.loop_triangles)
        assert volume>0,part.name
    target_name='CLOSURE_N' if 'collar' in slug else 'SIGN_ReplaceableFace'
    target=bpy.data.objects[target_name]
    bpy.context.view_layer.update();old=mesh_center(target).copy()
    old_roughness=target.data.materials[0].node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value
    for v in target.data.vertices:v.co.z+=.004
    target.data.materials[0].node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.61
    bpy.context.view_layer.update();edited=mesh_center(target).copy()
    with tempfile.TemporaryDirectory(prefix='gallery-source-proof-') as temp:
        copy=Path(temp)/'edited.blend';bpy.ops.wm.save_as_mainfile(filepath=str(copy),compress=True)
        bpy.ops.wm.open_mainfile(filepath=str(copy));target=bpy.data.objects[target_name];bpy.context.view_layer.update()
        assert (mesh_center(target)-edited).length<1e-6
        root=bpy.data.objects['ASSET_'+slug.replace('-','_')];bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
        for o in root.children_recursive:o.select_set(True)
        export=Path(temp)/'edited.glb';bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_cameras=False,export_lights=False)
        bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(export));bpy.context.view_layer.update()
        imported=bpy.data.objects[target_name];delta=mesh_center(imported)-old
        rough=imported.data.materials[0].node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value
        # Blender imports glTF into Z-up again, so the same vertical displacement must remain.
        assert abs(delta.z-.004)<1e-6 and abs(rough-.61)<1e-6
    assert hashlib.sha256(source.read_bytes()).hexdigest()==canonical
    results.append({'slug':slug,'source_sha256':canonical,'editable_meshes':len(parts),'closed_positive_volume_components':True,'edited_part':target_name,'saved_reopened_reexported_delta_z_m':delta.z,'exported_roughness':rough,'canonical_unchanged':True,'pass':True})
(P/'reports/source-proof.json').write_text(json.dumps(results,indent=2)+'\n')
print('SOURCE_PROOF',len(results),'PASS')
