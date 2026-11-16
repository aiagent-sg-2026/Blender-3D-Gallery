"""Original painted atlas. Analytic brush masks keep every detail reproducible at full resolution."""
import struct
import zlib
import numpy as np
from config import TILES, PALETTE


def rgb(value):
    return np.array(list(bytes.fromhex(value)),dtype=float)


def tile(name, width, height):
    y, x = np.mgrid[0:height, 0:width]
    u = np.clip((x-4)/(width-9), 0, 1)
    v = np.clip(1-(y-4)/(height-9), 0, 1)
    rng = np.random.default_rng(37371 + sum(map(ord, name)))
    grain = rng.normal(0, 1, (height, width))
    bases = dict(face=PALETTE["skin"], eye="FFF6EA", hair="342A28", skin=PALETTE["skin"],
                 ear="F7C6A4", lash="261B20", brow="2F2625", lip="6E302B", tongue="EC9188",
                 jeanFront="394F7C", jeanBack="3C507A", cuff="495D7F", shirt="F7F5F5",
                 knit="E3DEE1", bag="36343D", pocket="3B3941", strap="37343B", sole="EBE5E4",
                 shoe="F5F0EC", laces="ECE5E4", watch="34323A", glass="242631", metal="907F70", teeth="FFF3E6")
    tones = {"hair":("hair",(5,7,10)), "hairCap":("hair",(5,7,10)), "shirt":("tee",(-7,-9,-9)), "knit":("tee",(-14,-17,-16)),
             "jeanFront":("denim",(-13,-15,-28)), "jeanPlain":("denim",(-13,-15,-28)), "jeanBack":("denim",(-12,-15,-29)), "cuff":("denim",(-13,-16,-35)),
             "shoe":("shoe",(10,10,7)), "eyelets":("shoe",(10,10,7)), "sole":("shoe",(-2,-3,-5)), "bag":("pack",(3,3,3)),
             "pocket":("pack",(4,4,4)), "strap":("pack",(1,1,1)), "watch":("watch",(2,2,2))}
    if name in tones:
        family,tint=tones[name]; pigment=rgb(PALETTE[family])+tint
    else:pigment=rgb(bases[name])
    col = np.broadcast_to(pigment, (height,width,3)).copy()

    def layer(color, mask):
        nonlocal col
        a = np.clip(mask,0,1)[:,:,None]
        col = col*(1-a) + rgb(color)*a

    def glow(cx, cy, rx, ry):
        return np.exp(-2*((u-cx)/rx)**2-2*((v-cy)/ry)**2)

    def edge(d, feather=.012):
        return np.clip(.5 - d/feather, 0, 1)

    def stroke(points, radius, color, alpha=1., dash=0):
        d = np.full(u.shape, 10.)
        length = 0.
        for (ax,ay),(bx,by) in zip(points,points[1:]):
            dx, dy = bx-ax, by-ay
            span = np.hypot(dx, dy)
            t = np.clip(((u-ax)*dx+(v-ay)*dy)/(span*span),0,1)
            here = np.hypot(u-ax-t*dx, v-ay-t*dy)
            if dash:
                here = np.where(((length+t*span)*dash)%1 < .68, here, 1.)
            d = np.minimum(d, here)
            length += span
        layer(color, edge(d-radius, .0037)*alpha)

    if name == "face":
        for cx in (.19,.81):
            layer("E99582", .76*glow(cx,.296,.212,.13))
            layer("D39B87", .32*glow(cx*.76+.12,.51,.18,.095))
        layer("E3A189", .40*glow(.5,.261,.085,.055))
        layer("FFDDBC", .60*glow(.48,.3,.042,.028))
        layer("FFDAB7", .38*glow(.50,.16,.175,.075))
        col += grain[:,:,None]*.38
    elif name == "lip":
        layer("431D22",np.clip((v-.16)*1.00,0,.86))
        layer("7B3838",.58*glow(.5,.23,.27,.18))
    elif name == "tongue":
        layer("CA716F",np.clip((v-.51)*.78,0,.38))
        layer("F1A297",.60*glow(.46,.33,.27,.20))
    elif name == "eye":
        r = np.sqrt(((u-.5)/.380)**2 + ((v-.49)/.55)**2)
        angle = np.arctan2((v-.49)/.55, (u-.5)/.380)
        layer("D1B4A5", np.clip((v-.55)*.65,0,.32))
        layer("291D20",edge(r-1))
        layer("5B392C",edge(r-.91))
        layer("925E43",edge(r-.86) * np.clip((.73-v)*1.55,0,1))
        rays = (.5+.5*np.cos(angle*49+np.sin(angle*17)*1.6))*.09
        layer("D09460",rays * edge(r-.88) * (1-edge(r-.58)))
        pupil = np.hypot((u-.50)/.266,(v-.57)/.376)
        layer("211A1D",edge(pupil-1))
        layer("160F13",edge(r-.98)*np.clip((v-.65)*1.4,0,.44))
        layer("FFFCF3",edge(np.hypot((u-.367)/.064,(v-.686)/.075)-1,.15))
        layer("F4EADB",edge(np.hypot((u-.645)/.037,(v-.70)/.043)-1,.18)*.91)
        layer("F9D3AE",edge(np.hypot((u-.603)/.027,(v-.238)/.022)-1,.2)*.47)
    elif name == "hair":
        # U runs around each lock; V follows the part-to-tip direction.
        lines = np.cos(2*np.pi*(u*8+.18*np.sin(v*4)))
        col += (.5*lines)[:,:,None] * np.array([1,.9,.85])
    elif name=="hairCap":
        col += .5*np.cos(2*np.pi*(u*22+.3*np.sin(v*6)))[:,:,None]*np.array([1,.85,.73])
    elif name == "ear":
        layer("D08972", .84*glow(.55,.49,.61,.67))
        layer("F1AB89", .75*glow(.46,.29,.46,.40))
    elif name in ("jeanFront","jeanPlain","jeanBack","cuff"):
        weave = 1.8*np.sin((x*.97+y*1.4)) + np.sin(y*np.pi*.87)
        col += (weave+grain*1.7+5*np.cos((u-.53)*4.4)+2*np.sin(v*6))[:,:,None]
        phase=1.7 if name=="jeanPlain" else .2
        for level,amplitude,center in ((.18,5,.25),(.34,3,.68),(.56,2,.43)):
            fold=level+.075*(u-.5)+.020*np.sin(u*4+phase)
            mask=np.exp(-((u-center)/.40)**2)
            col += (amplitude*(np.exp(-((v-fold-.023)/.040)**2)-np.exp(-((v-fold)/.035)**2))*mask)[:,:,None]
        if name in ("jeanFront","jeanPlain"):
            seam=[(.02,.03),(.025,.46),(.028,.94)]
            pocket=[(.017,.77),(.12,.79),(.22,.83),(.29,.89),(.32,.96)]
            for path in (seam,pocket):
                stroke(path,.010,"334B6C",.90)
                stroke([(a+.012,b-.005) for a,b in path],.0036,"D5A16A",.85,54)
            if name=="jeanFront":stroke([(.90,.99),(.90,.87),(.90,.805),(.93,.775),(.985,.76)],.0049,"BD9269",.75,68)
        elif name == "jeanBack":
            # The outseam belongs to both sides of the garment's UV split.
            stroke([(.02,.03),(.025,.46),(.028,.94)],.0052,"BD9269",.75,68)
            pocket=[(.16,.86),(.79,.87),(.76,.735),(.50,.690),(.20,.730),(.16,.86)]
            stroke(pocket,.009,"374766")
            stroke([(.50+(a-.50)*.92,.79+(b-.79)*.91) for a,b in pocket],.0042,"C29569",.76,70)
            stroke([(.20,.82),(.36,.80),(.50,.76),(.62,.79),(.77,.82)],.0042,"B59374",.70,68)
        else:
            col += (3.8*np.cos(v*15)*np.sin(np.pi*u))[:,:,None]
            stroke([(.01,.85),(.99,.85)],.008,"B19A82",.65,65)
    elif name in ("shirt","knit"):
        col += (grain*.63 + np.sin(x*1.8)*(.8 if name=="shirt" else 2.7))[:,:,None]
        if name=="shirt":
            col -= (6.5*(.5+.5*np.cos(4*np.pi*(u+.035*np.sin(v*6))))*(.65+.35*np.cos(v*4)))[:,:,None]
            for cx in (.19,.81):
                line=cx+(.17 if cx<.5 else -.17)*(v-.16)
                layer("BCB6BE", .14*np.exp(-((u-line)/.055)**2-((v-.17)/.14)**2))
            stroke([(.01,.055),(.99,.055)],.003,"D0CBCC",.53,95)
    elif name in ("bag","strap","pocket"):
        col += (grain*1.4+np.cos(x*1.9)*1.1+np.sin(y*1.7)*1.4)[:,:,None]
        if name=="pocket":
            stroke([(.02,.70),(.12,.72),(.88,.72),(.98,.70)],.026,"26252B")
            stroke([(.04,.716),(.96,.716)],.004,"858087",.86,90)
        if name=="strap":
            for a in (.12,.88):
                stroke([(a,.01),(a,.99)],.009,"81777C",.62,66)
    elif name=="eyelets":
        for cy in (.1,.3,.5,.7,.9):
            radius=np.hypot((u-.50)/.15,(v-cy)/.027)
            layer("D0C6C0",edge(radius-1.35,.2))
            layer("817773",edge(radius-.75,.22))
        for x in (.08,.92):stroke([(x,.01),(x,.99)],.013,"C9BFBA",.6,60)
    elif name in ("shoe","laces","sole"):
        col += (grain*.8)[:,:,None]
        if name=="laces":
            for cy in (.20,.38,.56,.74):
                for direction in (-1,1):
                    lace=[(.10,cy+.068*direction),(.5,cy+.01),(.90,cy-.068*direction)]
                    stroke(lace,.024,"B3A5A0",.8)
                    stroke([(a,b+.015) for a,b in lace],.019,"FFFCF6")
        elif name=="shoe":
            line=[(i/32,.65-.25*np.exp(-((i/32-.5)/.135)**2)+.07*np.cos(2*np.pi*i/32)) for i in range(33)]
            layer("DCD5D2",.38*edge(v-(.52-.21*np.exp(-((u-.5)/.19)**2)),.06))
            stroke(line,.017,"B7A8A4",.90)
            stroke([(a,b+.026) for a,b in line],.004,"C4B6B2",.85,76)
        else:
            stroke([(.01,.18),(.99,.18)],.016,"C9BFBE",.73)
            stroke([(.01,.82),(.99,.82)],.025,"D5CCC7",.84)
    elif name=="glass":
        layer("636673",.38*np.exp(-((u-.2*v-.2)/.19)**2))
    return np.uint8(np.clip(col,0,255))


def write_png(path,canvas):
    def chunk(kind, payload):
        return struct.pack(">I",len(payload))+kind+payload+struct.pack(">I",zlib.crc32(kind+payload))
    scan = b"".join(b"\0"+row.tobytes() for row in canvas)
    path.write_bytes(b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">IIBBBBB",1024,1024,8,2,0,0,0))
                     +chunk(b"IDAT",zlib.compress(scan,9))+chunk(b"IEND",b""))


def make_atlas(path):
    canvas = np.full((1024,1024,3), 234, dtype="uint8")
    for name,(x0,y0,x1,y1) in TILES.items():
        canvas[y0:y1,x0:x1] = tile(name,x1-x0,y1-y0)
    write_png(path,canvas)


def make_normal_atlas(path):
    """Millimetre-scale cloth relief shares the colour charts and their gutters."""
    canvas=np.full((1024,1024,3),(128,128,255),dtype="uint8")
    for name,(x0,y0,x1,y1) in TILES.items():
        height,width=y1-y0,x1-x0
        y,x=np.mgrid[0:height,0:width]
        u=np.clip((x-4)/(width-9),0,1);v=np.clip(1-(y-4)/(height-9),0,1)
        h=np.zeros_like(u);span_u,span_v=.25,.35
        if name in ("shirt","knit"):
            span_u,span_v=.86,.312
            h=.0023*np.sin(8*np.pi*u+5*v)*np.exp(-((v-.12)/.18)**2)
            h+=.0012*np.sin(12*np.pi*u-9*v)*np.exp(-((v-.68)/.22)**2)
        elif name in ("jeanFront","jeanPlain","jeanBack","cuff"):
            span_u,span_v=.23,.385
            phase=1.7 if name=="jeanPlain" else .2
            for level,amount,center in ((.18,.0025,.25),(.34,.0018,.68),(.56,.0014,.43)):
                fold=level+.075*(u-.5)+.020*np.sin(u*4+phase)
                h+=amount*np.exp(-((v-fold)/.050)**2)*np.exp(-((u-center)/.40)**2)
            h+=.000025*np.sin(2*np.pi*(u*69+v*94))
        elif name=="eyelets":
            span_u,span_v=.014,.075
            for cy in (.1,.3,.5,.7,.9):
                h-=.00025*np.exp(-2*(((u-.5)/.15)**2+((v-cy)/.027)**2))
        elif name=="shoe":
            span_u,span_v=.48,.12
            seam=.65-.25*np.exp(-((u-.5)/.135)**2)+.07*np.cos(2*np.pi*u)
            h=.0008*np.tanh((v-seam)/.015)
        elif name=="laces":
            span_u,span_v=.08,.075
            for cy in (.20,.38,.56,.74):
                for direction in (-1,1):
                    line=cy+.085*(1-2*u)*direction
                    h+=.0006*np.exp(-((v-line)/.025)**2)
        elif name in ("bag","pocket","strap"):
            h=.000025*np.sin(2*np.pi*u*73)*np.sin(2*np.pi*v*91)
        elif name=="hairCap":
            span_u,span_v=1.45,.55
            h=.00002*np.sin(2*np.pi*(u*22+.3*np.sin(v*6)))
        elif name=="hair":
            h=.00002*np.sin(2*np.pi*(u*8+.18*np.sin(v*4)))
        # V increases upward in the atlas, while NumPy rows increase downward.
        dy,dx=np.gradient(h)
        normal=np.stack((-dx*(width-9)/span_u,dy*(height-9)/span_v,np.ones_like(h)),axis=-1)
        normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
        encoded=np.uint8(np.clip(np.rint((normal*.5+.5)*255),0,255))
        encoded[:4]=encoded[4];encoded[-4:]=encoded[-5]
        encoded[:,:4]=encoded[:,4:5];encoded[:,-4:]=encoded[:,-5:-4]
        canvas[y0:y1,x0:x1]=encoded
    write_png(path,canvas)

