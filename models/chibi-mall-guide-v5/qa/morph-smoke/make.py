import bpy, bmesh, sys, os
out = sys.argv[sys.argv.index('--')+1]
bpy.ops.wm.read_factory_settings(use_empty=True)
# head mesh: uv sphere with a face-ish region
bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=0.5)
me = bpy.data.meshes.new('Head'); bm.to_mesh(me); bm.free()
head = bpy.data.objects.new('Head', me); bpy.context.scene.collection.objects.link(head)
head.shape_key_add(name='Basis')
def key(name, fn):
    k = head.shape_key_add(name=name, from_mix=False)
    for i, v in enumerate(me.vertices):
        x, y, z = v.co
        k.data[i].co = fn(x, y, z)
key('smile', lambda x,y,z: (x, y, z + (0.08 if (y < -0.1 and abs(x) < 0.25 and z < 0) else 0)))
key('surprised', lambda x,y,z: (x, y*1.0, z + (0.06 if (y > 0.1 and z < 0) else 0)))
key('blink', lambda x,y,z: (x, y, z + (0.05 if (abs(y) < 0.1 and z < 0) else 0)))
# armature, one bone, head rigidly bound
arm = bpy.data.armatures.new('Rig'); ao = bpy.data.objects.new('Rig', arm)
bpy.context.scene.collection.objects.link(ao)
bpy.context.view_layer.objects.active = ao; bpy.ops.object.mode_set(mode='EDIT')
b = arm.edit_bones.new('head'); b.head=(0,0,0); b.tail=(0,0,0.5)
bpy.ops.object.mode_set(mode='OBJECT')
vg = head.vertex_groups.new(name='head'); vg.add([v.index for v in me.vertices], 1.0, 'REPLACE')
pass  # head left unparented: skinned mesh stays a scene root
m = head.modifiers.new('Armature','ARMATURE'); m.object = ao
# animate shape key + bone
sk = head.data.shape_keys
sk.key_blocks['smile'].value = 0; sk.key_blocks['smile'].keyframe_insert('value', frame=1)
sk.key_blocks['smile'].value = 1; sk.key_blocks['smile'].keyframe_insert('value', frame=10)
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_morph=True, export_animations=True, export_skins=True, export_yup=True)
print('EXPORTED', out)
