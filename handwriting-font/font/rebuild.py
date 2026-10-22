"""Stage 3: rebuild every glyph as clean pen strokes, so the whole font is one hand with one pen.

For each glyph from stage 2: centre-lines (pen6.analyse6) -> smoothing B-spline per stroke
(corners stay corners, they are stroke ends) -> one uniform pen with real landings and flicks.
Filled heads keep their mass, dots become the one standard dot. On the way, the calligraphic
measures are applied: ascenders to one height (your notebook: ~10.5 pen widths), every word
widened (horizontal strokes are the soul of Ruqʿah), connectors lengthened."""
import sys, pickle, numpy as np, cv2
from scipy.interpolate import splprep, splev
sys.path.insert(0, '../pens')
import pen4
from pen6 import analyse6
from stage2 import R_W, PEN, SIDE
from redraw import ease, DOT

pen4.SPUR = (1.0, 0.0)
WX = 1.15          # widen: horizontal proportion of every letter
EXT = 0.35         # extra connector length on each joining side (pen widths)
ASC = 10.5         # ascender height (pen widths), the notebook hand's alef
R0 = 22.6          # pen radius in px at R_W=44
SIDES = {'init': ('left',), 'medi': ('left', 'right'), 'fina': ('right',)}


def fit(P, closed, eps=0.13):
    """Smoothing B-spline through a stroke (pen-width units); returns dense points."""
    P = np.asarray(P, float)
    if closed and len(P) > 3 and np.allclose(P[0], P[-1]): P = P[:-1]
    keep = np.r_[True, np.hypot(*np.diff(P, axis=0).T) > 1e-6]
    P = P[keep]
    if len(P) < 4:
        return P
    try:
        tck, u = splprep(P.T, s=len(P) * eps ** 2, per=1 if closed else 0, k=3)
        L = np.hypot(*np.diff(P, axis=0).T).sum()
        q = np.array(splev(np.linspace(0, 1, max(20, int(L * 24))), tck)).T
        if not closed:                              # ends exactly where they were (joins, corners)
            n = len(q); k = np.arange(n); span = max(3, n // 8)
            wa = np.clip(1 - k / span, 0, 1)[:, None]; wb = np.clip(1 - (n - 1 - k) / span, 0, 1)[:, None]
            q = q + wa * (P[0] - q[0]) + wb * (P[-1] - q[-1])
        return q
    except Exception:
        return P


def smooth_closed(C, keep=5):
    """A filled head as a clean shape: low-pass its outline (first few Fourier harmonics)."""
    z = C[:, 0] + 1j * C[:, 1]
    t = np.r_[0, np.cumsum(np.abs(np.diff(z)))]; L = t[-1] + abs(z[0] - z[-1])
    tt = np.linspace(0, L, 256, endpoint=False)
    zr = np.interp(tt, np.r_[t, L], np.r_[z.real, z[0].real]) + 1j * np.interp(tt, np.r_[t, L], np.r_[z.imag, z[0].imag])
    F = np.fft.fft(zr); F[keep + 1:-keep] = 0
    zs = np.fft.ifft(F)
    return np.column_stack([zs.real, zs.imag])


def squash(P, top):
    """Bring tall ascenders down to ASC, gently (no kink): only the part above the body moves."""
    if top <= ASC + 0.05: return P
    k = (ASC - 3.0) / (top - 3.0)
    y = P[:, 1]; t = np.clip((y - 2.0) / 2.0, 0, 1); t = t * t * (3 - 2 * t)     # blend 2..4
    yn = np.where(y > 3.0, 3.0 + (y - 3.0) * k, y)
    return np.column_stack([P[:, 0], y * (1 - t) + yn * t])


def rebuild_glyph(g, name):
    img = g['img']; L0, B0 = g['left'], g['base']
    U = lambda P: np.column_stack([(P[:, 0] - L0) / R_W, (B0 - P[:, 1]) / R_W])
    w = 2 * R0
    n, lab, st, cen = cv2.connectedComponentsWithStats(img.astype(np.uint8), connectivity=8)
    dots, body = [], np.zeros_like(img)
    for i in range(1, n):
        x, y, ww, hh, a = st[i]
        if max(ww, hh) < 1.75 * R_W and min(ww, hh) > 0.6 * R_W and a > 0.5 * ww * hh and a < 2.6 * R_W * R_W:
            dots.append(U(np.array([cen[i]]))[0])
        else:
            body |= lab == i
    # filled heads: ink much wider than the pen
    dt = cv2.distanceTransform(body.astype(np.uint8), cv2.DIST_L2, 5)
    core = (dt > 0.82 * R_W).astype(np.uint8)
    heads = []
    if core.any():
        hm = cv2.dilate(core, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(1.7 * R_W) | 1,) * 2)) & body
        hm = cv2.GaussianBlur(hm.astype(np.float32), (0, 0), 0.12 * R_W) > 0.5
        cs, _ = cv2.findContours(hm.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        heads = [smooth_closed(U(c[:, 0, :].astype(float))) for c in cs if len(c) > 8]
    A = analyse6(body, w, extend=False) if body.sum() > 0.5 * R_W * R_W else dict(strokes=[], bridges=[])
    strokes = []
    for s in A['strokes'] + A['bridges']:
        if len(s['p']) < 2: continue
        strokes.append(dict(p=U(s['p']), closed=bool(s['closed']), free=list(s['free'])))
    # proportions: ascenders, then width
    allp = np.vstack([s['p'] for s in strokes] + heads) if (strokes or heads) else np.zeros((1, 2))
    top = allp[:, 1].max()
    right = (g['right'] - L0) / R_W
    for s in strokes: s['p'] = squash(s['p'], top) * [WX, 1]
    heads = [squash(h, top) * [WX, 1] for h in heads]
    dots = [squash(np.array([d]), top)[0] * [WX, 1] for d in dots]
    right *= WX
    form = g['form']
    sides = SIDES.get(form, ()) or (('right',) if name == 'lamalef.fina' else ())
    left_e = -EXT if 'left' in sides else None
    right_e = right + EXT if 'right' in sides else None
    for s in strokes:                                   # ends at a join edge: laid onto the baseline, run into the edge
        for e in (0, 1):
            P = s['p'] if e == 1 else s['p'][::-1]
            x, y = P[-1]
            side = 'left' if ('left' in sides and x < 1.2 and abs(y) < 1.3) else \
                   'right' if ('right' in sides and x > right - 1.2 and abs(y) < 1.3) else None
            if not side: continue
            s['free'][e] = False
            d = np.r_[0, np.cumsum(np.hypot(*np.diff(P[::-1], axis=0).T))][::-1]      # distance from this end
            u = np.clip(d / 1.8, 0, 1); u = u * u * (3 - 2 * u)
            P = np.column_stack([P[:, 0], P[:, 1] * u])
            ex = (left_e - 0.5) if side == 'left' else (right_e + 0.5)
            P = np.vstack([P, [[ex, 0.0]]])
            s['p'] = P if e == 1 else P[::-1]
        s['q'] = fit(s['p'], s['closed'])
    return dict(strokes=strokes, heads=heads, dots=dots, left=left_e, right=right_e, form=form, side=g.get('side'))


def render(G, pad=3.0):
    pts = np.vstack([s['q'] for s in G['strokes']] + G['heads'] + [np.array(G['dots'], float).reshape(-1, 2)] +
                    [np.array([[G['left'] or 0, 0], [G['right'] or 0, 0]])])
    xmin, ymin = pts.min(0) - pad; xmax, ymax = pts.max(0) + pad
    H, W = int((ymax - ymin) * R_W), int((xmax - xmin) * R_W)
    X = lambda P: np.column_stack([(P[:, 0] - xmin) * R_W, (ymax - P[:, 1]) * R_W])
    canvas = np.zeros((H, W), np.uint8)
    sq = np.sqrt(PEN['contrast']); fl = PEN['flicks']; r_pen = R0 * PEN['weight']
    def stamp(p, r):
        for (x, y), rr in zip(p, r):
            cv2.ellipse(canvas, (int(x * 16), int(y * 16)), (max(1, int(rr * sq * 16)), max(1, int(rr / sq * 16))),
                        -PEN['angle'], 0, 360, 1, -1, cv2.LINE_8, 4)
    for s in G['strokes']:
        p = X(s['q'])
        d = np.r_[0, np.cumsum(np.hypot(*np.diff(p, axis=0).T))] if len(p) > 1 else np.zeros(1)
        if len(p) > 1:                                    # even spacing for the stamps
            t = np.arange(0, d[-1] + 1e-6, 0.6)
            p = np.column_stack([np.interp(t, d, p[:, 0]), np.interp(t, d, p[:, 1])]); d = t
        Lp = d[-1]; r = np.full(len(p), r_pen)
        if not s['closed'] and len(p) > 3 and Lp > 1.2 * R_W:
            sc = [-p[0, 0] + 0.8 * p[0, 1], -p[-1, 0] + 0.8 * p[-1, 1]]
            fr = s['free']
            if fr[0] and fr[1]: modes = ['land', 'flick'] if sc[1] > sc[0] else ['flick', 'land']
            else: modes = [('flick' if sc[e] > sc[1 - e] else 'land') if fr[e] else None for e in (0, 1)]
            for e, mode in enumerate(modes):
                dist = d if e == 0 else Lp - d
                if mode == 'land': r = r * (0.72 + 0.28 * ease(dist / (1.0 * R_W)))
                elif mode == 'flick':
                    floor = 1 - 0.72 * fl; r = r * (floor + (1 - floor) * ease(dist / (2.4 * R_W)) ** 0.8)
        stamp(p, r)
    for h in G['heads']:
        cv2.fillPoly(canvas, [np.round(X(h) * 16).astype(np.int32)], 1, cv2.LINE_8, shift=4)
    for (cx, cy) in G['dots']:
        c = X(np.array([[cx, cy]]))[0]; a = np.radians(35)
        v = np.array([np.cos(a), -np.sin(a)]) * 0.32 * R_W * DOT
        q = np.stack([np.linspace(-1, 1, 15)] * 2, 1) * v + c
        stamp(q, r_pen * 1.25 * DOT * (0.75 + 0.25 * np.sin(np.pi * np.linspace(0, 1, 15))))
    img = cv2.GaussianBlur(canvas.astype(np.float32), (0, 0), 1.0) > .5
    ys, xs = np.where(img)
    left = X(np.array([[G['left'], 0]]))[0, 0] if G['left'] is not None else xs.min() - SIDE * R_W
    right = X(np.array([[G['right'], 0]]))[0, 0] if G['right'] is not None else xs.max() + SIDE * R_W
    base = ymax * R_W
    return dict(img=img, left=left, right=right, base=base, form=G['form'], side=G['side'], rw=R_W,
                ink=(xs.min(), ys.min(), xs.max(), ys.max()), scale=1.0)


# letters drawn directly as pen paths (pen-width units, origin = left join on the baseline)
CUSTOM = {
    # ـهـ : the figure-eight through the line, one stroke
    'heh.medi': dict(form='medi', right=4.9, strokes=[
        ([(4.9, 0.0), (4.2, 0.0), (3.3, 0.05), (2.75, 0.4), (2.55, 1.25), (2.65, 2.2), (2.3, 2.95), (1.6, 2.85), (1.25, 2.05),
          (1.45, 1.0), (1.9, 0.2), (2.2, -0.65), (2.05, -1.6), (1.5, -1.95), (1.05, -1.45), (1.05, -0.65), (0.7, -0.1), (0.0, 0.0)],
         False, [False, False])]),
    # ـلـ : one clean stem rising from the line (alef height, alef lean), no tick
    'lam.medi': dict(form='medi', right=3.0, strokes=[
        ([(3.0, 0.0), (2.2, 0.0), (1.55, 0.0), (0.9, 0.0), (0.0, 0.0)], False, [False, False]),
        ([(1.5, 10.25), (1.42, 7.0), (1.33, 3.5), (1.3, 1.0), (1.42, 0.12)], False, [True, False])]),
}


def custom_glyph(name):
    c = CUSTOM[name]
    st = [dict(p=np.array(p, float) * [WX, 1], closed=cl, free=list(fr)) for p, cl, fr in c['strokes']]
    for s in st: s['q'] = fit(s['p'], s['closed'], eps=0.05)
    sides = SIDES.get(c['form'], ())
    return dict(strokes=st, heads=[], dots=[], left=-EXT if 'left' in sides else None,
                right=c['right'] * WX + EXT if 'right' in sides else None, form=c['form'], side=None)


def run(inp='stage2r.pkl', out='stage3.pkl', only=None):
    D = pickle.load(open(inp, 'rb'))
    for name, g in D['glyphs'].items():
        if g['form'] == 'mark' or (only and name not in only): continue
        D['glyphs'][name] = render(custom_glyph(name) if name in CUSTOM else rebuild_glyph(g, name))
        print('.', end='', flush=True)
    print()
    pickle.dump(D, open(out, 'wb'))


if __name__ == '__main__':
    run()
