"""Shape text with HarfBuzz and emit outlined SVG paths (no font dependency in the browser)."""
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from functools import lru_cache

import os
FONT_DIR = os.environ.get("FONT_DIR", os.path.join(os.path.dirname(__file__), "fonts")) + "/"


@lru_cache(None)
def _load(name):
    path = FONT_DIR + name + ".ttf"
    blob = hb.Blob.from_file_path(path)
    face = hb.Face(blob)
    font = hb.Font(face)
    tt = TTFont(path)
    return font, tt, tt.getGlyphSet(), tt["head"].unitsPerEm


def measure(text, font="sans", size=16, tracking=0.0):
    return _shape(text, font, size, tracking)[1]


def _shape(text, font, size, tracking):
    hbfont, tt, gs, upem = _load(font)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hbfont, buf, {"kern": True, "liga": True})
    s = size / upem
    order = tt.getGlyphOrder()
    glyphs, x = [], 0.0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        glyphs.append((order[info.codepoint], x + pos.x_offset * s, pos.y_offset * s))
        x += pos.x_advance * s + tracking * size
    if glyphs:
        x -= tracking * size
    return glyphs, x


def text(t, x, y, font="sans", size=16, anchor="start", tracking=0.0, **attrs):
    """Return an SVG <path> for text whose baseline starts at (x, y)."""
    glyphs, w = _shape(t, font, size, tracking)
    if anchor == "middle":
        x -= w / 2
    elif anchor == "end":
        x -= w
    _, _, gs, upem = _load(font)
    s = size / upem
    pen = SVGPathPen(gs)
    for name, gx, gy in glyphs:
        tp = TransformPen(pen, (s, 0, 0, -s, x + gx, y - gy))
        gs[name].draw(tp)
    d = pen.getCommands()
    # round numbers to keep files small
    import re
    d = re.sub(r"-?\d+\.\d+", lambda m: f"{float(m.group()):.1f}".rstrip("0").rstrip("."), d)
    a = " ".join(f'{k.rstrip("_").replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<path d="{d}" {a}/>'


def glyphs(t, font="sans", size=16, tracking=0.0):
    """Per-glyph outlined paths positioned at origin; returns ([(d, x_offset, advance)], total_width)."""
    import re
    gl, w = _shape(t, font, size, tracking)
    _, _, gs, upem = _load(font)
    s = size / upem
    out = []
    for i, (name, gx, gy) in enumerate(gl):
        pen = SVGPathPen(gs)
        gs[name].draw(TransformPen(pen, (s, 0, 0, -s, 0, -gy)))
        d = re.sub(r"-?\d+\.\d+", lambda m: f"{float(m.group()):.1f}".rstrip("0").rstrip("."), pen.getCommands())
        nxt = gl[i + 1][1] if i + 1 < len(gl) else w
        out.append((d, gx, nxt - gx))
    return out, w


if __name__ == "__main__":
    # one-off: convert @fontsource woff2 files to the TTFs gen.py expects
    from fontTools.ttLib import TTFont
    F = "node_modules/@fontsource/"
    m = {"serif": "instrument-serif/files/instrument-serif-latin-400-normal.woff2",
         "serif-it": "instrument-serif/files/instrument-serif-latin-400-italic.woff2",
         "sans": "geist-sans/files/geist-sans-latin-400-normal.woff2",
         "sans-md": "geist-sans/files/geist-sans-latin-500-normal.woff2",
         "sans-sb": "geist-sans/files/geist-sans-latin-600-normal.woff2",
         "mono": "geist-mono/files/geist-mono-latin-400-normal.woff2",
         "mono-md": "geist-mono/files/geist-mono-latin-500-normal.woff2",
         "urdu": "noto-nastaliq-urdu/files/noto-nastaliq-urdu-arabic-400-normal.woff2",
         "script": "mrs-saint-delafield/files/mrs-saint-delafield-latin-400-normal.woff2"}
    os.makedirs(FONT_DIR, exist_ok=True)
    for k, v in m.items():
        f = TTFont(F + v); f.flavor = None; f.save(FONT_DIR + k + ".ttf")
    print("fonts ready in", FONT_DIR)
