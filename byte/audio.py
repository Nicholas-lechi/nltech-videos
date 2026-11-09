import sys; sys.path.insert(0,'.')
import numpy as np, soundfile as sf
from tl import *
N=int(SR*DURATION); music=np.zeros(N); fx=np.zeros(N); voice=VOICE[:N].copy()
rng=np.random.default_rng(5)
bpm=96; bar=4*60/bpm; mf=lambda m:440*2**((m-69)/12)
chords=[[60,64,67],[57,60,64],[53,57,60],[55,59,62]]
for i in range(int(DURATION/bar)+1):
    s0=int(i*bar*SR); s1=min(N,int((i+1)*bar*SR)+int(0.3*SR))
    if s0>=N: break
    tt=np.arange(s1-s0)/SR; env=np.minimum(1,tt/0.5)*np.minimum(1,np.maximum(0,(bar+0.3-tt)/0.5))
    for m in chords[i%4]:
        f=mf(m); music[s0:s1]+=0.045*env*(np.sin(2*np.pi*f*tt)+0.25*np.sin(2*np.pi*2*f*tt))
    # plucky arpeggio
    for j in range(8):
        m=chords[i%4][j%3]+12; s=s0+int(j*bar/8*SR); L=int(0.25*SR); n=np.arange(L)/SR
        seg=0.05*np.sin(2*np.pi*mf(m)*n)*np.exp(-n*14); e_=min(N,s+L)
        if e_>s: music[s:e_]+=seg[:e_-s]
beat=60/bpm; k=np.arange(int(0.22*SR))/SR; kick=np.sin(2*np.pi*(50+90*np.exp(-k*30))*k)*np.exp(-k*13)
tb=0.0
while tb<DURATION-1.5:
    s=int(tb*SR); e_=min(N,s+len(kick)); music[s:e_]+=0.22*kick[:e_-s]; tb+=beat
duck=np.where(np.abs(np.convolve(np.abs(voice),np.ones(int(0.3*SR))/int(0.3*SR),'same'))>0.004,0.35,1.0)
duck=np.convolve(duck,np.ones(int(0.15*SR))/int(0.15*SR),'same'); music*=duck
def add(t,seg):
    s=int(t*SR); e_=min(N,s+len(seg))
    if e_>s: fx[s:e_]+=seg[:e_-s]
for t in EVENTS['whoosh']:
    L=int(0.5*SR); nz=np.convolve(rng.standard_normal(L),np.ones(14)/14,'same'); add(t-0.15,0.0*nz*np.sin(np.pi*np.arange(L)/L)**2)
for t in EVENTS['pop']:
    n=np.arange(int(0.25*SR))/SR; add(t,0.14*np.sin(2*np.pi*(600+500*np.exp(-n*30))*n)*np.exp(-n*16))
for t in EVENTS['ding']:
    n=np.arange(int(0.6*SR))/SR; add(t,0.12*(np.sin(2*np.pi*1318*n)+0.6*np.sin(2*np.pi*1975*n))*np.exp(-n*7))
for t in []:  # buzz sound removed for good
    n=np.arange(int(0.35*SR))/SR; add(t,0.12*np.sign(np.sin(2*np.pi*150*n))*np.exp(-n*8))
for t in EVENTS['swish']:
    L=int(0.3*SR); nz=np.convolve(rng.standard_normal(L),np.ones(6)/6,'same'); add(t,0.0*nz*np.sin(np.pi*np.arange(L)/L)**2)
# login typing clicks
for k_ in range(0):
    add(SWAP_B+0.5+k_*1.3/15, rng.standard_normal(int(0.02*SR))*np.exp(-np.arange(int(0.02*SR))/SR*250)*0.08)
for k_ in range(0):
    add(SWAP_B+2.0+k_*0.8/10, rng.standard_normal(int(0.02*SR))*np.exp(-np.arange(int(0.02*SR))/SR*250)*0.08)
# boing on hops
for t in SC[1:]:
    n=np.arange(int(0.3*SR))/SR; add(t,0.07*np.sin(2*np.pi*(300+250*n/0.3)*n)*np.exp(-n*8))
out=voice+0.6*music+0.8*fx
fo=int(1.2*SR); out[-fo:]*=np.linspace(1,0,fo); out=out/np.max(np.abs(out))*0.9
sf.write('audio.wav',out.astype(np.float32),SR,subtype='PCM_16'); print('audio ok')
