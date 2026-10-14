#!/usr/bin/env python3
"""tella-cuts.py: turn a cut-list.json (kept segments in SOURCE seconds, from paper-cut.py / hand-cut.py run on the
downloaded Tella recording) into the `cuts` array that the Tella MCP's update_clip expects (removed ranges of the RAW
recording, in ms).

The one trap: Tella's clip timeline starts ~2.4 s into the downloadable source (the recorder's lead-in), so
raw_clip_time = source_time - (source_duration - clip.maxDurationSeconds). Pass both numbers and the shift is applied.

Usage:
  python3 tella-cuts.py --cut-list videos/<p>/tella/cut-list.json --source-duration 192.789 --clip-max 190.385
Prints the JSON to paste into update_clip(cuts=...) and writes tella-cuts.json next to the cut list.
"""
import argparse, json, os
ap = argparse.ArgumentParser()
ap.add_argument("--cut-list", required=True)
ap.add_argument("--source-duration", type=float, required=True, help="seconds, from ffprobe on the downloaded source")
ap.add_argument("--clip-max", type=float, required=True, help="clip.maxDurationSeconds from get_clip / update_clip")
args = ap.parse_args()
cl = json.load(open(args.cut_list))
off = args.source_duration - args.clip_max
cuts, t = [], 0.0
for s in cl["kept"]:
    a, b = max(0.0, s["start"] - off), max(0.0, s["end"] - off)
    if a - t > 0.02: cuts.append({"startTimeMs": int(round(t * 1000)), "durationMs": int(round((a - t) * 1000))})
    t = max(t, b)
if args.clip_max - t > 0.02: cuts.append({"startTimeMs": int(round(t * 1000)), "durationMs": int(round((args.clip_max - t) * 1000))})
out = os.path.join(os.path.dirname(os.path.abspath(args.cut_list)), "tella-cuts.json")
json.dump({"offset_seconds": round(off, 3), "cuts": cuts}, open(out, "w"), indent=1)
print(json.dumps(cuts, separators=(",", ":")))
print("offset %.3f s, %d cuts, playback %.1f s -> %s" % (off, len(cuts), args.clip_max - sum(c["durationMs"] for c in cuts) / 1000, out))
