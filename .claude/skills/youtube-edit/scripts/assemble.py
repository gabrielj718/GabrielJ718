#!/usr/bin/env python3
"""assemble.py: put finished segments in order and deliver one 4K master. Replaces iMovie.

Input : assembly.json (the manifest; a segment is a local MP4: a HyperFrames render, a Tella 4K export, a cutaway)
Output: <out>.mp4 (3840x2160, 30 fps, H.264, BT.709 tags, AAC 48 kHz stereo), ASSEMBLY.md next to it
        (segment table with start times = YouTube chapter list, loudness per segment, md5), chapters.txt

Manifest:
{
  "project": "my-video",
  "width": 3840, "height": 2160, "fps": 30,
  "loudness": -14,                       # LUFS target applied per segment (null = leave levels alone)
  "music": {"file": "bed.mp3", "db": -26, "fade": 2.0},   # optional, loops under the whole video
  "segments": [
    {"name": "Hook",            "file": "~/Movies/YouTube Renders/my-video/hook-4k.mp4"},
    {"name": "1 · Setup",       "file": "~/Movies/YouTube Renders/my-video/01-setup-4k.mp4"},
    {"name": "1 · Tutorial",    "file": "tella/01-setup-tutorial-4k.mp4", "trim": [0.0, 71.4], "chapter": false}
  ]
}
Relative paths resolve against the manifest's folder. "trim" is [start, end] seconds (null = to the end).
"chapter": false hides a segment from the chapter list (a tutorial that continues the previous chapter).

Every segment is conformed to the master spec with one libx264 CRF 16 pass (or --gpu: VideoToolbox at
45 Mbit/s, ~4x faster, same setting the render step uses), loudness-normalised in two passes, then the
pieces are joined with the concat demuxer and stream copy. Mixed sources (a 45 Mbit/s HyperFrames render,
a 9 Mbit/s Tella export, a 720p cutaway) come out as one clean file with no level jumps between them.

Usage:
  python3 assemble.py --manifest videos/<project>/assembly.json --out "$HOME/Movies/YouTube Renders/<project>/<project>-full-4k.mp4" [--gpu] [--keep-work]
"""
import argparse, hashlib, json, os, shutil, subprocess, sys, tempfile

ap = argparse.ArgumentParser()
ap.add_argument("--manifest", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--gpu", action="store_true", help="h264_videotoolbox 45M instead of libx264 CRF 16")
ap.add_argument("--keep-work", action="store_true")
ap.add_argument("--work", help="work folder (default: <manifest dir>/assembly-work)")
args = ap.parse_args()

mdir = os.path.dirname(os.path.abspath(args.manifest))
M = json.load(open(args.manifest))
W, H, FPS = int(M.get("width", 3840)), int(M.get("height", 2160)), int(M.get("fps", 30))
LUFS = M.get("loudness", -14)
work = args.work or os.path.join(mdir, "assembly-work")
os.makedirs(work, exist_ok=True)

def resolve(p):
    p = os.path.expanduser(p)
    return p if os.path.isabs(p) else os.path.join(mdir, p)

def probe(path):
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
        "stream=codec_type,codec_name,width,height,r_frame_rate,pix_fmt,sample_rate,channels,color_transfer:format=duration",
        "-of", "json", path], capture_output=True, text=True, check=True).stdout)
    v = next((s for s in j["streams"] if s["codec_type"] == "video"), {})
    a = next((s for s in j["streams"] if s["codec_type"] == "audio"), None)
    return {"dur": float(j["format"]["duration"]), "w": v.get("width"), "h": v.get("height"),
            "fps": v.get("r_frame_rate"), "codec": v.get("codec_name"), "audio": a is not None,
            "sr": a and int(a.get("sample_rate", 0)), "ch": a and a.get("channels")}

def measure_loudness(path, ss, to):
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-i", path]
    if ss: cmd += ["-ss", str(ss)]
    if to: cmd += ["-to", str(to)]
    cmd += ["-vn", "-af", "loudnorm=I=%s:TP=-1.5:LRA=11:print_format=json" % LUFS, "-f", "null", "-"]
    out = subprocess.run(cmd, capture_output=True, text=True).stderr
    blob = out[out.rfind("{"):out.rfind("}") + 1]
    return json.loads(blob)

conformed, rows, t = [], [], 0.0
for n, seg in enumerate(M["segments"]):
    src = resolve(seg["file"])
    if not os.path.exists(src): sys.exit("missing segment: %s" % src)
    p = probe(src)
    trim = seg.get("trim") or [None, None]
    ss, to = trim[0] or None, trim[1] if len(trim) > 1 else None
    dst = os.path.join(work, "%02d-%s.mp4" % (n + 1, "".join(c if c.isalnum() else "-" for c in seg["name"]).strip("-").lower()))
    vf = "scale=%d:%d:force_original_aspect_ratio=decrease:flags=lanczos,pad=%d:%d:(ow-iw)/2:(oh-ih)/2:color=black,fps=%d,format=yuv420p" % (W, H, W, H, FPS)
    af_parts = []
    lin, lout = None, None
    if p["audio"] and LUFS is not None:
        m = measure_loudness(src, ss, to)
        lin = float(m["input_i"]); lout = LUFS
        af_parts.append("loudnorm=I=%s:TP=-1.5:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:linear=true:print_format=summary"
                        % (LUFS, m["input_i"], m["input_tp"], m["input_lra"], m["input_thresh"], m["target_offset"]))
    af_parts.append("aresample=48000,aformat=channel_layouts=stereo")
    cmd = ["ffmpeg", "-y", "-v", "error"]
    if ss: cmd += ["-ss", str(ss)]
    if to: cmd += ["-to", str(to)]
    cmd += ["-i", src]
    if not p["audio"]:
        cmd += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-shortest"]
    cmd += ["-map", "0:v:0", "-map", ("1:a:0" if not p["audio"] else "0:a:0"), "-vf", vf]
    if args.gpu: cmd += ["-c:v", "h264_videotoolbox", "-b:v", "45M", "-profile:v", "high", "-allow_sw", "1"]
    else: cmd += ["-c:v", "libx264", "-crf", "16", "-preset", "fast", "-profile:v", "high", "-level", "5.1"]
    cmd += ["-g", str(FPS), "-keyint_min", str(FPS), "-r", str(FPS), "-pix_fmt", "yuv420p",
            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
            "-af", ",".join(af_parts), "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
            "-video_track_timescale", "90000", "-movflags", "+faststart", dst]
    print("conform %d/%d  %s  (%sx%s %s, %.1fs%s)" % (n + 1, len(M["segments"]), seg["name"], p["w"], p["h"], p["fps"], p["dur"],
          "" if lin is None else ", %.1f LUFS -> %s" % (lin, LUFS)))
    subprocess.run(cmd, check=True)
    d = probe(dst)["dur"]
    rows.append({"name": seg["name"], "start": t, "dur": d, "src": src, "lufs_in": lin, "chapter": seg.get("chapter", True)})
    conformed.append(dst); t += d

lst = os.path.join(work, "concat.txt")
open(lst, "w").write("".join("file '%s'\n" % c.replace("'", "'\\''") for c in conformed))
joined = os.path.join(work, "joined.mp4")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", joined], check=True)

final_src = joined
music = M.get("music")
if music and music.get("file"):
    mp = resolve(music["file"]); gain = float(music.get("db", -26)); fade = float(music.get("fade", 2.0))
    mixed = os.path.join(work, "joined-music.mp4")
    fc = ("[1:a]aloop=loop=-1:size=2e9,atrim=0:%.3f,volume=%sdB,afade=t=out:st=%.3f:d=%.3f[m];[0:a][m]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[a]"
          % (t, gain, max(0.0, t - fade), fade))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", joined, "-i", mp, "-filter_complex", fc, "-map", "0:v:0", "-map", "[a]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-movflags", "+faststart", mixed], check=True)
    final_src = mixed

os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", final_src, "-c", "copy", "-color_primaries", "bt709", "-color_trc", "bt709",
                "-colorspace", "bt709", "-color_range", "tv", "-movflags", "+write_colr+faststart", args.out], check=True)
md5 = hashlib.md5(open(args.out, "rb").read()).hexdigest()
fp = probe(args.out)

def ts(s):
    s = int(round(s)); return "%d:%02d" % (s // 60, s % 60) if s < 3600 else "%d:%02d:%02d" % (s // 3600, s // 60 % 60, s % 60)
chapters = [(ts(r["start"]), r["name"]) for r in rows if r["chapter"]]
if chapters and chapters[0][0] != "0:00": chapters[0] = ("0:00", chapters[0][1])
lines = ["# Assembly: %s" % M.get("project", os.path.basename(mdir)), "",
         "`%s`  %dx%d %s fps, %.1f s, md5 %s. Open from Finder, not the app." % (os.path.basename(args.out), fp["w"], fp["h"], FPS, fp["dur"], md5), "",
         "| # | Start | Length | Segment | Source | Loudness in |", "|---|---|---|---|---|---|"]
for i, r in enumerate(rows):
    lines.append("| %d | %s | %.1f s | %s | %s | %s |" % (i + 1, ts(r["start"]), r["dur"], r["name"], os.path.basename(r["src"]),
                 "" if r["lufs_in"] is None else "%.1f LUFS" % r["lufs_in"]))
lines += ["", "Loudness target per segment: %s LUFS (true peak -1.5 dBTP)." % LUFS,
          "Music: %s" % ("%s at %s dB" % (os.path.basename(resolve(music["file"])), music.get("db", -26)) if music and music.get("file") else "none (silence by default)"),
          "", "## YouTube chapters", ""] + ["%s %s" % c for c in chapters]
open(os.path.join(os.path.dirname(os.path.abspath(args.out)), "ASSEMBLY.md"), "w").write("\n".join(lines) + "\n")
open(os.path.join(os.path.dirname(os.path.abspath(args.out)), "chapters.txt"), "w").write("".join("%s %s\n" % c for c in chapters))
if not args.keep_work: shutil.rmtree(work, ignore_errors=True)
print("-> %s (%.1f s, %d segments, md5 %s)" % (args.out, fp["dur"], len(rows), md5))
for c in chapters: print("   %s %s" % c)
