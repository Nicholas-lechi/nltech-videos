import numpy as np, os, re
from PIL import Image, ImageDraw, ImageFont
E='/home/claude/nltech-videos/engine/'
def font(n,s): return ImageFont.truetype(E+'fonts/'+n,s)
BLACK,BOLD,MONO,MONOB='InterDisplay-Black.otf','InterDisplay-Bold.otf','JetBrainsMonoNL-Medium.ttf','JetBrainsMonoNL-Bold.ttf'
W,H=1080,1350
INK=(23,26,33); SUB=(105,100,92); CARD=(24,28,38); TS=(12,138,95)
LOGO=Image.open(E+'assets/watermark_nltech.png'); BYTE=Image.open(E+'assets/byte_wave.png')
KW={'const','let','return','true','false','=>'}
C_KW,C_TYPE,C_ID,C_PUN,C_STR,C_CMT=(255,123,114),(255,166,87),(230,237,243),(201,209,217),(165,214,255),(120,130,146)
def bg():
    y,x=np.mgrid[0:H,0:W].astype(np.float32)
    img=np.zeros((H,W,3),np.float32)+np.array([238,250,244],np.float32)
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
BASE="const nums = [1, 2, 3, 4, 5];"
im=bg(); d=ImageDraw.Draw(im)
f=font(BOLD,36); d.rounded_rectangle((60,90,60+f.getlength("CHEAT SHEET")+56,156),radius=33,fill=TS); d.text((88,123),"CHEAT SHEET",font=f,fill=(255,255,255),anchor="lm")
for k,(t,c) in enumerate([("JavaScript",TS),("array methods",INK),("you'll use daily",INK)]):
    d.text((60,200+k*120),t,font=font(BLACK,104),fill=c)
d.text((60,580),"map · filter · find · includes",font=font(MONOB,36),fill=SUB); d.text((60,632),"reduce · some · every",font=font(MONOB,36),fill=SUB)
d.text((60,740),"All examples use this array:",font=font(BOLD,40),fill=SUB)
code(d,800,BASE,34)
im.alpha_composite(BYTE.resize((260,260)),(790,500)); footer(im,1,T); S.append(im)
def slide(n,a,ad,asrc,b,bd,bsrc,tip=None):
    im=bg(); d=ImageDraw.Draw(im)
    f=font(MONOB,54); x=60
    for nm in (a,b):
        tw=f.getlength(nm); d.rounded_rectangle((x,70,x+tw+50,160),radius=20,fill=TS); d.text((x+25,115),nm,font=f,fill=(255,255,255),anchor="lm"); x+=tw+70
    d.text((60,200),ad,font=font(BOLD,42),fill=INK)
    y=code(d,265,asrc,32)
    d.text((60,y+40),bd,font=font(BOLD,42),fill=INK)
    y=code(d,y+105,bsrc,32)
    if tip: d.text((60,y+40),tip,font=font(BOLD,36),fill=TS)
    footer(im,n,T); S.append(im)
slide(2,"map","Transform every item → new array","const doubled = nums.map(n => n * 2);\n// [2, 4, 6, 8, 10]",
      "filter","Keep only items that pass a test","const evens = nums.filter(n => n % 2 === 0);\n// [2, 4]","Neither one changes the original array.")
slide(3,"find","Get the FIRST item that matches","const big = nums.find(n => n > 3);\n// 4",
      "includes","Check if a value exists","nums.includes(3);\n// true","find returns undefined if nothing matches.")
slide(4,"reduce","Boil the array down to ONE value","const sum = nums.reduce(\n  (total, n) => total + n,\n  0\n);\n// 15",
      "in real life","Example: cart total","const cart = [1500, 2000, 500];\nconst total = cart.reduce(\n  (t, price) => t + price, 0);\n// 4000","The 0 is the starting value.")
slide(5,"some","Does AT LEAST ONE item pass?","nums.some(n => n > 4);\n// true",
      "every","Do ALL items pass?","nums.every(n => n > 0);\n// true","Both return true or false.")
im=bg(); d=ImageDraw.Draw(im)
d.text((60,80),"Quick recap",font=font(BLACK,96),fill=INK)
rows=[("map","new array, every item changed"),("filter","new array, some items kept"),("find","first matching item"),("includes","true / false: is it there?"),("reduce","one final value"),("some","true if ANY pass"),("every","true if ALL pass")]
y=230
for nm,desc in rows:
    d.rounded_rectangle((60,y,1020,y+96),radius=20,fill=CARD)
    d.text((95,y+48),nm,font=font(MONOB,40),fill=(255,166,87),anchor="lm")
    d.text((360,y+48),desc,font=font(BOLD,36),fill=(230,237,243),anchor="lm"); y+=112
d.text((60,y+20),"Save this 🔖 and follow for more".replace(" 🔖",""),font=font(BLACK,52),fill=TS)
footer(im,6,T); S.append(im)
os.makedirs('/home/claude/vsc/out/carousel',exist_ok=True)
for i,s in enumerate(S): s.convert('RGB').save(f'/home/claude/vsc/out/carousel/array-methods-{i+1}.jpg',quality=92)
print('ok')
