#!/usr/bin/env python3
"""gap-scan.py: coverage scan of a composition for long-form pacing.

Lists every timed overlay (card-host, cutaway) and every camera move in public/index.html by start time and
reports the stretches where nothing changes: no overlay on screen and no camera move. A camera move is a GSAP
tl.to / tl.fromTo on '#video-zoom' or '#video-wrap' with a literal time; a tl.set (the snap back at a jump cut)
is not a move. The test is whether any 15-20 second stretch feels static, so the defaults are: first 90 s
flag > 15 s, main body flag > 20 s, hard ceiling 30 s. Also prints the density: overlays and camera moves per
90 s against a target of about 7 + 7. Hooks under 60 s ignore the gaps; their budget is ~6 overlay moments
per 40 s (youtube-edit skill).

Usage:
  python3 gap-scan.py --index videos/<p>/public/index.html [--early 15 --body 20 --max 30]
"""
import argparse, re, sys

ap = argparse.ArgumentParser()
ap.add_argument("--index", required=True)
ap.add_argument("--early", type=float, default=15.0)
ap.add_argument("--body", type=float, default=20.0)
ap.add_argument("--max", type=float, default=30.0)
args = ap.parse_args()

html = open(args.index).read()
root = re.search(r'<div[^>]*data-composition-id="([^"]+)"[^>]*data-duration="([\d.]+)"', html)
if not root:
    sys.exit("no root composition found")
total = float(root.group(2))

items = []
for m in re.finditer(r"<(div|video|audio)\b([^>]*)>", html):
    attrs = m.group(2)
    if "data-start" not in attrs or "data-duration" not in attrs:
        continue
    if "data-composition-id" in attrs:      # the root stage is not an overlay
        continue
    gid = re.search(r'\bid="([^"]+)"', attrs)
    gid = gid.group(1) if gid else "?"
    if gid in ("bg-video", "fg-matte"):
        continue
    if m.group(1) == "audio":
        continue
    start = float(re.search(r'data-start="([\d.]+)"', attrs).group(1))
    dur = float(re.search(r'data-duration="([\d.]+)"', attrs).group(1))
    anchor = re.search(r'data-anchor="([^"]*)"', attrs)
    items.append((start, start + dur, gid, "[%s]" % anchor.group(1) if anchor else ""))
items.sort()

# camera moves: tl.to / tl.fromTo('#video-zoom' | '#video-wrap', {...}[, {...}], <time>); a set is not a move
moves = []
for m in re.finditer(r"tl\.(to|fromTo|set)\(\s*(['\"])#(video-zoom|video-wrap)\2\s*,([^;]*?),\s*([\d.]+)\s*\)\s*;", html):
    if m.group(1) == "set":
        continue
    t = float(m.group(5))
    d = re.findall(r"duration\s*:\s*([\d.]+)", m.group(4))
    moves.append((t, t + (float(d[-1]) if d else 0.0), "cam " + m.group(3), m.group(1)))
moves.sort()

print("composition %s  %.1fs  %d overlay(s), %d camera move(s)" % (root.group(1), total, len(items), len(moves)))
for s, e, gid, note in sorted(items + moves):
    print("  %7.2f - %7.2f  %-24s %s" % (s, e, gid, note))

gaps, cursor = [], 0.0
for s, e, gid, _ in sorted(items + moves):
    if s > cursor:
        gaps.append((cursor, s))
    cursor = max(cursor, e)
if cursor < total:
    gaps.append((cursor, total))

print("\ngaps (talking head only, camera still):")
flagged = 0
for a, b in gaps:
    g = b - a
    limit = args.early if a < 90 else args.body
    tag = ""
    if g > args.max:
        tag = "  <-- over the %.0fs ceiling" % args.max; flagged += 1
    elif g > limit:
        tag = "  <-- over %.0fs, consider a beat or a camera move" % limit; flagged += 1
    if g >= 5:
        print("  %7.2f - %7.2f  %5.1fs%s" % (a, b, g, tag))
covered, cur_s, cur_e = 0.0, None, None        # union of overlay spans, not their sum
for s, e, _, _ in items:
    if cur_e is None or s > cur_e:
        if cur_e is not None:
            covered += cur_e - cur_s
        cur_s, cur_e = s, e
    else:
        cur_e = max(cur_e, e)
if cur_e is not None:
    covered += cur_e - cur_s
per90 = lambda n: 90.0 * n / total if total else 0.0
print("\noverlay coverage %.0f%% of runtime, %d gap(s) flagged" % (100 * min(covered, total) / total, flagged))
print("density: %.1f overlays + %.1f camera moves per 90 s (target about 7 + 7)" % (per90(len(items)), per90(len(moves))))
sys.exit(1 if flagged else 0)
