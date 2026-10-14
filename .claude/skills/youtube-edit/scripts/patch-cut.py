#!/usr/bin/env python3
"""patch-cut.py: small fixes to an existing cut-list.json without rebuilding it by hand.
  --add A-B        put a stretch back (A = start of its first word, B = start of its last word, from the transcript);
                   the audio runs from A-0.15 s to the end of the speech chunk holding B (or just before the next word).
                   Needs --transcript and --speech.
  --drop T         remove the kept segment that starts within 0.3 s of T (a dangling fragment, a lone "Um").
  --drop-flat A-B  remove A-B given in FLAT-CUT time (what stutter-scan.py and CUT-REVIEW.html report). Mapped back to
                   the source through cut-map.json (src = src_start + (t - flat_start)), so the raw is cut once instead
                   of re-cutting input-video.mp4. Splits a segment when the range falls inside it; a range across a
                   join trims both sides. A remnant under --min-keep (0.10 s) goes too (it would be a flash frame).
                   Every range needs finite numeric start < end inside the flat duration, or nothing is written.
Then re-run apply-cut.py and re-transcribe the flat cut.
Usage: python3 patch-cut.py --cut-list W/cut-list.json --transcript W/transcript.json --speech W/speech.v1 --add 83.60-92.88 --drop 200.68
       python3 patch-cut.py --cut-list W/cut-list.json --drop-flat 41.20-41.62 --drop-flat 97.05-97.40 [--cut-map W/cut-map.json]
"""
import argparse, json, math, os, re, sys
ap = argparse.ArgumentParser()
ap.add_argument("--cut-list", required=True); ap.add_argument("--transcript"); ap.add_argument("--speech")
ap.add_argument("--add", action="append", default=[]); ap.add_argument("--drop", action="append", default=[], type=float)
ap.add_argument("--drop-flat", action="append", default=[]); ap.add_argument("--cut-map")
ap.add_argument("--min-keep", type=float, default=0.10)
ap.add_argument("--before", type=float, default=0.15); ap.add_argument("--after", type=float, default=0.45)
a = ap.parse_args()
if a.add and not (a.transcript and a.speech):
    ap.error("--add needs --transcript and --speech")
cl = json.load(open(a.cut_list))
kept = list(cl["kept"]); log = []

# ---- --drop-flat: validate every range against cut-map.json before touching anything ----------------------------
flat_src = []
if a.drop_flat:
    cm_path = a.cut_map or os.path.join(os.path.dirname(a.cut_list), "cut-map.json")
    if not os.path.exists(cm_path):
        sys.exit("no cut-map.json at %s: run apply-cut.py first (flat times only mean something against the flat cut it made)" % cm_path)
    cm = json.load(open(cm_path)); segs = cm["segments"]; flat_d = float(cm["flat_duration"])
    for c in segs:   # the map must describe THIS cut list (apply-cut snaps to the frame grid, so allow a frame)
        if not any(s["start"] - 0.05 <= c["src_start"] and c["src_end"] <= s["end"] + 0.05 for s in kept):
            sys.exit("cut-map.json does not match cut-list.json (source %.3f-%.3f is not kept): re-run apply-cut.py first"
                     % (c["src_start"], c["src_end"]))
    for spec in a.drop_flat:
        m = re.match(r"^\s*(-?[^\s-]+)\s*-\s*(-?[^\s-]+)\s*$", spec)
        try:
            A, B = float(m.group(1)), float(m.group(2))
        except (AttributeError, ValueError):
            A = B = float("nan")
        if not (math.isfinite(A) and math.isfinite(B) and A < B):
            sys.exit("--drop-flat %s: every cut range needs finite numeric start < end" % spec)
        if A < 0 or B > flat_d + 0.001:
            sys.exit("--drop-flat %s: cut range is outside the flat duration bounds (0 - %.3f s)" % (spec, flat_d))
        # a range that reaches a join also takes the sub-frame remainder apply-cut's snap left at that edge (0.04 s)
        src = [(c["src_start"] + (A - c["flat_start"]) if A > c["flat_start"] else c["src_start"] - 0.04,
                c["src_start"] + (B - c["flat_start"]) if B < c["flat_end"] else c["src_end"] + 0.04)
               for c in segs if A < c["flat_end"] and c["flat_start"] < B]
        flat_src.append((spec, [(round(x, 3), round(y, 3)) for x, y in src if y > x]))

for t in a.drop:
    n = len(kept); kept = [s for s in kept if abs(s["start"] + a.before - t) > 0.3 and abs(s["start"] - t) > 0.3]
    log.append("drop %.2f: %d segment(s)" % (t, n - len(kept)))
if a.add:
    raw = json.load(open(a.transcript)); words = raw["words"] if isinstance(raw, dict) and "words" in raw else raw
    words = sorted([{"start": float(w["start"]), "end": float(w["end"]), "text": w["text"]} for w in words], key=lambda w: w["start"])
    d = json.load(open(a.speech)); num, den = [int(x) for x in str(d.get("timebase", "30/1")).split("/")]; fps = num / den
    chunks = [(x / fps, y / fps) for x, y, sp in d["chunks"] if sp not in (99999, 0)]
for spec in a.add:
    A, B = [float(x) for x in spec.split("-")]
    wb = min(words, key=lambda w: abs(w["start"] - B))
    nxt = next((w for w in words if w["start"] > wb["start"] + 0.01), None)
    hold = [c for c in chunks if c[0] <= wb["start"] <= c[1] + 0.05]
    end = hold[-1][1] if hold else wb["end"] + a.after
    if nxt and nxt["start"] - 0.1 < end: end = max(wb["end"], nxt["start"] - 0.1)
    kept.append({"start": round(A - a.before, 3), "end": round(end, 3)}); log.append("add %.2f-%.2f -> %.2f-%.2f" % (A, B, A - a.before, end))
kept.sort(key=lambda s: s["start"]); merged = []
for s in kept:
    if merged and s["start"] <= merged[-1]["end"] + 0.05: merged[-1]["end"] = max(merged[-1]["end"], s["end"])
    else: merged.append(dict(s))

# ---- --drop-flat: subtract the mapped source ranges (after the merge, so a short drop is not merged back) --------
for spec, src in flat_src:
    log.append("drop-flat %s -> source %s" % (spec, ", ".join("%.3f-%.3f" % r for r in src)))
    for x, y in src:
        out = []
        for s in merged:
            if y <= s["start"] or x >= s["end"]:
                out.append(s); continue
            for piece in ({"start": s["start"], "end": round(x, 3)}, {"start": round(y, 3), "end": s["end"]}):
                L = piece["end"] - piece["start"]
                if L >= a.min_keep: out.append(piece)
                elif L > 0.001: log.append("sliver %.3f-%.3f (%.2f s) dropped too" % (piece["start"], piece["end"], L))
        merged = out
    cl.setdefault("flat_drops", []).append({"flat": spec, "source": [list(r) for r in src]})
if not merged:
    sys.exit("that would remove everything; nothing written")
cl["kept"] = merged; cl["kept_seconds"] = round(sum(s["end"] - s["start"] for s in merged), 2); cl["hand_patched"] = True
json.dump(cl, open(a.cut_list, "w"), indent=1)
print("; ".join(log) + " => kept %.1f s in %d segments" % (cl["kept_seconds"], len(merged)))
if flat_src:
    print("now re-run apply-cut.py (cut-map.json is stale) and re-transcribe the flat cut")
