#!/usr/bin/env python3
"""window-patch.py: make a render-ready copy of a composed project that covers only [T0, T1] of its timeline, so a
fix inside a long render costs seconds of capture instead of an hour. Render the copy with the same flags as the full
render, then lay it over the full render (ffmpeg overlay with enable='between(t,T0,T1)', patch shifted by T0).

What it rewrites in index.html: the stage and bg-video durations (bg-video gets data-media-start T0), every other
timed element shifted by -T0 (clamped into the window; ones fully outside get display:none), <audio> removed (the
patch is picture only; keep the full render's sound), and the registered timeline wrapped so window time t plays the
original timeline at T0 + t (tl.tweenFromTo). T0 and T1 are snapped to frames. The input video is hard-linked.

Usage: python3 window-patch.py --public videos/<p>/public --t0 1057.5 --t1 1092.1 --out videos/<p>/patch-a
Then:  npx hyperframes render videos/<p>/patch-a/public --resolution 4k --video-bitrate 45M --gpu --workers 1 -o .../patch-a.mp4
"""
import argparse, os, re, shutil
ap = argparse.ArgumentParser()
ap.add_argument("--public", required=True); ap.add_argument("--t0", type=float, required=True)
ap.add_argument("--t1", type=float, required=True); ap.add_argument("--out", required=True); ap.add_argument("--fps", type=int, default=30)
a = ap.parse_args()
T0, T1 = round(a.t0 * a.fps) / a.fps, round(a.t1 * a.fps) / a.fps; W = T1 - T0
dst = os.path.join(a.out, "public"); os.makedirs(dst, exist_ok=True)
for n in os.listdir(a.public):
    s, d = os.path.join(a.public, n), os.path.join(dst, n)
    if n in ("snapshots", "renders") or n.startswith("work-") or os.path.exists(d): continue
    if os.path.isdir(s): shutil.copytree(s, d)
    elif n.endswith((".mp4", ".mov", ".webm")) and os.path.getsize(s) > 50e6: os.link(s, d)
    else: shutil.copy2(s, d)
html = open(os.path.join(a.public, "index.html")).read()
html = re.sub(r"\n\s*<audio [^>]*></audio>", "", html)
def fix(m):
    tag = m.group(0)
    if 'id="stage"' in tag:
        return re.sub(r'data-duration="[0-9.]+"', 'data-duration="%.3f"' % W, tag)
    if 'id="bg-video"' in tag:
        tag = re.sub(r'data-duration="[0-9.]+"', 'data-duration="%.3f" data-media-start="%.3f"' % (W, T0), tag)
        return tag
    st, du = float(re.search(r'data-start="([0-9.]+)"', tag).group(1)), float(re.search(r'data-duration="([0-9.]+)"', tag).group(1))
    s, e = st - T0, st + du - T0
    if e <= 0 or s >= W:
        tag = re.sub(r'data-start="[0-9.]+"', 'data-start="0.000"', tag); tag = re.sub(r'data-duration="[0-9.]+"', 'data-duration="0.050"', tag)
        return re.sub(r'style="', 'style="display:none !important;', tag, count=1) if 'style="' in tag else tag.replace(">", ' style="display:none !important">', 1)
    ms = re.search(r'data-media-start="([0-9.]+)"', tag)
    if s < 0 and ms:
        tag = tag.replace(ms.group(0), 'data-media-start="%.3f"' % (float(ms.group(1)) - s))
    s2, e2 = max(0.0, s), min(W, e)
    tag = re.sub(r'data-start="[0-9.]+"', 'data-start="%.3f"' % s2, tag)
    return re.sub(r'data-duration="[0-9.]+"', 'data-duration="%.3f"' % (e2 - s2), tag)
html = re.sub(r'<[a-z]+ [^>]*data-start="[0-9.]+"[^>]*>', fix, html)
reg = re.search(r'window\.__timelines\["([^"]+)"\] = tl;', html)
if not reg: raise SystemExit("no window.__timelines registration found")
html = html.replace(reg.group(0), "const __outer = window.gsap.timeline({ paused: true }); tl.pause(0);\n        __outer.add(tl.tweenFromTo(%.4f, %.4f, { ease: 'none', duration: %.4f }), 0);\n"
                    "        window.__timelines[\"%s\"] = __outer;" % (T0, T1, W, reg.group(1)))
open(os.path.join(dst, "index.html"), "w").write(html)
print("window %.3f-%.3f (%.3f s, %d frames) -> %s" % (T0, T1, W, round(W * a.fps), dst))
