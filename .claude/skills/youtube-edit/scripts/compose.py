#!/usr/bin/env python3
"""compose.py: build public/index.html for a talking-head edit from a storyboard.json, using the proven
formats of the youtube-edit skill exactly as the reference builds render them (the format library in SKILL.md).

The storyboard is the review artifact AND the source of truth; retiming a beat is editing one number.
Formats covered here (the ones every segment intro / hook uses): progress tag (9, with 1-of-N pips),
lower line (2), logo card (4a), glass list card (3a), extended-left bullets (3b), punchline chip (5),
vignette + grain (17), description pointer (11), camera moves, and the one earned sound. Anything else
(big number, cutaways, diagrams, subscribe bar) is hand-authored: drop it into "raw_html" / "raw_js".

Usage:
  python3 compose.py --spec videos/<p>/storyboard.json --out videos/<p>/public --shared videos/<p>/../_shared
  (then: npx hyperframes check <out>; snapshot every beat; render)
  --shared (optional) is a folder of reusable assets: img/* and img/thumbs/* are copied to <out>/img, sfx/* to <out>/sfx
  (sfx/pop.mp3 for a logo "pop", sfx/typing.mp3 for a search "sound"). The DM Sans fonts come from the skill's own
  assets/fonts. GSAP comes from a local copy when one is found (the skill's assets/vendor/gsap.min.js, or the HyperFrames
  talking-head-recut skill's bundled copy), else the page loads it from the jsDelivr CDN.

storyboard.json:
{
  "id": "C0001", "duration": 38.0, "video": "input-video.mp4", "origin": "52% 0%",
  "tag":   {"n": 1, "of": 5, "label": "Thumbnails", "in": 0.2, "out": 5.3, "pos": "tr"},
  "beats": [
    {"type": "line",    "id": "l1", "text": "You clicked on a thumbnail", "em": [4], "color": "cyan|amber", "in": 8.5, "out": 11.6, "anchor": "clicked on a thumbnail"},
    {"type": "logo",    "id": "yt", "src": "img/youtube.svg", "in": 11.85, "out": 14.9, "pop": 11.92, "pos": "tl|tr", "anchor": "YouTube"},
    {"type": "list",    "id": "ls", "eyebrow": "", "items": [["Candles", 6.24], ["Soap", 7.12]], "in": 6.0, "out": 10.4, "pos": "tl|tr"},
    {"type": "bullets", "id": "bu", "items": [["Marketing", 38.48], ["Product catalog", 41.12]], "in": 37.9, "out": 44.9},
    {"type": "chip",    "id": "ch", "text": "let's be honest", "em": [0,1,2], "in": 24.9, "out": 27.0},
    {"type": "vignette","id": "vg", "in": 10.35, "out": 12.85},
    {"type": "pointer", "id": "pt", "in": 27.5, "out": 29.98}
  ],
  "camera": [["creep", 0.3, 5.4, 1.10], ["set", 9.70, 1.0], ["punch", 18.30, 1.18], ["release", 21.0, 0.5]],
  "raw_html": "", "raw_js": ""
}
B-roll beats (full-frame takeovers on the brand wash, hard cut in/out, optional "transition": "zoomthrough" | "punch"):
    {"type":"site",  "id":"st", "src":"img/site.png", "domain":"example.com/pricing", "scroll":500, "in":..,"out":..}
    {"type":"grid",  "id":"th", "images":["img/thumbs/a.jpg", ...6], "click_index":4, "click_at":8.9, "in":..,"out":..}
    {"type":"scene", "id":"mo", "kind":"money|catalog|room|plate|profile", "steps":{"drop":18.3}, "label":"Hundreds of dollars each", "label_em":[0,1,2], "label_color":"amber", "label_at":18.3, "in":..,"out":..}
      steps by kind: money drop | catalog fill, shine | room furnish, shine | plate snap, spice | profile card, headshot
A line can carry "shimmer": true (format 16).
Lists and bullets can carry "marker": "check" (a cyan check draws on each item); an item may be [text, t, "anchor phrase"].
DRAFT formats (each needs the creator's yes on a snapshot before it ships in a delivery):
    {"type":"browser3d","id":"b3","src":"img/site.png","domain":"example.com","scroll":600,"near":"right|left",
       "callout":{"at":..,"x":..,"y":..,"w":..,"h":..},"label":..,"in":..,"out":..}                       4c. 3D floating browser
    {"type":"fan3d","id":"fn","images":["img/a.png","img/b.png","img/c.png"],"frame":"card|phone","at":[t,t,t],
       "focus":{"index":1,"at":..},"label":..,"in":..,"out":..}                                               4d. 3D fan of screenshots
    {"type":"stats","id":"st","layout":"row|stack","pos":"tl|tr","title":"The numbers","em":[1],
       "items":[{"value":250,"prefix":"","suffix":"+","label":"Videos","at":..}],"in":..,"out":..}           24. stat tiles, count-up
    {"type":"growth","id":"gr","pos":"tl|tr","eyebrow":"Weekly views","value":248,"prefix":"+","suffix":"%",
       "sub":"since the switch","bars":[20,34,52,70,100],"count_at":..,"bars_at":..,"in":..,"out":..}         25. growth card
    {"type":"bars","id":"br","title":"Hours to ship one video","em":[3,4],
       "rows":[{"label":"Editor","value":6.5,"text":"6.5 hrs","at":..},{"label":"Claude Code","value":0.3,"text":"20 min","hi":true,"at":..}],
       "in":..,"out":..}                                                                                      26. bar comparison
    {"type":"pipeline","id":"pl","title":"","steps":[{"label":"Idea","sub":"one line","icon":"chat","at":..},
       {"label":"Paid","icon":"money","at":..,"payoff":true}],"in":..,"out":..}                               27. pipeline
    {"type":"hub","id":"hb","center":"Trust","ring_at":..,"spokes":[["Earned",t],["Inherited",t]],"resolve_at":..,"in":..,"out":..}   28. hub
    {"type":"equation","id":"eq","pos":"bottom|top","terms":[["Skills",t],["+",t],["Workflows",t],["=",t],["40 hrs saved",t,"em"]],"in":..,"out":..}   29. equation
    {"type":"wall","id":"wl","slots":["Thumbnails","Hooks","Scripts"],"filled":1,"now":1,"fill_at":..,"recap":false,"in":..,"out":..}   9c. slot wall
    {"type":"popout","id":"po","title":"What you need","items":[["A camera",t],["One script",t]],"marker":"dot|check","in":..,"out":..}   3c. glass pop-out
Icons for pipeline steps: doc browser bolt chat money check user code video mail gear chart search.
More DRAFT formats (same rule: the creator's yes on a snapshot first):
    {"type":"flow","id":"fl","title":"One video, four places","em":[3],"source":{"label":"One video","at":..},
       "outputs":[{"label":"Email","at":..},...up to 4],"result":{"label":"New subscribers","at":..},"repeat":true,"in":..,"out":..}   30. flowing paths
    {"type":"dashzoom","id":"dz","src":"img/studio.png","size":[w,h],"focus":{"x":..,"y":..,"w":..,"h":..},"find_at":..,"lift_at":..,
       "card":{"label":"Views","value":48210,"prefix":"","suffix":"","delta":"+18%","spark":[..]},"in":..,"out":..}  31. dashboard zoom
    {"type":"lens","id":"ln","title":"Welcome email","rows":[["Open rate","48%"],...up to 6],"stops":[[row,t],...],"in":..,"out":..}   32. glass focus
    growth + "morph": true, "badge": "Best week"                                                                  25. bars turn into the line
    {"type":"search","id":"sr","query":"customer discovery questions","sound":true,"cps":16,"type_at":..,
       "results":[{"title":..,"sub":..,"color":"cyan|amber|magenta|white","logo":"img/x.svg","at":..}],"in":..,"out":..}   33. search → results
    {"type":"dock","id":"dk","title":"My stack","items":[["img/claude.svg","Claude",t],...up to 7],"in":..,"out":..}   34. magnetic dock
    {"type":"masktitle","id":"mt","eyebrow":"PART 2","text":"Distribution","sub":"where the first ten come from","sub_em":[3],"in":..,"out":..}   35. masked title
    {"type":"player","id":"pv","pos":"tr|tl","label":"Watch this next","thumb":"img/thumbs/x.jpg","title":"..","length":754,
       "progress":0.3,"morph_at":..,"in":..,"out":..}                                                                36. button → player
    {"type":"image","id":"im","src":"img/x.jpg","frame":"card|full","slats":7,"reveal_at":..,"close":true,"label":..,"in":..,"out":..}   37. image reveal
    {"type":"layers","id":"ly","title":"What is inside an app","layers":[{"label":"Interface","src":"img/ui.png"},{"label":"Logic"},{"label":"Data"}],
       "split_at":..,"in":..,"out":..}                                                                              38. exploded layers
Approved formats (a camera over one canvas, numbered parts, pills, chat, doc read, video cutaway):
    {"type":"world","id":"wd","title":"","rings":[{"x":960,"y":540,"r":[200,330,460],"at":..}],
       "window":{"x":..,"y":..,"w":..,"h":..,"title":"","at":..},"dock":{"x":..,"y":..,"items":["img/a.svg"],"at":..},
       "nodes":[{"id":"pol","kind":"card|pill|orb|hex|stat|text|img","x":..,"y":.. (or "polar":[cx,cy,r,deg]),"icon":"shield",
                 "label":"..","sub":"..","no":"1","at":..,"lit":..,"lit_color":"cyan|amber|magenta","dim":t|[t,level],
                 "alerts":{"at":..,"n":4,"layout":"ring|corner"},"anchor":"spoken words",
                 stat: "value":51,"suffix":"%","bar":0.51,"to":[93,t,0.93] | text: "size":220 | img: "src","w","h"}],
       "links":[{"from":"biz","to":"pol","at":..,"dash":false,"run":true,"color":"cyan|amber|magenta"}],
       "cam":[[t,cx,cy,zoom],[t,cx,cy,zoom,dur,ease]],"label":..,"in":..,"out":..}                           39. world (camera over a canvas)
    {"type":"deck","id":"dk","head":"3 PREDICTIONS","cards":[{"title":"..","icon":"user"},...up to 4],"now":1,
       "focus_at":..,"recap_at":..,"zoom":1.5,"in":..,"out":..}                                               40. deck (numbered parts)
    {"type":"pills","id":"pl","layout":"sides|left|right|row","top":290,
       "items":[["Codebase",t],{"text":"Wrong price","at":t,"icon":"alert","tone":"cyan|amber","mark":"x","anchor":".."}],"in":..,"out":..}   41. pills
    {"type":"chat","id":"ch","frame":"float|window|phone","pos":"tl|tr","name":"Client","icon":"user",
       "messages":[["them","Did this work?",t],["me","Yes.",t,"anchor phrase"]],"in":..,"out":..}            42. chat
    {"type":"doc","id":"dc","domain":"anthropic.com/news/..","theme":"paper|dark","kicker":"","title":"..","date":"..",
       "paras":["verbatim paragraph", ...],"marks":[{"text":"verbatim passage","at":t,"p":0,"anchor":"..","focus":true}],
       "zoom":1.3,"focus":true,"in":..,"out":..}                                                              18b. doc read (format 18 + focus)
    {"type":"clip","id":"ai1","src":"broll/desk.mp4","media_start":0,"drift":true,"label":"..",
       "items":[["Fine-tune",t,"-"]],"marker":"check|dot","in":..,"out":..,"anchor":".."}                   20c. clip (video cutaway, AI b-roll)
Icons (pipeline, world, deck, pills): doc browser bolt chat money check user code video mail gear chart search shield lock robot globe
    cloud key alert folder eye bank chip.
Camera ops: set t scale | creep t0 t1 scale (power1.inOut) | punch t scale (0.32 s power2.out) | release t dur (to 1.0) | reveal t (1.10 to 1.00 as a card enters).
Positions: tl = left:70 top:96 (desk framing, clears the mic), tr = right:70 top:96.
"""
import argparse, json, os, shutil, glob, math, struct
from html import escape as _esc

hesc = lambda s: _esc(s, quote=False)

ap = argparse.ArgumentParser()
ap.add_argument("--spec", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--shared", default="")
args = ap.parse_args()
S = json.load(open(args.spec))
OUT = args.out
os.makedirs(OUT, exist_ok=True)

# ---- stage shared assets (fonts, gsap, logos, sfx) ---------------------------------------------------
SKILL = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # this skill's folder (youtube-edit)
ROOT = os.path.abspath(os.path.join(SKILL, "..", "..", ".."))                               # the project, for <project>/.claude/skills/youtube-edit
def stage(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(src) and not os.path.exists(dst):
        shutil.copy(src, dst)
# THE VIDEO FONT: the three 7 KB DMSans-400/500/700 files in the skill's own assets/fonts, with the stack below. They are
# glyph subsets, so Chrome draws the text in the system face (San Francisco on a Mac) with these exact metrics, and that
# is the approved look. The full variable DM Sans reads rounder and wider. Do not "fix" this to the full DM Sans file.
FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts")
fonts = sorted(glob.glob(os.path.join(FONTS, "*.woff2")))
if not fonts:
    print("WARN no .woff2 fonts in %s: the text falls back to the system sans" % os.path.abspath(FONTS))
for f in fonts:
    stage(f, os.path.join(OUT, "fonts", os.path.basename(f)))
# GSAP: a local copy when one exists (renders work offline): the skill's assets/vendor/gsap.min.js, else the copy bundled
# with the HyperFrames talking-head-recut skill (installed in the project or the home folder). Otherwise the page loads
# the CDN build the HyperFrames docs use.
GSAP_CDN = "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"
for cand in [os.path.join(SKILL, "assets", "vendor", "gsap.min.js")] + [
        os.path.join(base, hidden, "skills", "talking-head-recut", "assets", "vendor", "gsap.min.js")
        for base in (ROOT, os.getcwd(), os.path.expanduser("~")) for hidden in (".agents", ".claude")]:
    if os.path.exists(cand):
        stage(cand, os.path.join(OUT, "vendor", "gsap.min.js"))
        break
GSAP_SRC = "vendor/gsap.min.js" if os.path.exists(os.path.join(OUT, "vendor", "gsap.min.js")) else GSAP_CDN
if GSAP_SRC == GSAP_CDN:
    print("note: no local gsap.min.js, the page loads GSAP from %s (drop a copy in %s to render offline)"
          % (GSAP_CDN, os.path.join(SKILL, "assets", "vendor")))
if args.shared:
    for f in glob.glob(os.path.join(args.shared, "img/*")):
        if os.path.isfile(f): stage(f, os.path.join(OUT, "img", os.path.basename(f)))
    for f in glob.glob(os.path.join(args.shared, "img/thumbs/*")):
        stage(f, os.path.join(OUT, "img", "thumbs", os.path.basename(f)))
    for f in glob.glob(os.path.join(args.shared, "sfx/*")):
        stage(f, os.path.join(OUT, "sfx", os.path.basename(f)))

D = float(S["duration"])
origin = S.get("origin", "52% 0%")
POS = {"tl": "left:70px; top:96px;", "tr": "right:70px; top:96px;"}

CSS = """
  @font-face { font-family: "DM Sans"; src: url("fonts/DMSans-400.woff2") format("woff2"); font-weight: 400; font-display: block; }
  @font-face { font-family: "DM Sans"; src: url("fonts/DMSans-500.woff2") format("woff2"); font-weight: 500; font-display: block; }
  @font-face { font-family: "DM Sans"; src: url("fonts/DMSans-700.woff2") format("woff2"); font-weight: 700; font-display: block; }
  * { box-sizing: border-box; }
  html, body { margin:0; padding:0; width:100%; height:100%; overflow:hidden; background:#000;
    font-family: "DM Sans", ui-sans-serif, system-ui, sans-serif; }
  #stage { position:relative; width:100%; height:100%; overflow:hidden; background:#000; }
  :root { --cyan:#0AF0F0; --blue:#0005EE; --magenta:#CD00EE; --amber:#FFB904; --white:#FFFFFF; }
  .video-wrapper { position:absolute; left:0; top:0; width:1920px; height:1080px; overflow:hidden; transform-origin:50% 0%; will-change:transform; }
  #video-zoom { position:absolute; inset:0; transform-origin:ORIGIN; will-change:transform; }
  #video-zoom video { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; display:block; }
  #bg-video { z-index:1; }
  .card-host { position:absolute; pointer-events:none; overflow:hidden; z-index:10; }
  .card-host .card { position:relative; width:100%; height:100%; overflow:hidden; }
  /* 2. Lower line: words rise into place, staggered. No box, always centred. */
  .lower { position:absolute; left:50%; bottom:84px; transform:translateX(-50%); font-weight:700; line-height:1.12; color:var(--white);
    white-space:nowrap; letter-spacing:-.015em; font-size:0; text-shadow: 0 3px 8px rgba(0,0,0,.85), 0 8px 36px rgba(0,0,0,.7); }
  .lower .w { display:inline-block; font-size:100px; opacity:0; }
  .lower .sp { display:inline-block; font-size:100px; width:.26em; }
  .lower .w.em { color:var(--cyan); }
  .lower.amber .w.em { color:var(--amber); }
  /* light glass: the look is animated in, never an ancestor's opacity */
  .glass { position:absolute; border-radius:26px; background: rgba(255,255,255,0);
    backdrop-filter: blur(30px) saturate(1.25); -webkit-backdrop-filter: blur(30px) saturate(1.25);
    border: 3px solid rgba(255,255,255,0); box-shadow: 0 24px 80px rgba(0,0,0,0); }
  /* 9. progress tag: 1-of-N pips + the section name, top corner, holds ~5 s */
  .tag { position:absolute; display:flex; align-items:center; gap:22px; padding:18px 34px 18px 30px; border-radius:999px; }
  .tag .inner { display:flex; align-items:center; gap:22px; opacity:0; }
  .tag .pips { display:flex; gap:10px; }
  .tag .pip { width:16px; height:16px; border-radius:50%; background:rgba(255,255,255,.28); }
  .tag .pip.done { background:rgba(255,255,255,.85); }
  .tag .pip.now { background:var(--cyan); box-shadow: 0 0 14px rgba(10,240,240,.9); }
  .tag .label { font-weight:700; font-size:34px; color:var(--white); line-height:1; text-shadow: 0 2px 10px rgba(0,0,0,.7); }
  /* 4a. logo plate: logo only, big */
  .logo-plate { width:380px; height:386px; }
  .logo-plate .inner { opacity:0; width:100%; height:100%; display:flex; align-items:center; justify-content:center; }
  .logo-plate .inner img { max-height:264px; max-width:290px; width:auto; height:auto; display:block; filter: drop-shadow(0 4px 14px rgba(0,0,0,.45)); }
  /* 3a. glass list card: grows with its items */
  .list { width:600px; padding:28px 32px 16px; }
  .list .inner { opacity:0; }
  .list .eyebrow { font-weight:700; font-size:30px; color:rgba(255,255,255,.92); line-height:1; margin-bottom:22px; text-shadow: 0 2px 8px rgba(0,0,0,.8); }
  .list .item { display:none; align-items:center; gap:22px; margin-bottom:22px; }
  .list .item .d { width:20px; height:20px; border-radius:50%; background:var(--white); flex:none; box-shadow: 0 2px 8px rgba(0,0,0,.6); }
  .list .item .t { font-weight:700; font-size:64px; line-height:1.05; color:var(--white); letter-spacing:-.012em; white-space:nowrap;
    text-shadow: 0 2px 8px rgba(0,0,0,.85), 0 8px 30px rgba(0,0,0,.5); }
  /* 3b. extended-left bullets: footage pushed right, scrim, text straight on the dark */
  .scrim { position:absolute; inset:0; opacity:0; background: linear-gradient(90deg, rgba(0,0,0,.97) 0%, rgba(0,0,0,.82) 34%, rgba(0,0,0,.45) 46%, rgba(0,0,0,0) 60%); }
  .bullets { position:absolute; left:96px; top:318px; width:760px; }
  .bullets .b { display:none; align-items:center; gap:26px; margin-bottom:40px; }
  .bullets .b .d { width:22px; height:22px; border-radius:50%; background:var(--cyan); box-shadow: 0 0 16px rgba(10,240,240,.75); flex:none; }
  .bullets .b .t { font-weight:700; font-size:68px; line-height:1.05; color:var(--white); letter-spacing:-.012em; white-space:nowrap;
    text-shadow: 0 3px 8px rgba(0,0,0,.85), 0 8px 36px rgba(0,0,0,.6); }
  /* 5. punchline chip: dark glass, large, emphasis in magenta */
  .chip { position:absolute; left:50%; bottom:80px; transform:translateX(-50%); padding:22px 40px; border-radius:16px;
    background: rgba(17,17,17,0); backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px); white-space:nowrap; }
  .chip .inner { opacity:0; font-weight:700; font-size:70px; line-height:1.1; color:var(--white); letter-spacing:-.012em; text-shadow: 0 2px 10px rgba(0,0,0,.6); }
  .chip .inner .em { color:var(--magenta); }
  /* 17. vignette + grain: a beat, not a look */
  .vig { position:absolute; inset:0; opacity:0; background: radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 38%, rgba(0,0,0,.78) 100%); }
  .grain { position:absolute; inset:0; opacity:0; mix-blend-mode: overlay;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='220' height='220'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' seed='7' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E"); }
  /* 11. description pointer: glass bar low in frame, chevrons cascade beneath */
  .pointer { left:0; right:0; margin:0 auto; width:max-content; bottom:34px; padding:22px 44px 26px; border-radius:22px; white-space:nowrap; }
  .pointer .inner { opacity:0; display:flex; flex-direction:column; align-items:center; gap:10px; }
  .pointer .txt { font-weight:700; font-size:56px; line-height:1.1; color:var(--white); letter-spacing:-.012em; text-shadow: 0 2px 10px rgba(0,0,0,.7); }
  .pointer .txt .em { color:var(--cyan); }
  .pointer .chev { position:relative; height:34px; width:60px; }
  .pointer .chev span { position:absolute; left:50%; top:0; width:26px; height:26px; margin-left:-13px; border-right:5px solid var(--cyan); border-bottom:5px solid var(--cyan);
    transform: rotate(45deg); opacity:0; filter: drop-shadow(0 0 8px rgba(10,240,240,.8)); }

  /* ---- B-roll takeovers (formats 4b, 20, custom scenes): ambient wash + 96px grid, never flat black ---- */
  .cut { position:absolute; inset:0; background:
      radial-gradient(900px 600px at 12% 8%, rgba(0,5,238,.28), transparent 70%),
      radial-gradient(700px 500px at 90% 95%, rgba(10,240,240,.14), transparent 70%), #05060c; }
  .gridbg { position:absolute; inset:0; opacity:.28; background-image:
      linear-gradient(rgba(255,255,255,.09) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.09) 1px, transparent 1px);
      background-size:96px 96px; }
  .slabel { position:absolute; left:0; right:0; bottom:84px; text-align:center; font-weight:700; font-size:88px; line-height:1.1; color:var(--white);
    letter-spacing:-.015em; white-space:nowrap; text-shadow: 0 3px 8px rgba(0,0,0,.85), 0 8px 36px rgba(0,0,0,.7); opacity:0; }
  .slabel .em { color:var(--cyan); } .slabel.amber .em { color:var(--amber); }
  /* 4b. full-screen site cutaway: 62px chrome bar, bare domain in a pill, page drifts */
  .site { position:absolute; inset:0; background:#fff; overflow:hidden; }
  .site .chrome { position:absolute; left:0; right:0; top:0; height:62px; background:#1d1d1f; display:flex; align-items:center; padding:0 22px; gap:10px; z-index:2; }
  .site .chrome .dot { width:14px; height:14px; border-radius:50%; } .site .chrome .r { background:#ff5f57; } .site .chrome .y { background:#febc2e; } .site .chrome .g { background:#28c840; }
  .site .chrome .url { margin-left:18px; padding:8px 20px; border-radius:999px; background:#2c2c2e; color:#e5e5e7; font-size:21px; font-weight:500; line-height:1; }
  .site .pagewrap { position:absolute; left:0; right:0; top:62px; bottom:0; overflow:hidden; }
  .site .page { position:absolute; left:0; top:0; width:1920px; height:auto; display:block; transform-origin:50% 0%; }
  /* thumbnail grid + the oversized cursor */
  .tgrid { position:absolute; left:92px; top:211px; width:1736px; height:658px; display:grid; grid-template-columns:repeat(3, 560px); grid-auto-rows:315px; gap:28px; }
  .tgrid .tile { position:relative; border-radius:16px; overflow:hidden; box-shadow: 0 18px 50px rgba(0,0,0,.5); border:2px solid rgba(255,255,255,.12); opacity:0; transform-origin:50% 50%; }
  .tgrid .tile img { width:100%; height:100%; object-fit:cover; display:block; }
  .tgrid .tile .ring { position:absolute; inset:0; border:5px solid var(--cyan); border-radius:16px; opacity:0; box-shadow: 0 0 26px rgba(10,240,240,.75), inset 0 0 26px rgba(10,240,240,.35); }
  .cursor { position:absolute; width:134px; height:134px; z-index:30; filter: drop-shadow(0 4px 6px rgba(0,0,0,.35)); pointer-events:none; will-change:transform; transform-origin:21% 14%; }
  /* scene glyphs: line art in white on the wash, colour only where it means something */
  .scene { position:absolute; inset:0; }
  .scene svg { position:absolute; overflow:visible; }
  .scene .chip { position:absolute; width:124px; height:124px; border-radius:50%; background:var(--amber); color:#1a1200; font-weight:700; font-size:70px; line-height:124px; text-align:center;
    box-shadow: 0 14px 40px rgba(0,0,0,.45), inset 0 -6px 0 rgba(0,0,0,.18); opacity:0; }
  .scene .frame { position:absolute; width:400px; height:260px; border-radius:16px; background:rgba(255,255,255,.08); border:3px solid rgba(255,255,255,.55); overflow:hidden; opacity:0; }
  .scene .frame svg { left:0; top:0; width:100%; height:100%; }
  .scene .shine { position:absolute; top:-20%; left:-40%; width:26%; height:140%; will-change:transform; background: linear-gradient(90deg, transparent, rgba(10,240,240,.55), rgba(255,255,255,.9), rgba(10,240,240,.55), transparent);
    transform: skewX(-18deg); opacity:0; mix-blend-mode:screen; }
  .scene .phone { position:absolute; left:250px; top:110px; width:420px; height:860px; border-radius:60px; background:#0b0d16; border:6px solid rgba(255,255,255,.55); box-shadow: 0 30px 90px rgba(0,0,0,.6); overflow:hidden; opacity:0; }
  .scene .phone .screen { position:absolute; inset:16px; border-radius:46px; background:#151826; overflow:hidden; }
  .scene .phone .notch { position:absolute; left:50%; top:22px; width:150px; height:34px; margin-left:-75px; border-radius:999px; background:#000; }
  .scene .hero { position:absolute; left:960px; top:120px; width:760px; height:760px; opacity:0; transform-origin:50% 50%; }
  .scene .hero svg { left:0; top:0; width:100%; height:100%; filter: drop-shadow(0 30px 60px rgba(0,0,0,.6)); }
  .scene .sparkle { position:absolute; width:26px; height:26px; opacity:0; }
  .scene .sparkle::before, .scene .sparkle::after { content:""; position:absolute; left:50%; top:50%; width:100%; height:5px; margin:-2.5px 0 0 -50%; background:var(--cyan); border-radius:3px; box-shadow: 0 0 12px rgba(10,240,240,.9); }
  .scene .sparkle::after { transform:rotate(90deg); }
  .scene .card { position:absolute; left:460px; top:180px; width:1000px; height:620px; border-radius:26px; background:#fff; overflow:hidden; box-shadow: 0 30px 90px rgba(0,0,0,.6); opacity:0; }
  .scene .card .band { position:absolute; left:0; right:0; top:0; height:190px; background:#0A66C2; }
  .scene .card .avatar { position:absolute; left:64px; top:100px; width:220px; height:220px; border-radius:50%; background:#dfe6ee; border:8px solid #fff; overflow:hidden; }
  .scene .card .avatar svg { left:0; top:0; width:100%; height:100%; }
  .scene .card .ring { position:absolute; left:56px; top:92px; width:236px; height:236px; border-radius:50%; border:6px solid var(--cyan); box-shadow: 0 0 30px rgba(10,240,240,.85); opacity:0; }
  .scene .card .bar { position:absolute; height:26px; border-radius:13px; background:#e3e8ee; transform-origin:0 50%; }
  .scene .card .logo { position:absolute; right:44px; bottom:36px; width:110px; height:110px; }   /* on the white, never on the blue band */
  .scene .card .logo img { width:100%; height:100%; display:block; }
  .lower.shine .w { --c:#fff; --b:var(--cyan); background-image: linear-gradient(90deg, var(--c) 0%, var(--c) 42%, var(--b) 50%, var(--c) 58%, var(--c) 100%);
    background-repeat:no-repeat; background-position:-9999px 0; -webkit-background-clip:text; background-clip:text; color:transparent; text-shadow:none; }
  .lower.shine .w.em { --c:var(--cyan); --b:#fff; }
  .lower.shine.amber .w.em { --c:var(--amber); --b:#fff; }
  .lower.shine { text-shadow:none; filter: drop-shadow(0 3px 8px rgba(0,0,0,.85)) drop-shadow(0 8px 30px rgba(0,0,0,.6)); }

  /* ---- DRAFT formats: same tokens, same glass, same motion law ---- */
  .tsh { text-shadow: 0 2px 8px rgba(0,0,0,.85), 0 8px 30px rgba(0,0,0,.5); }
  /* check marker for lists and bullets: ring, then a cyan fill and a drawn check */
  .mk { position:relative; flex:none; width:44px; height:44px; }
  .mk svg { position:absolute; left:0; top:0; width:44px; height:44px; overflow:visible; }
  .mk .ring { fill:rgba(10,240,240,0); stroke:rgba(255,255,255,.85); stroke-width:3.5; }
  .mk .tick { fill:none; stroke:#04161a; stroke-width:5; stroke-linecap:round; stroke-linejoin:round; }
  /* 4c. 3D floating browser: a slanted window on the wash, a slow orbit while the page scrolls */
  .b3-stage { position:absolute; inset:0; perspective:2400px; perspective-origin:50% 38%; }
  .b3-rig { position:absolute; left:50%; top:118px; width:1340px; height:830px; margin-left:-670px; transform-style:preserve-3d; will-change:transform; }
  .b3-floor { position:absolute; left:12%; right:12%; bottom:-40px; height:24px; border-radius:50%; background:rgba(0,0,0,.35);
    box-shadow: 0 0 60px 40px rgba(0,0,0,.45); }   /* a box-shadow, not filter:blur: heavy-overlay budget */
  .b3-win { position:absolute; inset:0; border-radius:22px; overflow:hidden; background:#0d0f16;
    box-shadow: 0 70px 140px rgba(0,0,0,.6), 0 0 0 2px rgba(255,255,255,.16), 0 0 160px 20px rgba(10,240,240,.16); }
  .b3-bar { position:absolute; left:0; right:0; top:0; height:58px; background:#16181f; display:flex; align-items:center; padding:0 22px; gap:10px; z-index:3;
    border-bottom:1px solid rgba(255,255,255,.08); }
  .b3-bar .dot { width:14px; height:14px; border-radius:50%; } .b3-bar .r { background:#ff5f57; } .b3-bar .y { background:#febc2e; } .b3-bar .g { background:#28c840; }
  .b3-bar .url { margin-left:18px; padding:8px 22px; border-radius:999px; background:#262a33; color:#e5e5e7; font-size:21px; font-weight:500; line-height:1; }
  .b3-view { position:absolute; left:0; right:0; top:58px; bottom:0; overflow:hidden; }
  .b3-scroll { position:absolute; left:0; top:0; width:100%; will-change:transform; }
  .b3-scroll img { width:100%; height:auto; display:block; }
  .b3-call { position:absolute; border:5px solid var(--cyan); border-radius:14px; opacity:0; box-shadow: 0 0 30px rgba(10,240,240,.7), inset 0 0 20px rgba(10,240,240,.25); }
  .b3-sheen { position:absolute; top:-10%; left:-35%; width:22%; height:120%; z-index:4; opacity:0; transform:skewX(-16deg); will-change:transform;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,.16), rgba(255,255,255,.30), rgba(255,255,255,.16), transparent); mix-blend-mode:screen; }
  /* 4d. 3D fan: two or three screenshots in depth, the middle one forward */
  .fan-stage { position:absolute; inset:0; perspective:2200px; perspective-origin:50% 42%; }
  .fan-rig { position:absolute; left:50%; top:50%; width:0; height:0; transform-style:preserve-3d; will-change:transform; }
  .fan-card { position:absolute; border-radius:24px; overflow:hidden; background:#0d0f16; opacity:0; will-change:transform;
    box-shadow: 0 50px 110px rgba(0,0,0,.6), 0 0 0 2px rgba(255,255,255,.16); }
  .fan-card img { width:100%; height:100%; object-fit:cover; object-position:50% 0%; display:block; }
  .fan-card.browser { border-radius:18px; background:#fff; box-shadow: 0 50px 110px rgba(0,0,0,.55), 0 0 0 1px rgba(255,255,255,.2); }
  .fan-card.browser .fb-bar { position:absolute; left:0; top:0; right:0; height:46px; background:#eceef1; border-bottom:1px solid #d6d9de;
    display:flex; align-items:center; gap:8px; padding-left:18px; }
  .fan-card.browser .fb-dot { width:13px; height:13px; border-radius:50%; flex:none; }
  .fan-card.browser .fb-url { flex:1; margin:0 18px 0 16px; height:28px; line-height:28px; padding:0 14px; border-radius:14px; background:#fff;
    color:#3c4043; font-size:15px; font-weight:500; white-space:nowrap; overflow:hidden; }
  .fan-card.browser .fb-view { position:absolute; left:0; right:0; top:47px; bottom:0; overflow:hidden; background:#fff; }
  .fan-card.browser .fb-view img { width:100%; height:auto; object-fit:fill; display:block; }
  .fan-card.browser .fb-view.contain { display:flex; align-items:center; justify-content:center; background:#f4f6f8; }
  .fan-card.browser .fb-view.contain img { width:92%; height:auto; max-height:94%; object-fit:contain; }
  .fan-card.phone { border-radius:56px; border:10px solid #111318; box-shadow: 0 50px 110px rgba(0,0,0,.6), 0 0 0 2px rgba(255,255,255,.22); }
  /* 24. stat tiles: glass, the number counts up in full digits */
  .st-title { position:absolute; left:0; right:0; top:170px; text-align:center; font-weight:700; font-size:76px; line-height:1.1; color:#fff; letter-spacing:-.015em; opacity:0; }
  .st-title .em { color:var(--cyan); }
  .st-row { position:absolute; left:0; right:0; top:380px; display:flex; justify-content:center; gap:36px; }
  .st-tile { position:relative; width:480px; padding:44px 44px 40px; }
  .st-stack { position:absolute; display:flex; flex-direction:column; gap:22px; }
  .st-stack .st-tile { width:520px; padding:30px 38px 28px; }
  .st-tile .inner { opacity:0; }
  .st-num { font-weight:700; font-size:112px; line-height:1; color:#fff; letter-spacing:-.02em; white-space:nowrap; font-variant-numeric:tabular-nums; }
  .st-stack .st-num { font-size:92px; }
  .st-tile.em .st-num { color:var(--cyan); }
  .st-lab { margin-top:16px; font-weight:700; font-size:34px; line-height:1.1; color:rgba(255,255,255,.9); }
  /* 25. growth card: count-up, bars rise, the line draws, one dot lands */
  .gr { width:600px; padding:34px 38px 30px; }
  .gr .inner { opacity:0; }
  .gr-eye { font-weight:700; font-size:30px; line-height:1; color:rgba(255,255,255,.92); }
  .gr-num { margin-top:14px; font-weight:700; font-size:120px; line-height:1; color:var(--cyan); letter-spacing:-.02em; white-space:nowrap; font-variant-numeric:tabular-nums; }
  .gr-sub { margin-top:10px; font-weight:700; font-size:30px; line-height:1.1; color:rgba(255,255,255,.85); }
  .gr-plot { position:relative; margin-top:26px; height:250px; }
  .gr-bars { position:absolute; left:0; right:0; bottom:0; height:250px; display:flex; align-items:flex-end; gap:16px; }
  .gr-bar { flex:1; border-radius:10px 10px 3px 3px; transform-origin:50% 100%;
    background: linear-gradient(180deg, rgba(255,255,255,.85), rgba(255,255,255,.22)); box-shadow: 0 0 0 1px rgba(255,255,255,.18) inset; }
  .gr-bar.last { background: linear-gradient(180deg, var(--cyan), rgba(10,240,240,.30)); box-shadow: 0 0 26px rgba(10,240,240,.45); }
  .gr-plot svg { position:absolute; left:0; top:0; width:100%; height:100%; overflow:visible; }
  .gr-line { fill:none; stroke:#fff; stroke-width:6; stroke-linecap:round; stroke-linejoin:round; filter: drop-shadow(0 0 8px rgba(10,240,240,.8)); }
  .gr-dot { fill:#fff; opacity:0; filter: drop-shadow(0 0 12px rgba(10,240,240,1)); }
  /* 26. bar comparison: one row is ours, in cyan; the rest stay white and quiet */
  .bc { position:absolute; left:210px; right:210px; top:300px; }
  .bc-row { display:flex; align-items:center; gap:34px; height:118px; opacity:0; }
  .bc-lab { width:380px; flex:none; text-align:right; font-weight:700; font-size:46px; line-height:1.05; color:rgba(255,255,255,.88); white-space:nowrap; }
  .bc-track { position:relative; flex:1; height:62px; border-radius:14px; background:rgba(255,255,255,.07); }
  .bc-fill { position:absolute; left:0; top:0; bottom:0; border-radius:14px; transform-origin:0 50%;
    background: linear-gradient(90deg, rgba(255,255,255,.30), rgba(255,255,255,.62)); }
  .bc-row.hi .bc-lab { color:#fff; }
  .bc-row.hi .bc-fill { background: linear-gradient(90deg, rgba(10,240,240,.55), var(--cyan)); box-shadow: 0 0 34px rgba(10,240,240,.55); }
  .bc-val { position:absolute; top:50%; margin-left:22px; transform:translateY(-50%); font-weight:700; font-size:46px; color:#fff; white-space:nowrap; opacity:0; }
  .bc-row.hi .bc-val { color:var(--cyan); }
  /* 27. pipeline: glass nodes, connectors draw, a light runs the rail, each node lights on its word */
  .pl { position:absolute; left:0; right:0; top:410px; height:330px; }
  .pl-node { position:absolute; top:0; width:290px; height:290px; padding:0; border-radius:30px; }
  .pl-node .inner { position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:14px; opacity:0; }
  .pl-node svg { width:92px; height:92px; overflow:visible; }
  .pl-node .ic { fill:none; stroke:#fff; stroke-width:4.5; stroke-linecap:round; stroke-linejoin:round; }
  .pl-lab { font-weight:700; font-size:44px; line-height:1.05; color:#fff; text-align:center; padding:0 16px; }
  .pl-sub { font-weight:700; font-size:26px; line-height:1.1; color:rgba(255,255,255,.75); text-align:center; padding:0 18px; }
  .pl-num { position:absolute; left:22px; top:18px; font-weight:700; font-size:26px; color:rgba(255,255,255,.6); }
  .pl-link { position:absolute; top:143px; height:5px; border-radius:3px; background:rgba(255,255,255,.55); transform-origin:0 50%; }
  .pl-run { position:absolute; top:136px; width:19px; height:19px; margin-left:-9px; border-radius:50%; background:var(--cyan); opacity:0;
    box-shadow: 0 0 18px rgba(10,240,240,1), 0 0 44px rgba(10,240,240,.7); }
  .pl-title { position:absolute; left:0; right:0; top:150px; text-align:center; font-weight:700; font-size:72px; line-height:1.1; color:#fff; letter-spacing:-.015em; opacity:0; }
  .pl-title .em { color:var(--cyan); }
  /* 28. hub: one idea in the middle, the parts arrive around it */
  .hb-c { position:absolute; left:810px; top:390px; width:300px; height:300px; border-radius:50%; display:flex; align-items:center; justify-content:center; }
  .hb-c .inner { opacity:0; font-weight:700; font-size:54px; line-height:1.05; color:#fff; text-align:center; padding:0 20px; }
  .hb-svg { position:absolute; left:0; top:0; width:1920px; height:1080px; overflow:visible; }
  .hb-ring { fill:none; stroke:var(--cyan); stroke-width:5; filter: drop-shadow(0 0 10px rgba(10,240,240,.8)); }
  .hb-spoke { stroke:rgba(255,255,255,.55); stroke-width:4; stroke-linecap:round; }
  .hb-pill { position:absolute; padding:22px 36px; border-radius:999px; white-space:nowrap; }
  .hb-pill .inner { opacity:0; font-weight:700; font-size:44px; line-height:1; color:#fff; }
  /* 29. equation: terms rise into one glass strip, the result lands in cyan */
  .eq { position:absolute; left:0; right:0; margin:0 auto; width:max-content; padding:26px 48px; border-radius:26px; white-space:nowrap; }
  .eq .inner { display:flex; align-items:baseline; gap:28px; }
  .eq .tk { font-weight:700; font-size:76px; line-height:1.05; color:#fff; letter-spacing:-.015em; opacity:0; }
  .eq .tk.op { color:rgba(255,255,255,.6); }
  .eq .tk.em { color:var(--cyan); }
  .eq .tk.pay { color:var(--magenta); }
  /* 9c. slot wall: N sockets planted in the hook, one filled per section, the full wall at the recap */
  .wl { position:absolute; left:0; right:0; margin:0 auto; top:28px; width:max-content; padding:16px 18px; border-radius:24px; }
  .wl .inner { display:flex; gap:14px; opacity:0; position:relative; }
  .wl-slot { position:relative; width:264px; height:74px; border-radius:16px; border:3px dashed rgba(255,255,255,.55); display:flex; align-items:center; gap:12px; padding:0 16px; }
  .wl-slot .n { position:relative; flex:none; font-weight:700; font-size:22px; color:rgba(255,255,255,.6); }
  .wl-slot .t { position:relative; font-weight:700; font-size:30px; line-height:1; color:#fff; white-space:nowrap; opacity:0; }
  .wl-slot.done { border-style:solid; border-color:rgba(255,255,255,.35); background:rgba(255,255,255,.06); }
  .wl-slot.done .t { opacity:.56; }
  .wl-slot .n, .wl-slot .t { z-index:1; }
  .wl-slot .fill { position:absolute; inset:-3px; border-radius:16px; border:3px solid var(--cyan); background:rgba(10,240,240,.14); opacity:0;
    box-shadow: 0 0 24px rgba(10,240,240,.55); }
  .wl-thread { position:absolute; left:8px; right:8px; bottom:-12px; height:4px; border-radius:2px; background:var(--cyan); transform-origin:0 50%;
    box-shadow: 0 0 16px rgba(10,240,240,.9); }
  /* 3c. glass pop-out: footage pushed right (as 3b), a light glass panel carries the items on the left */
  .po { left:72px; top:230px; min-width:560px; max-width:820px; padding:40px 48px 20px; }
  .po .inner { opacity:0; }
  .po .ttl { font-weight:700; font-size:40px; line-height:1.1; color:rgba(255,255,255,.95); margin-bottom:30px; }
  .po .item { display:none; align-items:center; gap:24px; margin-bottom:30px; }
  .po .item .d { width:22px; height:22px; border-radius:50%; background:var(--cyan); flex:none; box-shadow: 0 0 14px rgba(10,240,240,.7); }
  .po .item .t { font-weight:700; font-size:62px; line-height:1.05; color:#fff; letter-spacing:-.012em; white-space:nowrap; }

  /* ---- more DRAFT formats, rebuilt in the house look ---- */
  .fx-title { position:absolute; left:0; right:0; top:110px; text-align:center; font-weight:700; font-size:68px; line-height:1.1; color:#fff; letter-spacing:-.015em; opacity:0; }
  .fx-title .em { color:var(--cyan); }
  /* 30. flow: one input, light runs out along curved paths to N outputs, then they converge on one result */
  .fl-svg { position:absolute; left:0; top:0; width:1920px; height:1080px; overflow:visible; }
  .fl-path { fill:none; stroke:rgba(255,255,255,.16); stroke-width:4; }
  .fl-glow { fill:none; stroke:rgba(10,240,240,.22); stroke-width:16; stroke-linecap:round; }
  .fl-lit { fill:none; stroke:var(--cyan); stroke-width:5; stroke-linecap:round; }
  .fl-glow.pay { stroke:rgba(205,0,238,.25); } .fl-lit.pay { stroke:var(--magenta); }
  .fl-node { position:absolute; width:340px; height:104px; margin:-52px 0 0 -170px; border-radius:52px; display:flex; align-items:center; justify-content:center; }
  .fl-node .inner { display:flex; align-items:center; gap:18px; opacity:.42; }
  .fl-ring { position:absolute; inset:-4px; border-radius:56px; border:3px solid var(--cyan); opacity:0; pointer-events:none; }
  .fl-node .dot { width:20px; height:20px; border-radius:50%; background:rgba(255,255,255,.55); flex:none; }
  .fl-node .lab { font-weight:700; font-size:42px; line-height:1; color:#fff; white-space:nowrap; }
  .fl-pulse { position:absolute; left:0; top:0; width:24px; height:24px; margin:-12px 0 0 -12px; border-radius:50%; background:#fff; opacity:0;
    box-shadow: 0 0 18px rgba(10,240,240,1), 0 0 44px rgba(10,240,240,.7); }
  .fl-pulse.pay { box-shadow: 0 0 18px rgba(205,0,238,1), 0 0 44px rgba(205,0,238,.7); }
  /* 31. dashboard zoom: a real dashboard screenshot, the camera finds one tile, the tile lifts out as a glass card */
  .dz-layer { position:absolute; left:0; top:0; width:1920px; height:1080px; transform-origin:0 0; will-change:transform; }
  .dz-img { position:absolute; border-radius:18px; box-shadow: 0 50px 120px rgba(0,0,0,.6), 0 0 0 2px rgba(255,255,255,.14); }
  .dz-dim { position:absolute; inset:0; background:rgba(3,4,10,.66); opacity:0; }
  .dz-br { position:absolute; opacity:0; }
  .dz-br span { position:absolute; width:34px; height:34px; border:0 solid var(--cyan); }
  .dz-br .a { left:-8px; top:-8px; border-left-width:5px; border-top-width:5px; border-top-left-radius:8px; }
  .dz-br .b { right:-8px; top:-8px; border-right-width:5px; border-top-width:5px; border-top-right-radius:8px; }
  .dz-br .c { left:-8px; bottom:-8px; border-left-width:5px; border-bottom-width:5px; border-bottom-left-radius:8px; }
  .dz-br .d { right:-8px; bottom:-8px; border-right-width:5px; border-bottom-width:5px; border-bottom-right-radius:8px; }
  .dz-leads { position:absolute; left:0; top:0; width:1920px; height:1080px; overflow:visible; opacity:0; }
  .dz-leads line { stroke:var(--cyan); stroke-width:2; stroke-dasharray:6 9; stroke-linecap:round; }
  .dz-card { left:580px; top:330px; width:760px; height:420px; padding:40px 48px 0; }
  .dz-card .inner { opacity:0; }
  .dz-top { display:flex; justify-content:space-between; align-items:center; }
  .dz-lab { font-weight:700; font-size:36px; color:rgba(255,255,255,.92); }
  .dz-delta { font-weight:700; font-size:30px; color:#04161a; background:var(--cyan); padding:8px 18px; border-radius:999px; }
  .dz-num { margin-top:14px; font-weight:700; font-size:132px; line-height:1; color:#fff; letter-spacing:-.02em; white-space:nowrap; font-variant-numeric:tabular-nums; }
  .dz-spark { display:block; margin-top:22px; width:664px; height:110px; overflow:visible; }
  .dz-spark path { fill:none; stroke:var(--cyan); stroke-width:6; stroke-linecap:round; stroke-linejoin:round; }
  /* 32. glass focus: a table in glass, a lens walks row to row on the words, the rest recede */
  .ln-card { left:360px; top:150px; width:1200px; padding:40px 56px 44px; }
  .ln-card .inner { opacity:0; }
  .ln-ttl { font-weight:700; font-size:44px; color:#fff; margin-bottom:22px; }
  .ln-rows { position:relative; }
  .ln-row { position:relative; display:flex; justify-content:space-between; align-items:center; height:104px; padding:0 36px; font-weight:700; font-size:50px; color:#fff; }
  .ln-row .v { font-variant-numeric:tabular-nums; }
  .ln-base { filter: blur(2.6px); opacity:.62; }           /* out of focus, a static blur */
  .ln-lens { position:absolute; left:-14px; right:-14px; top:0; height:120px; border-radius:60px; overflow:hidden; opacity:0;
    background:rgba(14,17,26,.94); border:2px solid rgba(255,255,255,.9); box-shadow: inset 0 0 0 3px rgba(10,240,240,.45), 0 10px 34px rgba(0,0,0,.35); }
  .ln-win { position:absolute; left:12px; right:12px; top:-2px; }   /* rows-aligned: the lens sits 14 px wider and has a 2 px rim */
  .ln-win .ln-row { font-size:54px; }                       /* the magnification: same centre, a size up */
  .ln-fr { position:absolute; left:0; right:0; top:0; }
  .ln-fr.c { transform:translateX(-1.5px); opacity:.38; } .ln-fr.c .ln-row { color:var(--cyan); }
  .ln-fr.m { transform:translateX(1.5px); opacity:.3; } .ln-fr.m .ln-row { color:var(--magenta); }
  .ln-sharp { position:relative; } .ln-sharp .v { color:var(--cyan); }
  .ln-hl { position:absolute; inset:0; border-radius:60px; background: linear-gradient(180deg, rgba(255,255,255,.28), rgba(255,255,255,.04) 50%, rgba(255,255,255,.12)); pointer-events:none; }
  /* 25 morph: the growth card's bars turn into a line (points on the bar tops, stems, an area) */
  .gr-area { fill:rgba(10,240,240,.16); opacity:0; }
  .gr-pt { fill:#0b0d16; stroke:#fff; stroke-width:4; opacity:0; }
  .gr-badge { position:absolute; padding:6px 14px; border-radius:10px; background:#fff; color:#04161a; font-weight:700; font-size:24px; white-space:nowrap; opacity:0; translate:-88% -100%; }
  /* 33. search → results: the query types in (the one allowed typing sound), results drop in one by one */
  .sr { position:absolute; left:360px; top:180px; width:1200px; }
  .sr-bar { position:relative; height:120px; border-radius:60px; display:flex; align-items:center; gap:26px; padding:0 46px; }
  .sr-bar svg { width:50px; height:50px; flex:none; }
  .sr-bar .ic { fill:none; stroke:#fff; stroke-width:5; stroke-linecap:round; }
  .sr-ph { position:absolute; left:122px; font-weight:700; font-size:52px; color:rgba(255,255,255,.45); white-space:nowrap; }
  .sr-q { font-weight:700; font-size:52px; color:#fff; white-space:nowrap; }
  .sr-caret { width:4px; height:58px; background:var(--cyan); margin-left:-18px; opacity:0; }
  .sr-res { position:relative; margin-top:26px; }
  .sr-row { position:relative; height:132px; margin-bottom:18px; border-radius:26px; }
  .sr-row .inner { position:absolute; inset:0; display:flex; align-items:center; gap:30px; padding:0 34px; opacity:0; }
  .sr-sq { width:80px; height:80px; border-radius:20px; flex:none; display:flex; align-items:center; justify-content:center; }
  .sr-sq img { width:62%; height:62%; object-fit:contain; }
  .sr-t { font-weight:700; font-size:44px; line-height:1.05; color:#fff; white-space:nowrap; }
  .sr-s { font-weight:700; font-size:28px; line-height:1.2; color:rgba(255,255,255,.72); margin-top:6px; white-space:nowrap; }
  /* 34. magnetic dock: the tools as a dock, the cursor walks along, the icon under it swells and gets its name */
  .dk-bar { position:absolute; left:50%; top:560px; height:150px; border-radius:42px; translate:-50% 0; }
  .dk-ic { position:absolute; left:0; top:578px; width:114px; height:114px; margin-left:-57px; border-radius:28px; background:#fff; opacity:0;
    display:flex; align-items:center; justify-content:center; transform-origin:50% 100%; box-shadow: 0 12px 34px rgba(0,0,0,.45); }
  .dk-ic img { width:64px; height:64px; display:block; }
  .dk-svg { position:absolute; left:0; top:0; width:1920px; height:1080px; overflow:visible; }
  .dk-svg path { fill:none; stroke:var(--cyan); stroke-width:2.5; stroke-dasharray:3 9; stroke-linecap:round; opacity:0; }
  .dk-svg circle { fill:#fff; opacity:0; }
  .dk-tip { position:absolute; left:0; top:0; padding:14px 26px; border-radius:18px; font-weight:700; font-size:36px; line-height:1; color:#04161a; background:#fff;
    white-space:nowrap; opacity:0; translate:-50% -100%; box-shadow: 0 10px 30px rgba(0,0,0,.4); }
  /* 35. masked title: a full-frame chapter card; the word rises letter by letter through a cyan line */
  .mt { position:absolute; left:0; right:0; top:230px; text-align:center; }
  .mt-eye { font-weight:700; font-size:30px; letter-spacing:.24em; color:rgba(255,255,255,.72); opacity:0; }
  .mt-svg { display:block; width:1920px; height:330px; overflow:visible; }
  .mt-t { font-family:inherit; font-weight:700; letter-spacing:-4px; }
  .mt-o { fill:none; stroke:rgba(255,255,255,.55); stroke-width:2.5; }
  .mt-edge { stroke:var(--cyan); stroke-width:5; stroke-linecap:round; }
  .mt-hd { fill:var(--cyan); }
  .mt-subm { overflow:hidden; height:90px; margin-top:6px; }
  .mt-sub { font-weight:700; font-size:64px; line-height:90px; color:rgba(255,255,255,.92); }
  .mt-sub .em { color:var(--cyan); }
  .mt-rule2 { width:900px; height:2px; margin:10px auto 0; background:rgba(255,255,255,.22); }
  /* 36. button → player: a "watch" pill grows into a small player of the video named on camera */
  .pv { width:300px; height:92px; border-radius:46px; overflow:hidden; }
  .pv .pill { position:absolute; left:0; top:0; height:92px; display:flex; align-items:center; gap:16px; padding:0 34px; font-weight:700; font-size:36px; color:#fff; white-space:nowrap; opacity:0; }
  .pv .tri, .pv .ptri { width:0; height:0; border-style:solid; border-color:transparent transparent transparent #fff; }
  .pv .tri { border-width:12px 0 12px 20px; }
  .pv .card { position:absolute; left:24px; top:24px; width:552px; opacity:0; }
  .pv .thumb { position:relative; width:552px; height:310px; border-radius:16px; overflow:hidden; background:#111; }
  .pv .thumb img { width:100%; height:100%; object-fit:cover; display:block; }
  .pv .pbtn { position:absolute; left:50%; top:50%; width:92px; height:92px; margin:-46px 0 0 -46px; border-radius:50%; background:rgba(0,0,0,.55);
    display:flex; align-items:center; justify-content:center; }
  .pv .ptri { border-width:18px 0 18px 30px; margin-left:8px; }
  .pv .meta { display:flex; justify-content:space-between; align-items:baseline; margin-top:16px; gap:20px; }
  .pv .ttl { font-weight:700; font-size:30px; color:#fff; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  .pv .tm { font-weight:700; font-size:24px; color:rgba(255,255,255,.75); white-space:nowrap; font-variant-numeric:tabular-nums; }
  .pv .track { position:relative; margin-top:14px; height:8px; border-radius:4px; background:rgba(255,255,255,.25); }
  .pv .fillx { position:absolute; left:0; top:0; bottom:0; width:100%; border-radius:4px; background:var(--cyan); transform-origin:0 50%; }
  .pv-fly { position:absolute; top:133px; width:92px; height:92px; display:flex; align-items:center; justify-content:center; opacity:0; z-index:2; }
  .pv-fly .disc { position:absolute; inset:0; border-radius:50%; background:rgba(0,0,0,.55); }
  .pv-fly .ptri { position:relative; }
  .pv-fly .pz { position:absolute; display:flex; gap:10px; opacity:0; }
  .pv-fly .pz i { display:block; width:11px; height:34px; border-radius:3px; background:#fff; }
  .pv .knob { position:absolute; left:0; top:50%; width:24px; height:24px; margin:-12px 0 0 -12px; border-radius:50%; background:#fff; box-shadow: 0 2px 8px rgba(0,0,0,.5); }
  /* 37. image reveal: an image behind vertical slats that open left to right, then a slow push */
  .im-frame { position:absolute; left:210px; top:118px; width:1500px; height:844px; border-radius:24px; overflow:hidden; background:#0b0d16;
    box-shadow: 0 50px 120px rgba(0,0,0,.6), 0 0 0 2px rgba(255,255,255,.14); }
  .im-frame.lab { left:320px; top:92px; width:1280px; height:720px; }   /* room for the caption under it */
  .im-frame.full { left:0; top:0; width:1920px; height:1080px; border-radius:0; box-shadow:none; }
  .im-frame img { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; transform-origin:50% 50%; }
  .im-slat { position:absolute; top:0; bottom:0; transform-origin:50% 50%; background: linear-gradient(90deg, #0b0d16, #1a1e2b); box-shadow: inset -2px 0 0 rgba(255,255,255,.07); }
  /* 38. exploded layers: one flat card tilts into depth and separates into its named layers */
  .ly-stage { position:absolute; inset:0; perspective:2400px; perspective-origin:50% 42%; }
  .ly-rig { position:absolute; left:45%; top:54%; width:0; height:0; transform-style:preserve-3d; will-change:transform; }
  .ly-w { position:absolute; left:0; top:0; transform-style:preserve-3d; will-change:transform; }
  .ly-card { position:absolute; left:-440px; top:-280px; width:880px; height:560px; border-radius:26px; overflow:hidden; box-shadow: 0 40px 100px rgba(0,0,0,.5), 0 0 0 2px rgba(255,255,255,.18); }
  .ly-card img { width:100%; height:100%; object-fit:cover; object-position:50% 0%; display:block; }
  .ly-card .blk { position:absolute; border-radius:10px; }
  .ly-lab { position:absolute; left:474px; font-weight:700; font-size:44px; line-height:1; color:#fff; white-space:nowrap; opacity:0;
    text-shadow: 0 2px 10px rgba(0,0,0,.8); }
  .ly-lab .d { display:inline-block; width:18px; height:18px; border-radius:50%; background:var(--cyan); margin-right:14px; box-shadow: 0 0 14px rgba(10,240,240,.8); }
  /* ---- approved formats (world, deck, pills, chat, doc, clip), rebuilt in the house look ---- */
  .icn { overflow:visible; flex:none; }
  .icn .ic { fill:none; stroke:#fff; stroke-width:4.5; stroke-linecap:round; stroke-linejoin:round; }
  /* 39. world: one canvas on the wash; nodes arrive on their words, links draw, a camera pushes in and pulls back over it */
  .wd-cam { position:absolute; left:0; top:0; width:1920px; height:1080px; transform-origin:0 0; }
  .wd-grid { position:absolute; left:-1920px; top:-1080px; width:5760px; height:3240px; opacity:.28; background-image:
      linear-gradient(rgba(255,255,255,.09) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.09) 1px, transparent 1px);
      background-size:96px 96px; background-position:0 0; }
  .wd-svg { position:absolute; left:0; top:0; width:1920px; height:1080px; overflow:visible; }
  .wd-ring { fill:none; stroke:rgba(255,255,255,.14); stroke-width:2; }
  .wd-link { fill:none; stroke:rgba(255,255,255,.55); stroke-width:4; stroke-linecap:round; }
  .wd-link.dash { stroke-dasharray:3 13; opacity:0; }
  .wd-dot { position:absolute; left:0; top:0; width:20px; height:20px; margin:-10px 0 0 -10px; border-radius:50%; background:#fff; opacity:0;
    box-shadow: 0 0 18px rgba(10,240,240,1), 0 0 40px rgba(10,240,240,.7); }
  .wd-n { position:absolute; translate:-50% -50%; }
  .wd-n .inner { opacity:0; }
  .wd-card { width:300px; height:300px; border-radius:30px; }
  .wd-card .inner, .wd-orb .inner { position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:14px; padding:0 20px; }
  .wd-card .icn { width:92px; height:92px; } .wd-orb .icn { width:78px; height:78px; }
  .wd-lab { font-weight:700; font-size:42px; line-height:1.05; color:#fff; text-align:center; }
  .wd-sub { font-weight:700; font-size:26px; line-height:1.15; color:rgba(255,255,255,.75); text-align:center; }
  .wd-no { position:absolute; left:22px; top:18px; font-weight:700; font-size:26px; color:rgba(255,255,255,.6); }
  .wd-pill { height:92px; padding:0 36px; border-radius:46px; white-space:nowrap; display:flex; align-items:center; }
  .wd-pill .inner { display:flex; align-items:center; gap:16px; }
  .wd-pill .icn { width:44px; height:44px; }
  .wd-pill .wd-lab { font-size:40px; line-height:1; }
  .wd-orb { width:260px; height:260px; border-radius:50%; }
  .wd-orb .wd-lab { font-size:32px; }
  .wd-hex { width:200px; opacity:0; }
  .wd-hex .hx { display:block; width:200px; height:200px; overflow:visible; }
  .wd-hex .hx polygon { fill:rgba(255,255,255,.10); stroke:rgba(255,255,255,.72); stroke-width:3.5; }
  .wd-hex .icn { position:absolute; left:58px; top:58px; width:84px; height:84px; }
  .wd-hex .wd-lab { position:absolute; left:50%; top:214px; translate:-50% 0; font-size:34px; white-space:nowrap; }
  .wd-stat { width:600px; padding:32px 40px 38px; border-radius:26px; }
  .wd-stat .top { display:flex; align-items:center; gap:14px; }
  .wd-stat .top .icn { width:40px; height:40px; }
  .wd-stat .top .wd-lab { font-size:32px; text-align:left; }
  .wd-stat .v { margin-top:12px; font-weight:700; font-size:118px; line-height:1; color:#fff; letter-spacing:-.02em; white-space:nowrap; font-variant-numeric:tabular-nums; }
  .wd-stat .track { position:relative; margin-top:22px; height:14px; border-radius:7px; background:rgba(255,255,255,.18); }
  .wd-stat .fill { position:absolute; left:0; top:0; bottom:0; width:100%; border-radius:7px; background:var(--cyan); transform-origin:0 50%; transform:scaleX(0);
    box-shadow: 0 0 18px rgba(10,240,240,.6); }
  .wd-text { font-weight:700; color:#fff; white-space:nowrap; line-height:1; letter-spacing:-.02em; opacity:0; text-shadow: 0 4px 30px rgba(0,0,0,.5); }
  .wd-img { border-radius:22px; overflow:hidden; opacity:0; box-shadow: 0 40px 100px rgba(0,0,0,.55), 0 0 0 2px rgba(255,255,255,.16); }
  .wd-img img { width:100%; height:100%; object-fit:cover; display:block; }
  .wd-alert { position:absolute; width:58px; height:58px; margin:-29px 0 0 -29px; border-radius:50%; background:var(--amber); color:#1a1200; font-weight:700;
    font-size:38px; line-height:58px; text-align:center; opacity:0; box-shadow: 0 0 0 6px rgba(255,185,4,.22), 0 10px 26px rgba(0,0,0,.45); }
  .wd-win { position:absolute; border-radius:24px; overflow:hidden; opacity:0; background:rgba(12,14,21,.9);
    box-shadow: 0 60px 140px rgba(0,0,0,.6), 0 0 0 2px rgba(255,255,255,.14); }
  .wd-win .bar { height:56px; display:flex; align-items:center; gap:10px; padding:0 22px; border-bottom:1px solid rgba(255,255,255,.08); }
  .wd-win .dot { width:14px; height:14px; border-radius:50%; } .wd-win .r { background:#ff5f57; } .wd-win .y { background:#febc2e; } .wd-win .g { background:#28c840; }
  .wd-win .wt { margin-left:16px; font-size:22px; font-weight:500; color:rgba(255,255,255,.6); }
  .wd-dock { position:absolute; height:112px; padding:0 22px; border-radius:30px; display:flex; align-items:center; gap:18px; translate:-50% 0; opacity:0;
    background:rgba(255,255,255,.14); box-shadow: 0 0 0 2px rgba(255,255,255,.22), 0 24px 60px rgba(0,0,0,.45); }
  .wd-dock .tile { width:76px; height:76px; border-radius:20px; background:#fff; display:flex; align-items:center; justify-content:center; }
  .wd-dock .tile img { width:48px; height:48px; display:block; }
  /* 40. deck: the video's numbered parts as tall glass cards; the camera settles on the live one, the rest recede */
  .dq-cam { position:absolute; left:0; top:0; width:1920px; height:1080px; transform-origin:0 0; }
  .dq-card { position:absolute; top:280px; width:380px; height:520px; border-radius:30px; }
  .dq-card .inner { position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:30px; padding:0 26px; opacity:0; }
  .dq-card .icn { width:112px; height:112px; }
  .dq-card .no { position:absolute; left:28px; top:22px; font-weight:700; font-size:40px; font-style:italic; color:rgba(255,255,255,.6); }
  .dq-card .ttl { font-weight:700; font-size:40px; line-height:1.12; color:#fff; text-align:center; }
  .dq-head { position:absolute; left:0; right:0; top:120px; text-align:center; font-weight:700; font-size:40px; letter-spacing:.2em; color:rgba(255,255,255,.72); opacity:0; }
  /* 41. pills: short labels that arrive one by one around the speaker (a column each side, or one row at the bottom) */
  .pls-col { position:absolute; top:290px; display:flex; flex-direction:column; gap:26px; }
  .pls-col.l { left:70px; align-items:flex-start; } .pls-col.r { right:70px; align-items:flex-end; }
  .pls-row { position:absolute; left:0; right:0; bottom:70px; display:flex; justify-content:center; gap:26px; }
  .pls { position:relative; height:88px; padding:0 34px; border-radius:44px; white-space:nowrap; display:flex; align-items:center; }
  .pls .inner { display:flex; align-items:center; gap:16px; opacity:0; }
  .pls .icn { width:42px; height:42px; }
  .pls .t { font-weight:700; font-size:42px; line-height:1; color:#fff; text-shadow: 0 2px 8px rgba(0,0,0,.85), 0 8px 30px rgba(0,0,0,.5); }
  .pls.cyan .t { color:var(--cyan); } .pls.cyan .ic { stroke:var(--cyan); }
  .pls.amber .t { color:var(--amber); } .pls.amber .ic { stroke:var(--amber); }
  .pls .x { position:absolute; right:-12px; top:-12px; width:40px; height:40px; border-radius:50%; background:var(--amber); color:#1a1200; font-weight:700;
    font-size:30px; line-height:40px; text-align:center; opacity:0; box-shadow: 0 6px 16px rgba(0,0,0,.45); }
  /* 42. chat: messages arrive one by one (beside the speaker, in an app window, or on a phone); cyan = me, white = them */
  .ch-float { position:absolute; top:96px; width:640px; display:flex; flex-direction:column; gap:16px; }
  .ch-b { max-width:620px; padding:20px 30px; border-radius:30px; font-weight:700; font-size:36px; line-height:1.2; opacity:0; }
  .ch-b.me { align-self:flex-end; background:var(--cyan); color:#04161a; border-bottom-right-radius:10px; box-shadow: 0 14px 40px rgba(0,0,0,.35); }
  .ch-b.them { align-self:flex-start; background:rgba(255,255,255,.92); color:#10131a; border-bottom-left-radius:10px; box-shadow: 0 14px 40px rgba(0,0,0,.35); }
  .ch-float.l .ch-b { align-self:flex-start; } .ch-float.r .ch-b { align-self:flex-end; }
  .ch-win { position:absolute; left:460px; top:50%; translate:0 -50%; width:1000px; height:840px; border-radius:28px; overflow:hidden; background:rgba(12,14,21,.92);
    box-shadow: 0 60px 140px rgba(0,0,0,.6), 0 0 0 2px rgba(255,255,255,.14), 0 0 120px 10px rgba(10,240,240,.10); opacity:0; }
  .ch-win .bar { height:84px; display:flex; align-items:center; gap:18px; padding:0 30px; border-bottom:1px solid rgba(255,255,255,.08); }
  .ch-win .av { width:48px; height:48px; border-radius:50%; background:rgba(255,255,255,.18); display:flex; align-items:center; justify-content:center; }
  .ch-win .av .icn { width:30px; height:30px; }
  .ch-win .nm { font-weight:700; font-size:32px; color:#fff; }
  .ch-view { position:absolute; left:0; right:0; top:84px; bottom:0; overflow:hidden; }
  .ch-list { position:absolute; left:40px; right:40px; top:34px; display:flex; flex-direction:column; gap:18px; }
  .ch-win.phone { left:710px; width:500px; height:940px; border-radius:64px; border:10px solid #1b1e27; }
  .ch-win.phone .bar { height:120px; padding-top:40px; }
  .ch-win.phone .ch-view { top:120px; }
  .ch-win.phone .ch-list { left:24px; right:24px; }
  .ch-win.phone .ch-b { font-size:30px; max-width:380px; padding:16px 24px; }
  /* 18b. doc: a page rebuilt in HTML; the camera glides passage to passage, each one stroked amber in one pass, the rest out of focus */
  .dc-doc { position:absolute; inset:0; background:#f6f5f1; overflow:hidden; }
  .dc-doc.dark { background:#101218; }
  .dc-chrome { position:absolute; left:0; right:0; top:0; height:62px; background:#1d1d1f; display:flex; align-items:center; padding:0 22px; gap:10px; z-index:3; }
  .dc-chrome .dot { width:14px; height:14px; border-radius:50%; } .dc-chrome .r { background:#ff5f57; } .dc-chrome .y { background:#febc2e; } .dc-chrome .g { background:#28c840; }
  .dc-chrome .url { margin-left:18px; padding:8px 20px; border-radius:999px; background:#2c2c2e; color:#e5e5e7; font-size:21px; font-weight:500; line-height:1; }
  .dc-wrap { position:absolute; left:0; right:0; top:62px; bottom:0; overflow:hidden; }
  .dc-pg { position:absolute; left:0; top:0; width:1920px; transform-origin:0 0; }
  .dc-col { position:absolute; left:370px; top:0; width:1180px; padding-top:90px; }
  .dc-col.sharp { z-index:1; }
  .dc-col.soft { filter: blur(3px); opacity:.5; }   /* the out-of-focus copy under the sharp one: a static blur, it never animates */
  .dc-kick { font-weight:700; font-size:24px; letter-spacing:.14em; text-transform:uppercase; color:#8a8a8a; margin-bottom:22px; }
  .dc-ttl { font-weight:700; font-size:66px; line-height:1.08; letter-spacing:-.02em; color:#141414; margin-bottom:22px; }
  .dc-date { font-weight:500; font-size:26px; color:#8a8a8a; margin-bottom:46px; }
  .dc-p { font-weight:400; font-size:38px; line-height:1.55; color:#26262a; margin-bottom:34px; }
  .dc-doc.dark .dc-ttl { color:#f2f2f4; } .dc-doc.dark .dc-p { color:#d6d7dc; } .dc-doc.dark .dc-kick, .dc-doc.dark .dc-date { color:#8b8e99; }
  .dc-w { position:relative; z-index:0; }
  .dc-w i { position:absolute; left:-3px; right:-3px; top:.12em; bottom:.04em; z-index:-1; background:rgba(255,185,4,.66); transform:scaleX(0); transform-origin:0 50%; }
  .dc-doc.dark .dc-w i { top:auto; bottom:-.02em; height:.16em; background:var(--amber); }
  /* 20c. clip: a full-frame video cutaway (a screen recording, archive footage, or an AI b-roll shot), with an optional caption or glass checklist */
  .cutaway-video { position:absolute; left:0; top:0; width:1920px; height:1080px; object-fit:cover; z-index:20; }
  .clip-over { z-index:21 !important; }
  .cl-list { position:absolute; left:70px; top:96px; padding:26px 32px 8px; }
  .cl-list .inner { opacity:0; }
  .cl-list .item { display:none; align-items:center; gap:20px; margin-bottom:20px; }
  .cl-list .item .t { font-weight:700; font-size:48px; line-height:1.05; color:#fff; white-space:nowrap; text-shadow: 0 2px 8px rgba(0,0,0,.85); }
""".replace("ORIGIN", origin)

def attr_anchor(anchor):
    """'-' marks a beat that is deliberately not tied to a spoken word (beat-check skips it)."""
    if anchor == "-":
        return ' data-unanchored="1"'
    return ' data-anchor="%s"' % anchor.replace('"', "&quot;") if anchor else ""

def host(bid, t_in, t_out, track, inner, anchor=""):
    a = attr_anchor(anchor)
    return ('    <div class="card-host clip" id="host-%s" data-card-id="%s" data-start="%.3f" data-duration="%.3f" data-track-index="%d"%s\n'
            '      style="left:0;top:0;width:1920px;height:1080px;visibility:hidden;opacity:1;">\n      <div class="card">%s</div>\n    </div>\n'
            % (bid, bid, t_in, t_out - t_in, track, a, inner))

def words_html(text):   # words kept in data-text; spans are built at load (seek-safe)
    return text


def item_attrs(it):
    """List/bullet items carry their own entry time and spoken anchor so beat-check.py can prove each one.
    it = [text, t] (the anchor is the text) or [text, t, "anchor phrase"] ("-" = not spoken)."""
    anchor = it[2] if len(it) > 2 else it[0]
    return ' data-at="%.3f"%s' % (float(it[1]), attr_anchor(anchor))

CHECK_SVG = ('<div class="mk"><svg viewBox="0 0 44 44"><circle class="ring" cx="22" cy="22" r="19"/>'
             '<path class="tick" d="M13 22.5 L19.5 29 L31 16" style="stroke-dasharray:30;stroke-dashoffset:30"/></svg></div>')

def check_in(sel, t):
    """The check marker: the ring fills cyan and the tick draws, a beat after the item lands."""
    js("tl.to('%s .ring', { fill: 'rgba(10,240,240,1)', stroke: 'rgba(10,240,240,1)', duration: 0.26, ease: 'power2.out' }, %.3f);" % (sel, t + 0.22))
    js("tl.to('%s .tick', { strokeDashoffset: 0, duration: 0.30, ease: 'power2.out' }, %.3f);" % (sel, t + 0.32))

# line icons for pipeline steps, 64x64, drawn in white strokes (no icon assets, no fills)
ICONS = {
    "doc": "M16 6h24l10 10v42H16z M40 6v10h10 M23 30h20 M23 39h20 M23 48h13",
    "browser": "M6 12h52v40H6z M6 22h52 M12 17h1 M18 17h1 M24 17h1",
    "bolt": "M36 4 14 36h16l-4 24 22-32H32z",
    "chat": "M8 12h48v30H26l-12 10V42H8z",
    "money": "M32 6a26 26 0 1 0 .01 0z M40 23c-2-3-5-4-8-4-5 0-8 2-8 6 0 8 16 5 16 13 0 4-3 6-8 6-4 0-7-1-9-4 M32 13v6 M32 43v7",
    "check": "M32 6a26 26 0 1 0 .01 0z M20 33l8 8 16-17",
    "user": "M32 8a11 11 0 1 0 .01 0z M12 56c2-12 10-18 20-18s18 6 20 18",
    "code": "M22 18 8 32l14 14 M42 18l14 14-14 14 M36 12 28 52",
    "video": "M6 12h52v40H6z M27 23v18l15-9z",
    "mail": "M6 14h52v36H6z M6 16l26 20 26-20",
    "gear": "M32 22a10 10 0 1 0 .01 0z M32 4v8 M32 52v8 M4 32h8 M52 32h8 M12 12l6 6 M46 46l6 6 M52 12l-6 6 M18 46l-6 6",
    "chart": "M8 56h48 M16 48V34 M28 48V22 M40 48V28 M52 48V10",
    "search": "M27 8a19 19 0 1 0 .01 0z M41 41l15 15",
    # for the world / deck / pills scenes (security, agents, systems)
    "shield": "M32 6 52 13v17c0 13-9 22-20 28C21 52 12 43 12 30V13z",
    "lock": "M18 28h28v26H18z M24 28v-8a8 8 0 0 1 16 0v8 M32 38v8",
    "robot": "M16 22h32v26H16z M32 22v-8 M32 8a3 3 0 1 0 .01 0z M25 33h1 M38 33h1 M26 41h12 M10 30v10 M54 30v10",
    "globe": "M32 6a26 26 0 1 0 .01 0z M6 32h52 M32 6c-9 8-9 44 0 52 M32 6c9 8 9 44 0 52",
    "cloud": "M20 46h26a10 10 0 0 0 0-20 14 14 0 0 0-27-3A11 11 0 0 0 20 46z",
    "key": "M22 16a10 10 0 1 0 .01 0z M29 33l25 25 M46 50l6-6 M52 56l5-5",
    "alert": "M32 8 58 54H6z M32 26v14 M32 47v1",
    "folder": "M6 16h20l6 6h26v32H6z",
    "eye": "M4 32c8-12 17-18 28-18s20 6 28 18c-8 12-17 18-28 18S12 44 4 32z M32 24a8 8 0 1 0 .01 0z",
    "bank": "M8 26 32 10l24 16z M12 30v18 M24 30v18 M40 30v18 M52 30v18 M6 54h52",
    "chip": "M18 18h28v28H18z M26 26h12v12H26z M24 10v8 M32 10v8 M40 10v8 M24 46v8 M32 46v8 M40 46v8 M10 24h8 M10 32h8 M10 40h8 M46 24h8 M46 32h8 M46 40h8",
}

def icon_svg(name, size=None):
    """A line icon from ICONS as an inline SVG (white stroke; .lit turns it cyan)."""
    if not name:
        return ""
    if name not in ICONS:
        raise SystemExit("unknown icon %r (one of: %s)" % (name, " ".join(sorted(ICONS))))
    st = ' style="width:%dpx;height:%dpx"' % (size, size) if size else ""
    return '<svg class="icn" viewBox="0 0 64 64"%s><path class="ic" d="%s"/></svg>' % (st, ICONS[name])

def em_spans(text, em):
    ws = text.split(" ")
    return " ".join('<span class="em">%s</span>' % w if i in set(em or []) else w for i, w in enumerate(ws))

def image_size(path):
    """(width, height) of a PNG or JPEG without extra libraries."""
    with open(path, "rb") as f:
        head = f.read(26)
        if head[:8] == b"\x89PNG\r\n\x1a\n":
            return struct.unpack(">II", head[16:24])
        if head[:2] == b"\xff\xd8":
            f.seek(2)
            while True:
                m = f.read(4)
                if len(m) < 4 or m[0] != 0xFF:
                    break
                if m[1] in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                    h, w = struct.unpack(">HH", f.read(5)[1:5])
                    return w, h
                f.seek(struct.unpack(">H", m[2:4])[0] - 2, 1)
    raise SystemExit('give "size": [w, h] for %s' % path)

def smooth_path(pts):
    """Catmull-Rom through the points as cubic Beziers (the curve the chart morph draws)."""
    d = "M%.1f %.1f" % pts[0]
    for i in range(len(pts) - 1):
        p0, p1, p2 = pts[i - 1] if i else pts[i], pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        d += " C%.1f %.1f %.1f %.1f %.1f %.1f" % (c1 + c2 + p2)
    return d

def fmt_value(v, prefix="", suffix="", decimals=0):
    return "%s%s%s" % (prefix, ("{:,.%df}" % int(decimals)).format(v), suffix)

CURSOR_SVG = ('<svg class="cursor" id="%s" viewBox="0 0 24 24" style="left:0;top:0"><path d="M5.2 2.6 L5.2 20.8 L9.9 16.6 L13 23 L16.3 21.4 L13.2 15.3 L19.4 15.3 Z" '
              'fill="#1c1c1c" stroke="#ffffff" stroke-width="1.4" stroke-linejoin="round"/></svg>')

def transition(b, t_in, t_out):
    """Dress the cut into and out of a full-frame cutaway. zoomthrough: the footage pushes in and blurs for 0.22 s
    before the cut, and settles back from 1.08/6px on the return. punch: the 2-frame scale pop on the return only."""
    tr = b.get("transition", "none")
    if tr == "zoomthrough":
        js("tl.to('#video-wrap', { scale: 1.12, filter: 'blur(8px)', duration: 0.22, ease: 'power2.in' }, %.3f);" % (t_in - 0.22))
        js("tl.set('#video-wrap', { scale: 1.0, filter: 'blur(0px)' }, %.3f);" % (t_in + 0.02))
        js("tl.fromTo('#video-wrap', { scale: 1.08, filter: 'blur(6px)' }, { scale: 1.0, filter: 'blur(0px)', duration: 0.32, ease: 'power2.out', immediateRender: false }, %.3f);" % t_out)
    elif tr == "punch":
        js("tl.fromTo('#video-wrap', { scale: 1.04 }, { scale: 1.0, duration: 0.12, ease: 'power2.out', immediateRender: false }, %.3f);" % t_out)

def scene_label(bid, b, t_out):
    """Optional caption on a scene: same voice as a lower line, 88 px, rises in on its own word."""
    if not b.get("label"):
        return ""
    em = set(b.get("label_em", []))
    ws = b["label"].split(" ")
    spans = " ".join('<span class="em">%s</span>' % w if i in em else w for i, w in enumerate(ws))
    t = float(b.get("label_at", b["in"]))
    js("tl.fromTo('#%s-label', { opacity: 0, y: 26 }, { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }, %.3f);" % (bid, t))
    js("tl.to('#%s-label', { opacity: 0, duration: 0.3, ease: 'power2.in' }, %.3f);" % (bid, t_out - 0.34))
    return '<div class="slabel%s" id="%s-label">%s</div>' % (" amber" if b.get("label_color") == "amber" else "", bid, spans)

html_parts, js_parts, audio_parts = [], [], []
track = 3
audio_track = 20

def js(s): js_parts.append(s)

# ---- tag(s) ---------------------------------------------------------------------------------------------
# "tag" (one) or "tags" (a list: the chapter fixture returns at every section boundary on a long-form video)
for ti, tag in enumerate(S.get("tags") or ([S["tag"]] if S.get("tag") else [])):
    tid = "tag" if ti == 0 else "tag%d" % ti
    pips = "".join('<span class="pip%s"></span>' % (" now" if i + 1 == tag["n"] else (" done" if i + 1 < tag["n"] else "")) for i in range(tag["of"]))
    pos = POS.get(tag.get("pos", "tr"), POS["tr"])
    inner = ('<div class="glass tag" id="%s-glass" style="%s"><div class="inner" id="%s-inner"><div class="pips">%s</div><div class="label">%s</div></div></div>'
             % (tid, pos, tid, pips, tag["label"]))
    html_parts.append(host(tid, tag["in"], tag["out"], track, inner, tag.get("anchor", "")))
    track += 1
    js("glassIn('#%s-glass', %.3f, { y: -22 });" % (tid, tag["in"]))
    js("tl.fromTo('#%s-inner', { opacity: 0 }, { opacity: 1, duration: 0.36 }, %.3f);" % (tid, tag["in"] + 0.04))
    js("tl.fromTo('#%s-glass .pip.now', { scale: 0 }, { scale: 1, duration: 0.42, ease: 'power2.out' }, %.3f);" % (tid, tag["in"] + 0.30))
    js("tl.fromTo('#%s-glass .pip.done', { scale: 0.4, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: 'power2.out', stagger: 0.06 }, %.3f);" % (tid, tag["in"] + 0.10))
    js("tl.to('#%s-inner', { opacity: 0, duration: 0.28, ease: 'power2.in' }, %.3f);" % (tid, tag["out"] - 0.40))
    js("glassOut('#%s-glass', %.3f, 0.33);" % (tid, tag["out"] - 0.35))
    js("tl.set('#%s-inner', { opacity: 0 }, %.3f);" % (tid, tag["out"] - 0.12))   # hard kill exactly where the fade ends

# ---- beats ------------------------------------------------------------------------------------------
for b in S.get("beats", []):
    t, bid, t_in, t_out = b["type"], b["id"], float(b["in"]), float(b["out"])
    anchor = b.get("anchor", "")
    if t == "line":
        cls = "lower" + (" amber" if b.get("color") == "amber" else "") + (" shine" if b.get("shimmer") else "")
        em = ",".join(str(i) for i in b.get("em", []))
        inner = '<div class="%s" id="%s" data-text="%s" data-em="%s"></div>' % (cls, bid, b["text"].replace('"', "&quot;"), em)
        html_parts.append(host(bid, t_in, t_out, track, inner, anchor))
        js("lowerIn('%s', %.3f);" % (bid, t_in + 0.05))
        if b.get("shimmer"):    # 16. one cyan light band travels the line, twice, once the words have landed
            nwords = len(b["text"].split(" ")); t_sh = t_in + 0.05 + 0.4 + 0.055 * nwords + 0.35
            js("(function(){ var line = document.getElementById('%s'); var W = line.offsetWidth; var spans = line.querySelectorAll('.w');"
               " spans.forEach(function(sp){ sp.style.backgroundSize = (3*W) + 'px 100%%'; sp.style.backgroundPositionX = (-0.3*W - sp.offsetLeft) + 'px'; });   /* the pre-sweep state must equal the tween's first value or Chrome leaves the white words unpainted until the sweep starts */"
               " tl.fromTo(spans, { backgroundPositionX: function(i, sp){ return (-0.3*W - sp.offsetLeft) + 'px'; } },"
               " { backgroundPositionX: function(i, sp){ return (-1.7*W - sp.offsetLeft) + 'px'; }, duration: 1.3, ease: 'power1.inOut', repeat: 1, repeatDelay: 0.5, immediateRender: false }, %.3f); })();" % (bid, t_sh))
        js("lowerOut('host-%s', %.3f);" % (bid, t_out))
        js("tl.set('#host-%s .lower', { opacity: 0 }, %.3f);" % (bid, t_out - 0.01))
    elif t == "logo":
        pos = POS.get(b.get("pos", "tl"), POS["tl"])
        inner = '<div class="glass logo-plate" id="%s-glass" style="%s"><div class="inner" id="%s-inner"><img src="%s" alt="" /></div></div>' % (bid, pos, bid, b["src"])
        html_parts.append(host(bid, t_in, t_out, track, inner, anchor))
        js("glassIn('#%s-glass', %.3f, { x: %d });" % (bid, t_in, -40 if b.get("pos", "tl") == "tl" else 40))
        js("tl.fromTo('#%s-inner', { opacity: 0 }, { opacity: 1, duration: 0.36 }, %.3f);" % (bid, t_in + 0.04))
        js("tl.to('#%s-inner', { opacity: 0, duration: 0.28, ease: 'power2.in' }, %.3f);" % (bid, t_out - 0.38))
        js("glassOut('#%s-glass', %.3f, 0.33);" % (bid, t_out - 0.34))
        js("tl.set('#%s-inner', { opacity: 0 }, %.3f);" % (bid, t_out - 0.10))
        if b.get("pop") is not None:
            audio_parts.append('    <audio id="sfx-pop-%s" src="sfx/pop.mp3" data-start="%.3f" data-duration="0.72" data-track-index="%d" data-volume="0.34"></audio>\n' % (bid, float(b["pop"]), audio_track))
            audio_track += 1
    elif t == "list":
        pos = POS.get(b.get("pos", "tl"), POS["tl"])
        mark = CHECK_SVG if b.get("marker") == "check" else '<div class="d"></div>'
        items = "".join('<div class="item" id="%s-i%d"%s>%s<div class="t">%s</div></div>' % (bid, i, item_attrs(it), mark, it[0]) for i, it in enumerate(b["items"]))
        eyebrow = ('<div class="eyebrow"%s>%s</div>' % (' style="font-size:%dpx"' % int(b["eyebrow_size"]) if b.get("eyebrow_size") else "", b["eyebrow"])) if b.get("eyebrow") else ""
        extra = "width:%dpx;" % int(b["width"]) if b.get("width") else ""
        sz = ' style="font-size:%dpx"' % int(b["size"]) if b.get("size") else ""
        items = items.replace('<div class="t">', '<div class="t"%s>' % sz)
        inner = '<div class="glass list" id="%s-glass" style="%s%s"><div class="inner" id="%s-inner">%s%s</div></div>' % (bid, pos, extra, bid, eyebrow, items)
        html_parts.append(host(bid, t_in, t_out, track, inner, anchor))
        js("glassIn('#%s-glass', %.3f, { x: %d });" % (bid, t_in, -40 if b.get("pos", "tl") == "tl" else 40))
        js("tl.fromTo('#%s-inner', { opacity: 0 }, { opacity: 1, duration: 0.36 }, %.3f);" % (bid, t_in + 0.04))
        for i, it in enumerate(b["items"]):
            js("tl.set('#%s-i%d', { display: 'flex' }, %.3f);" % (bid, i, float(it[1])))
            js("tl.fromTo('#%s-i%d', { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: 0.40, ease: 'power2.out' }, %.3f);" % (bid, i, float(it[1])))
            if b.get("marker") == "check":
                check_in("#%s-i%d" % (bid, i), float(it[1]))
        js("tl.to('#%s-inner', { opacity: 0, duration: 0.30, ease: 'power2.in' }, %.3f);" % (bid, t_out - 0.40))
        js("glassOut('#%s-glass', %.3f, 0.35);" % (bid, t_out - 0.35))
        js("tl.set('#%s-inner', { opacity: 0 }, %.3f);" % (bid, t_out - 0.10))
    elif t == "bullets":
        mark = CHECK_SVG if b.get("marker") == "check" else '<div class="d"></div>'
        items = "".join('<div class="b" id="%s-b%d"%s>%s<div class="t">%s</div></div>' % (bid, i, item_attrs(it), mark, it[0]) for i, it in enumerate(b["items"]))
        inner = '<div class="scrim" id="%s-scrim"></div><div class="bullets" id="%s-bullets">%s</div>' % (bid, bid, items)
        html_parts.append(host(bid, t_in, t_out, track, inner, anchor))
        rel = float(b.get("release", t_out - 0.55))
        js("tl.to('#video-wrap', { scale: 1.18, x: 150, duration: 0.75, ease: 'power2.inOut' }, %.3f);" % t_in)
        js("tl.fromTo('#%s-scrim', { opacity: 0 }, { opacity: 1, duration: 0.45, ease: 'power2.out' }, %.3f);" % (bid, t_in + 0.10))
        for i, it in enumerate(b["items"]):
            js("tl.set('#%s-b%d', { display: 'flex' }, %.3f);" % (bid, i, float(it[1])))
            js("tl.fromTo('#%s-b%d', { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.40, ease: 'power2.out' }, %.3f);" % (bid, i, float(it[1])))
            if b.get("marker") == "check":
                check_in("#%s-b%d" % (bid, i), float(it[1]))
        js("tl.to('#%s-bullets .b', { opacity: 0, duration: 0.30, ease: 'power2.in' }, %.3f);" % (bid, rel - 0.05))
        js("tl.to('#%s-scrim', { opacity: 0, duration: 0.45, ease: 'power2.in' }, %.3f);" % (bid, rel))
        js("tl.to('#video-wrap', { scale: 1.00, x: 0, duration: 0.55, ease: 'power2.inOut' }, %.3f);" % rel)
        js("tl.set('#%s-bullets .b, #%s-scrim', { opacity: 0 }, %.3f);" % (bid, bid, t_out - 0.01))
    elif t == "chip":
        ws = b["text"].split(" "); em = set(b.get("em", []))
        spans = " ".join('<span class="em">%s</span>' % w if i in em else w for i, w in enumerate(ws))
        inner = '<div class="chip" id="%s-chip"><div class="inner" id="%s-inner">%s</div></div>' % (bid, bid, spans)
        html_parts.append(host(bid, t_in, t_out, track, inner, anchor))
        js("tl.fromTo('#%s-chip', { backgroundColor: 'rgba(17,17,17,0)', y: 18 }, { backgroundColor: 'rgba(17,17,17,0.45)', y: 0, duration: 0.40, ease: 'power2.out' }, %.3f);" % (bid, t_in))
        js("tl.fromTo('#%s-inner', { opacity: 0 }, { opacity: 1, duration: 0.32 }, %.3f);" % (bid, t_in + 0.06))
        js("tl.to('#%s-inner', { opacity: 0, duration: 0.26, ease: 'power2.in' }, %.3f);" % (bid, t_out - 0.36))
        js("tl.to('#%s-chip', { backgroundColor: 'rgba(17,17,17,0)', duration: 0.30, ease: 'power2.in' }, %.3f);" % (bid, t_out - 0.32))
        js("tl.set('#%s-inner', { opacity: 0 }, %.3f);" % (bid, t_out - 0.10))
    elif t == "vignette":
        inner = '<div class="vig" id="%s-vig"></div><div class="grain" id="%s-grain"></div>' % (bid, bid)
        html_parts.append(host(bid, t_in, t_out, track, inner, anchor))
        js("tl.fromTo('#%s-vig', { opacity: 0 }, { opacity: 1, duration: 0.45, ease: 'power2.out' }, %.3f);" % (bid, t_in))
        js("tl.fromTo('#%s-grain', { opacity: 0 }, { opacity: 0.35, duration: 0.45, ease: 'power2.out' }, %.3f);" % (bid, t_in))
        js("tl.to('#%s-vig, #%s-grain', { opacity: 0, duration: 0.35, ease: 'power2.in' }, %.3f);" % (bid, bid, t_out - 0.35))
        js("tl.set('#%s-vig, #%s-grain', { opacity: 0 }, %.3f);" % (bid, bid, t_out - 0.01))
    elif t == "pointer":
        lead, emt = b.get("text", "Everything is"), b.get("em_text", "linked in the description")   # e.g. "Grab the" + "free template below"
        inner = ('<div class="glass pointer" id="%s-glass"><div class="inner" id="%s-inner"><div class="txt">%s <span class="em">%s</span></div>'
                 '<div class="chev"><span></span><span></span><span></span></div></div></div>' % (bid, bid, lead, emt))
        html_parts.append(host(bid, t_in, t_out, track, inner, anchor))
        js("glassIn('#%s-glass', %.3f, { y: 24 });" % (bid, t_in))
        js("tl.fromTo('#%s-inner', { opacity: 0 }, { opacity: 1, duration: 0.36 }, %.3f);" % (bid, t_in + 0.04))
        cycles = max(1, int((t_out - t_in - 0.5) / 0.78))
        js("tl.fromTo('#%s-glass .chev span', { y: -14, opacity: 0 }, { y: 20, opacity: 1, duration: 0.5, ease: 'power1.in', stagger: 0.14, repeat: %d, repeatDelay: 0.06 }, %.3f);" % (bid, cycles - 1, t_in + 0.45))
        js("tl.to('#%s-inner', { opacity: 0, duration: 0.28, ease: 'power2.in' }, %.3f);" % (bid, t_out - 0.38))
        js("glassOut('#%s-glass', %.3f, 0.33);" % (bid, t_out - 0.34))
        js("tl.set('#%s-inner', { opacity: 0 }, %.3f);" % (bid, t_out - 0.10))

    elif t == "site":
        # 4b. full-screen site cutaway: real capture, bare domain in the pill, slow drift, optional scroll for a full-page capture
        inner = ('<div class="cut"><div class="site"><div class="chrome"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span>'
                 '<div class="url">%s</div></div><div class="pagewrap"><img class="page" id="%s-page" src="%s" alt="" /></div></div></div>' % (b["domain"], bid, b["src"]))
        html_parts.append(host(bid, t_in, t_out, track, inner, anchor))
        hold = t_out - t_in
        js("tl.fromTo('#%s-page', { scale: 1.0, y: 0 }, { scale: 1.06, y: %d, duration: %.3f, ease: '%s' }, %.3f);" % (bid, -int(b.get("scroll", 0)), hold, "power1.inOut" if b.get("scroll") else "none", t_in))
        transition(b, t_in, t_out)
    elif t == "grid":
        # the channel's own thumbnails in a 3x2 grid; the oversized cursor enters from below, walks to one, clicks, the tile reacts
        tiles = "".join('<div class="tile" id="%s-t%d"><img src="%s" alt="" /><div class="ring"></div></div>' % (bid, i, src) for i, src in enumerate(b["images"][:6]))
        inner = '<div class="cut"><div class="gridbg"></div><div class="tgrid">%s</div>%s%s</div>' % (tiles, CURSOR_SVG % (bid + "-cur"), "")
        html_parts.append(host(bid, t_in, t_out, track, inner, anchor))
        js("tl.fromTo('#host-%s .tile', { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.45, ease: 'power2.out', stagger: 0.06 }, %.3f);" % (bid, t_in))
        ci = int(b.get("click_index", 4)); ct = float(b.get("click_at", t_in + 1.4))
        col, row = ci % 3, ci // 3
        cx, cy = 92 + col * 588 + 280, 211 + row * 343 + 157      # tile centre
        lx, ly = cx - 0.21 * 134, cy - 0.14 * 134                # cursor box so the TIP lands on the centre
        js("tl.set('#%s-cur', { x: %.0f, y: 1150 }, 0);" % (bid, lx))
        js("tl.to('#%s-cur', { x: %.0f, y: %.0f, duration: 0.85, ease: 'power3.out' }, %.3f);" % (bid, lx, ly, max(t_in + 0.25, ct - 0.95)))
        js("tl.to('#%s-cur', { scale: 0.84, duration: 0.10, ease: 'power2.in' }, %.3f);" % (bid, ct))
        js("tl.to('#%s-cur', { scale: 1.0, duration: 0.22, ease: 'power2.out' }, %.3f);" % (bid, ct + 0.10))
        js("tl.to('#%s-t%d', { scale: 0.96, duration: 0.10, ease: 'power2.in' }, %.3f);" % (bid, ci, ct))
        js("tl.to('#%s-t%d', { scale: 1.08, duration: 0.45, ease: 'power2.out' }, %.3f);" % (bid, ci, ct + 0.10))
        js("tl.to('#%s-t%d .ring', { opacity: 1, duration: 0.18 }, %.3f);" % (bid, ci, ct + 0.05))
        others = ", ".join("#%s-t%d" % (bid, i) for i in range(len(b["images"][:6])) if i != ci)
        js("tl.to('%s', { opacity: 0.38, duration: 0.4, ease: 'power2.out' }, %.3f);" % (others, ct + 0.10))
        js("tl.to('#%s-t%d', { scale: 1.16, duration: %.3f, ease: 'power1.inOut' }, %.3f);" % (bid, ci, max(0.3, t_out - ct - 0.6), ct + 0.6))
        js("tl.to('#%s-cur', { x: %.0f, y: %.0f, duration: 0.6, ease: 'power2.out' }, %.3f);" % (bid, lx + 150, ly + 110, ct + 0.5))
        transition(b, t_in, t_out)
    elif t == "scene":
        kind = b["kind"]; steps = {k: float(v) for k, v in b.get("steps", {}).items()}
        label = ""
        if kind == "money":
            # amber $ chips drop in one by one on the word, no digits: money as stakes, never an invented figure
            n = int(b.get("count", 6)); chips = "".join('<div class="chip" id="%s-c%d" style="left:%dpx; top:380px;">$</div>' % (bid, i, 960 - (n * 150) // 2 + i * 150 + 13) for i in range(n))
            inner_scene = '<div class="scene">%s</div>' % chips
            t0 = steps.get("drop", t_in + 0.3)
            for i in range(n):
                js("tl.fromTo('#%s-c%d', { opacity: 0, y: -520, rotation: %d }, { opacity: 1, y: 0, rotation: 0, duration: 0.55, ease: 'power2.in' }, %.3f);" % (bid, i, (-14 if i % 2 else 12), t0 + i * 0.11))
                js("tl.to('#%s-c%d', { y: -28, duration: 0.16, ease: 'power2.out' }, %.3f);" % (bid, i, t0 + i * 0.11 + 0.55))
                js("tl.to('#%s-c%d', { y: 0, duration: 0.22, ease: 'power2.in' }, %.3f);" % (bid, i, t0 + i * 0.11 + 0.71))
        elif kind == "catalog":
            # six photo frames fill a catalog one by one, then one shine sweeps the set: "beautiful images"
            pos = [(160, 150), (760, 150), (1360, 150), (160, 560), (760, 560), (1360, 560)]
            glyph = ('<svg viewBox="0 0 400 260"><rect x="0" y="0" width="400" height="260" fill="rgba(255,255,255,.04)"/>'
                     '<circle cx="300" cy="80" r="30" fill="rgba(255,255,255,.55)"/><path d="M0 230 L120 120 L210 200 L270 160 L400 250 L400 260 L0 260 Z" fill="rgba(255,255,255,.35)"/></svg>')
            frames = "".join('<div class="frame" id="%s-f%d" style="left:%dpx; top:%dpx;">%s</div>' % (bid, i, x, y, glyph) for i, (x, y) in enumerate(pos))
            inner_scene = '<div class="scene">%s<div class="shine" id="%s-shine"></div></div>' % (frames, bid)
            t0 = steps.get("fill", t_in + 0.3); ts = steps.get("shine", t0 + 1.4)
            for i in range(6):
                js("tl.fromTo('#%s-f%d', { opacity: 0, y: 30, scale: 0.96 }, { opacity: 1, y: 0, scale: 1, duration: 0.42, ease: 'power2.out' }, %.3f);" % (bid, i, t0 + i * 0.13))
            js("tl.fromTo('#%s-shine', { xPercent: 0, opacity: 0 }, { xPercent: 620, opacity: 1, duration: 1.1, ease: 'power1.inOut' }, %.3f);" % (bid, ts))
            js("tl.to('#%s-shine', { opacity: 0, duration: 0.15 }, %.3f);" % (bid, ts + 1.0))
            js("tl.to('#host-%s .frame', { borderColor: 'rgba(10,240,240,.9)', duration: 0.5, ease: 'power2.out', stagger: 0.06 }, %.3f);" % (bid, ts + 0.2))
        elif kind == "room":
            # an empty room drawn in line art; furniture drops in on the words: staging, without a single stock photo
            room = ('<svg viewBox="0 0 1920 1080" style="left:0;top:-90px;width:1920px;height:1080px" fill="none" stroke="rgba(255,255,255,.7)" stroke-width="4" stroke-linejoin="round">'
                    '<path class="draw" d="M360 240 H1560 V760 H360 Z"/><path class="draw" d="M160 940 L360 760 M1760 940 L1560 760 M160 940 H1760"/>'
                    '<rect class="draw" x="1180" y="330" width="240" height="260" rx="6"/><path class="draw" d="M1300 330 V590 M1180 460 H1420"/>'
                    '<g id="%s-rug" opacity="0"><ellipse cx="960" cy="860" rx="330" ry="52" stroke="rgba(10,240,240,.9)"/></g>'
                    '<g id="%s-sofa" opacity="0" stroke="#fff" stroke-width="6"><rect x="640" y="640" width="640" height="150" rx="30"/><rect x="600" y="580" width="90" height="210" rx="30"/><rect x="1230" y="580" width="90" height="210" rx="30"/><path d="M700 640 V560 Q700 530 730 530 H1190 Q1220 530 1220 560 V640"/></g>'
                    '<g id="%s-lamp" opacity="0" stroke="#fff" stroke-width="6"><path d="M470 780 V470"/><path d="M400 470 L540 470 L515 360 L425 360 Z" fill="rgba(255,185,4,.35)" stroke="var(--amber)"/><path d="M420 780 H520"/></g>'
                    '<g id="%s-plant" opacity="0" stroke="#fff" stroke-width="6"><path d="M1400 790 H1520 L1500 690 H1420 Z"/><path d="M1460 690 V600 M1460 640 Q1400 600 1380 540 M1460 620 Q1520 580 1540 520 M1460 600 Q1450 540 1470 490" stroke="var(--cyan)"/></g>'
                    '<g id="%s-art" opacity="0" stroke="#fff" stroke-width="6"><rect x="620" y="330" width="300" height="200" rx="6"/><path d="M640 500 L720 410 L790 470 L840 430 L900 500"/></g>'
                    '</svg>') % (bid, bid, bid, bid, bid)
            inner_scene = '<div class="scene">%s<div class="shine" id="%s-shine"></div></div>' % (room, bid)
            js("(function(){ var ps = document.querySelectorAll('#host-%s .draw'); ps.forEach(function(p){ var L = p.getTotalLength(); p.style.strokeDasharray = L; p.style.strokeDashoffset = L; });"
               " tl.to(ps, { strokeDashoffset: 0, duration: 0.9, ease: 'power2.inOut', stagger: 0.12 }, %.3f); })();" % (bid, t_in + 0.05))
            order = [("rug", 0.0), ("sofa", 0.16), ("lamp", 0.32), ("plant", 0.46), ("art", 0.60)]
            t0 = steps.get("furnish", t_in + 0.4)
            for name, off in order:
                js("tl.fromTo('#%s-%s', { opacity: 0, y: -70 }, { opacity: 1, y: 0, duration: 0.5, ease: 'power2.out' }, %.3f);" % (bid, name, t0 + off))
            if "shine" in steps:
                js("tl.fromTo('#%s-shine', { xPercent: 0, opacity: 0 }, { xPercent: 620, opacity: 1, duration: 1.1, ease: 'power1.inOut' }, %.3f);" % (bid, steps["shine"]))
                js("tl.to('#%s-shine', { opacity: 0, duration: 0.15 }, %.3f);" % (bid, steps["shine"] + 1.0))
        elif kind == "plate":
            # a phone with a casual plate on screen; on the word the picture jumps out as the hero and gets the sweep, sparkles and steam
            def plate_svg(pid, style):
                return ('<svg viewBox="0 0 400 400" style="%s"><circle cx="200" cy="200" r="170" fill="#f2efe8"/><circle cx="200" cy="200" r="130" fill="#e6e1d6"/>'
                        '<g id="%s-food"><ellipse cx="185" cy="205" rx="82" ry="58" fill="#b98a55"/><circle cx="235" cy="175" r="34" fill="#7fa653"/><circle cx="150" cy="230" r="26" fill="#d9503f"/><path d="M120 190 Q160 150 210 175" stroke="#f0d68a" stroke-width="10" fill="none"/></g>'
                        '<g id="%s-steam" opacity="0" stroke="#fff" stroke-width="7" fill="none" stroke-linecap="round"><path d="M150 96 q14 -28 0 -56 M200 86 q14 -28 0 -56 M250 96 q14 -28 0 -56"/></g></svg>') % (style, pid, pid)
            sparks = "".join('<div class="sparkle" id="%s-s%d" style="left:%dpx; top:%dpx;"></div>' % (bid, i, x, y) for i, (x, y) in enumerate([(1000, 200), (1690, 170), (1720, 640), (960, 700), (1360, 90), (1560, 880)]))
            inner_scene = ('<div class="scene"><div class="phone" id="%s-phone" style="left:230px;top:110px;"><div class="screen">%s</div><div class="notch"></div></div>'
                           '<div class="hero" id="%s-hero">%s<div class="shine" id="%s-shine"></div></div>%s</div>'
                           % (bid, plate_svg(bid + "-p", "left:0;top:180px;width:388px;height:388px"), bid, plate_svg(bid + "-h", "left:0;top:0;width:760px;height:760px"), bid, sparks))
            t0 = steps.get("snap", t_in + 0.2); ts = steps.get("spice", t0 + 1.6)
            js("tl.fromTo('#%s-phone', { opacity: 0, y: 60, rotation: -4 }, { opacity: 1, y: 0, rotation: 0, duration: 0.55, ease: 'power2.out' }, %.3f);" % (bid, t0))
            js("tl.fromTo('#%s-hero', { opacity: 0, scale: 0.45, x: -520, y: 120 }, { opacity: 1, scale: 1, x: 0, y: 0, duration: 0.6, ease: 'power2.out' }, %.3f);" % (bid, ts - 0.15))
            js("tl.fromTo('#%s-shine', { xPercent: 0, opacity: 0 }, { xPercent: 620, opacity: 1, duration: 0.9, ease: 'power1.inOut' }, %.3f);" % (bid, ts + 0.35))
            js("tl.to('#%s-shine', { opacity: 0, duration: 0.12 }, %.3f);" % (bid, ts + 1.17))
            js("tl.to('#%s-h-food ellipse', { attr: { fill: '#d4913f' }, duration: 0.6, ease: 'power2.out' }, %.3f);" % (bid, ts + 0.6))
            js("tl.to('#%s-h-food circle', { attr: { fill: (function(i, el){ return i === 0 ? '#5fb63f' : '#ef3b2a'; }) }, duration: 0.6, ease: 'power2.out' }, %.3f);" % (bid, ts + 0.6))
            js("tl.to('#%s-h-food path', { attr: { stroke: '#ffd66b' }, duration: 0.6, ease: 'power2.out' }, %.3f);" % (bid, ts + 0.6))
            js("tl.fromTo('#%s-h-steam', { opacity: 0, y: 14 }, { opacity: 0.95, y: -8, duration: 0.7, ease: 'power2.out' }, %.3f);" % (bid, ts + 0.75))
            for i in range(6):
                js("tl.fromTo('#%s-s%d', { opacity: 0, scale: 0.2, rotation: 0 }, { opacity: 1, scale: 1.2, rotation: 90, duration: 0.32, ease: 'power2.out' }, %.3f);" % (bid, i, ts + 0.55 + i * 0.07))
                js("tl.to('#%s-s%d', { opacity: 0, scale: 0.4, duration: 0.3, ease: 'power2.in' }, %.3f);" % (bid, i, ts + 0.55 + i * 0.07 + 0.55))
        elif kind == "profile":
            # a LinkedIn-style profile card, no real person: grey bars for text, a silhouette avatar that gets its ring on the word
            avatar = '<svg viewBox="0 0 220 220"><circle cx="110" cy="84" r="46" fill="#9fb0c3"/><path d="M30 215 Q110 120 190 215 Z" fill="#9fb0c3"/></svg>'
            bars = "".join('<div class="bar" id="%s-b%d" style="left:%dpx; top:%dpx; width:%dpx;"></div>' % (bid, i, x, y, w) for i, (x, y, w) in enumerate([(330, 236, 360), (330, 282, 520), (64, 380, 700), (64, 426, 560), (64, 500, 300)]))
            inner_scene = ('<div class="scene"><div class="card" id="%s-card"><div class="band"></div><div class="avatar">%s</div><div class="ring" id="%s-ring"></div>%s'
                           '<div class="logo"><img src="%s" alt="" /></div><div class="shine" id="%s-shine"></div></div>%s</div>'
                           % (bid, avatar, bid, bars, b.get("logo", "img/linkedin.svg"), bid,
                              "".join('<div class="sparkle" id="%s-s%d" style="left:%dpx; top:%dpx;"></div>' % (bid, i, x, y) for i, (x, y) in enumerate([(520, 250), (760, 230), (740, 470), (500, 500)]))))
            t0 = steps.get("card", t_in + 0.2); th = steps.get("headshot", t0 + 2.0)
            js("tl.fromTo('#%s-card', { opacity: 0, y: 50 }, { opacity: 1, y: 0, duration: 0.5, ease: 'power2.out' }, %.3f);" % (bid, t0))
            js("tl.set('#host-%s .bar', { scaleX: 0 }, 0);" % bid)
            js("tl.to('#host-%s .bar', { scaleX: 1, duration: 0.45, ease: 'power2.out', stagger: 0.08 }, %.3f);" % (bid, t0 + 0.35))
            js("tl.fromTo('#%s-shine', { xPercent: 0, opacity: 0 }, { xPercent: 620, opacity: 1, duration: 0.9, ease: 'power1.inOut' }, %.3f);" % (bid, th))
            js("tl.to('#%s-shine', { opacity: 0, duration: 0.12 }, %.3f);" % (bid, th + 0.82))
            js("tl.fromTo('#%s-ring', { opacity: 0, scale: 0.8 }, { opacity: 1, scale: 1, duration: 0.4, ease: 'power2.out' }, %.3f);" % (bid, th + 0.35))
            for i in range(4):
                js("tl.fromTo('#%s-s%d', { opacity: 0, scale: 0.2 }, { opacity: 1, scale: 1.1, rotation: 90, duration: 0.32, ease: 'power2.out' }, %.3f);" % (bid, i, th + 0.4 + i * 0.08))
                js("tl.to('#%s-s%d', { opacity: 0, scale: 0.4, duration: 0.3, ease: 'power2.in' }, %.3f);" % (bid, i, th + 0.4 + i * 0.08 + 0.55))
        else:
            raise SystemExit("unknown scene kind %r" % kind)
        label = scene_label(bid, b, t_out)
        inner = '<div class="cut"><div class="gridbg"></div>%s%s</div>' % (inner_scene, label)
        html_parts.append(host(bid, t_in, t_out, track, inner, anchor))
        transition(b, t_in, t_out)

    # ---- DRAFT formats. Same tokens, same glass rules, no bounces, no animated blur. ----
    elif t == "browser3d":
        # 4c. a real capture in a slanted browser window floating on the wash. It rises in from depth already tilted,
        # then the camera orbits slowly toward it while the page scrolls: one continuous move, never an idle wobble.
        side = -1 if b.get("near", "right") == "right" else 1          # which edge of the window is nearer the camera
        ry, rx = 15 * side, 7
        call = ""
        if b.get("callout"):
            c = b["callout"]
            call = '<div class="b3-call" id="%s-call" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx"></div>' % (bid, c["x"], c["y"], c["w"], c["h"])
        inner_scene = ('<div class="b3-stage"><div class="b3-rig" id="%s-rig"><div class="b3-floor"></div>'
                       '<div class="b3-win"><div class="b3-bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><div class="url">%s</div></div>'
                       '<div class="b3-view"><div class="b3-scroll" id="%s-scroll"><img src="%s" alt="" />%s</div></div>'
                       '<div class="b3-sheen" id="%s-sheen"></div></div></div></div>'
                       % (bid, b["domain"], bid, b["src"], call, bid))
        label = scene_label(bid, b, t_out)
        html_parts.append(host(bid, t_in, t_out, track, '<div class="cut"><div class="gridbg"></div>%s%s</div>' % (inner_scene, label), anchor))
        settle = 1.0
        js("tl.fromTo('#%s-rig', { rotationY: %d, rotationX: %d, z: -420, y: 170 }, { rotationY: %d, rotationX: %d, z: 0, y: 0, duration: %.2f, ease: 'power3.out' }, %.3f);"
           % (bid, ry + 12 * side, rx + 9, ry, rx, settle, t_in))
        hold = max(0.5, t_out - t_in - settle)
        js("tl.to('#%s-rig', { rotationY: %.2f, z: 90, duration: %.3f, ease: 'power1.inOut' }, %.3f);" % (bid, ry * 0.45, hold, t_in + settle))
        if b.get("scroll"):
            js("tl.fromTo('#%s-scroll', { y: 0 }, { y: %d, duration: %.3f, ease: 'power1.inOut' }, %.3f);" % (bid, -int(b["scroll"]), max(0.5, t_out - t_in - 0.9), t_in + 0.7))
        js("tl.fromTo('#%s-sheen', { xPercent: 0 }, { xPercent: 700, duration: 1.2, ease: 'power1.inOut' }, %.3f);" % (bid, t_in + 0.45))
        js("tl.fromTo('#%s-sheen', { opacity: 0 }, { opacity: 1, duration: 0.3, ease: 'power1.out' }, %.3f);" % (bid, t_in + 0.45))
        js("tl.to('#%s-sheen', { opacity: 0, duration: 0.3, ease: 'power1.in' }, %.3f);" % (bid, t_in + 1.35))
        if b.get("callout"):
            ca = float(b["callout"]["at"])
            js("tl.fromTo('#%s-call', { opacity: 0, scale: 1.06 }, { opacity: 1, scale: 1, duration: 0.4, ease: 'power2.out' }, %.3f);" % (bid, ca))
        transition(b, t_in, t_out)
    elif t == "fan3d":
        # 4d. two or three screenshots fanned in depth (an app showcase): side cards turned 16 deg and pushed back,
        # the middle one forward. They rise in, the fan orbits a little, one card can come forward on its word.
        imgs = b["images"][:3]; n = len(imgs); ph = b.get("frame", "card") == "phone"; br = b.get("frame") == "browser"
        w, h = (330, 700) if ph else ((600, 740) if br else (560, 700))
        gap = 430 if ph else (620 if br else 600)
        lift = 60 if b.get("label") else 20            # clear the caption line under the fan
        at = [float(x) for x in b.get("at", [t_in + 0.1 + 0.14 * i for i in range(n)])]
        slots = {1: [0], 2: [-0.5, 0.5], 3: [-1, 0, 1]}[n]
        cards = ""
        for i, (src, s) in enumerate(zip(imgs, slots)):
            if br:
                # "browser" (a cropped card cuts the website off instead of showing more of it): a real browser window,
                # the page width-fit from its top (a long capture), or a whole post contained on a light page
                # ("fit": "contain"); the page can scroll on its word ("scroll").
                dom = (b.get("domains") or [""] * n)[i]; fit = (b.get("fit") or ["width"] * n)[i]
                cards += ('<div class="fan-card browser" id="%s-c%d" style="width:%dpx;height:%dpx;left:%dpx;top:%dpx">'
                          '<div class="fb-bar"><span class="fb-dot" style="background:#FF5F57"></span><span class="fb-dot" style="background:#FEBC2E"></span>'
                          '<span class="fb-dot" style="background:#28C840"></span><div class="fb-url">%s</div></div>'
                          '<div class="fb-view%s"><img id="%s-p%d" src="%s" alt="" /></div></div>'
                          % (bid, i, w, h, -w // 2 + int(s * gap), -h // 2 - lift, dom, " contain" if fit == "contain" else "", bid, i, src))
                continue
            cards += ('<div class="fan-card%s" id="%s-c%d" style="width:%dpx;height:%dpx;left:%dpx;top:%dpx"><img src="%s" alt="" /></div>'
                      % (" phone" if ph else "", bid, i, w, h, -w // 2 + int(s * gap), -h // 2 - lift, src))
        inner_scene = '<div class="fan-stage"><div class="fan-rig" id="%s-rig">%s</div></div>' % (bid, cards)
        label = scene_label(bid, b, t_out)
        html_parts.append(host(bid, t_in, t_out, track, '<div class="cut"><div class="gridbg"></div>%s%s</div>' % (inner_scene, label), anchor))
        for i, s in enumerate(slots):
            rest_ry, rest_z, rest_sc = -16 * s, (-70 if s else 30), (1.0 if s else 1.05)
            js("tl.fromTo('#%s-c%d', { opacity: 0, y: 220, z: -320, rotationY: %.1f, scale: %.2f }, { opacity: 1, y: 0, z: %d, rotationY: %.1f, scale: %.2f, duration: 0.8, ease: 'power3.out' }, %.3f);"
               % (bid, i, rest_ry * 1.4, rest_sc, rest_z, rest_ry, rest_sc, at[i]))
        js("tl.fromTo('#%s-rig', { rotationY: 5, z: 0 }, { rotationY: -5, z: 70, duration: %.3f, ease: 'power1.inOut', immediateRender: false }, %.3f);" % (bid, max(0.5, t_out - t_in), t_in))
        if b.get("focus"):
            fi, ft = int(b["focus"]["index"]), float(b["focus"]["at"])
            js("tl.to('#%s-c%d', { z: 160, scale: 1.12, rotationY: 0, duration: 0.55, ease: 'power2.inOut' }, %.3f);" % (bid, fi, ft))
            others = ", ".join("#%s-c%d" % (bid, i) for i in range(n) if i != fi)
            if others:
                js("tl.to('%s', { opacity: 0.4, duration: 0.45, ease: 'power2.out' }, %.3f);" % (others, ft))
        if br and b.get("scroll"):          # "scrolling down a website": the page moves up inside its window, one smooth move
            sc = b["scroll"]
            js("tl.to('#%s-p%d', { y: %d, duration: %.3f, ease: 'power1.inOut' }, %.3f);"
               % (bid, int(sc["index"]), -int(sc["by"]), float(sc.get("dur", 1.8)), float(sc["at"])))
        transition(b, t_in, t_out)
    elif t == "stats":
        # 24. stat tiles: each number counts up in full digits on its own word. "row" = full-frame on the wash,
        # "stack" = a column of glass tiles over the footage at tl/tr.
        items = b["items"]; stack = b.get("layout", "row") == "stack"
        em = set(b.get("em_tiles", []))
        tiles = ""
        for i, it in enumerate(items):
            tiles += ('<div class="glass st-tile%s" id="%s-t%d"><div class="inner" id="%s-ti%d"><div class="st-num" id="%s-n%d">%s</div><div class="st-lab">%s</div></div></div>'
                      % (" em" if i in em else "", bid, i, bid, i, bid, i, fmt_value(0, it.get("prefix", ""), it.get("suffix", ""), it.get("decimals", 0)), it["label"]))
        if stack:
            pos = POS.get(b.get("pos", "tr"), POS["tr"])
            inner = '<div class="st-stack" style="%s">%s</div>' % (pos, tiles)
        else:
            title = '<div class="st-title" id="%s-title">%s</div>' % (bid, em_spans(b["title"], b.get("em"))) if b.get("title") else ""
            inner = '<div class="cut"><div class="gridbg"></div>%s<div class="st-row">%s</div></div>' % (title, tiles)
            if b.get("title"):
                js("tl.fromTo('#%s-title', { opacity: 0, y: 26 }, { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }, %.3f);" % (bid, t_in + 0.05))
        html_parts.append(host(bid, t_in, t_out, track, inner, anchor))
        for i, it in enumerate(items):
            ta = float(it.get("at", t_in + 0.3 + 0.35 * i))
            js("glassIn('#%s-t%d', %.3f, { y: 30 });" % (bid, i, ta))
            js("tl.fromTo('#%s-ti%d', { opacity: 0 }, { opacity: 1, duration: 0.36 }, %.3f);" % (bid, i, ta + 0.04))
            js("countUp('#%s-n%d', %s, %.3f, %.2f, %s, %s, %d);" % (bid, i, it["value"], ta + 0.1, float(it.get("dur", 1.1)),
               json.dumps(it.get("prefix", "")), json.dumps(it.get("suffix", "")), int(it.get("decimals", 0))))
            if stack:
                js("tl.to('#%s-ti%d', { opacity: 0, duration: 0.28, ease: 'power2.in' }, %.3f);" % (bid, i, t_out - 0.38))
                js("glassOut('#%s-t%d', %.3f, 0.33);" % (bid, i, t_out - 0.34))
                js("tl.set('#%s-ti%d', { opacity: 0 }, %.3f);" % (bid, i, t_out - 0.10))
        if not stack:
            transition(b, t_in, t_out)
    elif t == "growth":
        # 25. growth card (a "+248%" panel, in the house glass): the number counts up, bars rise left to right,
        # the line draws over them and one dot lands on the last value. Over the footage at tl/tr.
        vals = [float(v) for v in b.get("bars", [22, 35, 50, 72, 100])]; top = max(vals) or 1.0
        n = len(vals); W, H, G = 524.0, 250.0, 16.0; bw = (W - G * (n - 1)) / n
        bars = "".join('<div class="gr-bar%s" style="height:%.0fpx"></div>' % (" last" if i == n - 1 else "", H * v / top * 0.86) for i, v in enumerate(vals))
        morph = bool(b.get("morph"))       # chart morph: the bar tops become the line's points
        pts = [(i * (bw + G) + bw / 2, H - H * v / top * 0.86 - (0 if morph else 22)) for i, v in enumerate(vals)]
        d = smooth_path(pts) if morph else "M" + " L".join("%.1f %.1f" % p for p in pts)
        extra_svg, badge = "", ""
        if morph:
            extra_svg = ('<path class="gr-area" id="%s-area" d="%s L%.1f %.1f L%.1f %.1f Z"/>' % (bid, d, pts[-1][0], H, pts[0][0], H)
                         + "".join('<circle class="gr-pt" id="%s-pt%d" cx="%.1f" cy="%.1f" r="9"/>' % ((bid, i) + p) for i, p in enumerate(pts[:-1])))
            if b.get("badge"):
                badge = '<div class="gr-badge" id="%s-badge" style="left:%.0fpx;top:%.0fpx">%s</div>' % (bid, pts[-1][0], pts[-1][1] - 22, b["badge"])
        pos = POS.get(b.get("pos", "tr"), POS["tr"])
        inner = ('<div class="glass gr" id="%s-glass" style="%s"><div class="inner" id="%s-inner"><div class="gr-eye">%s</div>'
                 '<div class="gr-num" id="%s-num">%s</div>%s<div class="gr-plot"><div class="gr-bars" id="%s-bars">%s</div>'
                 '<svg viewBox="0 0 %d %d" preserveAspectRatio="none">%s<path class="gr-line" id="%s-line" d="%s"/><circle class="gr-dot" id="%s-dot" cx="%.1f" cy="%.1f" r="11"/></svg>%s</div></div></div>'
                 % (bid, pos, bid, b.get("eyebrow", ""), bid, fmt_value(0, b.get("prefix", ""), b.get("suffix", ""), b.get("decimals", 0)),
                    '<div class="gr-sub">%s</div>' % b["sub"] if b.get("sub") else "", bid, bars, W, H, extra_svg, bid, d, bid, pts[-1][0], pts[-1][1], badge))
        html_parts.append(host(bid, t_in, t_out, track, inner, anchor))
        tc = float(b.get("count_at", t_in + 0.35)); tb = float(b.get("bars_at", tc + 0.3)); tln = float(b.get("line_at", tb + 0.45))
        js("glassIn('#%s-glass', %.3f, { x: %d });" % (bid, t_in, -40 if b.get("pos", "tr") == "tl" else 40))
        js("tl.fromTo('#%s-inner', { opacity: 0 }, { opacity: 1, duration: 0.36 }, %.3f);" % (bid, t_in + 0.04))
        js("countUp('#%s-num', %s, %.3f, %.2f, %s, %s, %d);" % (bid, b["value"], tc, float(b.get("dur", 1.2)), json.dumps(b.get("prefix", "")), json.dumps(b.get("suffix", "")), int(b.get("decimals", 0))))
        js("tl.fromTo('#%s-bars .gr-bar', { scaleY: 0 }, { scaleY: 1, duration: 0.5, ease: 'power2.out', stagger: 0.08 }, %.3f);" % (bid, tb))
        LD = 1.4 if morph else 0.9      # the morph's line draws at an even pace, like the reference (1.5 s of a 2.2 s transform)
        if morph:   # (tuned to the reference motion) bars thin to stems one after another, each point appears as the line
                    # reaches it, the area fills with the line, the last point lands, then the badge
            js("tl.to('#%s-bars .gr-bar', { scaleX: 0.12, opacity: 0.45, duration: 1.1, ease: 'power3.inOut', stagger: 0.16 }, %.3f);" % (bid, tln - 0.35))
            for i in range(n - 1):
                js("tl.fromTo('#%s-pt%d', { opacity: 0, scale: 0.4, transformOrigin: '50%% 50%%' }, { opacity: 1, scale: 1, duration: 0.22, ease: 'power3.out' }, %.3f);" % (bid, i, tln + LD * i / (n - 1) - 0.03))
            js("tl.fromTo('#%s-area', { opacity: 0 }, { opacity: 1, duration: %.2f, ease: 'power3.inOut' }, %.3f);" % (bid, LD, tln))
            if badge:
                js("tl.fromTo('#%s-badge', { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.3, ease: 'power2.out' }, %.3f);" % (bid, tln + LD + 0.1))
        js("(function(){ var p = document.getElementById('%s-line'); var L = p.getTotalLength(); p.style.strokeDasharray = L; p.style.strokeDashoffset = L;"
           " tl.to(p, { strokeDashoffset: 0, duration: %.2f, ease: '%s' }, %.3f); })();" % (bid, LD, "none" if morph else "power2.inOut", tln))
        js("tl.fromTo('#%s-dot', { opacity: 0, scale: 0.4, transformOrigin: '50%% 50%%' }, { opacity: 1, scale: 1, duration: 0.3, ease: 'power2.out' }, %.3f);" % (bid, tln + LD - 0.05))
        js("tl.to('#%s-inner', { opacity: 0, duration: 0.28, ease: 'power2.in' }, %.3f);" % (bid, t_out - 0.38))
        js("glassOut('#%s-glass', %.3f, 0.33);" % (bid, t_out - 0.34))
        js("tl.set('#%s-inner', { opacity: 0 }, %.3f);" % (bid, t_out - 0.10))
    elif t == "bars":
        # 26. bar comparison, full-frame on the wash: rows arrive on their words, bars grow, the value lands at the tip.
        # One row is ours ("hi"): cyan. Everything else stays white and quiet so the gap is the message.
        rows = b["rows"]; top = max(float(r["value"]) for r in rows) or 1.0
        html_rows = ""
        for i, r in enumerate(rows):
            frac = max(0.012, 0.8 * float(r["value"]) / top)      # the longest bar stops at 80% so its value fits
            html_rows += ('<div class="bc-row%s" id="%s-r%d"><div class="bc-lab">%s</div><div class="bc-track"><div class="bc-fill" id="%s-f%d" style="width:%.2f%%"></div>'
                          '<div class="bc-val" id="%s-v%d" style="left:%.2f%%">%s</div></div></div>'
                          % (" hi" if r.get("hi") else "", bid, i, r["label"], bid, i, frac * 100, bid, i, frac * 100, r.get("text", str(r["value"]))))
        title = '<div class="st-title" id="%s-title" style="top:150px">%s</div>' % (bid, em_spans(b["title"], b.get("em"))) if b.get("title") else ""
        top_px = 300 if b.get("title") else 250
        inner = '<div class="cut"><div class="gridbg"></div>%s<div class="bc" style="top:%dpx">%s</div>%s</div>' % (title, top_px + (4 - len(rows)) * 45, html_rows, scene_label(bid, b, t_out))
        html_parts.append(host(bid, t_in, t_out, track, inner, anchor))
        if b.get("title"):
            js("tl.fromTo('#%s-title', { opacity: 0, y: 26 }, { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }, %.3f);" % (bid, t_in + 0.05))
        for i, r in enumerate(rows):
            ta = float(r.get("at", t_in + 0.4 + 0.5 * i))
            js("tl.fromTo('#%s-r%d', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }, %.3f);" % (bid, i, ta))
            js("tl.fromTo('#%s-f%d', { scaleX: 0 }, { scaleX: 1, duration: %.2f, ease: 'power2.inOut' }, %.3f);" % (bid, i, 0.5 + 0.4 * float(r["value"]) / top, ta + 0.1))
            js("tl.fromTo('#%s-v%d', { opacity: 0, x: -12 }, { opacity: 1, x: 0, duration: 0.3, ease: 'power2.out' }, %.3f);" % (bid, i, ta + 0.5 + 0.4 * float(r["value"]) / top))
        transition(b, t_in, t_out)
    elif t == "pipeline":
        # 27. pipeline, full-frame on the wash: one glass node per spoken step. The connector draws while a light runs it,
        # the node lands lit (cyan) and hands the light on; the payoff node lands magenta and keeps it.
        steps = b["steps"][:5]; n = len(steps); NW, GAP = 290, (110 if n <= 4 else 90)
        total = n * NW + (n - 1) * GAP; x0 = (1920 - total) // 2
        nodes, links = "", ""
        for i, s in enumerate(steps):
            x = x0 + i * (NW + GAP)
            icon = ('<svg viewBox="0 0 64 64"><path class="ic" d="%s"/></svg>' % ICONS[s["icon"]]) if s.get("icon") in ICONS else ""
            sub = '<div class="pl-sub">%s</div>' % s["sub"] if s.get("sub") else ""
            nodes += ('<div class="glass pl-node" id="%s-n%d" style="left:%dpx"><div class="inner" id="%s-ni%d"><div class="pl-num">%02d</div>%s<div class="pl-lab">%s</div>%s</div></div>'
                      % (bid, i, x, bid, i, i + 1, icon, s["label"], sub))
            if i:
                lx = x - GAP + 12
                links += '<div class="pl-link" id="%s-l%d" style="left:%dpx;width:%dpx"></div><div class="pl-run" id="%s-p%d" style="left:%dpx"></div>' % (bid, i, lx, GAP - 24, bid, i, lx)
        title = '<div class="pl-title" id="%s-title">%s</div>' % (bid, em_spans(b["title"], b.get("em"))) if b.get("title") else ""
        inner = '<div class="cut"><div class="gridbg"></div>%s<div class="pl">%s%s</div>%s</div>' % (title, links, nodes, scene_label(bid, b, t_out))
        html_parts.append(host(bid, t_in, t_out, track, inner, anchor))
        if b.get("title"):
            js("tl.fromTo('#%s-title', { opacity: 0, y: 26 }, { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }, %.3f);" % (bid, t_in + 0.05))
        lit = "'rgba(10,240,240,0.95)'"; litglow = "'0 0 40px rgba(10,240,240,0.55)'"
        pay = "'rgba(205,0,238,0.95)'"; payglow = "'0 0 46px rgba(205,0,238,0.6)'"
        rest = "'rgba(255,255,255,0.58)'"; restglow = "'0 24px 80px rgba(0,0,0,0.38)'"
        prev_at = None
        for i, s in enumerate(steps):
            ta = float(s.get("at", t_in + 0.3 + 1.2 * i))
            land = ta
            if i:
                js("tl.fromTo('#%s-l%d', { scaleX: 0 }, { scaleX: 1, duration: 0.45, ease: 'power2.inOut' }, %.3f);" % (bid, i, ta - 0.05))
                js("tl.fromTo('#%s-p%d', { x: 0, opacity: 0 }, { x: %d, opacity: 1, duration: 0.45, ease: 'power2.inOut' }, %.3f);" % (bid, i, GAP - 24, ta - 0.05))
                js("tl.to('#%s-p%d', { opacity: 0, duration: 0.15 }, %.3f);" % (bid, i, ta + 0.42))
                land = ta + 0.25
            c, g = (pay, payglow) if s.get("payoff") else (lit, litglow)
            js("tl.fromTo('#%s-n%d', { backgroundColor: 'rgba(255,255,255,0)', borderColor: 'rgba(255,255,255,0)', boxShadow: '0 0 0px rgba(0,0,0,0)', y: 30 },"
               " { backgroundColor: 'rgba(255,255,255,0.14)', borderColor: %s, boxShadow: %s, y: 0, duration: 0.42, ease: 'power2.out' }, %.3f);" % (bid, i, c, g, land))
            js("tl.fromTo('#%s-ni%d', { opacity: 0 }, { opacity: 1, duration: 0.36 }, %.3f);" % (bid, i, land + 0.04))
            if i and not steps[i - 1].get("payoff"):
                js("tl.to('#%s-n%d', { borderColor: %s, boxShadow: %s, duration: 0.4, ease: 'power2.out' }, %.3f);" % (bid, i - 1, rest, restglow, land + 0.1))
        transition(b, t_in, t_out)
    elif t == "hub":
        # 28. hub, full-frame on the wash: the idea sits in the middle and a cyan ring closes around it; each part arrives
        # on its word at the end of a spoke that draws out from the centre. resolve_at: the parts dim, the centre glows.
        spokes = b.get("spokes", [])[:6]; n = len(spokes)
        angles = {1: [0], 2: [180, 0], 3: [200, -20, 90], 4: [205, 335, 155, 25], 5: [200, 340, 150, 30, 270], 6: [210, 330, 150, 30, 270, 90]}.get(n, [])
        cx, cy, RX, RY = 960, 540, 610, 330
        lines, pills = "", ""
        for i, (sp, ang) in enumerate(zip(spokes, angles)):
            a = math.radians(ang); px, py = cx + RX * math.cos(a), cy + RY * math.sin(a)
            x1, y1 = cx + 168 * math.cos(a), cy + 168 * math.sin(a)
            x2, y2 = cx + (RX * math.cos(a)) * 0.74, cy + (RY * math.sin(a)) * 0.74
            lines += '<line class="hb-spoke" id="%s-s%d" x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f"/>' % (bid, i, x1, y1, x2, y2)
            pills += ('<div class="glass hb-pill" id="%s-p%d" style="left:%.0fpx;top:%.0fpx;translate:-50%% -50%%"><div class="inner" id="%s-pi%d">%s</div></div>'
                      % (bid, i, px, py, bid, i, sp[0]))
        svg = ('<svg class="hb-svg" viewBox="0 0 1920 1080">%s<circle class="hb-ring" id="%s-ring" cx="%d" cy="%d" r="164" transform="rotate(-90 %d %d)"/></svg>'
               % (lines, bid, cx, cy, cx, cy))
        center = '<div class="glass hb-c" id="%s-c"><div class="inner" id="%s-ci">%s</div></div>' % (bid, bid, b["center"])
        title = '<div class="pl-title" id="%s-title" style="top:90px">%s</div>' % (bid, em_spans(b["title"], b.get("em"))) if b.get("title") else ""
        inner = '<div class="cut"><div class="gridbg"></div>%s%s%s%s%s</div>' % (title, svg, center, pills, scene_label(bid, b, t_out))
        html_parts.append(host(bid, t_in, t_out, track, inner, anchor))
        if b.get("title"):
            js("tl.fromTo('#%s-title', { opacity: 0, y: 26 }, { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }, %.3f);" % (bid, t_in + 0.05))
        js("glassIn('#%s-c', %.3f, { y: 24 });" % (bid, t_in + 0.1))
        js("tl.fromTo('#%s-ci', { opacity: 0 }, { opacity: 1, duration: 0.36 }, %.3f);" % (bid, t_in + 0.14))
        js("(function(){ var L = 2 * Math.PI * 164; var r = document.getElementById('%s-ring'); r.style.strokeDasharray = L; r.style.strokeDashoffset = L;"
           " tl.to(r, { strokeDashoffset: 0, duration: 0.9, ease: 'power2.inOut' }, %.3f); })();" % (bid, float(b.get("ring_at", t_in + 0.5))))
        js("(function(){ document.querySelectorAll('#host-%s .hb-spoke').forEach(function(l){ var L = Math.hypot(l.x2.baseVal.value - l.x1.baseVal.value, l.y2.baseVal.value - l.y1.baseVal.value);"
           " l.style.strokeDasharray = L; l.style.strokeDashoffset = L; }); })();" % bid)
        for i, sp in enumerate(spokes):
            ta = float(sp[1])
            js("tl.to('#%s-s%d', { strokeDashoffset: 0, duration: 0.35, ease: 'power2.out' }, %.3f);" % (bid, i, ta - 0.1))
            js("glassIn('#%s-p%d', %.3f, { y: 16 });" % (bid, i, ta + 0.15))
            js("tl.fromTo('#%s-pi%d', { opacity: 0 }, { opacity: 1, duration: 0.36 }, %.3f);" % (bid, i, ta + 0.19))
        if b.get("resolve_at") is not None:
            tr = float(b["resolve_at"])
            if n:
                js("tl.to('#host-%s .hb-pill .inner, #host-%s .hb-spoke', { opacity: 0.56, duration: 0.4, ease: 'power2.out' }, %.3f);" % (bid, bid, tr))
            js("tl.to('#%s-c', { borderColor: 'rgba(10,240,240,0.95)', boxShadow: '0 0 60px rgba(10,240,240,0.55)', duration: 0.45, ease: 'power2.out' }, %.3f);" % (bid, tr))
            js("tl.to('#%s-ci', { color: '#0AF0F0', duration: 0.45, ease: 'power2.out' }, %.3f);" % (bid, tr))
        transition(b, t_in, t_out)
    elif t == "equation":
        # 29. equation strip over the footage: "Skills + Workflows = 40 hrs saved". Each term rises on its word into one
        # light glass strip (layout fixed, so the line never shifts); the result lands in cyan ("em") or magenta ("pay").
        toks = ""
        for i, tk in enumerate(b["terms"]):
            style = tk[2] if len(tk) > 2 else ("op" if tk[0] in ("+", "=", "-", "x", "×", "→", "/") else "")
            toks += '<span class="tk %s" id="%s-k%d">%s</span>' % (style, bid, i, tk[0])
        where = "bottom:80px;" if b.get("pos", "bottom") == "bottom" else "top:96px;"
        inner = '<div class="glass eq" id="%s-glass" style="%s"><div class="inner">%s</div></div>' % (bid, where, toks)
        html_parts.append(host(bid, t_in, t_out, track, inner, anchor))
        js("glassIn('#%s-glass', %.3f, { y: 20 });" % (bid, t_in))
        for i, tk in enumerate(b["terms"]):
            js("tl.fromTo('#%s-k%d', { opacity: 0, y: 26 }, { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }, %.3f);" % (bid, i, float(tk[1])))
        js("tl.to('#host-%s .tk', { opacity: 0, duration: 0.28, ease: 'power2.in' }, %.3f);" % (bid, t_out - 0.38))
        js("glassOut('#%s-glass', %.3f, 0.33);" % (bid, t_out - 0.34))
        js("tl.set('#host-%s .tk', { opacity: 0 }, %.3f);" % (bid, t_out - 0.10))
    elif t == "wall":
        # 9c. slot wall, top centre: the video's parts as sockets. In the hook they are planted empty (numbers only, an open
        # loop the viewer can see); at each section boundary the wall comes back with the spent slots dim and the live one
        # filling on its word; at the recap every slot is full and one cyan thread runs through all of them.
        slots = b["slots"]; filled = int(b.get("filled", 0)); now = b.get("now")
        cells = ""
        for i, s in enumerate(slots):
            cls = "wl-slot" + (" done" if i < filled and i != now else "")
            cells += '<div class="%s" id="%s-s%d"><div class="n">%02d</div><div class="fill"></div><div class="t">%s</div></div>' % (cls, bid, i, i + 1, s)
        thread = '<div class="wl-thread" id="%s-thread"></div>' % bid if b.get("recap") else ""
        inner = '<div class="glass wl" id="%s-glass"><div class="inner" id="%s-inner">%s%s</div></div>' % (bid, bid, cells, thread)
        html_parts.append(host(bid, t_in, t_out, track, inner, anchor))
        js("glassIn('#%s-glass', %.3f, { y: -22 });" % (bid, t_in))
        js("tl.fromTo('#%s-inner', { opacity: 0 }, { opacity: 1, duration: 0.36 }, %.3f);" % (bid, t_in + 0.04))
        if filled == 0 and now is None:
            js("tl.fromTo('#host-%s .wl-slot', { opacity: 0, y: -10 }, { opacity: 1, y: 0, duration: 0.35, ease: 'power2.out', stagger: 0.09 }, %.3f);" % (bid, t_in + 0.12))
        tf = float(b.get("fill_at", t_in + 0.8))
        if now is not None:
            js("tl.fromTo('#%s-s%d .fill', { opacity: 0 }, { opacity: 1, duration: 0.4, ease: 'power2.out' }, %.3f);" % (bid, int(now), tf))
            js("tl.fromTo('#%s-s%d .t', { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }, %.3f);" % (bid, int(now), tf + 0.05))
        if b.get("recap"):      # every slot lights left to right while the thread runs under the whole wall
            js("tl.to('#host-%s .wl-slot .t', { opacity: 1, duration: 0.3, ease: 'power2.out' }, %.3f);" % (bid, tf - 0.3))
            js("tl.fromTo('#host-%s .wl-slot .fill', { opacity: 0 }, { opacity: 1, duration: 0.35, ease: 'power2.out', stagger: 0.16 }, %.3f);" % (bid, tf + 0.05))
            js("tl.fromTo('#%s-thread', { scaleX: 0 }, { scaleX: 1, duration: 1.0, ease: 'power2.inOut' }, %.3f);" % (bid, tf))
        js("tl.to('#%s-inner', { opacity: 0, duration: 0.28, ease: 'power2.in' }, %.3f);" % (bid, t_out - 0.38))
        js("glassOut('#%s-glass', %.3f, 0.33);" % (bid, t_out - 0.34))
        js("tl.set('#%s-inner', { opacity: 0 }, %.3f);" % (bid, t_out - 0.10))
    elif t == "popout":
        # 3c. glass pop-out (a left glass pop-out, on our 3b move): the footage pushes right, a light glass panel
        # carries a short title and the items on the left, each on its word. The camera releases after the panel leaves.
        mark = CHECK_SVG if b.get("marker") == "check" else '<div class="d"></div>'
        items = "".join('<div class="item" id="%s-i%d"%s>%s<div class="t">%s</div></div>' % (bid, i, item_attrs(it), mark, it[0]) for i, it in enumerate(b["items"]))
        ttl = '<div class="ttl">%s</div>' % b["title"] if b.get("title") else ""
        inner = '<div class="glass po" id="%s-glass"><div class="inner" id="%s-inner">%s%s</div></div>' % (bid, bid, ttl, items)
        html_parts.append(host(bid, t_in, t_out, track, inner, anchor))
        rel = float(b.get("release", t_out - 0.3))
        js("tl.to('#video-wrap', { scale: 1.18, x: 150, duration: 0.75, ease: 'power2.inOut' }, %.3f);" % t_in)
        js("glassIn('#%s-glass', %.3f, { x: -40 });" % (bid, t_in + 0.2))
        js("tl.fromTo('#%s-inner', { opacity: 0 }, { opacity: 1, duration: 0.36 }, %.3f);" % (bid, t_in + 0.24))
        for i, it in enumerate(b["items"]):
            js("tl.set('#%s-i%d', { display: 'flex' }, %.3f);" % (bid, i, float(it[1])))
            js("tl.fromTo('#%s-i%d', { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: 0.40, ease: 'power2.out' }, %.3f);" % (bid, i, float(it[1])))
            if b.get("marker") == "check":
                check_in("#%s-i%d" % (bid, i), float(it[1]))
        js("tl.to('#%s-inner', { opacity: 0, duration: 0.28, ease: 'power2.in' }, %.3f);" % (bid, rel - 0.75))
        js("glassOut('#%s-glass', %.3f, 0.33);" % (bid, rel - 0.7))
        js("tl.set('#%s-inner', { opacity: 0 }, %.3f);" % (bid, rel - 0.36))
        js("tl.to('#video-wrap', { scale: 1.00, x: 0, duration: 0.55, ease: 'power2.inOut' }, %.3f);" % (rel - 0.3))

    # ---- more DRAFT formats, rebuilt on the house tokens ----
    elif t == "flow":
        # 30. flowing paths, full-frame (tuned to a reference motion board): one input on the left, light runs out along
        # curved paths to 2-4 outputs, each lighting on its word with a ring that opens and fades; then the outputs send light
        # on to one result (0.14 s apart, the lit stroke shading cyan to magenta) that lands magenta. The map is on screen, dim,
        # from the first frame. While it holds, a second wave of light runs the lit paths again so the frame keeps moving.
        outs = [o if isinstance(o, dict) else {"label": o[0], "at": o[1]} for o in b["outputs"][:4]]
        n = len(outs); src = b["source"]; res = b.get("result")
        SX, MX, RX = (330, 960, 1590) if res else (520, 1340, 0)
        ys = {1: [540], 2: [390, 690], 3: [300, 540, 780], 4: [250, 430, 610, 790]}[n]
        s_at = float(src.get("at", t_in + 0.4)); PD = 0.9          # pulse travel time (the reference's 1.05 s, a touch quicker for speech)
        paths, pulses = "", ""
        def curve(x1, y1, x2, y2):
            m = (x1 + x2) / 2.0
            return "M%d %d C%d %d %d %d %d %d" % (x1, y1, m, y1, m, y2, x2, y2)
        grad = ('<defs><linearGradient id="%s-pg" gradientUnits="userSpaceOnUse" x1="%d" y1="0" x2="%d" y2="0"><stop offset="0" stop-color="#0AF0F0"/>'
                '<stop offset="1" stop-color="#CD00EE"/></linearGradient></defs>' % (bid, MX + 170, RX - 170)) if res else ""
        for i, y in enumerate(ys):
            d = curve(SX + 170, 540, MX - 170, y)
            paths += '<path class="fl-path" d="%s"/><path class="fl-glow" id="%s-g%d" d="%s"/><path class="fl-lit" id="%s-p%d" d="%s"/>' % (d, bid, i, d, bid, i, d)
            pulses += '<div class="fl-pulse" id="%s-u%d"></div>' % (bid, i)
            if res:
                d2 = curve(MX + 170, y, RX - 170, 540)
                paths += ('<path class="fl-path" d="%s"/><path class="fl-glow pay" id="%s-G%d" d="%s"/><path class="fl-lit pay" id="%s-P%d" d="%s" style="stroke:url(#%s-pg)"/>'
                          % (d2, bid, i, d2, bid, i, d2, bid))
                pulses += '<div class="fl-pulse pay" id="%s-U%d"></div>' % (bid, i)
        def node(nid, x, y, label):
            return ('<div class="glass fl-node" id="%s" style="left:%dpx;top:%dpx"><div class="fl-ring" id="%s-r"></div><div class="inner" id="%s-i"><span class="dot" id="%s-d"></span><span class="lab">%s</span></div></div>'
                    % (nid, x, y, nid, nid, nid, label))
        nodes = node(bid + "-src", SX, 540, src["label"]) + "".join(node("%s-o%d" % (bid, i), MX, y, o["label"]) for i, (o, y) in enumerate(zip(outs, ys)))
        if res:
            nodes += node(bid + "-res", RX, 540, res["label"])
        title = '<div class="fx-title" id="%s-title">%s</div>' % (bid, em_spans(b["title"], b.get("em"))) if b.get("title") else ""
        inner = '<div class="cut"><div class="gridbg"></div>%s<svg class="fl-svg" viewBox="0 0 1920 1080">%s%s</svg>%s%s%s</div>' % (title, grad, paths, pulses, nodes, scene_label(bid, b, t_out))
        html_parts.append(host(bid, t_in, t_out, track, inner, anchor))
        if b.get("title"):
            js("tl.fromTo('#%s-title', { opacity: 0, y: 26 }, { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }, %.3f);" % (bid, t_in + 0.05))
        all_nodes = ["%s-src" % bid] + ["%s-o%d" % (bid, i) for i in range(n)] + (["%s-res" % bid] if res else [])
        for k, nid in enumerate(all_nodes):     # the map arrives dim, left to right
            js("tl.fromTo('#%s', { backgroundColor: 'rgba(255,255,255,0)', borderColor: 'rgba(255,255,255,0)' }, { backgroundColor: 'rgba(255,255,255,0.07)', borderColor: 'rgba(255,255,255,0.30)', duration: 0.42, ease: 'power2.out' }, %.3f);" % (nid, t_in + 0.1 + 0.05 * k))
            js("tl.fromTo('#%s-i', { opacity: 0 }, { opacity: 0.42, duration: 0.36 }, %.3f);" % (nid, t_in + 0.14 + 0.05 * k))
        def ring(nid, t, pay=False):     # the arrival ring: opens 10 px and fades over 0.65 s (the reference node response)
            js("tl.fromTo('#%s-r', { opacity: 0.8, scale: 1, borderColor: '%s' }, { opacity: 0, scale: 1.1, duration: 0.65, ease: 'power2.out', immediateRender: false }, %.3f);" % (nid, "#CD00EE" if pay else "#0AF0F0", t))
        def light(nid, t, pay=False):
            c, g = ("rgba(205,0,238,0.95)", "0 0 46px rgba(205,0,238,0.55)") if pay else ("rgba(10,240,240,0.95)", "0 0 40px rgba(10,240,240,0.5)")
            js("tl.to('#%s', { backgroundColor: 'rgba(255,255,255,0.16)', borderColor: '%s', boxShadow: '%s', duration: 0.25, ease: 'power2.out' }, %.3f);" % (nid, c, g, t))
            js("tl.to('#%s-i', { opacity: 1, duration: 0.25 }, %.3f);" % (nid, t))
            js("tl.to('#%s-d', { backgroundColor: '%s', duration: 0.25 }, %.3f);" % (nid, "#CD00EE" if pay else "#0AF0F0", t))
            ring(nid, t, pay)
        light(bid + "-src", s_at)
        arrivals = []
        for i, o in enumerate(outs):
            a = float(o.get("at", s_at + PD + 0.35 + 0.14 * i))
            js("along('#%s-p%d', '#%s-g%d', '#%s-u%d', %.3f, %.2f);" % (bid, i, bid, i, bid, i, a - PD, PD))
            light("%s-o%d" % (bid, i), a); arrivals.append(a)
        last = max(arrivals)
        if res:
            r = float(res.get("at", last + PD + 0.4 + 0.14 * (n - 1)))
            for i in range(n):
                js("along('#%s-P%d', '#%s-G%d', '#%s-U%d', %.3f, %.2f);" % (bid, i, bid, i, bid, i, r - PD - 0.14 * (n - 1 - i), PD))
            light(bid + "-res", r, pay=True); last = r
        w2 = last + 1.0       # second wave: packets only, along the already lit paths
        need = PD + 0.14 * (n - 1) + (PD + 0.14 * (n - 1) if res else 0)
        if b.get("repeat", True) and w2 + need < t_out - 0.3:
            for i in range(n):
                js("pulse('#%s-p%d', '#%s-u%d', %.3f, %.2f);" % (bid, i, bid, i, w2 + 0.14 * i, PD))
                ring("%s-o%d" % (bid, i), w2 + 0.14 * i + PD)
            if res:
                w3 = w2 + 0.14 * (n - 1) + PD
                for i in range(n):
                    js("pulse('#%s-P%d', '#%s-U%d', %.3f, %.2f);" % (bid, i, bid, i, w3 + 0.14 * i, PD))
                ring(bid + "-res", w3 + 0.14 * (n - 1) + PD, pay=True)
        transition(b, t_in, t_out)
    elif t == "dashzoom":
        # 31. dashboard zoom, full-frame: a REAL screenshot (YouTube Studio, a newsletter or analytics dashboard) rises in, the camera pushes to
        # one tile, cyan brackets find it, then the tile lifts out as a glass card: the number counts up, the trend draws.
        iw, ih = b.get("size") or image_size(os.path.join(OUT, b["src"]))
        f = b["focus"]; s0 = min(1640.0 / iw, 900.0 / ih); dw, dh = iw * s0, ih * s0; ox, oy = 960 - dw / 2, 548 - dh / 2
        rcx, rcy = ox + (f["x"] + f["w"] / 2.0) * s0, oy + (f["y"] + f["h"] / 2.0) * s0
        Z = max(1.2, min(760.0 / (f["w"] * s0), 430.0 / (f["h"] * s0), 3.2))
        TX, TY = 960 - Z * rcx, 530 - Z * rcy
        sx, sy, sw, sh = TX + Z * (ox + f["x"] * s0), TY + Z * (oy + f["y"] * s0), Z * f["w"] * s0, Z * f["h"] * s0
        card = b.get("card")
        card_html = ""
        if card:
            spark = [float(v) for v in card.get("spark", [])]
            spark_svg = ""
            if len(spark) > 1:
                lo, hi = min(spark), max(spark); rng = (hi - lo) or 1.0
                pts = " L".join("%.1f %.1f" % (i * 664.0 / (len(spark) - 1), 100 - (v - lo) / rng * 90) for i, v in enumerate(spark))
                spark_svg = '<svg class="dz-spark" viewBox="0 0 664 110"><path id="%s-spark" d="M%s"/></svg>' % (bid, pts)
            delta = '<div class="dz-delta">%s</div>' % card["delta"] if card.get("delta") else ""
            card_html = ('<div class="glass dz-card" id="%s-card"><div class="inner" id="%s-ci"><div class="dz-top"><div class="dz-lab">%s</div>%s</div>'
                         '<div class="dz-num" id="%s-num">%s</div>%s</div></div>'
                         % (bid, bid, card["label"], delta, bid, fmt_value(0, card.get("prefix", ""), card.get("suffix", ""), card.get("decimals", 0)), spark_svg))
        br = '<div class="dz-br" id="%s-br" style="left:%.0fpx;top:%.0fpx;width:%.0fpx;height:%.0fpx"><span class="a"></span><span class="b"></span><span class="c"></span><span class="d"></span></div>' % (bid, sx, sy, sw, sh)
        leads = ""
        if card:      # dashed leaders: the tile's corners to the lifted card's corners, so the eye follows the lift
            if sy + sh <= 330:
                pairs = [(sx, sy + sh, 580, 330), (sx + sw, sy + sh, 1340, 330)]
            else:
                pairs = [(sx, sy, 580, 750), (sx + sw, sy, 1340, 750)]
            leads = ('<svg class="dz-leads" id="%s-leads" viewBox="0 0 1920 1080">%s</svg>'
                     % (bid, "".join('<line x1="%.0f" y1="%.0f" x2="%d" y2="%d"/>' % pr for pr in pairs)))
        inner = ('<div class="cut"><div class="gridbg"></div><div class="dz-layer" id="%s-layer"><img class="dz-img" src="%s" alt="" style="left:%.0fpx;top:%.0fpx;width:%.0fpx;height:%.0fpx" /></div>'
                 '<div class="dz-dim" id="%s-dim"></div>%s%s%s%s</div>' % (bid, b["src"], ox, oy, dw, dh, bid, br, leads, card_html, scene_label(bid, b, t_out)))
        html_parts.append(host(bid, t_in, t_out, track, inner, anchor))
        tf = float(b.get("find_at", t_in + 0.9)); tlift = float(b.get("lift_at", tf + 1.6))
        js("tl.fromTo('#%s-layer', { x: 0, y: 50, scale: 1 }, { x: 0, y: 0, scale: 1, duration: 0.6, ease: 'power2.out' }, %.3f);" % (bid, t_in))
        js("tl.to('#%s-layer', { x: %.1f, y: %.1f, scale: %.3f, duration: 1.1, ease: 'power2.inOut' }, %.3f);" % (bid, TX, TY, Z, tf))
        js("tl.fromTo('#%s-br', { opacity: 0, scale: 1.08 }, { opacity: 1, scale: 1, duration: 0.4, ease: 'power3.out' }, %.3f);" % (bid, tf + 0.75))
        if card:
            js("tl.to('#%s-br', { opacity: 0, duration: 0.3, ease: 'power2.in' }, %.3f);" % (bid, tlift + 0.2))
            js("tl.fromTo('#%s-dim', { opacity: 0 }, { opacity: 1, duration: 0.6, ease: 'power2.out' }, %.3f);" % (bid, tlift))
            js("tl.fromTo('#%s-leads', { opacity: 0 }, { opacity: 0.6, duration: 0.6, ease: 'power2.out' }, %.3f);" % (bid, tlift + 0.1))
            js("tl.fromTo('#%s-card', { x: %.1f, y: %.1f, scale: %.3f, backgroundColor: 'rgba(255,255,255,0)', borderColor: 'rgba(255,255,255,0)', boxShadow: '0 24px 80px rgba(0,0,0,0)' },"
               " { x: 0, y: 0, scale: 1, backgroundColor: 'rgba(255,255,255,0.18)', borderColor: 'rgba(255,255,255,0.58)', boxShadow: '0 24px 80px rgba(0,0,0,0.38)', duration: 1.0, ease: 'power3.inOut' }, %.3f);"
               % (bid, sx + sw / 2 - 960, sy + sh / 2 - 540, max(0.15, min(sw / 760.0, sh / 420.0)), tlift))
            js("tl.fromTo('#%s-ci', { opacity: 0 }, { opacity: 1, duration: 0.45 }, %.3f);" % (bid, tlift + 0.35))
            js("countUp('#%s-num', %s, %.3f, 1.1, %s, %s, %d);" % (bid, card["value"], tlift + 0.5, json.dumps(card.get("prefix", "")), json.dumps(card.get("suffix", "")), int(card.get("decimals", 0))))
            if card.get("spark") and len(card["spark"]) > 1:
                js("(function(){ var p = document.getElementById('%s-spark'); var L = p.getTotalLength(); p.style.strokeDasharray = L; p.style.strokeDashoffset = L;"
                   " tl.to(p, { strokeDashoffset: 0, duration: 0.9, ease: 'power2.inOut' }, %.3f); })();" % (bid, tlift + 0.7))
        transition(b, t_in, t_out)
    elif t == "lens":
        # 32. glass focus, full-frame (tuned to a reference motion board): a table on one light glass card, every row out
        # of focus (a static blur, it never animates); a glass lens with a white rim glides to each row in `stops` on its word,
        # and only inside it the text is sharp, a touch larger, with a thin cyan/magenta fringe and the value in cyan. The lens
        # is a window: its sharp copy moves the opposite way, so the text inside lines up with the row under it.
        rows = b["rows"][:6]
        # the blurred rows, the two fringes and the sharp copy stack on purpose: each text block carries
        # data-layout-allow-overlap (the layout audit reads it on the block itself, never from a container), or
        # `hyperframes check` fails the scene with 12 content_overlap errors
        def rows_html(cls):
            return "".join('<div class="ln-row %s"><span data-layout-allow-overlap>%s</span><span class="v" data-layout-allow-overlap>%s</span></div>'
                           % (cls, r[0], r[1]) for r in rows)
        ttl = '<div class="ln-ttl">%s</div>' % b["title"] if b.get("title") else ""
        lens = ('<div class="ln-lens" id="%s-lens"><div class="ln-win" id="%s-win"><div class="ln-fr c">%s</div><div class="ln-fr m">%s</div><div class="ln-sharp">%s</div></div>'
                '<div class="ln-hl"></div></div>' % (bid, bid, rows_html(""), rows_html(""), rows_html("")))
        inner = ('<div class="cut"><div class="gridbg"></div><div class="glass ln-card" id="%s-glass"><div class="inner" id="%s-inner">%s'
                 '<div class="ln-rows"><div class="ln-base">%s</div>%s</div></div></div>%s</div>' % (bid, bid, ttl, rows_html(""), lens, scene_label(bid, b, t_out)))
        html_parts.append(host(bid, t_in, t_out, track, inner, anchor))
        js("glassIn('#%s-glass', %.3f, { y: 30 });" % (bid, t_in))
        js("tl.fromTo('#%s-inner', { opacity: 0 }, { opacity: 1, duration: 0.36 }, %.3f);" % (bid, t_in + 0.04))
        for k, (ri, ts) in enumerate(b.get("stops", [])):
            ri, ts = int(ri), float(ts); y = ri * 104 - 8
            if k == 0:
                js("tl.set('#%s-lens', { y: %d }, %.3f);" % (bid, y, t_in))
                js("tl.set('#%s-win', { y: %d }, %.3f);" % (bid, -y, t_in))
                js("tl.fromTo('#%s-lens', { opacity: 0, scale: 0.97 }, { opacity: 1, scale: 1, duration: 0.4, ease: 'power2.out' }, %.3f);" % (bid, ts - 0.15))
            else:     # the glide: lens and window move together, opposite ways, one ease
                js("tl.to('#%s-lens', { y: %d, duration: 0.6, ease: 'power3.inOut' }, %.3f);" % (bid, y, ts - 0.3))
                js("tl.to('#%s-win', { y: %d, duration: 0.6, ease: 'power3.inOut' }, %.3f);" % (bid, -y, ts - 0.3))
        transition(b, t_in, t_out)
    elif t == "search":
        # 33. search then results, full-frame: a glass search bar, the query types in character by character (typing is the
        # one confirmed sound, "sound": true), then result rows drop in one by one, each with a colour tile or a logo.
        q = b["query"]; cps = float(b.get("cps", 16)); ta = float(b.get("type_at", t_in + 0.85))
        tints = {"cyan": "var(--cyan)", "amber": "var(--amber)", "magenta": "var(--magenta)", "white": "#fff", "blue": "var(--blue)"}
        rows = ""
        for i, r in enumerate(b.get("results", [])[:4]):
            sq = ('<div class="sr-sq" style="background:#fff"><img src="%s" alt="" /></div>' % r["logo"]) if r.get("logo") else '<div class="sr-sq" style="background:%s"></div>' % tints.get(r.get("color", "cyan"), r.get("color", "var(--cyan)"))
            rows += ('<div class="glass sr-row" id="%s-r%d"><div class="inner" id="%s-ri%d">%s<div><div class="sr-t">%s</div>%s</div></div></div>'
                     % (bid, i, bid, i, sq, r["title"], '<div class="sr-s">%s</div>' % r["sub"] if r.get("sub") else ""))
        mag = '<svg viewBox="0 0 50 50"><circle class="ic" cx="21" cy="21" r="14"/><path class="ic" d="M31 31 L44 44"/></svg>'
        inner = ('<div class="cut"><div class="gridbg"></div><div class="sr"><div class="glass sr-bar" id="%s-bar">%s<span class="sr-ph" id="%s-ph">%s</span>'
                 '<span class="sr-q" id="%s-q"></span><span class="sr-caret" id="%s-caret"></span></div><div class="sr-res">%s</div></div>%s</div>'
                 % (bid, mag, bid, b.get("placeholder", "Search"), bid, bid, rows, scene_label(bid, b, t_out)))
        html_parts.append(host(bid, t_in, t_out, track, inner, anchor))
        js("glassIn('#%s-bar', %.3f, { y: 20 });" % (bid, t_in))
        js("tl.fromTo('#%s-bar', { width: 520 }, { width: 1200, duration: 0.55, ease: 'power3.inOut' }, %.3f);" % (bid, t_in + 0.2))   # the pill opens, then it types (the reference order)
        js("tl.fromTo('#%s-ph', { opacity: 0 }, { opacity: 1, duration: 0.3 }, %.3f);" % (bid, t_in + 0.1))
        js("tl.set('#%s-ph', { opacity: 0 }, %.3f);" % (bid, ta))
        js("tl.set('#%s-caret', { opacity: 1 }, %.3f);" % (bid, ta))
        # typing from one proxy (a tl.set per letter leaves the first letter behind on a backward seek; this reverts cleanly)
        js("(function(){ var el = document.getElementById('%s-q'), Q = %s, o = { n: 0 }; var put = function () { el.textContent = Q.slice(0, Math.floor(o.n)); };"
           " put(); tl.fromTo(o, { n: 0 }, { n: Q.length + 0.999, duration: %.3f, ease: 'none', immediateRender: false, onUpdate: put }, %.3f); })();" % (bid, json.dumps(q), len(q) / cps, ta))
        t_done = ta + len(q) / cps
        if b.get("sound"):
            audio_parts.append('    <audio id="sfx-typing-%s" src="sfx/typing.mp3" data-start="%.3f" data-duration="%.2f" data-track-index="%d" data-volume="0.22"></audio>\n' % (bid, ta, len(q) / cps + 0.1, audio_track))
            audio_track += 1
        for i, r in enumerate(b.get("results", [])[:4]):
            a = float(r.get("at", t_done + 0.35 + 0.22 * i))
            js("glassIn('#%s-r%d', %.3f, { y: 24 });" % (bid, i, a))
            js("tl.fromTo('#%s-ri%d', { opacity: 0 }, { opacity: 1, duration: 0.36 }, %.3f);" % (bid, i, a + 0.04))
        transition(b, t_in, t_out)
    elif t == "dock":
        # 34. magnetic dock, full-frame: the tools as a glass dock; the oversized cursor walks to each on its word, the icon under
        # it swells (neighbours make room) and a white tooltip names it. The whole scene is one pure function of time.
        items = b["items"][:7]; n = len(items)
        xs = [960 + (i - (n - 1) / 2.0) * 148 for i in range(n)]
        icons = "".join('<div class="dk-ic" id="%s-i%d"><img src="%s" alt="" /></div>' % (bid, i, it[0]) for i, it in enumerate(items))
        title = '<div class="fx-title" id="%s-title" style="top:250px">%s</div>' % (bid, em_spans(b["title"], b.get("em"))) if b.get("title") else ""
        inner = ('<div class="cut"><div class="gridbg"></div>%s<div class="glass dk-bar" id="%s-bar" style="width:%dpx"></div>'
                 '<svg class="dk-svg" viewBox="0 0 1920 1080"><path id="%s-curve" d=""/><circle id="%s-run" r="5" cx="0" cy="718"/></svg>%s<div class="dk-tip" id="%s-tip"></div>%s%s</div>'
                 % (title, bid, n * 148 + 200, bid, bid, icons, bid, CURSOR_SVG % (bid + "-cur"), scene_label(bid, b, t_out)))
        html_parts.append(host(bid, t_in, t_out, track, inner, anchor))
        if b.get("title"):
            js("tl.fromTo('#%s-title', { opacity: 0, y: 26 }, { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }, %.3f);" % (bid, t_in + 0.05))
        js("glassIn('#%s-bar', %.3f, { y: 30 });" % (bid, t_in + 0.05))
        js("tl.fromTo('#host-%s .dk-ic', { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.45, ease: 'power2.out', stagger: 0.05 }, %.3f);" % (bid, t_in + 0.15))
        keys = [[t_in, xs[-1] + 420, 1180]]          # the cursor enters from below right, then walks icon to icon
        for i, it in enumerate(items):
            ti = float(it[2]); keys.append([ti - 0.5, keys[-1][1], keys[-1][2]]); keys.append([ti, xs[i], 636])
        keys.append([t_out, keys[-1][1], keys[-1][2]])
        js("""(function(){ var X = %s, K = %s, L = %s, T = %s, n = X.length;
          var ic = [], tip = document.getElementById('%s-tip'), cur = document.getElementById('%s-cur'), cv = document.getElementById('%s-curve'), rn = document.getElementById('%s-run');
          for (var i = 0; i < n; i++) ic.push(document.getElementById('%s-i' + i));
          var ease = function (p) { return p < .5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2; };
          var at = function (t) { if (t <= K[0][0]) return [K[0][1], K[0][2]]; for (var k = 1; k < K.length; k++) { if (t <= K[k][0]) { var a = K[k - 1], b = K[k];
              var p = b[0] > a[0] ? ease((t - a[0]) / (b[0] - a[0])) : 1; return [a[1] + (b[1] - a[1]) * p, a[2] + (b[2] - a[2]) * p]; } } var z = K[K.length - 1]; return [z[1], z[2]]; };
          var frame = function (t) { var c = at(t), on = Math.max(0, Math.min(1, (1100 - c[1]) / 300)), s = [], ex = [], best = 0;
            for (var i = 0; i < n; i++) { var d = (c[0] - X[i]) / 140; s.push(1 + 0.75 * on * Math.exp(-d * d)); ex.push((s[i] - 1) * 114);
              if (Math.abs(c[0] - X[i]) < Math.abs(c[0] - X[best])) best = i; }
            for (var i = 0; i < n; i++) { var sh = 0; for (var j = 0; j < n; j++) { if (j < i) sh -= ex[j] / 2; if (j > i) sh += ex[j] / 2; }
              ic[i].style.left = (X[i] - sh) + 'px'; ic[i].style.scale = s[i]; }
            cur.style.transform = 'translate(' + (c[0] - 28) + 'px,' + (c[1] - 19) + 'px)';
            var show = on > 0.6 && t >= T[0] - 0.15;
            tip.style.opacity = show ? 1 : 0; tip.textContent = L[best];
            var sh2 = 0; for (var j = 0; j < n; j++) { if (j < best) sh2 -= ex[j] / 2; if (j > best) sh2 += ex[j] / 2; }
            tip.style.left = (X[best] - sh2) + 'px'; tip.style.top = (692 - 114 * s[best] - 20) + 'px';
            var L0 = X[0] - 110, L1 = X[n - 1] + 110, by = 452, cx = c[0], hh = 110 * on;      // the dotted curve bulges over the cursor
            cv.setAttribute('d', 'M' + L0 + ',' + by + ' C' + (cx - 90) + ',' + by + ' ' + (cx - 60) + ',' + (by - hh) + ' ' + cx + ',' + (by - hh) + ' C' + (cx + 60) + ',' + (by - hh) + ' ' + (cx + 90) + ',' + by + ' ' + L1 + ',' + by);
            cv.style.opacity = 0.55 * on; rn.setAttribute('cx', X[best] - sh2); rn.style.opacity = 0.8 * on; };
          var drv = { t: %.3f }; frame(drv.t);
          tl.fromTo(drv, { t: %.3f }, { t: %.3f, duration: %.3f, ease: 'none', immediateRender: false, onUpdate: function () { frame(drv.t); } }, %.3f); })();"""
           % (json.dumps([round(x, 1) for x in xs]), json.dumps([[round(k[0], 3), round(k[1], 1), round(k[2], 1)] for k in keys]),
              json.dumps([it[1] for it in items]), json.dumps([float(it[2]) for it in items]), bid, bid, bid, bid, bid, t_in, t_in, t_out, t_out - t_in, t_in))
        transition(b, t_in, t_out)
    elif t == "masktitle":
        # 35. masked title, full-frame chapter card (a "masked type" reveal): the word stands as an
        # outline; a solid fill rises inside the letters from the bottom (clipped by the letter shapes) with a cyan edge line
        # and its handle riding the fill, then the sub line rises from behind a mask over a thin rule. For section openers.
        size = int(b.get("size", 220)); word = b["text"]
        est = len(word) * size * 0.56; x0, x1 = 960 - est / 2 - 60, 960 + est / 2 + 60
        base = 250; top_y, bot_y = base - int(size * 0.80), base + int(size * 0.24)
        fill = b.get("fill", "#FFFFFF")
        svg = ('<svg class="mt-svg" viewBox="0 0 1920 330"><defs><clipPath id="%s-clip"><text x="960" y="%d" text-anchor="middle" class="mt-t" style="font-size:%dpx">%s</text></clipPath></defs>'
               '<text x="960" y="%d" text-anchor="middle" class="mt-t mt-o" style="font-size:%dpx">%s</text>'
               '<g clip-path="url(#%s-clip)"><rect id="%s-fill" x="0" y="%d" width="1920" height="330" fill="%s"/></g>'
               '<g id="%s-edge"><line x1="%.0f" y1="%d" x2="%.0f" y2="%d" class="mt-edge"/><rect x="%.0f" y="%d" width="16" height="16" rx="4" class="mt-hd"/></g></svg>'
               % (bid, base, size, word, base, size, word, bid, bid, bot_y, fill, bid, x0, bot_y, x1, bot_y, x1 - 8, bot_y - 8))
        eye = '<div class="mt-eye" id="%s-eye">%s</div>' % (bid, b["eyebrow"]) if b.get("eyebrow") else ""
        sub = ('<div class="mt-subm"><div class="mt-sub" id="%s-sub">%s</div></div><div class="mt-rule2"></div>' % (bid, em_spans(b["sub"], b.get("sub_em")))) if b.get("sub") else ""
        inner = '<div class="cut"><div class="gridbg"></div><div class="mt">%s%s%s</div></div>' % (eye, svg, sub)
        html_parts.append(host(bid, t_in, t_out, track, inner, anchor))
        if b.get("eyebrow"):
            js("tl.fromTo('#%s-eye', { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }, %.3f);" % (bid, t_in + 0.05))
        rise = 1.5
        js("tl.fromTo('#%s-edge', { opacity: 0 }, { opacity: 1, duration: 0.12 }, %.3f);" % (bid, t_in + 0.15))
        js("tl.fromTo('#%s-fill', { attr: { y: %d } }, { attr: { y: %d }, duration: %.2f, ease: 'power3.inOut' }, %.3f);" % (bid, bot_y, top_y, rise, t_in + 0.2))
        js("tl.fromTo('#%s-edge', { y: 0 }, { y: %d, duration: %.2f, ease: 'power3.inOut' }, %.3f);" % (bid, top_y - bot_y, rise, t_in + 0.2))
        js("tl.to('#%s-edge', { opacity: 0, duration: 0.25 }, %.3f);" % (bid, t_in + 0.2 + rise))
        if b.get("sub"):
            js("tl.fromTo('#%s-sub', { yPercent: 105 }, { yPercent: 0, duration: 0.9, ease: 'power3.inOut' }, %.3f);" % (bid, t_in + 0.2 + rise * 0.45))
        transition(b, t_in, t_out)
    elif t == "player":
        # 36. button to player, over the footage at tr/tl: a "watch this" glass pill arrives, then grows into a small player of
        # the video named on camera (its real thumbnail, title, running time, the scrubber moving). The next-video pill (22), upgraded.
        pos = POS.get(b.get("pos", "tr"), POS["tr"])
        total = float(b.get("length", 42)); p0 = float(b.get("progress", 0.3))
        mm = lambda v: "%d:%02d" % (int(v) // 60, int(v) % 60)
        side = "left" if b.get("pos", "tr") == "tl" else "right"
        inner = ('<div class="glass pv" id="%s-glass" style="%s"><div class="pill" id="%s-pill"><span class="tri"></span>%s</div>'
                 '<div class="card" id="%s-card"><div class="thumb"><img src="%s" alt="" /></div>'
                 '<div class="meta"><div class="ttl">%s</div><div class="tm" id="%s-tm">%s / %s</div></div>'
                 '<div class="track"><div class="fillx" id="%s-fill"></div><div class="knob" id="%s-knob"></div></div></div>'
                 '<div class="pv-fly" id="%s-fly" style="%s:254px"><div class="disc" id="%s-disc"></div><span class="ptri" id="%s-ptri"></span><span class="pz" id="%s-pz"><i></i><i></i></span></div></div>'
                 % (bid, pos, bid, b.get("label", "Watch this next"), bid, b["thumb"], b["title"], bid, mm(total * p0), mm(total), bid, bid, bid, side, bid, bid, bid))
        html_parts.append(host(bid, t_in, t_out, track, inner, anchor))
        tm = float(b.get("morph_at", t_in + 1.2))
        js("glassIn('#%s-glass', %.3f, { y: -20 });" % (bid, t_in))
        js("tl.fromTo('#%s-pill', { opacity: 0 }, { opacity: 1, duration: 0.36 }, %.3f);" % (bid, t_in + 0.04))
        GR = 1.1       # (tuned to the reference motion) the shell grows on one slow cubic in-out; the pill's play icon travels
                       # into the player, gains its disc on the way, and turns to pause once it plays
        js("tl.to('#%s-pill', { opacity: 0, duration: 0.2, ease: 'power2.in' }, %.3f);" % (bid, tm))
        js("tl.to('#%s-glass', { width: 600, height: 444, borderRadius: 28, duration: %.2f, ease: 'power3.inOut' }, %.3f);" % (bid, GR, tm))
        js("tl.set('#%s-fly', { x: %d, y: -133, scale: 0.67 }, %.3f);" % (bid, 44 if side == "right" else -256, t_in))
        js("tl.fromTo('#%s-fly', { opacity: 0 }, { opacity: 1, duration: 0.12 }, %.3f);" % (bid, tm))
        js("tl.to('#%s-fly', { x: 0, y: 0, scale: 1, duration: %.2f, ease: 'power3.inOut' }, %.3f);" % (bid, GR, tm))
        js("tl.fromTo('#%s-disc', { scale: 0 }, { scale: 1, duration: 0.55, ease: 'power2.out' }, %.3f);" % (bid, tm + 0.35 * GR))
        js("tl.fromTo('#%s-card', { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.45, ease: 'power2.out' }, %.3f);" % (bid, tm + 0.5 * GR))
        js("tl.to('#%s-ptri', { opacity: 0, duration: 0.15 }, %.3f);" % (bid, tm + GR + 0.35))
        js("tl.fromTo('#%s-pz', { opacity: 0 }, { opacity: 1, duration: 0.15 }, %.3f);" % (bid, tm + GR + 0.35))
        run = max(0.5, t_out - tm - GR - 0.5)
        js("""(function(){ var o = { p: %.3f }, f = document.getElementById('%s-fill'), k = document.getElementById('%s-knob'), tm = document.getElementById('%s-tm');
          var put = function () { f.style.transform = 'scaleX(' + o.p + ')'; k.style.left = (o.p * 100) + '%%'; var v = o.p * %.3f;
            tm.textContent = Math.floor(v / 60) + ':' + ('0' + Math.floor(v %% 60)).slice(-2) + ' / %s'; };
          put(); tl.fromTo(o, { p: %.3f }, { p: %.3f, duration: %.3f, ease: 'none', immediateRender: false, onUpdate: put }, %.3f); })();"""
           % (p0, bid, bid, bid, total, mm(total), p0, min(1.0, p0 + run / total), run, tm + GR + 0.35))
        js("tl.to('#%s-card, #%s-fly', { opacity: 0, duration: 0.28, ease: 'power2.in' }, %.3f);" % (bid, bid, t_out - 0.38))
        js("glassOut('#%s-glass', %.3f, 0.33);" % (bid, t_out - 0.34))
        js("tl.set('#%s-card, #%s-fly', { opacity: 0 }, %.3f);" % (bid, bid, t_out - 0.10))
    elif t == "image":
        # 37. image reveal, full-frame: an image (a photo, a screenshot, a public-domain still) behind dark vertical slats that
        # open left to right on the word, then a slow push. "close": true shuts the slats again before the cut back.
        full = b.get("frame", "card") == "full"; lab = bool(b.get("label")) and not full
        W = 1920 if full else (1280 if lab else 1500); N = int(b.get("slats", 7)); sw = W / float(N)
        slats = "".join('<div class="im-slat" style="left:%.1fpx;width:%.1fpx"></div>' % (i * sw, sw + 1.5) for i in range(N))
        inner = ('<div class="cut"><div class="gridbg"></div><div class="im-frame%s"><img id="%s-img" src="%s" alt="" />%s</div>%s</div>'
                 % (" full" if full else (" lab" if lab else ""), bid, b["src"], slats, scene_label(bid, b, t_out)))
        html_parts.append(host(bid, t_in, t_out, track, inner, anchor))
        tr_ = float(b.get("reveal_at", t_in + 0.35))
        js("tl.fromTo('#host-%s .im-slat', { scaleX: 1 }, { scaleX: 0, duration: 1.1, ease: 'power3.inOut', stagger: 0.12 }, %.3f);" % (bid, tr_))
        js("tl.fromTo('#%s-img', { scale: 1.0 }, { scale: 1.06, duration: %.3f, ease: 'none' }, %.3f);" % (bid, max(0.5, t_out - tr_), tr_))
        if b.get("close"):
            js("tl.to('#host-%s .im-slat', { scaleX: 1, duration: 0.6, ease: 'power3.inOut', stagger: 0.06 }, %.3f);" % (bid, t_out - 1.0))
        transition(b, t_in, t_out)
    elif t == "layers":
        # 38. exploded layers, full-frame: one flat card (the app), then the stack tilts into depth and separates into its named
        # layers (Interface, Logic, Data...), labels arriving on each; a slow orbit holds it. The tilt settles, nothing flips.
        lays = b["layers"][:4]; n = len(lays)
        def fake(k):      # a drawn layer when there is no screenshot: an interface, a logic graph, a data table
            if k == 0:
                return ('background:#f4f6fa', '<div class="blk" style="left:0;top:0;right:0;height:64px;border-radius:0;background:#1a1e2b"></div>'
                        '<div class="blk" style="left:56px;top:120px;width:420px;height:40px;background:#c9d0db"></div>'
                        '<div class="blk" style="left:56px;top:190px;width:640px;height:22px;background:#dde2ea"></div>'
                        '<div class="blk" style="left:56px;top:230px;width:560px;height:22px;background:#dde2ea"></div>'
                        '<div class="blk" style="left:56px;top:300px;width:360px;height:180px;background:#e6eaf0"></div>'
                        '<div class="blk" style="left:460px;top:300px;width:360px;height:180px;background:#e6eaf0"></div>'
                        '<div class="blk" style="left:56px;top:500px;width:200px;height:0"></div>'
                        '<div class="blk" style="right:60px;top:120px;width:190px;height:56px;border-radius:28px;background:#0AF0F0"></div>')
            if k == 1:
                boxes = "".join('<div class="blk" style="left:%dpx;top:%dpx;width:200px;height:80px;border:3px solid rgba(10,240,240,.8);background:rgba(10,240,240,.08)"></div>' % (x, y)
                                for x, y in [(70, 90), (340, 240), (610, 90), (610, 390), (70, 390)])
                wires = "".join('<div class="blk" style="left:%dpx;top:%dpx;width:%dpx;height:3px;border-radius:2px;background:rgba(255,255,255,.35)"></div>' % (x, y, w)
                                for x, y, w in [(270, 128, 340), (270, 428, 340), (440, 320, 3)])
                return ('background:#1b2030', boxes + wires)
            rows = "".join('<div class="blk" style="left:56px;right:56px;top:%dpx;height:34px;border-radius:6px;background:rgba(255,255,255,%.2f)"></div>' % (80 + i * 62, 0.10 if i % 2 else 0.05) for i in range(7))
            return ('background:#10131c', rows)
        ws = ""
        for k in reversed(range(n)):
            L = lays[k]
            if L.get("src"):
                card = '<div class="ly-card"><img src="%s" alt="" /></div>' % L["src"]
            else:
                bg, blks = fake(k % 3); card = '<div class="ly-card" style="%s">%s</div>' % (bg, blks)
            ws += '<div class="ly-w" id="%s-w%d">%s<div class="ly-lab" id="%s-l%d" style="top:%dpx"><span class="d"></span>%s</div></div>' % (bid, k, card, bid, k, -250 + 200 * k, L["label"])
        title = '<div class="fx-title" id="%s-title" style="top:70px">%s</div>' % (bid, em_spans(b["title"], b.get("em"))) if b.get("title") else ""
        inner = '<div class="cut"><div class="gridbg"></div>%s<div class="ly-stage"><div class="ly-rig" id="%s-rig">%s</div></div>%s</div>' % (title, bid, ws, scene_label(bid, b, t_out))
        html_parts.append(host(bid, t_in, t_out, track, inner, anchor))
        if b.get("title"):
            js("tl.fromTo('#%s-title', { opacity: 0, y: 26 }, { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }, %.3f);" % (bid, t_in + 0.05))
        tsp = float(b.get("split_at", t_in + 1.0))
        js("tl.fromTo('#%s-rig', { y: 120, opacity: 0, rotationY: 0, rotationX: 0 }, { y: 0, opacity: 1, duration: 0.6, ease: 'power2.out' }, %.3f);" % (bid, t_in))
        js("tl.to('#%s-rig', { rotationY: -30, rotationX: 16, duration: 1.4, ease: 'power3.inOut' }, %.3f);" % (bid, tsp))
        for k in range(n):
            js("tl.fromTo('#%s-w%d', { x: 0, y: 0, z: 0 }, { x: %d, y: %d, z: %d, duration: 1.4, ease: 'power3.inOut', immediateRender: false }, %.3f);" % (bid, k, 80 * k, -46 * k, -230 * k, tsp + 0.22 * k))
            js("tl.fromTo('#%s-l%d', { opacity: 0, x: -12 }, { opacity: 1, x: 0, duration: 0.4, ease: 'power2.out' }, %.3f);" % (bid, k, tsp + 1.0 + 0.2 * k))
        js("tl.to('#%s-rig', { rotationY: -21, duration: %.3f, ease: 'power1.inOut' }, %.3f);" % (bid, max(0.5, t_out - tsp - 1.4), tsp + 1.4))
        transition(b, t_in, t_out)
    # ---- approved formats (world, deck, pills, chat, doc, clip), rebuilt on the house tokens ----
    elif t == "world":
        # 39. world, full-frame on the wash: a dark stage as ONE canvas. Nodes arrive on their words, links draw between
        # them, amber alert pins land around a node, and a camera moves over all of it: push in on one node, pull back to show
        # what it is wired to, travel to the next. cam: [[t, cx, cy, zoom(, dur(, ease))]] = the canvas point at frame centre
        # and the zoom (1 = the 1920x1080 home frame); the first entry is where the camera sits at the cut in.
        nodes = b.get("nodes", [])
        geo = {}
        RGB = {"cyan": "10,240,240", "amber": "255,185,4", "magenta": "205,0,238"}
        nodes_html, links_svg, rings_svg, dots_html, alerts_html, back_html = "", "", "", "", "", ""
        node_js = []
        for i, nd in enumerate(nodes):
            nid, k = str(nd.get("id", i)), nd.get("kind", "card")
            if "polar" in nd:
                pcx, pcy, pr, pa = [float(v) for v in nd["polar"]]
                x, y = pcx + pr * math.cos(math.radians(pa)), pcy + pr * math.sin(math.radians(pa))
            else:
                x, y = float(nd["x"]), float(nd["y"])
            hw, hh, rnd = {"card": (nd.get("w", 300) / 2.0, nd.get("h", 300) / 2.0, False), "orb": (130, 130, True), "hex": (100, 100, True),
                           "stat": (300, 150, False), "text": (40, 40, False), "img": (nd.get("w", 640) / 2.0, nd.get("h", 360) / 2.0, False),
                           "pill": ((len(nd.get("label", "")) * 22 + 72 + (60 if nd.get("icon") else 0)) / 2.0, 46, False)}.get(k, (150, 150, False))
            geo[nid] = (x, y, hw, hh, rnd)
            eid = "%s-n%d" % (bid, i)
            at = float(nd.get("at", t_in))
            a_attr = (' data-at="%.3f"%s' % (at, attr_anchor(nd["anchor"]))) if nd.get("anchor") else ""
            style = "left:%.0fpx;top:%.0fpx" % (x, y)
            lab = '<div class="wd-lab">%s</div>' % nd["label"] if nd.get("label") else ""
            sub = '<div class="wd-sub">%s</div>' % nd["sub"] if nd.get("sub") else ""
            ic = icon_svg(nd.get("icon"))
            glass = k in ("card", "pill", "orb", "stat")
            if k == "card":
                if nd.get("w") or nd.get("h"):
                    style += ";width:%dpx;height:%dpx" % (nd.get("w", 300), nd.get("h", 300))
                no = '<div class="wd-no">%s</div>' % nd["no"] if nd.get("no") else ""
                body = no + ic + lab + sub
            elif k == "pill":
                body = ic + lab
            elif k == "orb":
                body = ic + lab
            elif k == "stat":
                sv = fmt_value(nd.get("value", 0), nd.get("prefix", ""), nd.get("suffix", ""), nd.get("decimals", 0))
                body = ('<div class="top">%s%s</div><div class="v" id="%s-v">%s</div><div class="track"><div class="fill" id="%s-f"></div></div>'
                        % (icon_svg(nd.get("icon")), lab, eid, sv, eid))
            if glass:
                nodes_html += '<div class="glass wd-n wd-%s" id="%s" style="%s;visibility:hidden"%s><div class="inner" id="%s-i">%s</div></div>' % (k, eid, style, a_attr, eid, body)
                node_js.append("tl.set('#%s', { visibility: 'inherit' }, %.3f);" % (eid, at))   # a glass that has not arrived must not blur what is behind it ('inherit', never 'visible': a visible child outlives its hidden host)
                node_js.append("glassIn('#%s', %.3f, { y: 18 });" % (eid, at))
                node_js.append("tl.fromTo('#%s-i', { opacity: 0 }, { opacity: 1, duration: 0.36 }, %.3f);" % (eid, at + 0.04))
            elif k == "hex":
                pts = " ".join("%.1f,%.1f" % (100 + 96 * math.cos(math.radians(a)), 100 + 96 * math.sin(math.radians(a))) for a in range(-90, 270, 60))
                nodes_html += ('<div class="wd-n wd-hex" id="%s" style="%s;height:200px"%s><svg class="hx" viewBox="0 0 200 200"><polygon id="%s-poly" points="%s"/></svg>%s%s</div>'
                               % (eid, style, a_attr, eid, pts, ic, lab))
            elif k == "text":
                nodes_html += ('<div class="wd-n wd-text" id="%s" style="%s;font-size:%dpx"%s>%s</div>' % (eid, style, int(nd.get("size", 160)), a_attr, nd.get("label", "")))
            elif k == "img":
                nodes_html += ('<div class="wd-n wd-img" id="%s" style="%s;width:%dpx;height:%dpx"%s><img src="%s" alt="" /></div>'
                               % (eid, style, int(nd.get("w", 640)), int(nd.get("h", 360)), a_attr, nd["src"]))
            else:
                raise SystemExit("world node kind %r: card | pill | orb | hex | stat | text | img" % k)
            if not glass:
                node_js.append("tl.fromTo('#%s', { opacity: 0, scale: 0.9 }, { opacity: 1, scale: 1, duration: 0.4, ease: 'power2.out' }, %.3f);" % (eid, at))
            if k == "stat":
                node_js.append("countUp('#%s-v', %s, %.3f, 1.1, %s, %s, %d);" % (eid, nd.get("value", 0), at + 0.3, json.dumps(nd.get("prefix", "")), json.dumps(nd.get("suffix", "")), int(nd.get("decimals", 0))))
                node_js.append("tl.to('#%s-f', { scaleX: %.3f, duration: 1.1, ease: 'power2.out' }, %.3f);" % (eid, float(nd.get("bar", 0.5)), at + 0.3))
                if nd.get("to"):       # [value, t, bar]: the number moves on (51 -> 93) and the bar with it
                    v2, t2 = nd["to"][0], float(nd["to"][1])
                    if t2 < at + 1.45:        # the first count and bar take 1.1 s from at + 0.3: never two tweens on one property
                        print("WARN world %s: stat 'to' at %.2f moved to %.2f, after the first count lands" % (bid, t2, at + 1.45)); t2 = at + 1.45
                    node_js.append("countFromTo('#%s-v', %s, %s, %.3f, 1.0, %s, %s, %d);" % (eid, nd.get("value", 0), v2, t2, json.dumps(nd.get("prefix", "")), json.dumps(nd.get("suffix", "")), int(nd.get("decimals", 0))))
                    if len(nd["to"]) > 2:
                        node_js.append("tl.to('#%s-f', { scaleX: %.3f, duration: 1.0, ease: 'power2.out' }, %.3f);" % (eid, float(nd["to"][2]), t2))
            if nd.get("lit") is not None:     # the node turns on: cyan border and glow (amber for a risk, magenta for the payoff)
                tl_ = max(float(nd["lit"]), at + 0.45)
                c = RGB.get(nd.get("lit_color", "cyan"), RGB["cyan"])
                if glass:
                    node_js.append("tl.to('#%s', { borderColor: 'rgba(%s,0.95)', boxShadow: '0 0 60px rgba(%s,0.45), 0 24px 80px rgba(0,0,0,0.38)', duration: 0.45, ease: 'power2.out' }, %.3f);" % (eid, c, c, tl_))
                elif k == "hex":
                    node_js.append("tl.to('#%s-poly', { stroke: 'rgba(%s,1)', fill: 'rgba(%s,0.16)', duration: 0.45, ease: 'power2.out' }, %.3f);" % (eid, c, c, tl_))
                elif k == "text":
                    node_js.append("tl.to('#%s', { color: 'rgb(%s)', duration: 0.45, ease: 'power2.out' }, %.3f);" % (eid, c, tl_))
                if ic:
                    node_js.append("tl.to('#%s .ic', { stroke: 'rgb(%s)', duration: 0.45, ease: 'power2.out' }, %.3f);" % (eid, c, tl_))
            if nd.get("dim") is not None:     # context .56 (spent .33): what is drawn stays, dimmed but legible
                dv = nd["dim"] if isinstance(nd["dim"], list) else [nd["dim"], 0.56]
                node_js.append("tl.to('#%s%s', { opacity: %.2f, duration: 0.4, ease: 'power2.out' }, %.3f);" % (eid, "-i" if glass else "", float(dv[1]), float(dv[0])))
            if nd.get("alerts"):              # amber pins land around the node: threats, errors, open risks
                al = nd["alerts"]; na = int(al.get("n", 1)); R = max(hw, hh) + 46
                angs = [-45] if al.get("layout") == "corner" or na == 1 else [-60 + j * 360.0 / na for j in range(na)]
                for j, ag in enumerate(angs[:na]):
                    ax, ay = (x + hw + 4, y - hh - 4) if al.get("layout") == "corner" else (x + R * math.cos(math.radians(ag)), y + R * math.sin(math.radians(ag)))
                    alerts_html += '<div class="wd-alert" id="%s-a%d" style="left:%.0fpx;top:%.0fpx">!</div>' % (eid, j, ax, ay)
                node_js.append("tl.fromTo('#host-%s [id^=\"%s-a\"]', { opacity: 0, scale: 0.3 }, { opacity: 1, scale: 1, duration: 0.3, ease: 'power2.out', stagger: 0.12 }, %.3f);" % (bid, eid, float(al["at"])))
        for j, ln in enumerate(b.get("links", [])):
            (x1, y1, w1, h1, r1), (x2, y2, w2, h2, r2) = geo[str(ln["from"])], geo[str(ln["to"])]
            dx, dy = x2 - x1, y2 - y1; L = math.hypot(dx, dy) or 1.0; ux, uy = dx / L, dy / L
            def trim(w, h, rnd):      # distance from a node centre to its edge along the link, plus a small gap
                if rnd:
                    return w + 14
                return min(w / abs(ux) if ux else 1e9, h / abs(uy) if uy else 1e9) + 14
            d1, d2 = trim(w1, h1, r1), trim(w2, h2, r2)
            if d1 + d2 >= L:
                raise SystemExit("world link %s -> %s: the nodes overlap" % (ln["from"], ln["to"]))
            links_svg += ('<line class="wd-link%s" id="%s-l%d" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"%s/>'
                          % (" dash" if ln.get("dash") else "", bid, j, x1 + ux * d1, y1 + uy * d1, x2 - ux * d2, y2 - uy * d2,
                             ' style="stroke:rgb(%s)"' % RGB[ln["color"]] if ln.get("color") in RGB else ""))
            la = float(ln.get("at", t_in))
            if ln.get("dash"):
                node_js.append("tl.to('#%s-l%d', { opacity: 0.85, duration: 0.4, ease: 'power2.out' }, %.3f);" % (bid, j, la))
            else:
                node_js.append("(function(){ var l = document.getElementById('%s-l%d'); var L = l.getTotalLength(); l.style.strokeDasharray = L; l.style.strokeDashoffset = L;"
                               " tl.to(l, { strokeDashoffset: 0, duration: 0.5, ease: 'power2.out' }, %.3f); })();" % (bid, j, la))
            if ln.get("run"):             # a light runs the link once it is drawn: something travels from A to B
                dots_html += '<div class="wd-dot" id="%s-d%d"></div>' % (bid, j)
                node_js.append("pulse('#%s-l%d', '#%s-d%d', %.3f, 0.8);" % (bid, j, bid, j, la + 0.45))
        for j, rg in enumerate(b.get("rings", [])):
            for q, r in enumerate(rg.get("r", [])):
                rings_svg += ('<circle class="wd-ring" id="%s-r%d-%d" cx="%.0f" cy="%.0f" r="%.0f" transform="rotate(-90 %.0f %.0f)"/>'
                              % (bid, j, q, rg["x"], rg["y"], r, rg["x"], rg["y"]))
                node_js.append("(function(){ var c = document.getElementById('%s-r%d-%d'); var L = 2 * Math.PI * %.1f; c.style.strokeDasharray = L; c.style.strokeDashoffset = L;"
                               " tl.to(c, { strokeDashoffset: 0, duration: 0.9, ease: 'power2.inOut' }, %.3f); })();" % (bid, j, q, r, float(rg.get("at", t_in)) + 0.12 * q))
        if b.get("window"):               # a macOS window on the stage (a "desktop"), behind the nodes
            w_ = b["window"]
            back_html += ('<div class="wd-win" id="%s-win" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx"><div class="bar"><span class="dot r"></span>'
                          '<span class="dot y"></span><span class="dot g"></span><span class="wt">%s</span></div></div>'
                          % (bid, w_["x"], w_["y"], w_["w"], w_["h"], w_.get("title", "")))
            node_js.append("tl.fromTo('#%s-win', { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.5, ease: 'power2.out' }, %.3f);" % (bid, float(w_.get("at", t_in))))
        if b.get("dock"):
            dk = b["dock"]
            tiles = "".join('<div class="tile"><img src="%s" alt="" /></div>' % src for src in dk["items"][:8])
            back_html += '<div class="wd-dock" id="%s-dock" style="left:%dpx;top:%dpx">%s</div>' % (bid, dk["x"], dk["y"], tiles)
            node_js.append("tl.fromTo('#%s-dock', { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.5, ease: 'power2.out' }, %.3f);" % (bid, float(dk.get("at", t_in))))
        title = '<div class="fx-title" id="%s-title">%s</div>' % (bid, em_spans(b["title"], b.get("em"))) if b.get("title") else ""
        inner = ('<div class="cut"><div class="wd-cam" id="%s-cam" data-layout-allow-overflow><div class="wd-grid" data-layout-allow-overflow></div><svg class="wd-svg" viewBox="0 0 1920 1080">%s%s</svg>%s%s%s%s</div>%s%s</div>'
                 % (bid, rings_svg, links_svg, back_html, nodes_html, alerts_html, dots_html, title, scene_label(bid, b, t_out)))
        html_parts.append(host(bid, t_in, t_out, track, inner, anchor))
        cams = b.get("cam") or [[t_in, 960, 540, 1.0]]
        def cam_xy(c):
            z = float(c[3]); return 960 - z * float(c[1]), 540 - z * float(c[2]), z
        x0_, y0_, z0_ = cam_xy(cams[0])
        js("tl.set('#%s-cam', { x: %.1f, y: %.1f, scale: %.3f }, %.3f);" % (bid, x0_, y0_, z0_, t_in))
        prev_end = t_in
        for c in cams[1:]:
            tc, dur = float(c[0]), float(c[4]) if len(c) > 4 else 1.0
            if tc < prev_end - 1e-3:
                raise SystemExit("world %s: camera move at %.2f starts before the last one ends (%.2f): one gesture at a time" % (bid, tc, prev_end))
            if float(c[3]) > 3.2:
                print("WARN world %s: zoom %.2f at %.2f; over 3.2 the text goes soft in a 4K render" % (bid, float(c[3]), tc))
            xc, yc, zc = cam_xy(c)
            js("tl.to('#%s-cam', { x: %.1f, y: %.1f, scale: %.3f, duration: %.3f, ease: '%s' }, %.3f);" % (bid, xc, yc, zc, dur, c[5] if len(c) > 5 else "power2.inOut", tc))
            prev_end = tc + dur
        if b.get("title"):
            js("tl.fromTo('#%s-title', { opacity: 0, y: 26 }, { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }, %.3f);" % (bid, float(b.get("title_at", t_in + 0.05))))
        for s_ in node_js:
            js(s_)
        transition(b, t_in, t_out)
    elif t == "deck":
        # 40. deck, full-frame: the video's numbered parts (e.g. "3 predictions") as tall glass cards in a row. The first time
        # it shows the whole row, then the camera pushes in on card 1; at every return it starts on the card just finished and
        # slides to the next one, which lights cyan while the rest recede. "recap_at" pulls back to the full row.
        cards = b["cards"][:4]; n = len(cards); now = max(1, min(n, int(b.get("now", 1)))); CW, GAP = 380, 60
        Z = float(b.get("zoom", 1.5)); x0 = (1920 - (n * CW + (n - 1) * GAP)) / 2.0
        cxs = [x0 + i * (CW + GAP) + CW / 2.0 for i in range(n)]
        cam = lambda i: (960 - Z * cxs[i], 540 - Z * 540)
        cards_html = "".join('<div class="glass dq-card" id="%s-c%d" style="left:%.0fpx"><div class="inner" id="%s-ci%d"><div class="no">%d</div>%s<div class="ttl">%s</div></div></div>'
                             % (bid, i, x0 + i * (CW + GAP), bid, i, i + 1, icon_svg(c_.get("icon")), c_["title"]) for i, c_ in enumerate(cards))
        head = '<div class="dq-head" id="%s-head">%s</div>' % (bid, b["head"]) if b.get("head") else ""
        inner = '<div class="cut"><div class="gridbg"></div><div class="dq-cam" id="%s-cam" data-layout-allow-overflow>%s%s</div>%s</div>' % (bid, head, cards_html, scene_label(bid, b, t_out))
        html_parts.append(host(bid, t_in, t_out, track, inner, anchor))
        k = now - 1
        fa = float(b.get("focus_at", t_in + (0.9 if now == 1 else 0.35)))
        if now == 1 or b.get("from") == "all":
            js("tl.set('#%s-cam', { x: 0, y: 0, scale: 1 }, %.3f);" % (bid, t_in))
            if b.get("head"):
                js("tl.fromTo('#%s-head', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }, %.3f);" % (bid, t_in))
            for i in range(n):
                js("glassIn('#%s-c%d', %.3f, { y: 30 });" % (bid, i, t_in + 0.08 * i))
                js("tl.fromTo('#%s-ci%d', { opacity: 0 }, { opacity: 1, duration: 0.36 }, %.3f);" % (bid, i, t_in + 0.08 * i + 0.04))
            js("tl.to('#%s-cam', { x: %.1f, y: %.1f, scale: %.3f, duration: 1.1, ease: 'power2.inOut' }, %.3f);" % ((bid,) + cam(k) + (Z, fa)))
            others = ", ".join("#%s-ci%d" % (bid, i) for i in range(n) if i != k)
            if others:
                js("tl.to('%s', { opacity: 0.38, duration: 0.5, ease: 'power2.out' }, %.3f);" % (others, fa + 0.1))
        else:
            js("tl.set('#%s-cam', { x: %.1f, y: %.1f, scale: %.3f }, %.3f);" % ((bid,) + cam(k - 1) + (Z, t_in)))
            for i in range(n):
                js("glassIn('#%s-c%d', %.3f, {}, 0.25);" % (bid, i, t_in))
                js("tl.set('#%s-ci%d', { opacity: %.2f }, %.3f);" % (bid, i, 1.0 if i == k - 1 else 0.38, t_in))
            js("tl.to('#%s-cam', { x: %.1f, y: %.1f, scale: %.3f, duration: 1.0, ease: 'power2.inOut' }, %.3f);" % ((bid,) + cam(k) + (Z, fa)))
            js("tl.to('#%s-ci%d', { opacity: 0.38, duration: 0.5, ease: 'power2.out' }, %.3f);" % (bid, k - 1, fa + 0.1))
            js("tl.to('#%s-ci%d', { opacity: 1, duration: 0.5, ease: 'power2.out' }, %.3f);" % (bid, k, fa + 0.3))
        tl_ = fa + 0.6
        js("tl.to('#%s-c%d', { borderColor: 'rgba(10,240,240,0.95)', boxShadow: '0 0 60px rgba(10,240,240,0.45), 0 24px 80px rgba(0,0,0,0.38)', duration: 0.45, ease: 'power2.out' }, %.3f);" % (bid, k, tl_))
        js("tl.to('#%s-c%d .ic', { stroke: '#0AF0F0', duration: 0.45, ease: 'power2.out' }, %.3f);" % (bid, k, tl_))
        if b.get("recap_at") is not None:
            tr_ = float(b["recap_at"])
            js("tl.to('#%s-cam', { x: 0, y: 0, scale: 1, duration: 1.1, ease: 'power2.inOut' }, %.3f);" % (bid, tr_))
            others = ", ".join("#%s-ci%d" % (bid, i) for i in range(n) if i != k)
            if others:
                js("tl.to('%s', { opacity: 1, duration: 0.5, ease: 'power2.out' }, %.3f);" % (others, tr_ + 0.3))
        transition(b, t_in, t_out)
    elif t == "pills":
        # 41. pills over the footage: two to five short labels that arrive one by one on their words, as a column on each side
        # of the speaker ("sides", alternating), one column ("left" / "right"), or one row at the bottom ("row", laid out from the first
        # frame so it never shifts). tone cyan = the one that matters, amber = a risk (with an x badge when "mark": "x").
        items = []
        for it in b["items"][:6]:
            if isinstance(it, dict):
                items.append(dict(it, at=float(it["at"])))
            else:
                items.append({"text": it[0], "at": float(it[1]), "anchor": it[2] if len(it) > 2 else it[0]})
        layout = b.get("layout", "sides")
        cols = {"l": [], "r": [], "row": []}
        for i, it in enumerate(items):
            side = "row" if layout == "row" else ("l" if layout == "left" else ("r" if layout == "right" else ("l" if i % 2 == 0 else "r")))
            badge = '<div class="x" id="%s-x%d">&times;</div>' % (bid, i) if it.get("mark") == "x" else ""
            cols[side].append('<div class="glass pls %s" id="%s-p%d" style="visibility:hidden"%s><div class="inner" id="%s-pi%d">%s<span class="t">%s</span></div>%s</div>'
                              % (it.get("tone", ""), bid, i, item_attrs([it["text"], it["at"], it.get("anchor", it["text"])]), bid, i, icon_svg(it.get("icon")), it["text"], badge))
            it["side"] = side
        body = ""
        if cols["l"]:
            body += '<div class="pls-col l" style="top:%dpx">%s</div>' % (int(b.get("top", 290)), "".join(cols["l"]))
        if cols["r"]:
            body += '<div class="pls-col r" style="top:%dpx">%s</div>' % (int(b.get("top", 290)), "".join(cols["r"]))
        if cols["row"]:
            body += '<div class="pls-row">%s</div>' % "".join(cols["row"])
        html_parts.append(host(bid, t_in, t_out, track, body, anchor))
        for i, it in enumerate(items):
            frm = {"l": "{ x: -30 }", "r": "{ x: 30 }", "row": "{ y: 20 }"}[it["side"]]
            js("tl.set('#%s-p%d', { visibility: 'inherit' }, %.3f);" % (bid, i, it["at"]))   # before its word it must not blur the footage
            js("glassIn('#%s-p%d', %.3f, %s);" % (bid, i, it["at"], frm))
            js("tl.fromTo('#%s-pi%d', { opacity: 0 }, { opacity: 1, duration: 0.36 }, %.3f);" % (bid, i, it["at"] + 0.04))
            if it.get("mark") == "x":
                js("tl.fromTo('#%s-x%d', { opacity: 0, scale: 0.3 }, { opacity: 1, scale: 1, duration: 0.3, ease: 'power2.out' }, %.3f);" % (bid, i, it["at"] + 0.3))
        js("tl.to('#host-%s .pls .inner, #host-%s .pls .x', { opacity: 0, duration: 0.28, ease: 'power2.in' }, %.3f);" % (bid, bid, t_out - 0.40))
        for i in range(len(items)):
            js("glassOut('#%s-p%d', %.3f, 0.33);" % (bid, i, t_out - 0.35))
        js("tl.set('#host-%s .pls .inner', { opacity: 0 }, %.3f);" % (bid, t_out - 0.12))
    elif t == "chat":
        # 42. chat: messages arrive one by one on their words. "float" = bubbles beside the speaker over the footage (tl / tr);
        # "window" = a dark app window on the wash; "phone" = the same thread on a phone. Cyan bubbles are the speaker's side ("me"),
        # white ones the other side ("them"). In a window the thread scrolls up as it grows, never jumps.
        frame = b.get("frame", "window")
        msgs = []
        for m in b["messages"][:8]:
            if isinstance(m, dict):
                msgs.append(dict(m, at=float(m["at"])))
            else:
                msgs.append({"from": m[0], "text": m[1], "at": float(m[2]), "anchor": m[3] if len(m) > 3 else "-"})
        bub = "".join('<div class="ch-b %s" id="%s-m%d"%s>%s</div>' % ("me" if m.get("from") == "me" else "them", bid, i,
                      item_attrs([m["text"], m["at"], m.get("anchor", "-")]), m["text"]) for i, m in enumerate(msgs))
        if frame == "float":
            side = "r" if b.get("pos", "tl") == "tr" else "l"
            body = '<div class="ch-float %s" style="%s">%s</div>' % (side, "right:70px" if side == "r" else "left:70px", bub)
            html_parts.append(host(bid, t_in, t_out, track, body, anchor))
        else:
            ph = " phone" if frame == "phone" else ""
            body = ('<div class="cut"><div class="gridbg"></div><div class="ch-win%s" id="%s-win"><div class="bar"><div class="av">%s</div><div class="nm">%s</div></div>'
                    '<div class="ch-view" id="%s-view" data-layout-allow-overflow><div class="ch-list" id="%s-list" data-layout-allow-overflow>%s</div></div></div>%s</div>'
                    % (ph, bid, icon_svg(b.get("icon", "user")), b.get("name", "Client"), bid, bid, bub, scene_label(bid, b, t_out)))
            html_parts.append(host(bid, t_in, t_out, track, body, anchor))
            js("tl.fromTo('#%s-win', { opacity: 0, y: 40, scale: 0.97 }, { opacity: 1, y: 0, scale: 1, duration: 0.5, ease: 'power2.out' }, %.3f);" % (bid, t_in))
            # the window grows with the thread (a card sized for messages that have not arrived is dead space), then the thread
            # scrolls up once the window is full. Measured lazily (function values), so the fonts are in.
            vb = bid.replace("-", "_"); maxh = 940 if frame == "phone" else 840; barh = 120 if frame == "phone" else 84
            js("const chatNeed_%s = function (i) { var m = document.getElementById('%s-m' + i); return %d + 34 + m.offsetTop + m.offsetHeight + 40; };" % (vb, bid, barh))
            js("const chatH_%s = function (i) { return Math.min(%d, Math.max(%d, chatNeed_%s(i))); };" % (vb, maxh, 260 if frame != "phone" else maxh, vb))
            js("const chatShift_%s = function (i) { return -Math.max(0, chatNeed_%s(i) - %d); };" % (vb, vb, maxh))
            js("tl.set('#%s-win', { height: function () { return chatH_%s(0); } }, %.3f);" % (bid, vb, t_in))
            for i, m in enumerate(msgs[1:], 1):
                js("tl.to('#%s-win', { height: function () { return chatH_%s(%d); }, duration: 0.4, ease: 'power2.out' }, %.3f);" % (bid, vb, i, m["at"] - 0.1))
                js("tl.to('#%s-list', { y: function () { return chatShift_%s(%d); }, duration: 0.4, ease: 'power2.out' }, %.3f);" % (bid, vb, i, m["at"] - 0.1))
        for i, m in enumerate(msgs):
            js("tl.fromTo('#%s-m%d', { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }, %.3f);" % (bid, i, m["at"]))
        if frame == "float":
            js("tl.to('#host-%s .ch-b', { opacity: 0, duration: 0.3, ease: 'power2.in' }, %.3f);" % (bid, t_out - 0.35))
        else:
            transition(b, t_in, t_out)
    elif t == "doc":
        # 18b. doc read, full-frame (format 18 in the composer, plus a focus pull): the page rebuilt in HTML under the 4b
        # chrome bar. For each passage in "marks", on its word: the camera glides to it and zooms, the passage is stroked amber
        # in one pass (0.14 s a word, 0.035 s apart), and with focus the rest of the page drops out of focus (a static blurred
        # copy underneath; only opacity animates). Paste the page's real words: a doc is a quote, never a paraphrase.
        paras = list(b["paras"]); marks = b.get("marks", []); Z = float(b.get("zoom", 1.3)); focus = b.get("focus", True)
        spans = {}          # para index -> [(start, end, mark k)]
        for k_, mk in enumerate(marks):
            found = None
            for pi in ([int(mk["p"])] if "p" in mk else range(len(paras))):
                j = paras[pi].find(mk["text"])
                if j >= 0:
                    found = (pi, j); break
            if not found:
                raise SystemExit("doc %s: mark %r is not in the page text (copy it exactly)" % (bid, mk["text"]))
            spans.setdefault(found[0], []).append((found[1], found[1] + len(mk["text"]), k_))
            mk["_p"] = found[0]
        def para_html(pi, sharp):
            txt, out, pos_ = paras[pi], "", 0
            for s0, e0, k_ in sorted(spans.get(pi, [])) if sharp else []:
                ws = txt[s0:e0].split(" ")
                out += hesc(txt[pos_:s0]) + '<span class="dc-m" id="%s-m%d">%s</span>' % (bid, k_, " ".join('<span class="dc-w">%s<i></i></span>' % hesc(w) for w in ws))
                pos_ = e0
            out += hesc(txt[pos_:])
            return '<p class="dc-p"%s data-layout-allow-overlap>%s</p>' % (' id="%s-p%d"' % (bid, pi) if sharp else "", out)
        def col(sharp):
            hd = ('<div class="dc-kick">%s</div>' % hesc(b["kicker"]) if b.get("kicker") else "") + \
                 ('<div class="dc-ttl">%s</div>' % hesc(b["title"]) if b.get("title") else "") + \
                 ('<div class="dc-date">%s</div>' % hesc(b["date"]) if b.get("date") else "")
            return '<div class="dc-col %s" data-layout-allow-overlap%s><div%s data-layout-allow-overlap>%s</div>%s</div>' % ("sharp" if sharp else "soft", ' id="%s-soft" style="opacity:0" data-layout-allow-overlap data-layout-allow-occlusion' % bid if not sharp else "",
                                                                    ' id="%s-hd"' % bid if sharp else "", hd, "".join(para_html(pi, sharp) for pi in range(len(paras))))
        anc = "".join('<div id="%s-a%d" data-at="%.3f"%s style="display:none"></div>' % (bid, k_, float(mk["at"]), attr_anchor(mk.get("anchor", " ".join(mk["text"].split(" ")[:4]))))
                      for k_, mk in enumerate(marks))
        inner = ('<div class="dc-doc%s"><div class="dc-chrome"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><div class="url">%s</div></div>'
                 '<div class="dc-wrap"><div class="dc-pg" id="%s-pg" data-layout-allow-overflow data-layout-allow-occlusion>%s%s</div></div>%s%s</div>'
                 % (" dark" if b.get("theme") == "dark" else "", b.get("domain", ""), bid, col(False), col(True), anc, scene_label(bid, b, t_out)))
        html_parts.append(host(bid, t_in, t_out, track, inner, anchor))
        vb = bid.replace("-", "_")
        # where passage k sits on the page, and the page transform that brings it to frame centre at zoom Z (clamped to the page)
        # each mark may carry its own "zoom" (so the zoom lands on the word that says "zoom", not on the first highlight):
        # zoom 1 = the highlight lands on the page as it is; the next mark zooms on its word
        js("const docCam_%s = function (k, z) { var pg = document.getElementById('%s-pg'), m = document.getElementById('%s-m' + k);"
           " var r = m.getBoundingClientRect(), p = pg.getBoundingClientRect(), f = p.width / 1920;"
           " var mx = (r.left + r.width / 2 - p.left) / f, my = (r.top + r.height / 2 - p.top) / f;"
           " var x = Math.min(0, Math.max(1920 - 1920 * z, 960 - z * mx)), y = Math.min(0, 440 - z * my);"
           " return { x: x, y: y, scale: z }; };" % (vb, bid, bid))
        js("tl.set('#%s-pg', { x: 0, y: 0, scale: 1 }, %.3f);" % (bid, t_in))
        starts = [max(t_in + 0.1, float(mk["at"]) - 0.35) for mk in marks]
        for k_, mk in enumerate(marks):
            s_ = starts[k_]; nxt = starts[k_ + 1] if k_ + 1 < len(marks) else t_out
            dur = max(0.5, min(1.1, nxt - s_ - 0.05))
            zk = float(mk.get("zoom", Z))
            if mk.get("move", True):        # "move": false = the page holds still and only the stroke lands
                js("tl.to('#%s-pg', { x: function () { return docCam_%s(%d, %.3f).x; }, y: function () { return docCam_%s(%d, %.3f).y; }, scale: %.3f, duration: %.3f, ease: 'power2.inOut' }, %.3f);"
                   % (bid, vb, k_, zk, vb, k_, zk, zk, dur, s_))
            js("tl.to('#%s-m%d .dc-w i', { scaleX: 1, duration: 0.14, ease: 'power1.out', stagger: 0.035 }, %.3f);" % (bid, k_, float(mk["at"])))
            if focus and mk.get("focus", True):
                if k_ == 0 or not any(m_.get("focus", True) for m_ in marks[:k_]):
                    js("tl.to('#%s-soft', { opacity: 0.5, duration: 0.5, ease: 'power2.out' }, %.3f);" % (bid, s_))
                    rest = ", ".join(["#%s-hd" % bid] + ["#%s-p%d" % (bid, pi) for pi in range(len(paras)) if pi != mk["_p"]])
                    js("tl.to('%s', { opacity: 0, duration: 0.5, ease: 'power2.out' }, %.3f);" % (rest, s_))
                elif marks[k_ - 1]["_p"] != mk["_p"]:
                    js("tl.to('#%s-p%d', { opacity: 0, duration: 0.5, ease: 'power2.out' }, %.3f);" % (bid, marks[k_ - 1]["_p"], s_))
                    js("tl.to('#%s-p%d', { opacity: 1, duration: 0.5, ease: 'power2.out' }, %.3f);" % (bid, mk["_p"], s_))
        transition(b, t_in, t_out)
    elif t == "clip":
        # 20c. full-frame video cutaway in the composer (format 20's rules: a direct child of the root, muted, z 20, a 1.00 to
        # 1.04 drift). For screen recordings, archive footage, and AI b-roll shots (the AI b-roll route in SKILL.md).
        # Optional over it: a caption ("label") or a glass checklist top-left ("items"), on a host above the video.
        html_parts.append('    <video class="cutaway-video clip" id="%s" src="%s" muted playsinline data-start="%.3f" data-duration="%.3f" data-media-start="%.3f" data-track-index="%d"%s></video>\n'
                          % (bid, b["src"], t_in, t_out - t_in, float(b.get("media_start", 0)), track, attr_anchor(anchor)))
        if b.get("drift", True):
            js("tl.fromTo('#%s', { scale: 1.0 }, { scale: 1.04, duration: %.3f, ease: 'none' }, %.3f);" % (bid, t_out - t_in, t_in))
        if b.get("label") or b.get("items"):
            track += 1
            lst = ""
            if b.get("items"):
                mark = CHECK_SVG if b.get("marker", "check") == "check" else '<div class="d"></div>'
                its = "".join('<div class="item" id="%s-i%d"%s>%s<div class="t">%s</div></div>' % (bid, i, item_attrs(it), mark, it[0]) for i, it in enumerate(b["items"]))
                lst = '<div class="glass cl-list" id="%s-glass"><div class="inner" id="%s-inner">%s</div></div>' % (bid, bid, its)
            html_parts.append(host(bid + "-over", t_in, t_out, track, lst + scene_label(bid, b, t_out), "-").replace('class="card-host clip"', 'class="card-host clip clip-over"', 1))
            if b.get("items"):
                t0 = float(b["items"][0][1])
                js("glassIn('#%s-glass', %.3f, { x: -40 });" % (bid, t0 - 0.1))
                js("tl.fromTo('#%s-inner', { opacity: 0 }, { opacity: 1, duration: 0.36 }, %.3f);" % (bid, t0 - 0.06))
                for i, it in enumerate(b["items"]):
                    js("tl.set('#%s-i%d', { display: 'flex' }, %.3f);" % (bid, i, float(it[1])))
                    js("tl.fromTo('#%s-i%d', { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: 0.40, ease: 'power2.out' }, %.3f);" % (bid, i, float(it[1])))
                    if b.get("marker", "check") == "check":
                        check_in("#%s-i%d" % (bid, i), float(it[1]))
                js("tl.to('#%s-inner', { opacity: 0, duration: 0.28, ease: 'power2.in' }, %.3f);" % (bid, t_out - 0.40))
                js("glassOut('#%s-glass', %.3f, 0.33);" % (bid, t_out - 0.35))
        transition(b, t_in, t_out)
    else:
        raise SystemExit("unknown beat type %r" % t)
    track += 1

# ---- camera -----------------------------------------------------------------------------------------
cam = ["tl.set('#video-zoom', { scale: 1.0 }, 0);", "tl.set('#video-wrap', { scale: 1.0, x: 0 }, 0);"]
for op in S.get("camera", []):
    if op[0] == "set":
        cam.append("tl.set('#video-zoom', { scale: %.3f }, %.3f);" % (float(op[2]), float(op[1])))
    elif op[0] == "creep":
        t0, t1, sc = float(op[1]), float(op[2]), float(op[3])
        cam.append("tl.to('#video-zoom', { scale: %.3f, duration: %.3f, ease: 'power1.inOut' }, %.3f);" % (sc, t1 - t0, t0))
    elif op[0] == "punch":
        cam.append("tl.to('#video-zoom', { scale: %.3f, duration: 0.32, ease: 'power2.out' }, %.3f);" % (float(op[2]), float(op[1])))
    elif op[0] == "reveal":     # zoom-out reveal as a card enters: footage recedes from 1.10 to 1.00
        cam.append("tl.fromTo('#video-zoom', { scale: 1.10 }, { scale: 1.00, duration: 0.5, ease: 'power2.inOut', immediateRender: false }, %.3f);" % float(op[1]))
    elif op[0] == "release":
        cam.append("tl.to('#video-zoom', { scale: 1.00, duration: %.3f, ease: 'power2.inOut' }, %.3f);" % (float(op[2]), float(op[1])))
    else:
        raise SystemExit("unknown camera op %r" % op)

HELPERS = """
        const glassIn = function (sel, t, from, dur) {
          const g0 = document.querySelector(sel);       // glass inside a full-frame scene on the wash takes glass_bg_cut
          tl.fromTo(sel, Object.assign({ backgroundColor: 'rgba(255,255,255,0)', borderColor: 'rgba(255,255,255,0)', boxShadow: '0 24px 80px rgba(0,0,0,0)' }, from || {}),
            { backgroundColor: (g0 && g0.closest('.cut')) ? 'GLASS_BG_CUT' : 'GLASS_BG', borderColor: 'rgba(255,255,255,0.58)', boxShadow: '0 24px 80px rgba(0,0,0,0.38)', x: 0, y: 0, duration: dur || 0.42, ease: 'power2.out' }, t);
        };
        const glassOut = function (sel, t, dur) {
          tl.to(sel, { backgroundColor: 'rgba(255,255,255,0)', borderColor: 'rgba(255,255,255,0)', boxShadow: '0 24px 80px rgba(0,0,0,0)', duration: dur || 0.35, ease: 'power2.in' }, t);
        };
        const lowerIn = function (lineId, t) {
          tl.fromTo('#' + lineId + ' .w', { opacity: 0, y: 26 }, { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out', stagger: 0.055 }, t);
        };
        const lowerOut = function (hostId, tEnd) {
          tl.to('#' + hostId + ' .lower', { opacity: 0, duration: 0.35, ease: 'power2.in' }, tEnd - 0.35);
        };
        // a light that runs along an SVG path, drawing the lit stroke (and its glow) behind it; one proxy, seek-safe
        const along = function (litSel, glowSel, dotSel, t, dur) {
          const p = document.querySelector(litSel), g = document.querySelector(glowSel), d = document.querySelector(dotSel), L = p.getTotalLength(), o = { v: 0 };
          [p, g].forEach(function (e) { e.style.strokeDasharray = L; });
          const put = function () { const q = p.getPointAtLength(o.v * L); d.style.left = q.x + 'px'; d.style.top = q.y + 'px';
            p.style.strokeDashoffset = L * (1 - o.v); g.style.strokeDashoffset = L * (1 - o.v); };
          put();
          tl.fromTo(o, { v: 0 }, { v: 1, duration: dur, ease: 'power1.inOut', immediateRender: false, onUpdate: put }, t);
          tl.fromTo(d, { opacity: 0 }, { opacity: 1, duration: 0.12 }, t);
          tl.to(d, { opacity: 0, duration: 0.16 }, t + dur - 0.02);
        };
        // a second light along a path that is already lit: moves the dot only
        const pulse = function (pathSel, dotSel, t, dur) {
          const p = document.querySelector(pathSel), d = document.querySelector(dotSel), L = p.getTotalLength(), o = { v: 0 };
          const put = function () { const q = p.getPointAtLength(o.v * L); d.style.left = q.x + 'px'; d.style.top = q.y + 'px'; };
          tl.fromTo(o, { v: 0 }, { v: 1, duration: dur, ease: 'power1.inOut', immediateRender: false, onUpdate: put }, t);
          tl.fromTo(d, { opacity: 0 }, { opacity: 1, duration: 0.12, immediateRender: false }, t);
          tl.to(d, { opacity: 0, duration: 0.16 }, t + dur - 0.02);
        };
        // a second count on a number already showing (51 -> 93): same format, from where it stands
        const countFromTo = function (sel, from, to, t, dur, prefix, suffix, dec) {
          const el = document.querySelector(sel); const o = { v: from };
          const fmt = function (v) { return prefix + v.toLocaleString('en-US', { minimumFractionDigits: dec, maximumFractionDigits: dec }) + suffix; };
          tl.fromTo(o, { v: from }, { v: to, duration: dur, ease: 'power2.out', immediateRender: false,
            onUpdate: function () { el.textContent = fmt(dec ? o.v : Math.round(o.v)); } }, t);
        };
        // count-up in full digits ("300,000", never "300K"); the proxy lives on the one paused timeline
        const countUp = function (sel, to, t, dur, prefix, suffix, dec) {
          const el = document.querySelector(sel); const o = { v: 0 };
          const fmt = function (v) { return prefix + v.toLocaleString('en-US', { minimumFractionDigits: dec, maximumFractionDigits: dec }) + suffix; };
          el.textContent = fmt(0);
          tl.fromTo(o, { v: 0 }, { v: to, duration: dur, ease: 'power2.out', immediateRender: false,
            onUpdate: function () { el.textContent = fmt(dec ? o.v : Math.round(o.v)); } }, t);
        };
"""

# "glass_bg": the glass tint glassIn lands on. Light (.18 white) is the house look; a bright room (white shelves) washes it
# out, so a storyboard may ask for a dark tint, e.g. "rgba(17,17,17,0.55)".
# "glass_bg_cut": the tint for glass INSIDE a full-frame scene on the brand wash
# (world nodes, stat tiles in a row, ...). A dark glass_bg keeps the glass over a bright set legible, but on the dark wash the
# approved look is the light glass. Defaults to glass_bg, so a storyboard without the key renders exactly as before.
HELPERS = HELPERS.replace("GLASS_BG_CUT", S.get("glass_bg_cut", S.get("glass_bg", "rgba(255,255,255,0.18)")))
HELPERS = HELPERS.replace("GLASS_BG", S.get("glass_bg", "rgba(255,255,255,0.18)"))

page = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<style>%s</style>
</head>
<body>
  <div id="stage" data-composition-id="%s" data-start="0" data-duration="%.3f" data-fps="30" data-width="1920" data-height="1080">

    <div class="video-wrapper" id="video-wrap">
      <div id="video-zoom">
        <video id="bg-video" src="%s" playsinline data-has-audio="true" data-start="0" data-duration="%.3f" data-track-index="1"></video>
      </div>
    </div>

%s%s%s
    <script src="%s"></script>
    <script>
      (function () {
        document.querySelectorAll('.lower').forEach(function (el) {
          const words = el.getAttribute('data-text').split(' ');
          const em = (el.getAttribute('data-em') || '').split(',').filter(Boolean).map(Number);
          el.textContent = '';
          words.forEach(function (word, i) {
            if (i > 0) { const sp = document.createElement('span'); sp.className = 'sp'; sp.innerHTML = '&nbsp;'; el.appendChild(sp); }
            const w = document.createElement('span'); w.className = 'w' + (em.indexOf(i) !== -1 ? ' em' : ''); w.textContent = word; el.appendChild(w);
          });
        });
        const tl = window.gsap.timeline({ paused: true });
%s
        // camera
        %s

        // beats
        %s
%s
        tl.to({}, { duration: %.3f }, 0);
        window.__timelines = window.__timelines || {};
        window.__timelines["%s"] = tl;
      })();
    </script>
  </div>
</body>
</html>
""" % (CSS, S["id"], D, S.get("video", "input-video.mp4"), D, "".join(html_parts), S.get("raw_html", ""), "".join(audio_parts),
       GSAP_SRC, HELPERS, "\n        ".join(cam), "\n        ".join(js_parts), S.get("raw_js", ""), D, S["id"])
open(os.path.join(OUT, "index.html"), "w").write(page)
open(os.path.join(OUT, "hyperframes.json"), "w").write(json.dumps({
    "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
    "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
    "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
    "media": {"autoProxy": True}, "authoringSkill": "talking-head-recut"}, indent=2))
beats = [(S["tag"]["in"], "tag") ] if S.get("tag") else []
beats += [(float(b["in"]), b["id"]) for b in S.get("beats", [])]
print("wrote %s/index.html: %d beats, %d camera ops, %d sounds" % (OUT, len(beats), len(S.get("camera", [])), len(audio_parts)))
print("snapshot moments:", " ".join("%.2f" % (t + 0.9) for t, _ in beats))
# format usage, for the "two formats compete: use the one used least so far in this video" rule (SKILL.md)
seq = sorted((float(b["in"]), b["type"] + ("m" if b.get("morph") else "")) for b in S.get("beats", []))
counts = {}
for _, ty in seq:
    counts[ty] = counts.get(ty, 0) + 1
print("format usage:", ", ".join("%s %d" % (k, v) for k, v in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))))
for (t1, a), (t2, b2) in zip(seq, seq[1:]):
    if a == b2 and a not in ("line", "vignette"):
        print("WARN same device twice in a row: %s at %.2f and %.2f" % (a, t1, t2))
