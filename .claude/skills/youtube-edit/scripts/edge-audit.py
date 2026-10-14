#!/usr/bin/env python3
"""edge-audit.py: check every edge of a cut list by the AUDIO, not the transcript, and optionally fix it.

Why: Parakeet merges a leaked sliver of a dropped take into the next word, so a transcript
looks clean while the viewer hears "right. [ght] A couple hours ago". Three glitch shapes, all found by level alone:
  - a segment that STARTS while sound is already playing (the tail of a dropped take rides in),
  - a segment that ENDS mid-sound (a chopped word, or the first sliver of the next dropped take),
  - a very short segment that holds no kept word (a restart fragment left behind by a later cut).

Fixes, in the direction that never loses a kept word:
  - a loud head moves to the quietest 10 ms in [first kept word start - 0.28, first kept word start + 0.10]
    (search BACKWARD from the first kept word; searching forward from the old start skipped "if you want the"),
  - a loud tail moves to the quietest 10 ms in [end - 0.35, end], never before the last kept word's start + 0.15,
  - a short fragment (< 0.5 s, no kept word) is dropped.

Usage:
  edge-audit.py --audio W/audio-raw.wav --cut-list W/cut-list.json --transcript W/transcript-raw.json
                [--keeps W/build/keeps.args] [--fix] [--threshold 300]
--keeps is the hand-cut keep list ("--keep A-B ..."); without it every transcript word counts as kept.
Always re-run after --fix: it must print "0 issues". Then apply-cut, then check the joins of the NEW file the same way.
"""
import argparse, json, re, wave
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--audio", required=True); ap.add_argument("--cut-list", required=True); ap.add_argument("--transcript", required=True)
ap.add_argument("--keeps", default=""); ap.add_argument("--fix", action="store_true"); ap.add_argument("--threshold", type=float, default=300)
a = ap.parse_args()

w = wave.open(a.audio); sr = w.getframerate()
x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float)
if w.getnchannels() > 1: x = x.reshape(-1, w.getnchannels()).mean(axis=1)
rms = lambda s, e: float(np.sqrt(np.mean(x[max(0, int(s * sr)):max(int(e * sr), int(s * sr) + 1)] ** 2)))
def valley(s, e):
    ts = np.arange(s, max(e, s + 0.02), 0.005); v = [rms(t, t + 0.02) for t in ts]; i = int(np.argmin(v)); return round(float(ts[i] + 0.01), 3), v[i]

T = json.load(open(a.transcript)); T = T["words"] if isinstance(T, dict) else T
keeps = [tuple(map(float, m.split("-"))) for m in re.findall(r"([\d.]+-[\d.]+)", open(a.keeps).read())] if a.keeps else []
kept = lambda t: (not keeps) or any(k0 - 0.02 <= t <= k1 + 0.02 for k0, k1 in keeps)
C = json.load(open(a.cut_list)); K = C["kept"]; issues, out = [], []
for i, s in enumerate(K):
    st, en = s["start"], s["end"]
    words = [q for q in T if st - 0.35 <= q["start"] < en and kept(q["start"])]
    if en - st < 0.5 and not any(st - 0.05 <= q["start"] < en for q in words):
        issues.append("seg %d %.2f-%.2f: short fragment, no kept word" % (i, st, en))
        if a.fix: continue
    if rms(st, st + 0.03) > a.threshold:
        issues.append("seg %d starts mid-sound at %.2f (rms %d)" % (i, st, rms(st, st + 0.03)))
        if a.fix and words:
            t, v = valley(words[0]["start"] - 0.28, words[0]["start"] + 0.10); s["start"] = t
    if rms(en - 0.03, en) > a.threshold:
        issues.append("seg %d ends mid-sound at %.2f (rms %d)" % (i, en, rms(en - 0.03, en)))
        if a.fix:
            floor = (words[-1]["start"] + 0.15) if words else st + 0.2
            t, v = valley(max(en - 0.35, floor), en); s["end"] = t
    out.append(s)
print("%d segments, %d issues" % (len(K), len(issues))); print("\n".join(issues))
if a.fix:
    C["kept"] = out; C["kept_seconds"] = round(sum(q["end"] - q["start"] for q in out), 3); C["edge_audit"] = "fixed by edge-audit.py"
    json.dump(C, open(a.cut_list, "w"), indent=1); print("wrote %s (%d segments, %.2f s); run again without --fix to confirm" % (a.cut_list, len(out), C["kept_seconds"]))
