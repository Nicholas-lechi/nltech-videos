"""Cookies vs localStorage vs sessionStorage with Byte, charcoal background."""
import re, json, math
SP = "/tmp/claude-0/-home-claude/e7805bda-0e11-5016-9991-51d072e57e6b/scratchpad/"
_SRC = open(SP + "clip3/tl.py").read()
_S4 = open(SP + "clip4/tl.py").read()
def _sec(a, b=None):
    i = _SRC.index(a); j = _SRC.index(b) if b else len(_SRC)
    return _SRC[i:j]
exec(_SRC[:_SRC.index("# ---------------- timeline")])
HERE = SP + "clip8/"
C_PUN, C_ID, C_STR = (201, 209, 217), (230, 237, 243), (165, 214, 255)

_cbg = None
def bg():
    global _cbg
    if _cbg is None:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        img = np.zeros((H, W, 3), np.float32) + np.array([18, 18, 21], np.float32)
        img += np.exp(-(((x - 540) / 700) ** 2 + ((y - 250) / 650) ** 2))[..., None] * np.array([34, 32, 30], np.float32)
        img += np.exp(-(((x - 540) / 600) ** 2 + ((y - 1650) / 380) ** 2))[..., None] * np.array([10, 40, 34], np.float32)
        img[((x % 54) < 3) & ((y % 54) < 3)] += 10
        _cbg = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
    return _cbg.copy()

VO = json.load(open(HERE + "vo.json"))
vo_start = {}
def place(i, t):
    vo_start[i] = t; return t + VO[i]["dur"]
def vend(i): return vo_start[i] + VO[i]["dur"]
def frac(i, f): return vo_start[i] + VO[i]["dur"] * f
TR = 0.55
SC = [0.0]
e = place(0, 0.3); SC.append(e + 0.45)
e = place(1, SC[1] + TR); e = place(2, e + 0.35); SWAP_B = vo_start[2]; SC.append(e + 0.45)
e = place(3, SC[2] + TR); SC.append(e + 0.45)
e = place(4, SC[3] + TR); e = place(5, e + 0.35); SWAP_D = vo_start[5]; SC.append(e + 0.45)
e = place(6, SC[4] + TR); SC.append(e + 0.45)
e = place(7, SC[5] + TR); SC.append(e + 0.45)
e = place(8, SC[6] + TR)
DURATION = round((e + 1.6) * FPS) / FPS
NS = len(SC)
def scene_at(t):
    i = 0
    for k in range(NS):
        if t >= SC[k]: i = k
    return i
LS = AN; SS = (190, 140, 255); CK = (230, 160, 80)
B_KEEP = frac(1, 0.55); B_CLOSE = frac(1, 0.65)
L_ROWS = [vo_start[2] + 0.3, frac(2, 0.55), frac(2, 0.7), frac(2, 0.85)]
S_STEP = [vo_start[3] + 0.4, vo_start[3] + 1.2, vo_start[3] + 2.0]; S_CLOSE = frac(3, 0.5); S_EMPTY = frac(3, 0.62)
K_REQ = frac(4, 0.4); K_SRV = frac(4, 0.62); K_TINY = frac(4, 0.82)
H_JS = frac(5, 0.45); H_OK = frac(5, 0.7)
M1, M2, M3 = frac(6, 0.05), frac(6, 0.4), frac(6, 0.65)
P1, P2 = frac(7, 0.15), frac(7, 0.55)
EVENTS = {"whoosh": [], "swish": [], "pop": [vo_start[1], B_KEEP] + L_ROWS[1:] + S_STEP + [K_REQ, K_SRV, M1, M2, M3, P1, P2],
          "ding": [B_CLOSE + 0.6, H_OK], "buzz": [S_EMPTY, H_JS]}

exec(_sec("# ---------------- voice amplitude", "# ---------------- character poses"))
POSES = {
    "idle":   (0.28, 0.15, 0.28, 0.15, 0, 0, None),
    "wave":   (0.28, 0.15, 2.55, 0.35, 0, 1, None),
    "point":  (0.30, 0.15, 2.35, -0.25, 0, 0, None),
    "box":    (1.25, -1.15, 2.35, -0.25, 0, 0, "box"),
    "cookie": (1.25, -1.15, 2.35, -0.25, 0, 0, "cookie"),
    "both":   (2.55, 0.35, 2.55, 0.35, 1, 1, None),
    "shrug":  (1.05, 1.2, 1.05, 1.2, 0, 0, None),
}
KEYS = [(0.0, "wave"), (vend(0), "idle"), (vo_start[1] - 0.15, "box"), (SWAP_B, "point"), (vend(2), "idle"),
        (vo_start[3] - 0.15, "point"), (vend(3), "idle"),
        (vo_start[4] - 0.15, "cookie"), (SWAP_D, "point"), (vend(5), "idle"),
        (vo_start[6] - 0.15, "point"), (vend(6), "idle"),
        (vo_start[7] - 0.15, "shrug"), (P1 - 0.1, "point"), (vend(7), "idle"), (vo_start[8] - 0.15, "both")]
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
def cookie_shape(pd, cx, cy, r, a=255):
    pd.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(196, 140, 80, a), outline=INK + (a,), width=max(3, int(r / 9)))
    for (dx, dy) in ((-0.4, -0.3), (0.3, -0.4), (0.1, 0.2), (-0.3, 0.4), (0.45, 0.25)):
        q = r * 0.14; pd.ellipse((cx + dx * r - q, cy + dy * r - q, cx + dx * r + q, cy + dy * r + q), fill=(80, 50, 30, a))
def draw_prop(pd, prop, hx, hy):
    if prop == "box":
        pd.rounded_rectangle((hx - 130, hy - 230, hx + 130, hy - 40), radius=18, fill=LS, outline=INK, width=10)
        pd.rounded_rectangle((hx - 50, hy - 150, hx + 50, hy - 120), radius=10, fill=(240, 244, 250))
    else:
        cookie_shape(pd, hx, hy - 120, 100)
_char = _sec("# ---------------- character drawing", "# ---------------- panels")
_char = re.sub(r'        if prop == "id":.*?(?=        d2_alpha)', "        draw_prop(pd, prop, hx, hy)\n", _char, flags=re.S)
exec(_char)
exec(_sec("# ---------------- panels", "# ---------------- captions"))
exec(_S4[_S4.index("# ---------------- generic bits"):_S4.index("def panel_A")])
exec(_S4[_S4.index("def tradeoff"):_S4.index("def panel_D")])

def panel_A(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    for (txt, f, col, y) in [("Cookies", font(F_BLACK, 120), CK, 130), ("localStorage", font(F_BLACK, 104), LS, 270), ("sessionStorage", font(F_BLACK, 96), SS, 400)]:
        ctext(d, txt, 540, y, f, col)
    pill(d, "Which one should you use?", 540, 520, WHITE, (50, 50, 56), size=38)
    return L

def panel_B(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    head(d, "LOCALSTORAGE", LS, "Stays until you remove it", t, SC[1] + 0.3, size=74)
    x1, x2 = slide_x(t, SWAP_B)
    a = appear(t, vo_start[1])
    if a > 0 and x1 > -W + 1:
        C = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); c = ImageDraw.Draw(C); oy = (1 - a) * 40
        card_box(c, 70, 240 + oy, 1010, 730 + oy, "REAL LIFE  ·  A DRAWER AT HOME")
        c.rounded_rectangle((130, 330 + oy, 470, 620 + oy), radius=18, fill=(60, 66, 80), outline=EDGE, width=3)
        c.rounded_rectangle((150, 350 + oy, 450, 470 + oy), radius=12, fill=LS)
        c.rounded_rectangle((260, 400 + oy, 340, 420 + oy), radius=8, fill=(240, 244, 250))
        c.text((300, 545 + oy), "theme: dark", font=font(F_MONOB, 30), fill=WHITE, anchor="mm")
        k1 = appear(t, B_KEEP, 0.3)
        if k1 > 0:
            A = int(255 * k1)
            c.text((760, 400 + oy), "Close the", font=font(F_BLACK, 40), fill=WHITE + (A,), anchor="mm")
            c.text((760, 450 + oy), "browser…", font=font(F_BLACK, 40), fill=WHITE + (A,), anchor="mm")
        k2 = appear(t, B_CLOSE + 0.6, 0.3)
        if k2 > 0:
            A = int(255 * k2)
            icon_check(c, 760, 540 + oy, 30, a=A)
            c.text((760, 610 + oy), "still there", font=font(F_BOLD, 34), fill=GREEN + (A,), anchor="mm")
        L.alpha_composite(C, (int(x1), 0))
    if t >= SWAP_B:
        C = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); c = ImageDraw.Draw(C)
        card_box(c, 70, 240, 1010, 730, "IN CODE")
        p = appear(t, L_ROWS[0], 0.3)
        if p > 0:
            A = int(255 * p); f = font(F_MONOB, 30)
            c.text((120, 320), "localStorage.setItem('theme', 'dark');", font=f, fill=C_ID + (A,))
            c.text((120, 370), "localStorage.getItem('theme'); // 'dark'", font=f, fill=C_STR + (A,))
        for k, (txt, ok, t0) in enumerate([("About 5 MB per site", True, L_ROWS[1]), ("Only your site's JavaScript reads it", True, L_ROWS[2]), ("Themes, drafts, settings", True, L_ROWS[3])]):
            q = appear(t, t0, 0.3)
            if q <= 0: continue
            A = int(255 * q); y = 470 + k * 75
            icon_check(c, 140, y, 22, a=A); c.text((180, y), txt, font=font(F_BOLD, 36), fill=WHITE + (A,), anchor="lm")
        L.alpha_composite(C, (int(x2), 0))
    return L

def panel_C(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    head(d, "SESSIONSTORAGE", SS, "Gone when the tab closes", t, SC[2] + 0.3, size=74)
    C = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); c = ImageDraw.Draw(C)
    card_box(c, 70, 240, 1010, 730, "EXAMPLE  ·  A 3-STEP SIGN-UP FORM")
    closed = appear(t, S_CLOSE, 0.3)
    tab_a = int(255 * (1 - closed * 0.7))
    c.rounded_rectangle((120, 380, 960, 600), radius=18, fill=(10, 14, 22, tab_a), outline=SS + (tab_a,), width=3)
    c.rounded_rectangle((120, 340, 380, 385), radius=12, fill=SS + (tab_a,))
    c.text((250, 362), "signup tab", font=font(F_BOLD, 26), fill=INK + (tab_a,), anchor="mm")
    for k, (lab, t0) in enumerate(zip(["Step 1: name", "Step 2: email", "Step 3: plan"], S_STEP)):
        q = appear(t, t0, 0.3) * (1 - appear(t, S_EMPTY, 0.3))
        if q > 0:
            A = int(255 * q * (1 - closed * 0.5)); y = 435 + k * 55
            icon_check(c, 170, y, 18, a=A); c.text((205, y), lab, font=font(F_BOLD, 34), fill=WHITE + (A,), anchor="lm")
    if closed > 0:
        A = int(255 * closed)
        c.line((850, 410, 910, 470), fill=RED + (A,), width=10); c.line((850, 470, 910, 410), fill=RED + (A,), width=10)
        c.text((880, 510), "tab closed", font=font(F_BOLD, 26), fill=RED + (A,), anchor="mm")
    e1 = appear(t, S_EMPTY, 0.3)
    if e1 > 0:
        c.text((540, 665), "Saved steps are cleared", font=font(F_BLACK, 44), fill=SS + (int(255 * e1),), anchor="mm")
    L.alpha_composite(C)
    return L

def panel_D(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    head(d, "COOKIES", CK, "Sent with every request", t, SC[3] + 0.3, size=78)
    x1, x2 = slide_x(t, SWAP_D)
    a = appear(t, vo_start[4])
    if a > 0 and x1 > -W + 1:
        C = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); c = ImageDraw.Draw(C); oy = (1 - a) * 40
        card_box(c, 70, 240 + oy, 1010, 730 + oy, "HOW IT WORKS")
        box(c, 110, 320 + oy, 380, 460 + oy, "Browser")
        box(c, 700, 320 + oy, 970, 460 + oy, "Server")
        cookie_shape(c, 245, 540 + oy, 40)
        c.text((300, 540 + oy), "sid=a8f3", font=font(F_MONOB, 30), fill=YEL, anchor="lm")
        arrow(c, 400, 680, 390 + oy)
        rq = appear(t, K_REQ, 0.3)
        if rq > 0: c.text((540, 360 + oy), "Cookie: sid=a8f3", font=font(F_MONOB, 24), fill=CK + (int(255 * rq),), anchor="mm")
        sv = appear(t, K_SRV, 0.3)
        if sv > 0: icon_check(c, 835, 500 + oy, 26, a=int(255 * sv)); c.text((835, 555 + oy), "server reads it", font=font(F_BOLD, 28), fill=GREEN + (int(255 * sv),), anchor="mm")
        tn = appear(t, K_TINY, 0.3)
        if tn > 0: c.text((540, 670 + oy), "Tiny: about 4 KB each", font=font(F_BOLD, 34), fill=YEL + (int(255 * tn),), anchor="mm")
        L.alpha_composite(C, (int(x1), 0))
    if t >= SWAP_D:
        C = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); c = ImageDraw.Draw(C)
        card_box(c, 70, 240, 1010, 730, "LOGINS  ·  HttpOnly COOKIE")
        c.text((120, 320), "Set-Cookie: sid=a8f3; HttpOnly; Secure", font=font(F_MONOB, 30), fill=CK)
        p = appear(t, H_JS, 0.3)
        if p > 0:
            A = int(255 * p)
            c.text((120, 420), "document.cookie", font=font(F_MONOB, 32), fill=C_ID + (A,))
            c.text((120, 470), '// ""  (JavaScript can\'t see it)', font=font(F_MONOB, 28), fill=GREY + (A,))
            icon_cross(c, 900, 440, 26, a=A)
        q = appear(t, H_OK, 0.3)
        if q > 0:
            A = int(255 * q)
            icon_check(c, 140, 600, 26, a=A)
            c.text((185, 600), "Server still gets it on every request", font=font(F_BOLD, 34), fill=WHITE + (A,), anchor="lm")
        L.alpha_composite(C, (int(x2), 0))
    return L

def panel_E(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a = appear(t, SC[4] + 0.3)
    pill(d, "WHEN TO USE WHICH", 540, (1 - a) * 16, YEL, (60, 50, 14), a=int(255 * a))
    for k, (name, col, use, t0) in enumerate([("localStorage", LS, "Settings that should stay", M1), ("sessionStorage", SS, "Data for one tab only", M2), ("Cookies", CK, "Anything the server needs", M3)]):
        p = appear(t, t0, 0.4)
        if p <= 0: continue
        A = int(255 * p); y = 110 + k * 200; X = 70 + (1 - p) * 300
        d.rounded_rectangle((X, y, X + 940, y + 170), radius=28, fill=CARD + (A,), outline=col + (A,), width=4)
        d.text((X + 44, y + 55), name, font=font(F_BLACK, 52), fill=col + (A,), anchor="lm")
        d.text((X + 44, y + 120), use, font=font(F_BOLD, 38), fill=WHITE + (A,), anchor="lm")
    return L

def panel_F(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a = appear(t, SC[5] + 0.3)
    pill(d, "PRO TIP · SECURITY", 540, (1 - a) * 16, YEL, (60, 50, 14), a=int(255 * a))
    for k, (ok, txt, sub, t0) in enumerate([(False, "Tokens in localStorage", "any script on the page can read them", P1), (True, "HttpOnly cookies", "JavaScript can't touch them", P2)]):
        p = appear(t, t0, 0.35)
        if p <= 0: continue
        A = int(255 * p); y = 130 + k * 230; X = 70 + (1 - p) * 200; col = GREEN if ok else RED
        d.rounded_rectangle((X, y, X + 940, y + 190), radius=26, fill=CARD + (A,), outline=col + (A,), width=3)
        (icon_check if ok else icon_cross)(d, X + 80, y + 95, 38, a=A)
        d.text((X + 145, y + 70), txt, font=font(F_BLACK, 52), fill=WHITE + (A,), anchor="lm")
        d.text((X + 145, y + 135), sub, font=font(F_BOLD, 34), fill=GREY + (A,), anchor="lm")
    return L

def panel_G(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a = appear(t, SC[6] + 0.35); ctext(d, "Follow for more", 540, 230 + (1 - a) * 24, font(F_BLACK, 104), YEL, a=int(255 * a))
    a = appear(t, SC[6] + 0.9); ctext(d, "Dev concepts, explained simply", 540, 370 + (1 - a) * 20, font(F_BOLD, 52), WHITE, a=int(255 * a))
    a = appear(t, SC[6] + 1.5)
    if a > 0: pill(d, "Next: What happens when you type a URL", 540, 470 + (1 - a) * 14, WHITE, (50, 50, 56), size=34, a=int(255 * a))
    return L

PANELS = [panel_A, panel_B, panel_C, panel_D, panel_E, panel_F, panel_G]
exec(_sec("# ---------------- captions"))
def cap_text(s): return s.replace("local storage", "localStorage").replace("Local storage", "localStorage").replace("session storage", "sessionStorage").replace("Session storage", "sessionStorage").replace("multi step", "multi-step")
CAPTIONS = [c for i in range(len(VO)) for c in chunks_for(i)]
def wcol(w):
    lw = w.lower().strip(".,?!")
    if lw.startswith("localstorage"): return LS
    if lw.startswith("sessionstorage"): return SS
    if lw.startswith("cookie"): return CK
    if lw in ("httponly", "tokens", "passwords", "server"): return YEL
    return WHITE
_frame0 = frame
_WM = Image.open("/home/claude/nltech-videos/engine/assets/watermark_nltech.png").convert("RGBA")
def frame(t):
    im = _frame0(t).convert("RGBA"); im.alpha_composite(_WM, ((W - _WM.width) // 2, 92)); return im.convert("RGB")
