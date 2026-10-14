#!/usr/bin/env python3
"""phrase-times.py: where is it said? Finds each phrase in a Parakeet transcript.json and prints the start of its
first word and the end of its last word (seconds), so storyboard beats can be timed to word starts without reading
the whole transcript. Fuzzy on punctuation and case; --after T restricts the search to after T seconds.
Usage: python3 phrase-times.py --transcript W/transcript.json "most important part" "driving force" ... [--after 30]
"""
import argparse, json, re
ap = argparse.ArgumentParser(); ap.add_argument("--transcript", required=True); ap.add_argument("phrases", nargs="+"); ap.add_argument("--after", type=float, default=0.0)
a = ap.parse_args()
d = json.load(open(a.transcript)); W = d["words"] if isinstance(d, dict) and "words" in d else d
norm = lambda s: re.sub(r"[^a-z0-9' ]", "", s.lower()).split()
toks = [(norm(w["text"]), float(w["start"]), float(w["end"])) for w in W]
toks = [(t[0][0] if t[0] else "", t[1], t[2]) for t in toks]
for ph in a.phrases:
    p = norm(ph); hits = []
    for i in range(len(toks) - len(p) + 1):
        if toks[i][1] < a.after: continue
        if all(toks[i + k][0] == p[k] for k in range(len(p))): hits.append((toks[i][1], toks[i + len(p) - 1][2]))
    if not hits: print("%-44s  NOT FOUND" % ph); continue
    print("%-44s  " % ph + "   ".join("%.2f-%.2f" % h for h in hits[:4]) + ("   (+%d more)" % (len(hits) - 4) if len(hits) > 4 else ""))
