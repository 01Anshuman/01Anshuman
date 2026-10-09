import subprocess,os,sys,json
SRC="/root/.claude/uploads/6892b85b-1300-5884-923d-4ed5a00f045f/5263a38c-new_one.mp4"
FONT="/usr/share/fonts/opentype/inter/Inter-Bold.otf"
FONTR="/usr/share/fonts/opentype/inter/Inter-Medium.otf"
def sh(c):
    r=subprocess.run(c,shell=True,capture_output=True,text=True)
    if r.returncode: print(r.stderr[-1500:]); sys.exit(1)
speech=[(0.405,5.096),(5.753,12.445),(12.918,16.653),(17.214,18.529),(19.079,31.943),(33.294,42.540),(43.12,49.06),(49.55,56.75),(57.16,68.18),(68.89,75.30),(75.78,86.01),(86.53,90.30),(90.82,99.15)]
# split long runs; (start,end,contiguous-with-previous)
pieces=[]; sp_idx=[]
for si,(a,b) in enumerate(speech):
    n=max(1,round((b-a)/7.0)); step=(b-a)/n
    for i in range(n): pieces.append((a+i*step,a+(i+1)*step)); sp_idx.append((si,i==0,i==n-1))
# zoom plans: (z0,z1) scale at start/end of piece. alternating focus steps
plans=[(1.0,1.08),(1.28,1.28),(1.0,1.0),(1.18,1.32),(1.0,1.10),(1.25,1.25),(1.05,1.05),(1.2,1.34)]
FPS=30
CH={2,5,8,11}
os.makedirs("p",exist_ok=True)
for i,(a,b) in enumerate(pieces):
    si,first,last=sp_idx[i]; chap_start=first and si in CH; chap_end=last and (si+1) in CH
    pa=0.22 if chap_start else (0.06 if first else 0.0); pb=0.22 if chap_end else (0.06 if last else 0.0)
    a2=max(0,a-pa); b2=min(99.1,b+pb); d=b2-a2
    z0,z1=plans[i%len(plans)]
    z=f"({z0}+({z1}-{z0})*t/{d:.3f})"
    # face sits upper third: keep crop anchored high
    vf=(f"scale=w='1080*{z}':h='1920*{z}':eval=frame:flags=lanczos,"
        f"crop=1080:1920:x='(iw-1080)/2':y='(ih-1920)*0.22',"
        f"eq=contrast=1.08:saturation=1.12:brightness=0.01,unsharp=5:5:0.6,"
        f"vignette=PI/6,fps={FPS},format=yuv420p")
    af="highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,aresample=48000"
    sh(f'ffmpeg -y -v error -ss {a2:.3f} -t {d:.3f} -i "{SRC}" -vf "{vf}" -af "{af}" -c:v libx264 -preset veryfast -crf 17 -c:a aac -b:a 192k p/p{i:02d}.mp4')
    print("piece",i,round(d,2),flush=True)
json.dump({"pieces":pieces,"sp":sp_idx},open("pieces.json","w"))
