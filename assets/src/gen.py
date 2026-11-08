"""Generate every README asset in light + dark. Run: python3 gen.py <outdir>"""
import math, os, sys
from typeset import text as T, glyphs, measure

OUT = sys.argv[1] if len(sys.argv) > 1 else "out"
os.makedirs(OUT, exist_ok=True)

THEMES = {
    "light": dict(paper="#F3EFE7", ink="#141311", mute="#6E685E", rule="#D6CFC2", panel="#EAE4D8", accent="#FF4A1C", onaccent="#F3EFE7", grain=0.07, tile="#141311", tiletext="#F3EFE7"),
    "dark":  dict(paper="#0E0E0D", ink="#EEE9DF", mute="#8D877C", rule="#2B2926", panel="#171615", accent="#FF5A2E", onaccent="#0E0E0D", grain=0.05, tile="#24221F", tiletext="#EEE9DF"),
}
EASE = "cubic-bezier(.16,1,.3,1)"
REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important;}}"


def svg(w, h, body, css, th, title, grain=True):
    g = ""
    if grain:
        g = (f'<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" stitchTiles="stitch"/>'
             f'<feColorMatrix type="saturate" values="0"/><feComponentTransfer><feFuncA type="table" tableValues="0 {th["grain"]}"/></feComponentTransfer></filter>')
    grain_rect = f'<rect width="{w}" height="{h}" filter="url(#grain)"/>' if grain else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{title}">'
            f'<title>{title}</title><defs>{g}</defs><style>{css}{REDUCED}</style>'
            f'<rect width="{w}" height="{h}" fill="{th["paper"]}"/>{body}{grain_rect}</svg>')


def star(cx, cy, r, fill, cls=""):
    """Eight-point asterisk drawn as a path (fonts lack one)."""
    pts = []
    for i in range(16):
        a = math.pi * i / 8
        rr = r if i % 2 == 0 else r * 0.38
        pts.append(f"{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}")
    c = f' class="{cls}"' if cls else ""
    return f'<polygon{c} points="{" ".join(pts)}" fill="{fill}"/>'


def reveal_word(word, font, size, x, y, fill, delay0, step, clip_id, cls="rv"):
    """Each glyph rises out of a clip mask, staggered."""
    gl, w = glyphs(word, font, size)
    out = [f'<clipPath id="{clip_id}"><rect x="{x - 40}" y="{y - size}" width="{w + 120}" height="{size * 1.28:.0f}"/></clipPath><g clip-path="url(#{clip_id})">']
    for i, (d, gx, adv) in enumerate(gl):
        out.append(f'<path class="{cls}" style="animation-delay:{delay0 + i * step:.2f}s" transform="translate({x + gx:.1f} {y})" d="{d}" fill="{fill}"/>')
    out.append("</g>")
    return "".join(out), w


# ---------------------------------------------------------------- HERO
def hero(th, ctx=None, season=None):
    W, H = 1200, 640
    css = (f".rv{{animation:rise 1.25s {EASE} both;}}"
           f"@keyframes rise{{from{{transform:translateY(105%);}}}}"
           ".rv{transform-box:fill-box;}"
           f".fade{{animation:fade 1s ease both;}}@keyframes fade{{from{{opacity:0;}}}}"
           ".spin{animation:spin 24s linear infinite;transform-origin:1052px 190px;}@keyframes spin{to{transform:rotate(360deg);}}"
           ".mq{animation:mq 38s linear infinite;}@keyframes mq{to{transform:translateX(var(--w));}}"
           ".pulse{animation:pulse 2s ease-in-out infinite;transform-box:fill-box;transform-origin:center;}@keyframes pulse{50%{opacity:.25;}}"
           f".draw{{stroke-dasharray:1200;animation:draw 1.6s {EASE} .2s both;}}@keyframes draw{{from{{stroke-dashoffset:1200;}}}}"
           ".bob{animation:bob 3.2s ease-in-out infinite;}@keyframes bob{50%{transform:translate(6px,6px);}}"
           ".glow{animation:glow 3s ease-in-out infinite;transform-box:fill-box;transform-origin:center;}@keyframes glow{50%{transform:scale(1.5);opacity:.05;}}"
           ".tw{animation:tw 2.6s ease-in-out infinite;}@keyframes tw{50%{opacity:.15;}}")
    b = []
    # meta row
    m = 13
    b.append(f'<g class="fade" style="animation-delay:.1s">')
    b.append(T("HAMZA ISHAQ — PORTFOLIO INDEX", 36, 46, "mono", m, tracking=.06, fill=th["mute"]))
    b.append(T("FULL-STACK DEVELOPER · FOUNDER, ALBATIX", 600, 46, "mono", m, anchor="middle", tracking=.06, fill=th["mute"]))
    b.append(T("KARACHI 24.86°N 67.00°E", 1164, 46, "mono", m, anchor="end", tracking=.06, fill=th["mute"]))
    b.append("</g>")
    b.append(f'<line class="draw" x1="36" y1="66" x2="1164" y2="66" stroke="{th["ink"]}" stroke-width="1.2"/>')

    # name
    s1, w1 = reveal_word("Hamza", "serif", 268, 26, 312, th["ink"], .25, .07, "c1")
    w2 = measure("Ishaq", "serif-it", 268)
    s2, _ = reveal_word("Ishaq", "serif-it", 268, 1176 - w2, 512, th["accent"], .55, .07, "c2")
    b += [s1, s2]

    # rotating badge
    cx, cy, R = 1052, 190, 92
    ring_text = (season or {}).get("ring") or "AVAILABLE FOR WORK · FREELANCE + FULL-TIME · "
    gl, tw = glyphs(ring_text, "mono-md", 13.5, tracking=.16)
    circ = 2 * math.pi * (R - 14)
    scale = circ / tw
    parts = [f'<g class="fade" style="animation-delay:1.1s"><g class="spin">']
    for d, gx, adv in gl:
        ang = (gx + adv / 2) * scale / (R - 14) - math.pi / 2
        px, py = cx + (R - 14) * math.cos(ang), cy + (R - 14) * math.sin(ang)
        deg = math.degrees(ang) + 90
        parts.append(f'<path transform="translate({px:.1f} {py:.1f}) rotate({deg:.1f}) translate({-adv / 2:.1f} 4.6)" d="{d}" fill="{th["ink"]}"/>')
    parts.append("</g>")
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{th["ink"]}" stroke-width="1"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{R - 28}" fill="{th["accent"]}"/>')
    parts.append(T("حمزہ", cx, cy + 16, "urdu", 44, anchor="middle", fill=th["onaccent"]))
    parts.append("</g>")
    b += parts

    # statement block
    b.append(f'<g class="fade" style="animation-delay:1.0s">')
    lines = ["I build web products that are judged", "by customers, sales and profit —", "not by how much code went into them."]
    for i, ln in enumerate(lines):
        b.append(T(ln, 38, 384 + i * 30, "sans", 21, fill=th["ink"]))
    b.append(f'<circle class="pulse" cx="45" cy="476" r="5" fill="{th["accent"]}"/>')
    b.append(T("OPEN TO FRONT-END ROLES & FREELANCE BUILDS", 60, 481, "mono", 12.5, tracking=.06, fill=th["mute"]))
    b.append("</g>")
    if season and season.get("ornament"):
        b.append(f'<g class="bob"><g class="fade" style="animation-delay:1.3s">{crescent(668, 352, 26, th["accent"], th["paper"])}</g></g>')
    else:
        b.append(f'<g class="bob"><g class="fade" style="animation-delay:1.3s">{T("↘", 640, 380, "sans", 64, fill=th["accent"])}</g></g>')
    if ctx:
        b.append(sky(th, ctx))

    # marquee band (drawn underneath the name so the q's tail overlaps it)
    y0 = 590
    band = []
    band.append(f'<rect x="0" y="{y0}" width="{W}" height="{H - y0}" fill="{th["ink"]}"/>')
    items = ["NEXT.JS", "REACT", "TYPESCRIPT", "TAILWIND", "NODE.JS", "PRISMA", "POSTGRESQL", "SUPABASE", "MONGODB", "GEMINI", "WEBRTC", "PYTHON"]
    seq, x = [], 0
    for it in items:
        seq.append(T(it, x, y0 + 32, "mono-md", 15, tracking=.14, fill=th["paper"]))
        x += measure(it, "mono-md", 15, .14) + 26
        seq.append(star(x, y0 + 26.5, 7, th["accent"]))
        x += 26
    span = x
    row = "".join(seq)
    band.append(f'<g class="mq" style="--w:-{span:.0f}px">{row}<g transform="translate({span:.0f} 0)">{row}</g><g transform="translate({2 * span:.0f} 0)">{row}</g></g>')
    return svg(W, H, "".join(band + b), css, th, "Hamza Ishaq — full-stack developer in Karachi, Pakistan. Open to front-end roles and freelance builds.")


# ---------------------------------------------------------------- SECTION HEADERS
def section(th, num, title, note):
    W, H = 1200, 170
    css = (f".rv{{animation:rise 1.1s {EASE} both;transform-box:fill-box;}}@keyframes rise{{from{{transform:translateY(105%);}}}}"
           f".draw{{stroke-dasharray:1130;animation:draw 1.8s {EASE} .3s both;}}@keyframes draw{{from{{stroke-dashoffset:1130;}}}}"
           ".fade{animation:fade 1s ease .6s both;}@keyframes fade{from{opacity:0;}}"
           ".sp{animation:sp 9s linear infinite;transform-box:fill-box;transform-origin:center;}@keyframes sp{to{transform:rotate(360deg);}}")
    b = []
    b.append(f'<g class="fade">{T(f"({num:02d})", 38, 52, "mono-md", 15, tracking=.08, fill=th["accent"])}</g>')
    s, w = reveal_word(title, "serif", 96, 34, 134, th["ink"], .05, .035, "cs")
    b.append(s)
    b.append(f'<g class="fade">{star(34 + w + 30, 96, 13, th["accent"], "sp")}</g>')
    b.append(f'<g class="fade">{T(note.upper(), 1164, 130, "mono", 13, anchor="end", tracking=.08, fill=th["mute"])}</g>')
    b.append(f'<line class="draw" x1="36" y1="158" x2="1164" y2="158" stroke="{th["ink"]}" stroke-width="1.2"/>')
    return svg(W, H, "".join(b), css, th, f"{title} — {note}", grain=False)


# ---------------------------------------------------------------- MOTIFS (each in its own panel box)
def m_curewell(th, X, Y, w, h):
    css = ""
    b = [T("DOSES · THIS WEEK", X + 28, Y + 40, "mono", 12, tracking=.08, fill=th["mute"])]
    days = "MTWTFSS"
    rows = ["AM", "PM", "NT"]
    gx0, gy0, dx, dy = X + 110, Y + 82, 54, 50
    for j, dch in enumerate(days):
        b.append(T(dch, gx0 + j * dx, gy0 - 12, "mono", 12, anchor="middle", fill=th["mute"]))
    n = 0
    for i, r in enumerate(rows):
        b.append(T(r, X + 40, gy0 + 24 + i * dy, "mono", 12, fill=th["mute"]))
        for j in range(7):
            cx, cy = gx0 + j * dx, gy0 + 20 + i * dy
            on = 4 + (j * 3 + i) * 3.6
            css += (f"@keyframes cw{n}{{0%,{on:.1f}%{{fill:transparent;transform:scale(.6);}}{on + 2:.1f}%{{fill:{th['accent']};transform:scale(1.15);}}"
                    f"{on + 4:.1f}%,90%{{fill:{th['accent']};transform:scale(1);}}96%,100%{{fill:transparent;transform:scale(.6);}}}}"
                    f".cw{n}{{animation:cw{n} 9s ease infinite;transform-box:fill-box;transform-origin:center;}}")
            b.append(f'<circle class="cw{n}" cx="{cx}" cy="{cy}" r="14" fill="transparent" stroke="{th["ink"]}" stroke-width="1.3"/>')
            n += 1
    # ECG trace
    ey = Y + h - 52
    pts, x = [], X + 28
    while x < X + w - 28:
        pts += [(x, ey), (x + 34, ey), (x + 42, ey - 8), (x + 50, ey), (x + 58, ey + 10), (x + 66, ey - 44), (x + 74, ey + 22), (x + 82, ey), (x + 120, ey)]
        x += 120
    p = " ".join(f"{a:.0f},{c:.0f}" for a, c in pts if a < X + w - 28)
    css += ".ecg{stroke-dasharray:900;animation:ecg 3.6s linear infinite;}@keyframes ecg{from{stroke-dashoffset:900;}to{stroke-dashoffset:-900;}}"
    b.append(f'<polyline points="{p}" fill="none" stroke="{th["rule"]}" stroke-width="1.5"/>')
    b.append(f'<polyline class="ecg" points="{p}" fill="none" stroke="{th["accent"]}" stroke-width="2" stroke-linejoin="round"/>')
    return css, "".join(b)


def m_stash(th, X, Y, w, h):
    ink, acc = th["ink"], th["accent"]
    b = [T("DEVICE TO DEVICE · NO LOGIN", X + 28, Y + 40, "mono", 12, tracking=.08, fill=th["mute"])]
    # laptop
    lx, ly = X + 50, Y + 110
    b.append(f'<rect x="{lx}" y="{ly}" width="170" height="110" rx="6" fill="{th["paper"]}" stroke="{ink}" stroke-width="1.5"/>')
    b.append(f'<path d="M{lx - 20} {ly + 118}h210l-12 12h-186z" fill="{ink}"/>')
    for i in range(4):
        b.append(f'<rect x="{lx + 16}" y="{ly + 18 + i * 20}" width="{[110, 80, 128, 60][i]}" height="7" rx="3.5" fill="{th["rule"]}"/>')
    # phone
    px, py = X + w - 120, Y + 90
    b.append(f'<rect x="{px}" y="{py}" width="78" height="150" rx="14" fill="{th["paper"]}" stroke="{ink}" stroke-width="1.5"/>')
    b.append(f'<rect x="{px + 28}" y="{py + 8}" width="22" height="5" rx="2.5" fill="{ink}"/>')
    css = (".bar{animation:bar 3s ease-in-out infinite;transform-box:fill-box;transform-origin:left;}@keyframes bar{0%,20%{transform:scaleX(0);}70%,100%{transform:scaleX(1);}}"
           ".png{animation:png 3s ease-out infinite;transform-box:fill-box;transform-origin:center;}@keyframes png{0%,60%{opacity:0;transform:scale(.4);}70%{opacity:1;}100%{opacity:0;transform:scale(1.8);}}")
    for i in range(3):
        b.append(f'<rect x="{px + 12}" y="{py + 36 + i * 28}" width="54" height="16" rx="3" fill="{th["panel"]}"/>')
        b.append(f'<rect class="bar" style="animation-delay:{i * .5}s" x="{px + 12}" y="{py + 36 + i * 28}" width="54" height="16" rx="3" fill="{acc}"/>')
    b.append(f'<circle class="png" cx="{px + 39}" cy="{py + 128}" r="9" fill="none" stroke="{acc}" stroke-width="2"/>')
    # arc + traveling files (SMIL for broad support)
    sx, sy, ex, ey = lx + 175, ly + 30, px - 8, py + 60
    arc = f"M{sx} {sy} C {sx + 70} {Y + 30}, {ex - 70} {Y + 30}, {ex} {ey}"
    b.append(f'<path id="arcS" d="{arc}" fill="none" stroke="{th["rule"]}" stroke-width="1.5" stroke-dasharray="4 6"/>')
    for i in range(3):
        b.append(f'<g opacity="0"><path d="M-11 -14h15l7 7v21h-22z" fill="{th["paper"]}" stroke="{ink}" stroke-width="1.4"/><path d="M4 -14v7h7" fill="none" stroke="{ink}" stroke-width="1.4"/>'
                 f'<rect x="-7" y="1" width="14" height="3" fill="{acc}"/>'
                 f'<animateMotion dur="3s" begin="{i}s" repeatCount="indefinite" keyPoints="0;1" keyTimes="0;1" calcMode="spline" keySplines=".6 0 .3 1"><mpath href="#arcS" xlink:href="#arcS"/></animateMotion>'
                 f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.85;1" dur="3s" begin="{i}s" repeatCount="indefinite"/></g>')
    b.append(T("P2P FILES · SCREEN CAST · CLIPBOARD SYNC", X + w / 2, Y + h - 30, "mono", 12, anchor="middle", tracking=.08, fill=th["mute"]))
    return css, "".join(b)


def m_gadi(th, X, Y, w, h):
    ink, acc = th["ink"], th["accent"]
    cx, cy, R = X + 160, Y + 214, 116
    b = [T("MARKETPLACE · PAKISTAN", X + 28, Y + 40, "mono", 12, tracking=.08, fill=th["mute"])]
    b.append(f'<path d="M{cx - R} {cy} A{R} {R} 0 0 1 {cx + R} {cy}" fill="none" stroke="{th["rule"]}" stroke-width="10"/>')
    for i in range(0, 41):
        a = math.pi + math.pi * i / 40
        r1 = R - 20 if i % 5 else R - 32
        b.append(f'<line x1="{cx + (R - 12) * math.cos(a):.1f}" y1="{cy + (R - 12) * math.sin(a):.1f}" x2="{cx + r1 * math.cos(a):.1f}" y2="{cy + r1 * math.sin(a):.1f}" stroke="{ink}" stroke-width="{1.6 if i % 5 == 0 else 1}"/>')
    for i, lab in enumerate(["0", "60", "120", "180", "240"]):
        a = math.pi + math.pi * i / 4
        b.append(T(lab, cx + (R - 50) * math.cos(a), cy + (R - 50) * math.sin(a) + 4, "mono", 11, anchor="middle", fill=th["mute"]))
    css = (f".ndl{{animation:ndl 5s {EASE} infinite;transform-origin:{cx}px {cy}px;}}"
           "@keyframes ndl{0%{transform:rotate(-80deg);}30%{transform:rotate(55deg);}45%{transform:rotate(38deg);}70%{transform:rotate(70deg);}100%{transform:rotate(-80deg);}}"
           f".arcf{{stroke-dasharray:365;animation:arcf 5s {EASE} infinite;}}@keyframes arcf{{0%{{stroke-dashoffset:344;}}30%{{stroke-dashoffset:71;}}45%{{stroke-dashoffset:105;}}70%{{stroke-dashoffset:40;}}100%{{stroke-dashoffset:344;}}}}")
    b.append(f'<path class="arcf" d="M{cx - R} {cy} A{R} {R} 0 0 1 {cx + R} {cy}" fill="none" stroke="{acc}" stroke-width="10"/>')
    b.append(f'<g class="ndl"><path d="M{cx - 4} {cy} L{cx} {cy - R + 26} L{cx + 4} {cy}z" fill="{ink}"/></g><circle cx="{cx}" cy="{cy}" r="10" fill="{acc}"/>')
    # listing ticker
    lx = X + 320
    b.append(T("LISTED TODAY", lx, Y + 96, "mono", 12, tracking=.08, fill=th["mute"]))
    cars = [("Corolla", "4.25M"), ("Civic", "7.80M"), ("Alto", "2.45M"), ("Yaris", "5.10M"), ("Corolla", "4.25M")]
    rows = []
    for i, (n, p) in enumerate(cars):
        yy = i * 46
        rows.append(f'<line x1="{lx}" y1="{yy + 16}" x2="{X + w - 30}" y2="{yy + 16}" stroke="{th["rule"]}"/>')
        rows.append(T(n, lx, yy, "sans", 17, fill=ink))
        rows.append(T("PKR " + p, X + w - 30, yy, "mono-md", 14, anchor="end", fill=acc))
    css += "@keyframes tk{0%,18%{transform:translateY(0)}25%,43%{transform:translateY(-46px)}50%,68%{transform:translateY(-92px)}75%,93%{transform:translateY(-138px)}100%{transform:translateY(-184px)}}.tk{animation:tk 8s ease-in-out infinite;}"
    b.append(f'<clipPath id="tkc"><rect x="{lx - 4}" y="{Y + 112}" width="{w - 330}" height="150"/></clipPath>'
             f'<g clip-path="url(#tkc)"><g class="tk"><g transform="translate(0 {Y + 140})">{"".join(rows)}</g></g></g>')
    b.append(T("SEARCH · FILTER · AI-ASSISTED LISTINGS", X + 28, Y + h - 30, "mono", 12, tracking=.08, fill=th["mute"]))
    return css, "".join(b)


def m_snap(th, X, Y, w, h):
    ink, acc = th["ink"], th["accent"]
    px, py, pw, ph = X + w / 2 - 70, Y + 20, 140, h - 40
    b = [f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="20" fill="{th["paper"]}" stroke="{ink}" stroke-width="1.5"/>']
    posts = []
    for i in range(6):
        yy = i * 92
        posts.append(f'<circle cx="{px + 22}" cy="{yy + 14}" r="7" fill="{th["rule"]}"/><rect x="{px + 34}" y="{yy + 10}" width="{[50, 66, 40][i % 3]}" height="7" rx="3.5" fill="{th["rule"]}"/>')
        posts.append(f'<rect x="{px + 14}" y="{yy + 28}" width="{pw - 28}" height="48" rx="4" fill="{acc if i % 3 == 1 else th["panel"]}"/>')
    css = ".feed{animation:feed 6s linear infinite;}@keyframes feed{to{transform:translateY(-276px);}}"
    css += ".hrt{animation:hrt 2s ease-out infinite;transform-box:fill-box;transform-origin:center bottom;}@keyframes hrt{0%{opacity:0;transform:translateY(10px) scale(.4);}20%{opacity:1;transform:translateY(0) scale(1.1);}100%{opacity:0;transform:translateY(-60px) scale(.8);}}"
    b.append(f'<clipPath id="fc"><rect x="{px + 2}" y="{py + 22}" width="{pw - 4}" height="{ph - 30}"/></clipPath>'
             f'<g clip-path="url(#fc)"><g class="feed"><g transform="translate(0 {py + 30})">{"".join(posts)}</g></g></g>')
    heart = "M0 6 C-10 -4 -18 4 -10 12 L0 21 L10 12 C18 4 10 -4 0 6z"
    for i, (dx, d) in enumerate([(px + pw + 26, 0), (px + pw + 50, .7), (px - 34, 1.3)]):
        b.append(f'<g transform="translate({dx} {Y + h - 70})"><path class="hrt" style="animation-delay:{d}s" d="{heart}" fill="{acc}"/></g>')
    return css, "".join(b)


def m_devshot(th, X, Y, w, h):
    ink, acc = th["ink"], th["accent"]
    bx, by, bw, bh = X + 70, Y + 40, w - 140, h - 70
    b = [f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="8" fill="{th["paper"]}" stroke="{ink}" stroke-width="1.5"/>',
         f'<line x1="{bx}" y1="{by + 24}" x2="{bx + bw}" y2="{by + 24}" stroke="{ink}" stroke-width="1.2"/>']
    for i in range(3):
        b.append(f'<circle cx="{bx + 16 + i * 14}" cy="{by + 12}" r="4" fill="{acc if i == 0 else th["rule"]}"/>')
    b.append(f'<rect x="{bx + 20}" y="{by + 44}" width="{bw * .45:.0f}" height="12" rx="6" fill="{ink}"/>')
    b.append(f'<rect x="{bx + 20}" y="{by + 66}" width="{bw * .3:.0f}" height="8" rx="4" fill="{th["rule"]}"/>')
    b.append(f'<rect x="{bx + 20}" y="{by + 90}" width="{bw - 40}" height="{bh - 110}" rx="4" fill="{th["panel"]}"/>')
    css = (".crn{animation:crn 3.2s cubic-bezier(.7,0,.2,1) infinite;}"
           "@keyframes crn{0%,15%{transform:translate(0,0);}45%,100%{transform:translate(var(--dx),var(--dy));}}"
           ".fl{animation:fl 3.2s linear infinite;}@keyframes fl{0%,46%{opacity:0;}48%{opacity:.85;}60%,100%{opacity:0;}}")
    L = 22
    pad = 26
    for (cx, cy, sx, sy) in [(bx - pad, by - pad, 1, 1), (bx + bw + pad, by - pad, -1, 1), (bx - pad, by + bh + pad, 1, -1), (bx + bw + pad, by + bh + pad, -1, -1)]:
        b.append(f'<path class="crn" style="--dx:{sx * (pad - 8)}px;--dy:{sy * (pad - 8)}px" d="M{cx} {cy + sy * L}V{cy}H{cx + sx * L}" fill="none" stroke="{acc}" stroke-width="3"/>')
    b.append(f'<rect class="fl" x="{X}" y="{Y}" width="{w}" height="{h}" fill="{th["paper"]}" opacity="0"/>')
    return css, "".join(b)


def m_link(th, X, Y, w, h):
    ink, acc = th["ink"], th["accent"]
    long = "https://shop.example.pk/collections/summer?utm_source=ig&ref=8812"
    short = "lnkwhz.app/x7Q"
    cy = Y + h / 2
    lw = measure(long, "mono", 13)
    sx = X + (w - lw) / 2
    css = (".cl{animation:cl 5s cubic-bezier(.7,0,.2,1) infinite;transform-box:fill-box;transform-origin:center;}"
           "@keyframes cl{0%,25%{transform:scaleX(1);}50%,85%{transform:scaleX(.27);}100%{transform:scaleX(1);}}"
           ".lt{animation:lt 5s ease infinite;}@keyframes lt{0%,25%{opacity:1;}35%,90%{opacity:0;}100%{opacity:1;}}"
           ".st{animation:st 5s ease infinite;}@keyframes st{0%,45%{opacity:0;}55%,85%{opacity:1;}92%,100%{opacity:0;}}"
           ".ck{animation:ck 5s ease infinite;}@keyframes ck{0%,55%{opacity:0;transform:translateY(8px);}62%,85%{opacity:1;transform:none;}92%,100%{opacity:0;}}")
    b = [f'<rect class="cl" x="{sx - 18:.0f}" y="{cy - 26}" width="{lw + 36:.0f}" height="52" rx="26" fill="{th["paper"]}" stroke="{ink}" stroke-width="1.5"/>',
         f'<g class="lt">{T(long, sx, cy + 5, "mono", 13, fill=th["mute"])}</g>',
         f'<g class="st" opacity="0">{T(short, X + w / 2, cy + 6, "mono-md", 17, anchor="middle", fill=acc)}</g>',
         f'<g class="ck" opacity="0">{T("SHORT LINK COPIED", X + w / 2, cy + 64, "mono", 12, anchor="middle", tracking=.08, fill=th["mute"])}</g>']
    return css, "".join(b)


def m_vault(th, X, Y, w, h):
    ink, acc = th["ink"], th["accent"]
    cx, cy, R = X + w / 2, Y + h / 2 + 6, 72
    css = (f".dial{{animation:dial 6s {EASE} infinite;transform-origin:{cx}px {cy}px;}}"
           "@keyframes dial{0%{transform:rotate(0)}25%{transform:rotate(130deg)}50%{transform:rotate(-70deg)}75%{transform:rotate(210deg)}100%{transform:rotate(360deg)}}")
    b = [f'<circle cx="{cx}" cy="{cy}" r="{R + 22}" fill="none" stroke="{th["rule"]}" stroke-width="1.5"/>',
         f'<path d="M{cx} {cy - R - 30}l-7 -12h14z" fill="{acc}"/>', '<g class="dial">']
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="{th["paper"]}" stroke="{ink}" stroke-width="1.5"/>')
    for i in range(60):
        a = 2 * math.pi * i / 60
        r1 = R - (14 if i % 5 == 0 else 7)
        b.append(f'<line x1="{cx + R * math.sin(a):.1f}" y1="{cy - R * math.cos(a):.1f}" x2="{cx + r1 * math.sin(a):.1f}" y2="{cy - r1 * math.cos(a):.1f}" stroke="{ink}" stroke-width="{1.6 if i % 5 == 0 else .9}"/>')
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{R - 34}" fill="{th["panel"]}"/><rect x="{cx - 6}" y="{cy - R + 34}" width="12" height="{2 * R - 68}" rx="6" fill="{ink}"/></g>')
    b.append(f'<circle cx="{cx}" cy="{cy}" r="9" fill="{acc}"/>')
    # daily squares
    for i in range(12):
        b.append(f'<rect x="{X + 30 + i * 13}" y="{Y + h - 34}" width="9" height="9" fill="{acc if i in (2,3,5,6,7,9,10,11,12,13) else th["rule"]}"/>')
    b.append(T("ONE DEEP DIVE A DAY", X + w - 24, Y + h - 26, "mono", 12, anchor="end", tracking=.08, fill=th["mute"]))
    return css, "".join(b)



# ---------------------------------------------------------------- SEASONS + SKY
def season_for(day):
    """Seasonal palette and badge text for Pakistani holidays (Hijri dates via Umm al-Qura)."""
    try:
        from hijridate import Gregorian
        h = Gregorian(day.year, day.month, day.day).to_hijri()
        hm, hd = h.month, h.day
    except Exception:
        hm = hd = 0
    if day.month == 8 and day.day <= 15:
        return dict(name="independence", light="#01632E", dark="#35B26B", ring="PAKISTAN ZINDABAD · 14 AUGUST · ", ornament=True)
    if hm == 9:
        return dict(name="ramadan", light="#A8721A", dark="#E2A93F", ring="RAMADAN KAREEM · RAMADAN KAREEM · ", ornament=True)
    if (hm == 10 and hd <= 3) or (hm == 12 and 10 <= hd <= 13):
        return dict(name="eid", light="#0D7A55", dark="#3DC08A", ring="EID MUBARAK · EID MUBARAK · EID MUBARAK · ", ornament=True)
    return None


def seasonal(themes, season):
    if not season:
        return themes
    return {k: dict(v, accent=season[k]) for k, v in themes.items()}


def crescent(cx, cy, r, fill, cut):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + math.pi * i / 5
        rr = r * .34 if i % 2 == 0 else r * .14
        pts.append(f"{cx + r * .55 + rr * math.cos(a):.1f},{cy - r * .2 + rr * math.sin(a):.1f}")
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/><circle cx="{cx + r * .38:.1f}" cy="{cy - r * .18:.1f}" r="{r * .82:.1f}" fill="{cut}"/>'
            f'<polygon points="{" ".join(pts)}" fill="{fill}"/>')


def sky(th, ctx):
    """Little sky dial between the name and the badge: sun or moon riding an arc, Karachi time + weather."""
    cx, cy, R = 806, 236, 112
    h = ctx["hour"]
    rise, sset = ctx.get("sunrise", 6.5), ctx.get("sunset", 17.8)
    day = rise <= h < sset
    if day:
        f = (h - rise) / (sset - rise)
    else:
        span = 24 - sset + rise
        f = ((h - sset) % 24) / span
    a = math.pi * (1 - f)
    px, py = cx + R * math.cos(a), cy - R * math.sin(a)
    out = [f'<g class="fade" style="animation-delay:1.2s">',
           f'<path d="M{cx - R} {cy} A{R} {R} 0 0 1 {cx + R} {cy}" fill="{th["panel"] if not day else "none"}" stroke="{th["rule"]}" stroke-width="1.2" stroke-dasharray="3 5"/>',
           f'<line x1="{cx - R - 14}" y1="{cy}" x2="{cx + R + 14}" y2="{cy}" stroke="{th["ink"]}" stroke-width="1.2"/>']
    if day:
        out.append(f'<circle class="glow" cx="{px:.1f}" cy="{py:.1f}" r="20" fill="{th["accent"]}" opacity=".18"/><circle cx="{px:.1f}" cy="{py:.1f}" r="10" fill="{th["accent"]}"/>')
    else:
        rnd = [(0.22, .55), (0.35, .8), (0.5, .45), (0.63, .78), (0.78, .5), (0.42, .25), (0.7, .28)]
        for i, (fx, fy) in enumerate(rnd):
            sx, sy = cx - R + fx * 2 * R, cy - fy * R * .9
            if (sx - cx) ** 2 + (cy - sy) ** 2 < (R - 8) ** 2:
                out.append(f'<circle class="tw" style="animation-delay:{i * .37:.2f}s" cx="{sx:.1f}" cy="{sy:.1f}" r="1.6" fill="{th["ink"]}"/>')
        out.append(crescent(px, py, 11, th["ink"], th["panel"]))
    label = f'KARACHI · {ctx["time"]}' + (f' · {ctx["temp"]}' if ctx.get("temp") else "")
    out.append(T(label, cx, cy + 24, "mono", 12, anchor="middle", tracking=.08, fill=th["mute"]))
    out.append("</g>")
    return "".join(out)


# ---------------------------------------------------------------- DEVICE FRAMES WITH REAL SCREENSHOTS
def _img_uri(path, width, max_h=None):
    import base64, io
    from PIL import Image
    im = Image.open(path).convert("RGB")
    im = im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)
    if max_h and im.height > max_h:
        im = im.crop((0, 0, width, max_h))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=70, optimize=True, progressive=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode(), im.height


def shots_for(slug):
    d = os.path.join(OUT, "shots")
    dk, mb = os.path.join(d, slug + "-desktop.jpg"), os.path.join(d, slug + "-mobile.jpg")
    return (dk, mb) if os.path.exists(dk) and os.path.exists(mb) else None


def m_shots(slug):
    """Laptop + phone showing the real site; both screens slowly scroll the full page."""
    def motif(th, X, Y, w, h):
        dk, mb = shots_for(slug)
        ink = th["ink"]
        small = h < 300
        lw = (w - 130) if not small else 330
        lw = min(lw, 420)
        lh = lw * 0.625
        lx = X + (w - lw - (60 if not small else 40)) / 2 - (10 if small else 20)
        ly = Y + (h - lh) / 2 - 12
        pw = 104 if not small else 78
        ph = pw * 2.05
        px, py = lx + lw - pw * .35, Y + h - ph - (14 if small else 20)
        ds, dh = _img_uri(dk, int(lw - 16) * 2, max_h=int((lw - 16) * 2 * 3.2))
        ms, mh = _img_uri(mb, int(pw - 10) * 2, max_h=int((pw - 10) * 2 * 4.2))
        sw, sh = lw - 16, lh - 16
        dh, mh = dh / 2, mh / 2
        travel_d = max(0, dh - sh)
        travel_m = max(0, mh - (ph - 28))
        css = (f".sd{slug}{{animation:sd{slug} 14s ease-in-out infinite;}}@keyframes sd{slug}{{0%,12%{{transform:translateY(0)}}55%,67%{{transform:translateY(-{travel_d:.0f}px)}}100%{{transform:translateY(0)}}}}"
               f".sm{slug}{{animation:sm{slug} 11s ease-in-out 1.5s infinite;}}@keyframes sm{slug}{{0%,15%{{transform:translateY(0)}}55%,70%{{transform:translateY(-{travel_m:.0f}px)}}100%{{transform:translateY(0)}}}}"
               f".fl{slug}{{animation:fl{slug} 5s ease-in-out infinite;}}@keyframes fl{slug}{{50%{{transform:translateY(-6px)}}}}")
        b = [f'<rect x="{lx:.0f}" y="{ly:.0f}" width="{lw:.0f}" height="{lh:.0f}" rx="8" fill="{ink}"/>',
             f'<clipPath id="cd{slug}"><rect x="{lx + 8:.0f}" y="{ly + 8:.0f}" width="{sw:.0f}" height="{sh:.0f}" rx="2"/></clipPath>',
             f'<g clip-path="url(#cd{slug})"><image class="sd{slug}" href="{ds}" x="{lx + 8:.0f}" y="{ly + 8:.0f}" width="{sw:.0f}" height="{dh:.0f}"/></g>',
             f'<path d="M{lx - 22:.0f} {ly + lh:.0f}h{lw + 44:.0f}l-10 11h{-(lw + 24):.0f}z" fill="{ink}"/>',
             f'<g class="fl{slug}"><rect x="{px:.0f}" y="{py:.0f}" width="{pw:.0f}" height="{ph:.0f}" rx="16" fill="{ink}"/>',
             f'<clipPath id="cm{slug}"><rect x="{px + 5:.0f}" y="{py + 14:.0f}" width="{pw - 10:.0f}" height="{ph - 28:.0f}" rx="4"/></clipPath>',
             f'<g clip-path="url(#cm{slug})"><image class="sm{slug}" href="{ms}" x="{px + 5:.0f}" y="{py + 14:.0f}" width="{pw - 10:.0f}" height="{mh:.0f}"/></g>',
             f'<rect x="{px + pw / 2 - 12:.0f}" y="{py + 5:.0f}" width="24" height="4" rx="2" fill="{th["panel"]}"/></g>']
        return css, "".join(b)
    return motif


# ---------------------------------------------------------------- CARDS
def wrap(s, font, size, maxw):
    words, lines, cur = s.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if measure(t, font, size) > maxw and cur:
            lines.append(cur); cur = wd
        else:
            cur = t
    lines.append(cur)
    return lines


def tags_row(th, tags, x, y):
    out = []
    for tg in tags:
        tw = measure(tg, "mono", 12, .06)
        out.append(f'<rect x="{x}" y="{y - 17}" width="{tw + 22:.0f}" height="26" rx="13" fill="none" stroke="{th["rule"]}" stroke-width="1.2"/>')
        out.append(T(tg, x + 11, y + .5, "mono", 12, tracking=.06, fill=th["ink"]))
        x += tw + 30
    return "".join(out)


BASE_CARD_CSS = (f".rv{{animation:rise 1.1s {EASE} both;transform-box:fill-box;}}@keyframes rise{{from{{transform:translateY(105%);}}}}"
                 ".fade{animation:fade 1s ease both;}@keyframes fade{from{opacity:0;}}")


def card_big(th, p):
    W, H = 1200, 420
    PX, PY, PW, PH = 620, 30, 550, 360
    css, motif = (m_shots(p["slug"]) if shots_for(p["slug"]) else p["motif"])(th, PX, PY, PW, PH)
    b = [f'<rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" fill="{th["panel"]}"/>', motif,
         f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" fill="none" stroke="{th["rule"]}" stroke-width="1.5"/>']
    b.append(f'<g class="fade">{T(p["num"] + "  /  " + p["kind"].upper(), 40, 66, "mono-md", 13, tracking=.08, fill=th["accent"])}</g>')
    s, w = reveal_word(p["name"], "serif", 108, 36, 172, th["ink"], .1, .04, "cn" + p["num"])
    b.append(s)
    if p.get("badge"):
        b.append(f'<g class="fade" style="animation-delay:.8s">{T(p["badge"].upper(), 40, 214, "mono", 12, tracking=.06, fill=th["mute"])}</g>')
    dy0 = 262 if p.get("badge") else 240
    for i, ln in enumerate(wrap(p["desc"], "sans", 19, 530)):
        b.append(f'<g class="fade" style="animation-delay:.5s">{T(ln, 40, dy0 + i * 28, "sans", 19, fill=th["ink"])}</g>')
    b.append(f'<g class="fade" style="animation-delay:.7s">{tags_row(th, p["tags"], 40, 362)}</g>')
    return svg(W, H, "".join(b), BASE_CARD_CSS + css, th, f'{p["name"]} — {p["desc"]}')


def card_small(th, p):
    W, H = 600, 490
    PX, PY, PW, PH = 24, 24, 552, 230
    css, motif = (m_shots(p["slug"]) if shots_for(p["slug"]) else p["motif"])(th, PX, PY, PW, PH)
    b = [f'<rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" fill="{th["panel"]}"/>', motif,
         f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" fill="none" stroke="{th["rule"]}" stroke-width="1.5"/>']
    b.append(f'<g class="fade">{T(p["num"] + "  /  " + p["kind"].upper(), 30, 292, "mono-md", 12.5, tracking=.08, fill=th["accent"])}</g>')
    s, w = reveal_word(p["name"], "serif", 70, 27, 360, th["ink"], .1, .04, "cn" + p["num"])
    b.append(s)
    for i, ln in enumerate(wrap(p["desc"], "sans", 16.5, 540)[:2]):
        b.append(f'<g class="fade" style="animation-delay:.5s">{T(ln, 30, 396 + i * 23, "sans", 16.5, fill=th["mute"])}</g>')
    b.append(f'<g class="fade" style="animation-delay:.7s">{tags_row(th, p["tags"][:3], 30, 458)}</g>')
    return svg(W, H, "".join(b), BASE_CARD_CSS + css, th, f'{p["name"]} — {p["desc"]}')


BIG = [
    dict(slug="curewell", num="01", kind="Health · AI", name="Curewell", motif=m_curewell, badge="Bano Qabil × Alibaba Cloud AI Hackathon — national finalist",
         desc="A personal health OS for Pakistan: reads handwritten prescriptions, schedules doses around meals, tracks lab results over time.",
         tags=["TypeScript", "React", "Supabase", "OCR", "Offline-first"]),
    dict(slug="gadighar", num="02", kind="Marketplace", name="Gadi Ghar", motif=m_gadi,
         desc="A full-stack car marketplace built for the Pakistani market, with Gemini helping buyers and sellers through listings.",
         tags=["Next.js", "Supabase", "Gemini API", "Tailwind"]),
    dict(slug="snapistan", num="03", kind="Social", name="Snapistan", motif=m_snap,
         desc="A social network with sign-in, posts, likes and notifications, typed end to end from database to UI.",
         tags=["Next.js", "TypeScript", "Prisma", "PostgreSQL"]),
]
SMALL = [
    dict(slug="almuzzammil", num="04", kind="Client · Real estate", name="Al-Muzzamil", motif=m_devshot,
         desc="Website for a Karachi real-estate agency with a decade in the market, built to turn visitors into booked consultations.",
         tags=["Landing page", "Lead capture", "Vercel"]),
    dict(slug="79stauto", num="05", kind="Client · Auto repair", name="79st Auto Center", motif=m_devshot,
         desc="Website for a family-owned Miami repair shop serving drivers since 1974: services up front, 50 years of trust.",
         tags=["Landing page", "Local SEO", "Vercel"]),
]


# ---------------------------------------------------------------- SPLIT-FLAP "NOW" BOARD
def board(th):
    rows = [("NOW BUILDING", "ANYREF"), ("LATEST", "CUREWELL · HACKATHON FINAL"), ("OPEN TO", "FRONT-END ROLES"),
            ("TAKING ON", "FREELANCE BUILDS"), ("BASED IN", "KARACHI · UTC+5")]
    W = 1200
    tw, th_, gap = 30, 44, 4
    cols = 26
    x0 = W - 36 - cols * (tw + gap) + gap
    H = 70 + len(rows) * (th_ + 14) + 30
    css = (f".fp{{animation:fp .5s {EASE} both;transform-box:fill-box;transform-origin:center;}}@keyframes fp{{0%{{transform:scaleY(0);}}60%{{transform:scaleY(1.08);}}100%{{transform:scaleY(1);}}}}"
           ".bl{animation:bl 1.4s steps(1) infinite;}@keyframes bl{50%{opacity:0;}}")
    b = [T("STATUS BOARD · UPDATED NOV 2026", 36, 40, "mono", 12.5, tracking=.08, fill=th["mute"]),
         f'<rect class="bl" x="{W - 48}" y="29" width="12" height="12" fill="{th["accent"]}"/>']
    tile_bg = th["tile"]
    for r, (lab, val) in enumerate(rows):
        y = 70 + r * (th_ + 14)
        b.append(T(lab, 36, y + 28, "mono-md", 14, tracking=.1, fill=th["ink"]))
        for c in range(cols):
            x = x0 + c * (tw + gap)
            ch = val[c] if c < len(val) else " "
            delay = .3 + r * .25 + c * .035
            b.append(f'<g class="fp" style="animation-delay:{delay:.2f}s"><rect x="{x}" y="{y}" width="{tw}" height="{th_}" rx="3" fill="{tile_bg}"/>')
            if ch.strip():
                col = th["accent"] if r == 0 else th["tiletext"]
                b.append(T(ch, x + tw / 2, y + 30, "mono-md", 21, anchor="middle", fill=col))
            b.append(f'<line x1="{x}" y1="{y + th_ / 2}" x2="{x + tw}" y2="{y + th_ / 2}" stroke="{th["paper"]}" stroke-opacity=".5" stroke-width="1"/></g>')
    alt = "; ".join(f"{a.title()}: {v.title()}" for a, v in rows)
    return svg(W, H, "".join(b), css, th, "Right now — " + alt, grain=False)


# ---------------------------------------------------------------- TOOLBOX
def toolbox(th):
    rows = [("INTERFACE", ["Next.js", "React", "TypeScript", "Tailwind"]),
            ("SERVER", ["Node.js", "Express", "Prisma", "REST"]),
            ("DATA", ["PostgreSQL", "Supabase", "MongoDB"]),
            ("AI", ["Gemini", "Vision OCR", "LLM workflows"]),
            ("SHIPPING", ["Vercel", "GitHub Actions", "Vitest", "Python"])]
    W, rh = 1200, 76
    H = 20 + len(rows) * rh + 10
    css = (f".rw{{animation:rw 1s {EASE} both;}}@keyframes rw{{from{{opacity:0;transform:translateX(-24px);}}}}"
           ".hl{animation:hl 10s ease-in-out infinite;transform-box:fill-box;transform-origin:left;}")
    b = []
    for i, (lab, items) in enumerate(rows):
        y = 20 + i * rh
        p0, p1 = i * 20, i * 20 + 16
        css += f"@keyframes h{i}{{0%,{p0}%{{transform:scaleX(0);transform-origin:left;}}{p0 + 6}%,{p1 - 4}%{{transform:scaleX(1);transform-origin:left;}}{p1}%,100%{{transform:scaleX(0);transform-origin:right;}}}}.h{i}{{animation:h{i} 10s cubic-bezier(.7,0,.2,1) infinite;transform-box:fill-box;}}"
        b.append(f'<g class="rw" style="animation-delay:{.15 + i * .12:.2f}s">')
        b.append(f'<rect class="h{i}" style="transform:scaleX(0)" x="0" y="{y}" width="{W}" height="{rh}" fill="{th["panel"]}"/>')
        b.append(T(lab, 36, y + 46, "mono-md", 13, tracking=.1, fill=th["accent"]))
        x = 250
        for j, it in enumerate(items):
            b.append(T(it, x, y + 52, "serif" if j % 2 == 0 else "serif-it", 46, fill=th["ink"]))
            x += measure(it, "serif" if j % 2 == 0 else "serif-it", 46) + 18
            if j < len(items) - 1:
                b.append(T("/", x, y + 50, "serif", 40, fill=th["rule"]))
                x += 30
        b.append(f'<line x1="36" y1="{y + rh}" x2="1164" y2="{y + rh}" stroke="{th["rule"]}"/></g>')
    alt = "; ".join(f"{a.title()}: {', '.join(v)}" for a, v in rows)
    return svg(W, H, "".join(b), css, th, "Toolbox — " + alt, grain=False)


# ---------------------------------------------------------------- WORK WITH ME
def work(th):
    W, H = 1200, 400
    css = (f".rw{{animation:rw 1s {EASE} both;}}@keyframes rw{{from{{opacity:0;transform:translateY(16px);}}}}"
           ".pulse{animation:pulse 2s ease-in-out infinite;}@keyframes pulse{50%{opacity:.2;}}"
           f".ul{{animation:ul 1.2s {EASE} .6s both;transform-box:fill-box;transform-origin:left;}}@keyframes ul{{from{{transform:scaleX(0);}}}}")
    cols = [("(A)  FOR TEAMS HIRING", "Front-end roles", ["React, Next.js, TypeScript and Tailwind", "Karachi on-site or fully remote", "CV and portfolio on request"]),
            ("(B)  FOR BUSINESSES", "Websites that sell", ["Business sites, online stores, landing pages", "Built through Albatix, my studio", "Send the goal, get a scoped plan back"])]
    b = []
    for k, (tag, head, items) in enumerate(cols):
        x = 36 + k * 582
        b.append(f'<g class="rw" style="animation-delay:{.15 + k * .2:.2f}s">')
        b.append(f'<rect x="{x}" y="20" width="546" height="350" fill="{th["panel"] if k == 0 else th["ink"]}"/>')
        fg = th["ink"] if k == 0 else th["paper"]
        b.append(T(tag, x + 32, 64, "mono-md", 13, tracking=.1, fill=th["accent"]))
        b.append(T(head, x + 28, 150, "serif" if k == 0 else "serif-it", 66, fill=fg))
        b.append(f'<rect class="ul" x="{x + 32}" y="170" width="{measure(head, "serif" if k == 0 else "serif-it", 66) - 4:.0f}" height="3" fill="{th["accent"]}"/>')
        for i, it in enumerate(items):
            y = 232 + i * 40
            b.append(star(x + 40, y - 6, 6, th["accent"]))
            b.append(T(it, x + 60, y, "sans", 19, fill=fg))
        b.append("</g>")
    b.append(f'<circle class="pulse" cx="1150" cy="58" r="6" fill="{th["accent"] if False else th["paper"]}"/>')
    b.append(T("AVAILABLE NOW", 1134, 63, "mono-md", 12, anchor="end", tracking=.1, fill=th["paper"]))
    return svg(W, H, "".join(b), css, th, "Work with me. For teams hiring: front-end roles, React, Next.js, TypeScript, Karachi or remote, CV on request. For businesses: websites, online stores and landing pages through Albatix.", grain=False)


def button(th, label, primary):
    w = measure(label, "mono-md", 15, .1) + 110
    W, H = int(w), 64
    bg, fg = (th["accent"], th["onaccent"]) if primary else (th["paper"], th["ink"])
    css = ".ar{animation:ar 1.6s ease-in-out infinite;}@keyframes ar{50%{transform:translateX(6px);}}"
    b = [f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="31" fill="{bg}" stroke="{th["ink"] if not primary else bg}" stroke-width="1.5"/>',
         T(label, 32, 38, "mono-md", 15, tracking=.1, fill=fg), f'<g class="ar">{T("→", W - 58, 40, "sans", 22, fill=fg)}</g>']
    return svg(W, H, "".join(b), css, dict(th, paper="none") if False else th, label, grain=False).replace(f'<rect width="{W}" height="{H}" fill="{th["paper"]}"/>', "", 1)



# ---------------------------------------------------------------- FOOTER
def footer(th):
    W, H = 1200, 470
    css = (f".rv{{animation:rise 1.2s {EASE} both;transform-box:fill-box;}}@keyframes rise{{from{{transform:translateY(105%);}}}}"
           ".fade{animation:fade 1s ease .9s both;}@keyframes fade{from{opacity:0;}}"
           ".ar{animation:ar 1.8s ease-in-out infinite;}@keyframes ar{50%{transform:translateX(10px);}}"
           ".sp{animation:sp 12s linear infinite;transform-box:fill-box;transform-origin:center;}@keyframes sp{to{transform:rotate(360deg);}}"
           ".sig{fill-opacity:0;stroke-dasharray:1400;stroke-dashoffset:0;animation:sig 4.5s cubic-bezier(.6,0,.3,1) 1s both, sigf .8s ease 4.6s forwards;}"
           "@keyframes sig{from{stroke-dashoffset:1400;}}@keyframes sigf{to{fill-opacity:1;}}"
           "@media (prefers-reduced-motion: reduce){.sig{fill-opacity:1;}}")
    b = [f'<line x1="36" y1="30" x2="1164" y2="30" stroke="{th["ink"]}" stroke-width="1.2"/>',
         f'<g class="fade">{T("(07)  SAY HELLO", 36, 66, "mono-md", 13, tracking=.08, fill=th["accent"])}</g>']
    s1, w1 = reveal_word("Got a business problem?", "serif", 100, 30, 176, th["ink"], .1, .025, "f1")
    s2, w2 = reveal_word("Let's ship the fix.", "serif-it", 100, 30, 280, th["accent"], .4, .025, "f2")
    b += [s1, s2]
    b.append(f'<g class="fade">{star(30 + w2 + 56, 246, 30, th["ink"], "sp")}</g>')
    sw = measure("Hamza Ishaq", "script", 96)
    b.append(T("Hamza Ishaq", 1150 - sw, 360, "script", 96, class_="sig", fill=th["ink"], stroke=th["ink"], stroke_width="1.1"))
    b.append('<g class="fade">')
    b.append(T("hamzaisadev@gmail.com", 36, 352, "mono-md", 20, fill=th["ink"]))
    em = measure("hamzaisadev@gmail.com", "mono-md", 20)
    b.append(f'<g class="ar">{T("→", 36 + em + 14, 353, "sans", 22, fill=th["accent"])}</g>')
    b.append(T("Tell me the goal, the pages you need and a rough budget — I'll reply with a scoped plan.", 36, 384, "sans", 15, fill=th["mute"]))
    b.append(f'<line x1="36" y1="416" x2="1164" y2="416" stroke="{th["rule"]}"/>')
    b.append(T("SET IN INSTRUMENT SERIF, GEIST, NOTO NASTALIQ URDU & MRS SAINT DELAFIELD — EVERY LETTER OUTLINED TO VECTOR", 36, 446, "mono", 11, tracking=.08, fill=th["mute"]))
    b.append(T("© 2026 HAMZA ISHAQ · KARACHI", 1164, 446, "mono", 11, anchor="end", tracking=.08, fill=th["mute"]))
    b.append("</g>")
    return svg(W, H, "".join(b), css, th, "Got a business problem? Let's ship the fix. Email hamzaisadev@gmail.com")


SECTIONS = [(1, "Selected work", "products + client sites"), (2, "Right now", "what's on the desk"),
            (3, "Toolbox", "what I reach for"), (4, "Pulse", "commits, streaks, hours"),
            (5, "Work with me", "two ways in"), (6, "Guestbook", "sign it, vote, ask")]

def build(out=None, ctx=None, day=None):
    """Write every static asset. ctx = Karachi time/weather for the hero sky; day picks the seasonal palette."""
    import datetime as _dt
    out = out or OUT
    os.makedirs(out, exist_ok=True)
    season = season_for(day or _dt.date.today())
    for tn, th in seasonal(THEMES, season).items():
        files = {"hero": hero(th, ctx, season), "now": board(th), "toolbox": toolbox(th), "footer": footer(th), "work": work(th),
                 "btn-project": button(th, "START A PROJECT", True), "btn-cv": button(th, "REQUEST MY CV", False),
                 "btn-sign": button(th, "SIGN THE GUESTBOOK", True), "btn-vote": button(th, "VOTE", False),
                 "btn-ama": button(th, "ASK ME ANYTHING", False)}
        for n, t, note in SECTIONS:
            files[f"h{n:02d}"] = section(th, n, t, note)
        for p in BIG:
            files["card-" + p["slug"]] = card_big(th, p)
        for p in SMALL:
            files["card-" + p["slug"]] = card_small(th, p)
        for lab in ("PORTFOLIO", "LINKEDIN", "X", "YOUTUBE", "EMAIL"):
            files["nav-" + lab.lower()] = button(th, lab, lab == "PORTFOLIO")
        for k, v in files.items():
            with open(f"{out}/{k}-{tn}.svg", "w") as f:
                f.write(v)
    return season


if __name__ == "__main__":
    build()
    print("ok", len(os.listdir(OUT)))
