"""REST vs GraphQL explainer with Byte, plum background."""
import re, json, math
SP = "/tmp/claude-0/-home-claude/e7805bda-0e11-5016-9991-51d072e57e6b/scratchpad/"
_SRC = open(SP + "clip3/tl.py").read()
_S4 = open(SP + "clip4/tl.py").read()
def _sec(a, b=None):
    i = _SRC.index(a); j = _SRC.index(b) if b else len(_SRC)
    return _SRC[i:j]
exec(_SRC[:_SRC.index("# ---------------- timeline")])
HERE = SP + "clip7/"

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
e = place(0, 0.3); SC.append(e + 0.45)
e = place(1, SC[1] + TR); e = place(2, e + 0.35); SWAP_B = frac(1, 0.43); SC.append(e + 0.45)
e = place(3, SC[2] + TR); e = place(4, e + 0.35); SWAP_C = vo_start[4]; SC.append(e + 0.45)
e = place(5, SC[3] + TR); SC.append(e + 0.45)
e = place(6, SC[4] + TR); SC.append(e + 0.45)
e = place(7, SC[5] + TR)
DURATION = round((e + 1.6) * FPS) / FPS
NS = len(SC)
def scene_at(t):
    i = 0
    for k in range(NS):
        if t >= SC[k]: i = k
    return i
REST = AN; GQL = (240, 90, 175)
C_PUN, C_ID, C_STR = (201, 209, 217), (230, 237, 243), (165, 214, 255)
R1 = frac(1, 0.5); R2 = frac(1, 0.78); OVER = vo_start[2] + 0.4; MANY = frac(2, 0.55)
PLATE = frac(3, 0.35); ONE_EP = frac(3, 0.7)
Q_T = vo_start[4] + 0.2; A_T = frac(4, 0.55)
K1, K2 = frac(5, 0.08), frac(5, 0.55)
U1, U2 = frac(6, 0.05), frac(6, 0.45)
EVENTS = {"whoosh": [], "swish": [], "pop": [vo_start[1], R1, R2, vo_start[3], PLATE, Q_T, A_T, K1, K2, U1, U2], "ding": [A_T + 0.5], "buzz": [OVER, MANY]}

exec(_sec("# ---------------- voice amplitude", "# ---------------- character poses"))
POSES = {
    "idle":  (0.28, 0.15, 0.28, 0.15, 0, 0, None),
    "wave":  (0.28, 0.15, 2.55, 0.35, 0, 1, None),
    "point": (0.30, 0.15, 2.35, -0.25, 0, 0, None),
    "menu":  (1.25, -1.15, 2.35, -0.25, 0, 0, "menu"),
    "plate": (1.25, -1.15, 2.35, -0.25, 0, 0, "plate"),
    "both":  (2.55, 0.35, 2.55, 0.35, 1, 1, None),
    "shrug": (1.05, 1.2, 1.05, 1.2, 0, 0, None),
}
KEYS = [(0.0, "wave"), (vend(0), "idle"), (vo_start[1] - 0.15, "menu"), (SWAP_B, "point"), (vend(2), "idle"),
        (vo_start[3] - 0.15, "plate"), (SWAP_C, "point"), (vend(4), "idle"),
        (vo_start[5] - 0.15, "shrug"), (K1 - 0.1, "point"), (vend(5), "idle"),
        (vo_start[6] - 0.15, "point"), (vend(6), "idle"), (vo_start[7] - 0.15, "both")]
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
    if prop == "menu":
        x0, y0 = hx - 110, hy - 260
        pd.rounded_rectangle((x0, y0, x0 + 220, y0 + 260), radius=16, fill=(250, 236, 200), outline=INK, width=10)
        pd.text((x0 + 110, y0 + 50), "MENU", font=font(F_BLACK, 44), fill=INK, anchor="mm")
        for k in range(3): pd.rounded_rectangle((x0 + 30, y0 + 100 + k * 50, x0 + 190, y0 + 120 + k * 50), radius=8, fill=(150, 130, 100))
    else:
        pd.ellipse((hx - 150, hy - 150, hx + 150, hy + 10), fill=(240, 244, 250), outline=INK, width=10)
        for (dx, dy, c) in [(-60, -80, (90, 190, 90)), (10, -95, (232, 72, 72)), (70, -70, (255, 200, 60))]:
            pd.ellipse((hx + dx - 34, hy + dy - 26, hx + dx + 34, hy + dy + 26), fill=c)
_char = _sec("# ---------------- character drawing", "# ---------------- panels")
_char = re.sub(r'        if prop == "id":.*?(?=        d2_alpha)', "        draw_prop(pd, prop, hx, hy)\n", _char, flags=re.S)
exec(_char)
exec(_sec("# ---------------- panels", "# ---------------- captions"))
exec(_S4[_S4.index("# ---------------- generic bits"):_S4.index("def panel_A")])
exec(_S4[_S4.index("def tradeoff"):_S4.index("def panel_D")])

def mono_block(c, x, y, lines, col_fn, size=30, lh=42, a=255):
    f = font(F_MONOB, size)
    for i, (ln, col) in enumerate(lines):
        c.text((x, y + i * lh), ln, font=f, fill=col + (a,))

def panel_A(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    for (txt, f, col, y, t0) in [("REST", font(F_BLACK, 170), REST, 170, 0.25), ("vs", font(F_BOLD, 64), GREY, 310, 0.7), ("GraphQL", font(F_BLACK, 150), GQL, 440, 1.05)]:
        a = appear(t, t0)
        if a > 0: ctext(d, txt, 540, y + (1 - a) * 30, f, col, a=int(255 * a))
    a = appear(t, frac(0, 0.4))
    if a > 0: pill(d, "Two ways to get data from a server", 540, 570 + (1 - a) * 14, WHITE, (60, 40, 80), size=36, a=int(255 * a))
    return L

def panel_B(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    head(d, "REST", REST, "A set menu", t, SC[1] + 0.3)
    x1, x2 = slide_x(t, SWAP_B)
    a = appear(t, vo_start[1])
    if a > 0 and x1 > -W + 1:
        C = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); c = ImageDraw.Draw(C); oy = (1 - a) * 40
        card_box(c, 70, 240 + oy, 1010, 730 + oy, "REAL LIFE  ·  FIXED MEALS")
        for k, (name, items) in enumerate([("Combo 1", "burger · fries · drink"), ("Combo 2", "rice · chicken · salad")]):
            y = 320 + k * 170 + oy
            c.rounded_rectangle((130, y, 950, y + 140), radius=20, fill=(10, 14, 22), outline=EDGE, width=2)
            c.text((170, y + 45), name, font=font(F_BLACK, 44), fill=WHITE, anchor="lm")
            c.text((170, y + 100), items, font=font(F_BOLD, 32), fill=GREY, anchor="lm")
        c.text((540, 680 + oy), "Each URL = one fixed meal", font=font(F_BOLD, 32), fill=YEL, anchor="mm")
        L.alpha_composite(C, (int(x1), 0))
    if t >= SWAP_B:
        C = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); c = ImageDraw.Draw(C)
        card_box(c, 70, 240, 1010, 730, "IN AN APP  ·  ONE SCREEN, TWO CALLS")
        for k, (route, body, t0) in enumerate([("GET /users/7", '{ name, email, phone, address,\n  avatar, createdAt, ... }', R1), ("GET /users/7/posts", '[ { title, body, tags, likes, ... } ]', R2)]):
            p = appear(t, t0, 0.3)
            if p <= 0: continue
            A = int(255 * p); y = 325 + k * 195
            c.text((120, y + 20), route, font=font(F_MONOB, 36), fill=REST + (A,), anchor="lm")
            for i, ln in enumerate(body.split("\n")):
                c.text((120, y + 75 + i * 40), ln, font=font(F_MONO, 28), fill=GREY + (A,), anchor="lm")
        o = appear(t, OVER, 0.3)
        if o > 0:
            icon_cross(c, 820, 360, 22, a=int(255 * o)); c.text((850, 360), "extra data", font=font(F_BOLD, 28), fill=RED + (int(255 * o),), anchor="lm")
        m = appear(t, MANY, 0.3)
        if m > 0:
            icon_cross(c, 820, 555, 22, a=int(255 * m)); c.text((850, 555), "2 requests", font=font(F_BOLD, 28), fill=RED + (int(255 * m),), anchor="lm")
        L.alpha_composite(C, (int(x2), 0))
    return L

def panel_C(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    head(d, "GRAPHQL", GQL, "A buffet", t, SC[2] + 0.3)
    x1, x2 = slide_x(t, SWAP_C)
    a = appear(t, vo_start[3])
    if a > 0 and x1 > -W + 1:
        C = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); c = ImageDraw.Draw(C); oy = (1 - a) * 40
        card_box(c, 70, 240 + oy, 1010, 730 + oy, "REAL LIFE  ·  PICK WHAT YOU WANT")
        foods = [("rice", (240, 230, 200)), ("chicken", (210, 140, 70)), ("salad", (90, 190, 90)), ("fries", (255, 200, 60)), ("soup", (200, 80, 60))]
        for k, (nm, col) in enumerate(foods):
            x = 150 + k * 165; y = 330 + oy
            picked = k in (0, 2)
            c.ellipse((x, y, x + 110, y + 110), fill=col, outline=(GQL if picked and t > PLATE else EDGE), width=6 if picked and t > PLATE else 2)
            c.text((x + 55, y + 140), nm, font=font(F_BOLD, 26), fill=WHITE if picked else GREY, anchor="mm")
        p = appear(t, PLATE, 0.3)
        if p > 0:
            A = int(255 * p)
            c.ellipse((390, 520 + oy, 690, 640 + oy), fill=(240, 244, 250, A), outline=EDGE + (A,), width=3)
            c.ellipse((460, 545 + oy, 540, 605 + oy), fill=(240, 230, 200, A)); c.ellipse((550, 545 + oy, 630, 605 + oy), fill=(90, 190, 90, A))
        e1 = appear(t, ONE_EP, 0.3)
        if e1 > 0: c.text((540, 690 + oy), "One endpoint, exactly what you ask for", font=font(F_BOLD, 30), fill=YEL + (int(255 * e1),), anchor="mm")
        L.alpha_composite(C, (int(x1), 0))
    if t >= SWAP_C:
        C = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); c = ImageDraw.Draw(C)
        card_box(c, 70, 240, 1010, 730, "IN AN APP  ·  POST /graphql")
        q = appear(t, Q_T, 0.3)
        if q > 0:
            A = int(255 * q)
            c.text((120, 315), "YOU ASK", font=font(F_BOLD, 24), fill=GQL + (A,))
            mono_block(c, 120, 355, [("query {", C_PUN), ("  user(id: 7) {", C_ID), ("    name", GQL), ("    posts {", C_ID), ("      title", GQL), ("    }", C_PUN), ("  }", C_PUN), ("}", C_PUN)], None, size=28, lh=40, a=A)
        r = appear(t, A_T, 0.3)
        if r > 0:
            A = int(255 * r)
            c.line((540, 320, 540, 690), fill=EDGE + (A,), width=2)
            c.text((580, 315), "YOU GET", font=font(F_BOLD, 24), fill=GREEN + (A,))
            mono_block(c, 580, 355, [('{ "user": {', C_PUN), ('  "name": "Ada",', C_STR), ('  "posts": [', C_PUN), ('    { "title":', C_STR), ('      "Hello" }', C_STR), ('  ]', C_PUN), ('} }', C_PUN)], None, size=28, lh=40, a=A)
        L.alpha_composite(C, (int(x2), 0))
    return L

def panel_D(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a = appear(t, SC[3] + 0.3)
    pill(d, "WHICH ONE?", 540, (1 - a) * 16, YEL, (60, 50, 14), a=int(255 * a))
    for (name, col, rows, t0, y) in [("REST", REST, [(True, "Simple and easy to cache"), (True, "Perfect for most APIs")], K1, 100),
                                      ("GraphQL", GQL, [(True, "Exact data in one request"), (False, "More setup, harder to cache")], K2, 420)]:
        p = appear(t, t0, 0.4)
        if p > 0: tradeoff(d, 70 + (1 - p) * 300, y, name, col, rows, int(255 * p))
    return L

def panel_E(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a = appear(t, SC[4] + 0.3)
    pill(d, "SIMPLE RULE", 540, (1 - a) * 16, YEL, (60, 50, 14), a=int(255 * a))
    for (qq, ans, col, t0, y) in [("Starting out / most APIs", "REST", REST, U1, 110), ("Screens with lots of connected data", "GraphQL", GQL, U2, 420)]:
        p = appear(t, t0, 0.4)
        if p <= 0: continue
        X = 70 + (1 - p) * 300; A = int(255 * p)
        d.rounded_rectangle((X + 6, y + 14, X + 946, y + 254), radius=30, fill=(0, 0, 0, int(A * 0.45)))
        d.rounded_rectangle((X, y, X + 940, y + 240), radius=30, fill=CARD + (A,), outline=col + (A,), width=4)
        d.text((X + 470, y + 70), qq, font=font(F_BOLD, 42), fill=GREY + (A,), anchor="mm")
        d.line((X + 470, y + 110, X + 470, y + 140), fill=DIM + (A,), width=6)
        d.polygon([(X + 455, y + 135), (X + 485, y + 135), (X + 470, y + 152)], fill=DIM + (A,))
        d.text((X + 470, y + 190), ans, font=font(F_BLACK, 76), fill=col + (A,), anchor="mm")
    return L

def panel_F(t):
    L = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a = appear(t, SC[5] + 0.35); ctext(d, "Follow for more", 540, 230 + (1 - a) * 24, font(F_BLACK, 104), YEL, a=int(255 * a))
    a = appear(t, SC[5] + 0.9); ctext(d, "Dev concepts, explained simply", 540, 370 + (1 - a) * 20, font(F_BOLD, 52), WHITE, a=int(255 * a))
    a = appear(t, SC[5] + 1.5)
    if a > 0: pill(d, "Next: SQL vs NoSQL", 540, 470 + (1 - a) * 14, WHITE, (60, 40, 80), size=36, a=int(255 * a))
    return L

def _panel_A_cover(t): return panel_A(t + 3.0)
PANELS = [_panel_A_cover, panel_B, panel_C, panel_D, panel_E, panel_F]
exec(_sec("# ---------------- captions"))
def cap_text(s): return s.replace("slash users", "/users").replace("slash posts", "/posts")
CAPTIONS = [c for i in range(len(VO)) for c in chunks_for(i)]
def wcol(w):
    lw = w.lower().strip(".,?!")
    if lw == "rest": return REST
    if lw.startswith("graphql"): return GQL
    if lw in ("/users", "/posts", "exactly", "endpoint", "cache"): return YEL
    return WHITE
_frame0 = frame
_WM = Image.open("/home/claude/nltech-videos/engine/assets/watermark_nltech.png").convert("RGBA")
def frame(t):
    im = _frame0(t).convert("RGBA"); im.alpha_composite(_WM, ((W - _WM.width) // 2, 92)); return im.convert("RGB")
