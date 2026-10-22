import sys, pickle, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
from glyphmap import G
D2 = pickle.load(open('stage2.pkl', 'rb'))['glyphs']
names = sys.argv[2].split(',')
TW, TH = 260, 230
sheet = Image.new('RGB', (TW * len(names), TH * 2 + 24), (246, 244, 239)); d = ImageDraw.Draw(sheet)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
for i, n in enumerate(names):
    s = G[n]; x0, y0, x1, y1 = s['box']; m = 10
    src = Image.open('../sources/' + s['src']).convert('RGB').crop((x0 - m, y0 - m, x1 + m, y1 + m))
    sc = min((TW - 20) / src.width, (TH - 20) / src.height); src = src.resize((int(src.width * sc), int(src.height * sc)))
    col = len(names) - 1 - i
    sheet.paste(src, (col * TW + (TW - src.width) // 2, 24 + (TH - src.height) // 2))
    g = D2[n]; a, b, c, e = g['ink']; img = g['img'][max(0, b - 20):e + 20, max(0, a - 20):c + 20]
    im = np.full(img.shape + (3,), (246, 244, 239), np.uint8); im[img] = (28, 30, 40)
    pim = Image.fromarray(im); sc = min((TW - 20) / pim.width, (TH - 20) / pim.height, 0.6)
    pim = pim.resize((max(1, int(pim.width * sc)), max(1, int(pim.height * sc))), Image.LANCZOS)
    sheet.paste(pim, (col * TW + (TW - pim.width) // 2, 24 + TH + (TH - pim.height) // 2))
    d.text((col * TW + 6, 4), n, fill=(60, 60, 150), font=f)
sheet.save(sys.argv[1])
