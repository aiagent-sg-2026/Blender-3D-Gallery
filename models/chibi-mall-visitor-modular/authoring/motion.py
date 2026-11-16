"""A shared humanoid skeleton, world-space two-link IK and editable Blender Actions."""
import math
import bpy
from mathutils import Vector, Quaternion, Euler, Matrix
from config import BONES, SOCKETS, FPS, CLIPS, PICKUP_ROTATION_DEG
from meshkit import clamp, mix

IDENT=Quaternion()
BIND={n:(Vector(h),Vector(t),par) for n,h,t,par in BONES}
PICK=(-.149,-.218,.409)
CHIN=(-.045,-.141,.803)
GAIT={"walk":(.145,.55,.045,.028),"run":(.222,.49,.086,.063)}

def quat(x=0,y=0,z=0):
    return Euler(tuple(map(math.radians,(x,y,z))),"XYZ").to_quaternion()

def smooth(x):
    x=clamp(x); return x*x*(3-2*x)

def envelope(t,on=.28,off=.78):
    return smooth(t/on)*smooth((1-t)/(1-off))

def make_rig(coll):
    rig=bpy.data.objects.new("Visitor_Rig",bpy.data.armatures.new("Visitor • humanoid"))
    coll.objects.link(rig); bpy.context.view_layer.objects.active=rig; rig.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    for name,head,tail,parent in BONES:
        b=rig.data.edit_bones.new(name); b.head=head; b.tail=tail
        if parent:b.parent=rig.data.edit_bones[parent]
    bpy.ops.object.mode_set(mode="OBJECT")
    rig.data.display_type="STICK"; rig.show_in_front=False
    bpy.context.view_layer.update()
    for name,(joint,where) in SOCKETS.items():
        obj=bpy.data.objects.new(name,None); coll.objects.link(obj)
        obj.empty_display_type="SPHERE"; obj.empty_display_size=.008
        obj.parent=rig; obj.parent_type="BONE"; obj.parent_bone=joint
        bpy.context.view_layer.update()
        obj.matrix_world=Matrix.Translation(where)
        obj["attachment"]=name
    return rig

class Pose:
    def __init__(self,rotations,shift):
        self.rotation={}; self.position={}; self.offset=Vector(shift)
        for name,(h,_,parent) in BIND.items():
            pd=self.rotation.get(parent,IDENT)
            self.position[name]=(self.position[parent]+pd@(h-BIND[parent][0]) if parent else h.copy())
            if name=="pelvis": self.position[name]+=self.offset
            self.rotation[name]=pd@rotations.get(name,IDENT)

    def solve(self,upper,lower,end,target,pole,end_rotation=None):
        # Solve the elbow/knee plane in armature coordinates, preserving segment lengths.
        h=self.position[upper]; dest=Vector(target)-h; direction=dest.normalized()
        first=BIND[lower][0]-BIND[upper][0]; second=BIND[end][0]-BIND[lower][0]
        l1,l2=first.length,second.length
        distance=clamp(dest.length,abs(l1-l2)+1e-6,l1+l2-1e-6)
        along=(l1*l1-l2*l2+distance*distance)/(2*distance)
        perpendicular=Vector(pole)-direction*Vector(pole).dot(direction); perpendicular.normalize()
        joint=h+direction*along+perpendicular*math.sqrt(max(0,l1*l1-along*along))
        parent_rot=self.rotation[BIND[upper][2]]
        self.rotation[upper]=(parent_rot@first).rotation_difference(joint-h)@parent_rot
        self.position[lower]=joint
        wrist=h+direction*distance
        upper_rot=self.rotation[upper]
        self.rotation[lower]=(upper_rot@second).rotation_difference(wrist-joint)@upper_rot
        self.position[end]=wrist
        self.rotation[end]=end_rotation if end_rotation is not None else self.rotation[lower]

    def hand(self,side,target,orient,power):
        upper,lower,end=[n+"."+side for n in ("upperarm","forearm","hand")]
        target=self.position[end].lerp(Vector(target),power)
        hand=self.rotation[end].slerp(orient,power)
        self.solve(upper,lower,end,target,((1 if side=="L" else -1)*.8,.25,-.55),hand)

def make_pose(name,t):
    a=t*math.tau; sin=math.sin; cos=math.cos
    r={}; shift=(0,0,0); up=envelope(t)
    if name=="idle":
        r={"chest":quat(1.15*sin(a)),"head":quat(-.9*sin(a),.75*sin(a),1.5*sin(a))}
    elif name in GAIT:
        run=name=="run"
        span,duty,h,drop=GAIT[name]
        shift=(.008*sin(a),0,-drop+.005*cos(2*a))
        r={"pelvis":quat(0,0,2.3*sin(a)),"chest":quat(5 if run else 1,0,-4*sin(a)),
           "head":quat(-3 if run else -1,0,2*sin(a))}
        for sign,side in ((1,"L"),(-1,"R")):
            r["upperarm."+side]=quat(sign*(32 if run else 20)*cos(a),-sign*(3 if run else 0))
            r["forearm."+side]=quat((-45 if run else -11)+sign*(13 if run else 7)*cos(a))
    elif name=="talk":
        r={"head":quat(3*sin(2*a),2*sin(a),4*sin(a)),
           "upperarm.R":quat(-11*(1-cos(a))*.5,3*(1-cos(a))),
           "forearm.R":quat(-25*(1-cos(a))*.5)}
    elif name=="browse":
        k=(1-cos(a))*.5
        r={"chest":quat(3*k,0,12*sin(a)),"head":quat(6*k,-3*sin(a),20*sin(a)),
           "forearm.L":quat(-17*k)}
    elif name=="sit":
        up=smooth(t/.86); shift=(0,.093*up,-.174*up)
        r={"spine":quat(6*up),"chest":quat(3*up),"upperarm.L":quat(-28*up),
           "upperarm.R":quat(-28*up),"forearm.L":quat(-24*up),"forearm.R":quat(-24*up)}
    elif name=="wave":
        r={"clavicle.L":quat(0,-8*up),"upperarm.L":quat(-18*up,-65*up),
           "forearm.L":quat(-37*up,(-78+13*sin(3*a))*up),"hand.L":quat(0,15*sin(3*a)*up),
           "head":quat(0,-4*up,4*up)}
    elif name=="pick_up":
        up=envelope(t,.295,.65); shift=(0,.008*up,-.077*up)
        r={"spine":quat(14*up),"chest":quat(15*up),"head":quat(9*up),
           "upperarm.L":quat(5*up,-7*up)}
    elif name in ("inspect","thinking"):
        up=1. if name=="thinking" else envelope(t,.37,.72)
        r={"head":quat((3 if name=="thinking" else 8)*up,4*up,-5*up),"chest":quat(2*up)}
    elif name=="point":
        r={"chest":quat(0,0,-6*up),"head":quat(-2*up,0,-8*up)}
    elif name=="nod":
        r={"neck":quat(4*up),"head":quat(11*sin(a*1.5)*up)}
    elif name=="cheer":
        for s,side in ((1,"L"),(-1,"R")):
            r["clavicle."+side]=quat(0,-s*9*up)
            r["upperarm."+side]=quat(-17*up,-s*103*up)
            r["forearm."+side]=quat(-26*up,-s*24*up)
        r["head"]=quat(-6*up)
    pose=Pose(r,shift)
    if name in (*GAIT,"pick_up","sit"):
        for s,side in ((1,"L"),(-1,"R")):
            foot="foot."+side; target=BIND[foot][0].copy(); pitch=0
            if name in GAIT:
                phase=(t+(.5 if s<0 else 0))%1.
                span,duty,lift,_=GAIT[name]
                if phase<duty: target.y+=span*(phase/duty-.5)
                else:
                    k=(phase-duty)/(1-duty)
                    target.y+=span*(.5-smooth(k))
                    target.z+=lift*sin(math.pi*k)**2
                    pitch=8*sin(math.tau*k)*sin(math.pi*k)
            pose.solve("thigh."+side,"shin."+side,foot,target,(s*.04,-1,0),quat(pitch))
    if name=="pick_up":
        swing=quat(*PICKUP_ROTATION_DEG)
        rest=Vector(SOCKETS["Socket_Palm_R"][1])-BIND["hand.R"][0]
        wrist=Vector(PICK)-swing@rest
        wrist.x-=.078*(1-smooth((t-.31)/.19))
        pose.hand("R",wrist,swing,up)
    elif name=="point":
        pose.hand("R",(-.19,-.196,.683),quat(-84,-8,5),up)
    elif name=="inspect":
        pose.hand("R",(-.117,-.148,.716),quat(-110,12,6),up)
    elif name=="thinking":
        from head import face_y
        rest_tip=Vector((-.205,-.056,.382))-BIND["hand.R"][0]
        cheek=Vector((-.067,face_y(-.067,.851)-.001,.851))
        target=pose.position["head"]+pose.rotation["head"]@(cheek-BIND["head"][0])
        wrist=target+Vector((-.026,.014,-.090))
        orientation=rest_tip.rotation_difference(target-wrist)
        wrist=target-orientation@rest_tip
        pose.hand("R",wrist,orientation,up)
    return pose

def motion_shapes(name,t):
    blink=max(0,1-abs(t-.67)/.048)
    if name=="idle":return {"blink_L":smooth(blink),"blink_R":smooth(blink)}
    if name=="talk":return {"open":(.5-.5*math.cos(t*math.tau*3))*(.46+.16*math.sin(t*math.tau)),
                            "round":.22*(.5-.5*math.cos(t*math.tau*2))}
    up=envelope(t)
    if name=="point":return {"point_R":up,"grip_R":.78*up}
    if name=="pick_up":
        grip=smooth((t-.50)/(.5625-.50))
        return {"pickup_open_R":smooth(t/.24)*(1-grip),"pickup_grasp_R":grip}
    if name=="inspect":return {"grip_R":.6*up}
    if name=="cheer":return {"grip_L":.72*up,"grip_R":.72*up,"open":.45*up,"smile":.72*up}
    return {}

def stash(owner,label):
    ad=owner.animation_data; action=ad.action
    track=ad.nla_tracks.new(); track.name=label
    strip=track.strips.new(label,0,action); strip.name=label
    ad.action=None; track.mute=True

def write_actions(rig,objects):
    bases={b.name:b.matrix_local.to_quaternion() for b in rig.data.bones}
    for name,(frames,_,_) in CLIPS.items():
        ad=rig.animation_data_create(); ad.action=bpy.data.actions.new(name)
        keyed=[]
        active=set(motion_shapes(name,.5))
        for obj in objects:
            sk=obj.data.shape_keys
            if not sk:continue
            keys=[k for k in sk.key_blocks if k.name in active]
            if keys:
                sk.animation_data_create().action=bpy.data.actions.new(name+" • "+obj.name)
                keyed.append((sk,keys))
        for f in range(frames+1):
            t=f/frames; pose=make_pose(name,t)
            for bone in rig.pose.bones:
                n=bone.name; par=BIND[n][2]; parent=pose.rotation.get(par,IDENT)
                bone.rotation_quaternion=bases[n].inverted()@parent.inverted()@pose.rotation[n]@bases[n]
                bone.keyframe_insert(data_path="rotation_quaternion",frame=f,group=n)
            pelvis=rig.pose.bones["pelvis"]; pelvis.location=bases["pelvis"].inverted()@pose.offset
            pelvis.keyframe_insert(data_path="location",frame=f,group="pelvis")
            values=motion_shapes(name,t)
            for sk,keys in keyed:
                for k in keys:
                    k.value=values[k.name]; k.keyframe_insert(data_path="value",frame=f)
        stash(rig,name)
        for sk,keys in keyed:
            stash(sk,name)
            for k in keys:k.value=0.
    for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4)
    bpy.context.scene.frame_set(0)
    return bases

