import sys, pickle, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
D = pickle.load(open('stage2.pkl', 'rb'))['glyphs']
TW, TH, C = 200, 160, 8
names = list(D); rows = (len(names) + C - 1) // C
sheet = Image.new('RGB', (TW * C, TH * rows), (246, 244, 239)); d = ImageDraw.Draw(sheet)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
# one scale for all: 1 pen width = 7 px in the sheet (true relative sizes)
S = 7 / 44
for i, n in enumerate(names):
    g = D[n]; img = g['img']; x0, y0, x1, y1 = g['ink']
    L, R = int(g['left']), int(g['right'])
    top = int(min(y0, (g['base'] or y0) - 44 * 9)); bot = int(max(y1, (g['base'] or y1) + 44 * 5))
    crop = img[max(0, top):bot, max(0, L - 40):R + 40]
    im = np.full(crop.shape + (3,), (246, 244, 239), np.uint8); im[crop] = (28, 30, 40)
    ox = max(0, L - 40)
    if g['base'] is not None:
        yb = int(g['base']) - max(0, top); cv2.line(im, (0, yb), (im.shape[1], yb), (80, 180, 120), 2)
    for xx in (L, R): cv2.line(im, (xx - ox, 0), (xx - ox, im.shape[0]), (230, 120, 120), 2)
    pim = Image.fromarray(im); pim = pim.resize((max(1, int(pim.width * S)), max(1, int(pim.height * S))), Image.LANCZOS)
    col = C - 1 - i % C; r = i // C
    sheet.paste(pim, (col * TW + (TW - pim.width) // 2, r * TH + 18))
    d.text((col * TW + 3, r * TH + 2), n, fill=(60, 60, 150), font=f)
sheet.save(sys.argv[1]); print(sheet.size)
