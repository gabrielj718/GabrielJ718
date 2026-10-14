"""patch-cut.py --drop-flat: flat-cut ranges mapped back through cut-map.json, with its guards."""
import os, unittest
from .helpers import load, read, run, scratch, write

KEPT = [{"start": 1.0, "end": 3.0}, {"start": 5.0, "end": 7.0}, {"start": 9.0, "end": 10.0}]
MAP = {"cuts": [2.0, 4.0], "flat_duration": 5.0, "segments": [
    {"flat_start": 0.0, "flat_end": 2.0, "src_start": 1.0, "src_end": 3.0},
    {"flat_start": 2.0, "flat_end": 4.0, "src_start": 5.0, "src_end": 7.0},
    {"flat_start": 4.0, "flat_end": 5.0, "src_start": 9.0, "src_end": 10.0}]}


class DropFlat(unittest.TestCase):
    def setUp(self):
        d = scratch(self)
        self.cl = write(os.path.join(d, "cut-list.json"), {"source_duration": 12.0, "kept": KEPT})
        write(os.path.join(d, "cut-map.json"), MAP)

    def kept(self):
        return [(s["start"], s["end"]) for s in load(self.cl)["kept"]]

    def test_range_across_a_join(self):
        r = run("patch-cut.py", "--cut-list", self.cl, "--drop-flat", "1.5-2.5")   # no --transcript / --speech needed
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.kept(), [(1.0, 2.5), (5.5, 7.0), (9.0, 10.0)])

    def test_range_inside_a_segment_splits_it(self):
        r = run("patch-cut.py", "--cut-list", self.cl, "--drop-flat", "4.2-4.4")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.kept(), [(1.0, 3.0), (5.0, 7.0), (9.0, 9.2), (9.4, 10.0)])

    def test_guards_write_nothing(self):
        before = read(self.cl)
        for spec, msg in [("3-2", "finite numeric start < end"), ("nan-2", "finite numeric start < end"), ("abc", "finite numeric start < end"),
                          ("-1-2", "outside the flat duration"), ("4-6", "outside the flat duration")]:
            r = run("patch-cut.py", "--cut-list", self.cl, "--drop-flat=" + spec)
            self.assertNotEqual(r.returncode, 0, spec)
            self.assertIn(msg, r.stderr, spec)
        self.assertEqual(read(self.cl), before)

    def test_stale_cut_map_is_refused(self):
        write(self.cl, {"kept": [{"start": 1.0, "end": 3.0}, {"start": 5.5, "end": 7.0}, {"start": 9.0, "end": 10.0}]})
        r = run("patch-cut.py", "--cut-list", self.cl, "--drop-flat", "0.5-0.7")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("re-run apply-cut.py", r.stderr)

    def test_add_still_needs_transcript(self):
        r = run("patch-cut.py", "--cut-list", self.cl, "--add", "1-2")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("--add needs --transcript and --speech", r.stderr)


if __name__ == "__main__":
    unittest.main()
