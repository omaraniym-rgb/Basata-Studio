import sys, cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont
from glyphmap import G
from names import proof_char
SRC = '../sources/'
cache = {}
TW, TH, C = 200, 150, 8
names = list(G)
rows = (len(names) + C - 1) // C
sheet = Image.new('RGB', (TW * C, TH * rows), 'white'); d = ImageDraw.Draw(sheet)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
fa = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 34)
for i, n in enumerate(names):
    s = G[n]
    if s['src'] not in cache: cache[s['src']] = Image.open(SRC + s['src']).convert('RGB')
    x0, y0, x1, y1 = s['box']; m = 12
    c = cache[s['src']].crop((x0 - m, y0 - m, x1 + m, y1 + m)).copy()
    ImageDraw.Draw(c).rectangle([m - 2, m - 2, m + x1 - x0 + 2, m + y1 - y0 + 2], outline=(255, 60, 60))
    sc = min((TW - 50) / c.width, (TH - 24) / c.height, 3)
    c = c.resize((max(1, int(c.width * sc)), max(1, int(c.height * sc))))
    col = C - 1 - i % C; r = i // C
    sheet.paste(c, (col * TW + 46, r * TH + 20))
    d.text((col * TW + 3, r * TH + 3), n, fill=(30, 30, 160), font=f)
    d.text((col * TW + 6, r * TH + 40), proof_char(n), fill=(0, 150, 0), font=fa, features=None)
    d.rectangle([col * TW, r * TH, col * TW + TW - 1, r * TH + TH - 1], outline=(220, 220, 220))
sheet.save(sys.argv[1]); print(sheet.size)
