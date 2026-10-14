#!/usr/bin/env python3
"""dead-air.py W [--max 0.45] [--target 0.30] [--keep T ...] [--plan] [--json out]: the dead-air scan of a flat cut
(the little stretches of dead silence a flat cut can still hold after a line is spoken).
W = the cut folder holding audio.wav (the flat cut's audio), cut-map.json and transcript.json.

By the AUDIO of the flat cut (audio.wav = public/input-video.mp4), never by Parakeet's word gaps (it stretches sentence ends):
a pause is a stretch with no 10 ms frame over SPEECH RMS between two stretches of speech. Every pause longer than --max
(joins and inner pauses alike, plus the section's head and tail) is listed with the words on both sides; with --plan the
script proposes the flat range to drop so the pause comes down to --target: the cut sits inside the quietest core of the
pause (frames under QUIET RMS), keeps the decay of the last word and the breath before the next one, and both new edges
land in room tone. --keep T leaves the pause that holds flat time T alone (a deliberate beat).
Then: patch-cut.py --drop-flat for each range -> edge-audit.py to 0 issues -> apply-cut -> re-transcribe -> this scan again."""
import argparse, json, os, sys, wave
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("folder"); ap.add_argument("--max", type=float, default=0.45); ap.add_argument("--target", type=float, default=0.30)
ap.add_argument("--max-sentence", type=float, default=0.40, help="the limit for a pause that follows a sentence end (. ? !)")
ap.add_argument("--speech", type=float, default=300.0); ap.add_argument("--quiet", type=float, default=80.0)
ap.add_argument("--head", type=float, default=0.12, help="lead-in kept before the first speech frame of the section")
ap.add_argument("--tail", type=float, default=0.15, help="tail kept after the last speech frame of the section (it meets the next section's head)")
ap.add_argument("--keep", type=float, action="append", default=[]); ap.add_argument("--plan", action="store_true")
ap.add_argument("--json", default="")
a = ap.parse_args()
D = os.path.abspath(a.folder); a.section = os.path.basename(D.rstrip("/"))
w = wave.open(os.path.join(D, "audio.wav")); FR = w.getframerate() // 100        # one RMS frame = 10 ms at any sample rate
x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float)
if w.getnchannels() > 1: x = x.reshape(-1, w.getnchannels()).mean(axis=1)
n = len(x) // FR; r = np.sqrt((x[: n * FR].reshape(n, FR) ** 2).mean(axis=1))
cm = json.load(open(os.path.join(D, "cut-map.json"))); cuts = cm["cuts"]; T = float(cm["flat_duration"])
W = json.load(open(os.path.join(D, "transcript.json"))); W = W["words"] if isinstance(W, dict) else W
sp = np.where(r > a.speech)[0]
word_before = lambda t: ([q["text"] for q in W if q["start"] < t] or ["(start)"])[-1]
word_after = lambda t: ([q["text"] for q in W if q["start"] >= t - 0.05] or ["(end)"])[0]

rows, plan = [], []
def core(i0, i1):
    """longest run of frames under QUIET inside [i0, i1)"""
    best, k = (i0, i0), i0
    while k < i1:
        if r[k] < a.quiet:
            j = k
            while j + 1 < i1 and r[j + 1] < a.quiet: j += 1
            if j + 1 - k > best[1] - best[0]: best = (k, j + 1)
            k = j + 1
        else:
            k += 1
    return best

# inner pauses
for p, q in zip(sp[:-1], sp[1:]):
    gap = (q - p - 1) / 100.0
    g0, g1 = (p + 1) / 100.0, q / 100.0
    if gap <= (a.max_sentence if word_before(g0).rstrip().endswith((".", "?", "!")) else a.max):
        continue
    at_join = [c for c in cuts if g0 - 0.05 <= c <= g1 + 0.05]
    kept = any(g0 - 0.05 <= k <= g1 + 0.05 for k in a.keep)
    row = {"from": round(g0, 2), "to": round(g1, 2), "gap": round(gap, 2), "join": [round(c, 3) for c in at_join],
           "before": word_before(g0), "after": word_after(g1), "keep": kept}
    if not kept:
        # the drop window: `want` long, at least KEEP_A after the last speech frame (the word's decay) and KEEP_B before the
        # next (the breath into it); both new edges in room tone; it may swallow a small blip (a lip click) on the way.
        # Among the windows that fit, the one whose edges are quietest, then the one nearest the middle of the pause.
        want = round(gap - a.target, 2); KEEP_A, KEEP_B = 0.10, 0.08
        lo, hi = int(round((g0 + KEEP_A) * 100)), int(round((g1 - KEEP_B - want) * 100))
        best = None
        for k0 in range(lo, hi + 1):
            k1 = k0 + int(round(want * 100))
            e = max(r[k0], r[k1])
            if e >= a.quiet:
                continue
            score = (round(e / 20.0), abs((k0 + k1) / 2.0 - (p + q) / 2.0))
            if best is None or score < best[0]:
                best = (score, k0, k1)
        if best:
            d0, d1 = round(best[1] / 100.0, 3), round(best[2] / 100.0, 3)
            row.update({"drop": [d0, d1], "after_gap": round(gap - (d1 - d0), 2), "edge_rms": [int(r[best[1]]), int(r[best[2]])],
                        "max_in_drop": int(r[best[1]:best[2]].max())})
            plan.append((d0, d1))
        else:
            row["note"] = "no quiet window of %.2f s with room-tone edges: a breath fills it" % want
    rows.append(row)

# head and tail of the section (they meet the next section at the assembly join)
head = sp[0] / 100.0; tail = (n - 1 - sp[-1]) / 100.0
edges = {"head": round(head, 2), "tail": round(tail, 2)}
if head > a.head + 0.15:
    plan.append((0.0, round(head - a.head, 3))); edges["head_drop"] = [0.0, round(head - a.head, 3)]
if tail > a.tail + 0.08:
    t0 = round((sp[-1] + 1) / 100.0 + a.tail, 3)
    c0, c1 = core(int(t0 * 100) - 1, n)
    if c1 - c0 > 5:
        t0 = max(t0, round(c0 / 100.0 + 0.04, 3))
    if T - t0 > 0.05:
        plan.append((t0, round(T, 3))); edges["tail_drop"] = [t0, round(T, 3)]

print("%s: flat %.3f s, %d joins, %d pauses over %.2f s (%.2f s after a sentence end; speech > %d RMS), head %.2f s, tail %.2f s"
      % (a.section, T, len(cuts), len(rows), a.max, a.max_sentence, a.speech, head, tail))
for row in rows:
    where = ("join %s" % ",".join("%.2f" % c for c in row["join"])) if row["join"] else "inside a segment"
    s = "  %6.2f-%6.2f  %.2f s  %-18s  %r -> %r" % (row["from"], row["to"], row["gap"], where, row["before"], row["after"])
    if row["keep"]:
        s += "   KEEP (deliberate beat)"
    elif "drop" in row:
        s += "   drop %.3f-%.3f -> %.2f s (edges %d / %d RMS, max inside %d)" % (row["drop"][0], row["drop"][1], row["after_gap"],
                                                                              row["edge_rms"][0], row["edge_rms"][1], row["max_in_drop"])
    elif "note" in row:
        s += "   " + row["note"]
    print(s)
if "head_drop" in edges: print("  head %.2f s: drop %.3f-%.3f" % (head, *edges["head_drop"]))
if "tail_drop" in edges: print("  tail %.2f s: drop %.3f-%.3f" % (tail, *edges["tail_drop"]))
if a.plan:
    print("PLAN " + " ".join("--drop-flat %.3f-%.3f" % ab for ab in sorted(plan)) if plan else "PLAN none")
if a.json:
    json.dump({"section": a.section, "rows": rows, "edges": edges, "plan": sorted(plan)}, open(a.json, "w"), indent=1)
