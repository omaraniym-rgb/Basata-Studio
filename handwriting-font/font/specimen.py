import sys
from PIL import Image, ImageDraw, ImageFont
font = sys.argv[1]; out = sys.argv[2]
LINES = [(150, 'بسم الله الرحمن الرحيم'), (110, 'السلام عليكم ورحمة الله وبركاته'),
         (84, 'في الصباح ظهر وجه الشيخ أحمد عند بحر هادئ'), (84, 'كتب الولد ثلاث كلمات في كتاب جديد'),
         (84, 'صغيرة كانت قطة ضفدع غزال خوخ ذئب ثعلب'), (84, 'هل وصل هذا الحجاج إلى رأس المسجد؟'),
         (84, 'مُحَمَّدٌ يُحِبُّ القِرَاءَةَ، ١٢٣٤٥٦٧٨٩٠')]
W = 2000
H = sum(int(s * 1.75) for s, _ in LINES) + 80
im = Image.new('RGB', (W, H), (246, 244, 239)); d = ImageDraw.Draw(im); y = 40
for s, t in LINES:
    f = ImageFont.truetype(font, s, layout_engine=ImageFont.Layout.RAQM)
    d.text((W - 60, y + s * 1.15), t, font=f, fill=(24, 26, 36), anchor='rs', direction='rtl', language='ar')
    y += int(s * 1.75)
im.save(out); print(im.size)
