#!/usr/bin/env python3
"""tella-timeline.py: one view of a cut Tella clip for laying it out: sentences on the PLAYBACK timeline with the
clicks and the screen activity that fall inside each. Source-time data (Parakeet words, activity.json) is mapped
through the clip's cuts (raw-recording ms, from get_clip / update_clip) and the lead-in offset.
Usage: python3 tella-timeline.py --clip-dir videos/<p>/tella/c5 --cuts-json cuts-final.json --key c5 [--tella-words tella-words.json] [--clicks clicks.json]
"""
import argparse, json, os, re
ap = argparse.ArgumentParser(); ap.add_argument("--clip-dir", required=True); ap.add_argument("--cuts-json", required=True); ap.add_argument("--key", required=True)
ap.add_argument("--tella-words"); ap.add_argument("--clicks", help="json list of [playback_ms, x, y]"); ap.add_argument("--activity")
a = ap.parse_args()
C = json.load(open(a.cuts_json))[a.key]; off = C["offset"]; cuts = sorted([(s / 1000, (s + d) / 1000) for s, d in C["cuts"]])
def playback(src_t):
    t = src_t - off; removed = 0.0
    for s, e in cuts:
        if t >= e: removed += e - s
        elif t > s: return None
        else: break
    return t - removed
d = json.load(open(os.path.join(a.clip_dir, "transcript.json"))); W = d["words"] if isinstance(d, dict) and "words" in d else d
words = [(playback(float(w["start"])), w["text"]) for w in W]; words = [(t, x) for t, x in words if t is not None]
# sentences by punctuation
sents = []; cur = []
for t, x in words:
    cur.append((t, x))
    if re.search(r"[.?!]$", x): sents.append(cur); cur = []
if cur: sents.append(cur)
clicks = json.load(open(a.clicks)) if a.clicks else []
act = None
if a.activity and os.path.exists(a.activity):
    act = [(playback(t), v) for t, v in json.load(open(a.activity))]; act = [(t, v) for t, v in act if t is not None]
if a.tella_words:
    tw = json.load(open(a.tella_words))["words"]; tm = {}
    for w in tw: tm.setdefault(w["text"].lower().strip(".,?!"), []).append(w["startTimeMs"] / 1000)
    errs = []
    for t, x in words:
        k = x.lower().strip(".,?!")
        if k in tm: errs.append(min(abs(t - u) for u in tm[k]))
    errs.sort(); print("mapping check vs Tella words: median %.2f s, 90th pct %.2f s (%d words)" % (errs[len(errs) // 2], errs[int(len(errs) * 0.9)], len(errs)))
for s in sents:
    t0, t1 = s[0][0], s[-1][0]; text = " ".join(x for _, x in s)
    cl = [c for c in clicks if t0 - 0.2 <= c[0] / 1000 <= t1 + 0.6]
    ac = ""
    if act:
        inside = [v for t, v in act if t0 - 0.3 <= t <= t1 + 0.6]
        ac = " act=%4.2f/%4.2f" % (sum(inside) / len(inside), max(inside)) if inside else " act=  ?  /  ?  "
    print("%6.1f-%6.1f%s clicks=%d  %s" % (t0, t1, ac, len(cl), text[:110]))
