"""Independent editable volume study made from the front and profile landmarks."""
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from studio import camera

def generate(out):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    out.mkdir(parents=True,exist_ok=True)
    sc=bpy.context.scene;sc.name="Proportion study";sc["expressionPresets"]={"default":{}};sc["clipInfo"]={}
    mat=bpy.data.materials.new("Clay");mat.diffuse_color=(.55,.51,.55,1.)
    def ell(name,center,radius,rot=0):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,location=center)
        o=bpy.context.object;o.name=name;o["partSlot"]="Study"
        o.scale=radius;o.rotation_euler.y=rot
        for f in o.data.polygons:f.use_smooth=True
        o.data.materials.append(mat)
    ell("Skull",(0,.002,1.027),(.200,.19,.227))
    ell("Hair mass",(0,.014,1.124),(.241,.211,.176))
    ell("Fringe sweep",(-.066,-.153,1.136),(.138,.058,.067),-.39)
    ell("Part return",(.103,-.134,1.131),(.081,.059,.071),.54)
    ell("Nose",(0,-.180,.914),(.018,.022,.014))
    ell("Neck",(0,0,.763),(.056,.052,.058))
    ell("Chest",(0,0,.611),(.139,.093,.163))
    ell("Pelvis",(0,.006,.447),(.143,.094,.083))
    ell("Pack",(0,.139,.586),(.116,.076,.138))
    for s in (-1,1):
        ell("Eye",(s*.084,-.168,.960),(.046,.016,.043))
        ell("Ear",(s*.189,-.024,.930),(.037,.031,.051))
        ell("Sleeve",(s*.141,0,.672),(.064,.066,.085),-s*.31)
        ell("Arm",(s*.180,-.010,.559),(.035,.034,.102),-s*.24)
        ell("Hand",(s*.209,-.032,.418),(.035,.031,.052))
        ell("Denim leg",(s*.084,.006,.270),(.079,.081,.198),-s*.04)
        ell("Cuff",(s*.092,.004,.113),(.079,.082,.024))
        ell("Sneaker",(s*.095,-.036,.053),(.077,.124,.053))
    sc.camera=camera(sc.collection,"Study camera",0,pitch=0)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/"01-blockout.blend"),compress=True)
    bpy.ops.object.select_all(action="DESELECT")
    for o in sc.objects:
        if o.type=="MESH":o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(out/"01-blockout.glb"),export_format="GLB",export_extras=True,
                              use_selection=True,export_animations=False)

if __name__=="__main__":generate(Path(sys.argv[-1]).resolve())

