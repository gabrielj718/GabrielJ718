#!/usr/bin/env python3
"""verify-render.py: unattended checks on the RENDERED file, before it goes to the Renders folder.

The pre-render snapshot sheet cannot see render-only failures (a long render once painted the footage black for
long stretches and the sheet passed). This reads the encoded MP4 itself and writes VERIFY.md next to it:
  black       blackdetect pix_th=0.08 on a downscaled decode. Any black run is a FAIL: an interval of 0.1 s or more
              (the usual rule) and a shorter flash too (d=0.1 alone misses a 2-frame flash, 0.067 s at 30 fps)
  probe       width x height (--res, default 3840x2160); color_primaries / color_transfer / color_space all bt709;
              video bitrate >= 40 Mb/s at 4K (floor scaled by pixel count); video duration within one frame of the
              composition's data-duration (--index); video vs audio stream durations within 0.12 s
  sheet       render-sheet.png from the MP4 at the beat moments (first frame, every card-host data-start + 0.9 s,
              last frame), 4 columns at 480 px, each tile's time written on it when ffmpeg has drawtext
  words       with --words DELIVERED.json --kept FLAT.json: a transcript of the render's audio vs the flat-cut
              transcript (lowercase tokens, difflib). A word in the flat cut but not in the render was clipped at
              a join: FAIL. Words heard differently are listed, not failed.

Usage:
  python3 verify-render.py --render videos/<p>/output-4k.mp4 [--index videos/<p>/public/index.html] [--res 3840x2160]
                           [--words videos/<p>/delivered-transcript.json --kept videos/<p>/transcript.json] [--out VERIFY.md]
Exit 1 on any FAIL.
"""
import argparse, difflib, json, os, re, shutil, subprocess, sys, tempfile, time

ap = argparse.ArgumentParser()
ap.add_argument("--render", required=True)
ap.add_argument("--index", help="composition for data-duration and the beat moments (default: public/index.html next to the render)")
ap.add_argument("--res", default="3840x2160")
ap.add_argument("--min-mbps", type=float, default=40.0, help="video bitrate floor at 3840x2160, scaled by pixel count")
ap.add_argument("--words", help="word-level transcript of the RENDER's audio")
ap.add_argument("--kept", help="word-level transcript of the flat cut (transcript.json)")
ap.add_argument("--out", help="default: VERIFY.md next to the render")
args = ap.parse_args()
R = args.render
if not os.path.exists(R):
    sys.exit("no render at %s" % R)
out_md = args.out or os.path.join(os.path.dirname(os.path.abspath(R)), "VERIFY.md")
out_dir = os.path.dirname(os.path.abspath(out_md))
os.makedirs(out_dir, exist_ok=True)
index = args.index or os.path.join(os.path.dirname(os.path.abspath(R)), "public", "index.html")

def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None

checks, sections = [], []   # (name, ok, measured, expected)
def check(name, ok, measured, expected):
    checks.append((name, ok, measured, expected))

# ---- probe --------------------------------------------------------------------------------------------------
p = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
    "stream=codec_type,width,height,r_frame_rate,bit_rate,duration,color_primaries,color_transfer,color_space",
    "-show_entries", "format=duration,bit_rate,size", "-of", "json", R], capture_output=True, text=True, check=True).stdout)
v = next((s for s in p.get("streams", []) if s.get("codec_type") == "video"), None)
a = next((s for s in p.get("streams", []) if s.get("codec_type") == "audio"), None)
if v is None:
    sys.exit("no video stream in %s" % R)
n, d = [int(x) for x in v.get("r_frame_rate", "30/1").split("/")]
fps = n / d if d else 30.0
W, Hh = int(v.get("width", 0)), int(v.get("height", 0))
ew, eh = [int(x) for x in args.res.lower().split("x")]
check("Resolution", (W, Hh) == (ew, eh), "%dx%d" % (W, Hh), args.res)

tags = [v.get(k, "unknown") for k in ("color_primaries", "color_transfer", "color_space")]
check("Colour tags", all(t == "bt709" for t in tags), "primaries %s, transfer %s, space %s" % tuple(tags),
      "bt709 x3 (else run the step-8 remux)")

fmt = p.get("format", {})
vdur = num(v.get("duration")) or num(fmt.get("duration")) or 0.0
adur = num(a.get("duration")) if a else None
vbr = num(v.get("bit_rate"))
if vbr is None and num(fmt.get("size")) and vdur:     # no per-stream rate (some muxers): file rate minus the audio
    vbr = num(fmt["size"]) * 8 / vdur - ((num(a.get("bit_rate")) or 0) if a else 0)
floor = args.min_mbps * 1e6 * (W * Hh) / (3840 * 2160)
check("Video bitrate", vbr is not None and vbr >= floor, "%.1f Mb/s" % (vbr / 1e6) if vbr else "unknown", ">= %.1f Mb/s" % (floor / 1e6))

comp_d, hosts = None, []
if os.path.exists(index):
    html = open(index).read()
    root = re.search(r'<div[^>]*data-composition-id="[^"]+"[^>]*>', html)
    m = root and re.search(r'data-duration="([\d.]+)"', root.group(0))
    comp_d = float(m.group(1)) if m else None
    for m in re.finditer(r"<div\b([^>]*)>", html):
        at = m.group(1)
        c, s, i = re.search(r'\bclass="([^"]*)"', at), re.search(r'data-start="([\d.]+)"', at), re.search(r'\bid="([^"]+)"', at)
        if c and "card-host" in c.group(1).split() and s:
            hosts.append((float(s.group(1)), (i.group(1) if i else "?").replace("host-", "")))
frame = 1.0 / fps
if comp_d is not None:
    check("Duration", abs(vdur - comp_d) <= frame + 1e-6, "%.3f s" % vdur, "%.3f s +/- %.3f (data-duration)" % (comp_d, frame))
else:
    check("Duration", None, "%.3f s" % vdur, "no composition at %s: not checked" % index)
check("Video vs audio", adur is not None and abs(vdur - adur) <= 0.12,
      "%.3f / %s s" % (vdur, "%.3f" % adur if adur is not None else "no audio stream"), "within 0.12 s")

# ---- black frames ----------------------------------------------------------------------------------------------
r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", R, "-map", "0:v:0", "-vf",
                    "scale=320:-2,blackdetect=d=0:pix_th=0.08", "-an", "-f", "null", "-"], capture_output=True, text=True)
blacks = [(float(x), float(y), float(z)) for x, y, z in
          re.findall(r"black_start:\s*([\d.]+)\s+black_end:\s*([\d.]+)\s+black_duration:\s*([\d.]+)", r.stderr)]
check("Black frames", r.returncode == 0 and not blacks,
      "%d interval(s), %d flash(es)" % (sum(1 for b in blacks if b[2] >= 0.1 - 1e-6), sum(1 for b in blacks if b[2] < 0.1 - 1e-6))
      if r.returncode == 0 else "blackdetect failed", "none (pix_th 0.08; d 0.1 plus shorter flashes)")
if blacks:
    sections.append(["## Black frames", ""] + ["- %.3f - %.3f s (%.3f s, %d frame%s): %s" % (
        s, e, dd, max(1, round(dd * fps)), "" if max(1, round(dd * fps)) == 1 else "s", "black interval" if dd >= 0.1 - 1e-6 else "flash")
        for s, e, dd in blacks] + ["", "Look at those frames in the MP4. A long 4K render painted black means the parallel"
                                   " stream encode (Traps: --workers 1)."])

# ---- frame sheet at the beat moments -------------------------------------------------------------------------
last = max(0.0, vdur - 1.5 * frame)
moments = [(0.0, "first")] + [(min(t + 0.9, last), gid) for t, gid in sorted(hosts)] + [(last, "last")]
seen, uniq = set(), []
for t, lab in moments:
    if round(t, 2) not in seen:
        seen.add(round(t, 2)); uniq.append((t, lab))
tmp = tempfile.mkdtemp(prefix="verify-render-")
has_text = "Unknown filter" not in subprocess.run(["ffmpeg", "-hide_banner", "-h", "filter=drawtext"], capture_output=True, text=True).stdout

def grab(t, dst, label):
    """One frame at t, 480 px wide, its time drawn on it when drawtext works (fonts can be missing: fall back)."""
    global has_text
    run = lambda vf: subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "%.3f" % t, "-i", R, "-frames:v", "1", "-vf", vf, dst],
                                    capture_output=True).returncode == 0 and os.path.exists(dst)
    if has_text:
        txt = re.sub(r"[^A-Za-z0-9 ._-]", "", "%.2fs %s" % (t, label))
        if run("scale=480:-2,drawtext=text='%s':x=12:y=10:fontsize=24:fontcolor=white:box=1:boxcolor=black@0.6:boxborderw=6" % txt):
            return True
        has_text = False
    return run("scale=480:-2")

got = 0
for t, lab in uniq:
    got += grab(t, os.path.join(tmp, "f_%03d.png" % got), lab)
sheet = os.path.join(out_dir, "render-sheet.png")
if got:
    rows = (got + 3) // 4
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-start_number", "0", "-i", os.path.join(tmp, "f_%03d.png"),
                    "-vf", "tile=4x%d" % rows, "-frames:v", "1", sheet], check=True)
shutil.rmtree(tmp, ignore_errors=True)
sections.append(["## Frame sheet", "", "`%s`: %d frame(s)%s, read it before delivering: first frame, every card at data-start + 0.9 s, last frame."
                 % (os.path.basename(sheet), got, "" if has_text else " (no drawtext in this ffmpeg: times listed here, not on the tiles)"),
                 "", " ".join("%.2f" % t for t, _ in uniq)])

# ---- clipped words -----------------------------------------------------------------------------------------------
if args.words and args.kept:
    FILL = {"um", "uh", "er", "ah", "hmm", "mm"}
    def load(path):
        raw = json.load(open(path)); ws = raw["words"] if isinstance(raw, dict) and "words" in raw else raw
        out = []
        for w in ws:
            for tok in re.sub(r"[^a-z0-9' ]+", " ", str(w.get("text", w.get("word", ""))).lower()).split():
                if tok not in FILL:
                    out.append((tok, float(w["start"])))
        return out
    K, D = load(args.kept), load(args.words)
    missing, differ = [], []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, [k for k, _ in K], [k for k, _ in D], autojunk=False).get_opcodes():
        if op == "delete":
            missing.append((K[i1][1], " ".join(k for k, _ in K[i1:i2]), " ".join(k for k, _ in K[max(0, i1 - 3):i1])))
        elif op == "replace":
            differ.append((K[i1][1], " ".join(k for k, _ in K[i1:i2]), " ".join(k for k, _ in D[j1:j2])))
    check("Clipped words", not missing, "%d missing of %d" % (sum(len(m[1].split()) for m in missing), len(K)), "none")
    sec = ["## Clipped words", ""]
    sec += ["- %.2f s: **%s** (after \"%s\"): missing from the render, clipped at a join?" % m for m in missing] or ["None missing."]
    if differ:
        sec += ["", "Heard differently (ASR noise or a clipped syllable; listen if it sits on a join):", ""]
        sec += ["- %.2f s: flat \"%s\" / render \"%s\"" % d for d in differ[:40]]
    sections.append(sec)
elif args.words or args.kept:
    check("Clipped words", None, "needs both --words and --kept", "not checked")

# ---- report ----------------------------------------------------------------------------------------------------
fails = [c for c in checks if c[1] is False]
lines = ["# Render check: %s" % os.path.basename(R), "",
         "**%s**  (%s)" % ("PASS" if not fails else "FAIL: " + ", ".join(c[0] for c in fails), time.strftime("%Y-%m-%d %H:%M")), "",
         "| Check | Result | Measured | Expected |", "|---|---|---|---|"]
lines += ["| %s | %s | %s | %s |" % (nm, {True: "PASS", False: "FAIL", None: "skip"}[ok], me, ex) for nm, ok, me, ex in checks]
for sec in sections:
    lines += [""] + sec
open(out_md, "w").write("\n".join(lines) + "\n")
for nm, ok, me, ex in checks:
    print("%-15s %-5s %s  (expected %s)" % (nm, {True: "PASS", False: "FAIL", None: "skip"}[ok], me, ex))
for s, e, dd in blacks:
    print("  black %.3f - %.3f s (%.3f s)" % (s, e, dd))
print("%s -> %s%s" % ("PASS" if not fails else "FAIL", out_md, ", " + sheet if got else ""))
sys.exit(1 if fails else 0)
