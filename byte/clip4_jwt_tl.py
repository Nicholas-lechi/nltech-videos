"""JWT vs Sessions explainer with Byte. Reuses helpers/character from clip3."""
import re, json, math
_SRC = open("/tmp/claude-0/-home-claude/e7805bda-0e11-5016-9991-51d072e57e6b/scratchpad/clip3/tl.py").read()
def _sec(a, b=None):
    i = _SRC.index(a); j = _SRC.index(b) if b else len(_SRC)
    return _SRC[i:j]
exec(_SRC[:_SRC.index("# ---------------- timeline")])
HERE = SP + "clip4/"

# ---------------- timeline ----------------
VO = json.load(open(HERE + "vo.json"))
vo_start = {}
def place(i, t):
    vo_start[i] = t; return t + VO[i]["dur"]
def vend(i): return vo_start[i] + VO[i]["dur"]
def frac(i, f): return vo_start[i] + VO[i]["dur"] * f

TR = 0.55
SC = [0.0]
e = place(0, 0.3)
SC.append(e + 0.45)
e = place(1, SC[1] + TR); e = place(2, e + 0.35); e = place(3, e + 0.3)
B1, SWAP_B = vo_start[1], vo_start[2]
SC.append(e + 0.45)
e = place(4, SC[2] + TR); e = place(5, e + 0.35); e = place(6, e + 0.3)
C1, SWAP_C = vo_start[4], vo_start[5]
SC.append(e + 0.45)
e = place(7, SC[3] + TR)
SC.append(e + 0.45)
e = place(8, SC[4] + TR)
SC.append(e + 0.45)
e = place(9, SC[5] + TR)
DURATION = round((e + 1.6) * FPS) / FPS
NS = len(SC)
def scene_at(t):
    i = 0
    for k in range(NS):
        if t >= SC[k]: i = k
    return i

# animation beats
B_RIGHT = frac(1, 0.55)
L_LOGIN = vo_start[2] + 0.3
L_DB = frac(2, 0.38)
L_COOKIE = frac(2, 0.72)
R_SEND = vo_start[3] + 0.1
R_LOOK = R_SEND + 1.2
R_BACK = R_LOOK + 1.0
C_CHECK = frac(4, 0.72)
T_TOKEN = frac(5, 0.15)
T_PAY = frac(5, 0.45)
T_SIGN = frac(5, 0.7)
J_SEND = vo_start[6] + 0.1
J_VER = frac(6, 0.42)
J_NODB = frac(6, 0.7)
D1, D2 = frac(7, 0.25), frac(7, 0.62)
E1, E2 = frac(8, 0.12), frac(8, 0.55)

EVENTS = {
    "whoosh": SC[1:] + [SWAP_B, SWAP_C],
    "pop": [B1, B_RIGHT, L_DB, T_TOKEN, T_PAY, J_NODB, D1, D2, E1, E2, vo_start[1] - 0.2, vo_start[4] - 0.2],
    "ding": [R_BACK + 0.6, C_CHECK, T_SIGN, J_VER],
    "swish": [L_LOGIN, L_COOKIE, R_SEND, R_BACK, J_SEND],
    "buzz": [],
}

exec(_sec("# ---------------- voice amplitude", "# ---------------- character poses"))

# ---------------- poses ----------------
POSES = {
    "idle":   (0.28, 0.15, 0.28, 0.15, 0, 0, None),
    "wave":   (0.28, 0.15, 2.55, 0.35, 0, 1, None),
    "point":  (0.30, 0.15, 2.35, -0.25, 0, 0, None),
    "ticket": (1.25, -1.15, 2.35, -0.25, 0, 0, "ticket"),
    "band":   (1.25, -1.15, 2.35, -0.25, 0, 0, "band"),
    "both":   (2.55, 0.35, 2.55, 0.35, 1, 1, None),
    "shrug":  (1.05, 1.2, 1.05, 1.2, 0, 0, None),
}
KEYS = [(0.0, "wave"), (vend(0), "idle"),
        (vo_start[1] - 0.15, "ticket"), (SWAP_B, "point"), (vend(3), "idle"),
        (vo_start[4] - 0.15, "band"), (SWAP_C, "point"), (vend(6), "idle"),
        (vo_start[7] - 0.15, "shrug"), (D1 - 0.2, "point"), (vend(7), "idle"),
        (vo_start[8] - 0.15, "point"), (vend(8), "idle"),
        (vo_start[9] - 0.15, "both")]
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

def draw_prop(pd, prop, hx, hy):
    if prop == "ticket":
        x0, y0 = hx - 130, hy - 200
        pd.rounded_rectangle((x0, y0, x0 + 260, y0 + 160), radius=16, fill=(250, 236, 200), outline=INK, width=10)
        for cy in (y0 + 80,):
            pd.ellipse((x0 - 22, cy - 22, x0 + 22, cy + 22), fill=(0, 0, 0, 0), outline=INK, width=0)
        pd.line((x0 + 70, y0 + 20, x0 + 70, y0 + 140), fill=(200, 170, 120), width=6)
        pd.text((x0 + 165, y0 + 84), "#42", font=font(F_BLACK, 62), fill=INK, anchor="mm")
    else:
        x0, y0 = hx - 150, hy - 190
        pd.rounded_rectangle((x0, y0, x0 + 300, y0 + 110), radius=40, fill=AZ, outline=INK, width=10)
        pd.ellipse((x0 + 200, y0 + 12, x0 + 286, y0 + 98), fill=(255, 220, 90), outline=INK, width=8)
        pd.line((x0 + 222, y0 + 56, x0 + 238, y0 + 74, x0 + 266, y0 + 38), fill=INK, width=10)
        pd.text((x0 + 105, y0 + 56), "ADA", font=font(F_BLACK, 50), fill=INK, anchor="mm")

_char = _sec("# ---------------- character drawing", "# ---------------- panels")
_char = re.sub(r'        if prop == "id":.*?(?=        d2_alpha)', "        draw_prop(pd, prop, hx, hy)\n", _char, flags=re.S)
exec(_char)
exec(_sec("# ---------------- panels", "# ---------------- captions"))

# ---------------- generic bits ----------------
def head(d, label, col, q, t, t0, size=88):
    a = appear(t, t0)
    if a <= 0: return
    pill(d, label, 540, (1 - a) * 16, col, tuple(int(c * 0.22) for c in col), a=int(255 * a))
    ctext(d, q, 540, 150 + (1 - a) * 20, font(F_BLACK, size), WHITE, a=int(255 * a))

def lerp(a, b, p): return a + (b - a) * p

def packet(c, x0, x1, y, t, t0, dur, text, col, fsize=30):
    p = (t - t0) / dur
    if p < 0 or p > 1.15: return
    q = ease_io(min(1, p)); x = lerp(x0, x1, q)
    a = 1.0 if p <= 1 else max(0, 1 - (p - 1) / 0.15)
    f = font(F_MONOB, fsize); tw = f.getlength(text)
    A = int(255 * a)
    c.rounded_rectangle((x - tw / 2 - 18, y - 26, x + tw / 2 + 18, y + 26), radius=26, fill=tuple(int(v * 0.25) for v in col) + (A,), outline=col + (A,), width=3)
    c.text((x, y), text, font=f, fill=col + (A,), anchor="mm")

def box(c, x0, y0, x1, y1, title, col=EDGE, a=255, tcol=WHITE):
    c.rounded_rectangle((x0, y0, x1, y1), radius=20, fill=(10, 14, 22, a), outline=col + (a,), width=3)
    c.text(((x0 + x1) / 2, y0 + 40), title, font=font(F_BLACK, 38), fill=tcol + (a,), anchor="mm")

def db(c, x0, y0, x1, y1, a=255, col=(120, 132, 150)):
    A = a
    c.rectangle((x0, y0 + 20, x1, y1 - 20), fill=(24, 30, 42, A))
    c.ellipse((x0, y1 - 40, x1, y1), fill=(24, 30, 42, A), outline=col + (A,), width=3)
    c.rectangle((x0 + 2, y0 + 20, x1 - 2, y1 - 22), fill=(24, 30, 42, A))
    c.line((x0, y0 + 20, x0, y1 - 20), fill=col + (A,), width=3)
    c.line((x1, y0 + 20, x1, y1 - 20), fill=col + (A,), width=3)
    c.ellipse((x0, y0, x1, y0 + 40), fill=(34, 42, 58, A), outline=col + (A,), width=3)

def arrow(c, x0, x1, y, col=DIM, a=255, both=False):
    c.line((x0, y, x1, y), fill=col + (a,), width=5)
    c.polygon([(x1, y), (x1 - 18, y - 12), (x1 - 18, y + 12)], fill=col + (a,))
    if both: c.polygon([(x0, y), (x0 + 18, y - 12), (x0 + 18, y + 12)], fill=col + (a,))

# ---------------- panels ----------------
def panel_A(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    for (txt, f, col, y, t0) in [("JWT", font(F_BLACK, 160), AZ, 170, 0.25),
                                  ("vs", font(F_BOLD, 64), GREY, 310, 0.7),
                                  ("Sessions", font(F_BLACK, 140), AN, 440, 1.05)]:
        a = appear(t, t0)
        if a > 0: ctext(d, txt, 540, y + (1 - a) * 30, f, col, a=int(255 * a))
    a = appear(t, frac(0, 0.3))
    if a > 0: pill(d, "How apps keep you logged in", 540, 570 + (1 - a) * 14, WHITE, (44, 50, 64), size=38, a=int(255 * a))
    return L

def panel_B(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    head(d, "SESSIONS", AN, "The server remembers", t, SC[1] + 0.3)
    x1, x2 = slide_x(t, SWAP_B)
    a = appear(t, B1)
    if a > 0 and x1 > -W + 1:
        C = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); c = ImageDraw.Draw(C)
        oy = (1 - a) * 40
        card_box(c, 70, 240 + oy, 1010, 730 + oy, "REAL LIFE  ·  COAT CHECK")
        # rack + coat
        c.line((140, 330 + oy, 480, 330 + oy), fill=(150, 160, 176), width=10)
        for k, (cx, colr) in enumerate([(220, (90, 110, 150)), (390, (150, 80, 70))]):
            c.line((cx, 330 + oy, cx, 360 + oy), fill=(150, 160, 176), width=6)
            c.polygon([(cx - 60, 370 + oy), (cx + 60, 370 + oy), (cx + 85, 600 + oy), (cx - 85, 600 + oy)], fill=colr)
            c.polygon([(cx - 20, 370 + oy), (cx + 20, 370 + oy), (cx, 430 + oy)], fill=(30, 36, 48))
        c.rounded_rectangle((350, 470 + oy, 430, 520 + oy), radius=8, fill=(250, 236, 200))
        c.text((390, 495 + oy), "#42", font=font(F_BLACK, 28), fill=INK, anchor="mm")
        c.text((310, 660 + oy), "Server keeps your data", font=font(F_BOLD, 32), fill=GREY, anchor="mm")
        b = appear(t, B_RIGHT, 0.3)
        if b > 0:
            A = int(255 * b)
            c.rounded_rectangle((620, 380 + oy, 920, 540 + oy), radius=18, fill=(250, 236, 200, A), outline=(200, 170, 120, A), width=4)
            c.text((770, 460 + oy), "#42", font=font(F_BLACK, 84), fill=INK + (A,), anchor="mm")
            c.text((770, 610 + oy), "You hold", font=font(F_BLACK, 40), fill=WHITE + (A,), anchor="mm")
            c.text((770, 660 + oy), "just a ticket", font=font(F_BLACK, 40), fill=WHITE + (A,), anchor="mm")
        L.alpha_composite(C, (int(x1), 0))
    if t >= SWAP_B:
        C = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); c = ImageDraw.Draw(C)
        card_box(c, 70, 240, 1010, 730, "IN AN APP  ·  SESSION + COOKIE")
        box(c, 110, 300, 400, 440, "Browser")
        box(c, 680, 300, 970, 440, "Server")
        arrow(c, 420, 660, 370, both=True)
        # DB
        db(c, 700, 480, 950, 700)
        c.text((825, 530), "SESSIONS", font=font(F_BOLD, 22), fill=GREY, anchor="mm")
        r = appear(t, L_DB, 0.3)
        if r > 0:
            hl = 0.0
            if t > R_LOOK: hl = max(0, 1 - abs((t - R_LOOK - 0.5) / 0.5))
            A = int(255 * r)
            c.rounded_rectangle((718, 565, 932, 640), radius=12, fill=tuple(int(v * (0.25 + 0.5 * hl)) for v in AN) + (A,), outline=AN + (A,), width=3)
            c.text((825, 590), "a8f3", font=font(F_MONOB, 28), fill=WHITE + (A,), anchor="mm")
            c.text((825, 620), "Ada · user", font=font(F_BOLD, 22), fill=GREY + (A,), anchor="mm")
            if hl > 0:
                c.text((825, 680), "lookup…", font=font(F_BOLD, 26), fill=YEL + (int(255 * hl),), anchor="mm")
        # cookie on browser
        ck = appear(t, L_COOKIE + 0.9, 0.25)
        if ck > 0:
            A = int(255 * ck)
            c.ellipse((130, 520, 210, 600), fill=(196, 140, 80, A), outline=INK + (A,), width=4)
            for (dx, dy) in ((150, 545), (180, 565), (160, 580), (190, 540)):
                c.ellipse((dx - 6, dy - 6, dx + 6, dy + 6), fill=(80, 50, 30, A))
            c.text((230, 560), "sid=a8f3", font=font(F_MONOB, 34), fill=YEL + (A,), anchor="lm")
            c.text((130, 640), "cookie holds only the ID", font=font(F_BOLD, 26), fill=GREY + (A,))
        packet(c, 260, 820, 370, t, L_LOGIN, 0.9, "login", AN)
        packet(c, 820, 260, 370, t, L_COOKIE, 0.9, "sid=a8f3", YEL, 28)
        packet(c, 260, 820, 370, t, R_SEND, 1.0, "sid=a8f3", YEL, 28)
        packet(c, 820, 260, 370, t, R_BACK, 0.9, "Hi Ada", GREEN)
        ok = appear(t, R_BACK + 0.9, 0.25)
        if ok > 0: icon_check(c, 255, 400, 24, a=int(255 * ok))
        L.alpha_composite(C, (int(x2), 0))
    return L

PCOL = [(255, 110, 130), (190, 140, 255), (90, 210, 230)]

def panel_C(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    head(d, "JWT", AZ, "You carry the proof", t, SC[2] + 0.3)
    x1, x2 = slide_x(t, SWAP_C)
    a = appear(t, C1)
    if a > 0 and x1 > -W + 1:
        C = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); c = ImageDraw.Draw(C)
        oy = (1 - a) * 40
        card_box(c, 70, 240 + oy, 1010, 730 + oy, "REAL LIFE  ·  SIGNED WRISTBAND")
        # wristband
        c.rounded_rectangle((120, 380 + oy, 560, 530 + oy), radius=60, fill=AZ, outline=(120, 70, 20), width=5)
        c.text((280, 432 + oy), "ADA", font=font(F_BLACK, 52), fill=INK, anchor="mm")
        c.text((280, 482 + oy), "VIP · ALL AREAS", font=font(F_BOLD, 26), fill=(60, 30, 10), anchor="mm")
        c.ellipse((420, 395 + oy, 540, 515 + oy), fill=(255, 220, 90), outline=(120, 70, 20), width=5)
        c.text((480, 455 + oy), "SIGNED", font=font(F_BLACK, 22), fill=(120, 70, 20), anchor="mm")
        c.text((340, 620 + oy), "Info is written on it", font=font(F_BOLD, 32), fill=GREY, anchor="mm")
        b = appear(t, C_CHECK, 0.3)
        if b > 0:
            A = int(255 * b)
            c.text((800, 420 + oy), "Guard checks", font=font(F_BLACK, 40), fill=WHITE + (A,), anchor="mm")
            c.text((800, 470 + oy), "it's real", font=font(F_BLACK, 40), fill=WHITE + (A,), anchor="mm")
            icon_check(c, 800, 560 + oy, 40 * (0.6 + 0.4 * b), a=A)
        L.alpha_composite(C, (int(x1), 0))
    if t >= SWAP_C:
        C = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); c = ImageDraw.Draw(C)
        card_box(c, 70, 240, 1010, 730, "IN AN APP  ·  JSON WEB TOKEN")
        parts = ["eyJhbGci", "eyJpZCI6", "SflKxwRJ"]
        labels = ["HEADER", "PAYLOAD", "SIGNATURE"]
        f = font(F_MONOB, 40); cw = f.getlength("M")
        full = ".".join(parts); nshow = int(clamp((t - T_TOKEN) / 1.0) * len(full))
        x = 540 - cw * len(full) / 2; y = 300
        ci = 0
        for pi, p in enumerate(parts):
            for ch in p:
                if ci < nshow: c.text((x, y), ch, font=f, fill=PCOL[pi])
                x += cw; ci += 1
            if pi < 2:
                if ci < nshow: c.text((x, y), ".", font=f, fill=WHITE)
                x += cw; ci += 1
        la = appear(t, T_TOKEN + 1.0, 0.3)
        if la > 0:
            x = 540 - cw * len(full) / 2
            for pi, p in enumerate(parts):
                c.text((x + cw * len(p) / 2, 368), labels[pi], font=font(F_BOLD, 22), fill=PCOL[pi] + (int(255 * la),), anchor="mm")
                x += cw * (len(p) + 1)
        pa = appear(t, T_PAY, 0.3)
        if pa > 0:
            A = int(255 * pa)
            c.rounded_rectangle((150, 405, 640, 485), radius=14, fill=(26, 20, 40, A), outline=PCOL[1] + (A,), width=3)
            c.text((395, 445), '{ "id": 7, "role": "user" }', font=font(F_MONOB, 28), fill=WHITE + (A,), anchor="mm")
        sa = appear(t, T_SIGN, 0.3)
        if sa > 0:
            A = int(255 * sa)
            c.rounded_rectangle((670, 405, 930, 485), radius=14, fill=(16, 36, 42, A), outline=PCOL[2] + (A,), width=3)
            c.text((800, 445), "signed by server", font=font(F_BOLD, 26), fill=PCOL[2] + (A,), anchor="mm")
        # request row
        ra = appear(t, J_SEND - 0.3, 0.3)
        if ra > 0:
            A = int(255 * ra)
            box(c, 110, 530, 360, 680, "You", a=A)
            box(c, 640, 530, 970, 680, "Server", a=A)
            arrow(c, 380, 620, 605, a=A)
        packet(c, 235, 805, 605, t, J_SEND, 1.0, "token", AZ)
        va = appear(t, J_VER, 0.3)
        if va > 0:
            A = int(255 * va)
            icon_check(c, 690, 635, 20, a=A)
            c.text((720, 635), "signature OK", font=font(F_BOLD, 28), fill=GREEN + (A,), anchor="lm")
        na = appear(t, J_NODB, 0.3)
        if na > 0:
            A = int(255 * na)
            c.text((805, 708), "no database lookup", font=font(F_BOLD, 26), fill=YEL + (A,), anchor="mm")
        L.alpha_composite(C, (int(x2), 0))
    return L

def tradeoff(d, X, y, name, col, rows, A):
    d.rounded_rectangle((X + 6, y + 14, X + 946, y + 284), radius=30, fill=(0, 0, 0, int(A * 0.45)))
    d.rounded_rectangle((X, y, X + 940, y + 270), radius=30, fill=CARD + (A,), outline=col + (A,), width=4)
    d.text((X + 44, y + 30), name, font=font(F_BLACK, 62), fill=col + (A,))
    for k, (ok, txt) in enumerate(rows):
        yy = y + 145 + k * 70
        (icon_check if ok else icon_cross)(d, X + 70, yy, 24, a=A)
        d.text((X + 115, yy), txt, font=font(F_BOLD, 40), fill=(WHITE if ok else GREY) + (A,), anchor="lm")

def panel_D(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a = appear(t, SC[3] + 0.3)
    pill(d, "WHICH IS BETTER?", 540, (1 - a) * 16, YEL, (60, 50, 14), a=int(255 * a))
    for (name, col, rows, t0, y) in [("Sessions", AN, [(True, "Easy to log out / revoke"), (False, "Server must store them")], D1, 100),
                                      ("JWT", AZ, [(True, "Scales across many servers"), (False, "Hard to revoke early")], D2, 420)]:
        p = appear(t, t0, 0.4)
        if p > 0: tradeoff(d, 70 + (1 - p) * 300, y, name, col, rows, int(255 * p))
    return L

def panel_E(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a = appear(t, SC[4] + 0.3)
    pill(d, "SIMPLE RULE", 540, (1 - a) * 16, YEL, (60, 50, 14), a=int(255 * a))
    for (q, ans, col, t0, y) in [("Classic web app", "Sessions", AN, E1, 110),
                                  ("APIs · mobile · microservices", "JWT", AZ, E2, 420)]:
        p = appear(t, t0, 0.4)
        if p <= 0: continue
        X = 70 + (1 - p) * 300; A = int(255 * p)
        d.rounded_rectangle((X + 6, y + 14, X + 946, y + 254), radius=30, fill=(0, 0, 0, int(A * 0.45)))
        d.rounded_rectangle((X, y, X + 940, y + 240), radius=30, fill=CARD + (A,), outline=col + (A,), width=4)
        d.text((X + 470, y + 70), q, font=font(F_BOLD, 44), fill=GREY + (A,), anchor="mm")
        d.line((X + 470, y + 110, X + 470, y + 140), fill=DIM + (A,), width=6)
        d.polygon([(X + 455, y + 135), (X + 485, y + 135), (X + 470, y + 152)], fill=DIM + (A,))
        d.text((X + 470, y + 190), ans, font=font(F_BLACK, 76), fill=col + (A,), anchor="mm")
    return L

def panel_F(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a = appear(t, SC[5] + 0.35)
    ctext(d, "Follow for more", 540, 230 + (1 - a) * 24, font(F_BLACK, 104), YEL, a=int(255 * a))
    a = appear(t, SC[5] + 0.9)
    ctext(d, "Dev concepts, explained simply", 540, 370 + (1 - a) * 20, font(F_BOLD, 52), WHITE, a=int(255 * a))
    a = appear(t, SC[5] + 1.5)
    if a > 0: pill(d, "Next: Hashing vs Encryption", 540, 470 + (1 - a) * 14, WHITE, (44, 50, 64), size=36, a=int(255 * a))
    return L

PANELS = [panel_A, panel_B, panel_C, panel_D, panel_E, panel_F]

exec(_sec("# ---------------- captions"))

def wcol(w):
    lw = w.lower().strip(".,?!")
    if lw.startswith("jwt"): return AZ
    if lw.startswith("session"): return AN
    if lw in ("cookie", "token", "signature", "ticket", "wristband", "id", "revoke", "scale"): return YEL
    return WHITE
