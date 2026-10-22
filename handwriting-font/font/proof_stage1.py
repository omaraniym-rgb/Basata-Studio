import sys, pickle, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
from names import proof_char
D = pickle.load(open('stage1.pkl', 'rb'))['glyphs']
TW, TH, C = 200, 150, 8
names = list(D); rows = (len(names) + C - 1) // C
sheet = Image.new('RGB', (TW * C, TH * rows), 'white'); d = ImageDraw.Draw(sheet)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
for i, n in enumerate(names):
    g = D[n]; m = g['mask']
    im = np.full(m.shape + (3,), 255, np.uint8); im[m] = (30, 30, 40)
    if g['base'] is not None:
        y = int(g['base']); cv2.line(im, (0, y), (im.shape[1], y), (0, 170, 0), 3)
    pim = Image.fromarray(im)
    sc = min((TW - 10) / pim.width, (TH - 24) / pim.height)
    pim = pim.resize((max(1, int(pim.width * sc)), max(1, int(pim.height * sc))), Image.LANCZOS)
    col = C - 1 - i % C; r = i // C
    sheet.paste(pim, (col * TW + 5, r * TH + 20))
    d.text((col * TW + 3, r * TH + 3), n, fill=(30, 30, 160), font=f)
    d.rectangle([col * TW, r * TH, col * TW + TW - 1, r * TH + TH - 1], outline=(220, 220, 220))
sheet.save(sys.argv[1])
