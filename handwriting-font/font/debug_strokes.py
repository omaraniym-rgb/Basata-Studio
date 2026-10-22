import sys, pickle, numpy as np, cv2
sys.path.insert(0, '../pens')
from stage2 import analyse_joined
D = pickle.load(open('stage1.pkl', 'rb'))['glyphs']
tiles = []
for n in sys.argv[2].split(','):
    g = D[n]; m = g['mask']; w = g['w']
    A, cuts = analyse_joined(m, g['base'], g['form'], w, w)
    im = np.full(m.shape + (3,), 255, np.uint8); im[m] = (215, 215, 215)
    rng = np.random.default_rng(3)
    for s in A['strokes']:
        c = tuple(int(v) for v in rng.integers(30, 200, 3))
        cv2.polylines(im, [s['p'].astype(np.int32).reshape(-1, 1, 2)], s['closed'], c, 3)
        for e in (0, 1):
            pt = tuple(int(v) for v in s['p'][0 if e == 0 else -1])
            col = (0, 160, 0) if e in s.get('joined', []) else ((220, 0, 0) if s['free'][e] else (0, 0, 220))
            cv2.circle(im, pt, 6, col, -1)
    cv2.line(im, (0, int(g['base'])), (im.shape[1], int(g['base'])), (255, 150, 0), 2)
    for k, x in cuts.items(): cv2.line(im, (int(x), 0), (int(x), im.shape[0]), (255, 0, 255), 2)
    tiles.append(cv2.resize(im, (int(im.shape[1] * 300 / im.shape[0]), 300)))
cv2.imwrite(sys.argv[1], np.hstack(tiles)[:, :, ::-1])
