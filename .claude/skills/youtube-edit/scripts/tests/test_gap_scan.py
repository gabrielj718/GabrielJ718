"""gap-scan.py: a camera move is an event (a set at a jump cut is not)."""
import os, unittest
from .helpers import run, scratch, write

PAGE = """<div id="stage" data-composition-id="t" data-start="0" data-duration="60.000">
<div class="video-wrapper" id="video-wrap"><div id="video-zoom"><video id="bg-video" src="input-video.mp4" data-start="0" data-duration="60"></video></div></div>
<div class="card-host clip" id="host-a" data-start="0.500" data-duration="4.500" data-anchor="Hi"></div>
<script>
const tl = gsap.timeline({ paused: true });
tl.set('#video-zoom', { scale: 1.0 }, 0);
%s
</script>
</div>
"""
MOVES = """tl.to('#video-zoom', { scale: 1.180, duration: 0.32, ease: 'power2.out' }, 18.000);
tl.set('#video-zoom', { scale: 1.000 }, 25.000);
tl.fromTo('#video-wrap', { scale: 1.08 }, { scale: 1.0, duration: 0.32, ease: 'power2.out', immediateRender: false }, 32.000);
tl.to('#video-zoom', { scale: 1.10, duration: 5.000, ease: 'power1.inOut' }, 46.000);"""


class GapScan(unittest.TestCase):
    def scan(self, js):
        d = scratch(self)
        return run("gap-scan.py", "--index", write(os.path.join(d, "public", "index.html"), PAGE % js))

    def test_camera_moves_end_gaps(self):
        r = self.scan(MOVES)
        self.assertEqual(r.returncode, 0, r.stdout)          # gaps 13.0, 13.7, 13.7, 9.0 s: nothing over 15 s
        self.assertIn("1 overlay(s), 3 camera move(s)", r.stdout)
        self.assertIn("18.32 -   32.00   13.7s", r.stdout)     # the set at 25.0 did not split this gap
        self.assertIn("density: 1.5 overlays + 4.5 camera moves per 90 s", r.stdout)

    def test_without_moves_the_gap_is_flagged(self):
        r = self.scan("tl.set('#video-zoom', { scale: 1.000 }, 25.000);")
        self.assertEqual(r.returncode, 1)
        self.assertIn("0 camera move(s)", r.stdout)
        self.assertRegex(r.stdout, r"5\.00 -   60\.00   55\.0s  <-- over the 30s ceiling")


if __name__ == "__main__":
    unittest.main()
