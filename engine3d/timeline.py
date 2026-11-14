import json, os, sys
import numpy as np, soundfile as sf

sys.path.insert(0, "/home/claude/nltech-videos/engine")
os.environ.setdefault("KOKORO_DIR", "/home/claude/v3d/tts")
from codevid import tts_lines

FPS = 30
LINES = [
    ("intro", "let or const? Which one should you actually use?"),
    ("cards", "Here's the difference."),
    ("let", "Use let when the value will change later."),
    ("const", "Use const when it never changes. Start with const by default."),
    ("outro", "Follow for a new dev tip every day!"),
]
GAP = 0.35
LEAD = 0.6

clips = tts_lines([t for _, t in LINES], "/home/claude/v3d/cache", speed=1.08)
sr = sf.info(clips[0][0]).samplerate
t = LEAD
beats, chunks = [], [np.zeros(int(LEAD * sr))]
for (key, text), (path, dur) in zip(LINES, clips):
    a, _ = sf.read(path)
    words = text.split()
    weights = np.array([len(w) + 2 for w in words], float)
    edges = np.concatenate([[0], np.cumsum(weights) / weights.sum()]) * dur
    beats.append({"key": key, "text": text, "t0": t, "t1": t + dur,
                  "words": [{"w": w, "t": t + edges[i]} for i, w in enumerate(words)]})
    chunks += [a, np.zeros(int(GAP * sr))]
    t += dur + GAP
total = t + 1.4
chunks.append(np.zeros(int(1.4 * sr)))
audio = np.concatenate(chunks)
sf.write("/home/claude/v3d/voice.wav", audio, sr)

hop = sr // FPS
n = int(total * FPS)
rms = []
for i in range(n):
    seg = audio[i * hop:(i + 1) * hop]
    rms.append(float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0)
rms = np.array(rms); rms = np.clip(rms / (np.percentile(rms[rms > 0.005], 90) + 1e-6), 0, 1.2)
json.dump({"fps": FPS, "duration": total, "beats": beats, "rms": [round(x, 3) for x in rms]},
          open("/home/claude/v3d/timeline.json", "w"))
print(round(total, 2), [(b["key"], round(b["t0"], 2), round(b["t1"], 2)) for b in beats])
