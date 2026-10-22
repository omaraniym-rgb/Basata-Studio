"""Stage 3: traced glyphs -> OpenType Arabic font (TTF + WOFF2)."""
import sys, pickle, numpy as np, cv2, potrace
sys.path.insert(0, '../pens')
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.transformPen import TransformPen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.ttLib import TTFont
from pen6 import render6
from stage2 import PEN, R_W
from names import BASE, PRES, OFF
from punctuation import SHAPES

FAMILY = sys.argv[1] if len(sys.argv) > 1 else 'Omar Hand'
ALEF_UNITS = 620
MARKS = ['fatha', 'damma', 'kasra', 'fathatan', 'dammatan', 'kasratan', 'sukun']
ALL_MARKS = MARKS + ['shadda']


def trace(img):
    bm = potrace.Bitmap(~img)
    return bm.trace(turdsize=30, alphamax=1.0, opticurve=True, opttolerance=0.4)


def draw(pen, path, f):
    for c in path:
        pen.moveTo(f(c.start_point))
        for s in c.segments:
            if s.is_corner:
                pen.lineTo(f(s.c)); pen.lineTo(f(s.end_point))
            else:
                pen.curveTo(f(s.c1), f(s.c2), f(s.end_point))
        pen.closePath()


def glyph_from_img(img, x0, base, U):
    pen = TTGlyphPen(None)
    qp = Cu2QuPen(pen, 0.8, reverse_direction=True)
    draw(qp, trace(img), lambda p: (round((p.x - x0) * U), round((base - p.y) * U)))
    return pen.glyph()


def synth(shape, U):
    """Render a punctuation shape (pen-width units) with the pen."""
    pad = 3 * R_W; s = R_W
    pts = [st * [s, -s] + [pad, 12 * s + pad] for st in shape.get('strokes', [])]
    strokes = []
    for P in pts:
        strokes.append(dict(p=P, r=np.full(len(P), R_W / 2), closed=False, free=[not shape.get('join'), not shape.get('join')],
                            bridged=[False, False], loop=None, stem=None, line=-1, word=-1))
    for (dx, dy) in shape.get('dots', []):
        c = np.array([[dx * s + pad, 12 * s + pad - dy * s]])
        strokes.append(dict(p=np.vstack([c - [0.35 * s, -0.35 * s], c + [0.35 * s, -0.35 * s]]), r=np.full(2, R_W * 0.62),
                            closed=False, free=[False, False], bridged=[False, False], loop=None, stem=None, dot=True, line=-1, word=-1))
    A = dict(strokes=strokes, bridges=[], words={}, lines=[], w=R_W, rmed=R_W / 2, stem_target=0)
    H, W = int(22 * s + 2 * pad), int(shape['w'] * s + 2 * pad + 4 * s)
    img = render6(A, (H, W), snap=0, level=0, heads=True, **PEN)
    if shape.get('flip'): img = img[:, ::-1]; xs = np.where(img.any(0))[0]; shift = W - (pad + shape['w'] * s)
    base = 12 * s + pad
    left = pad if not shape.get('flip') else W - pad - shape['w'] * s
    return img, left, left + shape['w'] * s, base


def main(stage2='stage2.pkl', out='OmarHand'):
    D = pickle.load(open(stage2, 'rb'))
    G, alef_u = D['glyphs'], D['alef_u']
    U = ALEF_UNITS / (alef_u * R_W)
    glyphs, adv, cmap = {}, {}, {}
    anchors = {}
    # letters
    for name, g in G.items():
        if g['form'] == 'mark':
            continue
        glyphs[name] = glyph_from_img(g['img'], g['left'], g['base'], U)
        adv[name] = int(round((g['right'] - g['left']) * U))
        x0, y0, x1, y1 = g['ink']
        cx = ((max(x0, g['left']) + min(x1, g['right'])) / 2 - g['left']) * U
        anchors[name] = dict(top=(round(cx), round((g['base'] - y0) * U + 0.9 * R_W * U)),
                             bottom=(round(cx), round((g['base'] - y1) * U - 0.9 * R_W * U)))
    # marks: zero width, anchored at their own centre-bottom (top marks) / centre-top (bottom marks)
    mark_anchor = {}
    for name in MARKS:
        g = G[name]; x0, y0, x1, y1 = g['ink']
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        k = 0.62                                   # marks are written smaller than letters in Ruqʿah
        img = cv2.resize(g['img'].astype(np.uint8), None, fx=k, fy=k, interpolation=cv2.INTER_AREA) > 0
        glyphs[name] = glyph_from_img(img, cx * k, cy * k, U)
        adv[name] = 0
        hh = (y1 - y0) / 2 * k * U
        mark_anchor[name] = (G[name]['side'], (0, round(-hh) if G[name]['side'] == 'top' else round(hh)))
    # punctuation + tatweel
    for name, sh in SHAPES.items():
        img, l, r, base = synth(sh, U)
        if sh.get('mark'):
            k = 0.62; img = cv2.resize(img.astype(np.uint8), None, fx=k, fy=k, interpolation=cv2.INTER_AREA) > 0
            ys, xs = np.where(img); cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
            glyphs[name] = glyph_from_img(img, cx, cy, U); adv[name] = 0; cmap[sh['cp']] = name
            mark_anchor[name] = ('top', (0, round(-(ys.max() - ys.min()) / 2 * U)))
            continue
        glyphs[name] = glyph_from_img(img, l, base, U)
        adv[name] = int(round((r - l) * U))
        if sh['cp']: cmap[sh['cp']] = name
        if sh.get('letter'):
            anchors[name] = dict(top=(adv[name] // 2, int(1.6 * R_W * U)), bottom=(adv[name] // 2, int(-1.6 * R_W * U)))
    # space, notdef
    nd = TTGlyphPen(None)
    for (a, b, c, d) in [(60, 0, 460, 700)]:
        nd.moveTo((a, b)); nd.lineTo((a, d)); nd.lineTo((c, d)); nd.lineTo((c, b)); nd.closePath()
    glyphs['.notdef'], adv['.notdef'] = nd.glyph(), 520
    glyphs['space'], adv['space'] = TTGlyphPen(None).glyph(), int(0.36 * ALEF_UNITS)
    cmap[0x20] = cmap[0xA0] = 'space'
    # character map
    for name in glyphs:
        base, _, form = name.partition('.')
        if base in BASE and form == '':
            cmap[BASE[base]] = name
        if base in BASE and BASE[base] in PRES and form in OFF:
            cmap[PRES[BASE[base]] + OFF[form]] = name
    cmap[0xFEFB] = 'lamalef'; cmap[0xFEFC] = 'lamalef.fina'
    order = ['.notdef', 'space'] + sorted(n for n in glyphs if n not in ('.notdef', 'space'))
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf({n: glyphs[n] for n in order})
    for n in order: glyphs[n].recalcBounds(fb.font['glyf'])
    fb.setupHorizontalMetrics({n: (adv[n], getattr(glyphs[n], 'xMin', 0) if glyphs[n].numberOfContours else 0) for n in order})
    ymax = max(getattr(glyphs[n], 'yMax', 0) for n in order); ymin = min(getattr(glyphs[n], 'yMin', 0) for n in order)
    asc, desc = int(ymax + 60), int(ymin - 60)
    fb.setupHorizontalHeader(ascent=asc, descent=desc, lineGap=0)
    fb.setupNameTable({'familyName': FAMILY, 'styleName': 'Regular', 'uniqueFontIdentifier': FAMILY.replace(' ', '') + '-Regular-1.0',
                       'fullName': FAMILY + ' Regular', 'psName': FAMILY.replace(' ', '') + '-Regular', 'version': 'Version 1.000',
                       'designer': 'Drawn by hand, built with Claude', 'description': 'A Ruqʿah handwriting font made from one hand.'})
    fb.setupOS2(sTypoAscender=asc, sTypoDescender=desc, sTypoLineGap=0, usWinAscent=asc, usWinDescent=-desc,
                ulUnicodeRange1=(1 << 13), ulCodePageRange1=(1 << 6), achVendID='BSTA', fsType=0)
    fb.setupPost()
    # ---- OpenType layout ----
    have = set(glyphs)
    letters = [b for b in BASE if b in have and b not in ALL_MARKS and not b.startswith('digit')]
    def sub(form):
        return ' '.join(f'sub {b} by {b}.{form};' for b in letters if f'{b}.{form}' in have)
    fea = 'languagesystem DFLT dflt;\nlanguagesystem arab dflt;\n'
    for form in ('init', 'medi', 'fina'):
        fea += f'feature {form} {{ {sub(form)} }} {form};\n'
    fea += 'feature rlig { sub lam.init alef.fina by lamalef; sub lam.medi alef.fina by lamalef.fina; } rlig;\n'
    fea += ''.join(f'markClass {m} <anchor {a[1][0]} {a[1][1]}> @{"TOP" if a[0] == "top" else "BOTTOM"};\n' for m, a in mark_anchor.items())
    bases = [n for n in glyphs if n in anchors]
    fea += 'feature mark {\n' + ''.join(
        f'  pos base {n} <anchor {anchors[n]["top"][0]} {anchors[n]["top"][1]}> mark @TOP <anchor {anchors[n]["bottom"][0]} {anchors[n]["bottom"][1]}> mark @BOTTOM;\n'
        for n in bases) + '} mark;\n'
    fea += 'table GDEF { GlyphClassDef [' + ' '.join(sorted(set(n for n in bases + [s for s in SHAPES if not SHAPES[s].get("mark")] + ['space']))) + '], , [' + ' '.join(ALL_MARKS) + '], ; } GDEF;\n'
    addOpenTypeFeaturesFromString(fb.font, fea)
    fb.save(out + '.ttf')
    f = TTFont(out + '.ttf'); f.flavor = 'woff2'; f.save(out + '.woff2')
    print('glyphs', len(order), 'ascent', asc, 'descent', desc, 'units/px', round(U, 3))


if __name__ == '__main__':
    main()
