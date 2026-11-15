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
    'sole': 'E6D1BC', 'cap_jade': '56735C', 'hair': '58382F',
}

# ---- step 5: detail dimensions (m), starting values read from sheet B; Blender space, character's left = +X ----
ARM_PATH = [(0.122, 0.000, 0.435), (0.140, 0.018, 0.345), (0.146, 0.035, 0.275)]   # shoulder, elbow, wrist
ARM_RADII = [0.031, 0.029, 0.026]
VEST = dict(c=(0.0, -0.010, 0.380), r=(0.095, 0.111, 0.096), z_hem=0.300, z_neck=0.445, armhole_z=0.435, armhole_r=0.058, thick=0.004)
SHIRT = dict(c=(0.0, -0.010, 0.380), r=(0.084, 0.098, 0.084), z_hem=0.310, z_neck=0.435, armhole_r=0.052, sleeve_to_z=0.350)
SHORTS = dict(c=(0.0, 0.0, 0.250), r=(0.094, 0.094, 0.056), leg_r=0.050, z_hem=0.195, leg_x=0.058)
LEG = dict(x=0.058, y=0.013, z_top=0.205, z_sock=0.165, z_bot=0.075, r_top=0.040, r_bot=0.036, sock_r=0.044)
SHOE = dict(x=0.062, y=0.005)
CAP = dict(c=(0.0, 0.073, 0.948), r=(0.135, 0.130, 0.052), z_rim=0.900)
