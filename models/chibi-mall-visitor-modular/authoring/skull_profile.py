"""Rest-space cranium shared by the face and reference-volume fit."""
from config import LANDMARKS

# Horizontal skull sections: height, lateral radius, depth radius, depth centre.
PROFILE = [(LANDMARKS["chin"],.022,.043,-.040),(.808,.058,.072,-.044),(.823,.105,.109,-.038),
           (.843,.140,.141,-.027),(.854,.156,.150,-.021),(.875,.181,.16,-.019),
           (.901,.197,.17,-.013),(.915,.203,.176,-.009),(.939,.204,.181,-.006),
           (.961,.199,.184,-.004),(.986,.2,.187,-.001),(1.014,.201,.188,.000),
           (1.041,.203,.190,.002),(1.084,.205,.192,.005),(1.135,.204,.189,.008),
           (1.187,.18,.166,.011),(1.226,.141,.132,.012),(1.25,.082,.077,.013),
           (1.26,.042,.041,.012)]


def skull(z):
    for i,(lo,hi) in enumerate(zip(PROFILE,PROFILE[1:])):
        if z<=hi[0]:
            t=min(1.,max(0.,(z-lo[0])/(hi[0]-lo[0])))
            prev=PROFILE[max(0,i-1)]; nxt=PROFILE[min(len(PROFILE)-1,i+2)]
            span=hi[0]-lo[0]
            m0=[(hi[k]-prev[k])/(hi[0]-prev[0])*span for k in range(1,4)]
            m1=[(nxt[k]-lo[k])/(nxt[0]-lo[0])*span for k in range(1,4)]
            return tuple((2*t**3-3*t*t+1)*a+(t**3-2*t*t+t)*c+
                         (-2*t**3+3*t*t)*b+(t**3-t*t)*d
                         for a,b,c,d in zip(lo[1:],hi[1:],m0,m1))
    return PROFILE[-1][1:]

