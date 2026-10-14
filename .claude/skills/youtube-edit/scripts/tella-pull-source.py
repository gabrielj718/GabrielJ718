#!/usr/bin/env python3
"""tella-pull-source.py: download a Tella raw recording (camera+mic or screen) from the signed HLS URL
that the Tella MCP's `list_sources` returns, into a local MP4 (and optionally a 16 kHz mono WAV).

Tella's master playlist points at relative audio/video playlists and segments; the signed query string
has to travel with every one of them, which ffmpeg's HLS demuxer does not do (hence the "no stream" error).
This script fetches playlists and segments itself, appends the query, concatenates the fragments and
remuxes with ffmpeg (stream copy, so the 720p HEVC camera or the screen capture arrive untouched).

Usage:
  python3 tella-pull-source.py --url "<m3u8 url>" --out videos/<project>/tella/camera.mp4 [--wav audio-raw.wav]
  python3 tella-pull-source.py --url-file cam-url.txt --out camera.mp4     # URL read from a file (safer than pasting)
"""
import argparse, os, re, subprocess, sys, tempfile, urllib.parse, urllib.request

ap = argparse.ArgumentParser()
ap.add_argument("--url"); ap.add_argument("--url-file")
ap.add_argument("--out", required=True, help="output .mp4 (stream copy)")
ap.add_argument("--wav", help="also write a 16 kHz mono WAV for the cut stage / Parakeet")
ap.add_argument("--audio-only", action="store_true", help="skip the video rendition (faster when only the WAV is needed)")
args = ap.parse_args()
url = args.url or open(args.url_file).read().strip()
if not url: sys.exit("no URL")
split = urllib.parse.urlsplit(url)
base = split.scheme + "://" + split.netloc + split.path.rsplit("/", 1)[0] + "/"
query = split.query

def get(u):
    with urllib.request.urlopen(u, timeout=120) as r: return r.read()
def signed(rel):
    if rel.startswith("http"): full = rel
    else: full = urllib.parse.urljoin(base, rel)
    return full + ("&" if "?" in full else "?") + query

master = get(url).decode()
audio_uri, video_uri = None, None
lines = master.splitlines()
for i, ln in enumerate(lines):
    if ln.startswith("#EXT-X-MEDIA") and "TYPE=AUDIO" in ln:
        m = re.search(r'URI="([^"]+)"', ln); audio_uri = m.group(1) if m else audio_uri
    if ln.startswith("#EXT-X-STREAM-INF") and i + 1 < len(lines) and not lines[i + 1].startswith("#"):
        video_uri = video_uri or lines[i + 1].strip()
if not audio_uri and not video_uri:   # a media playlist, not a master
    video_uri = url

def pull(rel, dest):
    pl = get(signed(rel)).decode()
    pbase = urllib.parse.urljoin(base, rel).rsplit("/", 1)[0] + "/"
    parts = []
    for ln in pl.splitlines():
        if ln.startswith("#EXT-X-MAP"):
            m = re.search(r'URI="([^"]+)"', ln); parts.append(urllib.parse.urljoin(pbase, m.group(1)))
        elif ln and not ln.startswith("#"):
            parts.append(urllib.parse.urljoin(pbase, ln.strip()))
    with open(dest, "wb") as f:
        for n, p in enumerate(parts):
            f.write(get(p + ("&" if "?" in p else "?") + query))
            if n % 20 == 0: print("  %s: %d/%d" % (os.path.basename(dest), n + 1, len(parts)), file=sys.stderr)
    return dest

tmp = tempfile.mkdtemp(prefix="tella-pull-")
inputs = []
if audio_uri: inputs.append(pull(audio_uri, os.path.join(tmp, "audio.bin")))
if video_uri and not args.audio_only: inputs.append(pull(video_uri, os.path.join(tmp, "video.bin")))
os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
cmd = ["ffmpeg", "-y", "-v", "error"]
for i in inputs: cmd += ["-i", i]
cmd += ["-map", "0:a:0?"] if audio_uri else []
if video_uri and not args.audio_only: cmd += ["-map", "%d:v:0" % (len(inputs) - 1)]
cmd += ["-c", "copy", "-movflags", "+faststart", args.out]
subprocess.run(cmd, check=True)
if args.wav:
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", args.out, "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", args.wav], check=True)
probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", args.out], capture_output=True, text=True).stdout.strip()
print("-> %s (%s s)%s" % (args.out, probe, (" + " + args.wav) if args.wav else ""))
