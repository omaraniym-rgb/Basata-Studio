"""Clean redraws of the letters the rough paper shook (ح ج خ ع غ ص ض).

Each body is traced from the writer's own glyph as a few points per pen stroke
(pen-width units, origin at the left join / baseline, y up). A centripetal
Catmull-Rom spline runs through them, so the line is one confident stroke with the
writer's own proportions. Sister letters share one body and differ only by dots.
Rendered with the same pen as every other glyph (contrast, angle, flicks, weight)."""
import sys, pickle, numpy as np, cv2
from scipy.ndimage import gaussian_filter1d
from stage2 import R_W, PEN, OVER, SIDE

R0 = 22.6                 # pen radius in px at R_W=44 (matches the other glyphs' measured weight)
DOT = 0.9                 # dot size: matches the writer's own dots on ن ف ز
HEAVY = np.array([-1.0, 1.0]) / np.sqrt(2)


def catmull(P, n_per=40):
    P = np.asarray(P, float)
    if len(P) == 2:
        t = np.linspace(0, 1, n_per)[:, None]; return P[0] + (P[1] - P[0]) * t
    Q = np.vstack([2 * P[0] - P[1], P, 2 * P[-1] - P[-2]])
    out = []
    for i in range(1, len(Q) - 2):
        p0, p1, p2, p3 = Q[i - 1], Q[i], Q[i + 1], Q[i + 2]
        t0 = 0; t1 = t0 + np.linalg.norm(p1 - p0) ** .5 + 1e-6; t2 = t1 + np.linalg.norm(p2 - p1) ** .5 + 1e-6
        t3 = t2 + np.linalg.norm(p3 - p2) ** .5 + 1e-6
        for t in np.linspace(t1, t2, n_per, endpoint=False):
            a1 = (t1 - t) / (t1 - t0) * p0 + (t - t0) / (t1 - t0) * p1
            a2 = (t2 - t) / (t2 - t1) * p1 + (t - t1) / (t2 - t1) * p2
            a3 = (t3 - t) / (t3 - t2) * p2 + (t - t2) / (t3 - t2) * p3
            b1 = (t2 - t) / (t2 - t0) * a1 + (t - t0) / (t2 - t0) * a2
            b2 = (t3 - t) / (t3 - t1) * a2 + (t - t1) / (t3 - t1) * a3
            out.append((t2 - t) / (t2 - t1) * b1 + (t - t1) / (t2 - t1) * b2)
    out.append(P[-1])
    return np.array(out)


def resample(p, step):
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(p, axis=0).T))]
    if d[-1] < step: return p, d
    t = np.arange(0, d[-1], step)
    q = np.stack([np.interp(t, d, p[:, 0]), np.interp(t, d, p[:, 1])], 1)
    return q, t


def ease(u):
    u = np.clip(u, 0, 1); return u * u * (3 - 2 * u)


def render(strokes, dots, shape, to_px):
    """strokes: list of (points_units, start_mode, end_mode); mode in land / flick / join"""
    canvas = np.zeros(shape, np.uint8)
    sq = np.sqrt(PEN['contrast']); W = R_W; fl = PEN['flicks']
    def stamp(p, r):
        for (x, y), rr in zip(p, r):
            cv2.ellipse(canvas, (int(x * 16), int(y * 16)), (max(1, int(rr * sq * 16)), max(1, int(rr / sq * 16))),
                        -PEN['angle'], 0, 360, 1, -1, cv2.LINE_8, 4)
    for pts, m0, m1 in strokes:
        p = to_px(catmull(pts))
        p, d = resample(p, 0.5)
        if len(p) > 9:                      # a final whisper of smoothing, ends pinned
            s = 3.0; q = gaussian_filter1d(p, s, axis=0, mode='nearest'); n = len(p); k = np.arange(n)
            wa = np.clip(1 - k / (2.5 * s), 0, 1)[:, None]; wb = np.clip(1 - (n - 1 - k) / (2.5 * s), 0, 1)[:, None]
            p = q + wa * (p[0] - q[0]) + wb * (p[-1] - q[-1])
        L = d[-1] if len(d) else 0
        tr = np.gradient(p, axis=0) if len(p) > 1 else np.zeros((1, 2))
        tr /= (np.linalg.norm(tr, axis=1, keepdims=True) + 1e-9)
        r = R0 * (1 + 0.10 * (tr @ HEAVY))
        for mode, dist in ((m0, d), (m1, L - d)):
            if mode == 'land': r = r * (0.7 + 0.3 * ease(dist / (1.1 * W)))
            elif mode == 'flick':
                floor = 1 - 0.78 * fl; r = r * (floor + (1 - floor) * ease(dist / (2.8 * W)) ** 0.75)
        stamp(p, r * PEN['weight'])
    for (cx, cy), size in dots:                 # the writer's dot: a short pressed dash
        c = to_px(np.array([[cx, cy]]))[0]; a = np.radians(35)
        v = np.array([np.cos(a), -np.sin(a)]) * 0.32 * W * size
        q = np.stack([np.linspace(-1, 1, 15)] * 2, 1) * v + c
        r = R0 * 1.25 * size * (0.75 + 0.25 * np.sin(np.pi * np.linspace(0, 1, 15)))
        stamp(q, r * PEN['weight'])
    return cv2.GaussianBlur(canvas.astype(np.float32), (0, 0), 3 * .35) > .5


# ------------------------------------------------------------------ bodies (pen widths)
# Traced from the writer's clean samples (sources/src10_jeem_ain_sad.jpg, src9_basmala.jpg), in photo pixels,
# then scaled to Ruqʿah proportions (Aref Ruqaa ink box) and seated on the baseline.

def tr(pts, k, J, Jy=0.0, dx=0.0):
    """photo px (y down) -> pen widths (y up), junction J at (dx, Jy)."""
    return [((x - J[0]) * k + dx, Jy + (J[1] - y) * k) for x, y in pts]

# ---- ح ج خ : flat oval head, descent, long bowl (new ج sample) ----
KH, JH = 0.0405, (255, 345)
H_OVAL = [(255, 345), (295, 325), (307, 300), (285, 272), (220, 261), (155, 272), (122, 300), (140, 330), (200, 345), (250, 348)]
H_DESC = [(262, 342), (230, 370), (195, 395), (160, 422), (132, 458), (121, 500), (136, 540), (178, 563), (240, 568),
          (300, 557), (360, 537), (408, 508)]
H_JY = -5.55 + (568 - 345) * KH            # bowl bottom on Ruqʿah depth -> junction height

def hah_isol():
    S = [(tr(H_OVAL, KH, JH, H_JY), 'land', 'join'), (tr(H_DESC, KH, JH, H_JY), 'join', 'flick')]
    return dict(strokes=S, cuts={}, bowl=tr([(271, 462)], KH, JH, H_JY)[0], top=tr([(220, 205)], KH, JH, H_JY)[0])

def hah_fina():
    """Standard final ح on a flat line: the connector climbs into a pointed head, then the writer's bowl."""
    rc, ay = 6.4, 3.5
    d0 = tr(H_DESC, KH, (262, 342), ay)            # the writer's descent + bowl, hanging from the head point
    conn = [(rc + 0.7, 0.0), (rc, 0.0), (4.9, 0.05), (3.7, 0.45), (2.5, 1.3), (1.4, 2.35), (0.55, 3.2), (0.0, ay)]
    S = [(conn + d0[1:], 'join', 'flick')]
    return dict(strokes=S, cuts=dict(right=rc), bowl=(-1.9, -3.3), top=(-0.4, 5.6))

# the closed triangle head of initial/medial ح, from الرحيم
KT, JT = 0.0671, (389, 313)
TRI = [(389, 311), (392, 285), (397, 258), (404, 237), (414, 240), (428, 255), (441, 271), (445, 288), (440, 302),
       (420, 307), (400, 311), (389, 313)]

def hah_init(dot=None):
    S = [(tr(TRI, KT, JT) + [(-1.0, 0.0), (-1.7, 0.0)], 'land', 'join')]
    return dict(strokes=S, cuts=dict(left=-1.0), apex=(1.1, 5.1))

def hah_medi(dot=None):
    rc = 5.0
    S = [(tr(TRI, KT, JT) + [(-1.0, 0.0), (-1.7, 0.0)], 'land', 'join'),
         ([(rc + 0.7, 0.0), (rc, 0.0), (4.4, 0.08), (3.85, 0.4), (3.42, 0.74)], 'join', 'join')]
    return dict(strokes=S, cuts=dict(left=-1.0, right=rc), apex=(1.1, 5.1))

# ---- ع غ : open 'c' head with its tongue, long bowl (new ع sample) ----
KA, JA = 0.0436, (532, 402)
A_HEAD = [(588, 296), (555, 286), (522, 295), (505, 320), (503, 350), (513, 380), (532, 400), (560, 392), (600, 377),
          (640, 363), (660, 356)]
A_BOWL = [(532, 402), (505, 430), (488, 465), (487, 500), (493, 530), (510, 560), (545, 588), (600, 603), (650, 600),
          (700, 592), (742, 584)]
A_JY = -5.65 + (603 - 402) * KA

def ain_isol():
    S = [(tr(A_HEAD, KA, JA, A_JY), 'land', 'flick'), (tr(A_BOWL, KA, JA, A_JY), 'join', 'flick')]
    return dict(strokes=S, cuts={}, top=tr([(552, 232)], KA, JA, A_JY)[0])

def ain_init():
    S = [(tr(A_HEAD, KA, JA), 'land', 'flick'), ([(0.05, 0.02), (-1.0, 0.0), (-2.0, 0.0), (-2.7, 0.0)], 'join', 'join')]
    return dict(strokes=S, cuts=dict(left=-2.0), top=tr([(552, 232)], KA, JA)[0])

def ain_fina():
    """Standard final ع on a flat line: a small closed head, then the writer's bowl (scaled to Ruqʿah depth)."""
    rc = 5.2
    J = (0.45, 0.65)
    bowl = [(J[0] + (x - JA[0]) * KA * 0.75, J[1] + (JA[1] - y) * KA * 0.75) for x, y in A_BOWL]
    P = [(rc + 0.7, 0.0), (rc, 0.0), (3.7, 0.04), (2.5, 0.2), (1.6, 0.6), (0.95, 1.3), (0.8, 2.3), (1.35, 3.1), (2.15, 3.2),
         (2.55, 2.6), (2.25, 1.7), (1.45, 1.0)] + bowl
    return dict(strokes=[(P, 'join', 'flick')], cuts=dict(right=rc), top=(1.65, 5.0))

# ---- ص ض : starting tick, tilted leaf loop, deep bowl (new ص sample) ----
KS, JS = 0.0319, (1165, 465)
S_TICK = [(1085, 393), (1112, 415), (1140, 440), (1165, 465)]
S_LOOP = [(1165, 465), (1195, 425), (1225, 382), (1258, 345), (1292, 322), (1326, 318), (1350, 334), (1351, 362),
          (1328, 386), (1288, 404), (1242, 422), (1200, 445), (1172, 470)]
S_BOWL = [(1165, 465), (1180, 505), (1178, 540), (1160, 570), (1120, 592), (1060, 600), (1000, 593), (950, 572),
          (918, 540), (912, 500), (925, 463), (955, 435)]
S_JY = 0.55 + (600 - 465) * KS            # isolated ص: the bowl sits on the line
S_DOT = (1300, 262)

def sad_isol():
    S = [(tr(S_TICK, KS, JS, S_JY), 'land', 'join'), (tr(S_LOOP, KS, JS, S_JY), 'join', 'join'),
         (tr(S_BOWL, KS, JS, S_JY), 'join', 'flick')]
    return dict(strokes=S, cuts={}, top=tr([S_DOT], KS, JS, S_JY)[0])

# the writer's ـط loop (from طـ / ـط), 1.3x for ص: a tilted leaf sitting on the line, bottom point B at the origin
T_LOOP = [(0.0, 0.3), (1.0, 0.55), (1.95, 1.3), (2.6, 2.6), (1.05, 3.6), (-0.8, 2.85), (-1.7, 1.25), (-1.5, 0.4)]
TL_DOT = (0.9, 5.3)

def loop_at(xb):
    return [(x + xb, y) for x, y in T_LOOP]

def sad_init():
    xb = 2.6
    S = [([(xb - 1.6, 0.35)] + loop_at(xb) + [(xb - 2.5, 0.06), (0.0, 0.0), (-0.7, 0.0)], 'land', 'join')]
    return dict(strokes=S, cuts=dict(left=0.0), top=(TL_DOT[0] + xb, TL_DOT[1]))

def sad_medi():
    xb, rc = 2.6, 6.3
    S = [([(xb - 1.6, 0.35)] + loop_at(xb) + [(xb - 2.5, 0.06), (0.0, 0.0), (-0.7, 0.0)], 'land', 'join'),
         ([(rc + 0.7, 0.0), (rc, 0.0), (xb + 2.4, 0.05), (xb + 1.0, 0.22), (xb, 0.3)], 'join', 'join')]
    return dict(strokes=S, cuts=dict(left=0.0, right=rc), top=(TL_DOT[0] + xb, TL_DOT[1]))

def sad_fina():
    xb, rc = 8.9, 12.6
    J = loop_at(xb)[-1]
    bowl = [(J[0] + (x - JS[0]) * KS, J[1] + (JS[1] - y) * KS) for x, y in S_BOWL]
    S = [([(rc + 0.7, 0.0), (rc, 0.0), (xb + 2.4, 0.05), (xb + 1.0, 0.22)] + loop_at(xb) + bowl[1:], 'join', 'flick')]
    return dict(strokes=S, cuts=dict(right=rc), top=(TL_DOT[0] + xb, TL_DOT[1]))


def ain_medi():
    """The writer's medial ع: a small filled triangle sitting on the line."""
    rc = 5.6
    S = [([(rc + 0.7, 0.0), (rc, 0.0), (4.55, -0.03), (3.9, 0.15), (4.1, 0.85), (4.2, 1.5), (3.6, 1.6), (3.0, 1.55),
           (3.15, 0.95), (3.5, 0.3), (2.6, 0.02), (1.0, 0.0), (0.0, 0.0), (-0.7, 0.0)], 'join', 'join'),
         ([(3.6, 0.6), (3.6, 1.2)], 'join', 'join')]          # fills the triangle: a blind head, no pinhole
    return dict(strokes=S, cuts=dict(left=0.0, right=rc), top=(3.6, 3.35))


def glyph_defs():
    G = {}
    for fam, dot in (('hah', None), ('jeem', 'below'), ('khah', 'above')):
        s, i, m, f = hah_isol(), hah_init(), hah_medi(), hah_fina()
        for g in (i, m):
            g['dots'] = [] if dot is None else [((1.6, -2.0) if dot == 'below' else (1.2, 6.8), DOT)]
        for g in (s, f):
            g['dots'] = [] if dot is None else [(g['bowl'] if dot == 'below' else g['top'], DOT)]
        G[fam], G[fam + '.init'], G[fam + '.medi'], G[fam + '.fina'] = s, i, m, f
    for fam, dotted in (('ain', False), ('ghain', True), ('sad', False), ('dad', True)):
        mk = (ain_isol, ain_init, ain_medi, ain_fina) if fam in ('ain', 'ghain') else (sad_isol, sad_init, sad_medi, sad_fina)
        for suf, f in zip(('', '.init', '.medi', '.fina'), mk):
            g = f(); g['dots'] = [(g['top'], DOT)] if dotted else []
            G[fam + suf] = g
    return G


def build(defs, base_pkl='stage2.pkl', out='stage2r.pkl'):
    D = pickle.load(open(base_pkl, 'rb'))
    for name, g in defs.items():
        pts = np.vstack([np.array(s[0]) for s in g['strokes']] + [np.array([d[0]]) for d in g['dots']])
        xmin, ymin = pts.min(0) - 2.5; xmax, ymax = pts.max(0) + 2.5
        H, W = int((ymax - ymin) * R_W), int((xmax - xmin) * R_W)
        to_px = lambda P: np.column_stack([(np.asarray(P)[:, 0] - xmin) * R_W, (ymax - np.asarray(P)[:, 1]) * R_W])
        img = render(g['strokes'], g['dots'], (H, W), to_px)
        base = ymax * R_W
        X = lambda x: (x - xmin) * R_W
        y0b, y1b = max(0, int(base - 1.7 * R_W)), int(base + 1.7 * R_W)
        cuts = g['cuts']
        if 'left' in cuts: img[y0b:y1b, :max(0, int(X(cuts['left']) - OVER * R_W))] = False
        if 'right' in cuts: img[y0b:y1b, int(X(cuts['right']) + OVER * R_W):] = False
        ys, xs = np.where(img)
        left = X(cuts['left']) if 'left' in cuts else xs.min() - SIDE * R_W
        right = X(cuts['right']) if 'right' in cuts else xs.max() + SIDE * R_W
        form = name.split('.')[1] if '.' in name else 'isol'
        D['glyphs'][name] = dict(img=img, left=left, right=right, base=base, form=form, side=None, rw=R_W,
                                 ink=(xs.min(), ys.min(), xs.max(), ys.max()), scale=1.0, redrawn=True)
    pickle.dump(D, open(out, 'wb'))
    print('redrawn', len(defs), '->', out)


if __name__ == '__main__':
    build(glyph_defs())
