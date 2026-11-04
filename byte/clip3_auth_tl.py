"""Auth vs Authz explainer with original robot mascot 'Byte'. 1080x1920 @30fps."""
import json, math, re
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
SP = "/tmp/claude-0/-home-claude/e7805bda-0e11-5016-9991-51d072e57e6b/scratchpad/"
HERE = SP + "clip3/"
INTER = "/usr/share/fonts/opentype/inter/"
F_BLACK = INTER + "InterDisplay-Black.otf"
F_BOLD = INTER + "InterDisplay-Bold.otf"
F_SEMI = INTER + "Inter-SemiBold.otf"
F_MONO = SP + "fonts/JetBrainsMonoNL-Medium.ttf"
F_MONOB = SP + "fonts/JetBrainsMonoNL-Bold.ttf"

_fc = {}
def font(p, s):
    if (p, s) not in _fc: _fc[(p, s)] = ImageFont.truetype(p, s)
    return _fc[(p, s)]

def ease(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def ease_io(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))

BG = (9, 12, 19); WHITE = (240, 244, 250); GREY = (139, 148, 158); DIM = (90, 100, 116)
YEL = (255, 210, 63); RED = (255, 92, 92); GREEN = (63, 220, 130)
AN = (88, 166, 255)     # authentication blue
AZ = (255, 159, 67)     # authorization orange
CARD = (17, 22, 32); EDGE = (42, 52, 70)
MINT = (74, 222, 190); MINT_D = (44, 168, 140); INK = (12, 16, 24); SCREEN = (14, 24, 36)

# ---------------- background ----------------
_bg = None
def bg():
    global _bg
    if _bg is None:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        img = np.zeros((H, W, 3), np.float32) + np.array(BG, np.float32)
        img += np.exp(-(((x - 540) / 700) ** 2 + ((y - 250) / 650) ** 2))[..., None] * np.array([20, 45, 95], np.float32)
        img += np.exp(-(((x - 540) / 600) ** 2 + ((y - 1650) / 380) ** 2))[..., None] * np.array([10, 60, 55], np.float32)
        img[((x % 54) < 3) & ((y % 54) < 3)] += 12
        _bg = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
    return _bg.copy()

# ---------------- timeline ----------------
VO = json.load(open(HERE + "vo.json"))
vo_start = {}
def place(i, t):
    vo_start[i] = t; return t + VO[i]["dur"]

TR = 0.55  # slide transition length
SC = []    # scene start times
SC.append(0.0)
e = place(0, 0.3)
SC.append(e + 0.45)
e = place(1, SC[1] + TR); e = place(2, e + 0.35)
SWAP_B = vo_start[2] + VO[2]["dur"] * 0.44
SC.append(e + 0.45)
e = place(3, SC[2] + TR); e = place(4, e + 0.35)
SWAP_C = vo_start[4] + VO[4]["dur"] * 0.5
SC.append(e + 0.45)
e = place(5, SC[3] + TR)
STEP2 = vo_start[5] + VO[5]["dur"] * 0.55
SC.append(e + 0.45)
e = place(6, SC[4] + TR)
E403 = vo_start[6] + VO[6]["dur"] * 0.5
EFOOT = vo_start[6] + VO[6]["dur"] * 0.9
SC.append(e + 0.45)
e = place(7, SC[5] + TR)
DURATION = round((e + 1.6) * FPS) / FPS
NS = len(SC)

def scene_at(t):
    i = 0
    for k in range(NS):
        if t >= SC[k]: i = k
    return i

# card-level events for sfx
B1 = vo_start[2]; C1 = vo_start[4]
EVENTS = {
    "whoosh": SC[1:] + [SWAP_B, SWAP_C],
    "pop": [B1, vo_start[3] - 0.1, STEP2, vo_start[6], E403],
    "ding": [B1 + 1.3, SWAP_B + 3.0, C1 + 0.9, SWAP_C + 0.9],
    "buzz": [C1 + 2.3, SWAP_C + 1.9],
    "keys": [],
}

# ---------------- voice amplitude -> mouth ----------------
SR = 24000
_voice = np.zeros(int(SR * DURATION) + SR)
for i in range(len(VO)):
    a, sr = sf.read(HERE + f"vo{i}.wav")
    s = int(vo_start[i] * SR); _voice[s:s + len(a)] += a
VOICE = _voice
hop = SR // FPS
rms = np.array([np.sqrt(np.mean(VOICE[n * hop:(n + 1) * hop] ** 2) + 1e-9) for n in range(int(DURATION * FPS) + 2)])
rms = np.clip(rms / (np.percentile(rms[rms > 0.005], 90) + 1e-6), 0, 1.2)
MOUTH = np.convolve(rms, [0.25, 0.5, 0.25], "same")

def talking(t):
    for i in range(len(VO)):
        if vo_start[i] - 0.1 <= t <= vo_start[i] + VO[i]["dur"] + 0.1: return True
    return False

# ---------------- character poses ----------------
# pose = (L_shoulder, L_elbow, R_shoulder, R_elbow, wave_L, wave_R, prop)
POSES = {
    "idle":   (0.28, 0.15, 0.28, 0.15, 0, 0, None),
    "wave":   (0.28, 0.15, 2.55, 0.35, 0, 1, None),
    "point":  (0.30, 0.15, 2.35, -0.25, 0, 0, None),
    "id":     (1.25, -1.15, 2.35, -0.25, 0, 0, "id"),
    "key":    (1.25, -1.15, 2.35, -0.25, 0, 0, "key"),
    "both":   (2.55, 0.35, 2.55, 0.35, 1, 1, None),
    "shrug":  (1.05, 1.2, 1.05, 1.2, 0, 0, None),
}
KEYS = [(0.0, "wave"), (vo_start[0] + VO[0]["dur"], "idle"),
        (vo_start[1] - 0.15, "point"),
        (B1, "id"), (SWAP_B, "point"), (vo_start[2] + VO[2]["dur"], "idle"),
        (vo_start[3] - 0.15, "point"),
        (C1, "key"), (SWAP_C, "point"), (vo_start[4] + VO[4]["dur"], "idle"),
        (vo_start[5] - 0.15, "point"), (vo_start[5] + VO[5]["dur"], "idle"),
        (vo_start[6] - 0.15, "point"), (vo_start[6] + VO[6]["dur"] * 0.82, "shrug"), (vo_start[6] + VO[6]["dur"] + 0.2, "idle"),
        (vo_start[7] - 0.15, "both")]

def pose_at(t):
    cur, prev, ts = "idle", "idle", 0.0
    for k, (kt, name) in enumerate(KEYS):
        if t >= kt: prev, cur, ts = (KEYS[k - 1][1] if k else name), name, kt
    b = ease_io((t - ts) / 0.35)
    A, B = POSES[prev], POSES[cur]
    vals = [A[i] + (B[i] - A[i]) * b for i in range(6)]
    prop = B[6] if b > 0.5 else A[6]
    palpha = (b if B[6] else 1 - b) if A[6] != B[6] else (1.0 if B[6] else 0.0)
    return vals, prop, palpha

# ---------------- character drawing (2x supersampled) ----------------
CH_W, CH_H = 1080, 720   # region at 1x
CH_Y = 1180              # top of region in frame
S2 = 2

def draw_byte(t):
    n = int(round(t * FPS))
    im = Image.new("RGBA", (CH_W * S2, CH_H * S2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # hop on scene transitions
    hop_y = 0.0
    for st in SC[1:]:
        p = (t - st) / 0.5
        if 0 <= p <= 1: hop_y = -70 * math.sin(math.pi * p)
    bob = 10 * math.sin(2 * math.pi * t / 1.7)
    cx = CH_W  # center x at 2x
    oy = bob + hop_y
    tilt = 0.0

    # shadow
    sh = 1 - min(0.5, abs(hop_y) / 140)
    d.ellipse((cx - 230 * sh, 1330, cx + 230 * sh, 1380), fill=(0, 0, 0, 110))

    def R(box, r, fill, ol=INK, w=10):
        x0, y0, x1, y1 = box
        d.rounded_rectangle((x0, y0 + oy, x1, y1 + oy), radius=r, fill=fill, outline=ol, width=w)

    # legs
    for sx in (-1, 1):
        R((cx + sx * 95 - 45, 1160, cx + sx * 95 + 45, 1310), 30, MINT_D)
        R((cx + sx * 95 - 75, 1270, cx + sx * 95 + 75, 1330), 28, MINT_D)
    # body
    R((cx - 220, 900, cx + 220, 1220), 80, MINT)
    R((cx - 110, 980, cx + 110, 1120), 30, SCREEN, w=8)
    fb = font(F_MONOB, 70)
    glow = int(150 + 100 * (0.5 + 0.5 * math.sin(t * 3)))
    d.text((cx, 1050 + oy), "{ }", font=fb, fill=(110, 255, 210, glow), anchor="mm")

    vals, prop, palpha = pose_at(t)
    Ls, Le, Rs, Re, wl, wr = vals

    def arm(side, a1, a2, wave_amt):
        a2 = a2 + wave_amt * 0.55 * math.sin(t * 9)
        sx, sy = cx + side * 205, 960 + oy
        L1, L2 = 165, 150
        d1 = (side * math.sin(a1), math.cos(a1))
        ex, ey = sx + L1 * d1[0], sy + L1 * d1[1]
        a = a1 + a2
        d2 = (side * math.sin(a), math.cos(a))
        hx, hy = ex + L2 * d2[0], ey + L2 * d2[1]
        for (x0, y0, x1, y1) in ((sx, sy, ex, ey), (ex, ey, hx, hy)):
            d.line((x0, y0, x1, y1), fill=INK, width=74)
        for (x, y) in ((sx, sy), (ex, ey)):
            d.ellipse((x - 37, y - 37, x + 37, y + 37), fill=INK)
        for (x0, y0, x1, y1) in ((sx, sy, ex, ey), (ex, ey, hx, hy)):
            d.line((x0, y0, x1, y1), fill=MINT_D, width=54)
        for (x, y) in ((sx, sy), (ex, ey)):
            d.ellipse((x - 27, y - 27, x + 27, y + 27), fill=MINT_D)
        d.ellipse((hx - 50, hy - 50, hx + 50, hy + 50), fill=MINT, outline=INK, width=10)
        return hx, hy

    hl = arm(-1, Ls, Le, wl)
    hr = arm(1, Rs, Re, wr)

    # neck + head
    R((cx - 60, 860, cx + 60, 920), 16, MINT_D)
    # antenna
    d.line((cx, 420 + oy, cx, 290 + oy), fill=INK, width=26)
    d.line((cx, 420 + oy, cx, 290 + oy), fill=MINT_D, width=12)
    pulse = 0.5 + 0.5 * math.sin(t * 4)
    lc = (255, int(190 + 50 * pulse), 63) if talking(t) else (110, 255, 210)
    d.ellipse((cx - 44, 236 + oy, cx + 44, 324 + oy), fill=lc, outline=INK, width=10)
    # ears
    for sx in (-1, 1):
        R((cx + sx * 395 - 40, 560, cx + sx * 395 + 40, 740), 22, MINT_D)
    R((cx - 380, 400, cx + 380, 880), 130, MINT)
    R((cx - 315, 455, cx + 315, 825), 95, SCREEN, w=8)
    # screen shine
    d.rounded_rectangle((cx - 270, 480 + oy, cx - 150, 500 + oy), radius=10, fill=(255, 255, 255, 30))

    # eyes (blink + look)
    bp = (t % 3.3) / 3.3
    blink = 1.0
    if bp > 0.955: blink = abs((bp - 0.9775) / 0.0225)
    blink = max(0.08, blink)
    look = -14 if talking(t) else 0
    eh = 118 * blink
    for sx in (-1, 1):
        ex = cx + sx * 135
        d.rounded_rectangle((ex - 42, 600 - eh / 2 + oy + look, ex + 42, 600 + eh / 2 + oy + look),
                            radius=38 if blink > 0.4 else 8, fill=(110, 255, 210))
    # cheeks
    for sx in (-1, 1):
        d.ellipse((cx + sx * 220 - 34, 690 + oy, cx + sx * 220 + 34, 722 + oy), fill=(255, 120, 150, 90))
    # mouth
    m = float(MOUTH[min(n, len(MOUTH) - 1)]) if talking(t) else 0.0
    my = 735 + oy
    if m > 0.08:
        mh = 18 + 78 * min(1, m); mw = 92 + 30 * min(1, m)
        d.rounded_rectangle((cx - mw / 2, my - mh / 2, cx + mw / 2, my + mh / 2), radius=int(min(mw, mh) / 2),
                            fill=(255, 110, 130), outline=(110, 255, 210), width=8)
    else:
        d.arc((cx - 60, my - 50, cx + 60, my + 25), start=20, end=160, fill=(110, 255, 210), width=12)

    # props in left hand (screen-left)
    if prop and palpha > 0.02:
        hx, hy = hl
        pl = Image.new("RGBA", im.size, (0, 0, 0, 0)); pd = ImageDraw.Draw(pl)
        if prop == "id":
            x0, y0 = hx - 150, hy - 210
            pd.rounded_rectangle((x0, y0, x0 + 300, y0 + 190), radius=22, fill=(240, 244, 250), outline=INK, width=10)
            pd.rounded_rectangle((x0 + 22, y0 + 30, x0 + 112, y0 + 150), radius=12, fill=AN)
            pd.ellipse((x0 + 45, y0 + 50, x0 + 89, y0 + 94), fill=(240, 244, 250))
            pd.pieslice((x0 + 32, y0 + 98, x0 + 102, y0 + 170), 180, 360, fill=(240, 244, 250))
            for k in range(3):
                pd.rounded_rectangle((x0 + 132, y0 + 45 + k * 38, x0 + 270 - k * 30, y0 + 63 + k * 38), radius=9, fill=(160, 170, 184))
        else:
            x0, y0 = hx - 120, hy - 200
            pd.rounded_rectangle((x0, y0, x0 + 240, y0 + 160), radius=22, fill=AZ, outline=INK, width=10)
            pd.rounded_rectangle((x0 + 26, y0 + 30, x0 + 96, y0 + 80), radius=10, fill=(255, 220, 120), outline=INK, width=6)
            pd.text((x0 + 120, y0 + 118), "204", font=font(F_BLACK, 52), fill=INK, anchor="mm")
        d2_alpha = pl.getchannel("A").point(lambda v: int(v * palpha))
        pl.putalpha(d2_alpha)
        im.alpha_composite(pl)
        # redraw hand on top
        d.ellipse((hx - 50, hy - 50, hx + 50, hy + 50), fill=MINT, outline=INK, width=10)

    return im.resize((CH_W, CH_H), Image.LANCZOS)

# ---------------- small drawing helpers ----------------
def icon_check(d, cx, cy, r, col=GREEN, a=255):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col + (a,))
    w = max(4, int(r * 0.24))
    d.line((cx - r * 0.45, cy + r * 0.02, cx - r * 0.12, cy + r * 0.35, cx + r * 0.48, cy - r * 0.35), fill=(10, 30, 20, a), width=w, joint="curve")

def icon_cross(d, cx, cy, r, col=RED, a=255):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col + (a,))
    w = max(4, int(r * 0.24)); k = r * 0.38
    d.line((cx - k, cy - k, cx + k, cy + k), fill=(40, 10, 10, a), width=w)
    d.line((cx - k, cy + k, cx + k, cy - k), fill=(40, 10, 10, a), width=w)

def pill(d, text, cx, y, fg, bgc, size=32, a=255):
    f = font(F_BOLD, size); tw = f.getlength(text)
    d.rounded_rectangle((cx - tw / 2 - 26, y, cx + tw / 2 + 26, y + size + 28), radius=(size + 28) // 2, fill=bgc + (a,))
    d.text((cx, y + (size + 28) / 2), text, font=f, fill=fg + (a,), anchor="mm")

def ctext(d, text, cx, cy, f, col, a=255, shadow=True):
    if shadow: d.text((cx + 3, cy + 5), text, font=f, fill=(0, 0, 0, int(a * 0.55)), anchor="mm")
    d.text((cx, cy), text, font=f, fill=col + (a,), anchor="mm")

def card_box(d, x0, y0, x1, y1, label, a=255):
    d.rounded_rectangle((x0 + 6, y0 + 14, x1 + 6, y1 + 14), radius=30, fill=(0, 0, 0, int(a * 0.45)))
    d.rounded_rectangle((x0, y0, x1, y1), radius=30, fill=CARD + (a,), outline=EDGE + (a,), width=2)
    if label:
        d.text((x0 + 36, y0 + 30), label, font=font(F_BOLD, 26), fill=GREY + (a,))

def fade_layer(layer, a):
    if a >= 0.999: return layer
    al = layer.getchannel("A").point(lambda v: int(v * a)); layer.putalpha(al); return layer

# ---------------- panels (1080 x PH canvas) ----------------
PY, PH = 410, 760

def appear(t, t0, dur=0.35):
    return ease((t - t0) / dur)

def header(d, label, col, q, t, t0):
    a = appear(t, t0)
    if a <= 0: return
    pill(d, label, 540, 0 + (1 - a) * 16, col, tuple(int(c * 0.22) for c in col), a=int(255 * a))
    ctext(d, q, 540, 150 + (1 - a) * 20, font(F_BLACK, 92), WHITE, a=int(255 * a))

def panel_A(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    for (txt, f, col, y, t0) in [("Authentication", font(F_BLACK, 112), AN, 170, 0.25),
                                  ("vs", font(F_BOLD, 64), GREY, 300, 0.75),
                                  ("Authorization", font(F_BLACK, 112), AZ, 430, 1.15)]:
        a = appear(t, t0)
        if a > 0: ctext(d, txt, 540, y + (1 - a) * 30, f, col, a=int(255 * a))
    a = appear(t, vo_start[0] + VO[0]["dur"] * 0.45)
    if a > 0: pill(d, "Not the same thing.", 540, 560 + (1 - a) * 14, WHITE, (44, 50, 64), size=38, a=int(255 * a))
    return L

def slide_x(t, swap):
    """x-offsets for card1/card2 swapping horizontally at time swap."""
    p = ease_io((t - swap) / TR)
    return -W * p, W * (1 - p)

def panel_B(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    header(d, "AUTHENTICATION", AN, "Who are you?", t, SC[1] + 0.3)
    x1, x2 = slide_x(t, SWAP_B)
    # card 1: hotel ID
    a = appear(t, B1)
    if a > 0 and x1 > -W + 1:
        C = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); c = ImageDraw.Draw(C)
        oy = (1 - a) * 40
        card_box(c, 70, 250 + oy, 1010, 720 + oy, "REAL LIFE  ·  HOTEL FRONT DESK")
        # ID card
        X, Y = 120, 330 + oy
        c.rounded_rectangle((X, Y, X + 430, Y + 270), radius=26, fill=(236, 240, 246), outline=(60, 70, 90), width=4)
        c.rectangle((X, Y + 40, X + 430, Y + 52), fill=AN)
        c.rounded_rectangle((X + 30, Y + 78, X + 150, Y + 236), radius=14, fill=(200, 214, 232))
        c.ellipse((X + 60, Y + 100, X + 120, Y + 160), fill=(120, 140, 170))
        c.pieslice((X + 45, Y + 168, X + 135, Y + 260), 180, 360, fill=(120, 140, 170))
        c.text((X + 180, Y + 88), "ADA OKAFOR", font=font(F_BLACK, 34), fill=(30, 36, 48))
        for k, w_ in enumerate([200, 170, 120]):
            c.rounded_rectangle((X + 180, Y + 150 + k * 32, X + 180 + w_, Y + 166 + k * 32), radius=8, fill=(170, 180, 196))
        c.text((X + 22, Y + 8), "ID", font=font(F_BLACK, 26), fill=AN)
        ok = appear(t, B1 + 1.3, 0.3)
        if ok > 0:
            ctext(c, "Identity", 790, 420 + oy, font(F_BLACK, 50), WHITE, a=int(255 * ok), shadow=False)
            ctext(c, "confirmed", 790, 478 + oy, font(F_BLACK, 50), WHITE, a=int(255 * ok), shadow=False)
            r = 42 * (0.6 + 0.4 * ok)
            icon_check(c, 790, 580 + oy, r, a=int(255 * ok))
        L.alpha_composite(C, (int(x1), 0)) if x1 > -W else None
    # card 2: login form
    if t >= SWAP_B:
        C = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); c = ImageDraw.Draw(C)
        card_box(c, 70, 250, 1010, 720, "IN AN APP  ·  LOGIN")
        lt = t - SWAP_B - 0.5
        email = "ada@example.com"; ne = int(clamp(lt / 1.3) * len(email))
        npw = int(clamp((lt - 1.5) / 0.8) * 10)
        fm = font(F_MONO, 36)
        for k, (lab, val) in enumerate([("Email", email[:ne]), ("Password", "•" * npw)]):
            yy = 320 + k * 120
            c.text((120, yy), lab, font=font(F_SEMI, 26), fill=GREY)
            c.rounded_rectangle((120, yy + 36, 960, yy + 100), radius=14, fill=(10, 14, 22), outline=EDGE, width=2)
            c.text((146, yy + 50), val, font=fm, fill=WHITE)
            active = (k == 0 and 0 <= lt < 1.4) or (k == 1 and 1.4 <= lt < 2.4)
            if active and int(t * 3) % 2 == 0:
                cxp = 146 + fm.getlength(val) + 4
                c.rectangle((cxp, yy + 50, cxp + 4, yy + 90), fill=AN)
        press = 1.0 - 0.06 * math.sin(math.pi * clamp((lt - 2.5) / 0.25))
        ok = appear(t, SWAP_B + 3.0, 0.3)
        bw, bh = 300 * press, 74 * press
        if ok <= 0:
            c.rounded_rectangle((540 - bw / 2, 600 - bh / 2, 540 + bw / 2, 600 + bh / 2), radius=18, fill=AN)
            ctext(c, "Log in", 540, 600, font(F_BLACK, 36), (8, 16, 30), shadow=False)
        else:
            c.rounded_rectangle((200, 563, 880, 637), radius=18, fill=(20, 70, 46, int(255 * ok)), outline=GREEN + (int(255 * ok),), width=3)
            icon_check(c, 260, 600, 24, a=int(255 * ok))
            c.text((300, 600), "Logged in as Ada", font=font(F_BLACK, 36), fill=GREEN + (int(255 * ok),), anchor="lm")
        L.alpha_composite(C, (int(x2), 0))
    return L

def door(c, x, y, label, state, a_light, open_amt):
    c.rounded_rectangle((x, y, x + 300, y + 330), radius=14, fill=(34, 40, 54), outline=(70, 80, 100), width=3)
    w = 260 * (1 - 0.35 * open_amt)
    c.rectangle((x + 20, y + 20, x + 20 + w, y + 330), fill=(120, 84, 60) if state else (96, 70, 56))
    c.ellipse((x + 20 + w - 44, y + 170, x + 20 + w - 20, y + 194), fill=(230, 200, 120))
    # reader light
    col = (GREEN if state else RED) if a_light > 0 else (80, 90, 104)
    c.rounded_rectangle((x + 236, y + 60, x + 280, y + 120), radius=8, fill=(20, 24, 30))
    c.ellipse((x + 246, y + 70, x + 270, y + 94), fill=col)
    c.text((x + 150, y + 370), label, font=font(F_BLACK, 34), fill=WHITE, anchor="mm")
    if a_light > 0:
        (icon_check if state else icon_cross)(c, x + 150, y + 420, 26 * (0.6 + 0.4 * a_light), a=int(255 * a_light))

def panel_C(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    header(d, "AUTHORIZATION", AZ, "What can you do?", t, SC[2] + 0.3)
    x1, x2 = slide_x(t, SWAP_C)
    a = appear(t, C1)
    if a > 0 and x1 > -W + 1:
        C = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); c = ImageDraw.Draw(C)
        oy = int((1 - a) * 40)
        card_box(c, 70, 230 + oy, 1010, 740 + oy, "REAL LIFE  ·  YOUR KEY CARD")
        a1 = appear(t, C1 + 0.9, 0.25); a2 = appear(t, C1 + 2.3, 0.25)
        door(c, 170, 290 + oy, "Room 204", True, a1, a1)
        door(c, 610, 290 + oy, "Manager", False, a2, 0)
        L.alpha_composite(C, (int(x1), 0))
    if t >= SWAP_C:
        C = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); c = ImageDraw.Draw(C)
        card_box(c, 70, 250, 1010, 720, "IN AN APP  ·  LOGGED IN AS: USER")
        fm = font(F_MONOB, 44)
        rows = [("/profile", True, SWAP_C + 0.9, "200 OK"), ("/admin", False, SWAP_C + 1.9, "403 Denied")]
        for k, (route, okk, t0, res) in enumerate(rows):
            yy = 350 + k * 170
            c.rounded_rectangle((120, yy, 960, yy + 130), radius=20, fill=(10, 14, 22), outline=EDGE, width=2)
            c.text((160, yy + 65), "GET", font=font(F_MONOB, 30), fill=GREY, anchor="lm")
            c.text((250, yy + 65), route, font=fm, fill=WHITE, anchor="lm")
            ra = appear(t, t0, 0.3)
            if ra > 0:
                col = GREEN if okk else RED
                (icon_check if okk else icon_cross)(c, 640, yy + 65, 28 * (0.6 + 0.4 * ra), a=int(255 * ra))
                c.text((690, yy + 65), res, font=font(F_BLACK, 40), fill=col + (int(255 * ra),), anchor="lm")
        L.alpha_composite(C, (int(x2), 0))
    return L

def panel_D(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a = appear(t, SC[3] + 0.3)
    pill(d, "THE ORDER", 540, (1 - a) * 16, YEL, (60, 50, 14), a=int(255 * a))
    for k, (num, name, q, col, t0, y) in enumerate([("1", "Authentication", "Proves who you are", AN, vo_start[5] + 0.2, 110),
                                                     ("2", "Authorization", "Decides what you can access", AZ, STEP2, 440)]):
        p = appear(t, t0, 0.4)
        if p <= 0: continue
        X = 70 + (1 - p) * 300
        A = int(255 * p)
        d.rounded_rectangle((X + 6, y + 14, X + 946, y + 254), radius=30, fill=(0, 0, 0, int(A * 0.45)))
        d.rounded_rectangle((X, y, X + 940, y + 240), radius=30, fill=CARD + (A,), outline=col + (A,), width=4)
        d.ellipse((X + 40, y + 60, X + 160, y + 180), fill=col + (A,))
        d.text((X + 100, y + 120), num, font=font(F_BLACK, 72), fill=INK + (A,), anchor="mm")
        d.text((X + 200, y + 50), name, font=font(F_BLACK, 66), fill=col + (A,))
        d.text((X + 200, y + 140), q, font=font(F_BOLD, 42), fill=WHITE + (A,))
        if k == 1:
            # arrow between
            ay0, ay1 = 365, 425
            d.line((540, ay0, 540, ay1 - 10), fill=GREY + (A,), width=10)
            d.polygon([(510, ay1 - 30), (570, ay1 - 30), (540, ay1 + 8)], fill=GREY + (A,))
    return L

def panel_E(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a = appear(t, SC[4] + 0.3)
    pill(d, "BONUS TIP", 540, (1 - a) * 16, YEL, (60, 50, 14), a=int(255 * a))
    for (code, name, desc, col, t0, y) in [("401", "Unauthorized", "Not logged in", AN, vo_start[6] + 0.3, 100),
                                            ("403", "Forbidden", "Logged in, not allowed", AZ, E403, 380)]:
        p = appear(t, t0, 0.4)
        if p <= 0: continue
        X = 70 + (1 - p) * 300; A = int(255 * p)
        d.rounded_rectangle((X + 6, y + 14, X + 946, y + 244), radius=30, fill=(0, 0, 0, int(A * 0.45)))
        d.rounded_rectangle((X, y, X + 940, y + 230), radius=30, fill=CARD + (A,), outline=col + (A,), width=4)
        d.text((X + 50, y + 115), code, font=font(F_BLACK, 130), fill=col + (A,), anchor="lm")
        d.text((X + 370, y + 55), name, font=font(F_BLACK, 54), fill=WHITE + (A,))
        d.text((X + 370, y + 135), desc, font=font(F_BOLD, 40), fill=GREY + (A,))
    p = appear(t, EFOOT, 0.4)
    if p > 0:
        A = int(255 * p)
        d.text((540, 680), "Fun fact: 401 says “Unauthorized”", font=font(F_BOLD, 36), fill=YEL + (A,), anchor="mm")
        d.text((540, 728), "but really means “not authenticated”.", font=font(F_BOLD, 36), fill=YEL + (A,), anchor="mm")
    return L

def panel_F(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a = appear(t, SC[5] + 0.35)
    ctext(d, "Follow for more", 540, 230 + (1 - a) * 24, font(F_BLACK, 104), YEL, a=int(255 * a))
    a = appear(t, SC[5] + 0.9)
    ctext(d, "Dev concepts, explained simply", 540, 370 + (1 - a) * 20, font(F_BOLD, 52), WHITE, a=int(255 * a))
    a = appear(t, SC[5] + 1.5)
    if a > 0: pill(d, "Next: JWT vs Sessions", 540, 470 + (1 - a) * 14, WHITE, (44, 50, 64), size=36, a=int(255 * a))
    return L

PANELS = [panel_A, panel_B, panel_C, panel_D, panel_E, panel_F]

# ---------------- captions ----------------
def cap_text(s):
    return s.replace("four oh one", "401").replace("four oh three", "403")

def chunks_for(i):
    words = cap_text(VO[i]["text"]).split()
    out, cur = [], []
    for w in words:
        cur.append(w)
        if len(" ".join(cur)) > 22 or w[-1] in ".?!,":
            out.append(" ".join(cur)); cur = []
    if cur: out.append(" ".join(cur))
    total = sum(len(c) + 3 for c in out); t = vo_start[i]; res = []
    for c in out:
        dur = VO[i]["dur"] * (len(c) + 3) / total; res.append((t, t + dur, c)); t += dur
    return res
CAPTIONS = [c for i in range(len(VO)) for c in chunks_for(i)]

def wcol(w):
    lw = w.lower()
    if lw.startswith("authentic"): return AN
    if lw.startswith("authoriz"): return AZ
    if "401" in lw: return AN
    if "403" in lw: return AZ
    if lw.strip(".,?!") in ("who", "what", "id", "admin", "manager's"): return YEL
    return WHITE

def draw_caption(img, text, t, s):
    f = font(F_BLACK, 62); words = text.split(); sp = f.getlength(" ")
    tw = sum(f.getlength(w) for w in words) + sp * (len(words) - 1)
    p = ease((t - s) / 0.12)
    L = Image.new("RGBA", (W, 160), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    x = (W - tw) / 2; y = 50 + (1 - p) * 10; A = int(255 * p)
    for w in words:
        d.text((x + 3, y + 5), w, font=f, fill=(0, 0, 0, int(A * 0.6)))
        d.text((x, y), w, font=f, fill=wcol(w) + (A,)); x += f.getlength(w) + sp
    img.alpha_composite(L, (0, 200))

# ---------------- frame ----------------
def frame(t):
    img = bg()
    i = scene_at(t)
    st = SC[i]
    if i > 0 and t < st + TR:
        p = ease_io((t - st) / TR)
        prev = PANELS[i - 1](t)
        cur = PANELS[i](t)
        img.alpha_composite(prev, (int(-W * p), PY))
        img.alpha_composite(cur, (int(W * (1 - p)), PY))
    else:
        img.alpha_composite(PANELS[i](t), (0, PY))
    img.alpha_composite(draw_byte(t), (0, CH_Y))
    for s, e_, c in CAPTIONS:
        if s <= t < e_:
            draw_caption(img, c, t, s); break
    return img.convert("RGB")
