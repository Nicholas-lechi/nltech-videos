import numpy as np
from PIL import Image, ImageDraw, ImageFont
E='/home/claude/nltech-videos/engine/'
def font(n,s): return ImageFont.truetype(E+'fonts/'+n,s)
BLACK,BOLD,MONO,MONOB='InterDisplay-Black.otf','InterDisplay-Bold.otf','JetBrainsMonoNL-Medium.ttf','JetBrainsMonoNL-Bold.ttf'
W,H=1080,1350
INK=(23,26,33); SUB=(105,100,92); CARD=(24,28,38); ORANGE=(214,90,30); GREEN=(40,150,90); BLUE=(40,110,210); PURPLE=(130,70,200); RED=(200,50,50)
MINT=(110,255,210); GREYL=(160,170,184)
LOGO=Image.open(E+'assets/watermark_nltech.png'); BYTE=Image.open(E+'assets/byte_wave.png'); BYTE2=Image.open(E+'assets/byte_idle.png')
def bg():
    y,x=np.mgrid[0:H,0:W].astype(np.float32)
    img=np.zeros((H,W,3),np.float32)+np.array([250,246,238],np.float32)
    img-=np.exp(-(((x-900)/600)**2+((y-100)/500)**2))[...,None]*np.array([4,10,22],np.float32)
    img[((x%54)<3)&((y%54)<3)]-=14
    return Image.fromarray(np.clip(img,0,255).astype(np.uint8)).convert('RGBA')
def footer(im,n,total):
    d=ImageDraw.Draw(im)
    l=LOGO.resize((200,int(LOGO.height*200/LOGO.width)),Image.LANCZOS); im.alpha_composite(l,(60,H-30-l.height))
    d.text((W-60,H-75),f"{n}/{total}",font=font(BOLD,34),fill=SUB,anchor="rm")
    if n<total: d.text((W-150,H-75),"Swipe →",font=font(BOLD,34),fill=INK,anchor="rm")
def header(d,label,col,title,sub):
    f=font(BOLD,34); tw=f.getlength(label)
    d.rounded_rectangle((60,70,60+tw+56,134),radius=32,fill=col); d.text((88,102),label,font=f,fill=(255,255,255),anchor="lm")
    d.text((60,165),title,font=font(BLACK,84),fill=INK); d.text((60,272),sub,font=font(BOLD,40),fill=SUB)
def rows(d,items,col,y0,rh):
    for k,(cmd,desc) in enumerate(items):
        y=y0+k*rh; h=rh-22
        d.rounded_rectangle((60,y,1020,y+h),radius=24,fill=CARD)
        d.rounded_rectangle((60,y,74,y+h),radius=7,fill=col)
        d.text((108,y+h/2-24),"$",font=font(MONOB,40),fill=(63,220,130),anchor="lm")
        d.text((150,y+h/2-24),cmd,font=font(MONOB,40),fill=(240,244,250),anchor="lm")
        d.text((108,y+h/2+30),desc,font=font(BOLD,32),fill=GREYL,anchor="lm")
T=6; slides=[]
im=bg(); d=ImageDraw.Draw(im)
f=font(BOLD,36); d.rounded_rectangle((60,90,60+f.getlength("CHEAT SHEET")+56,156),radius=33,fill=ORANGE); d.text((88,123),"CHEAT SHEET",font=f,fill=(255,255,255),anchor="lm")
for k,(t,c) in enumerate([("Git commands",INK),("you'll use",ORANGE),("every day",INK)]):
    d.text((60,200+k*125),t,font=font(BLACK,118),fill=c)
d.text((60,600),"From first commit",font=font(BOLD,44),fill=SUB); d.text((60,656),"to pull request",font=font(BOLD,44),fill=SUB)
d.rounded_rectangle((60,760,430,840),radius=40,fill=INK); d.text((245,800),"Save this",font=font(BLACK,40),fill=(255,255,255),anchor="mm")
im.alpha_composite(BYTE.resize((560,560)),(520,660)); footer(im,1,T); slides.append(im)
for (lab,col,title,sub,items,rh) in [
 ("1 · START",BLUE,"Start a project","Create or copy a repository.",[("git init","Start a new repo in this folder"),("git clone <url>","Copy a repo from GitHub"),("git status","See what changed")],250),
 ("2 · SAVE",GREEN,"Save your work","Stage changes, then commit them.",[("git add .","Stage all changes"),('git commit -m "msg"',"Save a snapshot with a message"),("git log --oneline","See your commit history")],250),
 ("3 · BRANCH",PURPLE,"Work on branches","Build features without breaking main.",[("git branch","List branches"),("git switch -c feature","Create a branch and switch to it"),("git switch main","Go back to main"),("git merge feature","Merge feature into current branch")],200),
 ("4 · SYNC",ORANGE,"Sync with GitHub","Upload and download changes.",[("git remote add origin <url>","Connect to a GitHub repo"),("git push -u origin main","Upload your commits"),("git pull","Download and merge changes"),("git fetch","Download without merging")],200),
 ("5 · OOPS",RED,"Undo mistakes","Fix things before they get worse.",[("git restore file.js","Throw away changes to a file"),("git restore --staged file.js","Unstage a file"),("git commit --amend","Fix your last commit"),("git stash","Park changes for later")],180),
]:
    im=bg(); d=ImageDraw.Draw(im); header(d,lab,col,title,sub); rows(d,items,col,370,rh)
    n=len(slides)+1
    if n==T: d.text((60,1100),"Follow @nicholaslechitech for daily dev tips",font=font(BLACK,36),fill=ORANGE)
    footer(im,n,T); slides.append(im)
import os; os.makedirs('/home/claude/nltech-videos/images/2026-11-06',exist_ok=True)
for k,s in enumerate(slides,1): s.convert('RGB').save(f'/home/claude/nltech-videos/images/2026-11-06/git-commands-{k}.jpg',quality=92)
sheet=Image.new('RGB',(360*3,450*2))
for k,s in enumerate(slides): sheet.paste(s.convert('RGB').resize((360,450)),((k%3)*360,(k//3)*450))
sheet.save('sheet.jpg',quality=85)
