"""Draw the printable writing template (PNG pages + one PDF)."""
import sys, os
from PIL import Image, ImageDraw, ImageFont
from glyphs import *

FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
GHOST, LINE = 205, 190


def draw_page(pg, items, fill_black=False):
    img = Image.new('L', (PAGE_W, PAGE_H), 255)
    d = ImageDraw.Draw(img)
    for cx, cy in MARKER_CENTERS:
        d.rectangle([cx - MARKER // 2, cy - MARKER // 2, cx + MARKER // 2, cy + MARKER // 2], fill=0)
    lab = ImageFont.truetype(FONT, 22, layout_engine=ImageFont.Layout.BASIC)
    big = ImageFont.truetype(FONT, 190, layout_engine=ImageFont.Layout.BASIC)
    ttl = ImageFont.truetype(FONT, 38, layout_engine=ImageFont.Layout.BASIC)
    d.text((PAGE_W // 2, 200), 'MY ARABIC FONT  -  page %d   |   write with a DARK pen, stay on the baseline, '
           'let join strokes run along it' % (pg + 1), font=ttl, fill=60, anchor='mm')
    for i, s in enumerate(items):
        x, y, w, h = cell_rect(i)
        d.text((x, y - 10), s['label'], font=lab, fill=90, anchor='ls', features=None)
        d.rectangle([x, y, x + w, y + h], outline=GHOST, width=2)
        by = y + BASE_Y
        d.line([x, by, x + w, by], fill=LINE, width=2)
        ch = chr(s['ghost'])
        tw = d.textlength(ch, font=big)
        d.text((x + w / 2 - tw / 2, by), ch, font=big, fill=0 if fill_black else GHOST, anchor='ls')
    return img


def main(out='template'):
    os.makedirs(out, exist_ok=True)
    sl = slots()
    pages = [sl[i:i + PER_PAGE] for i in range(0, len(sl), PER_PAGE)]
    imgs = []
    for p, items in enumerate(pages):
        im = draw_page(p, items)
        im.save(f'{out}/template_page{p + 1}.png')
        imgs.append(im)
    imgs[0].save(f'{out}/template.pdf', save_all=True, append_images=imgs[1:], resolution=300)
    print(len(sl), 'slots,', len(pages), 'pages')


if __name__ == '__main__':
    main(*sys.argv[1:])
