"""beat-check.py negative controls: one anchor word at 2.5 s, move the card around it."""
import os, time, unittest
from .helpers import run, scratch, write

WORDS = {"words": [{"text": "Hello", "start": 2.5, "end": 2.8}, {"text": "there.", "start": 2.85, "end": 3.1},
                   {"text": "Candles,", "start": 6.45, "end": 6.9}, {"text": "soap", "start": 7.12, "end": 7.5}]}
PAGE = ('<div id="stage" data-composition-id="t" data-start="0" data-duration="10.000">\n'
        '<video id="bg-video" src="input-video.mp4" data-start="0" data-duration="10"></video>\n%s\n</div>\n')


class BeatCheck(unittest.TestCase):
    def project(self, body, stale=False, video=True):
        d = scratch(self)
        index = write(os.path.join(d, "public", "index.html"), PAGE % body)
        tr = write(os.path.join(d, "transcript.json"), WORDS)
        if video:
            v = write(os.path.join(d, "public", "input-video.mp4"), "")
            now = time.time()
            os.utime(v, (now - 100, now - 100) if not stale else (now, now))
            os.utime(tr, (now - 50, now - 50))
        return index, tr

    def check(self, body, *extra, **kw):
        index, tr = self.project(body, **kw)
        return run("beat-check.py", "--index", index, "--transcript", tr, *extra)

    def host(self, start, anchor='data-anchor="Hello"'):
        return '<div class="card-host clip" id="host-x" data-start="%s" data-duration="2" %s></div>' % (start, anchor)

    def test_window(self):
        for start, code, status in [(2.25, 0, "OK"), (1.5, 1, "EARLY"), (2.7, 1, "LATE")]:
            r = self.check(self.host(start))
            self.assertEqual(r.returncode, code, r.stdout + r.stderr)
            self.assertRegex(r.stdout, r"host-x .* %s " % status)

    def test_missing_anchor_fails(self):
        r = self.check(self.host(2.25, anchor=""))
        self.assertEqual(r.returncode, 1)
        self.assertIn("NO-ANCHOR", r.stdout)

    def test_cutaway_video_without_anchor_fails(self):
        r = self.check('<video id="cut-1" class="clip" src="b.mp4" data-start="4" data-duration="2"></video>')
        self.assertEqual(r.returncode, 1)
        self.assertIn("NO-ANCHOR", r.stdout)

    def test_unanchored_is_skipped(self):
        r = self.check(self.host(0.2, anchor="data-unanchored"))
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("0 checked", r.stdout)

    def test_data_at_items(self):
        ok = '<div class="item" id="ls-i0" data-at="6.240" data-anchor="Candles"></div>'
        late = '<div class="item" id="ls-i1" data-at="7.500" data-anchor="Soap"></div>'
        r = self.check(ok)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertRegex(r.stdout, r"ls-i0 +6\.24@ +6\.45 +\+0\.21 +OK")
        r = self.check(ok + late, "--suggest")
        self.assertEqual(r.returncode, 1)
        self.assertRegex(r.stdout, r"ls-i1 .* LATE")
        self.assertIn('ls-i1                  data-at="6.87"', r.stdout)

    def test_suggest_for_missing_anchor(self):
        r = self.check(self.host(2.3, anchor=""), "--suggest")
        self.assertIn('data-anchor="hello there candles"', r.stdout)

    def test_stale_transcript_fails(self):
        r = self.check(self.host(2.25), stale=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn("transcript is older than the video: re-transcribe the flat cut", r.stdout)
        r = self.check(self.host(2.25), "--allow-stale", stale=True)
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_no_video_skips_staleness(self):
        r = self.check(self.host(2.25), video=False)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("staleness not checked", r.stdout)


if __name__ == "__main__":
    unittest.main()
