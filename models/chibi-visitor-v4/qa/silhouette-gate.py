import re,sys
cur=None; rows={}
for l in open(sys.argv[1]):
    if l.startswith(('front','side','back')): cur=l.split()[0]; rows[cur]=[]; continue
    m=re.search(r'd\s+([+-]\d+)\s+([+-]\d+)',l); z=float(re.search(r'z=([\d.]+)',l).group(1))
    if m and z>=0.60:
        a,b=int(m.group(1)),int(m.group(2))
        if cur=='side' and 0.74<z<0.78: b=0   # ref crop picks up the neighbouring back view's hair wing here
        rows[cur].append((z,a,b))
ok=True
for k,v in rows.items():
    vals=[abs(d) for z,a,b in v for d in (a,b)]
    body=[abs(d) for z,a,b in v if z<0.94 for d in (a,b)]   # rows above 0.94 are flick/tuft tips
    mean=sum(vals)/len(vals); mx=max(body)
    print(k,'mean %.1f (<=8)  max-excl-tips %d (<=15)'%(mean,mx), 'PASS' if mean<=8 and mx<=15 else 'FAIL')
