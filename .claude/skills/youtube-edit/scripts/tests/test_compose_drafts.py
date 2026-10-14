"""compose.py, the world / deck / pills / chat / doc / clip formats: they build, and the guards hold."""
import os, re, unittest
from .helpers import run, scratch, write, read

DOC = {"type": "doc", "id": "dc", "domain": "example.com", "title": "A title", "in": 20.0, "out": 25.0, "anchor": "-",
       "paras": ["First paragraph with the passage we read out loud.", "Second paragraph & more."],
       "marks": [{"text": "the passage we read", "at": 20.8}, {"text": "more", "at": 23.0, "anchor": "-"}]}
WORLD = {"type": "world", "id": "wd", "in": 1.0, "out": 8.0, "anchor": "-",
         "nodes": [{"id": "a", "kind": "orb", "x": 960, "y": 540, "icon": "shield", "label": "Policy", "at": 1.2, "lit": 1.8,
                    "alerts": {"at": 2.2, "n": 3}},
                   {"id": "b", "kind": "card", "x": 300, "y": 540, "label": "Business", "at": 3.4, "anchor": "the business"},
                   {"id": "s", "kind": "stat", "x": 1600, "y": 540, "label": "Rate", "value": 51, "to": [93, 5.0, 0.93], "at": 3.0}],
         "links": [{"from": "b", "to": "a", "at": 3.8, "run": True}, {"from": "a", "to": "s", "at": 4.0, "dash": True}],
         "cam": [[1.0, 960, 540, 1.6], [3.0, 700, 540, 0.9, 1.2], [5.5, 1600, 540, 1.4]]}


def board(*beats):
    return {"id": "t", "duration": 30.0, "beats": list(beats)}


class ComposeDrafts(unittest.TestCase):
    def build(self, spec):
        d = scratch(self)
        sp = write(os.path.join(d, "storyboard.json"), spec)
        r = run("compose.py", "--spec", sp, "--out", os.path.join(d, "public"))
        page = read(os.path.join(d, "public", "index.html")) if r.returncode == 0 else ""
        return r, page

    def test_all_six_build(self):
        r, page = self.build(board(
            {"type": "pills", "id": "pl", "layout": "row", "in": 0.2, "out": 0.9, "anchor": "-",
             "items": [["Read access", 0.3], {"text": "Wrong price", "at": 0.5, "tone": "amber", "mark": "x", "icon": "alert"}]},
            WORLD,
            {"type": "chat", "id": "cf", "frame": "float", "pos": "tr", "in": 8.2, "out": 11.0, "anchor": "-",
             "messages": [["me", "Which agents can touch it?", 8.4, "which agents"]]},
            {"type": "deck", "id": "dk", "now": 2, "recap_at": 13.5, "in": 11.5, "out": 15.0, "anchor": "-",
             "cards": [{"title": "One", "icon": "user"}, {"title": "Two", "icon": "shield"}, {"title": "Three"}]},
            {"type": "chat", "id": "cw", "frame": "phone", "in": 15.2, "out": 19.0, "anchor": "-",
             "messages": [["them", "Can you build this?", 15.5], ["me", "Sure.", 16.4]]},
            DOC,
            {"type": "clip", "id": "br", "src": "broll/desk.mp4", "in": 25.5, "out": 28.0, "anchor": "a desk",
             "items": [["Fine-tune", 25.8, "-"]], "label": "Workforce"}))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for needle in ('id="wd-cam"', 'id="dk-cam"', 'id="pl-p1"', 'class="ch-float r"', 'class="ch-win phone"',
                       'id="dc-m0"', 'class="cutaway-video clip" id="br"', 'id="host-br-over"', "countFromTo('#wd-n2-v'"):
            self.assertIn(needle, page)
        self.assertIn("Second paragraph &amp; more.", page)           # page text is escaped
        self.assertIn('data-at="3.400" data-anchor="the business"', page)   # a world node carries its anchor
        self.assertIn('id="dc-a0" data-at="20.800" data-anchor="the passage we read"', page)   # a doc mark defaults to its first words

    def test_glass_waits_with_inherit_never_visible(self):
        # a glass that has not arrived must not blur the footage, and a child set to 'visible' would outlive its hidden host
        r, page = self.build(board(WORLD, {"type": "pills", "id": "pl", "in": 9.0, "out": 12.0, "anchor": "-", "items": [["A", 9.2], ["B", 9.6]]}))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertRegex(page, r'id="pl-p0" style="visibility:hidden"')
        self.assertRegex(page, r'id="wd-n1" style="[^"]*visibility:hidden"')
        self.assertIn("visibility: 'inherit'", page)
        self.assertNotIn("visibility: 'visible'", page)

    def test_world_camera_moves_never_overlap(self):
        w = dict(WORLD, cam=[[1.0, 960, 540, 1.0], [2.0, 700, 540, 1.5, 1.2], [2.8, 960, 540, 1.0]])
        r, _ = self.build(board(w))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("one gesture at a time", r.stdout + r.stderr)

    def test_world_stat_recount_waits_for_the_first(self):
        w = dict(WORLD, nodes=WORLD["nodes"][:2] + [dict(WORLD["nodes"][2], to=[93, 3.5])])
        r, page = self.build(board(w))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("moved to 4.45", r.stdout)
        self.assertRegex(page, r"countFromTo\('#wd-n2-v', 51, 93, 4\.450")

    def test_doc_mark_must_be_verbatim(self):
        r, _ = self.build(board(dict(DOC, marks=[{"text": "a paraphrase of it", "at": 21.0}])))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("not in the page text", r.stdout + r.stderr)

    def test_unknown_icon_is_named(self):
        r, _ = self.build(board({"type": "pills", "id": "pl", "in": 0.2, "out": 2.0, "anchor": "-",
                                 "items": [{"text": "A", "at": 0.4, "icon": "rocket"}]}))
        self.assertNotEqual(r.returncode, 0)
        self.assertRegex(r.stdout + r.stderr, r"unknown icon 'rocket' \(one of: .*shield")


if __name__ == "__main__":
    unittest.main()
