#!/usr/bin/env python3
"""broll-conform.py: turn one AI b-roll result (a generated clip, or a still) into a cutaway the composer can use.

Generated clips arrive at 720p / 1080p, 24 fps, often with sound, in whatever colour the model liked. Format 20's rules
want 30 fps, dense keyframes (a clip that seeks badly freezes in the render), no audio, BT.709 tags. A still (a Nano Banana
frame, when a video generation is not worth the credits) becomes a slow push-in of the same length.

Usage:
  python3 broll-conform.py --in gen/desk.mp4 --out videos/<p>/public/broll/desk.mp4 [--start 0.4] [--dur 4] [--grade]
  python3 broll-conform.py --in gen/desk.png --out videos/<p>/public/broll/desk.mp4 --dur 4 [--push 1.08]
  add --4k to write 3840x2160 (the composition is 1920x1080 and renders at 2x, so 1080p is the default; 4K stock
  keeps its detail only with --4k)
  add --vf "<ffmpeg filters>" to clean a stock clip first, in source pixels: crop a readable logo out
  ("crop=3490:1964:175:0") or soften a browser bar ("split[a][b];[b]crop=1480:170:1080:600,boxblur=18[bb];[a][bb]overlay=1080:600")
Writes the clip, <out>.sheet.png (first, middle, last frame) and prints the storyboard beat to paste.
"""
import argparse, json, os, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument("--in", dest="src", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--start", type=float, default=0.0, help="seconds into the generated clip (skip the model's settle-in)")
ap.add_argument("--dur", type=float, help="seconds to keep (default: the rest of the clip; required for a still)")
ap.add_argument("--push", type=float, default=1.08, help="still only: end scale of the push-in (1.00 = none)")
ap.add_argument("--grade", action="store_true", help="a light grade toward camera footage: contrast +3%%, saturation -8%%")
ap.add_argument("--4k", dest="uhd", action="store_true")
ap.add_argument("--vf", default="", help="ffmpeg filters applied first, in source pixels (crop a logo out, blur a browser bar)")
args = ap.parse_args()

W, H = (3840, 2160) if args.uhd else (1920, 1080)
still = os.path.splitext(args.src)[1].lower() in (".png", ".jpg", ".jpeg", ".webp")
if still and not args.dur:
    sys.exit("a still needs --dur (seconds of push-in)")


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate:format=duration",
                        "-of", "json", path], capture_output=True, text=True)
    if r.returncode:
        sys.exit("ffprobe could not read %s" % path)
    return json.loads(r.stdout)


fill = "scale=%d:%d:force_original_aspect_ratio=increase:flags=lanczos,crop=%d:%d" % (W, H, W, H)   # fill 16:9, never letterbox
grade = ",eq=contrast=1.03:saturation=0.92" if args.grade else ""
os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
if still:
    n = int(round(args.dur * 30))
    # zoompan on a 2x canvas so the push is smooth, not stepped; centred, linear in scale (format 20's drift)
    vf = ("scale=%d:%d:force_original_aspect_ratio=increase:flags=lanczos,crop=%d:%d,"
          "zoompan=z='1+(%.4f-1)*on/%d':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=%d:s=%dx%d:fps=30%s,format=yuv420p"
          % (W * 2, H * 2, W * 2, H * 2, args.push, max(1, n - 1), n, W, H, grade))
    cmd = ["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", args.src, "-vf", vf, "-frames:v", str(n)]
else:
    info = probe(args.src)
    dur = float(info["format"]["duration"]) - args.start
    if args.dur:
        if args.dur > dur + 0.01:
            sys.exit("the clip has %.2f s after --start %.2f; --dur %.2f is longer" % (dur, args.start, args.dur))
        dur = args.dur
    vf = "%s%s,fps=30%s,format=yuv420p" % ((args.vf + ",") if args.vf else "", fill, grade)
    cmd = ["ffmpeg", "-y", "-v", "error", "-ss", "%.3f" % args.start, "-i", args.src, "-t", "%.3f" % dur, "-vf", vf]
cmd += ["-an", "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-g", "15", "-keyint_min", "15", "-sc_threshold", "0",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-movflags", "+faststart", args.out]
subprocess.run(cmd, check=True)

out = probe(args.out)
d_out = float(out["format"]["duration"])
v = [s for s in out["streams"] if s["codec_type"] == "video"][0]
if [s for s in out["streams"] if s["codec_type"] == "audio"]:
    sys.exit("FAIL %s still has audio" % args.out)
sheet = args.out + ".sheet.png"
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", args.out, "-vf",
                "select='eq(n,0)+eq(n,%d)+eq(n,%d)',scale=640:-2,tile=3x1" % (int(d_out * 15), max(0, int(d_out * 30) - 2)),
                "-frames:v", "1", "-fps_mode", "vfr", sheet], check=True)
print("wrote %s: %dx%d, %s fps, %.2f s, no audio" % (args.out, v["width"], v["height"], v["r_frame_rate"], d_out))
print("sheet: %s (look at it: hands, text on screens, faces that drifted)" % sheet)
rel = "broll/" + os.path.basename(args.out)
print("beat:", json.dumps({"type": "clip", "id": os.path.splitext(os.path.basename(args.out))[0][:12], "src": rel,
                           "in": 0.0, "out": round(min(d_out, 4.0), 2), "anchor": "the words spoken as it cuts in"}))
