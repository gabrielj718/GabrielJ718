---
name: youtube-edit
description: Edit a YouTube video end to end in Claude Code. Takes a raw camera clip (retakes and all) or a flat cut, cuts it, adds animated overlays, cutaways, stock or AI B-roll, camera moves and the few sounds that earn a place, then renders a tagged 4K MP4 locally with HyperFrames. Use whenever the user drops a video file or an SD-card clip and says "cut this", "edit this", "overlay this", "add animations", "edit this hook", "add B-roll", "render it in 4K", "edit the Tella tutorial", "assemble the video" or "put the segments together", or names a video file to edit. Covers the cut stage (paper cut, hand cut, tighten, sliver and edge checks, dead-air scan), the storyboard composer and its format library, long-form pacing, camera, sound, Tella screen tutorials, assembly into one master, render checks and delivery.
---

# YouTube editor

Turns raw footage or a flat cut into a finished video: the cut, animated overlays, cutaways, camera moves, sound and a
tagged 4K MP4. Everything runs on your own machine through HyperFrames (Chrome + FFmpeg): no per-render cost, and no
footage leaves the computer.

**The house style.** This is a real channel's editing skill, so it has opinions: light glass cards, DM Sans 700, cyan
for key words, amber for money, magenta for punchlines, a camera anchored to the top of the frame, and silence unless
something on screen makes a sound. Those are the defaults, written to you, the creator. `STYLE-GUIDE.md` (in the kit
folder this skill came in) sums up the look: colours, font, cards, motion, camera, sound and cuts. When you change it,
Claude updates the matching rules here and the colour tokens in the `:root` block of `scripts/compose.py`. For the
look, the style guide wins.

**This skill keeps learning.** Every rule below came from a real note on a real video. When you give a note worth
keeping ("the text is too small", "no sound on this part"), say **"save this to the skill"**: Claude writes it into the
right section of this file as one plain rule, and the next edit starts from it. See "Keeping the skill yours".

Commands run from your project folder with `SK=".claude/skills/youtube-edit"` (where this skill is installed) and
`W="videos/<project>"` (one working folder per video).

## Setup check (first use, and after any update)

On first use Claude checks each line, installs what is missing (asking before anything that needs admin rights), then
runs the tests. Check again after updating HyperFrames or moving the skill.

| Needs | Check | Install when missing |
|---|---|---|
| Node.js 22 or newer | `node -v` | nodejs.org, or `brew install node` |
| HyperFrames CLI | `npx hyperframes --version`, then `npx hyperframes doctor` | comes through npx; `doctor` lists anything else it wants |
| FFmpeg and ffprobe | `ffmpeg -version` | `brew install ffmpeg` (Mac), `winget install ffmpeg` (Windows), the package manager (Linux) |
| Python 3 with numpy | `python3 -c "import numpy"` | `python3 -m pip install numpy` |
| auto-editor | `auto-editor --version` | `pip install auto-editor` or `brew install auto-editor` |
| Parakeet, the transcriber `npx hyperframes transcribe --engine parakeet` uses | transcribe a 5 s WAV with `--engine parakeet --json` | `npx hyperframes models install parakeet` |
| Google Chrome | snapshots, page captures and headless screenshots run in it | google.com/chrome |
| GSAP | compose.py prints a note when it falls back to the CDN (the first render then needs internet) | optional local copy: `mkdir -p "$SK/assets/vendor" && curl -sL https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js -o "$SK/assets/vendor/gsap.min.js"` |
| yt-dlp (optional) | `yt-dlp --version` | `brew install yt-dlp` or `pip install yt-dlp` |

Then, from the scripts folder (not from inside `tests/`): `cd "$SK/scripts" && python3 -m unittest tests`. The tests use
synthetic media and must end with `OK` (the media tests skip themselves without ffmpeg). Run them after touching any script.

- **What ships:** the scripts, `formats/`, and the fonts in `assets/fonts/` (DM Sans 400/500/700, SIL Open Font
  License), which compose.py stages into `public/fonts/` itself. **No sounds, images, logos or footage ship.** Keep yours
  in a shared folder that compose.py copies with `--shared DIR` (`DIR/sfx/`, `DIR/img/`, `DIR/img/thumbs/`): sounds from
  your Epidemic Sound account (its connector) or the free HyperFrames library (`npx hyperframes skills update media-use`
  puts 19 effects in the media-use skill's `audio/assets/sfx/`, Pixabay Content License, no attribution needed); logos
  from the brands' own press kits or sites (see "Sourcing assets").
- **Optional connectors:** Tella (screen tutorials) and Epidemic Sound. Without Tella, record the screen with anything.
- numpy scripts: `sync-tracks.py`, `tighten-cut.py`, `sliver.py`, `edge-audit.py`, `dead-air.py`. Node: `stutter-scan.py`
  (it runs `find-cut-candidates.mjs`) and the cut review page (`build-edl-review.mjs`).

## The routes

| Input | Route |
|---|---|
| A flat cut you made (no baked zooms, captions or transitions; 4K preferred) | the Pipeline |
| One raw clip, 1 to 3 min (a hook, a segment intro) | Cut stage → `storyboard.json` → `compose.py` → `snap-beats.py` → render |
| Several raw clips for one video | `ingest.py` (order and join into `source.mp4`) → the same on `source.mp4` |
| A long talking-head section (over 3 min) | Cut stage + `stutter-scan.py` + `CUT-REVIEW.html` at Checkpoint A → storyboard under the long-form doctrine → `gap-scan.py` + `beat-check.py` → render per section |
| A screen tutorial recorded in Tella (camera and screen as two tracks) | the Tella route |
| A tutorial recorded as two files (face + screen) | `sync-tracks.py` → Cut stage on the face file → the screen as full-frame `clip` cutaways; or upload both into Tella |
| A whole video (hook + intros + sections + tutorials) | `assemble.py` → one 4K master, level-matched, with the chapter list |
| A Short (9:16) | not the default routine; see "Shorts" |
| A channel you want to learn from | `teardown.py`; see "The teardown" |

Two checkpoints per video; everything else runs unattended. **A, the cut:** `PAPER-CUT.md` (plus `CUT-REVIEW.html`
when long); you answer in plain words ("keep the earlier take of the studio line"). **B, the plan:** `storyboard.json` +
`snaps/sheet.png`, every card moment as a still. Then the render, `verify-render.py` on the file, delivery.

**The hook gate** (every hook, at Checkpoint B):
- The first 3 seconds convince someone to watch to the end. The first frame is a meaningful image, not a settling camera.
- It works muted: the first overlay says the promise on its own. The first spoken word survives: no sound, card
  entrance or cut lands on it.
- The promise has a payoff time: `"loops": [{"question": "...", "planted": 2.1, "payoff": 412.0}]` in the storyboard,
  checked in the assembled master. One main loop open at a time, one secondary at most; an object that comes back without
  resolving anything is a callback, not a closed loop. Close the promised lesson before any call to action.

## Recording so the cut works

- 4K at 30 fps (29.97 is fine), standard colour, flat (no in-camera zooms, captions or transitions), the mic on every
  file, one framing per session, a second of silence at each end. 1080p goes soft past ~112% zoom; 4K holds 200%.
- **Fluff a line? Pause about two seconds and restart the whole sentence from its first word.** The last take wins; redo
  the full sentence when a number, name or price came out wrong. "Cut that" or "scratch that" drops a stretch.
- No spoken slates or notes to yourself (they are speech and get kept); clap or hold fingers up instead. Say lists as
  lists, name tools out loud (logos come from the name), say money in full ("a thousand dollars a month", never "1K"),
  point where a graphic should go, leave the pause after a joke, end a segment on its outro line.
- Two-file tutorials: face and screen recorded at once, both with the mic, one clap, the same file stem.

## Scripts (`scripts/`)

| Script | Does | Options |
|---|---|---|
| `ingest.py` | probe, order and join several raw clips; `ingest.json` maps source time back to (clip, time) | `--raw --out [--concat] [--order A,B] [--only A,B] [--name]` |
| `sync-tracks.py` | audio cross-correlation offset between a face file and a screen file | `--a cam --b screen [--write-aligned DIR] [--window 180]` |
| `paper-cut.py` | what to remove from a raw take: restarts, "cut that", retakes (keeps the last), false starts, long pauses | `--transcript --duration --out-dir --speech`; writes `cut-list.json` + `PAPER-CUT.md` |
| `hand-cut.py` | rebuilds `cut-list.json` from the lines you keep | `--keep A-B` (starts of the first and last kept word; `A-B!` keeps it whole) `--transcript --speech --duration --out-dir` |
| `tighten-cut.py` | trims lead-ins, tails and inner pauses by the sound | `--audio --cut-list --out [--lead 0.07] [--tail 0.11] [--maxgap 0.30]` |
| `sliver.py` | what edge-audit lets through: breath-only segments, heads carrying a dropped word's decay, tails leaking the next onset, edges under 40 ms | `--cut-list --audio [--fix]` |
| `edge-audit.py` | every cut edge checked by the audio: starts or ends mid-sound, restart fragments | `--audio --cut-list --transcript [--keeps FILE] [--fix] [--threshold 300]` |
| `apply-cut.py` | one frame-accurate re-encode into `public/input-video.mp4` + `cut-map.json` (every jump cut) | `--input --cut-list --out [--fps 30] [--crf 16]` |
| `dead-air.py` | every pause in the flat cut over 0.40 s after a sentence end (0.45 s elsewhere), by the audio | `W [--plan] [--keep T] [--max 0.45] [--max-sentence 0.40] [--target 0.30]` |
| `patch-cut.py` | small fixes to a cut list | `--cut-list` with `--add A-B`, `--drop T` or `--drop-flat A-B` (flat time, mapped back through `cut-map.json`) |
| `stutter-scan.py` | word-level stutters and a retake pass on the flat-cut transcript, a second opinion | `--transcript --out-dir` |
| `cutlist-to-edl.py` | the cut list as an EDL for the side-by-side review page (`node build-edl-review.mjs`) | `--cut-list --out` |
| `phrase-times.py` | where a phrase is said (start of its first word, end of its last) | `--transcript "phrase" ... [--after T]` |
| `compose.py` | `storyboard.json` → `public/index.html` | `--spec --out [--shared DIR]` |
| `beat-check.py` | each anchored element enters 0.10 s after to 0.60 s before its word; fails unanchored cards and a stale transcript | `--index --transcript [--suggest] [--allow-stale] [--video]` |
| `snap-beats.py` | one snapshot per beat and per state inside a beat, tiled into `snaps/sheet.png` | `--project [--at T ...]` |
| `gap-scan.py` | long-form coverage: stretches with no overlay and no camera move; density per 90 s | `--index [--early 15] [--body 20] [--max 30]` |
| `storyboard-md.py` | the delivery `STORYBOARD.md` from one or more storyboards | `--title --project dir:slug:title --out [--note] [--concern]` |
| `broll-conform.py` | a stock clip, generated clip or still → a cutaway (30 fps, no audio, a keyframe every 15 frames, BT.709) + a 3-frame sheet + the beat to paste | `--in --out [--start] [--dur] [--4k] [--grade] [--push 1.08] [--vf FILTERS]` |
| `window-patch.py` | a render-ready copy covering only [T0, T1], for a fix inside a long render | `--public --t0 --t1 --out` |
| `verify-render.py` | checks the rendered file: black runs, size, BT.709 tags, bitrate, duration, A/V, clipped words | `--render [--index] [--res] [--words --kept] [--out]`; exit 1 on a FAIL |
| `assemble.py` | `assembly.json` → one 4K master at -14 LUFS + `ASSEMBLY.md` + `chapters.txt` | `--manifest --out [--gpu] [--keep-work]` |
| `tella-pull-source.py` | downloads a Tella raw recording from the signed URL `list_sources` returns | `--url-file --out [--wav] [--audio-only]` |
| `tella-cuts.py` | `cut-list.json` → the `cuts` array for Tella's `update_clip`, lead-in offset applied | `--cut-list --source-duration --clip-max` |
| `tella-timeline.py` | a cut Tella clip's sentences on the playback timeline, with clicks and screen activity | `--clip-dir --cuts-json --key [--tella-words] [--clicks] [--activity]` |
| `screen-activity.py` | how much a screen recording changes over time (`activity.json`) | `--video --out [--fps 2]` |
| `teardown.py` | measures any video; counts a storyboard exactly; compares reports | `--video` / `--storyboard` / `--compare`, `--out [--transcript] [--every 2]` |

`formats/claude_chat.py` is the AI chat window (format 13b).

## Cut stage (raw clip to flat cut)

```bash
mkdir -p "$W/raw" "$W/public" && cp "<card or folder>/<clip>.MP4" "$W/raw/"     # eject the card only after the copy is confirmed
ffmpeg -y -v error -i "$W/raw/<clip>.MP4" -vn -acodec pcm_s16le -ar 16000 -ac 1 "$W/audio-raw.wav"
npx hyperframes transcribe "$W/audio-raw.wav" -d "$W" --engine parakeet --json && mv "$W/transcript.json" "$W/transcript-raw.json"
auto-editor "$W/raw/<clip>.MP4" --edit audio:-30dB --margin 0.12s,0.35s --export v1 -o "$W/speech.v1"   # speech chunks by the audio
python3 "$SK/scripts/paper-cut.py" --transcript "$W/transcript-raw.json" --duration <seconds> --out-dir "$W" --speech "$W/speech.v1"
#   read PAPER-CUT.md; fix misreads with hand-cut.py (it rewrites cut-list.json)
python3 "$SK/scripts/tighten-cut.py" --audio "$W/audio-raw.wav" --cut-list "$W/cut-list.json" --out "$W/cut-list.json"
python3 "$SK/scripts/sliver.py" --cut-list "$W/cut-list.json" --audio "$W/audio-raw.wav" --fix
python3 "$SK/scripts/edge-audit.py" --audio "$W/audio-raw.wav" --cut-list "$W/cut-list.json" --transcript "$W/transcript-raw.json" --fix
python3 "$SK/scripts/edge-audit.py" --audio "$W/audio-raw.wav" --cut-list "$W/cut-list.json" --transcript "$W/transcript-raw.json"  # 0 issues
python3 "$SK/scripts/apply-cut.py" --input "$W/raw/<clip>.MP4" --cut-list "$W/cut-list.json" --out "$W/public/input-video.mp4"
ffmpeg -y -v error -i "$W/public/input-video.mp4" -vn -acodec pcm_s16le -ar 16000 -ac 1 "$W/audio.wav"
npx hyperframes transcribe "$W/audio.wav" -d "$W" --engine parakeet --json      # transcript.json, in flat-cut time
python3 "$SK/scripts/dead-air.py" "$W" --plan
#   each proposed range: patch-cut.py --cut-list "$W/cut-list.json" --drop-flat A-B, then edge-audit to 0 issues,
#   apply-cut, re-transcribe, and dead-air again until it prints 0 pauses
```

The order on every clip: paper cut → hand fixes → tighten-cut → sliver → edge-audit to 0 → apply-cut → re-transcribe →
dead-air → patch-cut `--drop-flat` → edge-audit → apply-cut → re-transcribe → dead-air prints 0. `<seconds>` comes from
`ffprobe -v error -show_entries format=duration -of csv=p=0 <clip>`. edge-audit's `--keeps FILE` holds your hand-cut
`--keep A-B` arguments; leave it out after a plain paper cut.

**paper-cut.py** keeps the **last take** of every line, cuts restarts inside a sentence from the audio, drops other takes
of the same beat, honours "cut that / scratch that / let me redo / start over / take two" (the marker and the sentence
before it go), drops short false starts and trims long pauses. A later take that only adds a leading filler ("So, ...")
loses to the clean earlier take.

**Where it misreads (fix with hand-cut.py):** a list read as restarts ("candles, soap, t-shirts"); a spoken slate; a
retake with the wrong number in it; one sentence retaken many times without a pause (Parakeet merges the takes and the
paper cut keeps fragments: `--keep` the last clean take); the same phrase twice with a different ending ("is able to find
the fact, is able to find a screenshot" is a restart: keep the second). hand-cut keeps restarts spoken without a pause, so
after every apply scan the flat transcript for the same 3 to 4 word phrase twice within 7 s and remove the real ones.

**Edges:**
- **Sentence starts come from Parakeet, ends from the audio.** Parakeet stretches a last word into the pause (one read
  8.8 s long), so silences never come from word gaps. It also marks phrase starts up to 0.4 s early after a pause, the
  source of "too much breathing room": tighten-cut took one cut from 3:12 to 3:02 with no word lost.
- **Audit every edge by the audio, every time.** A leaked sliver of a dropped take hides in the transcript but plays as
  "right. [ght] A couple hours ago". Heads move BACKWARD from the first kept word to the quiet gap (searching forward
  clipped words); check the joins of the new file the same way.
- **Dead air:** no pause over 0.40 s after a sentence end, 0.45 s elsewhere; `--plan` brings each to 0.30 s with both new
  edges in room tone, `--keep T` protects a deliberate beat. Run it on every section and every Tella flat cut.
- **A cut in the quiet dip before a sentence's last word deletes that word,** and edge-audit passes it. After every
  apply, compare the last word of each kept segment with the fresh flat transcript; when the next word runs straight on,
  cut through speech at the word boundary and check the join by ear and by transcription.
- **Deliberate air:** a segment of your own room tone (`"room_tone": true`, the quietest 0.5 s of a long pause), never
  digital silence, with its picture hidden under a full-frame cutaway.
- **Raw files over ~3 minutes:** Parakeet can drop whole sentences. Transcribe ~25 s windows cut at auto-editor
  silences, shift each window's word times by its start, merge.

**apply-cut.py** does one frame-accurate re-encode (trim/atrim + concat, 20 ms audio fades at every join, CRF 16, a
keyframe every 30 frames, 30 fps, BT.709) straight into `public/input-video.mp4`, every edge snapped to the source frame
grid (without the snap, the picture drifted 4 frames behind the voice over 24 segments). The output is checked against
`cut-map.json` (duration within a frame, A/V under 0.12 s); a DRIFT line means do not dress that file. `cut-map.json`
lists every jump cut: put cutaways on those cuts and dress at most one or two of the rest.

## Pipeline (flat cut to 4K MP4)

```bash
VIDEO="/path/to/flat-cut.mp4"; mkdir -p "$W/public" "$W/snaps"
# 1. Probe + 16 kHz mono audio, then transcribe locally
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,color_transfer \
  -show_entries format=duration -of json "$VIDEO" > "$W/metadata.json"
ffmpeg -y -v error -i "$VIDEO" -vn -acodec pcm_s16le -ar 16000 -ac 1 "$W/audio.wav"
npx hyperframes transcribe "$W/audio.wav" -d "$W" --engine parakeet --json
# 2. Re-encode at the SOURCE resolution with dense keyframes, or the render freezes on seek (the Cut stage did this already)
ffmpeg -y -v error -i "$VIDEO" -map 0:v:0 -map 0:a:0 -r 30 -c:v libx264 -crf 16 -preset fast -g 30 -keyint_min 30 \
  -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv \
  -movflags +faststart -c:a aac -b:a 256k -ar 48000 "$W/public/input-video.mp4"
# 3. Only for text behind you: the subject matte
npx hyperframes remove-background "$W/public/input-video.mp4" -o "$W/public/subject-matte.webm" --quality best
# 4. Storyboard → compose → checks → snapshots (Checkpoint B: read the sheet before rendering)
python3 "$SK/scripts/compose.py" --spec "$W/storyboard.json" --out "$W/public" --shared videos/_shared
npx hyperframes check "$W/public"
python3 "$SK/scripts/beat-check.py" --index "$W/public/index.html" --transcript "$W/transcript.json"
python3 "$SK/scripts/snap-beats.py" --project "$W"
# 5. Render 4K: the 1920x1080 composition renders at 2x. --gpu ignores CRF, so give the bitrate (45M = YouTube's 2160p
#    figure). About a minute per 30 s on a recent Mac; without a hardware encoder, drop --gpu.
PRODUCER_BROWSER_GPU_MODE=hardware NODE_OPTIONS=--max-old-space-size=8192 \
  npx hyperframes render "$W/public" --resolution 4k --video-bitrate 45M --gpu --workers 4 -o "$W/output-4k-raw.mp4"
# 6. Full BT.709 tags (the render leaves them "unknown" and QuickTime shows faces darker and redder). Lossless.
ffmpeg -y -v error -i "$W/output-4k-raw.mp4" -c copy -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -color_range tv -movflags +write_colr+faststart "$W/output-4k.mp4"
# 7. Check the FILE (exit 1 = do not deliver), then deliver
python3 "$SK/scripts/verify-render.py" --render "$W/output-4k.mp4" --index "$W/public/index.html"
mkdir -p "$HOME/Movies/YouTube Renders/<project>" && cp "$W/output-4k.mp4" "$HOME/Movies/YouTube Renders/<project>/<project>-4k.mp4"
```

**Snapshot every card moment before rendering** (a snapshot is seconds, a render is minutes) and read the PNGs; never
assume. What the composer does not build goes into `raw_html` / `raw_js`, or a hand-built page on the skeleton below
(copy `$SK/assets/fonts/*.woff2` into `public/fonts/` for a hand build).

## Composition skeleton

```html
<div id="stage" data-composition-id="..." data-start="0" data-duration="D"
     data-fps="30" data-width="1920" data-height="1080">
  <div class="video-wrapper" id="video-wrap">     <!-- push-over moves (format 3b) -->
    <div id="video-zoom">                          <!-- the camera -->
      <video id="bg-video" src="input-video.mp4" playsinline data-has-audio="true"
             data-start="0" data-duration="D" data-track-index="1"></video>
      <div id="behind-layer"> ...text behind you... </div>
      <video id="fg-matte" src="subject-matte.webm" playsinline muted
             data-start="0" data-duration="D" data-track-index="2"></video>
    </div>
  </div>
  <div class="card-host clip" id="host-card-01" data-card-id="card-01" data-anchor="spoken phrase"
       data-start="..." data-duration="..." data-track-index="3"
       style="left:0;top:0;width:1920px;height:1080px;visibility:hidden;opacity:0;">...</div>
</div>
```

Two nested wrappers on purpose: `#video-wrap` carries push-over moves, `#video-zoom` the camera; two moves on one
element conflict and fail QA. What must ride the camera (footage, text behind you, matte) lives inside `#video-zoom`;
front cards stay outside so they never scale.

## The composer (`compose.py`) and `storyboard.json`

The storyboard is the review artifact **and** the source: retiming a card is editing one number and rebuilding.

```json
{"id": "hook", "duration": 38.0, "video": "input-video.mp4", "origin": "52% 0%",
 "tag": {"n": 1, "of": 5, "label": "Thumbnails", "in": 0.2, "out": 5.3, "pos": "tr", "anchor": "-"},
 "beats": [
   {"type": "line", "id": "l1", "text": "You clicked on a thumbnail", "em": [4], "color": "cyan", "in": 8.5, "out": 11.6, "anchor": "clicked on a thumbnail"},
   {"type": "logo", "id": "yt", "src": "img/youtube.svg", "in": 11.85, "out": 14.9, "pop": 11.92, "pos": "tl", "anchor": "YouTube"},
   {"type": "list", "id": "ls", "pos": "tr", "in": 15.6, "out": 20.4, "anchor": "candles",
    "items": [["Candles", 15.9], ["Soap", 17.12, "a bar of soap"], ["T-shirts", 18.3]]}],
 "camera": [["creep", 0.3, 5.4, 1.10], ["set", 9.698, 1.0], ["punch", 18.3, 1.18], ["release", 21.0, 0.5]],
 "loops": [{"question": "Why that thumbnail?", "planted": 2.1, "payoff": 31.0}], "raw_html": "", "raw_js": ""}
```

| Key | What it is |
|---|---|
| `id`, `duration`, `video` | composition id, length in seconds (the flat cut), the footage file in `public/` |
| `origin` | the camera anchor, always on the top edge: `"52% 0%"` centred, `"38% 0%"` when you sit left |
| `tag` / `tags` | the chapter or progress tag; `tags` is a list (long form: it returns at every section) |
| `glass_bg`, `glass_bg_cut` | the tint glass lands on (light `rgba(255,255,255,0.18)` by default; a bright room takes `"rgba(17,17,17,0.55)"`), and the tint inside full-frame scenes on the wash (defaults to `glass_bg`; keep it light) |
| `loops`, `raw_html`, `raw_js` | the hook's open loops (checked at Checkpoint B, ignored by the composer); hand-authored formats |

Every beat has `type`, `id`, `in`, `out` and an `anchor` (the spoken phrase; `"-"` marks a deliberate unanchored beat,
written as `data-unanchored`). List and bullet items carry their own time and anchor (`["Soap", 7.12, "a bar of soap"]`;
the text by default, `"-"` = not spoken), so beat-check proves every item. Full-frame beats take `"transition":
"zoomthrough"` (the footage pushes in and blurs 0.22 s before the cut) or `"punch"` (a 2-frame pop on return), and an
optional `label` (the 88 px scene caption).

| Camera op | Does |
|---|---|
| `["set", t, scale]` | jumps to a scale; `["set", t, 1.0]` at every jump cut in `cut-map.json` (never carry a zoom across a cut) |
| `["creep", t0, t1, scale]` | slow push across a thought, `power1.inOut` |
| `["punch", t, scale]` | punch-in, 0.32 s `power2.out` |
| `["release", t, dur]` / `["reveal", t]` | back to 1.0 / a zoom-out reveal, 1.10 to 1.00 as a card enters |

- Positions: `tl` = left 70, top 96 (clears a desk mic); `tr` = right 70, top 96. A lower line holds ~33 characters at
  100 px (split longer ones); list items over ~18 characters need `"width"` and `"size"` on the beat.
- The composer's two sounds are `sfx/pop.mp3` (the logo pop, 0.34) and `sfx/typing.mp3` (search typing, 0.22), copied
  from your `--shared` folder; logos and images go in its `img/`.
- Each build prints the snapshot moments, the count of every format, and a WARN when the same device runs twice in a row
  (lower lines excepted). Fix it; never ship past it.
- Line icons: doc browser bolt chat money check user code video mail gear chart search shield lock robot globe cloud key
  alert folder eye bank chip.

**The AI chat window (13b) is one shared function:** `formats/claude_chat.py`, `chat_css()` + `chat_scene(p, prompt,
t_in, t_out, type_t0, type_t1, send, think_end, head, items, ..., attachments=[...], att_times=[...])` returning `(html,
js_lines)`: image thumbnails drop into the composer box, the prompt types in as you say it, the message sends, the answer
rows land on your words. Each word is a nowrap span with real spaces between words and the box grows from the bottom, so
any prompt wraps (non-breaking spaces once made a prompt run out of the box). Call it from a build script; never hand-roll it.

## Format library

Vary the formats; never the same device twice in a row. `*` = built and snapshot-tested but used in fewer real
deliveries: read its first real snapshot with extra care and name it at Checkpoint B. The composer builds every format
with a type below (the JSON shapes are in compose.py's docstring); the specs give the numbers to check a snapshot
against, and to hand-build the rest.

| # | Format | Use for | Composer type |
|---|---|---|---|
| 1 | Big number behind the head | money and stakes figures | hand-built |
| 2 | Lower line | **any single line of copy, the default** | `line` |
| 3a | Glass card | lists, deliverables | `list` |
| 3b | Extended-left bullets | the same, for variety | `bullets` |
| 3c* | Glass pop-out | a short titled list when 3a and 3b were just used | `popout` |
| 4a | Logo card | naming a tool; the default for a list of tools | `logo` |
| 4b | Full-screen site cutaway | a site introduced as the subject, a glance under 3 s | `site` |
| 4c* | 3D floating browser | a site you talk about, held longer, or that scrolls | `browser3d` |
| 4d* | 3D screenshot fan | two or three screenshots at once: posts, wins, app screens | `fan3d` |
| 5 | Punchline chip | jokes, pattern interrupts | `chip` |
| 6 | Flow diagram | a long process with a detail line per step | hand-built |
| 7 | Ascending staircase | steps where each one earns the next | hand-built |
| 8 | Funnel | volume narrowing toward money | hand-built |
| 9 | Chapter tag | naming the section you just entered | `tag` |
| 9b | Progress tag | the same with N pips, on a numbered series | `tag` with `n`, `of` |
| 9c* | Slot wall | the video's parts as sockets, planted empty in the hook | `wall` |
| 10 | Success stamp | the moment something works | hand-built |
| 11 | Description pointer | "link in the description" | `pointer` |
| 12 | Key-word highlight | long form only: two or three key words | hand-built |
| 13 | Prompt window | reading out a prompt you give an AI | hand-built |
| 13b | AI chat window | the chat app itself: images drop in, the prompt types, the answer lands | `formats/claude_chat.py` |
| 14 | Subscribe bar | the ask, mid-video | hand-built |
| 16 | Shimmer sweep | a hero line | `"shimmer": true` on `line` |
| 17 | Vignette + grain | the awkward beat after a joke | `vignette` |
| 18 | Article cutaway with highlighter | one headline or quote from a page | hand-built |
| 18b | Doc read | two or three passages from one page, the rest out of focus | `doc` |
| 19 | Photo card | a named person | hand-built |
| 20 | Full-frame video cutaway | footage that needs hand work | hand-built |
| 20b | Before/after wipe | inside an image cutaway: the before becomes the after | hand-built |
| 20c | Clip | a full-frame cutaway: your screen, archive, stock, AI B-roll | `clip` |
| 21 | Logo swap plate | "X versus Y" | hand-built |
| 23 | Tutorial layout | screen + face in one glass composition | not built yet |
| 24* | Stat tiles | two to four numbers that belong together | `stats` |
| 25* | Growth card | one number that grew, with its shape | `growth` |
| 25m* | Chart morph | the growth bars turn into the trend line | `"morph": true` on `growth` |
| 26* | Bar comparison | "this takes X, that takes Y" | `bars` |
| 27* | Pipeline | three to five steps lit one by one | `pipeline` |
| 28* | Hub | one idea and the parts it is made of | `hub` |
| 29* | Equation | "A + B = C" said as one line | `equation` |
| 30* | Flowing paths | one thing becoming several, then one result | `flow` |
| 31* | Dashboard zoom | proof from a real dashboard: find one number, lift it out | `dashzoom` |
| 32* | Glass focus | walking through a table one row at a time | `lens` |
| 33* | Search → results | "I searched for X" | `search` |
| 34* | Magnetic dock | three or more tools named in a row | `dock` |
| 35* | Masked title | a full-frame chapter card | `masktitle` |
| 36* | Button → player | "watch this video", mid-video | `player` |
| 37* | Image reveal | a still opening behind slats | `image` |
| 38* | Exploded layers | what an app or a stack is made of | `layers` |
| 39 | World camera | a system you walk through: push in, pull back to reveal, travel | `world` |
| 40 | Numbered deck | the full-frame opener of each part of a numbered video | `deck` |
| 41 | Pills around the head | two to six short labels while you stay on camera | `pills` |
| 42 | Chat (bubbles, window, phone) | a conversation | `chat` |
| - | Check marker* | done and to-do lists: a check draws on each item | `"marker": "check"` on `list`, `bullets`, `popout` |
| - | Thumbnail grid | your own thumbnails; the cursor clicks one | `grid` |
| - | Coded scenes | money, catalog, room, plate, profile: B-roll with no stock | `scene` |

### When two formats compete

Pick the one that fits what you are saying. Tied: the one used least so far in this video (compose.py prints the
counts). Still tied: the one used least in your last video.

| You are... | Candidates | Pick |
|---|---|---|
| naming one tool | 4a, 34 | 4a; three or more tools in a row: 34 |
| showing a website | 4b, 4c | 4b for a glance under 3 s; 4c when you talk about it or it scrolls |
| giving numbers | 1, 24, 25 | 1 for one stakes figure; 24 for two to four that belong together; 25 when it grew and the shape matters (25m when the trend is the point) |
| explaining a process | 6, 7, 8, 27, 30 | 7 each step earns the next; 8 volume narrows to money; 30 one thing becomes several; 27 a quick sequence; 6 a long one |
| comparing | 26, 32, 21 | 26 for sizes (time, money); 32 for values read off a table; 21 for tool versus tool |
| listing | 3a, 3b, 3c, 41, check marker | never the same device twice in a row; the check marker for done or to-do; long form: no list panels |
| opening a section | 9, 9b, 9c, 35, 40 | 9c on a video with a spine; 40 for two to four numbered parts; 9b on a numbered series; 35 for a long break; 9 otherwise |
| showing an image or footage | 19, 20c, 37 | 19 for a named person; 20c for moving footage (20 when it needs hand work); 37 for a still |
| showing screenshots | 4d, 31, 4c | 31 when one number on it is the point; 4d for two or three; 4c for one site |
| typing | 13, 13b, 33 | 13 or 13b for a prompt to an AI (13b when the app itself matters); 33 for a search |
| saying one line | 2, 29, 5 | 29 only for an "A + B = C" line; 5 for a punchline; 2 otherwise |
| showing parts of a whole | 28, 38, 39 | 38 for layers of a product or stack; 28 for parts of an idea; 39 when the camera should move between them |
| naming a few short things on camera | 3a, 41 | 41 for labels of one to three words around you; 3a when you count a list |
| a conversation | 13, 42 | 42 for people talking; 13 for a prompt to an AI |
| reading from a page | 18, 18b | 18 for one headline; 18b for two or three passages |
| pointing to another video | 36 | mid-video only; at the end the YouTube end screen does the job |

### Copy on screen

- **2. Lower line (the default).** Any single line of copy, never in a card: bottom-centre, no box, always centred,
  ~100 to 104 px/700, letter-spacing -.015em, white with the key phrase cyan (amber for money). Words rise in staggered
  ~0.055 s (opacity 0→1, y 26→0, `power2.out`), never typed; animate `opacity`, not `display`, so the line never shifts.
  One span per word from `data-text` at load, container `font-size:0` (or whitespace doubles the gaps). Holds 5 to 7 s.
- **5. Punchline chip.** `rgba(17,17,17,.45)` glass, blur 18 px, radius 16, 64 to 76 px/700, the emphasis word solid
  magenta, bottom-centre 80 px up.
- **12. Key-word highlight (long form only).** A navy `#0005EE` block behind a word as you say it, white text, a glow;
  two or three words, never a sentence (word-by-word captions are for Shorts). ~78 px/700, bottom-centre, radius 14.
- **16. Shimmer sweep.** A cyan band crosses a hero line (`background-position` on a `background-clip:text` gradient),
  two passes of ~1.5 s; set the pre-sweep position inline or the words stay unpainted until the sweep.
- **29. Equation\*.** A glass strip bottom-centre (or `top`), 76 px terms rising on their words, `+` and `=` white at
  .6, the result cyan (`"em"`) or magenta (`"pay"`). Laid out from frame one so it never shifts; it takes the lower
  line's slot, never both.
- **41. Pills around the head.** Two to six glass pills (42 px icon + label, 88 px tall), each on its word: `sides`
  (alternating columns from `top` 290, clear of your face), `left`, `right` or `row` (bottom centre). `tone: "cyan"` for
  the one that matters, `"amber"` + `"mark": "x"` for a risk or a wrong answer. One to three words each; hidden until its
  word (glass that has not arrived blurs the footage).

### Cards and lists

Every light glass card uses one recipe:

```css
background: rgba(255,255,255,.18); backdrop-filter: blur(30px) saturate(1.25);
border: 3px solid rgba(255,255,255,.58); border-radius: 26px; box-shadow: 0 24px 80px rgba(0,0,0,.38);
```

- **3a. Glass card.** 600 px, monochrome (colour lives in the lower line): eyebrow 30 px/700 white at .92, items 64 to
  72 px/700 with white dots and no sub-text (each item stands alone: "Invite teammates", not "Invite feature" plus an
  explainer). Items start `display:none` and appear on their word, so the card grows with the list. Every text gets a
  dark `text-shadow`: at 18% white the card follows the footage behind it (a cyan eyebrow measured 2.4:1).
- **3b. Extended-left bullets.** `#video-wrap` pushes to scale 1.18, x 150 (0.75 s `power2.inOut`, origin `50% 0%`;
  back in 0.65 s), and the 173 px overhang covers the shift. Scrim `linear-gradient(90deg, rgba(0,0,0,.97) 0%,
  rgba(0,0,0,.82) 34%, rgba(0,0,0,.45) 46%, transparent 60%)`; items 68 px/700 at left 96, top 318, cyan dots, no card.
- **3c. Glass pop-out\*.** The 3b move with a glass panel at left 72, top 230 (40 px title, 62 px items, 560 to 820 px
  wide) that leaves 0.7 s before the release so the camera returns onto clean footage. Never zoom from `0% 50%`: it
  crops the head.
- **Check marker\*.** A 44 px ring per item; a beat after the item lands it fills cyan and a dark check draws in 0.3 s.
  Done and to-do lists only, not plain nouns.
- **1. Big number behind the head.** Full digits (`$207,000,000`, never `$207M`) so your head covers about one glyph in
  twelve. White, solid, never a gradient: ~230 px/700 + `-webkit-text-stroke: 5px`, centred at `top:17%`, counting up
  with `toLocaleString('en-US')` (~1.4 s `power2.out`). Inside `#video-zoom`: footage → number → matte. Supporting copy
  in front at the bottom, ~94 px/700, the key phrase amber. (The linter's `text_occluded` is the point here.)
  - Short figures lose digits behind a centred head: write the unit inline (`$1,000 A MONTH`, 200 px, left-anchored at
    150), or put the figure beside the head (170 to 200 px, no matte, 60 px clear of its edge measured on a frame).
  - **Counter split around the head:** a 190 px white number right-anchored so its last digit tucks ~24 px behind the
    hair (the head measured from the matte), a 120 px cyan unit 8 px clear on the other side (a tucked "/" vanishes),
    `font-variant-numeric: tabular-nums`. The count runs from the money word to the END of the amount word
    (`power2.out`, a 6% bump, a cha-ching at 0.07 on the landing); the unit enters on its word. Matte only that window
    (`ffmpeg -ss -t` → `remove-background --quality best`, `data-media-start="0"`); mark the text
    `data-layout-allow-occlusion`.
  - **Pixelated logo teaser:** mosaic a 480 px logo to 5x5 (`scale=5:5,scale=480:480:flags=neighbor`; 4x4 for a
    letterform logo, which still reads at 5x5), revealed in steps: blocks 48, 24, 12, clean, 0.1 s each.
- **24. Stat tiles\*.** Numbers 112 px (92 stacked) counting up in full digits over 1.1 s, 34 px labels; `layout: "row"`
  (full frame, a 76 px title) or `"stack"` (a column at `tl`/`tr`); `em_tiles` turns a number cyan. Only numbers you can
  source get a tile.
- **25. Growth card\*.** 600 px at `tr`/`tl`: the number counting up cyan at 120 px, then bars rising (the last one cyan)
  and a glowing white line drawing over them to a dot (`count_at`, `bars_at`, `line_at`). Once per video at most.
  **25m** (`"morph": true`): the bars thin to stems (1.1 s, 0.16 s apart) while a smooth Catmull-Rom line draws through
  their tops in 1.4 s at an even speed, then an optional `badge`.

### Sections

- **9. Chapter tag.** A pill top-right: a live cyan dot + 34 px/700 label, light glass, held ~5 s then dropped (one that
  stayed 76 s read as static), on its own `data-track-index` (`overlapping_clips_same_track` otherwise). **9b** (`n`,
  `of`) adds N pips (done, now, next) for the first ~5 s of each segment; the viewer sees the slots fill.
- **9c. Slot wall\*.** A glass strip top centre, one 264x74 slot per part: empty, dashed and numbered in the hook
  (`filled: 0`); at each section the live slot fills cyan with its name on the word (`filled`, `now`, `fill_at`; spent
  slots .56); at the recap (`recap: true`) every slot lights and a cyan thread draws under them. It replaces the progress
  tag on a video with a spine; never both in one section.
- **40. Numbered deck.** Two to four 380x520 glass cards (italic number, 112 px icon, a 40 px title of five words or
  fewer) under a `head` ("3 PREDICTIONS"). `now: 1`: the row arrives, the camera pushes in on card 1 (1.5x, 1.1 s), the
  others drop to .38; `now: k` slides from card k-1 to k (1.0 s); `recap_at` pulls back to the row. It returns at every
  part boundary; never with a progress tag in one section.
- **35. Masked title\*.** A letter-spaced eyebrow ("PART 2"), the word as a thin white outline filling solid from the
  bottom (1.5 s `power3.inOut`, with a cyan edge line and a small handle), then a 64 px sub line rising from behind a
  mask. `size` 220 px by default. Never over your face.

### Tools, sites and screenshots

- **4a. Logo card.** Logo only, no name (you say it): a 380 px glass plate, the logo ~264 px tall (150 px was "quite a
  bit too small"), `tl` at a desk, `tr` on a tight shot, one pop. **21. Logo swap plate:** one plate; the first logo
  slides out (x → -50) on the second name and the second slides in (x 50 → 0), one pop on the swap.
- **34. Magnetic dock\*.** White 114 px app tiles in a glass dock; the oversized cursor walks to each tool on its word,
  the tile under it swells to 1.75 on a smooth falloff and a tooltip names it. One driver tween, so any frame renders
  the same.
- **4b. Site cutaway** (`site`). The homepage fills the frame ~3 s: a 62 px chrome bar, traffic-light dots, the bare
  domain in a 21 px URL pill, no copy, a drift 1.00 → 1.06. From a real `npx hyperframes capture` (optional `scroll`).
- **4c. 3D floating browser\*.** A full-page capture in a 1340x830 window rising in already turned (rotateY 27→15°,
  rotateX 16→7°, z -420→0, 1.0 s `power3.out`), then a slow camera orbit toward it while the page scrolls (`scroll`, in
  displayed px); one sheen; `near` picks the edge closer to camera, `callout` rings a spot. No flip: the tilt only settles.
- **4d. 3D screenshot fan\*.** Two or three images in depth (the middle 30 px forward at 1.05, the sides turned 16° and
  70 px back) rising 0.14 s apart, the fan orbiting rotateY 5 → -5; `focus` brings one forward (z 160, 1.12) while the
  rest drop to .4. `"frame"`: card (560x700, default), `"phone"` (330x700) or `"browser"` with `domains`, `fit`
  (`"width"` = a long page from its top, `"contain"` = a whole post) and `scroll` (`{index, at, by, dur}`).
- **Screenshots are browser windows showing the page, never crops of video frames.** Posts come from X's official embed
  (see "Sourcing assets"). When a live page blocks headless capture, read its text in the browser, rebuild the long page
  in HTML with the site's fonts, then `"<Chrome binary>" --headless=new --force-device-scale-factor=2
  --window-size=760,2600 --screenshot`.
- **31. Dashboard zoom\*.** Your real analytics screenshot (one 16:9 screen; give `"size": [w, h]`): at `find_at` the
  camera pushes to `focus` (a rect in image px, zoom capped at 3.2x) and cyan brackets find it; at `lift_at` the tile
  lifts into a 760x420 glass card with leader lines back, then the number counts up with a delta chip and a sparkline.
  Real numbers only, read off the screenshot.
- **32. Glass focus\*.** A 1200 px card of up to six rows, all out of focus (a static blur); a glass lens glides to each
  row in `stops` on its word (0.6 s `power3.inOut`), sharp inside at 54 px with the value cyan. The lens's copy moves the
  opposite way to line up, and its glass is nearly opaque so the row never doubles.
- **33. Search → results\*.** A pill opens from 520 to 1200 px (0.55 s); from `type_at` the query types at `cps` (16) with
  a cyan caret; two to four result rows drop in. `"sound": true` adds typing for exactly the typing time.

### Explainers (full frame)

Every full-frame scene sits on an ambient three-radial brand wash plus a 96 px grid at .28, never flat black.

- **6. Flow diagram.** A rail 1840 px wide at left 40: N nodes of 320 px, 56 px gaps, a 44 px arrow centred in each
  (five nodes: lefts 0/376/752/1128/1504, arrows 326/702/1078/1454; recompute for another N). A node: a cyan number
  badge, a hand-drawn SVG glyph, a 30 px/700 two-line title, chips for specifics. One beat per spoken step (~6.4 s
  apart): the shaft draws (scaleX 0→1, origin `0% 50%`), the head fades, the node lands (y 34→0, scale .965→1), then a
  44 px detail line under the rail. Cyan for mechanical steps, amber for urgency, a magenta payoff banner once the rail
  dims to .5. No `drawSVG` (not in `gsap.min.js`).
- **7. Ascending staircase** ("therefore" where the flow says "then"). Treads 300x200, each +356 px right and -112 px up
  (lefts 60/416/772/1128/1484, tops 670/558/446/334/222), fixed height so the risers meet them. Risers span only the gap,
  (L+300, T+100) → (L+356, T-12), drawn with a dash sweep (`getTotalLength()`, `strokeDashoffset`). Treads arrive from
  below-left, the previous drops to .42, all return to .85 at the end; the last magenta, the rest cyan.
- **8. Funnel.** SVG polygons, not `clip-path` (borders do not follow it): bands 180 px tall, 14 px apart, narrowing 90 px
  a side: `200,280 920,280 830,460 290,460` / `290,474 830,474 740,654 380,654` / `380,668 740,668 660,848 460,848`.
  Cyan (reach) → amber (warming) → magenta (money); metrics count up inside the bands, text at left 1010. Every metric box
  shares one `left` on the centre axis (following the taper put boxes 45 and 90 px off). Done stages dim (band .5, panel
  .66, never lower or contrast fails).
- **27. Pipeline\*.** Three to five 290 px glass nodes; each lands on its word as a cyan light runs the connector, lit
  cyan while the previous settles white; `payoff: true` lands magenta. The fast version of 6.
- **28. Hub\*.** The idea in a 300 px glass circle with a cyan ring closing (`ring_at`), two to six parts arriving at the
  ends of spokes; `resolve_at` dims them to .56 and lights the centre ("all of that is really this").
- **30. Flowing paths\*.** An input pill left, two to four outputs, an optional result right, joined by S-curves and dim
  (.42) from frame one. A packet of light runs each path (0.9 s) and the pill lights on its word; at `result.at` light
  runs from every output 0.14 s apart and the result lands magenta; a second wave keeps it moving (`"repeat": false`).
- **38. Exploded layers\*.** One flat card tilts (rotateY -30, rotateX 16) at `split_at` and separates into two to four
  layers in depth (1.4 s, 0.22 s apart), labels on their layers, then a slow orbit.
- **26. Bar comparison\*.** A 76 px title, two to four rows of label (46 px) and bar, each on its word, growing 0.5 to
  0.9 s; the longest stops at 80% of the track; your row (`hi`) cyan with a glow, the rest white.
- **39. World camera.** One canvas in home-frame px (1920x1080 = zoom 1; nodes may sit off screen, or on a ring with
  `"polar": [cx, cy, r, deg]`). Node kinds: `card` (300 px: number, icon, 42 px label, 26 px sub), `pill`, `orb`, `hex`,
  `stat` (a 118 px number counting up + a cyan bar; `to` moves both on after the first count), `text`, `img`. Each node
  arrives on its word (glass stays hidden until then), can `lit` (cyan or `lit_color`), `dim` (.56; spent .33) and take
  amber `alerts`; `links` draw in 0.5 s and `run` sends a light along; `rings`, `window`, `dock` add circles, a window, a
  row of logos. `cam` = `[t, x, y, zoom, dur]`, one gesture each (`power2.inOut`, 1.0 s); a move that starts before the
  last ends fails the build. Open close on the thing you name (zoom 1.5 to 1.8), pull back to 0.8 to 1.0 as you say what
  it connects to, push to the next. Text 32 px or more at the zoom it is read at (the composer warns over 3.2).

### Cutaways and pages

- **18. Article cutaway with highlighter.** Full screen while you read from a page, cut in where your eyes drop (in a
  cut, the jump cut). Rebuild the page in HTML (real headline, byline, date, hero image, the site's own font): headless
  Chrome hits consent walls, and a rebuild makes the highlighter exact. Headline words get an amber block each
  (`rgba(255,185,4,.66)`, scaleX 0→1) stroked in one pass as the page appears (0.14 s a word, 0.035 s stagger), then a
  zoom into the headline for the rest of the read (1.0 → 1.42, `power1.inOut`), clipped under the 62 px chrome bar.
  Hard cuts in and out.
- **18b. Doc read.** The page rebuilt from the real kicker, title, date and paragraphs (a mark that is not verbatim fails
  the build; `"theme": "dark"` for dark pages, which get an amber underline). 0.35 s before each mark's word the camera
  glides to it at `zoom` (1.3), and on the word it is stroked in one pass; `focus` blurs the rest (a static copy; only
  opacity moves). Highlight on "highlight", zoom on "zoom": a mark can take its own `"zoom"` and `"move": false`.
- **19. Photo card.** Light glass 420 px wide, top-left: a 372 px square photo (radius 16), name 40 px/700, role 26 px.
  In on the name (x -40 → 0), gone ~1.8 s later.
- **20. Full-frame video cutaway** (hand-built). Your own screen recording first, public-domain archive for a metaphor
  second, then nothing. The `<video>` is a direct child of the root (`class="cutaway-video clip"`, its own timing
  attributes, `muted`, `z-index:20`); inside a timed wrapper it fails lint and shows the wrong frames.
  `object-fit:contain` does not paint its letterbox: `pad` to 16:9 with ffmpeg. Crop recordings to the window, re-encode
  like the footage (30 fps, dense keyframes, no audio), hard cuts, drift 1.0 → 1.04, 2 to 4 s; it hides a jump cut.
- **20b. Before/after wipe.** Two layers in a 1600x900 plate; the opaque after layer goes from `clip-path: inset(0px
  1600px 0px 0px)` to `inset(0px 0px 0px 0px)` (px on both ends so it interpolates) while a 5 px cyan line rides the
  edge, 0.65 to 1.1 s on the verb.
- **20c. Clip** (`clip`). Format 20 in the composer (muted, root level, z 20, drift, hard cuts, `anchor` on your words)
  for screen, archive, stock and AI B-roll conformed by `broll-conform.py`; an optional `label` or checklist (`items`).
- **37. Image reveal\*.** An image behind seven dark slats that close to their centres on `reveal_at` (1.1 s, 0.12 s
  apart), then a push 1.00 → 1.06; `"close": true` shuts them before the cut back. Stills only.
- **13. Prompt window.** A dark window, the prompt typing in as you read it (a cyan mic glyph and "Dictated" if you
  dictate). Characters start `display:none`, never `opacity:0`, or the caret parks at the finished width.
- **42. Chat.** Messages one by one: yours (`me`) cyan with dark text, theirs (`them`) white. `float` (up to five bubbles
  beside you), `window` (a dark app window that grows with the thread and scrolls once full) or `phone`. No anchor unless
  you read a message out. A client message is your example or a real one with permission, never made up.
- **36. Button → player\*.** A glass "Watch this next" pill grows into a 600x444 player at `morph_at` (1.1 s), the play
  icon travelling into the thumbnail; the real thumbnail, title and length fill in and the scrubber moves.
- **Thumbnail grid** (`grid`). Six of your thumbnails in a 3x2 grid; the oversized cursor clicks one (`click_index`,
  `click_at`) and the rest dim. Get them with `yt-dlp --flat-playlist -j <channel url>` and
  `https://i.ytimg.com/vi/<id>/maxresdefault.jpg`.
- **Coded scenes** (`scene`, no stock): `money` (amber $ chips drop on the word, never a digit), `catalog` (frames fill,
  one shine), `room` (furniture drops into a line-art room), `plate` (a phone with a plate: sweep, sparkles, steam),
  `profile` (the avatar gets its ring on "headshot"); `steps` time each kind, `label*` keys add the caption.

### Accents and asks

- **10. Success stamp.** A cyan circle with a dark check, a 62 px/700 label, glass with a cyan border, scale .86 → 1
  `back.out(2)` ~0.45 s (the house's one overshoot), bottom-left, ~5 s, on your own word ("boom", "it worked"), never on
  a read of the screen.
- **11. Description pointer** (`pointer`). A glass bar at bottom 34, "Everything is linked in the description" (cyan on
  the link phrase), three chevrons cascading beneath (0.14 s stagger, ~0.78 s cycle) on a finite loop, never `repeat:-1`.
- **14. Subscribe bar.** A pill glass bar: your channel mark in a dark avatar circle, the name 42 px/700, a 22 px/500
  tagline, a YouTube-red `#FF0000` pill 30 px/700 pulsing a finite 3 times (scale 1.08). Away from your head, under
  ~720 px wide.
- **17. Vignette + grain** (`vignette`). Radial darkening and fine grain: a beat, not a look (the pause after a dad joke).
- **23. Tutorial layout (not built yet).** The screen as a rounded plate, your face in a rounded crop bottom-right (a
  360x540 corner, right and bottom 48, radius 32; full to corner in 0.6 s `power3.inOut`, 0.3 s before the word),
  switched with `tl.set`, never a class toggle (not seek-safe).

### Rejected (do not rebuild)

- Freeze-frame and paper-and-tape dressing; an outro or end card; a "Next video" pill at the end (the YouTube end screen
  does that job); payment or system notification banners.
- Typing with a trailing caret for lower lines; word-by-word highlighter pacing on an article (one stroke, then zoom).
- The flash cut on a return (two white blinks read as a mistake): for energy use the fast punch, or leave the cut naked.
- Dark blue `#0005EE` for highlighted words (it disappears on dark footage); magenta outside the chip and payoffs.
- Bounces, elastic type, spring stacks, particle logos, idle wobble; generic stock of a smiling founder at a laptop.

## Finding explainers in the transcript

Diagrams (6, 7, 8, 27, 30) are **found, not requested.** Scan the transcript for enumeration ("first / second / third"),
a sentence that promises a shape ("the way this works is", "there are three"), chained causation ("and then", "which
leads to"), stage vocabulary ("top of funnel", "cold / warm") and named tools in a list (they become chips).

| The passage says... | Format |
|---|---|
| A then B then C, each a distinct action | 6 flow diagram (27 when quick) |
| B is only possible because of A: a climb | 7 staircase |
| many become few become paying | 8 funnel |
| one thing becomes several | 30 flowing paths |
| it used to be X, now it is Y | 20b before/after wipe |

Node titles are 2 to 4 words in your phrasing; detail lines are your own point tightened, never an invented claim,
number or step ("about seven days" stays "seven days"); each beat is the word start of the sentence that introduces the
step; duration = last beat + ~8 s; no outcome said, no payoff banner. **Propose before building** (the passage, the
format, the step labels, in one short message): a diagram is 30 to 40 s of screen time, worth one round of confirmation.

## Read the footage, not just the transcript

1. Find the shot changes: `ffmpeg -v error -i in.mp4 -vf "select='gt(scene,0.12)',metadata=print:file=-" -f null -`.
2. Place per shot and measure the face-safe zone; overlays sit opposite you. Framings measured so far (add yours):
   - You sit LEFT: cards live right of x 1000.
   - You sit CENTRE at a desk with a mic (mic head around x 500 to 800, y 330 to 500): cards live left of x 660; `tl`
     clears the mic; an 840 px card at left 62 reached x 902 and covered the face.
   - A tight shot, mic bottom-right: your face fills x 750 to 1150, your chest the bottom-left. Cards go top-right (left
     1220, 640 px wide) or top-left (left 62, top 80, under ~720 px wide, above y 220); nothing bottom-left.
3. **A card never covers your face.** When the copy will not fit the safe zone, make it a lower line instead of
   shrinking the card; check the card's edge against your hair in a snapshot.
4. Re-anchor the camera per shot (`38% 0%` when you sit left, `52% 0%` centred), and release every move before a cut.
5. **If the frame already says it, do not say it again.** A big number once duplicated a timer held up to the lens, and
   an out-of-focus hand cut its first digit through the matte. The overlay went.

## Long-form doctrine

- **One persistent world.** A long video is one space the camera moves through, not a stack of unrelated cards. Decide
  the spatial grammar first (left to right = toward the outcome, up = a person, down = the system).
- **The chapter fixture returns at every boundary** (progress tag, slot wall or deck); an open loop is planted in the
  hook as something visibly incomplete (empty slots, a ghosted stack) and filled on screen, never "we'll come back to this".
- **One element at full brightness at a time.** What is drawn stays, dimmed but legible (context .56, spent .33, labels
  never below luma 90); retire a finished prop to 0, not 0.3. About 20 on-screen words per section, no sentences;
  everything reads in under 2 seconds.
- **Pacing:** no stretch without an overlay or a camera move over 15 s in the first 90 s, 20 s after, 30 s ever
  (`gap-scan.py`); about 7 overlays + 7 camera moves per 90 s. One card across a topic span (an item building midway)
  beats five flashes. Enter 0.15 to 0.25 s ahead of the anchor word; never divide a section evenly.
- **One gesture, not two moves.** Two moves in a row on one subject read as a glitch: merge them into one move with one
  symmetric ease (`power2.inOut`). A front-loaded ease (`power3.out`) on visible footage rushes, then crawls.
- **A full-frame graphic moves as a camera over one canvas:** push in on the part you name, pull back to show what it
  connects to, travel to the next, one move at a time (`world`, `deck`).
- **One opacity owner per element per window:** two tweens on one element's opacity strobe in the master. Fade the child
  or the wrapper, never both; let the lint's `overlapping_gsap_tweens` warning stop the build.
- **Audit audio at the acoustic level** (digital zero inside pauses: fill with room tone; level cliffs at joins) and
  verify motion on contiguous frames (see "Verify and deliver"): every gate can pass and a viewer still sees a freeze.
- **Compose per section** (hook, each intro, each body section) and join with `assemble.py`: each stays under the
  heavy-overlay budget, and a note costs one section's render.

**The house rules for long form:**
- **Your face is not the default background.** Aim for 40% or more of a talking section full-frame on the brand wash,
  the animation alone on screen. An abstract explanation (what a tool can do: files, programs, an output folder) goes
  full-frame as a `world` scene, never as a card over your face.
- **Variety over lists.** No list or bullet panel in a long-form body: each list becomes a device (pills on each phrase,
  a `world` loop, one device per number, a pipeline).
- **Every person or job you name gets footage of that person:** a 2.6 to 3.4 s full-frame stock `clip` right after you
  describe the job, before the tool or answer is revealed; one or two AI shots of you where it lands a joke.
- **A board you fill one by one starts blurred:** each card shows only its icon, blurred, and clears on its own word.
- **Show a change the way you tell it:** "it was dark blue at first, I didn't like it" means dark blue first, switched on
  "didn't".
- **An app you name gets a designed window** (13b, its empty start state), not a screenshot of your real one; **a website
  you name gets the real page** (a 2x capture in a browser window), held until you move on.
- **Every on-screen click makes a light click** (0.28) on the frame the cursor bottoms out; a silent click reads as a mistake.
- **A thing you name in a joke gets its real picture** (say "chips" and two real bags sit either side of you): product
  photos from Open Food Facts (`cgi/search.pl?...&json=1`, swap `.400.jpg` for `.full.jpg`; CC BY-SA, so credit it),
  cut out with `npx hyperframes remove-background photo.jpg -o photo-cut.png` (pad a frame-filling photo 20% first),
  cropped to the alpha box, root-level `<img class="clip">` either side of you, in on the word with one pop.

## Camera

**Top-anchored origin, always** (`52% 0%` centred, `38% 0%` when you sit left): a centre-anchored zoom crops your head.

| Move | Numbers |
|---|---|
| Punch-in on emphasis (the number, the promise, a punchline) | 118 to 125%, 0.30 to 0.35 s, `power2.out` |
| Slow creep across a thought | 110 to 112% over 5 to 10 s, `power1.inOut`; release on the next cut |
| Zoom-out reveal | 110 → 100% over 0.5 s as a card enters |
| Snap back | to 100% at every shot change; never carry a zoom across a cut |
| Budget | 3 to 5 moves per 40 s hook; long form about 7 per 90 s |
| Limits | 1080p source: 112% at most; 4K: 150% freely, 200% for a deliberate crash-in |

- Compensate hero text for the zoom: at scale 1.12 with a 52% origin, a left-anchored element drags ~105 px left.
- **Jump cuts stay naked by default.** Dress one only when the energy changes (a pivot, a joke landing, a section
  start): a fast punch (scale 1.04 → 1.00 over 0.12 s), a zoom-through (scale up with a 10 px blur out) or a micro whip
  (12% x-shift with blur, 0.25 s). One or two per 40 s hook, at most one per 10 s in long form, never mid-word. On a long
  camera-only stretch, switch framing between jump cuts (1.0 / 1.09) so each reads as a punch, not a bump.
- **Put every reset on the jump frame.** Cut-map times are not frame-aligned: a `set` at 10.34 lands on the frame at
  10.367 while the footage jumped at 10.333, a one-frame double cut. Measure the jump frames once from a low-res decode
  (the max frame difference within ±4 frames of each cut) and set at `jump/30 - 0.003`.

## Pacing

- Hooks: about 6 overlay moments per 37 s (about 10 overlays + 4.5 to 7.5 camera moves a minute). Cards hold 3 to 7 s;
  past 7 s they need internal motion (staggered items, a count-up). Enter 0.4 s `power2.out`, exit 0.35 s `power2.in`;
  no bounces, no 3D flips, and blur never animates. One hero element at a time (a chip may sit with a logo card).
- **Motion from the first frame of a hook.** One pattern that worked: four short clips of your own work in glass cards
  around you (440x248 at x 36 / 1444, y 128 / 400), in 0.12 s apart from 0.35 s, all playing at once, out by 5.8 s;
  the title line lands about 1 s after the open, not on frame 0. The clips are root-level muted videos.
- **Reaction hooks (news, launches):** the hook moves the whole time; everything you name is on screen on the word
  (start a clip ~0.1 s in so its reveal hits the word). A count gets a click-click montage ("more than 20 releases":
  11 cards, one per ~0.3 s, a small counter). Event cutaways: one clean shot per clip (official streams switch cameras
  mid-shot), checked frame by frame. Posts 1560 px wide (1040 was unreadable on a phone), dark glass on a bright set, no
  big number over your face, a tag gone before the next full-frame cutaway.

## Sound

**Silence is the default. A sound has to earn its place:** what on screen makes this noise? If nothing would physically
make a sound, there is no sound. One or two per hook (eight in a 38 s hook was "way too busy").

| Sound | Allowed on | Volume | Never on |
|---|---|---|---|
| Typing | real typing, a prompt window or a search typing in, for exactly the typing time | 0.22 | anything that is not a keyboard |
| Pop | a logo appearing (4a, 21) | 0.34 | copy: not a chip, not a caption |
| Click | every on-screen cursor click | 0.28 | anything without a cursor |
| Ping / notification | a phone notification, literally | to taste | a number landing, a reveal, an accent |
| Cha-ching | a money count landing | 0.07 | anything louder than a whisper |
| Whoosh / swish | nothing confirmed | | **copy of any kind**: text arrives on motion, never on a sweep (the most common mistake) |

**Wiring:** `<audio id="sfx-typing" src="sfx/typing.mp3" data-start="8.22" data-duration="1.50" data-track-index="10"
data-volume="0.22"></audio>` as a direct child of the composition root, never inside a wrapper. Every `<audio>` needs an
`id`, or it is silent in the render while the preview plays fine (`check` reports `media_missing_id`). Overlapping sounds
need separate `data-track-index` values; trim any sound that would run past `data-duration`.

**Sourcing:** the Epidemic Sound connector (`SearchSoundEffects` filtered by duration, `DownloadSoundEffect`; for music
`SearchRecordings`, `DownloadRecording` with stems, `EditRecording` to an exact `targetDurationMs`), checked as attached
first; or the free HyperFrames library (typing, key-press, click, click-soft, pop, ping, notification, chime and more).

**Align the audible peak, not the file start:** trim the silence before the transient (`ffmpeg -af
silenceremove=start_periods=1:start_threshold=-40dB`) so the peak lands within two frames of its cause.

**Normalise before you mix:** library files differ up to 10x in level, so at one shared `data-volume` some vanish.
Peak-normalise each to -3 dBFS (read `max_volume` with `ffmpeg -i in.mp3 -af volumedetect -f null -`, then `-af
"volume=<-3 minus max_volume>dB"`), then use `data-volume` only for the mix. Sustained tones need less than transients.

**Verify the render contains each sound:** decode the render and the untouched footage to 16 kHz mono, gain-match on a
speech window, subtract, and read the RMS of the difference in each sound's window (offset to the file's own peak)
against two control windows (a pop shows ~650 against ~30). Never compare against a previous render: two AAC encodes
differ enough to hide a quiet effect.

**Music:** a track with some tension under the hook (~18 s), then a calm lo-fi bed under the rest, ducked about 16 dB
(hook) and 19 dB (body) under your voice, then a -1 dB limiter, after the voice is at -14 LUFS (`assemble.py` levels it).
The simplest bed is `assemble.py`'s `music` key; for a ducked bed on a finished master (keep a no-music twin):

```bash
ffmpeg -i master.mp4 -stream_loop -1 -i bed.mp3 -filter_complex \
 "[0:a]asplit=2[voice][sc];[1:a]volume=-16dB,afade=t=in:d=1[bed];[bed][sc]sidechaincompress=threshold=0.02:ratio=10:attack=15:release=350[duck];[voice][duck]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89[a]" \
 -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 256k -shortest master-music.mp4
```

## Animating glass (read before writing any entrance)

**Never fade a glass element through an ancestor's `opacity`:** Chrome drops `backdrop-filter` while any ancestor is
below opacity 1, so the frosted panel is missing for the whole fade and snaps in late. Hold the host at opacity 1 and
animate the look of the glass:

```js
tl.set('#host', { visibility:'visible', opacity:1 }, t);
tl.fromTo(glassSel,
  { backgroundColor:'rgba(255,255,255,0)', borderColor:'rgba(255,255,255,0)',
    boxShadow:'0 24px 80px rgba(0,0,0,0)', x:60 },
  { backgroundColor:'rgba(255,255,255,0.18)', borderColor:'rgba(255,255,255,0.58)',
    boxShadow:'0 24px 80px rgba(0,0,0,0.38)', x:0, duration:.42, ease:'power2.out' }, t);
tl.fromTo(contentSel, { opacity:0 }, { opacity:1, duration:.36 }, t + 0.04);   // text is safe to fade
```

The blur is live from frame one but invisible without tint, so this reads as a fade with panel, border and copy arriving
together; the exit reverses it. Copy sitting directly in the glass element needs an inner span to fade. Plain opacity
fades are fine without backdrop-filter (lower lines). Glass that has not arrived stays hidden, or it blurs the footage.

## Traps that waste a render

**Long renders**
- **Disk capture stores every frame first:** 12 minutes at 4K asked for ~714 GB of scratch. Over ~2 minutes, stream the
  encode with one worker (`PRODUCER_STREAMING_ENCODE_MAX_DURATION_SECONDS=3600`, `--workers 1`; ~35 minutes for 12
  minutes of 4K). Parallel streaming painted the footage BLACK for long stretches; `--low-memory-mode` is not the fix.
- **A long single-session 4K capture can hang** in Chrome's screenshot call. Over ~5 minutes, render segmented with a
  fresh browser per segment and keep `--resume` for a retry: `HF_SEGMENTED_CAPTURE=true HF_SEGMENT_FRAMES=1500
  HF_SEGMENT_BROWSER_RECYCLE=1` plus the streaming settings (8:53 rendered clean in 30 minutes).
- **Black footage under parallel workers:** `--workers 1`, and run `ffmpeg -i out.mp4 -vf
  "scale=192:-2,blackdetect=d=0.4:pix_th=0.08" -an -f null -` on every long render.
- **The frame cache fills the temp folder** (16 GB in a day) at `<tmpdir>/hyperframes-extract-cache-<uid>`: delete it
  when no render runs, or move it with `--frames-cache-dir`. Before an assembly, check free disk (about 2 x minutes x
  0.34 GB). Delete the `work-*` folder a failed run leaves; zsh aborts an `&&` chain on an empty glob (`work-*(N)`).
- **A note on a long render costs a patch, not a re-render:** `window-patch.py --public "$W/public" --t0 T0 --t1 T1 --out
  "$W/patch-a"`, rendered with the same flags, then overlaid on the full render (`overlay` with
  `enable='between(t,T0,T1)'`) or spliced in frame-exact (12 ms audio fades). Start the window before the card's host
  enters; prove alignment with `psnr` on the first and last frames (50 dB or more = the same frame). Anything held
  across a splice must be static on both sides.

**Encoding and files**
- **`--gpu` ignores CRF** (`--quality high --gpu` gave 14 Mb/s at 4K): always `--video-bitrate 45M`.
- **The render drops two colour tags:** always the BT.709 remux, or faces look redder than the camera original.
- **Skipping `assemble.py`:** the render keeps the camera level (~-25 LUFS). Level the voice to -14 first (a one-segment
  `assembly.json` does it), then add music; measure the file with `ebur128`.
- **The render finishes; the file can still be wrong** (black footage, a missing tag, audio a frame short):
  `verify-render.py` catches these, the pre-render sheet cannot. Its 40 Mb/s floor fails on mostly still screens
  (hardware encoders undershoot); if every other line passes, that is not a quality problem.

**Composition**
- **Every timed element needs `class="clip"`** or it shows for the whole video. Keep `data-has-audio="true"` on the
  footage (`video_missing_muted` is real) or the render is silent.
- **A second `<video>` on `input-video.mp4` does not paint:** cut the span to its own file and give it a `z-index` above
  `.card-host` (10). **One root composition per `public/`:** a backup inside it doubles the audio.
- **Never put CSS translate(), scale() or rotate() in the style of an element GSAP also moves:** GSAP replaces the whole
  value and the lint fails. Start states go in a `tl.fromTo`; lasting centring goes in the separate CSS `translate` property.
- **A count-up is an `onUpdate` on a proxy tweened on the one timeline;** write the start value in at load.
- **Text that changes step by step (typing, a clock) comes from one proxy tween, never a `tl.set` per step,** which
  leaves letters behind on a backward seek: tween `{ n: 0 }` to the length with `ease: 'none'` and write `slice(0,
  floor(n))`. The check for the whole class: seek past a beat, seek back inside it, compare with a fresh seek.
- **Heavy overlays have a budget:** `composition_heavy_overlay_count_high` counts every `filter: blur`,
  `radial-gradient` and `clip-path`, hidden ones included; around 40 and the capture paints black for the first half
  (every full-frame wash counts). Compose long form per section; prefer `box-shadow` glows.
- **The linter is wrong twice:** `text_occluded` behind the subject is the point, and `text_not_painted` fires on
  `background-clip:text`, which renders fine. Two text blocks in one rebuilt logo box trip `content_overlap` (draw the
  small word with `::before`); an SVG with `width="1em"` renders 16 px (give explicit width and height).

**Fonts, transcription, snapshots**
- **The house font look:** the three 7 KB `assets/fonts/DMSans-{400,500,700}.woff2` subsets under the stack `"DM Sans",
  ui-sans-serif, system-ui, sans-serif`, so Chrome draws in the system face (San Francisco on a Mac) at these metrics.
  That is the approved look; the full variable DM Sans reads rounder and wider. Body `font-family` lists concrete names,
  never a CSS variable, and a scene element never sets `"DM Sans"` alone (a whole scene once rendered in Times).
- **Always pass `--engine parakeet`:** with `auto`, a missing Parakeet falls back to whisper without a word.
- **Snapshot filenames:** `snapshot --at 8.0` writes `frame-00-at-8s.png` (no ".0") and wipes the folder each run; copy
  by exact name (`snap-beats.py` does).

## Sourcing assets

- **Tool logos:** the brand's press kit, or `npx hyperframes capture <url>` and the `<svg>` out of `extracted/page.html`
  (the real vector; watch for `fill="none"` paths and near-black wordmarks, make white variants for dark plates). The
  media-use skill's `scripts/resolve.mjs --type logo --intent "..." --project .` is another route (also `image`, `icon`,
  `bgm`, `sfx`).
- **Your own screen recordings** are the strongest cutaway: they are proof. **Public-domain archive** for a metaphor:
  NASA (`images-api.nasa.gov/search?q=...&media_type=video`, then the asset manifest's mp4).
- **Site captures:** request the explicit `/en` URL (a bare domain can geo-route to another language); a Cloudflare "Just
  a moment..." page is transient, retry. Never work around bot detection.
- **Pages that block robots:** do not work around it. Open the page in a real browser (Claude's browser tools), pull the
  facts with JavaScript (headline, date, nav, the logo `<svg>`, `@font-face` URLs, hero media), fetch fonts and images
  from their CDNs where allowed, and rebuild the top of the page at its real 1360 px layout, scaled to 50% into a 680 px
  browser card (resize the pane to 1360x765 first, scroll with `window.scrollTo`).
- **Stitched screenshots cannot fake a scroll** (pinned sections duplicate): one frame with a drift, a full-page capture
  in a scrolling window (4c, 4d), or your own screen recording.
- **X posts:** X's official embed (`platform.twitter.com/embed/Tweet.html?id=<ID>&theme=light&dnt=true&lang=en`) in
  headless Chrome at device scale 6, screenshotting the post's bordered parent (3300 px wide). Prove the text with the
  syndication JSON (`cdn.syndication.twimg.com/tweet-result?id=<ID>&token=<T>`, T =
  `((ID/1e15)*Math.PI).toString(36).replace(/(0+|\.)/g,'')`); post videos via `yt-dlp` as 1.1 s cutaways with a handle
  pill. Logged-out x.com answers headless Chrome with 403: never fake a user agent to get past it.
- **Person photos:** ask for the file. **Footage with captions burned in:** crop the plate about 10%, top-anchored.

## Stock B-roll route

The house routine runs this automatically (pick, download, clean, conform) and lists every clip in the storyboard. If
you would rather approve a shortlist first, say so and note it here.

- **Where:** every person or job you name, a 2.5 to 3.5 s full-frame `clip` right after you describe them, before the
  tool or answer is revealed (1.5 s is fine for an opener).
- **Search** in a forked subagent on a smaller model: two candidates per slot with page, licence, duration, resolution,
  fps, size, risks and the seconds to use, in `$W/broll-shortlist.md`, downloading nothing. Take the first unless a risk
  below rules it out.
- **Licence:** Pexels first (free on YouTube, no credit required, 4K), then Coverr and Mixkit's free licence. Never
  Mixkit's Restricted licence, never a clip labelled AI-generated, never a paid tier.
- **Look:** real people, a dark or moody room lit by screens, horizontal, 4K, no watermark, nobody looking into the lens,
  no readable brand logo or third-party UI (a recognisable but unreadable editor is fine).
- **Download** through the Pexels API (a free key in the `Authorization` header; take the 3840-wide entry in
  `video_files`) or the page's download button, into `$W/broll/raw/`.
- **Clean and conform** in one script per video (`$W/broll/conform-stock.sh`, the record of every window):
  `python3 "$SK/scripts/broll-conform.py" --4k --in "$W/broll/raw/<file>" --out "$W/public/broll/<job>.mp4" --start
  <s> --dur <slot + 1>`. Blur anything readable with `--vf "split[a][b];[b]crop=W:H:X:Y,boxblur=8[bb];[a][bb]overlay=X:Y"` in SOURCE
  pixels (find X and Y with ffmpeg's `drawgrid`); a crop rarely clears a label without wrecking the framing.
- **Pick the window by measured sharpness** (one clip breathed out of focus mid-window): the mean neighbour-pixel
  difference per 0.5 s on a 640x360 grey frame; take the steadiest high stretch. Snapshot every slot before rendering.

## AI B-roll route

Generated shots of you, from an image service and an image-to-video service of your choice. Narrow on purpose: these
shots work because the person is the presenter and the shot is the scene the sentence describes.

- **It stars you, or nobody:** never another real person; extras are generic and in the background. It shows the
  specific scene you describe, 2 to 5 s, on your words; if a viewer could not say what it shows in three words, cut it.
- **Never proof:** no fake dashboards, revenue, students, crowds, screenshots or results; proof is your real screen.
- About one shot a minute at most, never two in a row, each a `clip` with an anchor. **Label it on upload** (YouTube's
  "Altered or synthetic content": Yes). Every generation costs credits: quote the cost and get a yes for every run.

**The chain:**
1. Shot list first, `$W/BROLL.md`: anchor sentence, scene in one line, outfit (the one in your footage), camera move,
   length. Approved at Checkpoint B; nothing generates before.
2. References: a face pack (6 to 12 photos on a plain wall in video light: front, three-quarters, neutral and smiling,
   one half-body at your desk), photos of your empty set, and two or three frames from your footage (`ffmpeg -ss <t> -i
   "$W/public/input-video.mp4" -frames:v 1 ref-<n>.png`). The same set for every shot, or the face drifts. You upload
   your photos to the service yourself; Claude never posts them from the shell.
3. The still, 16:9, 2K: "The person from the reference photos, same face and hair, wearing [outfit], [one action] in [a
   specific place], [time of day] window light, 35mm lens at eye level, shallow depth of field, natural skin texture, no
   text, no logos, 16:9." Keep screens turned away or out of focus: generated screens show fake text.
4. Check the still (face, hands, anything written) before paying for motion: a bad still is a rerun, not a video.
5. Motion: image-to-video, 5 to 8 s, audio off, prompting the camera and one small action only ("slow push-in, he types,
   then looks up at the screen, natural motion, no cuts, no new people").
6. `python3 "$SK/scripts/broll-conform.py" --in "$W/broll/raw/<shot>.mp4" --out "$W/public/broll/<shot>.mp4" --start
   0.5 --dur 4 --grade` (`--start` skips the model's settle-in, `--grade` nudges it toward your footage), then read its
   sheet. Budget version: the still alone, `--in <shot>.png --dur 4`, a slow push-in (`--push 1.08`).
7. Into the storyboard as a `clip` beat on your words, with a `label` or a checklist when the shot carries a point.

## Tella route (screen tutorials)

You record tutorials in the Tella app (camera and screen as two tracks). The cut happens locally, the layouts and zooms
go in through the Tella connector (MCP), and the 4K export joins the rest at assembly.

```
get_timeline(videoId)                    # clips and durations; include layouts / zooms / cuts as needed
list_sources(videoId, clipId)            # the camera+mic signed URL: write it to "$W/tella/cam-url.txt" with a heredoc, never retype it
python3 "$SK/scripts/tella-pull-source.py" --url-file "$W/tella/cam-url.txt" --out "$W/tella/<clip>-camera.mp4" --wav "$W/tella/<clip>-audio-raw.wav"
                                         # the Cut stage on that file; PAPER-CUT.md = Checkpoint A
python3 "$SK/scripts/tella-cuts.py" --cut-list "$W/tella/cut-list.json" --source-duration <ffprobe of the mp4> --clip-max <clip.maxDurationSeconds>
update_clip(cuts=[...])                  # then get_transcript: the first kept word must sit near 0.4 s, or the offset is wrong
get_transcript + get_mouse_events        # words and clicks on the playback timeline → layouts and zooms by the rules below
apply_video_edits(...)                   # one batch: remove stale ranged layouts, add camera-only sections (spring), add manual zooms
get_clip_frame at every boundary, get_storyboard for the video     # Checkpoint B, saved in "$W/tella/snaps/"
export_video(resolution "4k", fps "30") → get_export_status → curl -L -o "$W/tella/<segment>-4k.mp4" "<url>"
```

- ffmpeg cannot open the signed playlist, hence `tella-pull-source.py`; one mistyped character in a signed URL is a 403.
  Tella's clip timeline starts ~2.4 s into the downloadable source; `tella-cuts.py` applies that lead-in.
- Work on the real video only after Checkpoint A; anything exploratory goes on a `duplicate_video` copy. Layouts and
  zooms survive a re-cut (Tella anchors them to the footage).
- `remove_silences` and `remove_fillers` cannot tell a retake from a keeper, so the cut stays local (`remove_fillers`
  after our cut is fine). `generate_auto_layouts` replaces every layout and uses hard cuts: a first draft on an empty
  clip only.
- **Never upload a HyperFrames render into Tella** (it re-encodes at ~15 Mb/s and comes back softer, SSIM 0.88). The
  export is 3840x2160, 30 fps, BT.709, ~9 Mb/s; a 720p camera track becomes an upscale, so record the camera higher.

**Settings** (`update_video`, the house defaults): canvas 1920x1080 with your background image; studio sound, motion
blur and `shrinkCameraDuringZooms` off; a large cursor (size about 3), no smoothing, no click ripple; hard cuts between
clips and `spring` for layout changes; no subtitles, nothing burned in, no music in Tella. Mic volume 1; system audio 0
(or ~0.05) where a video plays on screen while you talk.

**The three views** (every screen clip visits all three):
1. **You left, screen right:** `side-by-side`, position `left`, style `regular`, the base of every screen clip. Never
   `overlap` (your face never sits on the screen you are showing; new recordings often arrive that way) and never
   `side-by-side even` (it crops the screen to half width).
2. **A square or portrait card of you** on the wash (`camera-only`, style `middle`, shapes alternating) for short face
   moments. Long commentary stays `camera-only fullscreen` so the overlays have a full frame.
3. **The screen full frame** (`screen-only`, `fullscreen`, screenFit `cover`) while you draw, type or click and the
   screen is the point.

**The full-face rule.** Enter on the first word of a commentary sentence when nothing happens on screen for the next
~6 s (no click, scroll or typing in `get_mouse_events`), and while you talk to camera about a list until you reach the
item you then show. Return at the first sentence that points at the screen ("this", "right here", a price, a product
name) or the next click. Cap it at 12 to 13 s; one or two per minute; `spring` transitions; clips open and end on the screen.

**Zooms.** Manual, on the thing you name, never on clicks: ~5 s, scale 1.33 to 1.6 (2.0 for small text), starting with
that sentence; one or two per 30 s of screen time, none during full face or while a video plays in the recording. **No
zoom when a page first appears** (show the whole page), no `generate_auto_zooms`, no tracking zooms; a zoom that lands on
neighbouring cards becomes a fixed-origin zoom on the subject. A Tella zoom shrinks your camera into a bubble over the
page, so for a moment where the screen is the point, zoom in HyperFrames on the whole frame with an origin that pushes
your card out: a card whose right edge sits at fraction c of the width leaves once `origin_x * (1 - 1/scale) > c`.

**Cut rules for tutorials:**
- **The screen cut is tighter than the talking-head cut:** after our cut, `remove_silences` mode `fast` on the screen
  clips. It can clip a quiet word, so read the export's transcript, not Tella's.
- Cut forms with personal data (from before the click to after the close, with the sentence that described it),
  restarts and repeats even inside a demo (keep the last), a sentence that re-announces a step the next clip announces,
  and a mumbled line from another take even when its words are fine (check the join by level and a fresh transcription).
- **A browser resize is dead air:** cut it whole; when the page is then narrow, slide the window to the centre of the
  background instead of showing the desktop.
- **A live run shows the result, not the wait:** cut status lines and log read-outs, keep one of a repeated intro line,
  put an "N minutes later" pill on the cut and open on the result already playing (80 s became 37 s).
- Text and images you pasted into an AI chat get shown (13b with the attachments); a product you introduce gets its
  homepage (~3 s, after the name lands); "download the app" gets the real download page, held until you move on.

**The overlay pass on a Tella export.** The 4K export becomes `public/input-video.mp4` (re-encoded, a keyframe every
30 frames) and gets transcribed. Jump cuts are the union of the cuts you sent AND a frame-difference scan of the export
(96x54 grey, a spike over 3.5x the local median): duplicated clips carry cuts of their own, and the scan alone misses
subtle cuts on a still talking head. Overlays live on the full-face windows only (a tag per section, lines, chips, cards,
a logo, a site cutaway); anchors come from `phrase-times.py`; the camera gets `set 1.0` at every jump cut and window
edge, one creep per window, punches 1.6 s clear of any cut. Then the Pipeline.

**Many clips in one pass.** Duplicate the video, export the copy UNCUT once (1080p) and slice its audio per clip by the
timeline's start and duration: raw clip time, so no lead-in offset and no signed URLs. Per clip: windowed Parakeet +
paper-cut, hand cuts, `tighten-cut.py` (`--maxgap 1.2` on demo clips, 0.35 elsewhere), `update_clip` cuts; clamp face
windows to the clip's playback length or `apply_video_edits` rejects the batch.

**When the connector only takes strings** ("must be object (got string)"): ID-only calls still work (`remove_zoom`,
`remove_layout`, `export_video` with "4k" and "30", every `list_*`), and layouts go through `save_layout(videoId, clipId,
layoutId, name)` on a clip that has the one you want, then `apply_saved_layout(videoId, clipId, savedLayoutId)`. Cuts
then happen after the export: remove spans frame-exact (12 ms audio fades) and map every timing through the cut.

**Lip sync.** In one Tella setup the picture ran 3 frames (~100 ms) behind the mic; camera-card footage measured 0.
Measure once per setup on an uncut camera-only export: a box on the lips (80x48 grey, frame differences) cross-correlated
with the rise of the audio envelope over 9 to 15 minutes; the peak is the lag (short files with jump cuts are too noisy).
Fix it where you build the flat cut locally from an uncut export, never by moving the audio: shift the picture once,
then cut as usual, so every picture segment comes N frames after its audio and the audio cuts stay put (moving the
audio clips word tails and pulls slivers of dropped takes into the joins):

```bash
ffmpeg -ss 0.100 -i in.mp4 -i in.mp4 -map 0:v -map 1:a -c:v libx264 -crf 16 -c:a copy -shortest in-synced.mp4
```

**A Tella video you already edited:** work on a `duplicate_video` copy. Screen-only clips get `add_highlight` masks
(intensity 0.55) on the menu you explain, while it is open (no cards over dense UI); camera clips get `camera-only
fullscreen` sections by the full-face rule, where the graphics live. A step tag on white UI is dark glass.

**Two-file tutorials:** `sync-tracks.py --a <face> --b <screen> --write-aligned "$W/aligned"`, the Cut stage on the face
file, the screen as `clip` cutaways. `screen-activity.py` shows where a recording goes still (full-face candidates);
`tella-timeline.py` lines sentences up with clicks and activity.

## Assembly (one master)

```bash
python3 "$SK/scripts/assemble.py" --manifest "$W/assembly.json" \
  --out "$HOME/Movies/YouTube Renders/<project>/<project>-full-4k.mp4" --gpu
```

```json
{"project": "my-video", "width": 3840, "height": 2160, "fps": 30, "loudness": -14,
 "music": {"file": "bed.mp3", "db": -26, "fade": 2.0},
 "segments": [{"name": "Hook", "file": "~/Movies/YouTube Renders/my-video/hook-4k.mp4"},
              {"name": "1 · Thumbnails", "file": "intro-01-4k.mp4"},
              {"name": "1 · Tutorial", "file": "tella/01-tutorial-4k.mp4", "trim": [0.0, 71.4], "chapter": false}]}
```

Relative paths resolve against the manifest; `trim` is [start, end] seconds; `"chapter": false` hides a segment from the
chapter list; `music` is optional (silence is the default); `"loudness": null` leaves levels alone. Each segment is
conformed once (CRF 16, or `--gpu` at 45 Mb/s) and loudness-normalised in two passes (camera renders arrive around -25 to
-33 LUFS, Tella exports around -23: without this the joins jump 10 dB), then joined with stream copy and tagged BT.709.
Next to the master: `ASSEMBLY.md` (start times, loudness in, md5) and `chapters.txt` for the description. Changes mean
editing the manifest and running again: **the master is never hand-edited.**

## Verify and deliver

- **`verify-render.py` on every render:** black runs (one-frame flashes included), size, BT.709 tags, at least 40 Mb/s at
  4K, duration = `data-duration` ± 1 frame, A/V under 0.12 s; it writes `VERIFY.md` and `render-sheet.png`. Exit 1 = do
  not deliver. **Clipped words:** transcribe the render's audio and add `--words <that> --kept "$W/transcript.json"`.
- **Motion on contiguous frames:** `ffmpeg -i out.mp4 -vf "select='between(n,A,B)',scale=480:270,tile=6x7" -frames:v 1
  strip.png` across every transition window; look for a jump-then-crawl, a dead stop between moves, a one-frame pop.
- **Sound** as in "Sound"; **loudness** with `ebur128` (about -14 LUFS, true peak under -1); **lip sync** on a long cut:
  a flat frame matches the source near `src_start + x` within one frame for a few late segments.
- **Deliver** to `~/Movies/YouTube Renders/<project>/<project>-4k.mp4` (md5 it against the render) with `STORYBOARD.md`
  next to it (`storyboard-md.py`: time / beat / what is on screen, what changed, your concerns, every stock clip with
  page, licence and seconds) and, for a cut from raw, `PAPER-CUT.md`. Open it from Finder (or Explorer); never pass the
  MP4 through a chat download, since a hosted round trip can change the file.
- **Report** the folder, what was added and where, and **your own concerns** (a card held too long, a word lost on the
  shirt, a cut hidden under a cutaway). Version numbers keep going (v2, v3...). Notes come back in plain words; nothing
  is ever locked.
- **Retiming an approved design onto a new cut of the same content is the cheapest edit:** copy the reference `public/`,
  re-transcribe, move every `data-start` and timeline time to the new words, snapshot, render.

## The teardown (learning from a channel you admire)

Every two videos, measure two recent videos from a channel you want to learn from against your last two edits. Pull them
for private analysis (`yt-dlp -f "bv*[height<=1080]+ba" -o "videos/_teardown/<slug>.%(ext)s" <url>`, captions with
`--write-auto-subs --skip-download`); if a download is refused, do not force it.

```bash
python3 "$SK/scripts/teardown.py" --video videos/_teardown/<ref>.mp4 --out videos/_teardown/<ref>/ [--transcript words.json]
python3 "$SK/scripts/teardown.py" --storyboard videos/<ours>/storyboard.json --out videos/_teardown/<ours>-sb/
python3 "$SK/scripts/teardown.py" --compare videos/_teardown/*/report.json --out videos/_teardown/COMPARE.md
```

The script measures what pixels can tell (hard cuts against the local median frame change, since a same-framing jump
cut is 4 to 17 times the median; bursts; the quietest 15 s stretches; luma; loudness; words a minute). The contact sheets
are for the rest, counted by eye: overlay moments, entrances, on-screen words, camera moves, face presence, cutaway types,
captions. Never claim to have heard audio from waveform numbers. Turn each gap into one rule here (and in
`STYLE-GUIDE.md` when it is the look). Dense edits usually keep their density inside the card (a new element about every
second), not in the number of cards; keep the read-in-under-2-seconds rule anyway.

## Shorts (9:16)

Not the default routine. If you make one: a separate 1080x1920 composition (never a centre crop of the 16:9), hero type
88 to 110 px, cards full width minus 48 px, the caption chip ~280 px from the bottom, word-exact captions on the kept
words, a specific reason to stay in the first three seconds that the video pays off, one main open loop.

## Keeping the skill yours

- **After every delivery:** your note in plain words → edit the storyboard (one number) or the format (one rule) →
  rebuild → snapshot → render. The skill exists so the next first prompt is just "edit these intros".
- **"Save this to the skill":** write the note as one plain rule in the section it belongs to, with its number when it
  has one. When it changes the look, update `STYLE-GUIDE.md` and the composer's tokens too. When a new rule contradicts
  an old one, replace the old one; never leave both.
- **A liked result becomes a format:** a row in the library table plus a spec with its numbers.
- **A new format starts with a state sheet:** name every state before any code (what is on screen, where, size, colour)
  and every change between two states (what moves, the property, the ease, the time). Build to the sheet, snapshot each
  state, fix round by round, run the seek-back check (Traps) and add a test under `scripts/tests/`. A format without a
  state sheet drifts, and the review has nothing to point at.
- **Model and tokens:** routine passes run fine on a mid-size model; a new format, or a break this file does not cover,
  deserves the strongest. Most tokens go to snapshots and tool output: one snapshot per moment, scripts over retyping.

