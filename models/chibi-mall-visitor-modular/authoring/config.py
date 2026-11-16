"""Metres, Blender Z up, front -Y, anatomical left +X."""
from math import pi

HEIGHT = 1.30
HAIR_RADII = (.250,.225,.224)
LANDMARKS = {"iris": .96, "chin": .80, "hem": .45, "cuff": .13}
PALETTE = {"skin": "FACFAA", "hair": "3A2F2B", "tee": "FEFEFE",
           "denim": "5D73B1", "shoe": "EDE8E9", "pack": "3D3A42", "watch": "323038"}
BUDGET = (3000, 8000)
FPS = 30
# Feature atlas rectangles, in top-down image pixels. Each tile includes a gutter.
HAIR_BAKE_RECT = (512, 0, 1024, 512)
TILES = {"face": (0, 256, 512, 628), "eye": (0, 0, 256, 256),
         "hair": HAIR_BAKE_RECT, "shirt": (256, 0, 448, 256), "knit": (448, 0, 512, 256),
         "jeanFront": (0, 628, 160, 1012), "jeanPlain": (160, 628, 320, 1012),
         "jeanBack": (320, 628, 512, 1012), "cuff": (512, 512, 640, 788),
         "pocket": (640, 512, 896, 714), "bag": (896, 512, 1024, 788),
         "shoe": (640, 714, 832, 916), "eyelets": (832, 714, 896, 916),
         "skin": (512, 788, 640, 904), "ear": (512, 904, 640, 1020),
         "strap": (896, 788, 1024, 962), "watch": (896, 962, 960, 1024),
         "glass": (960, 962, 1024, 1024), "sole": (640, 916, 768, 980),
         "laces": (768, 916, 896, 980), "lash": (640, 980, 672, 1024),
         "brow": (672, 980, 704, 1024), "lip": (704, 980, 736, 1024),
         "tongue": (736, 980, 768, 1024), "metal": (768, 980, 832, 1024),
         "teeth": (832, 980, 896, 1024)}
TILES["hairCap"] = TILES["hair"]
PRESETS = {
    "default": {},
    "happy": {"blink_L": 1., "blink_R": 1., "smile": .7, "open": .57, "cheeks": .6},
    "wink": {"blink_L": 1., "smile": .36, "cheeks": .28},
    "surprised": {"browUp": .95, "wide": .75, "open": .90, "round": .94},
    "thinking": {"browTilt": .9, "asym": .85},
    "excited": {"blink_L": 1., "blink_R": 1., "smile": 1., "open": 1., "cheeks": 1., "browUp": .31},
}
# Length in frames at FPS, loop flag, representative review frame (zero-based).
CLIPS = {"idle": (90, True, 28), "walk": (32, True, 8), "run": (22, True, 6),
         "talk": (60, True, 23), "browse": (96, True, 53), "sit": (42, False, 42),
         "wave": (60, False, 36), "pick_up": (64, False, 36), "inspect": (66, False, 37),
         "point": (45, False, 25), "nod": (36, False, 14), "cheer": (56, False, 32)}
BONES = [
    ("root", (0, 0, .005), (0, 0, .065), None),
    ("pelvis", (0, .005, .405), (0, .005, .495), "root"),
    ("spine", (0, .005, .495), (0, 0, .60), "pelvis"),
    ("chest", (0, 0, .60), (0, 0, .741), "spine"),
    ("neck", (0, 0, .741), (0, -.008, .812), "chest"),
    ("head", (0, -.008, .812), (0, 0, 1.19), "neck"),
]
for side, sign in (("L", 1), ("R", -1)):
    def pt(x, y, z):
        return (sign*x, y, z)
    shoulder, elbow, wrist, palm = pt(.122, 0, .713), pt(.174, -.004, .586), pt(.202, -.024, .493), pt(.215, -.038, .426)
    hip, knee, ankle, toe = pt(.072, .007, .425), pt(.082, -.003, .258), pt(.093, .003, .096), pt(.096, -.096, .043)
    for name, a, b, parent in [
        ("clavicle", pt(.025, 0, .705), shoulder, "chest"),
        ("upperarm", shoulder, elbow, "clavicle."+side), ("forearm", elbow, wrist, "upperarm."+side),
        ("hand", wrist, palm, "forearm."+side), ("thigh", hip, knee, "pelvis"),
        ("shin", knee, ankle, "thigh."+side), ("foot", ankle, toe, "shin."+side)]:
        BONES.append((name+"."+side, a, b, parent))
SOCKETS = {"Socket_Back": ("chest", (0, .097, .64)), "Socket_Wrist_L": ("forearm.L", (.208, -.024, .502)),
           "Socket_Palm_R": ("hand.R", (-.181, -.059, .405)), "Socket_Palm_L": ("hand.L", (.181, -.059, .405))}
PICKUP_ROTATION_DEG = (-10, -5, -4)
PICKUP_PRODUCT_SIZE = (.043, .049, .043)  # glTF axes, in metres

