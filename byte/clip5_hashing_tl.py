"""Hashing vs Encryption explainer with Byte. Reuses clip3 character + clip4 helpers."""
import re, json, math
SP = "/tmp/claude-0/-home-claude/e7805bda-0e11-5016-9991-51d072e57e6b/scratchpad/"
_SRC = open(SP + "clip3/tl.py").read()
_S4 = open(SP + "clip4/tl.py").read()
def _sec(a, b=None, src=None):
    src = src or _SRC
    i = src.index(a); j = src.index(b) if b else len(src)
    return src[i:j]
exec(_SRC[:_SRC.index("# ---------------- timeline")])
HERE = SP + "clip5/"

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
e = place(3, SC[2] + TR); e = place(4, e + 0.35); SWAP_C = vo_start[4]; SC.append(e + 0.45)
e = place(5, SC[3] + TR); SC.append(e + 0.45)
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

# beats
B_LOCK = frac(1, 0.35); B_OPEN = frac(1, 0.78)
F_ENC = frac(2, 0.55); F_DEC = frac(2, 0.8)
C_BLEND = frac(3, 0.3); C_SMOOTH = frac(3, 0.5); C_NOBACK = frac(3, 0.72)
H1 = vo_start[4] + 0.3; H2 = frac(4, 0.62)
P_TYPE = vo_start[5] + 0.6; P_HASH = frac(5, 0.4); P_CMP = frac(5, 0.6); P_OK = frac(5, 0.72)
Q1, Q2 = frac(6, 0.05), frac(6, 0.5)
T1, T2, T3 = frac(7, 0.12), frac(7, 0.35), frac(7, 0.65)
EVENTS = {"whoosh": [], "swish": [],
          "pop": [vo_start[1], B_LOCK, vo_start[3], C_SMOOTH, H1, H2, P_HASH, Q1, Q2, T1, T2, T3],
          "ding": [B_OPEN, F_DEC, P_OK], "buzz": [C_NOBACK]}

exec(_sec("# ---------------- voice amplitude", "# ---------------- character poses"))

POSES = {
    "idle":   (0.28, 0.15, 0.28, 0.15, 0, 0, None),
    "wave":   (0.28, 0.15, 2.55, 0.35, 0, 1, None),
    "point":  (0.30, 0.15, 2.35, -0.25, 0, 0, None),
    "lock":   (1.25, -1.15, 2.35, -0.25, 0, 0, "lock"),
    "apple":  (1.25, -1.15, 2.35, -0.25, 0, 0, "apple"),
    "both":   (2.55, 0.35, 2.55, 0.35, 1, 1, None),
    "shrug":  (1.05, 1.2, 1.05, 1.2, 0, 0, None),
}
KEYS = [(0.0, "wave"), (vend(0), "idle"),
        (vo_start[1] - 0.15, "lock"), (SWAP_B, "point"), (vend(2), "idle"),
        (vo_start[3] - 0.15, "apple"), (SWAP_C, "point"), (vend(4), "idle"),
        (vo_start[5] - 0.15, "point"), (vend(5), "idle"),
        (vo_start[6] - 0.15, "point"), (vend(6), "idle"),
        (vo_start[7] - 0.15, "shrug"), (T1 - 0.2, "point"), (vend(7), "idle"),
        (vo_start[8] - 0.15, "both")]
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

def padlock(pd, cx, cy, s, col, ink, opened=0.0, a=255):
    # shackle
    lift = 28 * s * opened
    pd.arc((cx - 46 * s, cy - 110 * s - lift, cx + 46 * s, cy - 10 * s - lift), 180, 360, fill=ink + (a,), width=int(26 * s))
    pd.arc((cx - 46 * s, cy - 110 * s - lift, cx + 46 * s, cy - 10 * s - lift), 180, 360, fill=(200, 210, 222, a), width=int(12 * s))
    pd.line((cx - 46 * s, cy - 60 * s - lift, cx - 46 * s, cy - 20 * s - lift), fill=(200, 210, 222, a), width=int(12 * s))
    if opened < 0.5: pd.line((cx + 46 * s, cy - 60 * s - lift, cx + 46 * s, cy - 20 * s), fill=(200, 210, 222, a), width=int(12 * s))
    pd.rounded_rectangle((cx - 70 * s, cy - 30 * s, cx + 70 * s, cy + 80 * s), radius=int(18 * s), fill=col + (a,), outline=ink + (a,), width=int(8 * s))
    pd.ellipse((cx - 13 * s, cy + 2 * s, cx + 13 * s, cy + 28 * s), fill=ink + (a,))
    pd.rectangle((cx - 5 * s, cy + 20 * s, cx + 5 * s, cy + 52 * s), fill=ink + (a,))

def apple(pd, cx, cy, s, a=255):
    pd.ellipse((cx - 70 * s, cy - 60 * s, cx + 70 * s, cy + 70 * s), fill=(232, 72, 72, a), outline=INK + (a,), width=int(8 * s))
    pd.line((cx, cy - 60 * s, cx + 6 * s, cy - 95 * s), fill=(110, 70, 40, a), width=int(10 * s))
    pd.ellipse((cx + 8 * s, cy - 100 * s, cx + 52 * s, cy - 76 * s), fill=(80, 190, 90, a))

def draw_prop(pd, prop, hx, hy):
    if prop == "lock": padlock(pd, hx, hy - 120, 1.0, AZ, INK)
    else: apple(pd, hx, hy - 110, 1.0)

_char = _sec("# ---------------- character drawing", "# ---------------- panels")
_char = re.sub(r'        if prop == "id":.*?(?=        d2_alpha)', "        draw_prop(pd, prop, hx, hy)\n", _char, flags=re.S)
exec(_char)
exec(_sec("# ---------------- panels", "# ---------------- captions"))
exec(_S4[_S4.index("# ---------------- generic bits"):_S4.index("def panel_A")])
exec(_S4[_S4.index("def tradeoff"):_S4.index("def panel_D")])

ENC = AN; HSH = AZ

def panel_A(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    for (txt, f, col, y, t0) in [("Hashing", font(F_BLACK, 140), HSH, 170, 0.25),
                                  ("vs", font(F_BOLD, 64), GREY, 300, 0.7),
                                  ("Encryption", font(F_BLACK, 128), ENC, 430, 1.05)]:
        a = appear(t, t0)
        if a > 0: ctext(d, txt, 540, y + (1 - a) * 30, f, col, a=int(255 * a))
    a = appear(t, frac(0, 0.5))
    if a > 0: pill(d, "Same scramble, different jobs", 540, 570 + (1 - a) * 14, WHITE, (44, 50, 64), size=38, a=int(255 * a))
    return L

def panel_B(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    head(d, "ENCRYPTION", ENC, "A locked box", t, SC[1] + 0.3)
    x1, x2 = slide_x(t, SWAP_B)
    a = appear(t, vo_start[1])
    if a > 0 and x1 > -W + 1:
        C = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); c = ImageDraw.Draw(C)
        oy = (1 - a) * 40
        card_box(c, 70, 240 + oy, 1010, 730 + oy, "REAL LIFE  ·  LOCK & KEY")
        # message note
        c.rounded_rectangle((120, 380 + oy, 400, 560 + oy), radius=16, fill=(250, 236, 200))
        c.text((260, 440 + oy), "Meet me", font=font(F_BLACK, 38), fill=INK, anchor="mm")
        c.text((260, 490 + oy), "at 7pm", font=font(F_BLACK, 38), fill=INK, anchor="mm")
        arrow(c, 420, 520, 470 + oy)
        lk = appear(t, B_LOCK, 0.3); op = appear(t, B_OPEN, 0.4)
        if lk > 0:
            padlock(c, 640, 500 + oy, 1.1, ENC, INK, opened=op, a=int(255 * lk))
        if op > 0:
            A = int(255 * op)
            c.text((850, 440 + oy), "Right key", font=font(F_BLACK, 38), fill=WHITE + (A,), anchor="mm")
            c.text((850, 490 + oy), "opens it", font=font(F_BLACK, 38), fill=WHITE + (A,), anchor="mm")
            icon_check(c, 850, 570 + oy, 30, a=A)
        c.text((540, 680 + oy), "Two-way: lock it, then unlock it again", font=font(F_BOLD, 32), fill=GREY, anchor="mm")
        L.alpha_composite(C, (int(x1), 0))
    if t >= SWAP_B:
        C = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); c = ImageDraw.Draw(C)
        card_box(c, 70, 240, 1010, 730, "IN AN APP  ·  MESSAGES, CARDS, HTTPS")
        fm = font(F_MONOB, 34)
        rows = [("Hello Ada", WHITE, vo_start[2] + 0.2), ("x9#Lq2!vR7", YEL, F_ENC), ("Hello Ada", GREEN, F_DEC)]
        for k, (txt, col, t0) in enumerate(rows):
            p = appear(t, t0, 0.3)
            if p <= 0: continue
            A = int(255 * p); y = 320 + k * 140
            c.rounded_rectangle((300, y, 780, y + 92), radius=18, fill=(10, 14, 22, A), outline=col + (A,), width=3)
            c.text((540, y + 46), txt, font=fm, fill=col + (A,), anchor="mm")
            if k > 0:
                lab = "encrypt with key" if k == 1 else "decrypt with key"
                c.line((540, y - 44, 540, y - 6), fill=DIM + (A,), width=5)
                c.polygon([(526, y - 18), (554, y - 18), (540, y - 2)], fill=DIM + (A,))
                c.text((580, y - 25), lab, font=font(F_BOLD, 26), fill=ENC + (A,), anchor="lm")
        L.alpha_composite(C, (int(x2), 0))
    return L

def blender(c, cx, cy, s, fill_amt, a=255):
    A = a
    c.polygon([(cx - 80 * s, cy - 120 * s), (cx + 80 * s, cy - 120 * s), (cx + 60 * s, cy + 60 * s), (cx - 60 * s, cy + 60 * s)], fill=(200, 225, 240, int(A * 0.25)), outline=(200, 225, 240, A))
    if fill_amt > 0:
        top = cy + 60 * s - 170 * s * fill_amt
        c.polygon([(cx - 60 * s - 20 * s * fill_amt, top), (cx + 60 * s + 20 * s * fill_amt, top), (cx + 60 * s, cy + 58 * s), (cx - 60 * s, cy + 58 * s)], fill=(236, 110, 140, A))
    c.rounded_rectangle((cx - 90 * s, cy + 60 * s, cx + 90 * s, cy + 140 * s), radius=int(16 * s), fill=(60, 70, 90, A), outline=INK + (A,), width=4)
    c.ellipse((cx - 18 * s, cy + 84 * s, cx + 18 * s, cy + 120 * s), fill=(110, 255, 210, A))

def panel_C(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    head(d, "HASHING", HSH, "A blender", t, SC[2] + 0.3)
    x1, x2 = slide_x(t, SWAP_C)
    a = appear(t, vo_start[3])
    if a > 0 and x1 > -W + 1:
        C = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); c = ImageDraw.Draw(C)
        oy = (1 - a) * 40
        card_box(c, 70, 240 + oy, 1010, 730 + oy, "REAL LIFE  ·  FRUIT → SMOOTHIE")
        apple(c, 210, 470 + oy, 0.9)
        arrow(c, 300, 390, 470 + oy)
        bl = appear(t, C_BLEND, 0.3); sm = appear(t, C_SMOOTH, 0.8)
        if bl > 0:
            shake = 6 * math.sin(t * 40) if C_BLEND < t < C_SMOOTH + 0.6 else 0
            blender(c, 540 + shake, 450 + oy, 1.0, sm, a=int(255 * bl))
        if sm > 0.6:
            A = int(255 * min(1, (sm - 0.6) / 0.4))
            arrow(c, 660, 750, 470 + oy, a=A)
            c.rounded_rectangle((790, 380 + oy, 900, 570 + oy), radius=14, fill=(236, 110, 140, A), outline=INK + (A,), width=4)
        nb = appear(t, C_NOBACK, 0.3)
        if nb > 0:
            A = int(255 * nb)
            icon_cross(c, 540, 650 + oy, 26, a=A)
            c.text((580, 650 + oy), "Can't turn it back into fruit", font=font(F_BOLD, 32), fill=RED + (A,), anchor="lm")
        L.alpha_composite(C, (int(x1), 0))
    if t >= SWAP_C:
        C = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); c = ImageDraw.Draw(C)
        card_box(c, 70, 240, 1010, 730, "IN AN APP  ·  SHA-256")
        for k, (inp, out, t0, diff) in enumerate([("password123", "ef92b778bafe771e…", H1, False), ("password124", "33631376724e5d54…", H2, True)]):
            p = appear(t, t0, 0.35)
            if p <= 0: continue
            A = int(255 * p); y = 320 + k * 200
            f = font(F_MONOB, 34); fi = font(F_MONOB, 34)
            if diff:
                c.text((120, y + 30), "password12", font=fi, fill=WHITE + (A,), anchor="lm")
                c.text((120 + fi.getlength("password12"), y + 30), "4", font=fi, fill=YEL + (A,), anchor="lm")
            else:
                c.text((120, y + 30), inp, font=fi, fill=WHITE + (A,), anchor="lm")
            c.text((120, y + 90), "→  " + out, font=f, fill=(HSH if not diff else YEL) + (A,), anchor="lm")
            c.text((960, y + 30), "input", font=font(F_BOLD, 24), fill=GREY + (A,), anchor="rm")
            c.text((960, y + 90), "hash", font=font(F_BOLD, 24), fill=GREY + (A,), anchor="rm")
        p = appear(t, H2 + 1.0, 0.3)
        if p > 0:
            c.text((540, 690), "One character changed → totally different hash", font=font(F_BOLD, 30), fill=YEL + (int(255 * p),), anchor="mm")
        L.alpha_composite(C, (int(x2), 0))
    return L

def panel_D(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    head(d, "PASSWORDS", HSH, "Hash, then compare", t, SC[3] + 0.3, size=84)
    C = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); c = ImageDraw.Draw(C)
    a = appear(t, SC[3] + 0.4)
    card_box(c, 70, 240, 1010, 730, "LOGIN", a=int(255 * a))
    fm = font(F_MONOB, 32)
    nt = int(clamp((t - P_TYPE) / 0.9) * 7)
    c.text((120, 320), "You type", font=font(F_SEMI, 26), fill=GREY)
    c.rounded_rectangle((120, 356, 500, 420), radius=14, fill=(10, 14, 22), outline=EDGE, width=2)
    c.text((146, 388), "hunter2"[:nt], font=fm, fill=WHITE, anchor="lm")
    p = appear(t, P_HASH, 0.3)
    if p > 0:
        A = int(255 * p)
        c.text((540, 388), "hash →", font=font(F_BOLD, 30), fill=HSH + (A,), anchor="mm")
        c.rounded_rectangle((610, 356, 960, 420), radius=14, fill=(10, 14, 22, A), outline=HSH + (A,), width=2)
        c.text((785, 388), "f52fbd32b2b3…", font=font(F_MONOB, 28), fill=HSH + (A,), anchor="mm")
    p = appear(t, P_CMP, 0.3)
    if p > 0:
        A = int(255 * p)
        db(c, 610, 480, 960, 660, a=A)
        c.text((785, 530), "STORED HASH", font=font(F_BOLD, 22), fill=GREY + (A,), anchor="mm")
        c.text((785, 600), "f52fbd32b2b3…", font=font(F_MONOB, 28), fill=WHITE + (A,), anchor="mm")
        c.line((785, 425, 785, 470), fill=DIM + (A,), width=4)
    p = appear(t, P_OK, 0.3)
    if p > 0:
        A = int(255 * p)
        icon_check(c, 200, 560, 34, a=A)
        c.text((250, 545), "Match", font=font(F_BLACK, 44), fill=GREEN + (A,), anchor="lm")
        c.text((250, 595), "logged in", font=font(F_BOLD, 30), fill=GREY + (A,), anchor="lm")
        c.text((540, 700), "The real password is never stored", font=font(F_BOLD, 30), fill=YEL + (A,), anchor="mm")
    L.alpha_composite(C)
    return L

def panel_E(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a = appear(t, SC[4] + 0.3)
    pill(d, "THE DIFFERENCE", 540, (1 - a) * 16, YEL, (60, 50, 14), a=int(255 * a))
    for (name, col, rows, t0, y) in [("Encryption", ENC, [(True, "Two-way: read it again"), (True, "Messages, cards, HTTPS")], Q1, 100),
                                      ("Hashing", HSH, [(True, "One-way: just check it"), (True, "Passwords, file checks")], Q2, 420)]:
        p = appear(t, t0, 0.4)
        if p > 0: tradeoff(d, 70 + (1 - p) * 300, y, name, col, rows, int(255 * p))
    return L

def panel_F(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a = appear(t, SC[5] + 0.3)
    pill(d, "PRO TIP · PASSWORDS", 540, (1 - a) * 16, YEL, (60, 50, 14), a=int(255 * a))
    rows = [(False, "Encrypting passwords", T1), (False, "Plain SHA-256 or MD5", T2), (True, "bcrypt or argon2", T3)]
    for k, (ok, txt, t0) in enumerate(rows):
        p = appear(t, t0, 0.35)
        if p <= 0: continue
        A = int(255 * p); y = 120 + k * 170; X = 70 + (1 - p) * 200
        col = GREEN if ok else RED
        d.rounded_rectangle((X, y, X + 940, y + 140), radius=26, fill=CARD + (A,), outline=col + (A,), width=3)
        (icon_check if ok else icon_cross)(d, X + 80, y + 70, 36, a=A)
        d.text((X + 140, y + (52 if ok else 70)), txt, font=font(F_BLACK, 52), fill=WHITE + (A,), anchor="lm")
        if ok: d.text((X + 140, y + 105), "slow on purpose, so cracking is too", font=font(F_BOLD, 32), fill=GREY + (A,), anchor="lm")
    return L

def panel_G(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a = appear(t, SC[6] + 0.35)
    ctext(d, "Follow for more", 540, 230 + (1 - a) * 24, font(F_BLACK, 104), YEL, a=int(255 * a))
    a = appear(t, SC[6] + 0.9)
    ctext(d, "Dev concepts, explained simply", 540, 370 + (1 - a) * 20, font(F_BOLD, 52), WHITE, a=int(255 * a))
    a = appear(t, SC[6] + 1.5)
    if a > 0: pill(d, "Next: REST vs GraphQL", 540, 470 + (1 - a) * 14, WHITE, (44, 50, 64), size=36, a=int(255 * a))
    return L

PANELS = [panel_A, panel_B, panel_C, panel_D, panel_E, panel_F, panel_G]

exec(_sec("# ---------------- captions"))

def cap_text(s): return s.replace("SHA two fifty six", "SHA-256").replace("two way", "two-way").replace("one way", "one-way")
CAPTIONS = [c for i in range(len(VO)) for c in chunks_for(i)]

def wcol(w):
    lw = w.lower().strip(".,?!")
    if lw.startswith("encrypt") or lw.startswith("decrypt"): return ENC
    if lw.startswith("hash"): return HSH
    if lw in ("key", "reverse", "passwords", "password", "bcrypt", "argon2", "sha-256", "two-way", "one-way"): return YEL
    return WHITE

_frame0 = frame
_WM = Image.open("/home/claude/nltech-videos/engine/assets/watermark_nltech.png").convert("RGBA")
def frame(t):
    im = _frame0(t).convert("RGBA"); im.alpha_composite(_WM, ((W - _WM.width) // 2, 92)); return im.convert("RGB")
