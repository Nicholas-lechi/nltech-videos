import numpy as np, os, re
from PIL import Image, ImageDraw, ImageFont
E='/home/claude/nltech-videos/engine/'
def font(n,s): return ImageFont.truetype(E+'fonts/'+n,s)
BLACK,BOLD,MONO,MONOB='InterDisplay-Black.otf','InterDisplay-Bold.otf','JetBrainsMonoNL-Medium.ttf','JetBrainsMonoNL-Bold.ttf'
W,H=1080,1350
INK=(23,26,33); SUB=(105,100,92); CARD=(24,28,38); TS=(124,58,237)
LOGO=Image.open(E+'assets/watermark_nltech.png'); BYTE=Image.open(E+'assets/byte_wave.png')
KW={'const','let','return','true','false','=>'}
C_KW,C_TYPE,C_ID,C_PUN,C_STR,C_CMT=(255,123,114),(255,166,87),(230,237,243),(201,209,217),(165,214,255),(120,130,146)
def bg():
    y,x=np.mgrid[0:H,0:W].astype(np.float32)
    img=np.zeros((H,W,3),np.float32)+np.array([245,241,252],np.float32)
    img-=np.exp(-(((x-900)/600)**2+((y-100)/500)**2))[...,None]*np.array([20,6,14],np.float32)
    img[((x%54)<3)&((y%54)<3)]-=14
    return Image.fromarray(np.clip(img,0,255).astype(np.uint8)).convert('RGBA')
def footer(im,n,T):
    d=ImageDraw.Draw(im); l=LOGO.resize((200,int(LOGO.height*200/LOGO.width)),Image.LANCZOS); im.alpha_composite(l,(60,H-30-l.height))
    d.text((W-60,H-75),f"{n}/{T}",font=font(BOLD,34),fill=SUB,anchor="rm")
    if n<T: d.text((W-150,H-75),"Swipe →",font=font(BOLD,34),fill=INK,anchor="rm")
def code(d,y,src,size=34):
    lines=src.split('\n'); lh=int(size*1.42); h=50+len(lines)*lh
    d.rounded_rectangle((60,y,1020,y+h),radius=22,fill=CARD)
    f=font(MONOB,size); cw=f.getlength('M')
    for i,ln in enumerate(lines):
        x=95
        if ln.strip().startswith('//'):
            d.text((x,y+28+i*lh),ln,font=f,fill=C_CMT); continue
        for m in re.finditer(r"('[^']*')|([A-Za-z_]\w*)|(\s+)|(.)",ln):
            s=m.group(0)
            if m.group(1): c=C_STR
            elif m.group(2): c=C_KW if s in KW else (C_TYPE if s[0].isupper() else C_ID)
            else: c=C_PUN
            d.text((x,y+28+i*lh),s,font=f,fill=c); x+=cw*len(s)
    return y+h
def head(d,name,desc):
    f=font(MONOB,64); tw=f.getlength(name)
    d.rounded_rectangle((60,70,60+tw+60,170),radius=22,fill=TS); d.text((90,120),name,font=f,fill=(255,255,255),anchor="lm")
    d.text((60,200),desc,font=font(BLACK,64),fill=INK)


T=6; S=[]
GREEN,AMBER,RED=(17,163,91),(217,119,6),(220,38,38)
def codes(d,y,rows):
    for code,name,desc,col in rows:
        d.rounded_rectangle((60,y,1020,y+120),radius=22,fill=CARD)
        d.rounded_rectangle((60,y,230,y+120),radius=22,fill=col)
        d.text((145,y+60),code,font=font(MONOB,52),fill=(255,255,255),anchor="mm")
        d.text((260,y+38),name,font=font(BLACK,40),fill=(240,244,250),anchor="lm")
        d.text((260,y+84),desc,font=font(BOLD,30),fill=(170,180,196),anchor="lm")
        y+=138
    return y
im=bg(); d=ImageDraw.Draw(im)
f=font(BOLD,36); d.rounded_rectangle((60,90,60+f.getlength("CHEAT SHEET")+56,156),radius=33,fill=TS); d.text((88,123),"CHEAT SHEET",font=f,fill=(255,255,255),anchor="lm")
for k,(t,c) in enumerate([("HTTP status",TS),("codes every",INK),("dev must know",INK)]):
    d.text((60,200+k*120),t,font=font(BLACK,104),fill=c)
d.text((60,600),"2xx = success",font=font(MONOB,40),fill=GREEN); d.text((60,656),"4xx = client made a mistake",font=font(MONOB,40),fill=AMBER); d.text((60,712),"5xx = server broke",font=font(MONOB,40),fill=RED)
d.text((60,820),"Swipe for the ones you'll",font=font(BOLD,44),fill=SUB); d.text((60,876),"actually see every day 👉".replace(" 👉",""),font=font(BOLD,44),fill=SUB)
im.alpha_composite(BYTE.resize((260,260)),(790,640)); footer(im,1,T); S.append(im)
def page(n,title,rows,tip):
    im=bg(); d=ImageDraw.Draw(im)
    d.text((60,80),title,font=font(BLACK,80),fill=INK)
    y=codes(d,220,rows)
    d.text((60,y+30),tip,font=font(BOLD,36),fill=TS)
    footer(im,n,T); S.append(im)
page(2,"2xx: it worked",[("200","OK","Request succeeded, here's the data",GREEN),("201","Created","New item saved (after POST)",GREEN),("204","No Content","Done, nothing to send back (DELETE)",GREEN)],"Use 201 when you create something.")
page(3,"4xx: your fault",[("400","Bad Request","Invalid or missing data",AMBER),("401","Unauthorized","Not logged in / bad token",AMBER),("403","Forbidden","Logged in, but not allowed",AMBER),("404","Not Found","That route or item doesn't exist",AMBER)],"401 = who are you? · 403 = I know you, no.")
page(4,"4xx: more you'll meet",[("409","Conflict","Already exists (duplicate email)",AMBER),("422","Unprocessable","Data format OK, values invalid",AMBER),("429","Too Many Requests","Slow down, you hit a rate limit",AMBER)],"409 is perfect for 'email already taken'.")
page(5,"5xx: server broke",[("500","Server Error","Bug or crash in the backend",RED),("502","Bad Gateway","Proxy got a bad response upstream",RED),("503","Unavailable","Server down or overloaded",RED)],"5xx = check your server logs first.")
im=bg(); d=ImageDraw.Draw(im)
d.text((60,80),"Quick recap",font=font(BLACK,96),fill=INK)
rows=[("200","OK"),("201","Created"),("204","No Content"),("400","Bad Request"),("401","Not logged in"),("403","Not allowed"),("404","Not Found"),("409","Already exists"),("500","Server broke")]
y=220
for c,t in rows:
    col=GREEN if c[0]=="2" else (AMBER if c[0]=="4" else RED)
    d.rounded_rectangle((60,y,1020,y+80),radius=18,fill=CARD)
    d.text((95,y+40),c,font=font(MONOB,40),fill=col,anchor="lm"); d.text((240,y+40),t,font=font(BOLD,36),fill=(230,237,243),anchor="lm"); y+=92
d.text((60,y+20),"Save this and follow for more",font=font(BLACK,48),fill=TS)
footer(im,6,T); S.append(im)
os.makedirs('/home/claude/vsc/out/carousel2',exist_ok=True)
for i,s in enumerate(S): s.convert('RGB').save(f'/home/claude/vsc/out/carousel2/http-codes-{i+1}.jpg',quality=92)
print('ok')
