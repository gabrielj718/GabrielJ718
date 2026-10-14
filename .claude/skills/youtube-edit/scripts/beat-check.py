#!/usr/bin/env python3
"""beat-check.py: transcript-sync gate for our compositions (Gate 0: every card lands on its spoken word).

Every card-host / cutaway that carries data-anchor="exact spoken phrase" is checked against transcript.json:
the element must enter between --late seconds AFTER the anchor word (default 0.10) and --early seconds
BEFORE it (default 0.60). Our entrances are 0.4 s, so a data-start ~0.25 s before the word lands the card
exactly as the word is spoken. Run after authoring and after every retime; a miss here is a card on the wrong word.

Also FAILS on:
  NO-ANCHOR  a card-host div or a cutaway <video> (any video but bg-video / fg-matte) with no data-anchor.
             Mark a deliberate one (a chapter tag at 0.2 s, a vignette) with data-unanchored.
  items      any element with data-at="T" and data-anchor (list / bullet items) is checked with T as its entry.
  stale      transcript.json older than the video (default input-video.mp4 next to the index, --video to point
             elsewhere): the words are from another cut. Re-transcribe the flat cut, or --allow-stale.

Usage:
  python3 beat-check.py --index videos/<p>/public/index.html --transcript videos/<p>/transcript.json [--suggest]
Exit 1 on any EARLY / LATE / MISS / NO-ANCHOR or a stale transcript.
"""
import argparse, html as H, json, os, re, sys

ap = argparse.ArgumentParser()
ap.add_argument("--index", required=True)
ap.add_argument("--transcript", required=True)
ap.add_argument("--video", help="the video the transcript must be newer than (default: input-video.mp4 next to the index)")
ap.add_argument("--allow-stale", action="store_true")
ap.add_argument("--early", type=float, default=0.60)
ap.add_argument("--late", type=float, default=0.10)
ap.add_argument("--lead", type=float, default=0.25, help="target lead for --suggest")
ap.add_argument("--suggest", action="store_true")
args = ap.parse_args()

raw = json.load(open(args.transcript))
words = raw["words"] if isinstance(raw, dict) and "words" in raw else raw
norm = lambda s: re.sub(r"[^a-z0-9' ]+", " ", s.lower()).split()
toks = [(norm(w["text"]), float(w["start"])) for w in words]
flat = [(tok, st) for ts, st in toks for tok in ts]

def find(phrase, near):
    p = norm(phrase)
    if not p:
        return None
    best = None
    for i in range(len(flat) - len(p) + 1):
        if [flat[i + k][0] for k in range(len(p))] == p:
            st = flat[i][1]
            if best is None or abs(st - near) < abs(best - near):
                best = st
    return best

def spoken_at(t, n=3):   # the words spoken just after t: a candidate anchor for --suggest
    i = next((i for i, (_, st) in enumerate(flat) if st >= t), None)
    return " ".join(tok for tok, _ in flat[i:i + n]) if i is not None else ""

attr = lambda attrs, name: (lambda m: H.unescape(m.group(1)) if m else None)(re.search(r'\b%s="([^"]*)"' % name, attrs))

bad = 0
video = args.video or os.path.join(os.path.dirname(os.path.abspath(args.index)), "input-video.mp4")
stale = None
if os.path.exists(video):
    if os.path.getmtime(args.transcript) < os.path.getmtime(video):
        stale = "FAIL transcript is older than the video: re-transcribe the flat cut (%s < %s)" % (
            os.path.basename(args.transcript), os.path.basename(video))
        if args.allow_stale:
            stale = stale.replace("FAIL", "WARN", 1) + "  [--allow-stale]"
        else:
            bad += 1
else:
    stale = "(no video at %s: staleness not checked)" % video

src = open(args.index).read()
rows = []   # (id, entry, anchor, word, slack, status, key)
for m in re.finditer(r"<(div|video)\b([^>]*)>", src):
    tag, attrs = m.group(1), m.group(2)
    gid = attr(attrs, "id") or "?"
    anc, at, st = attr(attrs, "data-anchor"), attr(attrs, "data-at"), attr(attrs, "data-start")
    cls = (attr(attrs, "class") or "").split()
    key = "data-at" if at is not None else "data-start"
    entry = at if at is not None else st
    try:
        entry = float(entry) if entry is not None else None
    except ValueError:
        entry = None
    if anc is None:
        cutaway = tag == "video" and gid not in ("bg-video", "fg-matte")
        if ("card-host" in cls or cutaway) and "data-unanchored" not in attrs:
            rows.append((gid, entry, "", None, None, "NO-ANCHOR", key)); bad += 1
        continue
    if entry is None:
        continue
    ws = find(anc, entry)
    if ws is None:
        rows.append((gid, entry, anc, None, None, "MISS", key)); bad += 1; continue
    slack = ws - entry
    status = "OK"
    if slack < -args.late:
        status = "LATE"; bad += 1
    elif slack > args.early:
        status = "EARLY"; bad += 1
    rows.append((gid, entry, anc, ws, slack, status, key))

if stale:
    print(stale + "\n")
print("%-22s %8s %8s %7s  %-9s %s" % ("id", "start", "word", "slack", "status", "anchor"))
for gid, entry, anc, ws, slack, status, key in rows:
    print("%-22s %8s %8s %7s  %-9s %s" % (gid, ("%.2f" % entry if entry is not None else "-") + ("@" if key == "data-at" else " "),
                                          "%.2f" % ws if ws is not None else "-",
                                          "%+.2f" % slack if slack is not None else "-", status, anc[:40]))
if args.suggest:
    print("\nsuggested (word - %.2f; @ = a data-at item):" % args.lead)
    for gid, entry, anc, ws, slack, status, key in rows:
        if ws is not None:
            print('  %-22s %s="%.2f"' % (gid, key, max(0.0, ws - args.lead)))
        elif status == "NO-ANCHOR" and entry is not None:
            said = spoken_at(entry)
            print('  %-22s %s' % (gid, 'data-anchor="%s"  (spoken as it enters; or mark it data-unanchored)' % said if said
                                   else "nothing is said after it: mark it data-unanchored"))
print("\n%d checked, %d problem(s)" % (len(rows), bad))
sys.exit(1 if bad else 0)
