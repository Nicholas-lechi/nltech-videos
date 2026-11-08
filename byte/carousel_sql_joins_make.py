import numpy as np, os
from PIL import Image, ImageDraw, ImageFont, ImageChops
E='/home/claude/nltech-videos/engine/'
def font(n,s): return ImageFont.truetype(E+'fonts/'+n,s)
BLACK,BOLD,MONO,MONOB='InterDisplay-Black.otf','InterDisplay-Bold.otf','JetBrainsMonoNL-Medium.ttf','JetBrainsMonoNL-Bold.ttf'
W,H=1080,1350
WHITE=(240,244,250); GREY=(150,170,160); CARD=(14,30,24); EDGE=(40,70,58)
A_=(88,166,255); B_=(255,159,67); MIX=(110,255,210); NULLC=(255,110,110); YEL=(255,210,63)
LOGO=Image.open(E+'assets/watermark_nltech.png'); BYTE=Image.open(E+'assets/byte_wave.png')
def bg():
    y,x=np.mgrid[0:H,0:W].astype(np.float32)
    img=np.zeros((H,W,3),np.float32)+np.array([8,20,16],np.float32)
    img+=np.exp(-(((x-540)/700)**2+((y-150)/600)**2))[...,None]*np.array([10,55,40],np.float32)
    img[((x%54)<3)&((y%54)<3)]+=12
    return Image.fromarray(np.clip(img,0,255).astype(np.uint8)).convert('RGBA')
def footer(im,n,T):
    d=ImageDraw.Draw(im); l=LOGO.resize((200,int(LOGO.height*200/LOGO.width)),Image.LANCZOS); im.alpha_composite(l,(60,H-30-l.height))
    d.text((W-60,H-75),f"{n}/{T}",font=font(BOLD,34),fill=GREY,anchor="rm")
    if n<T: d.text((W-150,H-75),"Swipe →",font=font(BOLD,34),fill=WHITE,anchor="rm")
def venn(im,cx,cy,r,left,mid,right):
    off=r*0.62
    ml=Image.new('L',(W,H),0); ImageDraw.Draw(ml).ellipse((cx-off-r,cy-r,cx-off+r,cy+r),fill=255)
    mr=Image.new('L',(W,H),0); ImageDraw.Draw(mr).ellipse((cx+off-r,cy-r,cx+off+r,cy+r),fill=255)
    inter=ImageChops.multiply(ml,mr); lonly=ImageChops.subtract(ml,inter); ronly=ImageChops.subtract(mr,inter)
    for m,on,col in [(lonly,left,A_),(ronly,right,B_),(inter,mid,MIX)]:
        layer=Image.new('RGBA',(W,H),col+((230 if on else 28),)); im.paste(layer,(0,0),m) if False else im.alpha_composite(Image.composite(layer,Image.new('RGBA',(W,H),(0,0,0,0)),m))
    d=ImageDraw.Draw(im)
    d.ellipse((cx-off-r,cy-r,cx-off+r,cy+r),outline=A_,width=5); d.ellipse((cx+off-r,cy-r,cx+off+r,cy+r),outline=B_,width=5)
    d.text((cx-off-r*0.45,cy),"users",font=font(BLACK,34),fill=(10,20,16) if left else A_,anchor="mm")
    d.text((cx+off+r*0.45,cy),"orders",font=font(BLACK,34),fill=(10,20,16) if right else B_,anchor="mm")
def table(d,x,y,cols,rows,widths,head_col):
    rh=52; tw=sum(widths)
    d.rounded_rectangle((x,y,x+tw,y+rh*(len(rows)+1)+10),radius=16,fill=CARD,outline=EDGE,width=2)
    cx=x
    for c,w in zip(cols,widths): d.text((cx+18,y+30),c,font=font(MONOB,28),fill=head_col,anchor="lm"); cx+=w
    d.line((x+10,y+rh+2,x+tw-10,y+rh+2),fill=EDGE,width=2)
    for i,r in enumerate(rows):
        cx=x
        for v,w in zip(r,widths):
            col=NULLC if v=="NULL" else WHITE
            d.text((cx+18,y+rh*(i+1)+32),v,font=font(MONO,28),fill=col,anchor="lm"); cx+=w
def sql(d,y,lines):
    d.rounded_rectangle((60,y,1020,y+40+len(lines)*46),radius=18,fill=(6,12,10),outline=EDGE,width=2)
    for i,(t,c) in enumerate(lines): d.text((90,y+24+i*46),t,font=font(MONOB,32),fill=c)
    return y+40+len(lines)*46
KW=(255,123,114)
T=6; S=[]
# 1 cover
im=bg(); d=ImageDraw.Draw(im)
f=font(BOLD,36); d.rounded_rectangle((60,90,60+f.getlength("CHEAT SHEET")+56,156),radius=33,fill=MIX); d.text((88,123),"CHEAT SHEET",font=f,fill=(10,20,16),anchor="lm")
d.text((60,200),"SQL JOINs,",font=font(BLACK,124),fill=WHITE); d.text((60,330),"visually",font=font(BLACK,124),fill=MIX)
d.text((60,480),"INNER · LEFT · RIGHT · FULL",font=font(MONOB,40),fill=GREY)
venn(im,540,800,190,True,True,True)
im.alpha_composite(BYTE.resize((300,300)),(760,960)); footer(im,1,T); S.append(im)
# 2 tables
im=bg(); d=ImageDraw.Draw(im)
d.text((60,80),"Our two tables",font=font(BLACK,88),fill=WHITE); d.text((60,190),"Every example uses this data.",font=font(BOLD,40),fill=GREY)
d.text((60,290),"users",font=font(MONOB,40),fill=A_)
table(d,60,345,["id","name"],[["1","Ada"],["2","Ben"],["3","Chi"]],[160,300],A_)
d.text((60,620),"orders",font=font(MONOB,40),fill=B_)
table(d,60,675,["id","user_id","item"],[["101","1","Laptop"],["102","1","Mouse"],["103","2","Phone"],["104","9","Cable"]],[180,240,300],B_)
d.text((800,420),"Chi has",font=font(BOLD,34),fill=YEL,anchor="mm"); d.text((800,462),"no orders",font=font(BOLD,34),fill=YEL,anchor="mm")
d.text((870,850),"user 9",font=font(BOLD,34),fill=YEL,anchor="mm"); d.text((870,892),"doesn't exist",font=font(BOLD,34),fill=YEL,anchor="mm")
footer(im,2,T); S.append(im)
def join_slide(n,name,desc,flags,rows,extra=None):
    im=bg(); d=ImageDraw.Draw(im)
    d.text((60,70),name,font=font(BLACK,86),fill=WHITE); d.text((60,178),desc,font=font(BOLD,40),fill=GREY)
    venn(im,540,420,150,*flags); d=ImageDraw.Draw(im)
    y=sql(d,620,[("SELECT u.name, o.item",WHITE),("FROM users u",WHITE),(f"{name} orders o",KW),("  ON o.user_id = u.id;",WHITE)])
    table(d,60,y+30,["name","item"],rows,[400,560],MIX)
    if extra: d.text((60,H-140),extra,font=font(BOLD,32),fill=YEL)
    pass
    footer(im,n,T); S.append(im)
join_slide(3,"INNER JOIN","Only rows that match in both tables.",(False,True,False),[["Ada","Laptop"],["Ada","Mouse"],["Ben","Phone"]])
join_slide(4,"LEFT JOIN","Every user, even with no orders.",(True,True,False),[["Ada","Laptop"],["Ada","Mouse"],["Ben","Phone"],["Chi","NULL"]])
join_slide(5,"RIGHT JOIN","Every order, even with no user.",(False,True,True),[["Ada","Laptop"],["Ada","Mouse"],["Ben","Phone"],["NULL","Cable"]])
join_slide(6,"FULL JOIN","Everything from both. (Not in MySQL.)",(True,True,True),[["Ada","Laptop"],["Ada","Mouse"],["Ben","Phone"],["Chi","NULL"],["NULL","Cable"]])
os.makedirs('/home/claude/nltech-videos/images/2026-11-09',exist_ok=True)
for k,s in enumerate(S,1): s.convert('RGB').save(f'/home/claude/nltech-videos/images/2026-11-09/sql-joins-{k}.jpg',quality=92)
sheet=Image.new('RGB',(360*3,450*2))
for k,s in enumerate(S): sheet.paste(s.convert('RGB').resize((360,450)),((k%3)*360,(k//3)*450))
sheet.save('sheet.jpg',quality=85)
