"""Shape text with HarfBuzz and draw it from the font's own outlines, glyph boundaries marked."""
import sys, numpy as np, uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from PIL import Image, ImageDraw
import cv2

MARKS = False

class P(BasePen):
    def __init__(s, gs): super().__init__(gs); s.polys = []; s.cur = []
    def _moveTo(s, p): s.cur = [p]
    def _lineTo(s, p): s.cur.append(p)
    def _curveToOne(s, a, b, c):
        p0 = np.array(s.cur[-1]); a, b, c = map(np.array, (a, b, c))
        for t in np.linspace(0, 1, 14)[1:]: s.cur.append(tuple((1-t)**3*p0 + 3*(1-t)**2*t*a + 3*(1-t)*t*t*b + t**3*c))
    def _qCurveToOne(s, a, b):
        p0 = np.array(s.cur[-1]); a, b = np.array(a), np.array(b)
        for t in np.linspace(0, 1, 12)[1:]: s.cur.append(tuple((1-t)**2*p0 + 2*(1-t)*t*a + t*t*b))
    def _closePath(s): s.polys.append(s.cur); s.cur = []

def draw_line(font_path, text, d, x_right, y_base, sc, marks=True):
    blob = hb.Blob.from_file_path(font_path); face = hb.Face(blob); font = hb.Font(face)
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(font, buf, {})
    tt = TTFont(font_path); gs = tt.getGlyphSet(); order = tt.getGlyphOrder()
    total = sum(p.x_advance for p in buf.glyph_positions)
    x = x_right - total * sc
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        name = order[info.codepoint]; p = P(gs); gs[name].draw(p)
        ox = x + pos.x_offset * sc; oy = y_base - pos.y_offset * sc
        pts = [np.round(np.array([(ox + px * sc, oy - py * sc) for px, py in poly]) * 8).astype(np.int32) for poly in p.polys if len(poly) > 2]
        if pts:
            m = np.zeros((d._image.height, d._image.width), np.uint8)
            cv2.fillPoly(m, pts, 1, cv2.LINE_AA, shift=3)             # even-odd: counters stay open
            arr = np.array(d._image); arr[m > 0] = (20, 22, 30); d._image.paste(Image.fromarray(arr))
        if marks and pos.x_advance and MARKS: d.line([(x, y_base - 60), (x, y_base + 60)], fill=(230, 60, 60))
        x += pos.x_advance * sc

if __name__ == '__main__':
    out, *lines = sys.argv[1:]
    SC = 0.2
    im = Image.new('RGB', (2000, 360 * len(lines)), 'white'); d = ImageDraw.Draw(im)
    for i, t in enumerate(lines):
        y = 250 + i * 360
        d.line([(0, y), (2000, y)], fill=(120, 200, 140))
        draw_line('OmarHand.ttf', t, d, 1960, y, SC)
    im.save(out)
