#!/usr/bin/env python3
"""snap-beats.py: snapshot every card moment of a composed project and tile them into one contact sheet.
Reads the storyboard.json next to public/ (compose.py format): tag in + 0.9, every beat in + 0.9, a list or
bullets beat again 0.6 s after its last item, plus any --at extras. A snapshot is seconds; a render is a minute.

Usage: python3 snap-beats.py --project videos/<p> [--at 12.3 --at 20.0]
Writes videos/<p>/snaps/at-<t>.png and videos/<p>/snaps/sheet.png (tiled, 640 px wide each).
"""
import argparse, json, os, subprocess, shutil, glob, math

ap = argparse.ArgumentParser()
ap.add_argument("--project", required=True)
ap.add_argument("--at", action="append", default=[])
args = ap.parse_args()
P = args.project
S = json.load(open(os.path.join(P, "storyboard.json")))
moments = []
if S.get("tag"):
    moments.append(S["tag"]["in"] + 0.9)
for b in S.get("beats", []):
    moments.append(float(b["in"]) + (1.5 if b["type"] == "pointer" else 0.9))
    if b["type"] in ("list", "bullets") and b.get("items"):
        moments.append(float(b["items"][-1][1]) + 0.6)
    # world / deck / doc / pills / chat / clip beats change state inside one beat: snapshot each state, not only the entrance
    if b["type"] == "world":
        moments += [float(c[0]) + (float(c[4]) if len(c) > 4 else 1.0) + 0.3 for c in b.get("cam", [])[1:]]
    elif b["type"] == "deck":
        moments.append(float(b.get("focus_at", float(b["in"]) + 0.9)) + 1.3)
        if b.get("recap_at") is not None:
            moments.append(float(b["recap_at"]) + 1.4)
    elif b["type"] == "doc":
        moments += [float(m["at"]) + 1.2 for m in b.get("marks", [])]
    elif b["type"] in ("pills", "chat", "clip") and (b.get("items") or b.get("messages")):
        last = (b.get("items") or b.get("messages"))[-1]
        moments.append((float(last["at"]) if isinstance(last, dict) else float(last[2] if b["type"] == "chat" else last[1])) + 0.6)
moments += [float(x) for x in args.at]
moments = sorted(set(round(min(m, float(S["duration"]) - 0.05), 2) for m in moments))
snapdir = os.path.join(P, "snaps"); os.makedirs(snapdir, exist_ok=True)
pub = os.path.join(P, "public")
env = dict(os.environ, PRODUCER_BROWSER_GPU_MODE="hardware")
outs = []
for t in moments:
    subprocess.run(["npx", "hyperframes", "snapshot", pub, "--at", str(t)], env=env, capture_output=True)
    cands = sorted(glob.glob(os.path.join(pub, "snapshots", "frame-00-at-*.png")))
    if not cands:
        print("no snapshot at", t); continue
    dst = os.path.join(snapdir, "at-%05.2f.png" % t)
    shutil.copy(cands[0], dst); outs.append(dst)
    print("snap", t)
if outs:
    cols = 3; rows = math.ceil(len(outs) / cols)
    cmd = ["ffmpeg", "-y", "-v", "error"]
    for o in outs: cmd += ["-i", o]
    n = len(outs)
    # pad to a full grid with copies of the last frame so tile does not drop a row
    while n % cols: cmd += ["-i", outs[-1]]; n += 1
    cmd += ["-filter_complex", "".join("[%d]" % i for i in range(n)) + "concat=n=%d:v=1:a=0,scale=640:360,tile=%dx%d" % (n, cols, rows), "-frames:v", "1", os.path.join(snapdir, "sheet.png")]
    subprocess.run(cmd, check=True)
    print("sheet:", os.path.join(snapdir, "sheet.png"), "(%d frames, %dx%d)" % (len(outs), cols, rows))
