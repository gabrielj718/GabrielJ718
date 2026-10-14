"""claude_chat.py: the full-screen Claude chat cutaway (format 24), one function for every build.

Why: a typed prompt runs past the composer when every space is an &nbsp; (no line-break opportunity).
Here each word is a nowrap group of character spans and the spaces between words
are real, breakable spaces, so the prompt wraps like the real app; the composer is bottom-anchored with a min-height
and grows upward if a prompt needs a third line. Attachments (image thumbnails) can drop into the composer before the
typing and ride along into the sent message.

Usage (inside a build script that has host() and js() helpers and the glassIn-free full-frame "cut" style):
    import sys; sys.path.insert(0, "<project>/.claude/skills/youtube-edit/formats"); from claude_chat import chat_css, chat_scene
    html, lines = chat_scene("chat", prompt, t_in, t_out, type_t0, type_t1, send, think_end, head, items, attachments=[...], att_times=[...])
    host("chat", t_in, t_out, html, "<anchor>"); [js(l) for l in lines]; and add chat_css() to the page CSS once.
items: list of (bold, rest) rows revealed from item_t0 every item_gap seconds (rest may be ""). attachments: image paths
relative to public/ (thumbnails, cover-cropped). att_times: when each thumbnail drops in (one per attachment).
"""
import html as _h

def chat_css():
    return """
  .cc-app { position:absolute; left:180px; top:70px; width:1560px; height:940px; border-radius:18px; overflow:hidden; background:#FAF9F5;
    box-shadow: 0 40px 120px rgba(0,0,0,.6), 0 0 0 1px rgba(255,255,255,.10); transform-origin:50% 50%; }
  .cc-bar { position:absolute; left:0; right:0; top:0; height:44px; background:#EFEDE5; display:flex; align-items:center; gap:9px; padding:0 18px; }
  .cc-bar .dt { width:14px; height:14px; border-radius:50%; } .cc-bar .r { background:#FF5F57; } .cc-bar .y { background:#FEBC2E; } .cc-bar .g { background:#28C840; }
  .cc-side { position:absolute; left:0; top:44px; bottom:0; width:280px; background:#F2F0E8; border-right:1px solid #E4E1D8; padding:28px 26px; box-sizing:border-box; }
  .cc-brand { display:flex; align-items:center; gap:12px; font-weight:700; font-size:38px; color:#1F1E1D; } .cc-brand img { width:34px; height:34px; }
  .cc-sbtn { margin-top:34px; font-weight:500; font-size:24px; color:#1F1E1D; background:#E8E5DB; padding:12px 18px; border-radius:12px; }
  .cc-sbar { height:14px; border-radius:7px; background:#E1DED4; margin-top:26px; } .cc-sbar.w1 { width:80%; } .cc-sbar.w2 { width:62%; } .cc-sbar.w3 { width:72%; }
  .cc-main { position:absolute; left:280px; right:0; top:44px; bottom:0; }
  .cc-greet { position:absolute; left:0; right:0; top:280px; text-align:center; font-weight:500; font-size:54px; color:#1F1E1D; }
  .cc-greet img { width:46px; height:46px; vertical-align:-6px; margin-right:16px; }
  .cc-comp { position:absolute; left:80px; right:80px; bottom:50px; min-height:170px; box-sizing:border-box; padding:30px 110px 30px 34px;
    background:#fff; border:1.5px solid #DAD7CE; border-radius:24px; box-shadow: 0 6px 24px rgba(0,0,0,.06); }
  .cc-att { display:flex; gap:16px; margin-bottom:20px; } .cc-att:empty { display:none; }
  .cc-thumb { width:150px; height:104px; border-radius:14px; background-size:cover; background-position:center; box-shadow: 0 0 0 1.5px #DAD7CE; display:none; }
  .cc-typed { font-size:40px; line-height:1.3; color:#1F1E1D; min-height:52px; white-space:normal; }
  .cc-typed .wd { white-space:nowrap; } .cc-typed .ch { display:none; }
  .cc-ph { color:#9A968C; }
  .cc-caret { display:inline-block; width:3px; height:44px; background:#1F1E1D; vertical-align:-7px; margin-left:2px; }
  .cc-send { position:absolute; right:22px; bottom:22px; width:64px; height:64px; border-radius:16px; background:#D97757; display:flex; align-items:center; justify-content:center; }
  .cc-send svg { width:34px; height:34px; }
  .cc-umsg { position:absolute; top:40px; right:80px; max-width:980px; display:flex; flex-direction:column; align-items:flex-end; gap:14px; opacity:0; }
  .cc-uatt { display:flex; gap:14px; } .cc-uatt .cc-thumb { display:block; width:190px; height:132px; }
  .cc-utext { background:#EFEDE5; border-radius:22px; padding:22px 32px; font-size:40px; line-height:1.3; color:#1F1E1D; }
  .cc-resp { position:absolute; left:80px; right:80px; }
  .cc-star { position:absolute; left:0; top:2px; width:50px; height:50px; opacity:0; }
  .cc-rhead { margin-left:72px; font-weight:700; font-size:44px; line-height:54px; color:#1F1E1D; opacity:0; }
  .cc-item { margin-left:72px; margin-top:22px; font-size:40px; line-height:1.35; color:#2B2A28; display:flex; gap:14px; opacity:0; }
  .cc-item .rn { color:#D97757; font-weight:700; min-width:36px; } .cc-item b { font-weight:700; color:#1F1E1D; }
"""

def _typed(prompt):
    words = prompt.split(" ")
    out = []
    for i, w in enumerate(words):
        out.append('<span class="wd">%s</span>' % "".join('<span class="ch">%s</span>' % _h.escape(c) for c in w))
        if i < len(words) - 1:
            out.append('<span class="ch"> </span>')
    return "".join(out)

def chat_scene(p, prompt, t_in, t_out, type_t0, type_t1, send, think_end, head, items, item_t0=None, item_gap=0.42,
               attachments=(), att_times=(), resp_top=220, logo="img/claude.svg"):
    """Returns (html, js_lines). Times are composition seconds."""
    thumbs = "".join('<div class="cc-thumb" id="%s-a%d" style="background-image:url(%s)"></div>' % (p, k, src) for k, src in enumerate(attachments))
    uthumbs = "".join('<div class="cc-thumb" style="background-image:url(%s)"></div>' % src for src in attachments)
    rows = "".join('<div class="cc-item" id="%s-i%d"><span class="rn">%d.</span><span><b>%s%s</b>%s</span></div>'
                   % (p, k + 1, k + 1, _h.escape(a), ":" if b else "", (" " + _h.escape(b)) if b else "") for k, (a, b) in enumerate(items))
    if attachments: resp_top = max(resp_top, 360)
    html = ('<div class="cut"><div class="gridbg"></div><div class="cc-app" id="%(p)s-app">'
            '<div class="cc-bar"><span class="dt r"></span><span class="dt y"></span><span class="dt g"></span></div>'
            '<div class="cc-side"><div class="cc-brand"><img src="%(logo)s" alt="" /><span>Claude</span></div>'
            '<div class="cc-sbtn">+ New chat</div><div class="cc-sbar w1"></div><div class="cc-sbar w2"></div><div class="cc-sbar w3"></div></div>'
            '<div class="cc-main">'
            '<div class="cc-greet" id="%(p)s-greet"><img src="%(logo)s" alt="" />What should we build today?</div>'
            '<div class="cc-umsg" id="%(p)s-umsg">%(uatt)s<div class="cc-utext">%(prompt)s</div></div>'
            '<div class="cc-resp" id="%(p)s-resp" style="top:%(rt)dpx"><img class="cc-star" id="%(p)s-star" src="%(logo)s" alt="" />'
            '<div class="cc-rhead" id="%(p)s-rhead">%(head)s</div>%(rows)s</div>'
            '<div class="cc-comp" id="%(p)s-comp"><div class="cc-att">%(thumbs)s</div>'
            '<div class="cc-typed" id="%(p)s-typed"><span class="cc-ph" id="%(p)s-ph">Ask Claude anything</span>%(typed)s<span class="cc-caret" id="%(p)s-caret"></span></div>'
            '<div class="cc-send" id="%(p)s-send"><svg viewBox="0 0 24 24"><path d="M12 19V5M5 12l7-7 7 7" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg></div></div>'
            '</div></div></div>') % dict(p=p, logo=logo, prompt=_h.escape(prompt), head=_h.escape(head), rows=rows, thumbs=thumbs, rt=resp_top,
                                         uatt=('<div class="cc-uatt">%s</div>' % uthumbs) if attachments else "", typed=_typed(prompt))
    J = []
    J.append("tl.fromTo('#%s-app', { scale: 0.97, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.35, ease: 'power3.out' }, %.3f);" % (p, t_in))
    J.append("tl.to('#%s-app', { scale: 1.035, duration: %.3f, ease: 'none' }, %.3f);" % (p, t_out - t_in - 0.35, t_in + 0.35))
    for k, t in enumerate(att_times):
        J.append("tl.set('#%s-a%d', { display: 'block' }, %.3f);" % (p, k, t))
        J.append("tl.fromTo('#%s-a%d', { opacity: 0, scale: 0.8 }, { opacity: 1, scale: 1, duration: 0.28, ease: 'power2.out' }, %.3f);" % (p, k, t))
    first = type_t0 if not att_times else min(type_t0, att_times[0])
    J.append("tl.set('#%s-ph', { display: 'none' }, %.3f);" % (p, first))
    J.append("(function(){ const cs = document.querySelectorAll('#%s-typed .ch'); const n = cs.length; const t0 = %.3f, t1 = %.3f;"
             " for (let i = 0; i < n; i++) tl.set(cs[i], { display: 'inline' }, t0 + (t1 - t0) * i / n); })();" % (p, type_t0, type_t1))
    J.append("tl.fromTo('#%s-caret', { opacity: 1 }, { opacity: 0, duration: 0.25, ease: 'steps(1)', yoyo: true, repeat: %d }, %.3f);" % (p, int((send - t_in) / 0.25), t_in + 0.3))
    J.append("tl.fromTo('#%s-send', { scale: 1 }, { scale: 0.86, duration: 0.08, yoyo: true, repeat: 1, ease: 'power2.inOut' }, %.3f);" % (p, send))
    J.append("tl.set(['#%s-typed .ch', '#%s-caret', '#%s-comp .cc-att'], { display: 'none' }, %.3f);" % (p, p, p, send + 0.12))
    J.append("tl.set('#%s-ph', { display: 'inline' }, %.3f);" % (p, send + 0.12))
    J.append("tl.to('#%s-greet', { opacity: 0, y: -30, duration: 0.3, ease: 'power2.in' }, %.3f);" % (p, send + 0.05))
    J.append("tl.fromTo('#%s-umsg', { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: 0.4, ease: 'power3.out' }, %.3f);" % (p, send + 0.12))
    J.append("tl.fromTo('#%s-star', { opacity: 0 }, { opacity: 1, duration: 0.2 }, %.3f);" % (p, send + 0.35))
    J.append("tl.fromTo('#%s-star', { rotation: 0 }, { rotation: 360, duration: %.3f, ease: 'none' }, %.3f);" % (p, max(0.6, think_end - send - 0.35 + 0.6), send + 0.35))
    J.append("tl.fromTo('#%s-rhead', { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.3, ease: 'power2.out' }, %.3f);" % (p, think_end))
    t0 = item_t0 if item_t0 is not None else think_end + 0.4
    for k in range(len(items)):
        J.append("tl.fromTo('#%s-i%d', { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.3, ease: 'power2.out' }, %.3f);" % (p, k + 1, t0 + item_gap * k))
    return html, J
