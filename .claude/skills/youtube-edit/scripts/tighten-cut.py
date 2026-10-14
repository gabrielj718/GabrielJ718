#!/usr/bin/env python3
"""tighten-cut.py: trim dead air by the SOUND, not the transcript (a cut built from word starts alone leaves too much
breathing room). Parakeet puts a phrase start up to 0.4 s before the first audible frame after a long pause, so a cut list built
from word starts keeps that silence at every join. For every kept segment: lead-in down to LEAD s before the first
audible 10 ms frame, tail down to TAIL s after the last, and every inner silence longer than MAXGAP cut to TAIL + LEAD
(the segment splits there, one more jump cut). Segments marked "room_tone": true pass through untouched (deliberate air).

Run with a Python that has numpy (the Parakeet venv's python does):
  ~/.venvs/parakeet/bin/python tighten-cut.py --audio W/audio-raw.wav --cut-list W/cut-list.json --out W/cut-list-tight.json
Then apply-cut.py on the tight list. Check a fresh transcription of the flat cut: every word must survive.
"""
import argparse, json, subprocess, numpy as np
ap = argparse.ArgumentParser()
ap.add_argument("--audio", required=True); ap.add_argument("--cut-list", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--threshold", type=float, default=40.0, help="10 ms RMS (16-bit) above which a frame counts as sound; a quiet room floor is ~5, speech ~1300")
ap.add_argument("--lead", type=float, default=0.07); ap.add_argument("--tail", type=float, default=0.11); ap.add_argument("--maxgap", type=float, default=0.30)
a = ap.parse_args()
pcm = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", a.audio, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout, np.int16).astype(float)
rms = np.sqrt(np.mean(pcm[: len(pcm) // 160 * 160].reshape(-1, 160) ** 2, axis=1))
d = json.load(open(a.cut_list)); kept = []
for s in d["kept"]:
    if s.get("room_tone"):
        kept.append(s); continue
    i0, i1 = int(round(s["start"] * 100)), int(round(s["end"] * 100))
    loud = np.convolve((rms[i0:i1] > a.threshold).astype(float), np.ones(4) / 4, mode="same") >= 0.75
    idx = np.where(loud)[0]
    if not len(idx):
        continue
    runs, r0, prev = [], idx[0], idx[0]
    for i in idx[1:]:
        if (i - prev) / 100 > a.maxgap:
            runs.append((r0, prev)); r0 = i
        prev = i
    runs.append((r0, prev))
    for r0, r1 in runs:
        kept.append({"start": round(max(s["start"], (i0 + r0) / 100 - a.lead - 0.02), 3), "end": round(min(s["end"], (i0 + r1 + 1) / 100 + a.tail), 3)})
d["kept"] = kept; d["kept_seconds"] = round(sum(k["end"] - k["start"] for k in kept), 3)
json.dump(d, open(a.out, "w"), indent=1)
print("segments %d, kept %.2fs" % (len(kept), d["kept_seconds"]))
