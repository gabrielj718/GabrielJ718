#!/usr/bin/env python3
"""screen-activity.py: how much the screen recording changes over time (typing, scrolling, drawing show up; a
still page does not). Reads the screen track at 2 fps, 96 px wide, greyscale, and writes activity.json:
[[source_seconds, mean_abs_diff_0_255], ...]. Used to decide full-face sections on a Tella tutorial: a stretch
with no clicks AND activity near zero is a candidate; typing on a whiteboard shows as activity without clicks.
Usage: python3 screen-activity.py --video screen.mp4 --out activity.json
"""
import argparse, json, subprocess, sys
ap = argparse.ArgumentParser(); ap.add_argument("--video", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--fps", type=float, default=2.0); ap.add_argument("--width", type=int, default=96)
a = ap.parse_args()
probe = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "json", a.video], capture_output=True, text=True).stdout)
w0, h0 = probe["streams"][0]["width"], probe["streams"][0]["height"]; W = a.width; H = max(2, round(h0 * W / w0 / 2) * 2)
p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", a.video, "-vf", "fps=%s,scale=%d:%d,format=gray" % (a.fps, W, H), "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
n = W * H; prev = None; out = []; i = 0
while True:
    buf = p.stdout.read(n)
    if len(buf) < n: break
    if prev is not None:
        d = sum(abs(x - y) for x, y in zip(buf, prev)) / n
        out.append([round(i / a.fps, 2), round(d, 2)])
    prev = buf; i += 1
json.dump(out, open(a.out, "w"))
print("%s: %d samples, %.1f s, active(>1.5) %.0f%%" % (a.video, len(out), len(out) / a.fps, 100 * sum(1 for t, d in out if d > 1.5) / max(1, len(out))))
