# Original synthesized soundtrack + SFX (no third-party material => copyright-free)
import numpy as np, wave
SR=48000
def save(name,x):
    x=np.clip(x,-1,1); s=(np.stack([x[0],x[1]],1)*32767).astype('<i2')
    w=wave.open(name,'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(s.tobytes()); w.close()
def lp(x,a):  # one-pole lowpass
    y=np.zeros_like(x); p=0.0
    for i,v in enumerate(x): p+=a*(v-p); y[i]=p
    return y
D=103; N=D*SR; t=np.arange(N)/SR
bpm=92; beat=60/bpm
rng=np.random.default_rng(7)
chords=[(57,60,64,67),(53,57,60,64),(48,52,55,59),(55,59,62,66)]  # Am7 Fmaj7 Cmaj7 G6
mf=lambda m:440*2**((m-69)/12)
L=np.zeros(N); R=np.zeros(N)
bar=beat*4
for b in range(int(D/bar)+1):
    ch=chords[b%4]; s0=int(b*bar*SR); n=int(bar*SR)
    if s0>=N: break
    n=min(n,N-s0); tt=np.arange(n)/SR
    env=np.minimum(tt/0.6,1)*np.minimum((bar-tt)/0.8,1).clip(0,1)
    pad=np.zeros(n)
    for k,m in enumerate(ch):
        f=mf(m)
        for det in (-0.4,0.4):
            pad+=np.sin(2*np.pi*(f+det)*tt)*0.5+np.sin(2*np.pi*2*(f+det)*tt)*0.12
    pad*=env*0.05
    L[s0:s0+n]+=pad*1.0; R[s0:s0+n]+=np.roll(pad,40)
    # bass
    bf=mf(ch[0]-24); bn=np.sin(2*np.pi*bf*tt)*np.exp(-tt*1.6)*0.28*np.minimum(tt/0.01,1)
    L[s0:s0+n]+=bn; R[s0:s0+n]+=bn
    # plucky arp (8ths)
    for i in range(8):
        a0=int(i*beat/2*SR)
        if a0>=n: break
        m=ch[[0,2,1,3,2,3,1,2][i]]+12
        ln=int(0.5*SR); ln=min(ln,n-a0); u=np.arange(ln)/SR
        pl=(np.sin(2*np.pi*mf(m)*u)+0.3*np.sin(2*np.pi*2*mf(m)*u))*np.exp(-u*7)*0.07
        pan=0.3+0.4*((i%2))
        L[s0+a0:s0+a0+ln]+=pl*(1-pan); R[s0+a0:s0+a0+ln]+=pl*pan
# lofi drums
hat=np.zeros(N); kick=np.zeros(N); snare=np.zeros(N)
for i in range(int(D/(beat/2))):
    p=int(i*beat/2*SR)
    ln=int(0.05*SR)
    if p+ln>=N: break
    hat[p:p+ln]+=rng.standard_normal(ln)*np.exp(-np.arange(ln)/SR*90)*(0.05 if i%2 else 0.03)
for i in range(int(D/beat)):
    p=int(i*beat*SR)
    if i%4 in (0,) or i%4==2 and i%8==6:
        ln=int(0.25*SR); u=np.arange(ln)/SR
        kick[p:p+ln]+=np.sin(2*np.pi*(50+90*np.exp(-u*30))*u)*np.exp(-u*14)*0.35
    if i%4 in (1,3):
        ln=int(0.18*SR); u=np.arange(ln)/SR
        snare[p:p+ln]+=lp(rng.standard_normal(ln),0.5)*np.exp(-u*22)*0.14
dr=hat+kick+snare
L+=dr; R+=dr
# vinyl hiss + gentle lowpass for warmth
hiss=lp(rng.standard_normal(N),0.15)*0.004
L+=hiss; R+=np.roll(hiss,100)
L=lp(L,0.35); R=lp(R,0.35)
fade=np.minimum(t/2.0,1)*np.minimum((D-t)/4.0,1)
m=np.stack([L*fade,R*fade]); m/=np.abs(m).max()*1.15
save('music.wav',m)
# whoosh
def whoosh(name,dur=0.7,up=True):
    n=int(dur*SR); u=np.arange(n)/SR
    x=rng.standard_normal(n)
    # sweeping lowpass via block filtering
    out=np.zeros(n); blk=480
    for i in range(0,n,blk):
        fr=i/n; a=0.02+0.5*(fr if up else 1-fr)**1.5
        seg=x[i:i+blk]; p=out[i-1] if i else 0
        for j,v in enumerate(seg): p+=a*(v-p); out[i+j]=p
    env=np.sin(np.pi*np.clip(u/dur,0,1))**2
    out*=env; out/=np.abs(out).max(); out*=0.5
    save(name,np.stack([out,out]))
whoosh('whoosh.wav',0.75,True); whoosh('whoosh2.wav',0.6,False)
# riser-hit for intro
n=int(1.2*SR); u=np.arange(n)/SR
hit=np.sin(2*np.pi*(55+120*np.exp(-u*9))*u)*np.exp(-u*5)*0.6
save('hit.wav',np.stack([hit,hit]))
