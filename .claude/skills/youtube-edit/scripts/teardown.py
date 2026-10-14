#!/usr/bin/env python3
"""teardown.py: measure any video for the editing teardown loop (every two videos: two reference videos you admire vs
your own last two edits: cuts per minute, overlay density, camera moves, cutaway types, sound, captions).

Video mode writes into --out: sheet_NN.png contact sheets (4x4 tiles, 480x270, one tile every --every s), report.json
and TEARDOWN.md (the numbers, the sheet list, a "count by eye" block and a worksheet seeded with the spoken lines).
One ffmpeg decode does the sheets, the per-frame difference (64x36 gray, tblend difference, signalstats) and the
luminance; a second pass reads the audio RMS. Python never touches a full frame.
  hard cuts       a same-framing jump cut is a SPIKE against the local median difference, not a fixed threshold
                  (a fixed 40/255 misses every jump cut): a run of 1-2 frames at >= --cut-ratio (4) x the median
                  of the 0.5 s either side and >= 2 x the frames around it. Calibrated on real jump cuts made from
                  talking-head footage: full frame 5.5-17x, a face in a PiP 4.1-12x (0.45/255 absolute). The only
                  absolute bar is a 0.3/255 noise floor, so encoder flicker on a frozen screen never counts.
                  A graphic that snaps in or out in one frame also counts; check the list against the sheets.
  bursts          3-15 frame runs above the same bar: animated entrances, fast layout switches, big gestures.
  quietest        the lowest-change windows of >= --static s (15) against the video's own median change energy:
                  the "feels static" proxy.
  --transcript    words per minute and one spoken line every ~10 s in the worksheet (word-level JSON: a list,
                  {words:[...]} or whisper {segments:[{words}]}; segment-only JSON is spread evenly per segment).
Storyboard mode counts one of OUR storyboard.json files exactly (overlays, camera moves, cutaways, on-screen words
per minute, events per 90 s against a target of about 7 + 7). Compare mode puts reports side by side.

Usage:
  python3 teardown.py --video ref-1.mp4 --out teardowns/ref-1 [--every 2] [--transcript ref-1.json]
  python3 teardown.py --storyboard videos/<p>/storyboard.json [--out teardowns/<p>]
  python3 teardown.py --compare teardowns/ref-1/report.json teardowns/ref-2/report.json teardowns/<p>/report.json --out teardowns/COMPARE.md
"""
import argparse, glob, json, os, re, shutil, statistics as st, subprocess, sys, tempfile, time

ap = argparse.ArgumentParser()
g = ap.add_mutually_exclusive_group(required=True)
g.add_argument("--video"); g.add_argument("--storyboard"); g.add_argument("--compare", nargs="+")
ap.add_argument("--out")
ap.add_argument("--every", type=float, default=2.0, help="seconds between contact-sheet tiles")
ap.add_argument("--transcript", help="word-level JSON (list or {words:[{text,start,end}]})")
ap.add_argument("--cut-ratio", type=float, default=4.0)
ap.add_argument("--static", type=float, default=15.0, help="shortest quiet stretch reported, seconds")
ap.add_argument("--name", help="label in the report and the comparison (default: the file name, or its folder for final/output files)")
args = ap.parse_args()
TARGET = (7, 7)   # overlays + camera moves per 90 s, the target
mmss = lambda t: "%d:%02d" % (int(t) // 60, int(t) % 60)
per = lambda n, dur, span: span * n / dur if dur else 0.0

def write(path, text):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    open(path, "w").write(text)

# ================================================================================================================
# full-frame types on the brand wash (compose.py's "cut" layer), and beats that push the footage (#video-wrap in and out)
FULL = {"site", "grid", "scene", "browser3d", "fan3d", "bars", "pipeline", "hub", "video", "article", "image", "photo", "flow", "diagram", "broll", "cutaway"}
PUSH = {"bullets", "popout"}
wc = lambda s: sum(1 for w in str(s).split() if re.search(r"[A-Za-z0-9]", w))   # "+" and "=" are not words

def onscreen_words(b):
    n = sum(wc(b.get(k, "")) for k in ("text", "eyebrow", "label", "title", "sub", "center"))
    n += (1 if b.get("domain") else 0) + (1 if b.get("value") is not None else 0) + (6 if b["type"] == "pointer" else 0)  # pointer: "Everything is linked in the description"
    for k in ("items", "rows", "steps", "spokes", "terms", "slots"):
        for it in b.get(k, []):
            if isinstance(it, dict):
                n += wc(it.get("label", "")) + wc(it.get("sub", "")) + (wc(it["text"]) if it.get("text") else 1 if it.get("value") is not None else 0)
            else:
                n += wc(it if isinstance(it, str) else it[0])
    return n

def storyboard(path):
    S = json.load(open(path)); D = float(S["duration"])
    tags = S.get("tags") or ([S["tag"]] if S.get("tag") else [])
    beats = S.get("beats", [])
    words = sum(wc(t.get("label", "")) for t in tags)
    implied, cutaways, types = 0, [], {}
    for b in beats:
        t = b["type"]; types[t] = types.get(t, 0) + 1
        full = t in FULL or (t == "stats" and b.get("layout", "row") != "stack") or b.get("fullframe")
        if full:
            cutaways.append(t)
            implied += {"zoomthrough": 2, "punch": 1}.get(b.get("transition", "none"), 0)    # the dressed cut in / out
        implied += 2 if t in PUSH else 0                                                     # push in + release
        words += onscreen_words(b)
    ops = [op for op in S.get("camera", []) if op[0] != "set"]
    overlays, moves = len(tags) + len(beats), len(ops) + implied
    r = {"kind": "storyboard", "name": args.name or S.get("id", os.path.basename(os.path.dirname(os.path.abspath(path)))), "source": path,
         "duration": D, "overlays": overlays, "camera_moves": moves, "camera_ops": len(ops), "camera_implied": implied,
         "cutaways": len(cutaways), "cutaway_types": sorted(set(cutaways)), "beat_types": types, "onscreen_words": words,
         "overlays_per_min": round(per(overlays, D, 60), 2), "camera_moves_per_min": round(per(moves, D, 60), 2),
         "cutaways_per_min": round(per(len(cutaways), D, 60), 2), "onscreen_words_per_min": round(per(words, D, 60), 1),
         "overlays_per_90s": round(per(overlays, D, 90), 1), "camera_moves_per_90s": round(per(moves, D, 90), 1)}
    lines = ["storyboard %s  %.1f s (%s)" % (r["name"], D, mmss(D)),
             "  overlays      %3d  %5.2f /min  (%s)" % (overlays, r["overlays_per_min"], ", ".join("%s %d" % kv for kv in sorted(types.items()))
                                                    + (", tag %d" % len(tags) if tags else "")),
             "  camera moves  %3d  %5.2f /min  (%d ops other than set + %d from bullets/pop-outs/transitions)" % (moves, r["camera_moves_per_min"], len(ops), implied),
             "  cutaways      %3d  %5.2f /min  (%s)" % (len(cutaways), r["cutaways_per_min"], ", ".join(r["cutaway_types"]) or "none"),
             "  on-screen words %d  %5.1f /min" % (words, r["onscreen_words_per_min"]),
             "  per 90 s: %.1f overlays + %.1f camera moves (target about %d + %d)" % (r["overlays_per_90s"], r["camera_moves_per_90s"], TARGET[0], TARGET[1])]
    if S.get("raw_html") or S.get("raw_js"):
        lines.append("  (raw_html / raw_js present: hand-authored elements there are not counted)")
    print("\n".join(lines))
    if args.out:
        write(os.path.join(args.out, "report.json"), json.dumps(r, indent=1))
        print("-> %s" % os.path.join(args.out, "report.json"))

# ================================================================================================================
ROWS = [("Duration", lambda r: "%.1f s (%s)" % (r["duration"], mmss(r["duration"]))),
        ("Hard cuts / min", lambda r: "%.1f" % r["cuts_per_min"] if "cuts_per_min" in r else ""),
        ("Mean shot", lambda r: "%.1f s" % r["mean_shot_s"] if "mean_shot_s" in r else ""),
        ("Short bursts / min", lambda r: "%.1f" % r["bursts_per_min"] if "bursts_per_min" in r else ""),
        ("Median change /255", lambda r: "%.2f" % r["median_diff"] if "median_diff" in r else ""),
        ("Quietest stretch", lambda r: "%.0f s at %.2fx median (%s)" % (r["quiet"][0]["length"], r["quiet"][0]["ratio"], mmss(r["quiet"][0]["from"])) if r.get("quiet") else ""),
        ("Words / min", lambda r: "%.0f" % r["words_per_min"] if r.get("words_per_min") else ""),
        ("Audio RMS median", lambda r: "%.0f dB" % r["audio"]["median_db"] if r.get("audio") else ""),
        ("Overlays / 90 s", lambda r: "%.1f" % r["overlays_per_90s"] if "overlays_per_90s" in r else ""),
        ("Camera moves / 90 s", lambda r: "%.1f" % r["camera_moves_per_90s"] if "camera_moves_per_90s" in r else ""),
        ("Cutaways / min", lambda r: "%.2f" % r["cutaways_per_min"] if "cutaways_per_min" in r else ""),
        ("On-screen words / min", lambda r: "%.1f" % r["onscreen_words_per_min"] if "onscreen_words_per_min" in r else "")]

def compare(paths):
    R = [json.load(open(p)) for p in paths]
    names = [r.get("name") or os.path.basename(os.path.dirname(os.path.abspath(p))) for r, p in zip(R, paths)]
    rows = [(k, [f(r) for r in R]) for k, f in ROWS]
    rows = [(k, v) for k, v in rows if any(v)]
    md = ["# Teardown comparison", "", "Target: about %d overlays + %d camera moves per 90 s. Video reports are measured from the file;"
          " storyboard reports are exact counts from our storyboard.json." % TARGET, "",
          "| Metric | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    md += ["| %s | %s |" % (k, " | ".join(v)) for k, v in rows]
    text = "\n".join(md) + "\n"
    print(text)
    if args.out:
        out = os.path.join(args.out, "COMPARE.md") if os.path.isdir(args.out) or not args.out.endswith(".md") else args.out
        write(out, text); print("-> %s" % out)

# ================================================================================================================
def meta(path, key):
    """ffmpeg metadata=print file -> [(pts_time, value)]."""
    out, t = [], None
    for line in open(path):
        m = re.search(r"pts_time:([-\d.e]+)", line)
        if m:
            t = float(m.group(1)); continue
        m = re.search(key + r"=(\S+)", line)
        if m and t is not None:
            v = m.group(1); out.append((t, -120.0 if "inf" in v else float(v)))
    return out

def runs(flags):
    out, i = [], 0
    while i < len(flags):
        if flags[i]:
            j = i
            while j + 1 < len(flags) and flags[j + 1]: j += 1
            out.append((i, j)); i = j + 1
        else:
            i += 1
    return out

def video(path):
    if not args.out:
        sys.exit("--out is required with --video")
    os.makedirs(args.out, exist_ok=True)
    for f in glob.glob(os.path.join(args.out, "sheet_*.png")): os.remove(f)
    p = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate",
                                   "-show_entries", "format=duration", "-of", "json", path], capture_output=True, text=True, check=True).stdout)
    vs = next(s for s in p["streams"] if s["codec_type"] == "video")
    n, d = [int(x) for x in vs["r_frame_rate"].split("/")]; fps = n / d
    dur = float(p["format"]["duration"]); has_audio = any(s["codec_type"] == "audio" for s in p["streams"])
    tmp = tempfile.mkdtemp(prefix="teardown-")
    diff_f, luma_f, rms_f = (os.path.join(tmp, x) for x in ("diff.txt", "luma.txt", "rms.txt"))
    fc = ("[0:v]split=2[m][s];[m]scale=64:36:flags=area,format=gray,split=2[g1][g2];"
          "[g1]tblend=all_mode=difference,signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=%s[d];"
          "[g2]signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=%s[l];"
          "[s]fps=%.6f,scale=480:270:force_original_aspect_ratio=decrease,pad=480:270:-1:-1,tile=4x4[t]") % (diff_f, luma_f, 1.0 / args.every)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-filter_complex", fc, "-map", "[d]", "-f", "null", "-",
                    "-map", "[l]", "-f", "null", "-", "-map", "[t]", "-fps_mode", "passthrough", os.path.join(args.out, "sheet_%02d.png")], check=True)
    if has_audio:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-vn", "-af", "aresample=16000,aformat=channel_layouts=mono,"
                        "asetnsamples=n=4000:p=0,astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level:file=%s" % rms_f,
                        "-f", "null", "-"], check=True)
    D = meta(diff_f, r"lavfi\.signalstats\.YAVG"); L = meta(luma_f, r"lavfi\.signalstats\.YAVG")
    A = meta(rms_f, r"lavfi\.astats\.Overall\.RMS_level") if has_audio else []
    shutil.rmtree(tmp, ignore_errors=True)
    t = [x for x, _ in D]; dv = [v for _, v in D]

    # ---- hard cuts and bursts: runs above the local-median bar ----------------------------------------------
    W, EPS = max(3, round(0.5 * fps)), 0.05
    med = [st.median(dv[max(0, i - W):i] + dv[i + 1:i + 1 + W] or [0.0]) for i in range(len(dv))]
    hot = [dv[i] >= 0.3 and dv[i] >= args.cut_ratio * (med[i] + EPS) for i in range(len(dv))]
    cuts, bursts, detail = [], [], []
    for i, j in runs(hot):
        if i == 0 or j == len(dv) - 1:
            continue                                   # a spike on the first or last frame has no "after" (end card, fade)
        outer = max(dv[i - 1], dv[j + 1]) + EPS
        if j - i <= 1 and min(dv[i:j + 1]) >= 2.0 * outer:
            k = max(range(i, j + 1), key=lambda k: dv[k]); cuts.append(round(t[k], 3))
            detail.append({"t": round(t[k], 3), "diff": round(dv[k], 2), "x_median": round(dv[k] / (med[k] + EPS), 1)})
        elif j - i >= 2 and j - i <= 14:
            bursts.append((round(t[i], 3), round(t[j], 3)))
    per_min = lambda k: round(per(k, dur, 60), 2)

    # ---- quietest stretches: per-second change energy against the video's own median ---------------------------
    secs = int(dur)
    buckets = [[] for _ in range(secs)]
    for x, v in D:
        if 0 <= int(x) < secs: buckets[int(x)].append(v)
    e = [st.mean(b) if b else 0.0 for b in buckets]
    M = st.median(e) if e else 0.0
    quiet, taken = [], set()
    Wq = int(args.static)
    if M > 0 and secs >= Wq:
        wins = sorted(((st.mean(e[s:s + Wq]) / M, s) for s in range(secs - Wq + 1)))
        for ratio, s in wins:
            if len(quiet) >= 5 or ratio >= 1.0: break
            if any(x in taken for x in range(s, s + Wq)): continue
            a, b = s, s + Wq
            while a > 0 and a - 1 not in taken and e[a - 1] < M: a -= 1         # grow while the next second is still quiet
            while b < secs and b not in taken and e[b] < M: b += 1
            taken.update(range(a, b))
            quiet.append({"from": a, "to": b, "length": b - a, "ratio": round(st.mean(e[a:b]) / M, 2),
                          "cuts": sum(1 for c in cuts if a <= c < b)})
        quiet.sort(key=lambda q: q["ratio"])

    # ---- luminance, audio ------------------------------------------------------------------------------------------
    step = max(1, round(fps / 2))
    luma = [round(v) for _, v in L[::step]]
    rms = [round(v, 1) for _, v in A]
    audio = None
    if rms:
        srt = sorted(rms)
        onsets = [round(i * 0.25, 2) for i in range(4, len(rms)) if rms[i] - st.median(rms[i - 4:i]) >= 12 and rms[i] > -40]
        audio = {"median_db": st.median(rms), "p10_db": srt[len(srt) // 10], "p90_db": srt[9 * len(srt) // 10],
                 "quiet_pct": round(100.0 * sum(1 for v in rms if v < -45) / len(rms), 1), "onset_candidates": onsets}

    # ---- transcript ----------------------------------------------------------------------------------------------
    wpm, spoken = None, []
    if args.transcript:
        raw = json.load(open(args.transcript))
        ws = raw if isinstance(raw, list) else raw.get("words") or [w for sg in raw.get("segments", []) for w in sg.get("words", [])]
        if not ws and isinstance(raw, dict):      # segment-level whisper JSON: spread each segment's words across it
            for sg in raw.get("segments", []):
                tx = sg.get("text", "").split()
                ws += [{"text": x, "start": sg["start"] + (sg["end"] - sg["start"]) * k / len(tx)} for k, x in enumerate(tx)]
        ws = sorted(({"text": str(w.get("text", w.get("word", ""))).strip(), "start": float(w["start"])} for w in ws), key=lambda w: w["start"])
        ws = [w for w in ws if w["text"]]
        wpm = round(per(len(ws), dur, 60), 1)
        for slot in range(0, int(dur) + 1, 10):
            i = next((i for i, w in enumerate(ws) if w["start"] >= slot), None)
            if i is None or ws[i]["start"] >= slot + 10: continue
            i = next((k for k in range(i, len(ws)) if ws[k]["start"] < slot + 6 and k and re.search(r"[.?!]$", ws[k - 1]["text"])), i)
            line = []
            for w in ws[i:i + 14]:
                line.append(w["text"])
                if re.search(r"[.?!]$", w["text"]): break
            spoken.append((round(ws[i]["start"], 2), " ".join(line)))

    sheets = sorted(glob.glob(os.path.join(args.out, "sheet_*.png")), key=lambda f: int(re.sub(r"\D", "", os.path.basename(f))))
    sheet_rows = [{"file": os.path.basename(s), "from": round(k * 16 * args.every, 2), "to": round(min(dur, (k * 16 + 15) * args.every), 2)}
                  for k, s in enumerate(sheets)]
    stem = os.path.splitext(os.path.basename(path))[0]
    if not args.name and re.match(r"^(final|output|render|video|input-video)([-_].*)?$", stem):
        stem = os.path.basename(os.path.dirname(os.path.abspath(path))) or stem
    r = {"kind": "video", "name": args.name or stem, "source": path, "duration": round(dur, 3),
         "fps": round(fps, 3), "width": vs.get("width"), "height": vs.get("height"),
         "cuts": cuts, "cut_detail": detail, "cuts_per_min": per_min(len(cuts)), "mean_shot_s": round(dur / (len(cuts) + 1), 2),
         "bursts": bursts, "bursts_per_min": per_min(len(bursts)), "median_diff": round(st.median(dv), 3) if dv else 0.0,
         "quiet": quiet, "luma_every_0_5s": luma, "rms_db_every_0_25s": rms, "audio": audio,
         "words_per_min": wpm, "spoken_every_10s": spoken, "sheets": sheet_rows,
         "detector": {"cut_ratio": args.cut_ratio, "window_frames": W, "neighbour_ratio": 2.0, "min_diff": 0.3}}
    write(os.path.join(args.out, "report.json"), json.dumps(r, indent=1))

    # ---- TEARDOWN.md ---------------------------------------------------------------------------------------------
    lum_s = "min %d, median %d, max %d (0-255, every 0.5 s in report.json)" % (min(luma), st.median(luma), max(luma)) if luma else "n/a"
    md = ["# Teardown: %s" % r["name"], "",
          "Measured by teardown.py on %s from `%s`. The numbers are from the file; the eye-count block and the worksheet"
          " are filled by hand from the sheets." % (time.strftime("%Y-%m-%d"), path), "",
          "## Measured", "", "| Metric | Value |", "|---|---|",
          "| Duration | %.1f s (%s), %sx%s at %g fps |" % (dur, mmss(dur), vs.get("width"), vs.get("height"), round(fps, 3)),
          "| Hard cuts | %d, %.1f per min, mean shot %.1f s |" % (len(cuts), r["cuts_per_min"], r["mean_shot_s"]),
          "| Short bursts (animated entrances, fast switches, big gestures) | %d, %.1f per min |" % (len(bursts), r["bursts_per_min"]),
          "| Median frame change | %.2f /255 |" % r["median_diff"],
          "| Luminance | %s |" % lum_s,
          "| Audio RMS | %s |" % ("median %.0f dB, p10 %.0f, p90 %.0f, %.0f%% of 0.25 s windows under -45 dB" % (
              audio["median_db"], audio["p10_db"], audio["p90_db"], audio["quiet_pct"]) if audio else "no audio stream"),
          "| Words per minute | %s |" % (wpm if wpm is not None else "no --transcript"), "",
          "Hard cuts (s): %s" % (" ".join("%.2f" % c for c in cuts) or "none"), "",
          "Short bursts (s): %s" % (" ".join("%.2f-%.2f" % b for b in bursts) or "none"), "",
          "Loudness jumps, sound-cue candidates (s, +12 dB over the second before): %s" % (
              " ".join("%.2f" % x for x in audio["onset_candidates"][:60]) if audio and audio["onset_candidates"] else "none"), "",
          "## Quietest stretches (the \"feels static\" proxy)", "",
          "Windows of %d s or more with the least visual change, against this video's own median." % Wq, ""]
    md += (["| From | To | Length | Change vs median | Cuts inside |", "|---|---|---|---|---|"] +
           ["| %s | %s | %d s | %.2fx | %d |" % (mmss(q["from"]), mmss(q["to"]), q["length"], q["ratio"], q["cuts"]) for q in quiet]
           if quiet else ["None below the median for %d s straight." % Wq])
    md += ["", "## Sheets", "", "4x4 tiles, one every %g s, left to right then down." % args.every, ""]
    md += ["- `%s`  %s - %s" % (s["file"], mmss(s["from"]), mmss(s["to"])) for s in sheet_rows]
    md += ["", "## Count by eye from the sheets", "",
           "- Visual moments / min:", "- Element entrances / min:", "- On-screen words / min:", "- Camera moves / min:",
           "- Face presence %:", "- Cutaway types:", "- Caption style:", "",
           "Do not claim you heard audio based on waveform numbers; listen or say it was not listened to.", "",
           "## Worksheet", "", "| Time | Spoken idea | Visual change | Camera | Sound cue | Viewer question | Payoff |", "|---|---|---|---|---|---|---|"]
    said = {int(tt // 10): line for tt, line in spoken}
    md += ["| %s | %s |  |  |  |  |  |" % (mmss(s), said.get(s // 10, "").replace("|", "/")) for s in range(0, int(dur) + 1, 10)]
    write(os.path.join(args.out, "TEARDOWN.md"), "\n".join(md) + "\n")
    print("%s  %.1f s  cuts %d (%.1f/min, mean shot %.1f s)  bursts %d  median change %.2f  quietest %s%s"
          % (r["name"], dur, len(cuts), r["cuts_per_min"], r["mean_shot_s"], len(bursts), r["median_diff"],
             "%s-%s %.2fx" % (mmss(quiet[0]["from"]), mmss(quiet[0]["to"]), quiet[0]["ratio"]) if quiet else "none",
             "  wpm %.0f" % wpm if wpm else ""))
    print("cuts: %s" % " ".join("%.2f" % c for c in cuts))
    print("-> %s (%d sheets)" % (os.path.join(args.out, "TEARDOWN.md"), len(sheets)))

if args.storyboard:
    storyboard(args.storyboard)
elif args.compare:
    compare(args.compare)
else:
    video(args.video)
