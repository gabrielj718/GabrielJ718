#!/usr/bin/env python3
"""hand-cut.py: rebuild cut-list.json from an explicit list of kept lines, for the cases paper-cut.py gets
wrong (a list it read as restarts, a slate it kept, a "last take" that carries a wrong word, retakes merged
into one Parakeet sentence).

Each --keep is "A-B": A = start time of the FIRST kept word, B = start time of the LAST kept word, both
straight from the transcript (dump the words for the region first). "A-B!" keeps the stretch whole, with its
internal pauses (a visual gag, a pause that carries meaning). Starts trust the transcript; ends
trust the audio: the kept stretch runs to the end of the auto-editor speech chunk that holds B, unless the
next word follows closely, in which case it stops just before that word.

Usage:
  python3 hand-cut.py --transcript W/transcript-raw.json --speech W/speech.v1 --duration 125.1 --out-dir W \
      --keep 5.20-9.9 --keep 10.96-15.4 ...   [--label "C0001 first idea"]
Writes cut-list.json (same shape as paper-cut.py, plus hand_cut:true) and PAPER-CUT.md listing the kept lines.
"""
import argparse, json, os

ap = argparse.ArgumentParser()
ap.add_argument("--transcript", required=True)
ap.add_argument("--speech", required=True)
ap.add_argument("--duration", type=float, required=True)
ap.add_argument("--out-dir", required=True)
ap.add_argument("--keep", action="append", required=True)
ap.add_argument("--before", type=float, default=0.15)
ap.add_argument("--after", type=float, default=0.45)
ap.add_argument("--label", default="")
args = ap.parse_args()

raw = json.load(open(args.transcript))
words = raw["words"] if isinstance(raw, dict) and "words" in raw else raw
words = [{"text": w["text"], "start": float(w["start"]), "end": float(w["end"])} for w in words]
d = json.load(open(args.speech)); num, den = [int(x) for x in str(d.get("timebase", "30/1")).split("/")]; fps = num / den
chunks = [(a / fps, b / fps) for a, b, sp in d["chunks"] if sp not in (99999, 0)]

def nearest(t):
    i = min(range(len(words)), key=lambda k: abs(words[k]["start"] - t))
    if abs(words[i]["start"] - t) > 0.06:
        raise SystemExit("no word starts at %.2f (nearest %.2f %r)" % (t, words[i]["start"], words[i]["text"]))
    return i

segments, lines = [], []
for spec in args.keep:
    whole = spec.endswith("!")          # "A-B!" keeps the stretch whole: no inner silence trimming (a visual gag, a pause that carries)
    a, b = [float(x) for x in spec.rstrip("!").split("-")]
    i0, i1 = nearest(a), nearest(b)
    w0, w1 = words[i0], words[i1]
    nxt = words[i1 + 1] if i1 + 1 < len(words) else None
    # hard end: just before the next word if it follows without a pause, else the audio chunk end
    hit = [c for c in chunks if c[1] > w0["start"] - 0.3 and c[0] < w1["start"] + 0.2]
    chunk_end = max((c[1] for c in hit), default=w1["end"] + args.after)
    chunk_end = min(chunk_end, w1["end"] + 1.2)
    end = chunk_end
    if nxt and nxt["start"] - w1["start"] < 1.5 and nxt["start"] < chunk_end:
        end = max(w1["start"] + 0.12, nxt["start"] - 0.03)
    # internal pauses inside the kept stretch: keep each speech chunk, drop the silence between chunks
    start = max(0.0, w0["start"] - args.before)
    inner = sorted(c for c in hit if c[1] > start and c[0] < end)
    fixed = []
    if whole or not inner:
        fixed.append((round(start, 3), round(min(args.duration, end), 3)))
    else:
        cur_s, cur_e = start, min(end, inner[0][1] + args.after)
        for c0, c1 in inner[1:]:
            if c0 - cur_e > args.before + 0.05:          # a real pause: close the piece, reopen at the chunk
                fixed.append((cur_s, cur_e))
                cur_s = c0 - args.before
            cur_e = min(end, c1 + args.after)
        fixed.append((cur_s, max(cur_e, end)))
        fixed = [(round(max(0.0, a), 3), round(min(args.duration, b), 3)) for a, b in fixed]
    segments += fixed
    lines.append("%6.2f  %s" % (w0["start"], " ".join(w["text"] for w in words[i0:i1 + 1])))

segments.sort()
merged = []
for s, e in segments:
    if e - s < 0.2:
        continue
    if merged and s - merged[-1][1] < 0.12:
        merged[-1][1] = max(merged[-1][1], e)
    else:
        merged.append([s, e])
kept = [{"start": s, "end": e} for s, e in merged]
removed, cursor = [], 0.0
for s in kept:
    if s["start"] > cursor + 0.01:
        removed.append({"start": round(cursor, 3), "end": s["start"], "reason": "hand cut", "text": ""})
    cursor = s["end"]
if cursor < args.duration:
    removed.append({"start": round(cursor, 3), "end": args.duration, "reason": "tail", "text": ""})
total = sum(s["end"] - s["start"] for s in kept)
os.makedirs(args.out_dir, exist_ok=True)
json.dump({"source_duration": args.duration, "kept_seconds": round(total, 2), "kept": kept, "removed": removed, "hand_cut": True},
          open(os.path.join(args.out_dir, "cut-list.json"), "w"), indent=1)
md = ["# Paper cut (hand cut)%s" % ((" - " + args.label) if args.label else ""), "",
      "Raw %.1fs -> kept %.1fs (%d segments). Only the kept lines are listed; everything else is out." % (args.duration, total, len(kept)), ""] + lines
open(os.path.join(args.out_dir, "PAPER-CUT.md"), "w").write("\n".join(md) + "\n")
print("kept %.1fs of %.1fs in %d segments" % (total, args.duration, len(kept)))
for s in kept:
    print("  %7.3f - %7.3f" % (s["start"], s["end"]))
