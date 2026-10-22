import sys
from PIL import Image, ImageDraw, ImageFont
from names import BASE, PRES
font = sys.argv[1]; out = sys.argv[2]
f = ImageFont.truetype(font, 92, layout_engine=ImageFont.Layout.BASIC)
lab = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
order = ['alef', 'beh', 'teh', 'theh', 'jeem', 'hah', 'khah', 'dal', 'thal', 'reh', 'zain', 'seen', 'sheen', 'sad', 'dad', 'tah', 'zah',
         'ain', 'ghain', 'feh', 'qaf', 'kaf', 'lam', 'meem', 'noon', 'heh', 'waw', 'yeh', 'tehMarbuta', 'alefMaksura', 'hamza',
         'alefHamzaAbove', 'alefHamzaBelow', 'alefMadda', 'wawHamza', 'yehHamza']
two = {0x621, 0x622, 0x623, 0x624, 0x625, 0x627, 0x629, 0x62F, 0x630, 0x631, 0x632, 0x648, 0x649}
CW, RH = 150, 150
rows = order + ['lamalef', 'digits']
im = Image.new('RGB', (CW * 5 + 30, RH * len(rows) // 2 + 60), (246, 244, 239))
im = Image.new('RGB', (2 * (CW * 4 + 160), RH * ((len(rows) + 1) // 2) + 20), (246, 244, 239)); d = ImageDraw.Draw(im)
heads = ['end', 'middle', 'start', 'alone']
for i, n in enumerate(rows):
    col, r = i % 2, i // 2
    x0 = (1 - col) * (CW * 4 + 160); y0 = r * RH + 10
    if n == 'digits':
        d.text((x0 + 20, y0 + 110), '٠١٢٣٤٥٦٧٨٩', font=f, fill=(24, 26, 36), anchor='ls'); continue
    if n == 'lamalef':
        chars = [chr(0xFEFC), None, None, chr(0xFEFB)]
    else:
        cp = BASE[n]; p = PRES[cp]
        chars = [chr(p + 1), None if cp in two or cp == 0x621 else chr(p + 3), None if cp in two or cp == 0x621 else chr(p + 2), chr(p)]
        if cp == 0x621: chars = [None, None, None, chr(p)]
    for k, c in enumerate(chars):
        if c: d.text((x0 + 20 + k * CW + CW / 2, y0 + 100), c, font=f, fill=(24, 26, 36), anchor='ms')
    d.text((x0 + 4 * CW + 30, y0 + 70), n, font=lab, fill=(130, 120, 110))
im.save(out); print(im.size)
