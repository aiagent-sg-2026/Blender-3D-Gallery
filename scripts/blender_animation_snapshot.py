"""Snapshot active rigid Object actions; reject unsupported NLA/drivers."""
import bpy, hashlib, json
from array import array

def action_curves(action):
    if hasattr(action, 'fcurves'):
        return list(action.fcurves)
    return [curve for layer in action.layers for strip in layer.strips
            for bag in strip.channelbags for curve in bag.fcurves]

def animation_snapshot():
    digest = hashlib.sha256()
    def add(value):
        digest.update(json.dumps(value, sort_keys=True).encode())
    bindings = []
    for obj in sorted(bpy.data.objects, key=lambda o: o.name):
        data = obj.animation_data
        if not data:
            continue
        assert not data.nla_tracks and not data.drivers, 'NLA/drivers require separate source preservation review'
        bindings.append({'object':obj.name, 'action':data.action.name if data.action else None,
                         'slot':data.action_slot.identifier if getattr(data, 'action_slot', None) else None,
                         'blend_type':data.action_blend_type, 'influence':data.action_influence,
                         'extrapolation':data.action_extrapolation, 'use_nla':data.use_nla})
    add(bindings)
    curves = keys = 0
    for action in sorted(bpy.data.actions, key=lambda a: a.name):
        add({'action':action.name, 'frame_range':list(action.frame_range),
             'slots':[(s.identifier,s.handle,s.target_id_type) for s in getattr(action,'slots',[])],
             'layers':[(l.name,[(s.type,[(b.slot_handle,len(b.fcurves)) for b in s.channelbags]) for s in l.strips]) for l in getattr(action,'layers',[])]})
        for fc in action_curves(action):
            assert not fc.modifiers, 'Action modifiers require separate review'
            assert not fc.sampled_points, 'Sampled curves require separate review'
            add([fc.data_path,fc.array_index,fc.extrapolation,fc.mute,fc.group.name if fc.group else None])
            for attr,width in [('co',2),('handle_left',2),('handle_right',2)]:
                values=array('f',[0.0])*(len(fc.keyframe_points)*width)
                fc.keyframe_points.foreach_get(attr,values);digest.update(values.tobytes())
            add([(k.interpolation,k.easing,k.handle_left_type,k.handle_right_type,k.amplitude,k.back,k.period) for k in fc.keyframe_points])
            curves+=1;keys+=len(fc.keyframe_points)
    scene=bpy.context.scene
    add([scene.frame_start,scene.frame_end,scene.render.fps,scene.render.fps_base])
    return {'schema':'active-rigid-object-actions-v1','sha256':digest.hexdigest(),
            'actions':len(bpy.data.actions),'curves':curves,'keyframes':keys,'bindings':bindings}
