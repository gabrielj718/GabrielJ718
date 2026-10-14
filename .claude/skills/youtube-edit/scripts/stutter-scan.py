#!/usr/bin/env python3
"""stutter-scan.py: second opinion on the paper cut, using a mechanical mistake finder.

paper-cut.py handles retakes, restarts, markers and false starts at the sentence level. The finder
(find-cut-candidates.mjs, next to this script; MIT, see LICENSES/MIT-starter-kit.txt) adds word-level
stutters ("the the", "I- I") and a Jaccard retake pass. Run it on the transcript of the FLAT CUT (after
apply-cut.py) so any survivor is a real candidate, then read each one in context: emphatic repetition
("never, never") looks identical to a stutter and must stay. Needs Node.js (node on PATH).

Usage:
  python3 stutter-scan.py --transcript videos/<p>/transcript.json --out-dir videos/<p>/candidates
Writes candidates/<stem>.cut-candidates.json + .md (the finder's format) and prints the summary.
Approved cuts go into a second apply-cut.py pass (cut-list-v2.json), never into the raw cut list.
"""
import argparse, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FINDER = os.path.join(HERE, "find-cut-candidates.mjs")

ap = argparse.ArgumentParser()
ap.add_argument("--transcript", required=True)
ap.add_argument("--out-dir", required=True)
args = ap.parse_args()
if not os.path.exists(FINDER):
    sys.exit("find-cut-candidates.mjs not found at %s (it ships next to this script)" % FINDER)

raw = json.load(open(args.transcript))
words = raw["words"] if isinstance(raw, dict) and "words" in raw else raw
words = [{"text": w["text"], "start": float(w["start"]), "end": float(w["end"]), "type": "word"} for w in words if w.get("text")]
os.makedirs(args.out_dir, exist_ok=True)
kit_json = os.path.join(args.out_dir, "flat-transcript.json")
json.dump({"language_code": "en", "audio_duration_secs": words[-1]["end"] if words else 0,
           "text": " ".join(w["text"] for w in words), "words": words}, open(kit_json, "w"))
res = subprocess.run(["node", FINDER, kit_json, "--out-dir", args.out_dir], capture_output=True, text=True)
if res.returncode != 0:
    sys.exit(res.stderr)
summary = json.loads(res.stdout)
md = summary["outputs"]["md"]
print("candidates: %d %s -> %s" % (summary["candidates"], json.dumps(summary["counts"]), md))
print(open(md).read())
