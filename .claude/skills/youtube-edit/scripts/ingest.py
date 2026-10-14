#!/usr/bin/env python3
"""ingest.py: probe every clip in a raw/ folder, put them in order, and optionally join the talking-head
clips into one source file for a long-form edit.

Usage:
  python3 ingest.py --raw videos/<project>/raw --out videos/<project>            # probe + ingest.json only
  python3 ingest.py --raw videos/<project>/raw --out videos/<project> --concat   # also write source.mp4
  python3 ingest.py ... --order C0002,C0001                                       # explicit order (basenames, no ext)
  python3 ingest.py ... --only C0001,C0003                                        # subset

Order: --order if given, else filename order (Sony C0xxx numbers are sequential), else recording time.
Concat: ffmpeg concat demuxer with stream copy when every clip shares codec, size, fps and audio layout
(no quality loss); any odd clip is re-encoded to match first. Writes ingest.json with the offsets so a
timestamp in source.mp4 can always be mapped back to (clip, time).
Screen recordings and other non-talking-head files can live in the same raw/ folder: pass --only to
pick the camera clips, or they are skipped automatically when their resolution differs.
"""
import argparse, json, os, subprocess, sys, glob

ap = argparse.ArgumentParser()
ap.add_argument("--raw", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--concat", action="store_true")
ap.add_argument("--order", default="")
ap.add_argument("--only", default="")
ap.add_argument("--name", default="source.mp4")
args = ap.parse_args()

VIDEO_EXT = (".mp4", ".mov", ".mxf", ".m4v")

def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels,pix_fmt",
                          "-show_entries", "format=duration,size", "-of", "json", path],
                         capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    v = next((s for s in j["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in j["streams"] if s["codec_type"] == "audio"), None)
    num, den = (v["r_frame_rate"].split("/") + ["1"])[:2]
    return {
        "file": os.path.basename(path), "path": os.path.abspath(path),
        "duration": float(j["format"]["duration"]), "size": int(j["format"]["size"]),
        "width": v["width"], "height": v["height"], "fps": round(int(num) / int(den), 3),
        "vcodec": v["codec_name"], "pix_fmt": v.get("pix_fmt"),
        "acodec": a["codec_name"] if a else None, "sample_rate": int(a["sample_rate"]) if a else None,
        "channels": a["channels"] if a else 0,
        "mtime": os.path.getmtime(path),
    }

files = [f for f in glob.glob(os.path.join(args.raw, "*")) if f.lower().endswith(VIDEO_EXT)]
if not files:
    sys.exit("no video files in %s" % args.raw)
clips = [probe(f) for f in files]
stem = lambda c: os.path.splitext(c["file"])[0]

if args.only:
    keep = set(args.only.split(","))
    clips = [c for c in clips if stem(c) in keep]
if args.order:
    order = args.order.split(",")
    by = {stem(c): c for c in clips}
    missing = [o for o in order if o not in by]
    if missing:
        sys.exit("--order names not found in raw/: %s" % ", ".join(missing))
    clips = [by[o] for o in order]
else:
    clips.sort(key=lambda c: (c["file"].lower(), c["mtime"]))

# Talking-head clips are the majority resolution; anything else (a screen recording) is set aside.
if clips:
    from collections import Counter
    common = Counter((c["width"], c["height"]) for c in clips).most_common(1)[0][0]
    side = [c for c in clips if (c["width"], c["height"]) != common]
    clips = [c for c in clips if (c["width"], c["height"]) == common]
else:
    side = []

t = 0.0
for c in clips:
    c["source_start"] = round(t, 3)
    t += c["duration"]
    c["source_end"] = round(t, 3)

ingest = {"raw_dir": os.path.abspath(args.raw), "clips": clips, "set_aside": side,
          "total_duration": round(t, 3), "concat": None}
os.makedirs(args.out, exist_ok=True)

if args.concat and clips:
    ref = clips[0]
    same = all((c["vcodec"], c["width"], c["height"], c["fps"], c["acodec"], c["sample_rate"], c["channels"]) ==
               (ref["vcodec"], ref["width"], ref["height"], ref["fps"], ref["acodec"], ref["sample_rate"], ref["channels"])
               for c in clips)
    parts = []
    for c in clips:
        p = c["path"]
        if not same:
            fixed = os.path.join(args.out, "raw-normalised-%s.mp4" % stem(c))
            if not os.path.exists(fixed):
                subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", p, "-vf", "scale=%d:%d" % (ref["width"], ref["height"]),
                                "-r", str(ref["fps"]), "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-pix_fmt", "yuv420p",
                                "-c:a", "aac", "-b:a", "256k", "-ar", "48000", fixed], check=True)
            p = fixed
        parts.append(p)
    listfile = os.path.join(args.out, "concat-list.txt")
    with open(listfile, "w") as fh:
        for p in parts:
            fh.write("file '%s'\n" % p.replace("'", "'\\''"))
    out = os.path.join(args.out, args.name)
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", listfile]
    cmd += ["-c", "copy"] if same else ["-c:v", "libx264", "-crf", "16", "-preset", "fast", "-c:a", "aac", "-b:a", "256k"]
    cmd += ["-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    ingest["concat"] = {"file": out, "stream_copy": same}

json.dump(ingest, open(os.path.join(args.out, "ingest.json"), "w"), indent=1)
print("%d clip(s), %.1fs total%s" % (len(clips), t, ", set aside: %s" % ", ".join(c["file"] for c in side) if side else ""))
for c in clips:
    print("  %-14s %7.1fs  %dx%d %.3ffps  starts at %8.3f" % (c["file"], c["duration"], c["width"], c["height"], c["fps"], c["source_start"]))
if ingest["concat"]:
    print("-> %s (%s)" % (ingest["concat"]["file"], "stream copy" if same else "re-encoded"))
