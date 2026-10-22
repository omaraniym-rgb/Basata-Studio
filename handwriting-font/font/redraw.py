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
def hah_A(x0):
    """The writer's 'A' head of initial/medial ح, standing on the line at x0 (counter kept open at text sizes)."""
    left = [(x0 - 0.2, -0.30), (x0 + 0.8, 1.4), (x0 + 1.85, 3.1), (x0 + 2.6, 4.1), (x0 + 3.05, 4.45)]
    right = [(x0 + 3.05, 4.45), (x0 + 3.5, 3.95), (x0 + 3.6, 2.5), (x0 + 3.55, 1.2)]
    bar = [(x0 + 0.65, 1.05), (x0 + 2.0, 1.08), (x0 + 3.55, 1.15)]
    return left, right, bar

def hah_init(dot=None):
    x0 = 1.9
    left, right, bar = hah_A(x0)
    if dot == 'below': left = [(x0 - 1.65, -2.75)] + left
    S = [([(-0.7, 0.0), (0.0, 0.0), (1.0, 0.03), (x0 + 0.4, 0.06), (x0 + 0.75, 0.15)], 'join', 'join'),
         (left + right[1:] + [(x0 + 3.85, 1.12), (x0 + 4.6, 1.25), (x0 + 5.3, 1.55)], 'land', 'flick'),
         (bar, 'join', 'join')]
    return dict(strokes=S, cuts=dict(left=0.0), apex=(x0 + 3.05, 4.45), x0=x0)

def hah_medi(dot=None):
    x0 = 1.9
    left, right, bar = hah_A(x0)
    if dot == 'below': left = [(x0 - 1.65, -2.75)] + left
    rc = x0 + 6.3
    S = [([(-0.7, 0.0), (0.0, 0.0), (1.0, 0.03), (x0 + 0.4, 0.06), (x0 + 0.75, 0.15)], 'join', 'join'),
         (left + right[1:] + [(x0 + 3.9, 0.7), (x0 + 4.6, 0.2), (x0 + 5.4, 0.02), (rc, 0.0), (rc + 0.7, 0.0)], 'land', 'join'),
         (bar, 'join', 'join')]
    return dict(strokes=S, cuts=dict(left=0.0, right=rc), apex=(x0 + 3.05, 4.45), x0=x0)

def hah_isol():
    loop = [(4.6, 3.45), (3.0, 3.95), (1.9, 5.0), (1.8, 6.45), (2.9, 7.75), (4.6, 8.4), (6.6, 8.5), (8.5, 8.0), (9.5, 6.9),
            (8.95, 5.7), (7.4, 4.6), (5.8, 3.8), (4.45, 3.3)]
    tail = [(3.1, 1.8), (1.9, 0.2), (1.1, -1.6), (1.25, -3.2), (2.6, -4.4), (4.6, -5.0), (7.0, -5.2), (9.9, -5.15)]
    return dict(strokes=[(loop + tail, 'land', 'flick')], cuts={}, bowl=(5.0, -2.5), top=(5.6, 10.4))

def hah_fina():
    rc = 16.0
    P = [(rc + 0.7, 0.0), (rc, 0.0), (13.5, -0.42), (11.0, -0.82), (8.5, -1.22), (6.8, -1.42), (5.6, -1.15), (4.6, -0.95),
         (3.6, -1.35), (2.8, -2.3), (2.5, -3.35), (2.95, -3.95), (4.4, -3.9), (5.8, -4.0), (6.25, -4.3), (5.3, -5.1),
         (3.4, -6.3), (1.8, -7.6), (0.95, -9.0), (1.25, -10.2), (2.8, -10.9), (4.8, -11.0), (7.2, -10.5)]
    return dict(strokes=[(P, 'join', 'flick')], cuts=dict(right=rc), bowl=(4.3, -8.1), top=(3.5, 1.0))


def ain_isol():
    head = [(4.65, 7.95), (3.7, 7.35), (2.75, 6.35), (2.05, 5.2), (2.0, 4.25), (2.55, 3.6), (3.4, 3.35), (4.6, 3.75),
            (5.8, 4.35), (6.7, 4.85), (7.15, 5.0)]
    bowl = [(3.2, 3.5), (2.65, 2.0), (2.35, 0.0), (2.6, -2.0), (3.6, -3.9), (5.2, -5.1), (6.8, -5.5), (8.6, -5.2),
            (10.5, -4.1), (12.0, -2.6), (12.85, -1.5)]
    return dict(strokes=[(head, 'land', 'flick'), (bowl, 'join', 'flick')], cuts={}, top=(3.7, 9.9))

def ain_init():
    S = [([(4.95, 4.75), (4.1, 4.55), (3.45, 3.8), (3.15, 2.6), (3.15, 1.5), (3.05, 1.0), (2.0, 0.5), (1.0, 0.15),
           (0.0, 0.0), (-0.7, 0.0)], 'land', 'join'),
         ([(3.15, 1.05), (4.6, 1.35), (6.2, 1.65), (7.5, 1.95), (8.1, 2.15)], 'join', 'flick')]
    return dict(strokes=S, cuts=dict(left=0.0), top=(3.9, 6.7))

def ain_medi():
    """The writer's medial ع: a small filled triangle sitting on the line."""
    rc = 5.6
    S = [([(rc + 0.7, 0.0), (rc, 0.0), (4.55, -0.03), (3.9, 0.15), (4.1, 0.85), (4.2, 1.5), (3.6, 1.6), (3.0, 1.55),
           (3.15, 0.95), (3.5, 0.3), (2.6, 0.02), (1.0, 0.0), (0.0, 0.0), (-0.7, 0.0)], 'join', 'join'),
         ([(3.6, 0.6), (3.6, 1.2)], 'join', 'join')]          # fills the triangle: a blind head, no pinhole
    return dict(strokes=S, cuts=dict(left=0.0, right=rc), top=(3.6, 3.35))

def ain_fina():
    rc = 11.35
    P = [(rc + 0.7, 0.0), (rc, 0.0), (9.5, -0.35), (7.5, -0.95), (5.6, -1.45), (4.3, -1.35), (3.4, -0.75), (3.0, 0.3),
         (3.1, 1.6), (3.8, 2.9), (4.8, 3.5), (5.7, 3.2), (5.6, 2.2), (4.6, 1.0), (3.4, 0.0), (2.4, -1.3), (1.7, -3.2),
         (1.8, -5.3), (2.8, -7.2), (4.5, -8.6), (6.6, -9.3), (8.7, -8.8), (10.4, -7.3), (11.55, -5.6)]
    return dict(strokes=[(P, 'join', 'flick')], cuts=dict(right=rc), top=(4.6, 5.6))


def sad_body(T, medi=False):
    """tooth at T, flat base, the writer's leaf loop standing on it."""
    d = T - 5.95
    path = [(-0.7, 0.0), (0.0, 0.0), (0.8, 0.08), (T - 3.9, 0.6), (T - 1.75, 1.35), (T - 0.7, 1.95), (T, 2.75),
            (T + 0.45, 2.0), (T + 1.15, 1.3), (T + 2.45, 1.0), (T + 3.45, 0.95)]
    loop = [(T + 3.45, 0.95), (T + 4.65, 1.6), (T + 6.05, 2.6), (T + 7.15, 3.6), (T + 7.35, 4.3), (T + 6.65, 4.65),
            (T + 5.45, 4.3), (T + 4.35, 3.4), (T + 3.8, 2.3), (T + 3.65, 1.3)]
    S = [(path + loop[1:], 'join', 'join')]
    cuts = dict(left=0.0)
    if medi:
        rc = T + 8.4
        S.append(([(T + 3.6, 1.1), (T + 4.6, 0.55), (T + 6.0, 0.15), (T + 7.4, 0.0), (rc, 0.0), (rc + 0.7, 0.0)], 'join', 'join'))
        cuts['right'] = rc
    return dict(strokes=S, cuts=cuts, top=(T + 5.9, 6.4))

def sad_isol():
    tick = [(7.55, 6.75), (8.2, 5.55), (8.75, 4.6)]
    loop = [(8.75, 4.6), (10.6, 4.95), (12.5, 5.35), (14.2, 5.85), (15.7, 6.45), (16.45, 7.15), (16.1, 7.9), (14.95, 8.05),
            (13.75, 7.45), (13.05, 6.45), (12.55, 5.4)]
    bowl = [(8.75, 4.6), (8.7, 3.3), (8.15, 1.95), (6.9, 0.95), (5.0, 0.45), (3.3, 0.55), (2.0, 1.3), (1.45, 2.6),
            (1.55, 4.0), (1.95, 5.2)]
    return dict(strokes=[(tick, 'land', 'join'), (loop, 'join', 'join'), (bowl, 'join', 'flick')], cuts={}, top=(14.6, 9.9))

def sad_fina():
    rc = 15.5
    P = [(rc + 0.7, 0.0), (rc, 0.0), (14.0, -0.4), (12.4, -1.1), (11.1, -1.45), (10.25, -0.85), (9.95, 0.6), (10.2, 1.6),
         (11.1, 2.6), (12.4, 3.3), (13.6, 3.5), (14.15, 3.05), (13.6, 2.2), (12.2, 1.55), (10.8, 1.0), (9.4, 0.55),
         (7.8, 0.15), (6.4, 0.05), (5.75, 0.9), (5.45, 1.85)]
    bowl = [(5.45, 1.85), (5.75, 0.3), (5.65, -1.4), (4.6, -3.05), (3.0, -3.85), (1.55, -3.4), (0.8, -2.2), (0.7, -0.6),
            (0.95, 1.0)]
    return dict(strokes=[(P, 'join', 'join'), (bowl, 'join', 'flick')], cuts=dict(right=rc), top=(12.8, 5.4))


def glyph_defs():
    G = {}
    for fam, dot in (('hah', None), ('jeem', 'below'), ('khah', 'above')):
        i = hah_init(dot if dot == 'below' else None); m = hah_medi(dot if dot == 'below' else None)
        for g in (i, m):
            g['dots'] = [((g['apex'][0] - 0.35, g['apex'][1] + 1.9), DOT)] if dot == 'above' else []
        s = hah_isol(); f = hah_fina()
        s['dots'] = [] if dot is None else [(s['bowl'] if dot == 'below' else s['top'], DOT)]
        f['dots'] = [] if dot is None else [(f['bowl'] if dot == 'below' else f['top'], DOT)]
        G[fam] = s; G[fam + '.init'] = i; G[fam + '.medi'] = m; G[fam + '.fina'] = f
    for fam, dotted in (('ain', False), ('ghain', True), ('sad', False), ('dad', True)):
        mk = (ain_isol, ain_init, ain_medi, ain_fina) if fam in ('ain', 'ghain') else \
             (sad_isol, lambda: sad_body(4.2), lambda: sad_body(4.2, True), sad_fina)
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
