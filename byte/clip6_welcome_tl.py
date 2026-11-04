"""Welcome / channel intro with Byte, white background."""
import re, json, math
SP = "/tmp/claude-0/-home-claude/e7805bda-0e11-5016-9991-51d072e57e6b/scratchpad/"
_SRC = open(SP + "clip3/tl.py").read()
def _sec(a, b=None):
    i = _SRC.index(a); j = _SRC.index(b) if b else len(_SRC)
    return _SRC[i:j]
exec(_SRC[:_SRC.index("# ---------------- timeline")])
HERE = SP + "clip6/"
INKC = (17, 24, 39); SUB = (90, 100, 116)

# white background with a soft mint glow behind Byte
_wbg = None
def bg():
    global _wbg
    if _wbg is None:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        img = np.zeros((H, W, 3), np.float32) + np.array([248, 249, 251], np.float32)
        img -= np.exp(-(((x - 540) / 600) ** 2 + ((y - 1600) / 380) ** 2))[..., None] * np.array([22, 6, 14], np.float32)
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
e = place(0, 0.3); SC.append(e + 0.35)
e = place(1, SC[1] + TR); SC.append(e + 0.35)
e = place(2, SC[2] + TR); SC.append(e + 0.35)
e = place(3, SC[3] + TR); SC.append(e + 0.35)
e = place(4, SC[4] + TR)
DURATION = round((e + 1.4) * FPS) / FPS
NS = len(SC)
def scene_at(t):
    i = 0
    for k in range(NS):
        if t >= SC[k]: i = k
    return i
TILES = [frac(2, 0.02), frac(2, 0.22), frac(2, 0.42), frac(2, 0.6)]
EVENTS = {"whoosh": [], "swish": [], "pop": TILES + [frac(3, 0.3), frac(4, 0.5)], "ding": [], "buzz": []}

exec(_sec("# ---------------- voice amplitude", "# ---------------- character poses"))
POSES = {
    "idle":  (0.28, 0.15, 0.28, 0.15, 0, 0, None),
    "wave":  (0.28, 0.15, 2.55, 0.35, 0, 1, None),
    "point": (0.30, 0.15, 2.35, -0.25, 0, 0, None),
    "both":  (2.55, 0.35, 2.55, 0.35, 1, 1, None),
}
KEYS = [(0.0, "wave"), (vend(0), "point"), (vend(3), "idle"), (vo_start[4] - 0.1, "both")]
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

def dtext(d, xy, s, f, col, a=255): d.text(xy, s, font=f, fill=col + (a,), anchor="mm")

def panel_A(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a = appear(t, 0.25); dtext(d, (540, 200 + (1 - a) * 30), "Hey, I'm Byte", font(F_BLACK, 120), INKC, int(255 * a))
    a = appear(t, 1.2); dtext(d, (540, 340 + (1 - a) * 20), "Welcome to", font(F_BOLD, 54), SUB, int(255 * a))
    a = appear(t, 1.5); dtext(d, (540, 440 + (1 - a) * 20), "Nicholas Lechi Tech", font(F_BLACK, 84), (12, 140, 110), int(255 * a))
    return L

def panel_B(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a = appear(t, SC[1] + 0.2); dtext(d, (540, 130 + (1 - a) * 20), "Every day:", font(F_BOLD, 54), SUB, int(255 * a))
    for k, (txt, col, t0, y) in enumerate([("Dev concepts", INKC, SC[1] + 0.4, 250), ("in plain English", (30, 100, 200), SC[1] + 0.8, 360),
                                           ("+ real code", INKC, frac(1, 0.55), 500), ("you can use", (200, 95, 10), frac(1, 0.7), 610)]):
        a = appear(t, t0); dtext(d, (540, y + (1 - a) * 24), txt, font(F_BLACK, 96), col, int(255 * a))
    return L

def panel_C(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    tiles = [("8am", "Quick tips", YEL), ("12pm", "Cheat sheets", AN), ("4pm", "Byte explains", MINT), ("8pm", "Build a Real API", AZ)]
    for k, ((tm, name, col), t0) in enumerate(zip(tiles, TILES)):
        p = appear(t, t0, 0.35)
        if p <= 0: continue
        A = int(255 * p); y = 40 + k * 175; X = 90 + (1 - p) * 200
        d.rounded_rectangle((X + 6, y + 12, X + 906, y + 152), radius=28, fill=(0, 0, 0, int(A * 0.12)))
        d.rounded_rectangle((X, y, X + 900, y + 140), radius=28, fill=CARD + (A,))
        d.rounded_rectangle((X, y, X + 16, y + 140), radius=8, fill=col + (A,))
        d.text((X + 60, y + 70), tm, font=font(F_MONOB, 46), fill=col + (A,), anchor="lm")
        d.text((X + 250, y + 70), name, font=font(F_BLACK, 58), fill=WHITE + (A,), anchor="lm")
    return L

def panel_D(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a = appear(t, SC[3] + 0.2); dtext(d, (540, 120 + (1 - a) * 20), "Made by", font(F_BOLD, 54), SUB, int(255 * a))
    a = appear(t, SC[3] + 0.45); dtext(d, (540, 230 + (1 - a) * 24), "Nicholas", font(F_BLACK, 130), INKC, int(255 * a))
    a = appear(t, frac(3, 0.3)); dtext(d, (540, 360 + (1 - a) * 20), "Full-stack engineer", font(F_BLACK, 64), (12, 140, 110), int(255 * a))
    p = appear(t, frac(3, 0.55))
    if p > 0:
        x = 540; tags = ["NestJS", "React", "Next.js", "PostgreSQL"]
        f = font(F_BOLD, 36); widths = [f.getlength(s) + 50 for s in tags]; tot = sum(widths) + 16 * 3; x = 540 - tot / 2
        for s, w_ in zip(tags, widths):
            d.rounded_rectangle((x, 450, x + w_, 516), radius=33, fill=(17, 24, 39, int(255 * p)))
            d.text((x + w_ / 2, 483), s, font=f, fill=WHITE + (int(255 * p),), anchor="mm"); x += w_ + 16
    p = appear(t, frac(3, 0.75))
    if p > 0: dtext(d, (540, 600), "Building real apps for real clients", font(F_BOLD, 44), SUB, int(255 * p))
    return L

def panel_E(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a = appear(t, SC[4] + 0.2); dtext(d, (540, 150 + (1 - a) * 20), "Learning to code?", font(F_BLACK, 80), INKC, int(255 * a))
    a = appear(t, frac(4, 0.35)); dtext(d, (540, 260 + (1 - a) * 20), "Want to level up?", font(F_BLACK, 80), INKC, int(255 * a))
    p = appear(t, frac(4, 0.55))
    if p > 0:
        A = int(255 * p); f = font(F_BLACK, 76); s = "Follow  ·  Let's build"
        tw = f.getlength(s)
        d.rounded_rectangle((540 - tw / 2 - 50, 380, 540 + tw / 2 + 50, 520), radius=70, fill=(12, 140, 110, A))
        d.text((540, 450), s, font=f, fill=WHITE + (A,), anchor="mm")
    p = appear(t, frac(4, 0.8))
    if p > 0: dtext(d, (540, 600), "@nicholaslechitech", font(F_BOLD, 46), SUB, int(255 * p))
    return L

PANELS = [panel_A, panel_B, panel_C, panel_D, panel_E]
exec(_sec("# ---------------- captions"))

def draw_caption(img, text, t, s):
    f = font(F_BLACK, 60); words = text.split(); sp = f.getlength(" ")
    tw = sum(f.getlength(w) for w in words) + sp * (len(words) - 1)
    p = ease((t - s) / 0.12)
    L = Image.new("RGBA", (W, 160), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    x = (W - tw) / 2; y = 50 + (1 - p) * 10; A = int(255 * p)
    for w in words:
        lw = w.lower().strip(".,!?")
        col = (12, 140, 110) if lw in ("byte,", "byte", "nicholas", "follow,") else INKC
        d.text((x, y), w, font=f, fill=col + (A,)); x += f.getlength(w) + sp
    img.alpha_composite(L, (0, 200))
def cap_text(s): return s.replace("full stack", "full-stack")
CAPTIONS = [c for i in range(len(VO)) for c in chunks_for(i)]

_frame0 = frame
_WM = Image.open("/home/claude/nltech-videos/engine/assets/watermark_nltech.png").convert("RGBA")
def frame(t):
    im = _frame0(t).convert("RGBA"); im.alpha_composite(_WM, ((W - _WM.width) // 2, 92)); return im.convert("RGB")
