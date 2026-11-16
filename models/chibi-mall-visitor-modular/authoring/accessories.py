"""Rigid pack shell and watch, with a separately weighted pair of shoulder straps."""
import math
from meshkit import Part, TAU, signed, section_tube, spline, joint, loft

def fronted_case(p,cx,cz,profiles,tile,bone,n=24,front=-1,exponent=3.8,close_back=True):
    # From the rear of the case to its visible face.
    rings=[]
    for y,w,h in profiles:
        row=[]
        for j in range(n):
            a=TAU*j/n
            dx=w*signed(math.cos(a),2/exponent)
            dz=h*signed(math.sin(a),2/exponent)
            row.append(p.vert((cx+dx,y,cz+dz),bone))
        rings.append(row)
    def face(ids):
        w=max(a[1] for a in profiles); h=max(a[2] for a in profiles)
        if front==1:ids=list(reversed(ids))
        p.face(ids,tile,[(.5+(p.xyz[i][0]-cx)/(2*w),.5+(p.xyz[i][2]-cz)/(2*h)) for i in ids])
    for a,b in zip(rings,rings[1:]):
        for j in range(n):
            k=(j+1)%n; face([a[j],a[k],b[k],b[j]])
    if close_back:face(list(reversed(rings[0])))
    face(rings[-1])
    p.flat.add(len(p.faces)-1)

def build():
    p=Part("Daypack_shell","Backpack","Cloth")
    fronted_case(p,0,.579,[(.072,.085,.106),(.086,.106,.130),(.124,.118,.137),
                            (.174,.119,.133),(.203,.107,.122),(.212,.083,.102)],"bag","chest",16,1,3.0)
    fronted_case(p,0,.537,[(.196,.086,.058),(.213,.099,.063),(.218,.090,.057)],
                 "pocket","chest",12,1,4.1,close_back=False)
    for s in (-1,1):
        loft(p,[(s*.113,.151,.488,.015,.027,3.),(s*.121,.151,.494,.019,.033,3.),
                (s*.120,.150,.559,.017,.031,3.)],6,"bag","chest")
    handle=[(-.038,.125,.694),(-.040,.127,.726),(-.026,.128,.747),(0,.128,.754),
            (.026,.128,.747),(.040,.127,.726),(.038,.125,.694)]
    section_tube(p,handle,[.009]*7,[.008]*7,(0,1,0),"strap","chest",6)
    # A short pull stands out against the pocket's painted zipper teeth.
    section_tube(p,[(-.075,.218,.567),(-.077,.222,.558),(-.075,.223,.549)],
                 [.003,.0045,.003],[.0025]*3,(1,0,0),"metal","chest",6)
    straps=Part("Shoulder_straps","Backpack","Cloth")
    for s,side in ((1,"L"),(-1,"R")):
        control=[(.068,.105,.692),(.076,.065,.741),(.087,.015,.770),(.091,-.033,.758),
                 (.098,-.056,.714),(.108,-.061,.655),(.117,-.052,.597),
                 (.122,-.030,.548),(.131,.004,.523),(.124,.064,.495),(.099,.105,.482)]
        pts=[spline([(s*x,y,z) for x,y,z in control],i/14) for i in range(15)]
        def weights(co,i,j):
            influence=.28*max(0,1-abs(i/14-.35)/.36)
            return joint("chest","clavicle."+side,influence)
        section_tube(straps,pts,[.023 if i<11 else .014 for i in range(15)],[.007]*15,
                     (1,0,0),"strap",weights,6)
    watch=Part("Wristwatch","Watch","Hardware")
    loft(watch,[(.199,-.023,.478,.033,.032,2.4),(.201,-.024,.481,.036,.034,2.4),
                (.198,-.022,.500,.036,.034,2.4),(.197,-.022,.503,.033,.032,2.4)],8,"watch","forearm.L",tilt=.12)
    fronted_case(watch,.205,.491,[(-.047,.023,.016),(-.059,.026,.019),(-.065,.024,.018)],
                 "watch","forearm.L",8,-1,4.2)
    fronted_case(watch,.205,.492,[(-.0654,.021,.015),(-.067,.020,.014)],"glass","forearm.L",8,-1,4.2,close_back=False)

