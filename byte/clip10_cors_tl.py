"""CORS explained with Byte, plum background."""
import re, json, math
SP = "/tmp/claude-0/-home-claude/e7805bda-0e11-5016-9991-51d072e57e6b/scratchpad/"
_SRC = open(SP + "clip3/tl.py").read()
_S4 = open(SP + "clip4/tl.py").read()
def _sec(a, b=None):
    i = _SRC.index(a); j = _SRC.index(b) if b else len(_SRC)
    return _SRC[i:j]
exec(_SRC[:_SRC.index("# ---------------- timeline")])
HERE = SP + "clip10/"
C_PUN, C_ID, C_STR, C_KW2, C_FN = (201, 209, 217), (230, 237, 243), (165, 214, 255), (255, 123, 114), (210, 168, 255)

_pbg = None
def bg():
    global _pbg
    if _pbg is None:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        img = np.zeros((H, W, 3), np.float32) + np.array([22, 12, 32], np.float32)
        img += np.exp(-(((x - 540) / 700) ** 2 + ((y - 250) / 650) ** 2))[..., None] * np.array([62, 22, 74], np.float32)
        img += np.exp(-(((x - 540) / 600) ** 2 + ((y - 1650) / 380) ** 2))[..., None] * np.array([40, 20, 60], np.float32)
        img[((x % 54) < 3) & ((y % 54) < 3)] += 12
        _pbg = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
    return _pbg.copy()

VO = json.load(open(HERE + "vo.json"))
vo_start = {}
def place(i, t):
    vo_start[i] = t; return t + VO[i]["dur"]
def vend(i): return vo_start[i] + VO[i]["dur"]
def frac(i, f): return vo_start[i] + VO[i]["dur"] * f
TR = 0.55
SC = [0.0]
for i in range(7):
    e = place(i, SC[-1] + (0.3 if i == 0 else TR)); SC.append(e + 0.45)
e = place(7, SC[-1] + TR)
DURATION = round((e + 1.6) * FPS) / FPS
NS = len(SC)
def scene_at(t):
    i = 0
    for k in range(NS):
        if t >= SC[k]: i = k
    return i
PINK = (240, 90, 175); BLUEC = AN
O1, O2, O3 = frac(1, 0.55), frac(1, 0.7), frac(1, 0.85)
R_GO = frac(2, 0.55); R_BLOCK = frac(2, 0.8)
K_EVIL = frac(3, 0.35); K_BLOCK = frac(3, 0.7)
H_HDR = frac(4, 0.6); H_OK = frac(4, 0.85)
N_CODE = vo_start[5] + 0.4
P1, P2 = frac(6, 0.1), frac(6, 0.6)
EVENTS = {"whoosh": [], "swish": [], "pop": [O1, O2, O3, R_GO, K_EVIL, H_HDR, N_CODE, P1, P2], "ding": [H_OK], "buzz": []}

exec(_sec("# ---------------- voice amplitude", "# ---------------- character poses"))
POSES = {"idle": (0.28, 0.15, 0.28, 0.15, 0, 0, None), "wave": (0.28, 0.15, 2.55, 0.35, 0, 1, None),
         "point": (0.30, 0.15, 2.35, -0.25, 0, 0, None), "both": (2.55, 0.35, 2.55, 0.35, 1, 1, None),
         "shrug": (1.05, 1.2, 1.05, 1.2, 0, 0, None)}
KEYS = [(0.0, "shrug"), (vend(0), "point"), (vend(6), "idle"), (vo_start[7] - 0.1, "both")]
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
exec(_S4[_S4.index("# ---------------- generic bits"):_S4.index("def panel_A")])

def panel_A(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    ctext(d, "CORS", 540, 120, font(F_BLACK, 190), PINK)
    ctext(d, "explained", 540, 270, font(F_BLACK, 84), WHITE)
    d.rounded_rectangle((90, 370, 990, 620), radius=22, fill=(40, 14, 20), outline=RED, width=3)
    d.rounded_rectangle((90, 370, 104, 620), radius=7, fill=RED)
    f = font(F_MONO, 28)
    for k, ln in enumerate(["Access to fetch at 'http://localhost:4000'", "from origin 'http://localhost:3000' has", "been blocked by CORS policy: No", "'Access-Control-Allow-Origin' header."]):
        d.text((130, 400 + k * 52), ln, font=f, fill=(255, 190, 190))
    return L

def panel_B(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    head(d, "WHAT IS AN ORIGIN?", PINK, "Protocol + domain + port", t, SC[1] + 0.3, size=74)
    parts = [("https://", BLUEC, "protocol", O1), ("example.com", YEL, "domain", O2), (":443", GREEN, "port", O3)]
    f = font(F_MONOB, 64); tot = sum(f.getlength(p[0]) for p in parts); x = 540 - tot / 2
    for (txt, col, lab, t0) in parts:
        p = appear(t, t0, 0.3); A = int(255 * max(0.25, p)); w = f.getlength(txt)
        d.text((x, 360), txt, font=f, fill=col + (A,), anchor="lm")
        if p > 0:
            d.line((x + 4, 410, x + w - 4, 410), fill=col + (int(255 * p),), width=6)
            d.text((x + w / 2, 450), lab, font=font(F_BOLD, 34), fill=col + (int(255 * p),), anchor="mm")
        x += w
    p = appear(t, frac(1, 0.9), 0.3)
    if p > 0: ctext(d, "Change any one, and it's a different origin", 540, 580, font(F_BOLD, 38), WHITE, a=int(255 * p))
    return L

def panel_C(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    head(d, "DIFFERENT PORTS", PINK, "Different origins", t, SC[2] + 0.3, size=84)
    box(d, 80, 300, 420, 460, "Frontend"); d.text((250, 420), "localhost:3000", font=font(F_MONOB, 28), fill=BLUEC, anchor="mm")
    box(d, 660, 300, 1000, 460, "API"); d.text((830, 420), "localhost:4000", font=font(F_MONOB, 28), fill=GREEN, anchor="mm")
    arrow(d, 440, 640, 360)
    packet(d, 250, 830, 360, t, R_GO, 0.9, "fetch()", BLUEC)
    p = appear(t, R_BLOCK, 0.3)
    if p > 0:
        A = int(255 * p)
        d.line((440, 410, 640, 410), fill=RED + (A,), width=6)
        d.polygon([(440, 410), (460, 398), (460, 422)], fill=RED + (A,))
        icon_cross(d, 540, 410, 28, a=A)
        ctext(d, "Browser hides the response", 540, 560, font(F_BLACK, 50), RED, a=A)
        ctext(d, "(the request still reached the API)", 540, 625, font(F_BOLD, 32), GREY, a=A)
    return L

def panel_D(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    head(d, "WHY IT EXISTS", PINK, "It protects you", t, SC[3] + 0.3, size=90)
    p = appear(t, K_EVIL, 0.3)
    if p > 0:
        A = int(255 * p)
        d.rounded_rectangle((80, 300, 420, 470), radius=20, fill=(40, 14, 20, A), outline=RED + (A,), width=3)
        d.text((250, 350), "evil-site.com", font=font(F_MONOB, 32), fill=RED + (A,), anchor="mm")
        d.text((250, 410), "“read their balance”", font=font(F_BOLD, 28), fill=GREY + (A,), anchor="mm")
        d.rounded_rectangle((660, 300, 1000, 470), radius=20, fill=(10, 30, 22, A), outline=GREEN + (A,), width=3)
        d.text((830, 350), "your-bank.com", font=font(F_MONOB, 32), fill=GREEN + (A,), anchor="mm")
        d.text((830, 410), "you're logged in", font=font(F_BOLD, 28), fill=GREY + (A,), anchor="mm")
        arrow(d, 440, 640, 385, a=A)
    q = appear(t, K_BLOCK, 0.3)
    if q > 0:
        A = int(255 * q)
        sx, sy = 540, 560
        d.polygon([(sx, sy - 70), (sx + 60, sy - 45), (sx + 52, sy + 25), (sx, sy + 70), (sx - 52, sy + 25), (sx - 60, sy - 45)], fill=PINK + (A,))
        d.line((sx - 22, sy, sx - 5, sy + 18, sx + 25, sy - 20), fill=WHITE + (A,), width=10)
        ctext(d, "Blocked by the browser", 540, 690, font(F_BLACK, 46), WHITE, a=A)
    return L

def panel_E(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    head(d, "THE FIX", GREEN, "The server says who's allowed", t, SC[4] + 0.3, size=70)
    d.rounded_rectangle((80, 280, 1000, 560), radius=22, fill=CARD, outline=EDGE, width=2)
    d.text((120, 320), "HTTP/1.1 200 OK", font=font(F_MONOB, 36), fill=GREEN)
    d.text((120, 380), "Content-Type: application/json", font=font(F_MONO, 30), fill=GREY)
    p = appear(t, H_HDR, 0.3)
    if p > 0:
        A = int(255 * p)
        d.rounded_rectangle((105, 430, 975, 530), radius=14, fill=YEL + (int(40 * p),), outline=YEL + (A,), width=3)
        d.text((125, 440), "Access-Control-Allow-Origin:", font=font(F_MONOB, 32), fill=YEL + (A,))
        d.text((125, 484), "  http://localhost:3000", font=font(F_MONOB, 32), fill=WHITE + (A,))
    q = appear(t, H_OK, 0.3)
    if q > 0:
        icon_check(d, 360, 650, 30, a=int(255 * q))
        d.text((410, 650), "Browser allows it", font=font(F_BLACK, 46), fill=GREEN + (int(255 * q),), anchor="lm")
    return L

def panel_F(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    head(d, "IN NESTJS", PINK, "One line in main.ts", t, SC[5] + 0.3, size=84)
    p = appear(t, N_CODE, 0.35)
    if p > 0:
        A = int(255 * p); f = font(F_MONOB, 36)
        d.rounded_rectangle((80, 290, 1000, 560), radius=22, fill=CARD + (A,), outline=EDGE + (A,), width=2)
        lines = [[("app", C_ID), (".", C_PUN), ("enableCors", C_FN), ("({", C_PUN)],
                 [("  origin", C_ID), (": ", C_PUN), ("'http://localhost:3000'", C_STR), (",", C_PUN)],
                 [("});", C_PUN)]]
        for k, toks in enumerate(lines):
            x = 120
            for s, c in toks:
                d.text((x, 330 + k * 70), s, font=f, fill=c + (A,)); x += f.getlength(s)
    q = appear(t, frac(5, 0.8), 0.3)
    if q > 0: ctext(d, "Put your real frontend URL here", 540, 640, font(F_BOLD, 38), YEL, a=int(255 * q))
    return L

def panel_G(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a = appear(t, SC[6] + 0.3)
    pill(d, "PRO TIP · SECURITY", 540, (1 - a) * 16, YEL, (60, 50, 14), a=int(255 * a))
    for k, (ok, txt, sub, t0) in enumerate([(False, "origin: '*'", "on an API with logins", P1), (True, "List your trusted sites", "e.g. your real frontend URL", P2)]):
        p = appear(t, t0, 0.35)
        if p <= 0: continue
        A = int(255 * p); y = 130 + k * 230; X = 70 + (1 - p) * 200; col = GREEN if ok else RED
        d.rounded_rectangle((X, y, X + 940, y + 190), radius=26, fill=CARD + (A,), outline=col + (A,), width=3)
        (icon_check if ok else icon_cross)(d, X + 80, y + 95, 38, a=A)
        d.text((X + 145, y + 70), txt, font=font(F_MONOB if not ok else F_BLACK, 48), fill=WHITE + (A,), anchor="lm")
        d.text((X + 145, y + 135), sub, font=font(F_BOLD, 34), fill=GREY + (A,), anchor="lm")
    return L

def panel_H(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a = appear(t, SC[7] + 0.35); ctext(d, "Follow for more", 540, 230 + (1 - a) * 24, font(F_BLACK, 104), YEL, a=int(255 * a))
    a = appear(t, SC[7] + 0.9); ctext(d, "Dev concepts, explained simply", 540, 370 + (1 - a) * 20, font(F_BOLD, 52), WHITE, a=int(255 * a))
    a = appear(t, SC[7] + 1.5)
    if a > 0: pill(d, "Next: Git merge vs rebase", 540, 470 + (1 - a) * 14, WHITE, (60, 40, 80), size=36, a=int(255 * a))
    return L

PANELS = [panel_A, panel_B, panel_C, panel_D, panel_E, panel_F, panel_G, panel_H]
exec(_sec("# ---------------- captions"))
def cap_text(s): return (s.replace("localhost three thousand", "localhost:3000").replace("localhost four thousand", "localhost:4000")
                         .replace("Access Control Allow Origin", "Access-Control-Allow-Origin").replace("enable cors", "enableCors()").replace("logged in", "logged-in"))
CAPTIONS = [c for i in range(len(VO)) for c in chunks_for(i)]
def wcol(w):
    lw = w.lower().strip(".,?!")
    if lw == "cors" or lw.startswith("access-control"): return PINK
    if lw.startswith("localhost") or lw.startswith("enablecors") or lw in ("origin", "origins", "protocol", "domain", "port"): return YEL
    if lw in ("blocked", "star"): return RED
    return WHITE
_frame0 = frame
_WM = Image.open("/home/claude/nltech-videos/engine/assets/watermark_nltech.png").convert("RGBA")
def frame(t):
    im = _frame0(t).convert("RGBA"); im.alpha_composite(_WM, ((W - _WM.width) // 2, 92)); return im.convert("RGB")
