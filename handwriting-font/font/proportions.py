"""Ruqʿah proportions: measure each form in a reference Ruqʿah font (Aref Ruqaa) and in
the hand, both in units of the alef's height, and return the scale that brings the
hand's letter to the standard."""
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
from names import BASE

ZWJ = '‍'
REF = '/tmp/claude-0/-home-user-Basata-Studio/ce18369a-643e-5158-b3e8-8c2733124063/scratchpad/ref/ArefRuqaa-Regular.ttf'


def ref_text(name):
    if name.startswith('lamalef'):
        return ('لا' if not name.endswith('fina') else ZWJ + 'لا')
    base, _, form = name.partition('.')
    c = chr(BASE[base])
    if base in ('fatha', 'damma', 'kasra', 'fathatan', 'dammatan', 'kasratan', 'sukun'):
        return 'ـ' + c
    return {'': c, 'init': c + ZWJ, 'medi': ZWJ + c + ZWJ, 'fina': ZWJ + c}[form]


def ink_box(arr):
    ys, xs = np.where(arr)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def ref_metrics(names, size=400):
    f = ImageFont.truetype(REF, size, layout_engine=ImageFont.Layout.RAQM)
    out = {}
    for n in names:
        t = ref_text(n)
        im = Image.new('L', (size * 4, size * 3), 0); d = ImageDraw.Draw(im)
        d.text((size * 3, size * 1.6), t, font=f, fill=255, anchor='rs', direction='rtl', language='ar')
        a = np.array(im) > 127
        if n.split('.')[0] in ('fatha', 'damma', 'kasra', 'fathatan', 'dammatan', 'kasratan', 'sukun'):
            im2 = Image.new('L', im.size, 0); ImageDraw.Draw(im2).text((size * 3, size * 1.6), 'ـ', font=f, fill=255, anchor='rs')
            a = a & ~(np.array(im2) > 127)
        if not a.any():
            continue
        x0, y0, x1, y1 = ink_box(a)
        base = int(size * 1.6)
        out[n] = dict(w=x1 - x0, h=y1 - y0, up=base - y0, down=y1 - base)
    alef = out['alef']['h']
    return {k: {kk: vv / alef for kk, vv in v.items()} for k, v in out.items()}
