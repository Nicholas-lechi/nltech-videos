"""YouTube end card: animated SUBSCRIBE click + bell ring, appended to YouTube versions.

python3 endcard.py build            -> assets/endcard_yt.mp4 (5s, 1080x1920, 48 kHz stereo)
python3 endcard.py append in.mp4 out.mp4   -> in.mp4 + end card
"""
import math, os, subprocess, sys
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
W, H, FPS, DUR = 1080, 1920, 30, 5.0
F = lambda n, s: ImageFont.truetype(os.path.join(ROOT, "fonts", n), s)
BLACK, BOLD = "InterDisplay-Black.otf", "InterDisplay-Bold.otf"
WHITE = (240, 244, 250); GREY = (150, 160, 176); RED = (230, 33, 23); YEL = (255, 210, 63)
def ease(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def eio(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

T_CLICK1, T_BELL, T_CLICK2 = 1.55, 2.0, 2.75
BTN = (190, 860, 760, 1000)       # subscribe button box
BELL_C = (880, 930)               # bell centre

def background():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    img = np.zeros((H, W, 3), np.float32) + np.array([9, 12, 19], np.float32)
    img += np.exp(-(((x - 540) / 650) ** 2 + ((y - 900) / 600) ** 2))[..., None] * np.array([60, 14, 14], np.float32)
    img[((x % 54) < 3) & ((y % 54) < 3)] += 12
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
BG = background()
BYTE = Image.open(os.path.join(ROOT, "assets", "byte_wave.png")).convert("RGBA").resize((480, 480))
WM = Image.open(os.path.join(ROOT, "assets", "watermark_nltech.png")).convert("RGBA")

def bell(size, angle, col):
    s = size; L = Image.new("RGBA", (s * 2, s * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    cx, cy = s, s
    d.ellipse((cx - s * 0.12, cy - s * 0.78, cx + s * 0.12, cy - s * 0.56), fill=col)
    d.pieslice((cx - s * 0.5, cy - s * 0.66, cx + s * 0.5, cy + s * 0.2), 180, 360, fill=col)
    d.polygon([(cx - s * 0.5, cy - s * 0.24), (cx + s * 0.5, cy - s * 0.24), (cx + s * 0.66, cy + s * 0.34), (cx - s * 0.66, cy + s * 0.34)], fill=col)
    d.rounded_rectangle((cx - s * 0.74, cy + s * 0.28, cx + s * 0.74, cy + s * 0.42), radius=int(s * 0.07), fill=col)
    d.ellipse((cx - s * 0.16, cy + s * 0.42, cx + s * 0.16, cy + s * 0.64), fill=col)
    return L.rotate(angle, resample=Image.BICUBIC, center=(cx, cy - s * 0.6))

def cursor(d, x, y, press):
    s = 1.0 - 0.12 * press
    pts = [(0, 0), (0, 64), (16, 50), (28, 78), (40, 72), (28, 46), (50, 46)]
    pts = [(x + px * s * 1.4, y + py * s * 1.4) for px, py in pts]
    d.polygon(pts, fill=(255, 255, 255), outline=(17, 24, 39))
    d.line(pts + [pts[0]], fill=(17, 24, 39), width=4)

def frame(t):
    im = BG.copy(); d = ImageDraw.Draw(im)
    a = ease(t / 0.35)
    def ct(xy, s, f, col, aa=1.0):
        A = int(255 * a * aa)
        d.text((xy[0] + 3, xy[1] + 5), s, font=f, fill=(0, 0, 0, int(A * 0.5)), anchor="mm")
        d.text(xy, s, font=f, fill=col + (A,), anchor="mm")
    ct((540, 470 + (1 - a) * 20), "Enjoyed this?", F(BLACK, 110), WHITE)
    ct((540, 600 + (1 - a) * 20), "Learn something new every day", F(BOLD, 48), GREY)
    # subscribe button
    pressed = 1.0 if t >= T_CLICK1 + 0.12 else 0.0
    sq = 1.0 - 0.06 * math.sin(math.pi * max(0, min(1, (t - T_CLICK1) / 0.22))) if t >= T_CLICK1 else 1.0
    x0, y0, x1, y1 = BTN; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    w2, h2 = (x1 - x0) / 2 * sq, (y1 - y0) / 2 * sq
    pop = ease((t - 0.25) / 0.35)
    if pop > 0:
        w2 *= 0.7 + 0.3 * pop; h2 *= 0.7 + 0.3 * pop
        col = (70, 76, 90) if pressed else RED
        d.rounded_rectangle((cx - w2 + 6, cy - h2 + 12, cx + w2 + 6, cy + h2 + 12), radius=int(h2), fill=(0, 0, 0, 110))
        d.rounded_rectangle((cx - w2, cy - h2, cx + w2, cy + h2), radius=int(h2), fill=col + (int(255 * pop),))
        label = "SUBSCRIBED" if pressed else "SUBSCRIBE"
        f = F(BLACK, 62 if not pressed else 54)
        if pressed:
            tw = f.getlength(label); lx = cx - tw / 2 + 26
            d.line((lx - 62, cy, lx - 44, cy + 18, lx - 14, cy - 16), fill=WHITE, width=9)
            d.text((lx, cy), label, font=f, fill=WHITE, anchor="lm")
        else:
            d.text((cx, cy), label, font=f, fill=(255, 255, 255, int(255 * pop)), anchor="mm")
    # bell
    bp = ease((t - T_BELL) / 0.3)
    if bp > 0:
        ring = t >= T_CLICK2
        ang = 22 * math.sin((t - T_CLICK2) * 28) * math.exp(-(t - T_CLICK2) * 1.6) if ring else 0
        b = bell(int(78 * (0.6 + 0.4 * bp)), ang, YEL if ring else WHITE)
        im.alpha_composite(b, (int(BELL_C[0] - b.width / 2), int(BELL_C[1] - b.height / 2)))
        d = ImageDraw.Draw(im)
        if ring:
            for k in range(2):
                r = 95 + k * 28 + 10 * math.sin(t * 12)
                aa = int(200 * max(0, 1 - (t - T_CLICK2) / 1.6))
                d.arc((BELL_C[0] - r, BELL_C[1] - r, BELL_C[0] + r, BELL_C[1] + r), 290, 340, fill=YEL + (aa,), width=7)
                d.arc((BELL_C[0] - r, BELL_C[1] - r, BELL_C[0] + r, BELL_C[1] + r), 200, 250, fill=YEL + (aa,), width=7)
    if t >= T_CLICK2 + 0.2:
        q = ease((t - T_CLICK2 - 0.2) / 0.3)
        d.text((540, 1110 + (1 - q) * 14), "Turn on notifications", font=F(BLACK, 58), fill=YEL + (int(255 * q),), anchor="mm")
        d.text((540, 1185 + (1 - q) * 14), "so you never miss a video", font=F(BOLD, 42), fill=GREY + (int(255 * q),), anchor="mm")
    # cursor path: enters from bottom right -> button -> bell
    if 0.6 <= t < 4.2:
        p1 = eio((t - 0.6) / 0.9); p2 = eio((t - T_CLICK1 - 0.35) / 0.75)
        sx, sy = 1000, 1500; bx, by = cx + 120, cy + 10; ex, ey = BELL_C[0] + 10, BELL_C[1] + 20
        x = sx + (bx - sx) * p1 + (ex - bx) * p2; y = sy + (by - sy) * p1 + (ey - by) * p2
        press = 0
        for tc in (T_CLICK1, T_CLICK2):
            if tc - 0.05 <= t <= tc + 0.2: press = 1
        cursor(d, x, y, press)
    im.alpha_composite(BYTE, (300, int(1290 + 10 * math.sin(t * 3.5))))
    d = ImageDraw.Draw(im)
    d.text((540, 1810), "@nicholaslechitech", font=F(BOLD, 42), fill=WHITE + (int(255 * a),), anchor="mm")
    im.alpha_composite(WM, ((W - WM.width) // 2, 92))
    return im.convert("RGB")

def audio(path, SR=48000):
    N = int(SR * DUR); out = np.zeros(N); t = np.arange(N) / SR
    for tc in (T_CLICK1, T_CLICK2):
        i = int(tc * SR); n = np.arange(int(0.05 * SR)) / SR
        out[i:i + len(n)] += 0.35 * np.random.default_rng(1).standard_normal(len(n)) * np.exp(-n * 160)
    i = int((T_CLICK2 + 0.05) * SR); n = np.arange(int(1.6 * SR)) / SR
    for f, a in ((1318, 0.22), (1976, 0.12), (2637, 0.07)):
        out[i:i + len(n)] += a * np.sin(2 * np.pi * f * n) * np.exp(-n * 2.6) * (1 + 0.3 * np.sin(2 * np.pi * 9 * n))
    i = int(0.25 * SR); n = np.arange(int(0.3 * SR)) / SR
    out[i:i + len(n)] += 0.12 * np.sin(2 * np.pi * (520 + 300 * np.exp(-n * 25)) * n) * np.exp(-n * 12)
    for m, a in ((57, 0.05), (64, 0.04), (69, 0.035)):
        f = 440 * 2 ** ((m - 69) / 12); out += a * np.sin(2 * np.pi * f * t) * np.minimum(1, t / 0.4) * np.minimum(1, (DUR - t) / 0.8)
    out = out / np.max(np.abs(out)) * 0.6
    sf.write(path, np.stack([out, out], 1).astype(np.float32), SR, subtype="PCM_16")

def build():
    out = os.path.join(ROOT, "assets", "endcard_yt.mp4"); wav = out + ".wav"
    audio(wav)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2", "-shortest", out], stdin=subprocess.PIPE)
    for k in range(int(DUR * FPS)): p.stdin.write(frame(k / FPS).tobytes())
    p.stdin.close(); p.wait(); os.remove(wav); print(out)

def append(src, dst):
    ec = os.path.join(ROOT, "assets", "endcard_yt.mp4")
    fc = ("[0:v]fps=30,format=yuv420p,setsar=1[v0];[1:v]fps=30,format=yuv420p,setsar=1[v1];"
          "[0:a]aresample=48000,aformat=channel_layouts=stereo[a0];[1:a]aresample=48000,aformat=channel_layouts=stereo[a1];"
          "[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-i", ec, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", dst], check=True)
    print(dst)

if __name__ == "__main__":
    if sys.argv[1] == "build": build()
    elif sys.argv[1] == "append": append(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "stills":
        ims = [frame(x).resize((270, 480)) for x in (0.5, 1.4, 1.75, 2.6, 3.2, 4.6)]
        s = Image.new("RGB", (270 * 6, 480)); [s.paste(im, (i * 270, 0)) for i, im in enumerate(ims)]; s.save(sys.argv[2])
