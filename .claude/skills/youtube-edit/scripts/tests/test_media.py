"""The ffmpeg tests: apply-cut stays on the frame grid, verify-render catches a 2-frame black flash and missing
BT.709 tags, teardown finds same-framing jump cuts. All media is synthesised with lavfi (testsrc2, sine, color)."""
import os, random, unittest
from .helpers import ffmpeg, load, needs_ffmpeg, probe, read, run, scratch, write

TAGS = ["-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv", "-movflags", "+write_colr"]


@needs_ffmpeg
class ApplyCut(unittest.TestCase):
    def test_duration_within_one_frame_over_many_segments(self):
        d = scratch(self)
        src = os.path.join(d, "raw.mp4")
        ffmpeg("-f", "lavfi", "-i", "testsrc2=size=160x90:rate=30:duration=45", "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=45",
               "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", src)
        rnd, kept, t = random.Random(5), [], 0.37
        while len(kept) < 80:                               # 80 short segments at times that are never on the frame grid
            dur = rnd.uniform(0.18, 0.45)
            kept.append({"start": round(t, 3), "end": round(t + dur, 3)}); t += dur + rnd.uniform(0.05, 0.2)
        cl = write(os.path.join(d, "cut-list.json"), {"kept": kept})
        out = os.path.join(d, "public", "input-video.mp4"); os.makedirs(os.path.dirname(out))
        r = run("apply-cut.py", "--input", src, "--cut-list", cl, "--out", out, "--preset", "ultrafast")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        cm = load(os.path.join(d, "cut-map.json"))
        streams, _ = probe(out)
        self.assertLessEqual(abs(streams["video"] - cm["flat_duration"]), 1 / 30 + 1e-6)
        self.assertLessEqual(abs(streams["video"] - streams["audio"]), 0.12)
        self.assertAlmostEqual(cm["flat_duration"], sum(s["frames"] for s in cm["segments"]) / 30, places=3)
        for s in cm["segments"]:                             # every boundary sits on the source grid
            self.assertAlmostEqual(s["src_start"] * 30, round(s["src_start"] * 30), places=2)


@needs_ffmpeg
class VerifyRender(unittest.TestCase):
    def render(self, d, name, vf=None, tags=True):
        path = os.path.join(d, name)
        ffmpeg("-f", "lavfi", "-i", "testsrc2=size=320x180:rate=30:duration=6", "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=6",
               # ffmpeg 9: frame colour properties override the output flags on an encode, so tag the frames too
               *(["-vf", ",".join(f for f in (("setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709" if tags else None), vf) if f)]
                 if (vf or tags) else []), "-c:v", "libx264", "-preset", "ultrafast", "-b:v", "1M", "-pix_fmt", "yuv420p",
               *(TAGS if tags else []), "-c:a", "aac", "-shortest", path)
        return path

    def verify(self, d, path, *extra):
        index = write(os.path.join(d, "public", "index.html"), '<div id="stage" data-composition-id="t" data-start="0" data-duration="6.000">\n'
                      '<div class="card-host clip" id="host-a" data-start="1.200" data-duration="2" data-anchor="x"></div>\n</div>\n')
        out = os.path.join(d, "check", os.path.basename(path) + ".md")
        return run("verify-render.py", "--render", path, "--index", index, "--res", "320x180", "--out", out, *extra), out

    def test_clean_render_passes(self):
        d = scratch(self)
        r, out = self.verify(d, self.render(d, "clean.mp4"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(os.path.exists(os.path.join(os.path.dirname(out), "render-sheet.png")))
        self.assertIn("**PASS**", read(out))

    def test_two_frame_black_flash_fails(self):
        d = scratch(self)
        r, out = self.verify(d, self.render(d, "flash.mp4", vf="drawbox=x=0:y=0:w=iw:h=ih:color=black:t=fill:enable='between(n,60,61)'"))
        self.assertEqual(r.returncode, 1, r.stdout)
        md = read(out)
        self.assertIn("| Black frames | FAIL |", md)
        self.assertIn("2.000 - 2.067 s (0.067 s, 2 frames): flash", md)

    def test_missing_bt709_tags_fail(self):
        d = scratch(self)
        r, out = self.verify(d, self.render(d, "untagged.mp4", tags=False))
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("| Colour tags | FAIL |", read(out))

    def test_clipped_word_fails(self):
        d = scratch(self)
        kept = write(os.path.join(d, "flat.json"), [{"text": w, "start": i * 0.4, "end": i * 0.4 + 0.3} for i, w in enumerate("so the product is great".split())])
        heard = write(os.path.join(d, "heard.json"), {"words": [{"text": w, "start": i * 0.4, "end": i * 0.4 + 0.3} for i, w in enumerate("So product is great.".split())]})
        r, out = self.verify(d, self.render(d, "clean.mp4"), "--words", heard, "--kept", kept)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("**the**", read(out))


@needs_ffmpeg
class Teardown(unittest.TestCase):
    CUT = [(60, 77), (180, 194), (240, 255), (300, 321)]   # frames removed from a 14 s take

    def test_finds_same_framing_jump_cuts(self):
        d = scratch(self)
        path = os.path.join(d, "jump.mp4")
        sel = "*".join("not(between(n\\,%d\\,%d))" % c for c in self.CUT)
        # a grey room, sensor noise and a textured "head" that sways; drawn large then scaled so it moves smoothly
        ffmpeg("-f", "lavfi", "-i", "color=c=0x707070:s=1280x720:r=30:d=14", "-f", "lavfi", "-i", "testsrc2=s=360x440:r=30:d=14",
               "-f", "lavfi", "-i", "sine=f=220:sample_rate=48000:d=14", "-filter_complex",
               "[1]hue=s=0.3[h];[0][h]overlay=x='460+120*sin(2*PI*t/4)':y='140+20*sin(2*PI*t/3)',scale=320:180:flags=area,"
               "noise=alls=8:allf=t,select='%s',setpts=N/30/TB[v];[2]anull[a]" % sel,
               "-map", "[v]", "-map", "[a]", "-r", "30", "-shortest", "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac", path)
        kept = [n for n in range(420) if not any(a <= n <= b for a, b in self.CUT)]
        expected = [i / 30 for i in range(1, len(kept)) if kept[i] != kept[i - 1] + 1]
        words = write(os.path.join(d, "words.json"), [{"text": "word.", "start": i * 0.5, "end": i * 0.5 + 0.3} for i in range(20)])
        out = os.path.join(d, "td")
        r = run("teardown.py", "--video", path, "--out", out, "--every", "1", "--transcript", words)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        rep = load(os.path.join(out, "report.json"))
        self.assertEqual(len(rep["cuts"]), len(expected), rep["cuts"])
        for got, want in zip(rep["cuts"], expected):
            self.assertLessEqual(abs(got - want), 1 / 30 + 1e-3)
        self.assertTrue(all(c["diff"] < 40 for c in rep["cut_detail"]))   # a fixed 40/255 threshold would miss every one
        self.assertAlmostEqual(rep["words_per_min"], 20 / rep["duration"] * 60, places=0)
        md = read(os.path.join(out, "TEARDOWN.md"))
        for s in ("| Time | Spoken idea | Visual change | Camera | Sound cue | Viewer question | Payoff |", "## Count by eye from the sheets",
                  "Do not claim you heard audio based on waveform numbers; listen or say it was not listened to.", "sheet_01.png"):
            self.assertIn(s, md)


class TeardownStoryboard(unittest.TestCase):
    def test_exact_counts(self):
        d = scratch(self)
        sb = write(os.path.join(d, "storyboard.json"), {
            "id": "T1", "duration": 60.0, "tag": {"n": 1, "of": 3, "label": "Two words", "in": 0.2, "out": 5.0},
            "beats": [{"type": "line", "id": "l1", "text": "You clicked on a thumbnail", "in": 8, "out": 11},
                      {"type": "list", "id": "ls", "items": [["Candles", 13], ["Soap bars", 14]], "in": 12.5, "out": 16},
                      {"type": "bullets", "id": "bu", "items": [["One", 20]], "in": 19.5, "out": 24},
                      {"type": "site", "id": "sk", "src": "img/s.png", "domain": "example.com", "in": 30, "out": 34, "transition": "zoomthrough"},
                      {"type": "grid", "id": "gr", "images": [], "in": 40, "out": 44},
                      {"type": "stats", "id": "st", "title": "The numbers", "items": [{"value": 250, "suffix": "+", "label": "Videos", "at": 50}], "in": 49.5, "out": 53},
                      {"type": "popout", "id": "po", "title": "What you need", "items": [["Two cameras", 55.5]], "in": 55, "out": 58.5}],
            "camera": [["creep", 0.3, 5.0, 1.1], ["set", 9.7, 1.0], ["punch", 18.3, 1.18], ["release", 21.0, 0.5]]})
        out = os.path.join(d, "td")
        r = run("teardown.py", "--storyboard", sb, "--out", out)
        self.assertEqual(r.returncode, 0, r.stderr)
        rep = load(os.path.join(out, "report.json"))
        # 8 overlays (tag + 7 beats); 9 moves = creep, punch, release + bullets 2 + zoomthrough 2 + pop-out 2 (the set is not a move);
        # 3 cutaways = site, grid, stats row; 21 words = tag 2 + line 5 + list 3 + bullets 1 + domain 1 + stats 4 + pop-out 5
        self.assertEqual((rep["overlays"], rep["camera_moves"], rep["cutaways"], rep["onscreen_words"]), (8, 9, 3, 21))
        self.assertEqual((rep["overlays_per_90s"], rep["camera_moves_per_90s"]), (12.0, 13.5))
        r = run("teardown.py", "--compare", os.path.join(out, "report.json"), "--out", os.path.join(d, "COMPARE.md"))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("| Overlays / 90 s | 12.0 |", read(os.path.join(d, "COMPARE.md")))


if __name__ == "__main__":
    unittest.main()
