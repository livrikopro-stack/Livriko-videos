import numpy as np, wave, sys
sr=44100; dur=10.0; n=int(sr*dur)
t=np.arange(n)/sr
def tone(f,start,length,amp,decay=3.0):
    out=np.zeros(n)
    i0=int(start*sr); L=int(length*sr)
    i1=min(n,i0+L)
    tt=np.arange(i1-i0)/sr
    env=np.minimum(1,tt/0.02)*np.exp(-decay*tt)
    w=np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*2*f*tt)*np.exp(-2*tt)+0.1*np.sin(2*np.pi*3*f*tt)*np.exp(-4*tt)
    out[i0:i1]=amp*env*w
    return out
def pad(freqs,start,length,amp):
    out=np.zeros(n); i0=int(start*sr); i1=min(n,i0+int(length*sr))
    tt=np.arange(i1-i0)/sr
    env=np.minimum(1,tt/1.2)*np.minimum(1,(length-tt)/1.2)
    for f in freqs:
        for d in (-0.4,0.4):
            out[i0:i1]+=np.sin(2*np.pi*(f+d)*tt)
    out[i0:i1]*=amp*env/(len(freqs)*2)
    return out
N={'C4':261.63,'E4':329.63,'G4':392.0,'B4':493.88,'A4':440.0,'F4':349.23,'C5':523.25,'D5':587.33,'E5':659.25,'G5':783.99,'A5':880.0,'C3':130.81,'A3':220.0,'F3':174.61,'G3':196.0,'D4':293.66}
sig=np.zeros(n)
# slow chords: C, Am, F, G (2.5 s each)
chords=[(['C3','E4','G4','B4'],0),(['A3','C4' if 'C4' in N else 'C4','E4','A4'],2.5),(['F3','A4','C5','E4'],5.0),(['G3','D4','G4','B4'],7.5)]
for fr,s in chords:
    sig+=pad([N[x] for x in fr],s,2.8,0.9)
# gentle arpeggio on top, every 0.625 s
arp=[['E5','G5','C5','G4'],['E5','C5','A4','C5'],['A5','E5','C5','E5'],['D5','G4','B4','D5']]
step=0.625
k=0
for ci,(fr,s) in enumerate(chords):
    for j in range(4):
        sig+=tone(N[arp[ci][j]],s+j*step,2.0,0.35)
# master fades
fade=np.minimum(1,t/1.0)*np.minimum(1,(dur-t)/1.5)
sig*=fade
sig=sig/np.max(np.abs(sig))*0.55
pcm=(sig*32767).astype(np.int16)
st=np.column_stack([pcm,pcm]).flatten()
with wave.open(sys.argv[1],'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(st.tobytes())
