"""Chibi Mall Guide v5: single source of numbers (blockout stage).

Units: metres, Blender space (Z up, character faces -Y; exports to glTF +Z). Character about 1.00 m tall, feet on z = 0.
Every value is a starting value measured from reference sheet B's front and side silhouettes (blockout/sheet-b-silhouette.json,
751 px = 1.00 m). They are not final design values.
"""
HEIGHT = 1.00
SHEET_PX_PER_M = 751.0   # sheet B front view: cap top to sole = 751 px

def z_of_row(row):       # sheet row (0 = cap top) -> height in metres
    return HEIGHT - row / SHEET_PX_PER_M

# parts: name -> dict of ellipsoid parameters (centre, radii); head uses separate top/bottom z radii
# Side view of sheet B: origin y = 0 sits at sheet x = 150 (torso, legs and shoes centre there; the head and hair mass sit about
# 0.083 m behind it). Rows read from the sheet: vest rows 369..529, shorts 529..599, socks 619..689, shoes 689..751 (cap top = row 0).
PARTS = {
    'Cap':    dict(c=(0, 0.073, 0.948), r=(0.135, 0.130, 0.052)),
    'Head':   dict(c=(0, 0.073, 0.700), r=(0.250, 0.235, 0.226), rz_bot=0.185, p_bot=2.3),
    'Neck':   dict(c=(0, 0.010, 0.480), r=(0.058, 0.058, 0.055)),
    'Torso':  dict(c=(0, -0.010, 0.380), r=(0.105, 0.105, 0.090), p_bot=3.0),
    'Shorts': dict(c=(0, 0.000, 0.250), r=(0.098, 0.098, 0.056), p_bot=5.0, p_top=3.0),
    'Arm':    dict(c=(0.125, 0.013, 0.350), r=(0.036, 0.040, 0.100), mirror=True),
    'Hand':   dict(c=(0.130, 0.040, 0.248), r=(0.042, 0.042, 0.050), mirror=True),
    'Leg':    dict(c=(0.050, 0.013, 0.140), r=(0.044, 0.044, 0.075), mirror=True),
    'Shoe':   dict(c=(0.055, 0.005, 0.040), r=(0.063, 0.092, 0.040), mirror=True, p_bot=6.0),
}

# gate thresholds, set before the first comparison (G4-style): v4 used mean 8 px / max 15 px at 645 px per metre
GATE_MEAN_M = 8 / 645.0
GATE_MAX_M = 15 / 645.0

# ---- step 5: palette (sRGB hex, sampled from sheet B front view with parts_palette.py; shoe jade reuses the vest value
# because the sampled spot landed on ivory; hair is not used yet) ----
PALETTE = {
    'jade': '4D6752', 'ivory': 'F3E0CC', 'charcoal': '40363B', 'skin': 'D19E85', 'white': 'FBF3F2', 'brass': 'E3B553',
    'sole': 'E6D1BC', 'cap_jade': '56735C', 'hair': '4A2C22',
    'eye_dark': '2A160C', 'brow': '3A2218', 'mouth_red': '8C2A34', 'blush': 'F0A39B',   # step 6 face colours (read by eye from sheet B, not sampled)
}

# ---- step 5: detail dimensions (m), starting values read from sheet B; Blender space, character's left = +X ----
ARM_PATH = [(0.122, 0.000, 0.435), (0.140, 0.018, 0.345), (0.146, 0.035, 0.275)]   # shoulder, elbow, wrist
ARM_RADII = [0.031, 0.029, 0.026]
VEST = dict(c=(0.0, -0.010, 0.380), r=(0.095, 0.111, 0.096), z_hem=0.300, z_neck=0.445, armhole_z=0.435, armhole_r=0.058, thick=0.004)
SHIRT = dict(c=(0.0, -0.010, 0.380), r=(0.084, 0.098, 0.084), z_hem=0.310, z_neck=0.435, armhole_r=0.052, sleeve_to_z=0.350)
SHORTS = dict(c=(0.0, 0.0, 0.250), r=(0.094, 0.094, 0.056), leg_r=0.050, z_hem=0.195, leg_x=0.058)
LEG = dict(x=0.058, y=0.013, z_top=0.205, z_sock=0.165, z_bot=0.075, r_top=0.040, r_bot=0.036, sock_r=0.044)
SHOE = dict(x=0.062, y=0.005)
CAP = dict(c=(0.0, 0.079, 0.935), r=(0.135, 0.130, 0.065), z_rim=0.887, shear=0.45)   # top at z = 1.00 so the figure is 1.00 m tall like sheet B's 751 px


# ---- step 6: head (skull plus patches on its surface). Face landmarks read from sheet B front view (cap top = row 0):
# eyes about row 274 (z 0.635), brows row 199, mouth row 324, chin row 360. x offsets are about +/-0.08 for the eyes.
HEAD = dict(c=(0.0, 0.057, 0.700), r=(0.200, 0.188, 0.180), rz_bot=0.175, p_bot=3.2)
EYE = dict(x=0.080, z=0.640, a=0.050, b=0.054, lift=0.006)
BROW = dict(x=0.080, z=0.735, hw=0.042, th=0.009, arch=0.008, lift=0.003)
MOUTH = dict(x=0.0, z=0.570, hw=0.040, depth=0.022, corner=0.010, lift=0.0015)
CHEEK = dict(x=0.105, z=0.562, r=0.028, lift=0.002)
NOSE = dict(z=0.612, r=(0.011, 0.010, 0.009))
EAR = dict(x=0.203, y=0.055, z=0.600, r=(0.016, 0.026, 0.034))


# ---- step 7b: hair locks (layered, swept along the skull). Each lock: (azimuth start, elevation start, azimuth end, elevation end,
# swirl in degrees added to the azimuth mid-path, half width, half thickness, offset from the skull), angles in degrees, lengths in m.
# Layer A (ten locks) covers the skull from the crown down; layer B (eight locks) sits on top and overlaps A's seams.
HAIR_TAPER = 0.35    # profile exponent of sin(pi t): smaller = blunter, fuller ends
HAIR_END_MIN = 0.22  # width and thickness never fall below this fraction at the ends, so the ends are blunt, not pointed
HAIR_SIDES = 12
HAIR_STEPS = 12      # samples along each lock
HAIR_CAP_RINGS = 2   # rings of the rounded cap at each end
FRINGE = {'taper': 0.25, 'endmin': 0.5}      # fuller, blunter ends for the fringe locks (the thin ends read as a spike from the side)
FRINGE_B = {'taper': 0.25, 'endmin': 0.5}
HAIR_LOCKS = [
    # layer A (the optional ninth value flares the lower end outward, in m)
    (0, 78, 0, 9, 0, 0.054, 0.034, 0.002, 0.016, FRINGE),
    (32, 76, 38, 21, 6, 0.056, 0.034, 0.002, 0.014, FRINGE),
    (-32, 76, -38, 21, -6, 0.056, 0.034, 0.002, 0.014, FRINGE),
    (62, 74, 84, -18, -10, 0.070, 0.034, 0.006, 0.012),
    (-62, 74, -84, -18, 10, 0.070, 0.034, 0.006, 0.012),
    (100, 72, 112, -22, 0, 0.070, 0.036, 0.004, 0.015),
    (-100, 72, -112, -22, 0, 0.070, 0.036, 0.004, 0.015),
    (140, 72, 126, -25, 8, 0.085, 0.040, 0.002, -0.014),
    (-140, 72, -126, -25, -8, 0.085, 0.040, 0.002, -0.014),
    (180, 70, 180, -42, 0, 0.095, 0.036, 0.002, -0.018),
    # layer B
    (16, 72, 14, 22, 0, 0.042, 0.028, 0.012, 0.004, FRINGE_B),
    (-16, 72, -14, 22, 0, 0.042, 0.028, 0.012, 0.004, FRINGE_B),
    (48, 70, 56, 30, 0, 0.044, 0.024, 0.012),
    (-48, 70, -56, 30, 0, 0.044, 0.024, 0.012),
    (80, 66, 92, 10, 0, 0.050, 0.026, 0.012, 0.020),
    (-80, 66, -92, 10, 0, 0.050, 0.026, 0.012, 0.020),
    (160, 62, 165, 8, 0, 0.060, 0.026, 0.016),
    (-160, 62, -165, 8, 0, 0.060, 0.026, 0.016),
]


# ---- step 8: global hair multipliers (used by the target fit; neutral values are 1, 0, 1) ----
HAIR_T_MULT = 1.0    # scales every lock's thickness
HAIR_W_MULT = 1.0    # scales every lock's width
HAIR_OFF_ADD = 0.0   # added to every lock's offset from the skull (m)

# ---- step 8: optional overrides found by trellis-trial/fit_to_target.py; applied last so they win ----
import json as _json, os as _os
_FIT = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'fit.json')
if _os.path.exists(_FIT):
    for _k, _v in _json.load(open(_FIT)).items():
        if _k in globals():
            if isinstance(globals()[_k], dict):
                for _kk, _vv in _v.items(): globals()[_k][_kk] = tuple(_vv) if isinstance(_vv, list) else _vv
            elif isinstance(globals()[_k], list): globals()[_k] = [tuple(x) for x in _v]
            else: globals()[_k] = _v
