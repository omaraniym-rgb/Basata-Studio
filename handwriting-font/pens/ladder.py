"""Contrast ladder: one line of handwriting, from round pen to full qalam."""
import sys, cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont
from repen import ink_mask, stroke_width, render, UP
from pen2 import ink

def ladder(crop, rows, out, label_w=330):
    m = ink_mask(crop); w = stroke_width(m)
    tiles = []
    for name, sub, p in rows:
        r = m if p is None else ink(m, p['d'] * w, p['c'], p.get('a', 70), p.get('s', 1.0) * w, w)
        tiles.append((name, sub, render(r)))
    h, wd = tiles[0][2].shape[:2]
    S = Image.new('RGB', (wd + label_w, h * len(tiles)), (244, 241, 236))
    d = ImageDraw.Draw(S)
    f1 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 28)
    f2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 19)
    for i, (name, sub, img) in enumerate(tiles):
        S.paste(Image.fromarray(img), (label_w, i * h))
        d.text((26, i * h + h // 2 - 32), name, font=f1, fill=(28, 30, 40))
        d.text((26, i * h + h // 2 + 6), sub, font=f2, fill=(115, 108, 100))
        if i: d.line([(0, i * h), (S.width, i * h)], fill=(214, 206, 194), width=2)
    S.save(out)

if __name__ == '__main__':
    crop = cv2.imread('../sources/src1.jpg')[790:1030, 100:1790]
    rows = [
        ('Your pen now', 'ballpoint, as written', None),
        ('1.0 × round', 'smoothed, no contrast', dict(d=1.35, c=1.0)),
        ('1.4 ×', 'a hint of qalam', dict(d=1.35, c=1.4)),
        ('1.7 ×', 'the middle', dict(d=1.35, c=1.7)),
        ('2.1 ×', 'calligraphic', dict(d=1.35, c=2.1)),
        ('3.0 ×', 'full qalam (last try)', dict(d=1.35, c=3.0)),
    ]
    ladder(crop, rows, sys.argv[1])
