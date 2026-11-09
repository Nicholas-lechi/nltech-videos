import numpy as np, os, re
from PIL import Image, ImageDraw, ImageFont
E='/home/claude/nltech-videos/engine/'
def font(n,s): return ImageFont.truetype(E+'fonts/'+n,s)
BLACK,BOLD,MONO,MONOB='InterDisplay-Black.otf','InterDisplay-Bold.otf','JetBrainsMonoNL-Medium.ttf','JetBrainsMonoNL-Bold.ttf'
W,H=1080,1350
INK=(23,26,33); SUB=(105,100,92); CARD=(24,28,38); TS=(49,120,198)
LOGO=Image.open(E+'assets/watermark_nltech.png'); BYTE=Image.open(E+'assets/byte_wave.png')
KW={'type','interface','const','string','number','boolean','readonly'}
C_KW,C_TYPE,C_ID,C_PUN,C_STR,C_CMT=(255,123,114),(255,166,87),(230,237,243),(201,209,217),(165,214,255),(120,130,146)
def bg():
    y,x=np.mgrid[0:H,0:W].astype(np.float32)
    img=np.zeros((H,W,3),np.float32)+np.array([250,246,238],np.float32)
    img-=np.exp(-(((x-900)/600)**2+((y-100)/500)**2))[...,None]*np.array([16,8,0],np.float32)
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
BASE="interface User {\n  id: number;\n  name: string;\n  email: string;\n  password: string;\n}"
im=bg(); d=ImageDraw.Draw(im)
f=font(BOLD,36); d.rounded_rectangle((60,90,60+f.getlength("CHEAT SHEET")+56,156),radius=33,fill=TS); d.text((88,123),"CHEAT SHEET",font=f,fill=(255,255,255),anchor="lm")
for k,(t,c) in enumerate([("TypeScript",TS),("utility types",INK),("you'll use",INK)]):
    d.text((60,200+k*120),t,font=font(BLACK,112),fill=c)
d.text((60,580),"Partial · Required · Pick · Omit",font=font(MONOB,36),fill=SUB); d.text((60,632),"Record · Readonly",font=font(MONOB,36),fill=SUB)
d.text((60,740),"All examples use this type 👇".replace(" 👇",":"),font=font(BOLD,40),fill=SUB)
code(d,800,BASE,32)
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
slide(2,"Partial","Partial: every field becomes optional","type UpdateUser = Partial<User>;\n// { id?: number; name?: string; ... }",
      "Required","Required: every field becomes required","type FullUser = Required<UpdateUser>;\n// all fields required again","Partial is perfect for PATCH/update DTOs.")
slide(3,"Pick","Pick: keep only the fields you list","type PublicUser = Pick<User, 'id' | 'name'>;\n// { id: number; name: string }",
      "Omit","Omit: everything except the fields you list","type SafeUser = Omit<User, 'password'>;\n// { id; name; email }","Use Omit to never send a password back.")
im=bg(); d=ImageDraw.Draw(im); head(d,"Record","A typed object map")
d.text((60,290),"Record<Keys, Value>: every key gets the same value type",font=font(BOLD,36),fill=SUB)
y=code(d,360,"type Role = 'admin' | 'editor' | 'viewer';\n\nconst limits: Record<Role, number> = {\n  admin: 100,\n  editor: 50,\n  viewer: 10,\n};",32)
d.text((60,y+40),"Forget a role, and TypeScript tells you.",font=font(BOLD,38),fill=TS); footer(im,4,T); S.append(im)
im=bg(); d=ImageDraw.Draw(im); head(d,"Readonly","Lock it after creation")
y=code(d,300,"const config: Readonly<User> = {\n  id: 1, name: 'Ada',\n  email: 'ada@x.com', password: '...',\n};\n\nconfig.name = 'Ben';\n// Error: name is a read-only property",32)
d.text((60,y+40),"Great for config and constants.",font=font(BOLD,38),fill=TS); footer(im,5,T); S.append(im)
im=bg(); d=ImageDraw.Draw(im); d.text((60,80),"Quick summary",font=font(BLACK,84),fill=INK)
rows=[("Partial<T>","all optional"),("Required<T>","all required"),("Pick<T, K>","keep some fields"),("Omit<T, K>","remove some fields"),("Record<K, V>","typed key → value map"),("Readonly<T>","can't be changed")]
for k,(a,b) in enumerate(rows):
    y=220+k*125; d.rounded_rectangle((60,y,1020,y+105),radius=20,fill=CARD)
    d.text((95,y+52),a,font=font(MONOB,40),fill=C_TYPE,anchor="lm"); d.text((985,y+52),b,font=font(BOLD,36),fill=(200,208,220),anchor="rm")
d.text((60,1000),"Follow @nicholaslechitech",font=font(BLACK,44),fill=TS); d.text((60,1060),"for daily dev tips",font=font(BOLD,38),fill=SUB)
footer(im,6,T); S.append(im)
os.makedirs('/home/claude/nltech-videos/images/2026-11-10',exist_ok=True)
for k,s in enumerate(S,1): s.convert('RGB').save(f'/home/claude/nltech-videos/images/2026-11-10/ts-utility-types-{k}.jpg',quality=92)
sheet=Image.new('RGB',(360*3,450*2))
for k,s in enumerate(S): sheet.paste(s.convert('RGB').resize((360,450)),((k%3)*360,(k//3)*450))
sheet.save('sheet.jpg',quality=85)
