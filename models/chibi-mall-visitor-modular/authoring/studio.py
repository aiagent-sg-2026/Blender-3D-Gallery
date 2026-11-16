"""Soft portrait studio in metres. These objects live outside the export selection."""
import math
import bpy
from mathutils import Vector

def aim(o,target):
    o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler()

def camera(coll,name,angle,height=.647,pitch=.07):
    cam=bpy.data.cameras.new(name); o=bpy.data.objects.new(name,cam);coll.objects.link(o)
    angle=math.radians(angle); o.location=(3*math.sin(angle),-3*math.cos(angle),height+3*math.sin(pitch))
    aim(o,(0,0,height));cam.type="ORTHO";cam.ortho_scale=1.51
    return o

def setup(scene,coll):
    world=bpy.data.worlds.new("Lavender studio");world.use_nodes=True
    bg=world.node_tree.nodes.get("Background")
    bg.inputs[0].default_value=(.71,.73,.88,1);bg.inputs[1].default_value=.29
    scene.world=world
    for name,position,color,power,size in (
        ("Large softbox",(-1.55,-2.25,2.95),(1.,.91,.83),155,1.8),
        ("Fill",(1.65,-1.55,1.72),(.84,.90,1.),52,1.7),
        ("Hair light",(1.16,1.14,2.5),(1.,.88,.80),140,1.4)):
        lamp=bpy.data.lights.new(name,"AREA");o=bpy.data.objects.new(name,lamp);coll.objects.link(o)
        o.location=position;aim(o,(0,0,.78));lamp.energy=power;lamp.shape="DISK";lamp.size=size;lamp.color=color
    floor=bpy.data.meshes.new("Backdrop")
    floor.from_pydata([(-120,-120,-.0015),(120,-120,-.0015),(120,120,-.0015),(-120,120,-.0015)],[],[(0,1,2,3)])
    obj=bpy.data.objects.new("Studio floor",floor);coll.objects.link(obj)
    mat=bpy.data.materials.new("Studio • pale heather");mat.use_nodes=True
    bs=mat.node_tree.nodes.get("Principled BSDF");bs.inputs["Base Color"].default_value=(.68,.66,.77,1)
    bs.inputs["Roughness"].default_value=.88
    bs.inputs["Emission Color"].default_value=(.64,.62,.76,1)
    lightpath=mat.node_tree.nodes.new("ShaderNodeLightPath")
    mat.node_tree.links.new(lightpath.outputs["Is Camera Ray"],bs.inputs["Emission Strength"])
    floor.materials.append(mat)
    for n,a in (("Front",0),("Quarter",-35),("Side",90),("Back",180)):
        cam=camera(coll,n,a,pitch=.045 if n=="Quarter" else 0)
        if n=="Quarter":scene.camera=cam
    scene.render.engine="CYCLES";scene.cycles.samples=36;scene.cycles.use_denoising=True
    scene.view_settings.view_transform="Khronos PBR Neutral";scene.view_settings.look="None"
    scene.render.resolution_x=800;scene.render.resolution_y=900;scene.render.resolution_percentage=100
    return scene.camera

