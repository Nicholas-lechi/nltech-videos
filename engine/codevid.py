"""NL-TECH coding-video engine.

Turns a script (a list of steps, each with a voice line and editor/terminal actions)
into a vertical 1080x1920 video: human-speed typing, voiceover, captions, soft sound,
NL-TECH watermark. No transition whooshes.

Usage:  python3 codevid.py path/to/spec.py out.mp4 [--stills]
"""
import bisect, hashlib, json, math, os, random, re, subprocess, sys, importlib.util
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
F = lambda n: os.path.join(ROOT, "fonts", n)
F_BLACK, F_BOLD, F_SEMI = F("InterDisplay-Black.otf"), F("InterDisplay-Bold.otf"), F("Inter-SemiBold.otf")
F_MONO, F_MONOB = F("JetBrainsMonoNL-Medium.ttf"), F("JetBrainsMonoNL-Bold.ttf")
_fc = {}
def font(p, s):
    if (p, s) not in _fc: _fc[(p, s)] = ImageFont.truetype(p, s)
    return _fc[(p, s)]

BG = (9, 12, 19); WHITE = (240, 244, 250); GREY = (139, 148, 158); DIM = (72, 82, 98)
YEL = (255, 210, 63); RED = (255, 92, 92); GREEN = (63, 220, 130); BLUE = (88, 166, 255)
ORANGE = (255, 159, 67); MINT = (110, 255, 210); PURPLE = (210, 168, 255)
CARD = (17, 22, 32); EDGE = (42, 52, 70)
C_KW, C_STR, C_TYPE, C_PUN, C_NUM, C_ID, C_DEC, C_FN, C_CMT = (255, 123, 114), (165, 214, 255), (255, 166, 87), (201, 209, 217), (121, 192, 255), (230, 237, 243), (255, 210, 63), (210, 168, 255), (110, 120, 136)

def ease(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def ease_io(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

# ---------------- voice ----------------
def tts_lines(texts, cache_dir, voice="am_michael", speed=1.08):
    os.makedirs(cache_dir, exist_ok=True)
    out, need = [], []
    for t in texts:
        h = hashlib.md5(f"{voice}|{speed}|{t}".encode()).hexdigest()[:12]
        p = os.path.join(cache_dir, f"{h}.wav"); out.append(p)
        if not os.path.exists(p): need.append((t, p))
    if need:
        from kokoro_onnx import Kokoro
        md = os.environ.get("KOKORO_DIR", os.path.expanduser("~/.cache/kokoro"))
        for fn, url in [("kokoro.onnx", "kokoro-v1.0.onnx"), ("voices.bin", "voices-v1.0.bin")]:
            fp = os.path.join(md, fn)
            if not os.path.exists(fp):
                os.makedirs(md, exist_ok=True)
                subprocess.run(["curl", "-sSL", "-o", fp, f"https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/{url}"], check=True)
        k = Kokoro(os.path.join(md, "kokoro.onnx"), os.path.join(md, "voices.bin"))
        for t, p in need:
            a, sr = k.create(t, voice=voice, speed=speed, lang="en-us")
            idx = np.where(np.abs(a) > 0.01)[0]; a = a[max(0, idx[0] - 200):idx[-1] + 2000]
            sf.write(p, a, sr)
    return [(p, sf.info(p).duration) for p in out]

# ---------------- syntax colouring ----------------
KW = set("import from export class const let var return async await new interface type extends implements constructor private public protected readonly function if else throw for of in while try catch finally default as typeof void null undefined true false this static model generator datasource enum".split())
TYPES = set("string number boolean any unknown never void".split())
TOK = re.compile(r"((?<![:\w])//.*)|('[^']*'?|\"[^\"]*\"?|`[^`]*`?)|(@\w+)|(\d+)|([A-Za-z_$][\w$]*)|(\s+)|(.)")
def colorize(line, lang="ts"):
    if lang == "sh":
        out = []
        for m in re.finditer(r"(\S+)|(\s+)", line):
            s = m.group(0); out.append((s, C_ID if not s.startswith("-") else C_TYPE))
        return out
    out = []
    toks = list(TOK.finditer(line))
    for k, m in enumerate(toks):
        s = m.group(0)
        if m.group(1): c = C_CMT
        elif m.group(2): c = C_STR
        elif m.group(3): c = C_DEC
        elif m.group(4): c = C_NUM
        elif m.group(5):
            nxt = toks[k + 1].group(0) if k + 1 < len(toks) else ""
            if s in KW: c = C_KW
            elif s in TYPES: c = C_NUM
            elif nxt == "(": c = C_FN
            elif s[0].isupper(): c = C_TYPE
            else: c = C_ID
        else: c = C_PUN
        out.append((s, c))
    return out

# ---------------- human typing ----------------
def keystrokes(text, t0, base, rng, scale=1.0, typos=True):
    """Type `text` appended to `base`. Returns (events [(t, buffer)], end_time, key_times)."""
    ev, keys, buf, t, i = [], [], base, t0, 0
    def gap(prev):
        g = min(0.085 + rng.expovariate(1 / 0.06), 0.3)
        if prev in " ,": g += 0.04
        if prev in "({:[": g += 0.1
        if rng.random() < 0.04: g += rng.uniform(0.2, 0.45)
        return g * scale
    prev = ""
    while i < len(text):
        ch = text[i]
        if ch == "\n":
            t += (0.28 + rng.expovariate(1 / 0.15)) * scale
            j = i + 1
            while j < len(text) and text[j] == " ": j += 1
            buf += "\n" + text[i + 1:j]; ev.append((t, buf)); keys.append((t, "enter")); i = j; prev = "\n"; continue
        if typos and i + 1 < len(text) and ch.isalpha() and text[i + 1].isalpha() and rng.random() < 0.012:
            for c in (text[i + 1], ch):
                t += gap(prev); buf += c; ev.append((t, buf)); keys.append((t, "key")); prev = c
            t += 0.35 * scale
            for _ in range(2):
                t += 0.07; buf = buf[:-1]; ev.append((t, buf)); keys.append((t, "back"))
            t += 0.12
        t += gap(prev); buf += ch; ev.append((t, buf)); keys.append((t, "key")); prev = ch; i += 1
    return ev, t, keys

# ---------------- build timeline from spec ----------------
class Timeline:
    def __init__(self, spec, cache):
        global THEME
        self.spec = spec
        THEME = spec.get("theme", "navy")
        steps = spec["steps"]
        vo = tts_lines([s["say"] for s in steps], cache, spec.get("voice", "am_michael"), spec.get("speed", 1.08))
        rng = random.Random(spec.get("seed", 7))
        self.INTRO = spec.get("intro_len", 3.2)
        t = self.INTRO
        self.vo = []           # (start, wav, dur, caption)
        self.ed = []           # (t, file, buffer)
        self.files = []        # (t, file) file switches
        self.term = []         # (t, lines)
        self.term_shown = None
        self.focus = []        # (t, 'ed'|'term')
        self.hl = []           # (t0, t1, file, l0, l1)
        self.notes = []        # (t0, t1, text)
        self.keys = []         # (t, kind)
        self.pops = []
        bufs = {}; cur = None; tlines = []
        for si, st in enumerate(steps):
            wav, dur = vo[si]
            vstart = t + 0.15
            self.vo.append((vstart, wav, dur, st.get("cap", st["say"])))
            at = t + st.get("lead", 0.35)
            step_hl, step_notes = [], []
            for a in st.get("do", []):
                kind = a[0]
                if kind in ("open", "file"):
                    name, init = a[1], (a[2] if len(a) > 2 else "")
                    if name not in bufs or kind == "file": bufs[name] = init
                    cur = name; self.files.append((at, name)); self.ed.append((at, name, bufs[name]))
                    self.focus.append((at, "ed")); at += 0.6
                elif kind == "type":
                    self.focus.append((at, "ed"))
                    ev, end, keys = keystrokes(a[1], at, bufs[cur], rng, typos=a[2] if len(a) > 2 else True)
                    self.ed += [(et, cur, b) for et, b in ev]; self.keys += keys
                    bufs[cur] = ev[-1][1] if ev else bufs[cur]; at = end + 0.2
                elif kind == "term":
                    if self.term_shown is None: self.term_shown = at; at += 0.4
                    self.focus.append((at, "term"))
                    cmd = a[1]; outs = a[2] if len(a) > 2 else []
                    tlines = tlines + ["$ "]
                    self.term.append((at, list(tlines)))
                    ev, end, keys = keystrokes(cmd, at + 0.2, "", rng, scale=0.75, typos=False)
                    for et, b in ev:
                        parts = b.split("\n")
                        self.term.append((et, tlines[:-1] + ["$ " + parts[0]] + ["  " + p for p in parts[1:]]))
                    self.keys += keys
                    tlines = self.term[-1][1]
                    at = end + 0.35; self.keys.append((at - 0.3, "enter"))
                    for o in outs:
                        tlines = tlines + [o]; self.term.append((at, list(tlines))); at += a[3] if len(a) > 3 else 0.28
                    at += 0.25
                elif kind == "hl":
                    step_hl.append((a[1], a[2], at))
                elif kind == "note":
                    step_notes.append((at, a[1]))
                elif kind == "wait":
                    at += a[1]
                elif kind == "clear":
                    tlines = []; self.term.append((at, []))
            end = max(vstart + dur, at) + st.get("tail", 0.45)
            for (l0, l1, d0) in step_hl:
                self.hl.append((max(vstart, d0), end - 0.1, cur, l0, l1))
            for (nt, txt) in step_notes:
                self.notes.append((nt, end - 0.1, txt)); self.pops.append(nt)
            t = end
        self.CODE_END = t
        self.DURATION = round((t + spec.get("outro_len", 4.5)) * FPS) / FPS
        self.ed.sort(key=lambda x: x[0]); self.term.sort(key=lambda x: x[0])
        self.ed_t = [e[0] for e in self.ed]; self.term_t = [e[0] for e in self.term]
        self.files_t = [f[0] for f in self.files]; self.focus_t = [f[0] for f in self.focus]
        self.key_t = sorted(k[0] for k in self.keys)
        self.caps = self._captions()

    def _captions(self):
        res = []
        for (s, _, d, txt) in self.vo:
            words = txt.split(); chunks, cur = [], []
            for w in words:
                cur.append(w)
                if len(" ".join(cur)) > 24 or w[-1] in ".?!,":
                    chunks.append(" ".join(cur)); cur = []
            if cur: chunks.append(" ".join(cur))
            total = sum(len(c) + 3 for c in chunks); tt = s
            for c in chunks:
                dd = d * (len(c) + 3) / total; res.append((tt, tt + dd, c)); tt += dd
        return res

    def at(self, arr_t, arr, t, default=None):
        i = bisect.bisect_right(arr_t, t) - 1
        return arr[i] if i >= 0 else default

# ---------------- drawing ----------------
LAYOUT = dict(cap_y=318, ed_y0=408, ed_y1=1118, term_y0=1146, term_y1=1452, note_y=1480)
CX0, CX1 = 36, 1044
HEADER, PAD, LH, CS = 66, 26, 50, 30
NLINES = (LAYOUT["ed_y1"] - LAYOUT["ed_y0"] - HEADER - PAD * 2) // LH
CODE_X = CX0 + 92

# Background themes: (base colour, glow colour added at the top, dot-grid delta, is_light)
THEMES = {
    "navy":   ((9, 12, 19), (20, 45, 95), 12, False),
    "white":  ((248, 249, 251), (-6, -3, 6), -14, True),
    "cream":  ((250, 246, 238), (-4, -8, -18), -14, True),
    "mint":   ((236, 250, 245), (-14, -4, -10), -14, True),
    "plum":   ((22, 12, 30), (60, 20, 70), 12, False),
    "forest": ((8, 20, 16), (10, 55, 40), 12, False),
    "char":   ((18, 18, 20), (30, 30, 34), 10, False),
}
THEME = "navy"
def is_light(): return THEMES[THEME][3]
_bg = {}
def background():
    if THEME not in _bg:
        base, glow, dot, _ = THEMES[THEME]
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        img = np.zeros((H, W, 3), np.float32) + np.array(base, np.float32)
        img += np.exp(-(((x - 540) / 700) ** 2 + ((y - 250) / 650) ** 2))[..., None] * np.array(glow, np.float32)
        img[((x % 54) < 3) & ((y % 54) < 3)] += dot
        _bg[THEME] = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
    return _bg[THEME].copy()

INK = (17, 24, 39)
DARKER = {YEL: (176, 120, 0), (110, 255, 210): (12, 140, 110), (63, 220, 130): (20, 140, 70), (255, 159, 67): (200, 95, 10), (88, 166, 255): (30, 100, 200), (255, 92, 92): (200, 40, 40)}
def on_bg(col):
    """Text colour adjusted for the current background."""
    if not is_light(): return col
    if col == WHITE: return INK
    if col == GREY: return (90, 100, 116)
    return DARKER.get(tuple(col), col)

_assets = {}
def asset(name):
    if name not in _assets: _assets[name] = Image.open(os.path.join(ROOT, "assets", name)).convert("RGBA")
    return _assets[name]

def word_col(w, hot):
    lw = w.strip(".,?!:;").lower()
    if lw in hot: return hot[lw]
    if re.search(r"[A-Z].*[A-Z]|\.|\(|_", w.strip(".,?!")): return YEL
    return WHITE

def draw_caption(img, text, t, s, hot):
    f = font(F_BLACK, 60); words = text.split(); sp = f.getlength(" ")
    lines, cur, cw = [], [], 0
    for w in words:
        ww = f.getlength(w)
        if cur and cw + sp + ww > 980: lines.append((cur, cw)); cur, cw = [], 0
        cw += (sp if cur else 0) + ww; cur.append((w, ww))
    if cur: lines.append((cur, cw))
    p = ease((t - s) / 0.12); A = int(255 * p)
    L = Image.new("RGBA", (W, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    top = 100 - 36 * len(lines)
    for li, (ws, lw) in enumerate(lines):
        x = (W - lw) / 2; y = top + li * 72 + (1 - p) * 10
        for w, ww in ws:
            if not is_light(): d.text((x + 3, y + 5), w, font=f, fill=(0, 0, 0, int(A * 0.6)))
            d.text((x, y), w, font=f, fill=on_bg(word_col(w, hot)) + (A,)); x += ww + sp
    img.alpha_composite(L, (0, LAYOUT["cap_y"] - 100))

def draw_editor(img, tl, t):
    y0, y1 = LAYOUT["ed_y0"], LAYOUT["ed_y1"]
    fe = tl.at(tl.ed_t, tl.ed, t)
    if not fe: return
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((CX0 + 6, y0 + 16, CX1 + 6, y1 + 16), radius=26, fill=(0, 0, 0, 120))
    d.rounded_rectangle((CX0, y0, CX1, y1), radius=26, fill=CARD + (250,), outline=EDGE, width=2)
    d.rectangle((CX0 + 2, y0 + HEADER, CX1 - 2, y0 + HEADER + 1), fill=EDGE)
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        cx = CX0 + 38 + i * 32; d.ellipse((cx - 10, y0 + 23, cx + 10, y0 + 43), fill=c)
    fe = tl.at(tl.ed_t, tl.ed, t)
    fsw = tl.at(tl.files_t, tl.files, t)
    if not fe:
        return
    _, fname, buf = fe
    fs = font(F_SEMI, 27); d.text((CX0 + 150, y0 + 18), fname, font=fs, fill=WHITE)
    d.rectangle((CX0 + 150, y0 + HEADER - 5, CX0 + 150 + fs.getlength(fname), y0 + HEADER - 1), fill=BLUE)
    lines = buf.split("\n")
    cur_line = len(lines) - 1
    # smooth scroll toward keeping the cursor line visible
    def target(tt):
        e = tl.at(tl.ed_t, tl.ed, tt)
        if not e or e[1] != fname: return 0
        n = len(e[2].split("\n")); return max(0, n - NLINES + 1)
    sc = sum(target(t - k * 0.05) for k in range(6)) / 6.0
    # file-open slide
    slide = 0.0
    if fsw and t - fsw[0] < 0.45: slide = (1 - ease_io((t - fsw[0]) / 0.45)) * 60
    cw = font(F_MONO, CS).getlength("M")
    top = y0 + HEADER + PAD
    clip = Image.new("RGBA", (W, H), (0, 0, 0, 0)); c = ImageDraw.Draw(clip)
    for (h0, h1, hf, l0, l1) in tl.hl:
        if hf == fname and h0 <= t <= h1:
            a = ease((t - h0) / 0.25) * (1 - ease((t - h1 + 0.2) / 0.2))
            ya = top + (l0 - 1 - sc) * LH - 4; yb = top + (l1 - sc) * LH - 6
            c.rounded_rectangle((CODE_X - 14, ya, CX1 - 18, yb), radius=10, fill=YEL + (int(40 * a),), outline=YEL + (int(220 * a),), width=3)
    first = int(sc)
    fn = font(F_MONO, 24); f = font(F_MONO, CS)
    for li in range(first, min(len(lines), first + NLINES + 2)):
        yy = top + (li - sc) * LH + slide
        if yy < top - LH or yy > y1 - PAD: continue
        c.text((CX0 + 72, yy + 6), str(li + 1), font=fn, fill=DIM, anchor="ra")
        x = CODE_X
        for s, col in colorize(lines[li]):
            if s.strip(): c.text((x, yy), s, font=f, fill=col)
            x += cw * len(s)
    foc = tl.at(tl.focus_t, tl.focus, t, (0, "ed"))[1]
    lk = tl.key_t[bisect.bisect_right(tl.key_t, t) - 1] if tl.key_t and bisect.bisect_right(tl.key_t, t) else -9
    idle = t - lk
    if foc == "ed" and (idle < 0.5 or int(idle * 1.9) % 2 == 0):
        yy = top + (cur_line - sc) * LH + slide
        cx = CODE_X + len(lines[-1]) * cw
        c.rectangle((cx + 1, yy + 2, cx + 4, yy + 40), fill=BLUE)
    mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).rectangle((CX0 + 2, y0 + HEADER + 2, CX1 - 2, y1 - 2), fill=255)
    L.paste(clip, (0, 0), Image.composite(clip.getchannel("A"), Image.new("L", (W, H), 0), mask))
    img.alpha_composite(L)

def draw_terminal(img, tl, t):
    if tl.term_shown is None or t < tl.term_shown: return
    p = ease((t - tl.term_shown) / 0.35)
    ff = tl.files_t[0] if tl.files_t else 1e9
    m = ease_io((t - ff) / 0.5) if t >= ff else 0.0
    by0, by1 = LAYOUT["ed_y0"], LAYOUT["ed_y1"]
    y0 = by0 + (LAYOUT["term_y0"] - by0) * m + (1 - p) * 40
    y1 = by1 + (LAYOUT["term_y1"] - by1) * m + (1 - p) * 40
    A = int(255 * p)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((CX0, y0, CX1, y1), radius=22, fill=(7, 9, 13, int(245 * p)), outline=EDGE + (A,), width=2)
    d.text((CX0 + 28, y0 + 16), "TERMINAL", font=font(F_BOLD, 22), fill=GREY + (A,))
    e = tl.at(tl.term_t, tl.term, t)
    lines = e[1] if e else []
    f = font(F_MONO, 28); cw = f.getlength("M")
    maxl = int((y1 - y0 - 60) // 40)
    show = lines[-maxl:]
    for i, ln in enumerate(show):
        yy = y0 + 52 + i * 40
        if ln.startswith("$ "):
            d.text((CX0 + 28, yy), "$", font=f, fill=GREEN + (A,))
            d.text((CX0 + 28 + cw * 2, yy), ln[2:], font=f, fill=WHITE + (A,))
        else:
            col = GREEN if ln.startswith(("✔", "[Nest]", "CREATE", "UPDATE")) else (RED if "rror" in ln else (165, 214, 255) if ln.startswith(("{", "[")) else GREY)
            d.text((CX0 + 28, yy), ln, font=f, fill=col + (A,))
    foc = tl.at(tl.focus_t, tl.focus, t, (0, "ed"))[1]
    if foc == "term" and show and show[-1].startswith("$ "):
        lk = tl.key_t[bisect.bisect_right(tl.key_t, t) - 1] if bisect.bisect_right(tl.key_t, t) else -9
        if t - lk < 0.5 or int((t - lk) * 1.9) % 2 == 0:
            yy = y0 + 52 + (len(show) - 1) * 40; cx = CX0 + 28 + cw * len(show[-1])
            d.rectangle((cx + 2, yy + 2, cx + 5, yy + 34), fill=WHITE + (A,))
    img.alpha_composite(L)

def draw_note(img, tl, t):
    for (t0, t1, txt) in tl.notes:
        if t0 <= t <= t1:
            a = ease((t - t0) / 0.3) * (1 - ease((t - t1 + 0.25) / 0.25)); A = int(255 * a)
            f = font(F_BOLD, 38); tw = f.getlength(txt)
            x0 = (W - tw) / 2 - 34; y = LAYOUT["note_y"] + (1 - a) * 16
            L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
            d.rounded_rectangle((x0, y, x0 + tw + 68, y + 76), radius=22, fill=(60, 50, 14, int(235 * a)), outline=YEL + (A,), width=3)
            d.text((W / 2, y + 38), txt, font=f, fill=YEL + (A,), anchor="mm")
            img.alpha_composite(L)

def ctext(d, xy, s, f, col, a=255):
    if not is_light(): d.text((xy[0] + 3, xy[1] + 5), s, font=f, fill=(0, 0, 0, int(a * 0.55)), anchor="mm")
    d.text(xy, s, font=f, fill=on_bg(col) + (a,), anchor="mm")

def wrap(text, f, maxw):
    words = text.split(); lines, cur = [], ""
    for w in words:
        tt = (cur + " " + w).strip()
        if f.getlength(tt) > maxw and cur: lines.append(cur); cur = w
        else: cur = tt
    if cur: lines.append(cur)
    return lines

def draw_intro(img, spec, t, dur):
    a_out = 1 - ease((t - dur + 0.3) / 0.3)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    p = ease(t / 0.35); A = int(255 * p * a_out)
    lab = f"{spec['series']}  ·  {spec['episode']}" if spec.get("episode") else spec["series"]
    f = font(F_BOLD, 34); tw = f.getlength(lab)
    col = spec.get("color", ORANGE)
    d.rounded_rectangle((W / 2 - tw / 2 - 28, 440, W / 2 + tw / 2 + 28, 502), radius=31, fill=tuple(int(v * 0.25) for v in col) + (A,))
    d.text((W / 2, 471), lab, font=f, fill=on_bg(col) + (A,), anchor="mm")
    ft = font(F_BLACK, spec.get("title_size", 92))
    for i, ln in enumerate(wrap(spec["title"], ft, 960)):
        q = ease((t - 0.25 - i * 0.12) / 0.35); Aq = int(255 * q * a_out)
        ctext(d, (W / 2, 610 + i * 108 + (1 - q) * 20), ln, ft, WHITE, Aq)
    if spec.get("subtitle"):
        q = ease((t - 0.8) / 0.35)
        d.text((W / 2, 900), spec["subtitle"], font=font(F_BOLD, 44), fill=on_bg(GREY) + (int(255 * q * a_out),), anchor="mm")
    img.alpha_composite(L)
    b = asset("byte_wave.png").resize((460, 460))
    q = ease((t - 0.5) / 0.4) * a_out
    if q > 0:
        bb = b.copy(); bb.putalpha(b.getchannel("A").point(lambda v: int(v * q)))
        img.alpha_composite(bb, (310, int(1000 + 10 * math.sin(t * 3.5) + (1 - q) * 40)))

def draw_outro(img, spec, t0, t):
    lt = t - t0
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    for (txt, f, col, y, d0) in [("Follow for more", font(F_BLACK, 100), YEL, 520, 0.1),
                                 (spec.get("outro_sub", "Dev concepts, explained simply"), font(F_BOLD, 48), WHITE, 650, 0.5)]:
        q = ease((lt - d0) / 0.35)
        if q > 0: ctext(d, (W / 2, y + (1 - q) * 20), txt, f, col, int(255 * q))
    if spec.get("next"):
        q = ease((lt - 0.9) / 0.35)
        if q > 0:
            f = font(F_BOLD, 40); s = "Next: " + spec["next"]; tw = f.getlength(s); A = int(255 * q)
            d.rounded_rectangle((W / 2 - tw / 2 - 30, 740, W / 2 + tw / 2 + 30, 812), radius=36, fill=((44, 50, 64) if not is_light() else (17, 24, 39)) + (A,))
            d.text((W / 2, 776), s, font=f, fill=WHITE + (A,), anchor="mm")
    img.alpha_composite(L)
    q = ease((lt - 0.3) / 0.4)
    b = asset("byte_wave.png").resize((460, 460)); b.putalpha(b.getchannel("A").point(lambda v: int(v * q)))
    img.alpha_composite(b, (310, int(900 + 10 * math.sin(t * 3.5))))

def frame(tl, t):
    img = background()
    spec = tl.spec
    if t < tl.INTRO:
        draw_intro(img, spec, t, tl.INTRO)
    elif t < tl.CODE_END:
        a = ease((t - tl.INTRO) / 0.35)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        first_ui = min([x for x in [tl.term_shown, tl.files_t[0] if tl.files_t else None] if x is not None] or [1e9])
        if t < first_ui + 0.4:
            q = 1 - ease((t - first_ui) / 0.4) if t >= first_ui else 1.0
            b = asset("byte_idle.png").resize((520, 520)); b.putalpha(b.getchannel("A").point(lambda v: int(v * q)))
            layer.alpha_composite(b, (280, int(640 + 12 * math.sin(t * 3.2))))
        draw_editor(layer, tl, t); draw_terminal(layer, tl, t); draw_note(layer, tl, t)
        fade_out = 1 - ease((t - tl.CODE_END + 0.35) / 0.35)
        aa = a * fade_out
        if aa < 0.999: layer.putalpha(layer.getchannel("A").point(lambda v: int(v * aa)))
        img.alpha_composite(layer, (0, int((1 - a) * 40)))
        for s, e_, c in tl.caps:
            if s <= t < e_: draw_caption(img, c, t, s, spec.get("hot", {})); break
    else:
        draw_outro(img, spec, tl.CODE_END, t)
        for s, e_, c in tl.caps:
            if s <= t < e_: draw_caption(img, c, t, s, spec.get("hot", {})); break
    wm = asset("watermark_nltech.png"); img.alpha_composite(wm, ((W - wm.width) // 2, 92))
    return img.convert("RGB")

# ---------------- audio ----------------
def mix_audio(tl, path, SR=24000):
    N = int(SR * tl.DURATION) + SR
    voice = np.zeros(N); music = np.zeros(N); fx = np.zeros(N)
    for (s, wav, d, _) in tl.vo:
        a, sr = sf.read(wav)
        if a.ndim > 1: a = a.mean(1)
        i = int(s * SR); voice[i:i + len(a)] += a[:N - i]
    rng = np.random.default_rng(3)
    bpm = 84; bar = 4 * 60 / bpm; mf = lambda m: 440 * 2 ** ((m - 69) / 12)
    chords = [[57, 60, 64], [53, 57, 60], [48, 55, 60], [55, 59, 62]]
    for i in range(int(tl.DURATION / bar) + 1):
        s0 = int(i * bar * SR); s1 = min(N, int((i + 1) * bar * SR) + int(0.4 * SR))
        if s0 >= N: break
        tt = np.arange(s1 - s0) / SR; env = np.minimum(1, tt / 0.6) * np.minimum(1, np.maximum(0, (bar + 0.4 - tt) / 0.6))
        for m in chords[i % 4]:
            f_ = mf(m); music[s0:s1] += 0.04 * env * (np.sin(2 * np.pi * f_ * tt) + 0.3 * np.sin(2 * np.pi * f_ * 1.003 * tt + 1))
    k = np.arange(int(0.22 * SR)) / SR; kick = np.sin(2 * np.pi * (50 + 80 * np.exp(-k * 30)) * k) * np.exp(-k * 13)
    tb = 0.0
    while tb < tl.DURATION - 1.5:
        i = int(tb * SR); e = min(N, i + len(kick)); music[i:e] += 0.16 * kick[:e - i]; tb += 60 / bpm
    env = np.convolve(np.abs(voice), np.ones(int(0.3 * SR)) / int(0.3 * SR), "same")
    duck = np.where(env > 0.004, 0.3, 1.0); duck = np.convolve(duck, np.ones(int(0.15 * SR)) / int(0.15 * SR), "same")
    music *= duck
    def add(t, seg):
        i = int(t * SR); e = min(N, i + len(seg))
        if e > i: fx[i:e] += seg[:e - i]
    for (t, kind) in tl.keys:
        L = int((0.03 if kind != "enter" else 0.05) * SR); n = np.arange(L) / SR
        c = np.diff(rng.standard_normal(L), prepend=0)
        thump = np.sin(2 * np.pi * (rng.uniform(140, 200) if kind != "back" else 240) * n)
        add(t, (0.5 * c * np.exp(-n * 260) + 0.45 * thump * np.exp(-n * 90)) * rng.uniform(0.07, 0.11) * (1.3 if kind == "enter" else 1))
    for t in tl.pops:
        n = np.arange(int(0.25 * SR)) / SR; add(t, 0.07 * np.sin(2 * np.pi * (600 + 400 * np.exp(-n * 30)) * n) * np.exp(-n * 16))
    out = voice + 0.55 * music + 0.8 * fx
    out = out[:int(SR * tl.DURATION)]
    fo = int(1.2 * SR); out[-fo:] *= np.linspace(1, 0, fo)
    out = out / (np.max(np.abs(out)) + 1e-9) * 0.9
    sf.write(path, out.astype(np.float32), SR, subtype="PCM_16")

# ---------------- render ----------------
def load_spec(path):
    s = importlib.util.spec_from_file_location("spec", path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m.SPEC

def render_part(spec_path, cache, k, parts, out):
    tl = Timeline(load_spec(spec_path), cache)
    n = int(round(tl.DURATION * FPS)); a, b = k * n // parts, (k + 1) * n // parts
    tmp = out + ".tmp.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for i in range(a, b): p.stdin.write(frame(tl, i / FPS).tobytes())
    p.stdin.close()
    if p.wait() == 0: os.rename(tmp, out)

def main():
    spec_path, out = sys.argv[1], sys.argv[2]
    work = os.path.splitext(out)[0] + "_work"; os.makedirs(work, exist_ok=True)
    cache = os.path.join(work, "vo")
    tl = Timeline(load_spec(spec_path), cache)
    print(f"duration {tl.DURATION:.1f}s", flush=True)
    if "--stills" in sys.argv:
        ts = [1.5] + [v[0] + v[2] * 0.8 for v in tl.vo[::max(1, len(tl.vo) // 10)]] + [tl.CODE_END + 2.5]
        ims = [frame(tl, x).resize((270, 480)) for x in ts]
        cols = 6; rows = (len(ims) + cols - 1) // cols
        sheet = Image.new("RGB", (270 * cols, 480 * rows))
        for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * 270, (i // cols) * 480))
        sheet.save(os.path.join(work, "sheet.jpg"), quality=85); print(os.path.join(work, "sheet.jpg")); return
    parts = int(os.environ.get("PARTS", "4")); procs = int(os.environ.get("PROCS", "2"))
    names = [os.path.join(work, f"part{k}.mp4") for k in range(parts)]
    todo = [k for k in range(parts) if not os.path.exists(names[k])]
    running = []
    for k in todo:
        running.append(subprocess.Popen([sys.executable, __file__, "--part", spec_path, cache, str(k), str(parts), names[k]]))
        if len(running) >= procs:
            running.pop(0).wait()
    for r in running: r.wait()
    with open(os.path.join(work, "list.txt"), "w") as fh:
        fh.writelines(f"file '{n}'\n" for n in names)
    mix_audio(tl, os.path.join(work, "audio.wav"))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", os.path.join(work, "list.txt"), "-i", os.path.join(work, "audio.wav"),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
                    "-shortest", "-movflags", "+faststart", out], check=True)
    print("wrote", out)

if __name__ == "__main__":
    if sys.argv[1] == "--part":
        render_part(sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), sys.argv[6])
    else:
        main()
