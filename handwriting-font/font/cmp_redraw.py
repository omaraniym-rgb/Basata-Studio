import sys, pickle, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
from glyphmap import G
A = pickle.load(open('stage2.pkl', 'rb'))['glyphs']; B = pickle.load(open('stage2r.pkl', 'rb'))['glyphs']
names = sys.argv[2].split(','); TW, TH = 250, 210
sheet = Image.new('RGB', (TW * len(names), TH * 3 + 30), (246, 244, 239)); d = ImageDraw.Draw(sheet)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
SC = 0.32
for i, n in enumerate(names):
    col = len(names) - 1 - i
    s = G[n]; x0, y0, x1, y1 = s['box']; m = 10
    src = Image.open('../sources/' + s['src']).convert('RGB').crop((x0 - m, y0 - m, x1 + m, y1 + m))
    sc = min((TW - 20) / src.width, (TH - 20) / src.height); src = src.resize((int(src.width * sc), int(src.height * sc)))
    sheet.paste(src, (col * TW + (TW - src.width) // 2, 26 + (TH - src.height) // 2))
    for row, D in ((1, A), (2, B)):
        g = D[n]; a, b, c, e = g['ink']; img = g['img'][max(0, b - 20):e + 20, max(0, a - 20):c + 20]
        im = np.full(img.shape + (3,), (246, 244, 239), np.uint8); im[img] = (28, 30, 40)
        pim = Image.fromarray(im); s2 = min(SC, (TW - 16) / pim.width, (TH - 16) / pim.height)
        pim = pim.resize((max(1, int(pim.width * s2)), max(1, int(pim.height * s2))), Image.LANCZOS)
        sheet.paste(pim, (col * TW + (TW - pim.width) // 2, 26 + row * TH + (TH - pim.height) // 2))
    d.text((col * TW + 6, 4), n, fill=(60, 60, 150), font=f)
d.text((4, 26 + TH + 4), 'before', fill=(170, 60, 60), font=f); d.text((4, 26 + 2 * TH + 4), 'now', fill=(40, 130, 60), font=f)
sheet.save(sys.argv[1])
