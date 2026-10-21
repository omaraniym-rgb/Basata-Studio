"""Export handwriting for the Pen Lab: the raw ink and the consistency analysis."""
import json, base64, io, os, cv2, numpy as np
from PIL import Image
from repen import ink_mask, stroke_width, UP
from pen4 import analyse, carve

SAMPLES = [  # (id, label, file, y0, y1, x0, x1)
    ('salam', 'السلام عليكم', '../sources/src1.jpg', 520, 1075, 100, 1790),
    ('page', 'جاب البيت كثير الحديث', '../sources/src3.jpg', 170, 1500, 0, 1512),
    ('letters', 'ط ظ ع غ ك ل م ن ه و ي', '../sources/src6.jpg', 360, 2140, 120, 1420),
]
HEAD = 8   # per stroke: n, flags, line, stem angle*100, loop pivot x, loop pivot y, loop R*8, 0


def pack(A):
    flat = []
    for s in A['strokes'] + A['bridges']:
        P = np.round(s['p']).astype(int); R = np.round(s['r'] * 8).astype(int)
        st, lp = s.get('stem'), s.get('loop')
        f = (int(s['closed']) | int(s['free'][0]) << 1 | int(s['free'][1]) << 2 | int(s['bridged'][0]) << 3
             | int(s['bridged'][1]) << 4 | int(bool(s.get('bridge'))) << 5 | int(bool(st)) << 6
             | int(bool(st) and st['pivot'] == 1) << 7 | int(bool(lp)) << 8)
        flat += [len(P), f, s.get('line', -1), int(round(st['angle'] * 100)) if st else 0,
                 int(round(lp['pivot'][0])) if lp else 0, int(round(lp['pivot'][1])) if lp else 0,
                 int(round(lp['R'] * 8)) if lp else 0, 0]
        flat += np.column_stack([P, R]).ravel().tolist()
    return base64.b64encode(np.array(flat, '<i2').tobytes()).decode()


out = []
for sid, label, f, y0, y1, x0, x1 in SAMPLES:
    m = ink_mask(cv2.imread(f)[y0:y1, x0:x1])
    w = stroke_width(m)
    cnt, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8))      # drop paper specks
    for i in range(1, cnt):
        if st[i, 4] < 4 * w * w:
            x, y, ww, hh = st[i, :4]; r = int(6 * w)
            others = (lab > 0) & (lab != i)
            if not others[max(0, y - r):y + hh + r, max(0, x - r):x + ww + r].any():
                m[lab == i] = False
    raw, clean = analyse(m, w), analyse(carve(m, w), w)
    small = cv2.resize(m.astype(np.uint8) * 255, (m.shape[1] // UP, m.shape[0] // UP), interpolation=cv2.INTER_AREA)
    rgba = np.zeros(small.shape + (4,), np.uint8); rgba[..., 3] = small
    buf = io.BytesIO(); Image.fromarray(rgba).save(buf, 'PNG', optimize=True)
    out.append(dict(id=sid, label=label, w=round(w / UP, 3), W=m.shape[1] // UP, H=m.shape[0] // UP, up=UP,
                    raw=pack(raw), clean=pack(clean), rmed=round(clean['rmed'] / UP, 3),
                    rawRmed=round(raw['rmed'] / UP, 3), stemTarget=round(clean['stem_target'], 2),
                    lines=[dict(cx=round(l['cx'] / UP, 1), cy=round(l['cy'] / UP, 1), angle=round(l['angle'], 2)) for l in clean['lines']],
                    ink='data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()))
    print(sid, 'raw', len(raw['strokes']), 'clean', len(clean['strokes']), 'bridges', len(clean['bridges']),
          'stems', sum(1 for s in clean['strokes'] if s['stem']), 'lines', [l['angle'] for l in clean['lines']])
open('lab_data.js', 'w').write('window.PEN_SAMPLES=' + json.dumps(out, ensure_ascii=False) + ';')
print('data KB', os.path.getsize('lab_data.js') // 1024)
