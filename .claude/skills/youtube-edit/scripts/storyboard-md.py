#!/usr/bin/env python3
"""storyboard-md.py: render the delivery STORYBOARD.md (time / beat / what is on screen) from one or more
storyboard.json files, so the review document is generated from the same source the composition is built from.

Usage: python3 storyboard-md.py --title "Hook v2" --note "what changed" --project videos/<p>/C0001:01-hook:"Part 1" ... --out videos/<p>/STORYBOARD.md
"""
import argparse, json, os

ap = argparse.ArgumentParser()
ap.add_argument("--title", required=True)
ap.add_argument("--note", action="append", default=[])
ap.add_argument("--concern", action="append", default=[])
ap.add_argument("--project", action="append", required=True, help="<dir>:<slug>:<title>")
ap.add_argument("--out", required=True)
args = ap.parse_args()

WHAT = {"line": lambda b: "lower line (%s%s)" % (b.get("color", "cyan"), ", shimmer" if b.get("shimmer") else ""),
        "logo": lambda b: "logo card + pop", "list": lambda b: "glass list card", "bullets": lambda b: "pushed-over bullets",
        "chip": lambda b: "punchline chip", "vignette": lambda b: "vignette + grain (deadpan)", "pointer": lambda b: "description pointer",
        "site": lambda b: "full-screen site cutaway (%s)" % b.get("domain", ""), "grid": lambda b: "thumbnail grid + cursor click",
        "scene": lambda b: "animated scene: %s" % b.get("kind", "")}
def text_of(b):
    if b.get("text"): return b["text"]
    if b.get("label"): return b["label"]
    if b.get("items"): return ((b.get("eyebrow") + ": ") if b.get("eyebrow") else "") + ", ".join(i[0] for i in b["items"])
    if b.get("images"): return "%d of the channel's own thumbnails, click on tile %d" % (len(b["images"]), int(b.get("click_index", 0)) + 1)
    if b.get("src"): return os.path.basename(b["src"])
    return ""

out = ["# " + args.title, ""]
if args.note:
    out += ["## What changed", ""] + ["- " + n for n in args.note] + [""]
if args.concern:
    out += ["## Concerns to check", ""] + ["- " + c for c in args.concern] + [""]
for spec in args.project:
    d, slug, title = spec.split(":", 2)
    s = json.load(open(os.path.join(d, "storyboard.json")))
    out += ["## %s: %s (%s, %.1f s)" % (slug, title, s["id"], float(s["duration"])), "", "| Time | Beat | On screen |", "|---|---|---|"]
    if s.get("tag"):
        t = s["tag"]; out.append("| %.1f - %.1f | progress tag | %d of %d · %s |" % (t["in"], t["out"], t["n"], t["of"], t["label"]))
    for b in s.get("beats", []):
        tr = (" · " + b["transition"] + " cut") if b.get("transition") else ""
        out.append("| %.1f - %.1f | %s%s | %s |" % (b["in"], b["out"], WHAT.get(b["type"], lambda b: b["type"])(b), tr, text_of(b)))
    moves = [op for op in s.get("camera", []) if op[0] != "set"]
    out.append("| camera | %d moves | %s |" % (len(moves), ", ".join("%s %.1f" % (op[0], float(op[1])) for op in moves)))
    out.append("")
open(args.out, "w").write("\n".join(out))
print("wrote", args.out, len(out), "lines")
