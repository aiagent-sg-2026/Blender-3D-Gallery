"""Builds every part and merges them into one object per material group."""
import bpy

import body
import clothes
import hair
import head
import materials as M
import props
from mesh import make_object, shade, signed_volume, triangle_count

# Object name -> smooth-shading angle (degrees). Sharper angles keep creases.
SHADING = {
    "Body": 70.0, "Face": 80.0, "Hair": 180.0, "Tee": 70.0, "Jeans": 70.0,
    "Shoes": 55.0, "Backpack": 50.0, "Watch": 40.0,
}


def clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.armatures, bpy.data.actions,
                  bpy.data.cameras, bpy.data.lights):
        for item in list(block):
            block.remove(item)


def build(out_dir):
    clear_scene()
    scene = bpy.context.scene
    collection = bpy.data.collections.new("GJHChibiVisitor")
    scene.collection.children.link(collection)
    mats = M.build(out_dir)

    skull = head.build_skull(mats)
    tee = clothes.build_tee(mats)
    arm = body.build_arm(mats)
    groups = {
        "Body": [skull, head.build_nose(skull, mats), *head.build_ears(mats), head.build_neck(mats), arm,
                 body.mirror(arm)],
        "Hair": [hair.build_cap(mats), hair.build_locks(mats)],
        "Tee": tee,
        "Jeans": clothes.build_jeans(mats),
        "Shoes": clothes.build_shoe(mats),
        "Backpack": props.build_backpack(mats, tee),
        "Watch": [props.build_watch(mats)],
    }
    objects = {}
    # Every part is built closed or as an outward-facing shell, so a negative
    # signed volume means its faces point inwards.
    inside_out = [f"{name}/{part.name}" for name, parts in groups.items() for part in parts
                  if signed_volume(part) < 0.0]
    for name, parts in groups.items():
        obj = make_object(name, parts, collection)
        shade(obj, SHADING[name])
        objects[name] = obj

    face_builder = head.build_face(skull, mats)
    face = make_object("Face", [face_builder.part], collection)
    shade(face, SHADING["Face"])
    head.add_shape_keys(face, face_builder)
    objects["Face"] = face

    counts = {name: triangle_count(obj) for name, obj in objects.items()}
    counts["total"] = sum(counts.values())
    return objects, {"triangles": counts, "inside_out": inside_out}
