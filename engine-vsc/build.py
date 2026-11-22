import hashlib, json, os, random, subprocess, sys, runpy
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

ROOT = os.path.dirname(os.path.abspath(__file__))
TTS = "/home/claude/v3d/tts"
VOICE, SPEED = "am_liam", 1.05
SR = 24000
CHAIN = "highpass=f=80,equalizer=f=3200:t=q:w=1.2:g=3,equalizer=f=250:t=q:w=1:g=-2,acompressor=threshold=-20dB:ratio=3:attack=5:release=80"

_k = None
def tts(text):
    global _k
    os.makedirs(f"{ROOT}/cache", exist_ok=True)
    h = hashlib.md5(f"{VOICE}{SPEED}{text}".encode()).hexdigest()[:16]
    out = f"{ROOT}/cache/{h}.wav"
    if not os.path.exists(out):
        if _k is None:
            _k = Kokoro(f"{TTS}/kokoro.onnx", f"{TTS}/voices.bin")
        a, sr = _k.create(text, voice=VOICE, speed=SPEED, lang="en-us")
        raw = out + ".raw.wav"
        sf.write(raw, a, sr)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", CHAIN, "-ar", str(SR), out], check=True)
        os.remove(raw)
    a, _ = sf.read(out)
    return a


NEAR = {c: n for c, n in zip("qwertyuiopasdfghjklzxcvbnm", "wertyuiopqsdfghjklazxcvbnmq")}


def keystrokes(text, t, rng, cps=13.0):
    keys = []
    for ch in text:
        if ch.isalpha() and rng.random() < 0.025:
            keys.append([round(t, 3), NEAR.get(ch.lower(), ch)])
            t += 0.09 + rng.random() * 0.05
            t += 0.22
            keys.append([round(t, 3), "\b"])
            t += 0.12
        keys.append([round(t, 3), ch])
        base = 1.0 / cps
        if ch == "\n":
            base += 0.28
        elif ch in " .,(){};":
            base += 0.05
        t += base * (0.6 + rng.random() * 0.8)
    return keys, t


def build(spec_path):
    spec = runpy.run_path(spec_path)["SPEC"]
    rng = random.Random(spec.get("seed", 1))
    events, beats = [], []
    t = 0.35
    audio_marks = []
    first_open = True
    for si, step in enumerate(spec["steps"]):
        voice = tts(step["say"])
        vdur = len(voice) / SR
        vstart = t + 0.15
        audio_marks.append((vstart, voice))
        cap = step.get("cap", step["say"])
        words = cap.split()
        wts = np.array([len(w) + 2 for w in words], float)
        edges = np.concatenate([[0], np.cumsum(wts) / wts.sum()]) * vdur
        beats.append({"t0": vstart, "t1": vstart + vdur, "words": [{"w": w, "t": round(vstart + edges[i], 3)} for i, w in enumerate(words)]})
        a = t + 0.3
        zoom = False
        for act in step.get("do", []):
            kind = act[0]
            if kind == "zoom":
                zoom = act[1]
            elif kind == "open":
                a += 0.9
                events.append({"k": "mouse", "t": round(a - 0.85, 3), "to": "explorer", "file": act[1]})
                events.append({"k": "open", "t": round(a, 3), "file": act[1], "init": act[2] if len(act) > 2 else ""})
                if first_open:
                    events.append({"k": "sidebar", "t": round(a + 1.0, 3), "open": False})
                    first_open = False
                a += 0.5
            elif kind == "type":
                events.append({"k": "mouse", "t": round(a, 3), "to": "editor"})
                a += 0.25
                keys, end = keystrokes(act[1], a, rng)
                events.append({"k": "type", "t": round(a, 3), "end": round(end, 3), "keys": keys, "zoom": zoom})
                a = end + 0.35
            elif kind == "term":
                events.append({"k": "mouse", "t": round(a, 3), "to": "terminal"})
                a += 0.7
                keys, end = keystrokes(act[1], a, rng, cps=17)
                events.append({"k": "term", "t": round(a, 3), "keys": keys, "enter": round(end + 0.15, 3),
                               "out": [[round(end + 0.5 + i * 0.09, 3), o] for i, o in enumerate(act[2])]})
                a = end + 0.6 + 0.09 * len(act[2]) + 0.4
            elif kind == "hl":
                events.append({"k": "hl", "t": round(a, 3), "l0": act[1], "l1": act[2], "si": si})
            elif kind == "note":
                events.append({"k": "note", "t": round(a, 3), "text": act[1], "si": si})
                a += 0.3
            elif kind == "clear":
                events.append({"k": "clear", "t": round(a, 3)})
            elif kind == "wait":
                a += act[1]
        end = max(vstart + vdur, a) + 0.45
        for e in events:
            if e.get("si") == si and "until" not in e:
                e["until"] = round(end - 0.1, 3)
        t = end
    total = t + 3.8
    n = int(total * SR)
    mix = np.zeros(n)
    for s, v in audio_marks:
        i = int(s * SR)
        mix[i:i + len(v)] += v[: max(0, n - i)]
    crng = np.random.default_rng(7)
    def click(at, gain, dur=0.018, tone=2600):
        i = int(at * SR)
        m = int(dur * SR)
        if i + m >= n:
            return
        env = np.exp(-np.arange(m) / (m / 5))
        noise = crng.standard_normal(m)
        sig = (noise * 0.6 + np.sin(2 * np.pi * tone * np.arange(m) / SR) * 0.4) * env
        mix[i:i + m] += sig * gain
    for e in events:
        if e["k"] in ("type", "term"):
            for kt, ch in e["keys"]:
                click(kt, 0.05 * (0.7 + crng.random() * 0.6), tone=2200 + crng.random() * 900)
        if e["k"] == "term":
            click(e["enter"], 0.08, dur=0.03, tone=1500)
        if e["k"] == "mouse" and e["to"] in ("explorer", "terminal"):
            click(e["t"] + 0.75, 0.06, dur=0.012, tone=3500)
    wav = f"{ROOT}/out/voice.wav"
    os.makedirs(f"{ROOT}/out", exist_ok=True)
    sf.write(wav, mix, SR)
    tl = {"fps": 30, "duration": round(total, 3), "spec": {k: v for k, v in spec.items() if k != "steps"}, "beats": beats, "events": events}
    json.dump(tl, open(f"{ROOT}/out/timeline.json", "w"))
    print("duration", round(total, 1))


if __name__ == "__main__":
    build(sys.argv[1])
