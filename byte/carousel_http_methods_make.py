import numpy as np, os
from PIL import Image, ImageDraw, ImageFont
E='/home/claude/nltech-videos/engine/'
def font(n,s): return ImageFont.truetype(E+'fonts/'+n,s)
BLACK,BOLD,MONO,MONOB='InterDisplay-Black.otf','InterDisplay-Bold.otf','JetBrainsMonoNL-Medium.ttf','JetBrainsMonoNL-Bold.ttf'
W,H=1080,1350
INK=(17,24,39); SUB=(95,104,120); CARD=(20,24,34); GREYL=(160,170,184)
C={'GET':(22,150,90),'POST':(30,100,210),'PUT':(200,120,0),'PATCH':(130,70,200),'DELETE':(205,50,50)}
LOGO=Image.open(E+'assets/watermark_nltech.png'); BYTE=Image.open(E+'assets/byte_wave.png')
def bg():
    y,x=np.mgrid[0:H,0:W].astype(np.float32)
    img=np.zeros((H,W,3),np.float32)+np.array([248,249,251],np.float32)
    img-=np.exp(-(((x-950)/600)**2+((y-80)/500)**2))[...,None]*np.array([10,6,0],np.float32)
    img[((x%54)<3)&((y%54)<3)]-=14
    return Image.fromarray(np.clip(img,0,255).astype(np.uint8)).convert('RGBA')
def footer(im,n,T):
    d=ImageDraw.Draw(im); l=LOGO.resize((200,int(LOGO.height*200/LOGO.width)),Image.LANCZOS); im.alpha_composite(l,(60,H-30-l.height))
    d.text((W-60,H-75),f"{n}/{T}",font=font(BOLD,34),fill=SUB,anchor="rm")
    if n<T: d.text((W-150,H-75),"Swipe →",font=font(BOLD,34),fill=INK,anchor="rm")
def method_header(d,m,title,sub):
    col=C[m]; f=font(MONOB,64); tw=f.getlength(m)
    d.rounded_rectangle((60,70,60+tw+60,170),radius=24,fill=col); d.text((90,120),m,font=f,fill=(255,255,255),anchor="lm")
    d.text((60,205),title,font=font(BLACK,90),fill=INK); d.text((60,318),sub,font=font(BOLD,40),fill=SUB)
def code_card(d,y,lines,h=None):
    h=h or 70+len(lines)*52
    d.rounded_rectangle((60,y,1020,y+h),radius=24,fill=CARD)
    for i,(t,c) in enumerate(lines): d.text((100,y+40+i*52),t,font=font(MONOB,36),fill=c)
    return y+h
def bullet(d,y,ok,txt):
    col=(22,150,90) if ok else (205,50,50)
    d.ellipse((60,y-22,104,y+22),fill=col)
    if ok: d.line((70,y,80,y+11,95,y-11),fill=(255,255,255),width=6)
    else: d.line((72,y-10,92,y+10),fill=(255,255,255),width=6); d.line((72,y+10,92,y-10),fill=(255,255,255),width=6)
    d.text((124,y),txt,font=font(BOLD,40),fill=INK,anchor="lm")
W_,Y_,G_,B_,P_=(240,244,250),(255,210,63),(63,220,130),(121,192,255),(210,168,255)
T=6; S=[]
im=bg(); d=ImageDraw.Draw(im)
f=font(BOLD,36); d.rounded_rectangle((60,90,60+f.getlength("CHEAT SHEET")+56,156),radius=33,fill=INK); d.text((88,123),"CHEAT SHEET",font=f,fill=(255,255,255),anchor="lm")
for k,(t,c) in enumerate([("HTTP methods",INK),("every API",C['POST']),("uses",INK)]):
    d.text((60,200+k*125),t,font=font(BLACK,120),fill=c)
x=60
for m in C:
    fw=font(MONOB,34).getlength(m)+40; d.rounded_rectangle((x,620,x+fw,680),radius=16,fill=C[m]); d.text((x+fw/2,650),m,font=font(MONOB,34),fill=(255,255,255),anchor="mm"); x+=fw+14
d.text((60,740),"What each one does, with",font=font(BOLD,42),fill=SUB); d.text((60,794),"real examples",font=font(BOLD,42),fill=SUB)
im.alpha_composite(BYTE.resize((520,520)),(540,720)); footer(im,1,T); S.append(im)
# GET
im=bg(); d=ImageDraw.Draw(im); method_header(d,'GET',"Read data","Fetch something. Never changes anything.")
y=code_card(d,400,[("GET /tasks",G_),("→ 200 OK  [ {...}, {...} ]",GREYL)])
y=code_card(d,y+30,[("GET /tasks/7",G_),("→ 200 OK  { id: 7, ... }",GREYL)])
bullet(d,y+80,True,"Safe to call as many times as you like"); bullet(d,y+160,False,"No request body"); footer(im,2,T); S.append(im)
# POST
im=bg(); d=ImageDraw.Draw(im); method_header(d,'POST',"Create data","Send new data to the server.")
y=code_card(d,400,[("POST /tasks",B_),('{ "title": "Ship it" }',Y_),("→ 201 Created  { id: 8, ... }",GREYL)])
bullet(d,y+80,True,"Data goes in the request body"); bullet(d,y+160,False,"Send it twice = two new tasks"); footer(im,3,T); S.append(im)
# PUT vs PATCH
im=bg(); d=ImageDraw.Draw(im)
d.text((60,80),"PUT",font=font(MONOB,64),fill=C['PUT']); d.text((210,80),"vs",font=font(BOLD,56),fill=SUB); d.text((300,80),"PATCH",font=font(MONOB,64),fill=C['PATCH'])
d.text((60,185),"Replace vs update",font=font(BLACK,84),fill=INK)
d.text((60,310),"PUT replaces the whole thing",font=font(BOLD,40),fill=C['PUT'])
y=code_card(d,370,[("PUT /tasks/7",Y_),('{ "title": "New", "done": true }',W_)])
d.text((60,y+60),"PATCH changes only what you send",font=font(BOLD,40),fill=C['PATCH'])
y=code_card(d,y+120,[("PATCH /tasks/7",P_),('{ "done": true }',W_)])
d.text((60,y+60),"Most apps use PATCH for updates.",font=font(BOLD,38),fill=SUB); footer(im,4,T); S.append(im)
# DELETE
im=bg(); d=ImageDraw.Draw(im); method_header(d,'DELETE',"Remove data","Delete something from the server.")
y=code_card(d,400,[("DELETE /tasks/7",(255,120,120)),("→ 204 No Content",GREYL)])
y=code_card(d,y+30,[("GET /tasks/7",G_),("→ 404 Not Found",(255,120,120))])
bullet(d,y+80,True,"Deleting twice gives the same result"); bullet(d,y+160,False,"Usually no request body"); footer(im,5,T); S.append(im)
# Summary
im=bg(); d=ImageDraw.Draw(im); d.text((60,80),"Quick summary",font=font(BLACK,84),fill=INK)
rows=[('GET','Read','200 OK'),('POST','Create','201 Created'),('PUT','Replace','200 OK'),('PATCH','Update','200 OK'),('DELETE','Remove','204 No Content')]
for k,(m,a,s) in enumerate(rows):
    y=220+k*140
    d.rounded_rectangle((60,y,1020,y+118),radius=22,fill=CARD)
    d.rounded_rectangle((60,y,300,y+118),radius=22,fill=C[m]); d.rectangle((260,y,300,y+118),fill=C[m])
    d.text((180,y+59),m,font=font(MONOB,44),fill=(255,255,255),anchor="mm")
    d.text((340,y+59),a,font=font(BLACK,48),fill=W_,anchor="lm"); d.text((990,y+59),s,font=font(MONOB,32),fill=GREYL,anchor="rm")
d.text((60,1000),"Follow @nicholaslechitech",font=font(BLACK,44),fill=C['POST']); d.text((60,1060),"for daily dev tips",font=font(BOLD,38),fill=SUB)
footer(im,6,T); S.append(im)
os.makedirs('/home/claude/nltech-videos/images/2026-11-08',exist_ok=True)
for k,s in enumerate(S,1): s.convert('RGB').save(f'/home/claude/nltech-videos/images/2026-11-08/http-methods-{k}.jpg',quality=92)
sheet=Image.new('RGB',(360*3,450*2))
for k,s in enumerate(S): sheet.paste(s.convert('RGB').resize((360,450)),((k%3)*360,(k//3)*450))
sheet.save('sheet.jpg',quality=85)
