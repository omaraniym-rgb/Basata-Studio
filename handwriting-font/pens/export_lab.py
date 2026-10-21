"""Export handwriting strokes (ordered centre-lines) for the Pen Lab page."""
import json, base64, io, os, cv2, numpy as np
from PIL import Image
from repen import ink_mask, stroke_width, skeleton, UP
from pen3 import medial

SAMPLES = [  # (id, label, file, y0, y1, x0, x1)
    ('salam', 'السلام عليكم', '../sources/src1.jpg', 520, 1075, 100, 1790),
    ('page', 'جاب البيت كثير الحديث', '../sources/src3.jpg', 170, 1500, 0, 1512),
    ('letters', 'ط ظ ع غ ك ل م ن ه و ي', '../sources/src6.jpg', 360, 2140, 120, 1420),
]

out = []
for sid, label, f, y0, y1, x0, x1 in SAMPLES:
    m = ink_mask(cv2.imread(f)[y0:y1, x0:x1])
    w = stroke_width(m)
    # drop paper specks: small blobs far from any other ink
    cnt, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8))
    for i in range(1, cnt):
        if st[i, 4] < 4 * w * w:
            others = (lab > 0) & (lab != i)
            x, y, ww, hh = st[i, :4]; r = int(6 * w)
            if not others[max(0, y - r):y + hh + r, max(0, x - r):x + ww + r].any():
                m[lab == i] = False
    flat = []
    strokes = medial(m, w)
    for st in strokes:
        P, R = np.round(st['p']).astype(int), np.round(st['r'] * 8).astype(int)
        flags = int(st['closed']) | int(st['free'][0]) << 1 | int(st['free'][1]) << 2
        flat += [len(P), flags] + np.column_stack([P, R]).ravel().tolist()
    arr = np.array(flat, '<i2')
    small = cv2.resize(m.astype(np.uint8) * 255, (m.shape[1] // UP, m.shape[0] // UP), interpolation=cv2.INTER_AREA)
    rgba = np.zeros(small.shape + (4,), np.uint8); rgba[..., 3] = small
    buf = io.BytesIO(); Image.fromarray(rgba).save(buf, 'PNG', optimize=True)
    out.append(dict(id=sid, label=label, w=round(w / UP, 2), W=m.shape[1] // UP, H=m.shape[0] // UP, up=UP,
                    strokes=base64.b64encode(arr.tobytes()).decode(),
                    ink='data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()))
    print(sid, 'strokes', len(strokes), 'points', (len(arr) - 2 * len(strokes)) // 3)
open('lab_data.js', 'w').write('window.PEN_SAMPLES=' + json.dumps(out, ensure_ascii=False) + ';')
print('data KB', os.path.getsize('lab_data.js') // 1024)
