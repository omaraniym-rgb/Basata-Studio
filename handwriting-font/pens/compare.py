"""Side-by-side: the same handwriting inked with different pens."""
import sys, cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont
from repen import *

PENS = [
    ('Your pen now', 'round ballpoint, as written', lambda w: ('original',)),
    ('Felt-tip', 'round, bolder, even line', lambda w: ('round', w * 1.5)),
    ('Qalam fine', 'reed nib 70°, light', lambda w: ('nib', w * 1.6, 70, max(3, int(w * .15)))),
    ('Qalam  ·  Waseem-style', 'reed nib 70°: thick flats, thin uprights', lambda w: ('nib', w * 2.1, 70, max(3, int(w * .17)))),
    ('Qalam bold', 'same nib, wider', lambda w: ('nib', w * 2.7, 70, max(3, int(w * .2)))),
    ('Chisel marker', 'flat tip at 45°', lambda w: ('nib', w * 2.0, 45, max(3, int(w * .17)))),
]

def sheet(crop, out):
    m = ink_mask(crop)
    w = stroke_width(m)
    sk = skeleton(m, w)
    tiles = []
    for name, sub, pen in PENS:
        p = pen(w)
        if p[0] == 'original':
            r = repen(m, p, w)
        elif p[0] == 'round':
            r = cv2.GaussianBlur(cv2.dilate(sk.astype(np.uint8), disc(p[1])).astype(np.float32), (0, 0), UP * .7) > .5
        else:
            r = repen_from_skeleton(m, sk, p, w)
        tiles.append((name, sub, render(r)))
    h, wd = tiles[0][2].shape[:2]
    lab = 300
    S = Image.new('RGB', (wd + lab, h * len(tiles)), (244, 240, 232))
    d = ImageDraw.Draw(S)
    f1 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 26)
    f2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
    for i, (name, sub, img) in enumerate(tiles):
        S.paste(Image.fromarray(img), (lab, i * h))
        d.text((24, i * h + h // 2 - 30), name, font=f1, fill=(30, 32, 45))
        d.text((24, i * h + h // 2 + 6), sub, font=f2, fill=(120, 110, 100))
        if i: d.line([(0, i * h), (S.width, i * h)], fill=(215, 205, 190), width=2)
    S.save(out)

def repen_from_skeleton(mask, sk, pen, w):
    _, width, ang, thin = pen
    out = cv2.dilate(sk.astype(np.uint8), nib_kernel(width, ang, thin))
    cnt, lab, st, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8))
    for i in range(1, cnt):
        x, y, ww, hh, a = st[i]
        if max(ww, hh) < 2.2 * w:                      # a dot: stamp a qalam rhombus
            dot = np.zeros_like(out); dot[y + hh // 2, x + ww // 2] = 1
            dot = cv2.dilate(dot, nib_kernel(width * .9, ang, thin))
            dot = cv2.dilate(dot, nib_kernel(width * .6, ang - 80, thin))
            out |= dot
    return cv2.GaussianBlur(out.astype(np.float32), (0, 0), UP * .7) > .5

if __name__ == '__main__':
    src, y0, y1, x0, x1, out = sys.argv[1], *map(int, sys.argv[2:6]), sys.argv[6]
    sheet(cv2.imread(src)[y0:y1, x0:x1], out)
