"""Single source of truth for every number used by the GJH Chibi Visitor build.

Units are metres. Blender axes: +Z up, the character faces -Y, and the
character's left side is +X (it appears on the right of a front view).
Feet rest on z = 0 and the figure is centred on x = 0, y = 0 (leg centre).
The glTF exporter converts this to +Y up with the character facing +Z.

Landmarks were measured from the owner's character sheet v1.0 masks
(front, side and back views, about 350 px per metre); see reference/.
"""

ASSET_ID = "gjh-chibi-visitor"

# ---------------------------------------------------------------- reference
REF_SHEET = "character-sheet-v1.webp"
# Crop boxes in sheet pixels (x0, y0, x1, y1), top-left origin, and the row
# where floor shadow starts (anything at or below it is cut from the mask).
REF_VIEWS = {
    "front": {"crop": (270, 44, 512, 518), "floor_row": 506},
    "side": {"crop": (748, 44, 972, 518), "floor_row": 506},
    "back": {"crop": (978, 44, 1186, 518), "floor_row": 506},
}
REF_BG_STRIP = 6          # border columns used to estimate the background per row
REF_BG_DISTANCE = 20.0    # max channel difference still counted as background
REF_BG_TINT_GAP = 7.0     # max (blue - red) tint difference still counted as background
REF_MAX_HEIGHT_SPREAD = 0.02
# Rows of the leg band (metres) used to align model and sheet horizontally.
REF_ALIGN_BAND = (0.18, 0.30)
# The white sneakers match the background colour, so the sheet mask is not
# trusted below this height; silhouette gates ignore those rows.
REF_TRUST_MIN_Z = 0.10

# ---------------------------------------------------------------- overall
HEIGHT = 1.30
TRI_BUDGET_MIN = 3000
TRI_BUDGET_MAX = 8000
DRAW_CALL_MAX = 10

# ---------------------------------------------------------------- head (skull)
HEAD_CENTER = (0.0, 0.0, 1.005)
HEAD_RADII = (0.195, 0.212, 0.212)      # x (half width), y (half depth), z (half height)
HEAD_SEGMENTS = 22                       # around
HEAD_RINGS = 15                          # pole to pole
CHIN_Z = 0.795
JAW_START_Z = 0.862                      # below this the lower face narrows to the chin
JAW_MIN_SCALE = 0.60                     # width scale at the chin
CHEEK_PUFF = 0.018                       # extra cheek fullness at the front-sides
CHEEK_Z = 0.880
FACE_FLATTEN = 0.97                      # front of face flattened in depth (scale of y radius)
LOWER_FORWARD = 0.065                    # lower face pulled forward (chibi cheeks and chin)
HEAD_ROUNDNESS = (0.96, 0.74)            # cos(lat) exponent above / below the centre (boxier < 1)
EAR_CENTER = (0.196, 0.018, 0.896)
EAR_SIZE = (0.026, 0.044, 0.073)          # thickness, depth, height

NECK_RADIUS = 0.050
NECK_BOTTOM_Z = 0.72
NECK_TOP_Z = 0.86
NECK_CENTER_Y = 0.005

# ---------------------------------------------------------------- face decals
EYE_CENTER = (0.085, 0.950)              # x (+/-), z
EYE_SIZE = (0.084, 0.098)                # width, height
BROW_CENTER = (0.092, 1.022)
BROW_SIZE = (0.072, 0.022)               # length, thickness
BROW_ARCH = 0.008
MOUTH_CENTER = (0.0, 0.868)
MOUTH_WIDTH = 0.050
MOUTH_LINE = 0.0065                      # closed smile line thickness
MOUTH_CURVE = 0.010                      # smile curvature (corners up)
BLUSH_CENTER = (0.108, 0.884)
BLUSH_SIZE = (0.046, 0.024)
NOSE_CENTER = (0.0, 0.905)
NOSE_SIZE = (0.011, 0.007, 0.009)       # bump half width, half depth, half height
FACE_ATLAS_SIZE = 512

# ---------------------------------------------------------------- torso / tee
# Tee cross sections: (z, half width, front y, back y, superellipse power).
TEE_SECTIONS = [
    (0.435, 0.166, -0.136, 0.094, 2.6),
    (0.500, 0.144, -0.124, 0.090, 2.6),
    (0.560, 0.140, -0.124, 0.088, 2.6),
    (0.620, 0.144, -0.120, 0.090, 2.8),
    (0.675, 0.143, -0.108, 0.086, 2.8),
    (0.722, 0.122, -0.086, 0.076, 2.4),
    (0.756, 0.086, -0.060, 0.062, 2.2),
]
TEE_SEGMENTS = 20
COLLAR_INNER = 0.054                     # collar hole radius
COLLAR_Z = 0.765
SLEEVE_ROOT = (0.122, 0.0, 0.706)        # shoulder point on the tee
SLEEVE_END = (0.180, -0.004, 0.600)
SLEEVE_RADII = ((0.045, 0.047), (0.047, 0.050))   # (x/y radii) at root and end
SLEEVE_SEGMENTS = 12

# ---------------------------------------------------------------- arms
SHOULDER_JOINT = (0.130, 0.0, 0.700)
ELBOW = (0.187, 0.004, 0.556)
WRIST = (0.203, -0.002, 0.466)
FINGER_TIP = (0.209, -0.008, 0.346)
ARM_RADII = (0.037, 0.033, 0.029)        # upper, elbow, wrist
ARM_SEGMENTS = 10
THUMB_BASE = (0.006, -0.026, 0.436)      # x/y offset from the wrist joint, absolute z
THUMB_TIP = (0.000, -0.038, 0.404)

# ---------------------------------------------------------------- jeans
JEANS_WAIST_Z = 0.458
JEANS_HIP = (0.150, -0.102, 0.090)       # half width, front y, back y at the waist
CROTCH_Z = 0.330
# Leg sections from the crotch down: (z, centre x, half width, half depth).
LEG_SECTIONS = [
    (0.330, 0.083, 0.076, 0.100),
    (0.270, 0.0835, 0.077, 0.0995),
    (0.240, 0.084, 0.0785, 0.0990),
    (0.215, 0.0848, 0.0805, 0.0993),
    (0.190, 0.0855, 0.083, 0.0997),
    (0.165, 0.086, 0.0855, 0.100),
    (0.150, 0.087, 0.0885, 0.101),
]
CUFF = (0.110, 0.160, 0.010)
DENIM_TILE_M = 0.30                      # metres of jeans per denim texture repeat             # bottom z, top z, extra radius
LEG_SEGMENTS = 12

# ---------------------------------------------------------------- shoes
SHOE_CENTER_X = 0.090
SHOE_LENGTH = 0.285
SHOE_CENTER_Y = -0.030
SHOE_HEIGHT = 0.110
SOLE_HEIGHT = 0.028
SHOE_SEGMENTS = 10

# ---------------------------------------------------------------- backpack
PACK_CENTER = (0.0, 0.160, 0.578)
PACK_SIZE = (0.118, 0.062, 0.136)        # half width, half depth, half height
POCKET_SIZE = (0.088, 0.016, 0.058)
POCKET_Z = 0.522
STRAP_WIDTH = 0.030
STRAP_THICKNESS = 0.008

# ---------------------------------------------------------------- watch
WATCH_Z = 0.478
WATCH_RADIUS = 0.030
WATCH_WIDTH = 0.016
WATCH_FACE = (0.030, 0.036, 0.007)       # width, length, thickness

# ---------------------------------------------------------------- hair
# Tables are keyed by the front factor f = -sin(phi): 1 front, 0 sides, -1 back.
HAIR_SHELL_SEGMENTS = 18
HAIR_SHELL_RINGS = 7
HAIRLINE_DEG = [(-1.0, -40.0), (-0.5, -28.0), (0.0, -8.0), (0.3, -6.0), (0.6, 0.0), (1.0, 30.0)]
HAIR_MASS = [(-1.0, 0.080), (0.0, 0.068), (0.6, 0.072), (1.0, 0.085)]  # hair thickness over the skull
HAIR_EDGE = [(-1.0, 0.020), (0.0, 0.016), (0.6, 0.026), (1.0, 0.040)]  # thickness at the hairline
HAIR_CROWN = 0.076
HAIR_CROWN_TRIM_BAND = (0.55, 0.95)       # fraction of cap height where the crown is trimmed
HAIR_CROWN_TRIM_LEFT = 0.40
HAIR_CROWN_TRIM_BACK = 0.30
HAIR_FADE = 0.45                         # fraction of the cap height used to reach full mass
HAIR_DROP_DEG = 25.0                     # below the hairline, thickness falls to the skin over this
HAIR_LOCK_SEGMENTS = 6
HAIR_LOCK_STEPS = 3
HAIR_LOCK_POWER = 2.2                   # lens-shaped section: pointed sides, rounded faces
LOCK_WIDTH_PROFILE = [(0.0, 0.85), (0.3, 1.0), (0.65, 0.88), (0.88, 0.62), (1.0, 0.40)]
LOCK_THICK_PROFILE = [(0.0, 0.80), (0.3, 1.0), (0.8, 0.70), (1.0, 0.50)]
LOCK_ROOT_SINK = 0.9                     # root depth into the cap, as a fraction of lock thickness

# Shingle rows of locks radiating from the crown. Tips either sit at an absolute
# latitude (tip_theta) or a fixed number of degrees above the local hairline.
# gap: longitudes (deg) left to the hand-placed fringe.
HAIR_ROWS = [
    dict(count=8, phi0=10.0, tip_theta=46.0, length_deg=36.0, width=0.109, thick=0.030, lift=0.002, sweep=14.0,
         gap=(-125.0, -55.0)),
    dict(count=10, phi0=-8.0, tip_above_hairline=24.0, length_deg=46.0, width=0.115, thick=0.030, lift=0.006,
         sweep=12.0, gap=(-125.0, -55.0)),
    dict(count=13, phi0=8.0, tip_above_hairline=-3.0, length_deg=46.0, width=0.106, thick=0.027, lift=0.006,
         sweep=10.0, gap=(-140.0, -40.0)),
]
# Swept fringe (front view: big locks sweep to the image left, one long lock to the right).
HAIR_FRINGE = [
    dict(root=(68, -80), mid=(42, -98), tip=(17, -128), width=0.109, thick=0.034, lift=0.004),
    dict(root=(66, -88), tip=(15, -100), width=0.098, thick=0.032),
    dict(root=(60, -112), tip=(8, -150), width=0.098, thick=0.032, lift=0.012),
    dict(root=(64, -72), tip=(7, -52), width=0.098, thick=0.032, lift=0.006),
    dict(root=(55, -50), tip=(-12, -30), width=0.092, thick=0.029, lift=0.010),
    dict(root=(66, -100), tip=(16, -112), width=0.090, thick=0.030),
    dict(root=(63, -76), tip=(17, -80), width=0.088, thick=0.030),
]
# Nape: two locks meeting in a V at the back of the neck; one big outward flick
# above the character's right ear (the sheet's front view shows it clearly).
HAIR_EXTRA = [
    dict(root=(32, 196), tip=(-4, 186), width=0.100, thick=0.030, lift=0.034),
    dict(root=(-8, 76), tip=(-46, 88), width=0.081, thick=0.026, lift=0.004),
    dict(root=(-8, 104), tip=(-46, 92), width=0.081, thick=0.026, lift=0.004),
]

# ---------------------------------------------------------------- rig (left side; mirrored)
RIG_HIPS = (0.0, 0.0, 0.400)
RIG_SPINE = (0.0, 0.0, 0.500)
RIG_CHEST = (0.0, 0.0, 0.600)
RIG_NECK = (0.0, 0.005, 0.745)
RIG_HEAD = (0.0, 0.005, 0.800)
RIG_HEAD_END = (0.0, 0.005, 1.150)
RIG_CLAVICLE = (0.030, 0.0, 0.715)
RIG_HIP_JOINT = (0.083, 0.0, 0.400)
RIG_KNEE = (0.085, -0.006, 0.215)
RIG_ANKLE = (0.088, 0.035, 0.068)
RIG_TOE = (0.088, -0.110, 0.030)

# ---------------------------------------------------------------- colours (sRGB hex)
PALETTE = {
    "skin": "#F3D2B5",
    "hair": "#2E2420",
    "tee": "#F6F6F4",
    "jeans": "#4A6FB0",
    "cuff": "#6E8FC9",
    "shoe": "#F2F2F0",
    "sole": "#C6C7CC",
    "backpack": "#2C2E33",
    "watch": "#26272B",
    "iris": "#3A2418",
    "brow": "#2A1E1A",
    "mouth": "#7A3A34",
    "blush": "#F2A99A",
}
ROUGHNESS = {
    "skin": 0.6, "hair": 0.70, "tee": 0.85, "jeans": 0.9, "shoe": 0.7,
    "sole": 0.75, "backpack": 0.75, "watch": 0.4, "face": 0.5,
}

# ---------------------------------------------------------------- render / QA
RENDER_PX_PER_M = 350.0
SILHOUETTE_MEAN_MAX_PX = 8.0
SILHOUETTE_MAX_PX = 15.0
BLOCKOUT_IOU_MIN = 0.85
BODY_IOU_MIN = 0.88
LANDMARK_TOLERANCE = 0.02
