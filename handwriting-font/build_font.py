"""Scanned/photographed template pages -> joined Arabic TTF.
usage: python3 build_font.py out.ttf "Font Name" page1.jpg [page2.jpg page3.jpg]"""
import sys
import numpy as np, cv2, potrace
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from glyphs import *

SCALE = 3.5      # font units per template pixel
UP = 2           # upsample factor before tracing (smooths pen wobble)
OVERLAP, SB = 22, 45
THRESH = 150


def load_page(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    k = max(15, (img.shape[1] // 60) | 1)
    bg = cv2.morphologyEx(img, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    bg = cv2.GaussianBlur(bg, (0, 0), k / 3)
    norm = np.clip(img.astype(np.float32) / np.maximum(bg, 1) * 255, 0, 255).astype(np.uint8)
    # find the 4 corner squares
    _, b = cv2.threshold(norm, 100, 255, cv2.THRESH_BINARY_INV)
    n, _, st, cen = cv2.connectedComponentsWithStats(b)
    A = img.shape[0] * img.shape[1]
    c = [cen[i] for i in range(1, n) if 0.0002 * A < st[i, 4] < 0.02 * A
         and 0.75 < st[i, 2] / st[i, 3] < 1.33 and st[i, 4] / (st[i, 2] * st[i, 3]) > 0.85]
    if len(c) < 4:
        raise SystemExit(f'{path}: could not see the 4 black corner squares')
    c = np.array(c)
    s, d = c.sum(1), c[:, 0] - c[:, 1]
    src = np.float32([c[s.argmin()], c[d.argmax()], c[d.argmin()], c[s.argmax()]])  # TL TR BL BR
    M = cv2.getPerspectiveTransform(src, np.float32(MARKER_CENTERS))
    return cv2.warpPerspective(norm, M, (PAGE_W, PAGE_H), flags=cv2.INTER_CUBIC, borderValue=255)


def trace(mask):
    bm = potrace.Bitmap(~mask)
    return bm.trace(turdsize=8, alphamax=1.05, opticurve=True, opttolerance=0.3)


def glyph_from_cell(cell, slot):
    inset = 6
    c = cell[inset:-inset, inset:-inset]
    c = cv2.resize(c, None, fx=UP, fy=UP, interpolation=cv2.INTER_CUBIC)
    c = cv2.GaussianBlur(c, (0, 0), 1.2 * UP / 2)
    ink = c < THRESH
    n, lab, st, _ = cv2.connectedComponentsWithStats(ink.astype(np.uint8))
    for i in range(1, n):
        if st[i, 4] < 12 * UP * UP:
            ink[lab == i] = False
    if ink.sum() < 40 * UP * UP:
        return None
    ys, xs = np.where(ink)
    xmin, xmax = xs.min(), xs.max()
    base = (BASE_Y - inset) * UP
    jl, jr = slot['joins']
    left = -OVERLAP / 2 if jl else SB
    right = -OVERLAP / 2 if jr else SB
    width = (xmax - xmin) / UP * SCALE
    adv = int(round(left + width + right))
    pen = TTGlyphPen(None)
    cp = Cu2QuPen(pen, 1.0, reverse_direction=False)
    f = lambda p: (round((p.x - xmin) / UP * SCALE + left, 1), round((base - p.y) / UP * SCALE, 1))
    paths = []
    for curve in trace(ink):
        pts = []
        sp = f(curve.start_point)
        cp.moveTo(sp)
        for s in curve.segments:
            if s.is_corner:
                cp.lineTo(f(s.c)); cp.lineTo(f(s.end_point))
            else:
                cp.curveTo(f(s.c1), f(s.c2), f(s.end_point))
        cp.closePath()
    return pen.glyph(), adv


def build(out, family, pages):
    sl = slots()
    order = ['.notdef', 'space']
    glyphs, metrics, cmap, missing = {}, {}, {0x20: 'space', 0xA0: 'space'}, []
    nd = TTGlyphPen(None)
    nd.moveTo((60, 0)); nd.lineTo((60, 700)); nd.lineTo((440, 700)); nd.lineTo((440, 0)); nd.closePath()
    glyphs['.notdef'], metrics['.notdef'] = nd.glyph(), (520, 60)
    glyphs['space'], metrics['space'] = TTGlyphPen(None).glyph(), (320, 0)
    for p, path in enumerate(pages):
        page = load_page(path)
        for i, s in enumerate(sl[p * PER_PAGE:(p + 1) * PER_PAGE]):
            x, y, w, h = cell_rect(i)
            r = glyph_from_cell(page[y:y + h, x:x + w], s)
            if r is None:
                missing.append(s['name']); continue
            g, adv = r
            glyphs[s['name']] = g
            g.recalcBounds(None)
            metrics[s['name']] = (adv, int(g.xMin) if g.numberOfContours else 0)
            order.append(s['name'])
            if s['cmap']:
                cmap[s['cmap']] = s['name']
    if 'lamalef.fina' in glyphs: cmap[0xFEFC] = 'lamalef.fina'
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(order if '.notdef' == order[0] else ['.notdef'] + order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf({n: glyphs[n] for n in fb.font.getGlyphOrder()})
    fb.setupHorizontalMetrics({n: metrics[n] for n in fb.font.getGlyphOrder()})
    fb.setupHorizontalHeader(ascent=900, descent=-500)
    fb.setupNameTable({'familyName': family, 'styleName': 'Regular'})
    fb.setupOS2(sTypoAscender=900, sTypoDescender=-500, usWinAscent=1100, usWinDescent=700, sTypoLineGap=0)
    fb.setupPost()
    have = set(glyphs)
    def sub(form):
        return ' '.join(f'sub {gname(c)} by {gname(c, form)};' for c, k, _ in LETTERS
                        if gname(c) in have and gname(c, form) in have and (k == 'D' or (k == 'R' and form == 'fina')))
    fea = 'languagesystem DFLT dflt;\nlanguagesystem arab dflt;\n'
    for form in ('init', 'medi', 'fina'):
        fea += f'feature {form} {{ {sub(form)} }} {form};\n'
    lig = []
    if {'uni0644.init', 'uni0627.fina', 'lamalef'} <= have:
        lig.append('sub uni0644.init uni0627.fina by lamalef;')
    if {'uni0644.medi', 'uni0627.fina', 'lamalef.fina'} <= have:
        lig.append('sub uni0644.medi uni0627.fina by lamalef.fina;')
    if lig: fea += 'feature rlig { ' + ' '.join(lig) + ' } rlig;\n'
    addOpenTypeFeaturesFromString(fb.font, fea)
    fb.save(out)
    print('saved', out, '-', len(glyphs), 'glyphs;', 'missing:', missing or 'none')


if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2], sys.argv[3:])
