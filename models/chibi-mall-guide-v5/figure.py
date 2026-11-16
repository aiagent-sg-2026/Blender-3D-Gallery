"""Builds every part of the Mall Guide built so far (Blender only). Shared by build_parts.py and hair_gate.py."""
import config as C, kit, garments, limbs, head as H, hair as HR

def build_all(bpy, bmesh):
    mats = garments.make_materials(bpy)
    parts = [garments.build_cap(bmesh, mats), garments.build_vest(bmesh, mats), garments.build_shirt(bmesh, mats),
             garments.build_neckerchief(bmesh, mats), garments.build_shorts(bmesh, mats)]
    for fn in (limbs.build_arms, limbs.build_gloves, limbs.build_legs, limbs.build_socks, limbs.build_shoes):
        parts.extend(fn(bmesh, mats))
    head_obj, eyes_obj = H.build_head(bpy, bmesh, mats)
    parts.extend([head_obj, eyes_obj, HR.build_hair(bmesh, mats)])
    p = C.PARTS['Neck']; bm = bmesh.new()      # neck is still an ellipsoid placeholder
    kit.add_super(bm, p['c'], p['r'], seg=36, rings=24)
    placeholders = [kit.finish('Neck_placeholder', bm, [mats['skin']])]
    return mats, parts, placeholders
