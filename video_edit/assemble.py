import subprocess,json,sys,os
def sh(c):
    r=subprocess.run(c,shell=True,capture_output=True,text=True)
    if r.returncode: print(r.stderr[-2500:]); sys.exit(1)
    return r.stdout
J=json.load(open("pieces.json")); sp=J["sp"]; n=len(sp)
CH={2,5,8,11}
chap=[]; cur=-1
for i,(si,_,_) in enumerate(sp):
    if si in CH and (i==0 or sp[i-1][0]!=si): cur+=1; chap.append([])
    if cur<0: cur=0; chap.append([])
    chap[-1].append(i)
dur=lambda f:float(sh(f'ffprobe -v error -show_entries format=duration -of csv=p=0 {f}'))
D=[dur(f"p/p{i:02d}.mp4") for i in range(n)]
CD=[sum(D[i] for i in c) for c in chap]
X=0.3; trans=["smoothleft","circleopen","zoomin","slideup"]
fc=[]; inputs=" ".join(f"-i p/p{i:02d}.mp4" for i in range(n))
for k,c in enumerate(chap):
    ins="".join(f"[{i}:v][{i}:a]" for i in c)
    fc.append(f"{ins}concat=n={len(c)}:v=1:a=1[cv{k}][ca{k}]")
lv,la="cv0","ca0"; acc=CD[0]; offs=[]
for k in range(1,len(chap)):
    off=acc-X; offs.append(off)
    fc.append(f"[{lv}][cv{k}]xfade=transition={trans[(k-1)%4]}:duration={X}:offset={off:.3f}[xv{k}]")
    fc.append(f"[{la}][ca{k}]acrossfade=d={X}[xa{k}]")
    lv,la=f"xv{k}",f"xa{k}"; acc+=CD[k]-X
fc=";".join(fc)
sh(f'ffmpeg -y -v error {inputs} -filter_complex "{fc}" -map "[{lv}]" -map "[{la}]" -c:v libx264 -preset veryfast -crf 17 -c:a pcm_s16le base.mkv')
T=dur("base.mkv"); print("base",T,offs)
json.dump({"T":T,"offs":offs},open("meta.json","w"))
