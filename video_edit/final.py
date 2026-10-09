import json,subprocess,sys,os
M=json.load(open("meta.json")); T=M["T"]; offs=M["offs"]
FB="/usr/share/fonts/opentype/inter/Inter-Bold.otf"; FM="/usr/share/fonts/opentype/inter/Inter-Medium.otf"
cap="captions.ass"
fa=lambda a,b:f"if(lt(t,{a}),0,if(lt(t,{a+0.4}),(t-{a})/0.4,if(lt(t,{b-0.4}),1,if(lt(t,{b}),({b}-t)/0.4,0))))"
al=fa(0.9,4.6)
vf=(f"[0:v]drawbox=x=64:y=1560:w=8:h=110:color=0xFFC24B@1:t=fill:enable='between(t,0.9,4.6)',"
    f"drawtext=fontfile={FB}:text='ANSHUMAN MISHRA':fontsize=52:fontcolor=white:alpha='{al}':x=92:y=1566:shadowcolor=black@0.6:shadowx=2:shadowy=2,"
    f"drawtext=fontfile={FM}:text='Communication  ·  Personality Development':fontsize=30:fontcolor=0xFFC24B:alpha='{al}':x=94:y=1632:shadowcolor=black@0.6:shadowx=2:shadowy=2[v1];"
    f"color=c=0xFFC24B:s=1080x10:d={T}[bar];[v1][bar]overlay=x='-W+W*t/{T}':y=0:shortest=1[v2]")
if os.path.exists(cap): vf+=f";[v2]ass={cap}:fontsdir=/usr/share/fonts/opentype/inter[vout]"
else: vf+=";[v2]null[vout]"
# audio
aud=("[0:a]highpass=f=80,loudnorm=I=-16:TP=-1.5:LRA=7,asplit=2[vo][key];"
     f"[1:a]atrim=0:{T},volume=0.55,afade=t=out:st={T-3}:d=3[mu];[mu][key]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[md];")
sfx=[]; inp=" -i music.wav -i hit.wav -i whoosh.wav -i whoosh2.wav"
lab=["[vo]","[md]","[h]"]
aud+="[2:a]volume=0.8[h];"
for k,o in enumerate(offs):
    d=int(max(0,(o-0.25))*1000)
    aud+=f"[{3+k%2}:a]adelay={d}|{d},volume=0.7[w{k}];"; lab.append(f"[w{k}]")
aud+="".join(lab)+f"amix=inputs={len(lab)}:normalize=0:duration=first,alimiter=limit=0.95[aout]"
cmd=(f'ffmpeg -y -v error -i base.mkv{inp} -filter_complex "{vf};{aud}" -map "[vout]" -map "[aout]" '
     f'-c:v libx264 -preset medium -crf 16 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart out.mp4')
r=subprocess.run(cmd,shell=True,capture_output=True,text=True)
print(r.stderr[-2000:] or "ok")
