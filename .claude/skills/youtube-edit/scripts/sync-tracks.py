#!/usr/bin/env python3
"""sync-tracks.py: find the time offset between two recordings of the same take (the camera file and the
screen recording from the two-camera setup) by cross-correlating their audio, then optionally write copies
that start on the same instant.

Both files must have picked up the same sound (the voice reaches the camera mic and the computer mic).
Works on the first --window seconds of overlap, so a 20 minute session resolves in a few seconds.

Usage:
  ~/.venvs/parakeet/bin/python sync-tracks.py --a raw/C0001.MP4 --b raw/screen.mov
  ~/.venvs/parakeet/bin/python sync-tracks.py --a raw/C0001.MP4 --b raw/screen.mov --write-aligned videos/<p>/aligned
Prints: offset (seconds B starts after A; negative = B started first), confidence, and the ffmpeg
-ss to apply. With --write-aligned it trims the head of the earlier file so both begin together
(stream copy; frame-accurate to one keyframe, then the Cut stage re-encodes anyway).
Needs numpy: run with a Python that has it (the Parakeet venv's python does; or python3 -m pip install numpy).
"""
import argparse, json, os, subprocess, sys
try:
    import numpy as np
except ImportError:
    sys.exit("numpy missing: run with a Python that has it (e.g. ~/.venvs/parakeet/bin/python) or: python3 -m pip install numpy")

ap = argparse.ArgumentParser()
ap.add_argument("--a", required=True, help="reference (usually the camera file)")
ap.add_argument("--b", required=True, help="the other recording (usually the screen recording)")
ap.add_argument("--window", type=float, default=180.0, help="seconds of audio to correlate")
ap.add_argument("--rate", type=int, default=8000)
ap.add_argument("--write-aligned", default="")
args = ap.parse_args()

def audio(path, rate, seconds):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-t", str(seconds), "-vn", "-ac", "1", "-ar", str(rate),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
    x -= x.mean()
    # envelope-ish: emphasise onsets so room tone and hum do not dominate
    x = np.diff(x, prepend=0.0)
    return x / (np.abs(x).max() + 1e-9)

def duration(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                                 "default=nk=1:nw=1", path], capture_output=True, text=True).stdout.strip())

a = audio(args.a, args.rate, args.window)
b = audio(args.b, args.rate, args.window)
n = 1 << int(np.ceil(np.log2(len(a) + len(b))))
corr = np.fft.irfft(np.fft.rfft(a, n) * np.conj(np.fft.rfft(b, n)), n)
corr = np.concatenate([corr[-(len(b) - 1):], corr[:len(a)]])   # lags from -(len(b)-1) .. len(a)-1
lags = np.arange(-(len(b) - 1), len(a))
k = int(np.argmax(np.abs(corr)))
lag = lags[k]                       # samples: positive means B starts AFTER A (B is late), i.e. a[t] ~ b[t - lag]
peak = np.abs(corr[k]); rest = np.abs(corr); rest[max(0, k - args.rate // 10):k + args.rate // 10] = 0
confidence = float(peak / (rest.max() + 1e-9))
offset = lag / args.rate

# a[t] = b[t - lag]  ->  b starts `offset` seconds later than a when lag > 0 (b's sample i is a's sample i+lag)
res = {"a": args.a, "b": args.b, "offset_b_after_a": round(-offset, 4), "confidence": round(confidence, 2),
       "note": "trim the file that started EARLIER by |offset| so both begin on the same instant"}
print(json.dumps(res, indent=1))
if confidence < 3:
    print("WARNING: weak correlation; both files may not share sound, or the window missed speech. Try --window 600.", file=sys.stderr)

if args.write_aligned:
    os.makedirs(args.write_aligned, exist_ok=True)
    off = res["offset_b_after_a"]
    early, late = (args.a, args.b) if off > 0 else (args.b, args.a)
    for src in (args.a, args.b):
        dst = os.path.join(args.write_aligned, os.path.splitext(os.path.basename(src))[0] + "-aligned.mp4")
        cmd = ["ffmpeg", "-y", "-v", "error"]
        if src == early and abs(off) > 0.001:
            cmd += ["-ss", "%.3f" % abs(off)]
        cmd += ["-i", src, "-c", "copy", "-movflags", "+faststart", dst]
        subprocess.run(cmd, check=True)
        print("wrote", dst, "(trimmed %.3fs)" % abs(off) if src == early else "(untouched)")
