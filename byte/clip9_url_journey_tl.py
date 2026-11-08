"""What happens when you type a URL, with Byte, white background."""
import re, json, math
SP = "/tmp/claude-0/-home-claude/e7805bda-0e11-5016-9991-51d072e57e6b/scratchpad/"
_SRC = open(SP + "clip3/tl.py").read()
def _sec(a, b=None):
    i = _SRC.index(a); j = _SRC.index(b) if b else len(_SRC)
    return _SRC[i:j]
exec(_SRC[:_SRC.index("# ---------------- timeline")])
HERE = SP + "clip9/"
INKC = (17, 24, 39); SUB = (90, 100, 116)
STEPC = [(30, 100, 200), (12, 140, 110), (130, 70, 200), (200, 95, 10), (200, 50, 120)]

_wbg = None
def bg():
    global _wbg
    if _wbg is None:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        img = np.zeros((H, W, 3), np.float32) + np.array([248, 249, 251], np.float32)
        img -= np.exp(-(((x - 540) / 600) ** 2 + ((y - 1600) / 380) ** 2))[..., None] * np.array([18, 8, 2], np.float32)
        img[((x % 54) < 3) & ((y % 54) < 3)] -= 14
        _wbg = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
    return _wbg.copy()

VO = json.load(open(HERE + "vo.json"))
vo_start = {}
def place(i, t):
    vo_start[i] = t; return t + VO[i]["dur"]
def vend(i): return vo_start[i] + VO[i]["dur"]
def frac(i, f): return vo_start[i] + VO[i]["dur"] * f
TR = 0.5
SC = [0.0]
for i in range(7):
    e = place(i, SC[-1] + (0.3 if i == 0 else TR)); SC.append(e + 0.4)
e = place(7, SC[-1] + TR)
DURATION = round((e + 1.4) * FPS) / FPS
NS = len(SC)
def scene_at(t):
    i = 0
    for k in range(NS):
        if t >= SC[k]: i = k
    return i
EVENTS = {"whoosh": [], "swish": [], "pop": [frac(i, 0.45) for i in range(1, 6)] + [frac(6, 0.3)], "ding": [frac(4, 0.7)], "buzz": []}

exec(_sec("# ---------------- voice amplitude", "# ---------------- character poses"))
POSES = {"idle": (0.28, 0.15, 0.28, 0.15, 0, 0, None), "wave": (0.28, 0.15, 2.55, 0.35, 0, 1, None),
         "point": (0.30, 0.15, 2.35, -0.25, 0, 0, None), "both": (2.55, 0.35, 2.55, 0.35, 1, 1, None)}
KEYS = [(0.0, "wave"), (vend(0), "point"), (vend(6), "idle"), (vo_start[7] - 0.1, "both")]
def pose_at(t):
    cur, prev, ts = "idle", "idle", 0.0
    for k, (kt, name) in enumerate(KEYS):
        if t >= kt: prev, cur, ts = (KEYS[k - 1][1] if k else name), name, kt
    b = ease_io((t - ts) / 0.35)
    A, B = POSES[prev], POSES[cur]
    return [A[i] + (B[i] - A[i]) * b for i in range(6)], None, 0.0
def draw_prop(*a): pass
_char = _sec("# ---------------- character drawing", "# ---------------- panels")
_char = re.sub(r'        if prop == "id":.*?(?=        d2_alpha)', "        draw_prop(pd, prop, hx, hy)\n", _char, flags=re.S)
exec(_char)
exec(_sec("# ---------------- panels", "# ---------------- captions"))

def dtext(d, xy, s, f, col, a=255, anchor="mm"): d.text(xy, s, font=f, fill=col + (a,), anchor=anchor)
def dbox(c, x0, y0, x1, y1, title, a=255, col=EDGE):
    c.rounded_rectangle((x0, y0, x1, y1), radius=20, fill=CARD + (a,), outline=col + (a,), width=3)
    c.text(((x0 + x1) / 2, y0 + 38), title, font=font(F_BLACK, 36), fill=WHITE + (a,), anchor="mm")
def arrow_(c, x0, x1, y, col=(120, 130, 146), a=255):
    c.line((x0, y, x1, y), fill=col + (a,), width=6)
    s = 1 if x1 > x0 else -1
    c.polygon([(x1, y), (x1 - 20 * s, y - 13), (x1 - 20 * s, y + 13)], fill=col + (a,))
def mover(c, x0, x1, y, t, t0, dur, txt, col):
    p = (t - t0) / dur
    if p < 0 or p > 1.2: return
    q = ease_io(min(1, p)); x = x0 + (x1 - x0) * q; A = int(255 * (1 if p <= 1 else max(0, 1 - (p - 1) / 0.2)))
    f = font(F_MONOB, 26); tw = f.getlength(txt)
    c.rounded_rectangle((x - tw / 2 - 16, y - 24, x + tw / 2 + 16, y + 24), radius=24, fill=col + (A,))
    c.text((x, y), txt, font=f, fill=(255, 255, 255, A), anchor="mm")

def step_head(d, n, name, t, t0):
    col = STEPC[n - 1]; a = appear(t, t0); A = int(255 * a)
    f = font(F_BOLD, 34); lab = f"STEP {n}"; tw = f.getlength(lab)
    d.rounded_rectangle((540 - tw / 2 - 28, 0, 540 + tw / 2 + 28, 62), radius=31, fill=col + (A,))
    d.text((540, 31), lab, font=f, fill=(255, 255, 255, A), anchor="mm")
    dtext(d, (540, 140 + (1 - a) * 16), name, font(F_BLACK, 96), INKC, A)

def panel_A(t):
    t = t + 3.0
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    dtext(d, (540, 110), "What happens when", font(F_BLACK, 84), INKC)
    dtext(d, (540, 210), "you type a URL?", font(F_BLACK, 84), (30, 100, 200))
    d.rounded_rectangle((110, 330, 970, 430), radius=50, fill=(255, 255, 255), outline=(200, 205, 214), width=3)
    d.ellipse((150, 362, 186, 398), outline=(150, 156, 168), width=5); d.line((180, 392, 196, 408), fill=(150, 156, 168), width=5)
    full = "example.com"; n = len(full)
    d.text((220, 380), full[:n], font=font(F_MONOB, 44), fill=INKC, anchor="lm")
    d.rounded_rectangle((760, 345, 950, 415), radius=35, fill=(30, 100, 200)); d.text((855, 380), "Enter ↵", font=font(F_BOLD, 34), fill=(255, 255, 255), anchor="mm")
    dtext(d, (540, 540), "5 steps in under a second", font(F_BOLD, 46), SUB)
    return L

def panel_dns(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L); step_head(d, 1, "DNS lookup", t, SC[1] + 0.2)
    i = 1; c = d
    dbox(c, 80, 290, 400, 440, "Browser"); dbox(c, 680, 290, 1000, 440, "DNS server", col=STEPC[0])
    c.text((240, 400), "example.com ?", font=font(F_MONOB, 26), fill=YEL, anchor="mm")
    arrow_(c, 420, 660, 365)
    mover(c, 240, 840, 365, t, frac(i, 0.25), 1.0, "where is example.com?", STEPC[0])
    mover(c, 840, 240, 365, t, frac(i, 0.45), 1.0, "203.0.113.10", (12, 140, 110))
    p = appear(t, frac(i, 0.62), 0.3)
    if p > 0:
        A = int(255 * p)
        c.rounded_rectangle((200, 500, 880, 600), radius=20, fill=(255, 255, 255, A), outline=(210, 214, 222, A), width=3)
        c.text((540, 550), "example.com  →  203.0.113.10", font=font(F_MONOB, 36), fill=INKC + (A,), anchor="mm")
        dtext(c, (540, 660), "Like finding a number in your contacts", font(F_BOLD, 36), SUB, A)
    return L

def panel_conn(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L); step_head(d, 2, "Connect", t, SC[2] + 0.2)
    i = 2; c = d
    dbox(c, 80, 290, 400, 440, "Browser"); dbox(c, 680, 290, 1000, 440, "Server", col=STEPC[1])
    arrow_(c, 420, 660, 345); arrow_(c, 660, 420, 385)
    p = appear(t, frac(i, 0.45), 0.3)
    if p > 0:
        A = int(255 * p); cx, cy = 540, 520
        c.arc((cx - 40, cy - 90, cx + 40, cy - 10), 180, 360, fill=INKC + (A,), width=14)
        c.rounded_rectangle((cx - 60, cy - 40, cx + 60, cy + 50), radius=14, fill=STEPC[1] + (A,))
        c.ellipse((cx - 10, cy - 8, cx + 10, cy + 12), fill=(255, 255, 255, A))
        dtext(c, (540, 630), "HTTPS: the traffic is encrypted", font(F_BLACK, 44), STEPC[1], A)
        dtext(c, (540, 690), "Nobody in between can read it", font(F_BOLD, 34), SUB, A)
    return L

def panel_req(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L); step_head(d, 3, "The request", t, SC[3] + 0.2)
    i = 3; c = d
    p = appear(t, frac(i, 0.2), 0.3)
    if p > 0:
        A = int(255 * p)
        c.rounded_rectangle((140, 290, 940, 520), radius=22, fill=CARD + (A,))
        for k, (ln, col) in enumerate([("GET / HTTP/1.1", (63, 220, 130)), ("Host: example.com", WHITE), ("Accept: text/html", GREY)]):
            c.text((190, 340 + k * 60), ln, font=font(F_MONOB, 40), fill=col + (A,))
    q = appear(t, frac(i, 0.55), 0.3)
    if q > 0: dtext(c, (540, 620), "“Please send me your home page”", font(F_BLACK, 46), STEPC[2], int(255 * q))
    return L

def panel_srv(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L); step_head(d, 4, "The server works", t, SC[4] + 0.2)
    i = 4; c = d
    dbox(c, 80, 290, 400, 420, "Server", col=STEPC[3])
    p = appear(t, frac(i, 0.25), 0.3)
    if p > 0:
        A = int(255 * p)
        arrow_(c, 420, 560, 355, a=A)
        c.rectangle((600, 300, 800, 420), fill=CARD + (A,))
        c.ellipse((600, 280, 800, 320), fill=(40, 48, 64, A), outline=(120, 132, 150, A), width=3)
        c.ellipse((600, 400, 800, 440), fill=CARD + (A,), outline=(120, 132, 150, A), width=3)
        c.text((700, 370), "database", font=font(F_BOLD, 28), fill=WHITE + (A,), anchor="mm")
    q = appear(t, frac(i, 0.6), 0.3)
    if q > 0:
        A = int(255 * q)
        c.rounded_rectangle((140, 480, 940, 700), radius=22, fill=CARD + (A,))
        c.text((190, 525), "HTTP/1.1 200 OK", font=font(F_MONOB, 40), fill=(63, 220, 130) + (A,))
        c.text((190, 585), "Content-Type: text/html", font=font(F_MONOB, 34), fill=WHITE + (A,))
        c.text((190, 640), "<html>...</html>", font=font(F_MONOB, 34), fill=(165, 214, 255) + (A,))
    return L

def panel_render(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L); step_head(d, 5, "Render", t, SC[5] + 0.2)
    i = 5; c = d
    c.rounded_rectangle((140, 270, 940, 720), radius=22, fill=(255, 255, 255), outline=(200, 205, 214), width=3)
    c.rectangle((142, 272, 938, 320), fill=(236, 239, 244));
    for k, cc in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]): c.ellipse((165 + k * 30, 287, 183 + k * 30, 305), fill=cc)
    chips = [("HTML", (200, 95, 10), frac(i, 0.2)), ("CSS", (30, 100, 200), frac(i, 0.38)), ("JS", (180, 150, 0), frac(i, 0.48)), ("images", (12, 140, 110), frac(i, 0.58))]
    for k, (lab, col, t0) in enumerate(chips):
        p = appear(t, t0, 0.3)
        if p > 0:
            A = int(255 * p); x = 180 + k * 185
            c.rounded_rectangle((x, 345, x + 165, 400), radius=27, fill=col + (A,)); c.text((x + 82, 372), lab, font=font(F_BOLD, 30), fill=(255, 255, 255, A), anchor="mm")
    pnt = appear(t, frac(i, 0.75), 0.5)
    if pnt > 0:
        A = int(255 * pnt)
        c.rounded_rectangle((180, 430, 900, 500), radius=12, fill=(30, 100, 200, A))
        c.rounded_rectangle((180, 520, 520, 690), radius=12, fill=(225, 232, 242, A)); c.rounded_rectangle((550, 520, 900, 600), radius=12, fill=(225, 232, 242, A))
        c.rounded_rectangle((550, 615, 760, 690), radius=12, fill=(12, 140, 110, A))
    return L

def panel_recap(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a = appear(t, SC[6] + 0.2)
    dtext(d, (540, 40), "All in under a second", font(F_BLACK, 72), INKC, int(255 * a))
    for k, nm in enumerate(["DNS lookup", "Connect (HTTPS)", "Send the request", "Server responds", "Browser renders"]):
        p = appear(t, SC[6] + 0.4 + k * 0.35, 0.3)
        if p <= 0: continue
        A = int(255 * p); y = 130 + k * 115; X = 140 + (1 - p) * 120
        d.rounded_rectangle((X, y, X + 800, y + 95), radius=22, fill=CARD + (A,))
        d.ellipse((X + 20, y + 15, X + 85, y + 80), fill=STEPC[k] + (A,))
        d.text((X + 52, y + 48), str(k + 1), font=font(F_BLACK, 40), fill=(255, 255, 255, A), anchor="mm")
        d.text((X + 115, y + 48), nm, font=font(F_BLACK, 44), fill=WHITE + (A,), anchor="lm")
    return L

def panel_cta(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a = appear(t, SC[7] + 0.3); dtext(d, (540, 230 + (1 - a) * 20), "Follow for more", font(F_BLACK, 104), (30, 100, 200), int(255 * a))
    a = appear(t, SC[7] + 0.8); dtext(d, (540, 370), "Dev concepts, explained simply", font(F_BOLD, 52), INKC, int(255 * a))
    a = appear(t, SC[7] + 1.3)
    if a > 0:
        A = int(255 * a); f = font(F_BOLD, 36); s = "Next: CORS explained"; tw = f.getlength(s)
        d.rounded_rectangle((540 - tw / 2 - 30, 450, 540 + tw / 2 + 30, 520), radius=35, fill=INKC + (A,)); d.text((540, 485), s, font=f, fill=(255, 255, 255, A), anchor="mm")
    return L

PANELS = [panel_A, panel_dns, panel_conn, panel_req, panel_srv, panel_render, panel_recap, panel_cta]
exec(_sec("# ---------------- captions"))
def draw_caption(img, text, t, s):
    f = font(F_BLACK, 58); words = text.split(); sp = f.getlength(" ")
    tw = sum(f.getlength(w) for w in words) + sp * (len(words) - 1)
    p = ease((t - s) / 0.12)
    L = Image.new("RGBA", (W, 160), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    x = (W - tw) / 2; y = 50 + (1 - p) * 10; A = int(255 * p)
    for w in words:
        lw = w.lower().strip(".,!?")
        col = (30, 100, 200) if lw in ("dns", "https", "get", "html", "css", "javascript", "200") else INKC
        if lw in ("one", "two", "three", "four", "five"): col = (200, 95, 10)
        d.text((x, y), w, font=f, fill=col + (A,)); x += f.getlength(w) + sp
    img.alpha_composite(L, (0, 200))
def cap_text(s): return s.replace("two hundred OK", "200 OK")
CAPTIONS = [c for i in range(len(VO)) for c in chunks_for(i)]
_frame0 = frame
_WM = Image.open("/home/claude/nltech-videos/engine/assets/watermark_nltech.png").convert("RGBA")
def frame(t):
    im = _frame0(t).convert("RGBA"); im.alpha_composite(_WM, ((W - _WM.width) // 2, 92)); return im.convert("RGB")
