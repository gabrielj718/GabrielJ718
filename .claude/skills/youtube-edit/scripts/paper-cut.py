#!/usr/bin/env python3
"""paper-cut.py: decide what to remove from a raw talking-head recording.

Input : a word-level transcript JSON (Parakeet / whisper: [{text,start,end}] or {"words":[...]})
Output: cut-list.json  {source_duration, kept_seconds, kept:[{start,end}], removed:[{start,end,reason,text}]}
        PAPER-CUT.md   the transcript with removed stretches struck through + a reason each

Passes, in order:
  1. restarts inside a sentence   "Today chat, today ChatGPT made the, today ChatGPT made the craziest..." -> keep the last start
  2. explicit markers             "cut that", "scratch that", "let me redo", "start over", "take two", a lone "again"
                                  -> remove the marker sentence AND the sentence before it (the flub)
  3. retakes / alternates         a sentence that comes back within the next WINDOW sentences (similar wording, or the
                                  same short beat with the same key words) -> keep the LAST take, drop everything between.
                                  Exception: if the last take only adds a leading filler ("so", "okay", "and"), keep the
                                  clean earlier take instead.
  4. false starts                 a fragment of <= 5 words whose first 2 words open the next sentence -> drop the fragment
  5. silence                      gaps between kept words longer than GAP are trimmed to BEFORE s ahead of speech and
                                  AFTER s behind it; head and tail trimmed too

Usage:
  python3 paper-cut.py --transcript transcript.json --duration 187.19 --out-dir videos/proj
"""
import argparse, json, re, difflib, os

ap = argparse.ArgumentParser()
ap.add_argument("--transcript", required=True)
ap.add_argument("--duration", type=float, required=True)
ap.add_argument("--out-dir", required=True)
ap.add_argument("--sim", type=float, default=0.62)
ap.add_argument("--window", type=int, default=6)
ap.add_argument("--gap", type=float, default=0.60)
ap.add_argument("--before", type=float, default=0.15)
ap.add_argument("--after", type=float, default=0.45)
ap.add_argument("--head", type=float, default=0.25)
ap.add_argument("--tail", type=float, default=0.60)
ap.add_argument("--speech", help="auto-editor v1 JSON (audio-based speech chunks). When given, segment ends come from the audio, not the transcript, because ASR word ends stretch into pauses.")
args = ap.parse_args()

raw = json.load(open(args.transcript))
words = raw["words"] if isinstance(raw, dict) and "words" in raw else raw
words = [{"text": w["text"], "start": float(w["start"]), "end": float(w["end"])} for w in words]

STOP = set("the a an is are it it's to of in on and so if be at as for with my me i i'm i'll you you're your we that um uh".split())
FILLERS = ("so", "okay", "ok", "and", "yeah", "um", "uh", "alright")

def norm(t): return re.sub(r"[^a-z0-9' ]+", " ", t.lower()).split()
def content(tokens): return [t for t in tokens if t not in STOP]
def ratio(a, b): return difflib.SequenceMatcher(None, a, b).ratio() if a and b else 0.0
def jaccard(a, b):
    A, B = set(a), set(b)
    return len(A & B) / len(A | B) if A | B else 0.0

# ---- sentences (terminal punctuation or a pause > 0.9 s) ----
sentences, cur = [], []
for i, w in enumerate(words):
    cur.append(i)
    terminal = re.search(r"[.?!]$", w["text"]) is not None
    long_gap = i + 1 < len(words) and words[i + 1]["start"] - w["end"] > 0.9
    if terminal or long_gap:
        sentences.append(cur); cur = []
if cur: sentences.append(cur)

removed = []
S = []
for idx in sentences:
    toks = [norm(words[i]["text"]) for i in idx]
    toks = [t[0] if t else "" for t in toks]
    # 1. restarts inside the sentence: for a word at i, find the LAST later j (<= 12 words on) that repeats it with a
    #    similar following word; everything from i to j-1 is a restart. Scan left to right, jump to j.
    #    Only the restart itself (words i..j-1) is dropped; words before i stay (a restart can sit mid-sentence).
    #    A repeated function word ("that ... and that you") only counts when the two words after it match too.
    drop = set()
    i = 0
    while i < len(idx) - 1:
        best = None
        if toks[i]:
            for j in range(i + 1, min(i + 13, len(idx))):
                if toks[j] != toks[i]: continue
                nxt_i = toks[i + 1] if i + 1 < len(idx) else ""
                nxt_j = toks[j + 1] if j + 1 < len(idx) else ""
                if not (nxt_i and nxt_j and (nxt_i == nxt_j or ratio(nxt_i, nxt_j) >= 0.6)): continue
                if toks[i] in STOP and j - i > 4:   # a long stretch opened by a function word needs a third matching word
                    nn_i = toks[i + 2] if i + 2 < len(idx) else ""
                    nn_j = toks[j + 2] if j + 2 < len(idx) else ""
                    if not (nn_i and nn_j and (nn_i == nn_j or ratio(nn_i, nn_j) >= 0.6)): continue
                best = j
        if best is not None:
            removed.append({"start": round(words[idx[i]]["start"], 3), "end": round(words[idx[best]]["start"], 3),
                            "reason": "restart", "text": " ".join(words[k]["text"] for k in idx[i:best])})
            drop.update(idx[i:best]); i = best
        else:
            i += 1
    kept = [k for k in idx if k not in drop]
    #    Rapid retakes that the transcriber merged into one "sentence" leave a stutter behind even after the restarts
    #    go (one word said 3+ times in a short stretch). Then the old rule applies: keep from the last restart on.
    if drop:
        kt = [toks[idx.index(k)] for k in kept if toks[idx.index(k)]]
        top = max((kt.count(t) for t in set(kt)), default=0)
        if top >= 3 and top / max(1, len(kt)) >= 0.25:
            kept = idx[max(idx.index(k) for k in drop) + 1:]
    text = " ".join(words[k]["text"] for k in kept)
    S.append({"idx": kept, "text": text, "tokens": norm(text), "start": words[kept[0]]["start"],
              "end": words[kept[-1]]["end"], "remove": None})

MARKERS = [r"\bcut that\b", r"\bscratch that\b", r"\blet me (redo|do that again|start (over|again)|try (that )?again)\b",
           r"\bstart over\b", r"\btake two\b", r"\bone more time\b"]
# 2. explicit markers
for k, s in enumerate(S):
    t = " ".join(s["tokens"])
    if any(re.search(m, t) for m in MARKERS) or s["tokens"] in (["again"], ["okay", "again"], ["ok", "again"]):
        s["remove"] = "marker: \"%s\"" % s["text"]
        if k > 0 and S[k - 1]["remove"] is None:
            S[k - 1]["remove"] = "flub before \"%s\"" % s["text"]

# 3. retakes / alternates of the same beat: keep the last
def is_retake(a, b):
    if ratio(a["tokens"], b["tokens"]) >= args.sim: return True
    if a["tokens"][:3] == b["tokens"][:3] and len(b["tokens"]) >= 0.6 * len(a["tokens"]): return True
    ca, cb = content(a["tokens"]), content(b["tokens"])
    if len(a["tokens"]) <= 14 and len(b["tokens"]) <= 14 and ca and cb:
        j = jaccard(ca, cb)
        if j >= 0.4: return True
        if ca[-1] == cb[-1] and j >= 0.2: return True
    return False

for k, s in enumerate(S):
    if s["remove"] or len(s["tokens"]) < 2: continue
    for j in range(k + 1, min(k + 1 + args.window, len(S))):
        later = S[j]
        if later["remove"] or len(later["tokens"]) < 2: continue
        if is_retake(s, later):
            # exception: the later take is just the earlier one with a leading filler -> keep the clean one
            if later["tokens"][0] in FILLERS and later["tokens"][1:] == s["tokens"]:
                later["remove"] = "retake (only adds a leading filler; kept the clean take at %.1fs)" % s["start"]
                continue
            for m in range(k, j):
                if S[m]["remove"] is None:
                    S[m]["remove"] = "retake (kept the later take at %.1fs)" % later["start"]
            break

# 4. false starts
for k in range(len(S) - 1):
    s, nxt = S[k], S[k + 1]
    if s["remove"] or nxt["remove"]: continue
    if len(s["tokens"]) <= 5 and len(nxt["tokens"]) >= 4 and s["tokens"][:2] == nxt["tokens"][:2]:
        s["remove"] = "false start"

# ---- kept words -> segments with silence trimming ----
# Kept words are grouped into RUNS: consecutive kept words of one sentence. A run ends where dropped words (a
# mid-sentence restart) follow it, and that run's audio is clamped at the first dropped word, so the restart is
# really cut out of the sound, not only struck from the text (not only a restart at the head of a sentence).
kept_words = [words[i] for s in S if not s["remove"] for i in s["idx"]]
removed += [{"start": round(s["start"], 3), "end": round(s["end"], 3), "reason": s["remove"], "text": s["text"]}
            for s in S if s["remove"]]
runs = []
for s in S:
    if s["remove"]: continue
    run = []
    for k in s["idx"]:
        if run and k != run[-1] + 1:
            if len(run) > 2:   # a one- or two-word head before a restart ("or", "so the") folds into the restart
                runs.append({"idx": run, "clamp": words[run[-1] + 1]["start"]})
            run = []
        run.append(k)
    if run: runs.append({"idx": run, "clamp": None})
segments = []
if args.speech and kept_words:
    d = json.load(open(args.speech)); num, den = [int(x) for x in str(d.get("timebase", "30/1")).split("/")]; fps = num / den
    chunks = [(a / fps, b / fps) for a, b, sp in d["chunks"] if sp not in (99999, 0)]
    # speech chunks overlapping each run [first word start, last word start]; starts trust the ASR, ends trust the audio
    for r in runs:
        w0, w1 = words[r["idx"][0]]["start"], words[r["idx"][-1]]["start"]
        wend = words[r["idx"][-1]]["end"]
        hit = [c for c in chunks if c[1] > w0 - 0.3 and c[0] < w1 + 0.2]
        if not hit:
            segments.append({"start": w0 - args.before, "end": min(wend + args.after, r["clamp"] or 1e9)}); continue
        for n, (a, b) in enumerate(hit):
            st = (w0 - args.before) if n == 0 else a   # first chunk: start on the ASR word, so a restart sharing the chunk is cut
            en = b if r["clamp"] is None or n < len(hit) - 1 else min(b, r["clamp"] - 0.02)
            if en > st: segments.append({"start": st, "end": en})
    for i in range(1, len(segments)):
        g = segments[i]["start"] - segments[i - 1]["end"]
        if g > 0.05:
            removed.append({"start": round(segments[i - 1]["end"], 3), "end": round(segments[i]["start"], 3), "reason": "silence %.1fs" % g, "text": ""})
elif kept_words:
    for r in runs:
        rw = [words[k] for k in r["idx"]]
        seg_start = max(0.0, rw[0]["start"] - args.head if not segments else rw[0]["start"] - args.before)
        prev_end = rw[0]["end"]
        for w in rw[1:]:
            gap = w["start"] - prev_end
            if gap > args.gap:
                segments.append({"start": seg_start, "end": prev_end + args.after})
                removed.append({"start": round(prev_end + args.after, 3), "end": round(w["start"] - args.before, 3),
                                "reason": "silence %.1fs" % gap, "text": ""})
                seg_start = w["start"] - args.before
            prev_end = max(prev_end, w["end"])
        end = min(args.duration, prev_end + (args.tail if r is runs[-1] else args.after))
        if r["clamp"] is not None: end = min(end, r["clamp"] - 0.02)
        segments.append({"start": seg_start, "end": end})
merged = []
for seg in segments:
    seg = {"start": max(0.0, seg["start"]), "end": min(args.duration, seg["end"])}
    if seg["end"] - seg["start"] < 0.2: continue
    if merged and seg["start"] - merged[-1]["end"] < 0.12: merged[-1]["end"] = seg["end"]
    else: merged.append(seg)
segments = [{"start": round(s["start"], 3), "end": round(s["end"], 3)} for s in merged]
kept_total = sum(s["end"] - s["start"] for s in segments)
removed.sort(key=lambda r: r["start"])

os.makedirs(args.out_dir, exist_ok=True)
json.dump({"source_duration": args.duration, "kept_seconds": round(kept_total, 2), "kept": segments, "removed": removed},
          open(os.path.join(args.out_dir, "cut-list.json"), "w"), indent=1)

lines = ["# Paper cut", "", "Raw %.1fs -> kept %.1fs (%d segments). Struck-through = removed, reason in brackets." %
         (args.duration, kept_total, len(segments)), ""]
restarts = {r["start"]: r for r in removed if r["reason"] == "restart"}
for s in S:
    pre = [r for r in restarts.values() if abs(r["end"] - s["start"]) < 0.02]
    for r in pre:
        lines.append("%6.2f  ~~%s~~  [restart]" % (r["start"], r["text"]))
    stamp = "%6.2f" % s["start"]
    lines.append("%s  ~~%s~~  [%s]" % (stamp, s["text"], s["remove"]) if s["remove"] else "%s  %s" % (stamp, s["text"]))
sil = [r for r in removed if r["reason"].startswith("silence")]
if sil: lines += ["", "Silence trimmed: %d gaps, %.1fs total." % (len(sil), sum(r["end"] - r["start"] for r in sil))]
open(os.path.join(args.out_dir, "PAPER-CUT.md"), "w").write("\n".join(lines) + "\n")
print("kept %.1fs of %.1fs in %d segments; %d sentences removed; %d restarts; %d silences trimmed" %
      (kept_total, args.duration, len(segments), sum(1 for s in S if s["remove"]), len(restarts), len(sil)))
