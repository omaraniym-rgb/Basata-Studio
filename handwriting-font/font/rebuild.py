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
CL = 1.75          # standard run from a letter's body to its join edge (pen widths), the same for every letter
ASC = 10.5         # ascender height (pen widths), the notebook hand's alef
R0 = 22.6          # pen radius in px at R_W=44
SIDES = {'init': ('left',), 'medi': ('left', 'right'), 'fina': ('right',)}


def fit(P, closed, eps=0.2):
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


def rail(P, closed):
    """The pen glides along the line: any near-horizontal part of a stroke close to the baseline
    is laid exactly onto it, blending smoothly where the stroke leaves the line."""
    if len(P) < 4: return P
    from scipy.ndimage import gaussian_filter1d
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))]
    if d[-1] < 0.3: return P
    t = np.arange(0, d[-1] + 1e-9, 0.05)
    Q = np.column_stack([np.interp(t, d, P[:, 0]), np.interp(t, d, P[:, 1])])
    mode = 'wrap' if closed else 'nearest'
    S = gaussian_filter1d(Q, 6, axis=0, mode=mode)                    # direction from the calm line, not the jitter
    g = np.gradient(S, axis=0)
    ang = np.degrees(np.arctan2(np.abs(g[:, 1]), np.abs(g[:, 0]) + 1e-9))
    sm = lambda v, a, b: np.clip((v - a) / (b - a), 0, 1) ** 2 * (3 - 2 * np.clip((v - a) / (b - a), 0, 1))
    w = (1 - sm(ang, 10, 24)) * (1 - sm(np.abs(Q[:, 1]), 0.4, 0.75))
    w = gaussian_filter1d(w, 8, mode=mode)
    Q[:, 1] = Q[:, 1] * (1 - np.clip(w * 1.15, 0, 1))
    return Q


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
    for s in strokes: s['p'] = rail(squash(s['p'], top) * [WX, 1], s['closed'])
    heads = [squash(h, top) * [WX, 1] for h in heads]
    for h in heads:                                     # heads sit on the line, never hang below the rail
        if h[:, 1].mean() > -0.6: h[:, 1] = np.maximum(h[:, 1], -0.5)
    if name.split('.')[0] in ('tah', 'zah'):            # the stem stands on its loop
        for s in strokes:
            if s['closed'] or s['p'][:, 1].max() < 5: continue
            e = 0 if s['p'][0, 1] < s['p'][-1, 1] else 1
            end = s['p'][0 if e == 0 else -1]
            others = np.vstack([o['p'] for o in strokes if o is not s])
            k = int(np.argmin(np.hypot(*(others - end).T))); gap = np.hypot(*(others[k] - end))
            if 0.05 < gap < 4.5:
                tgt = others[k] + (end - others[k]) / gap * 0.25
                P = np.vstack([s['p'], tgt[None]]) if e == 1 else np.vstack([tgt[None], s['p']])
                s['p'] = P; s['free'][e] = False
    dots = [squash(np.array([d]), top)[0] * [WX, 1] for d in dots]
    right *= WX
    form = g['form']
    sides = SIDES.get(form, ()) or (('right',) if name == 'lamalef.fina' else ())
    fam = name.split('.')[0]
    if sides and fam not in ('seen', 'sheen'):          # one measured run between letters, everywhere
        P = np.vstack([s['p'] for s in strokes if s['p'][:, 1].min() < 3.5] + heads)    # floating dashes don't count
        body = P[np.abs(P[:, 1]) > 0.8]
        if len(body):
            near = body[(body[:, 1] > -2.6) & (body[:, 1] < 3.0)]   # nor a tail swinging under, nor a leaning stem top
            near = near if len(near) else body
            x0 = body[body[:, 1] > -2.6][:, 0].min() - CL if 'left' in sides else 0.0
            x1 = near[:, 0].max() + CL if 'right' in sides else right
            cut = []
            for s in strokes:
                p = s['p'] - [x0, 0]
                keep = ~((np.abs(p[:, 1]) < 0.6) & ((('left' in sides) & (p[:, 0] < 0)) | (('right' in sides) & (p[:, 0] > x1 - x0))))
                if keep.all():
                    s['p'] = p; cut.append(s); continue
                idx = np.where(keep)[0]
                for run in np.split(idx, np.where(np.diff(idx) > 1)[0] + 1):
                    if len(run) < 3: continue
                    fr = [s['free'][0] and run[0] == 0, s['free'][1] and run[-1] == len(p) - 1]
                    cut.append(dict(p=p[run], closed=False, free=fr))
            strokes = cut
            heads = [h - [x0, 0] for h in heads]
            dots = [d - [x0, 0] for d in dots]
            right = x1 - x0
        # the pen never lifts on the line: a free end resting near another stroke joins it
        for s in strokes:
            if s['closed']: continue
            for e in (0, 1):
                end = s['p'][0 if e == 0 else -1]
                if not s['free'][e] or abs(end[1]) > 1.0: continue
                others = [o['p'] for o in strokes if o is not s]
                if not others: continue
                O = np.vstack(others); k = int(np.argmin(np.hypot(*(O - end).T))); gap = np.hypot(*(O[k] - end))
                if 0.05 < gap < 3.2:
                    tgt = O[k] + (end - O[k]) / gap * 0.2
                    s['p'] = np.vstack([s['p'], tgt[None]]) if e == 1 else np.vstack([tgt[None], s['p']])
                    s['free'][e] = False
    left_e = -EXT if 'left' in sides else None
    right_e = right + EXT if 'right' in sides else None
    for s in strokes:                                   # strokes meeting on the rail meet exactly on the line
        if s['closed'] or len(s['p']) < 3: continue
        for e in (0, 1):
            if s['free'][e]: continue
            P = s['p'] if e == 1 else s['p'][::-1]
            if abs(P[-1, 1]) > 0.6: continue
            d = np.r_[0, np.cumsum(np.hypot(*np.diff(P[::-1], axis=0).T))][::-1]
            u = np.clip(d / 0.9, 0, 1); u = u * u * (3 - 2 * u)
            P = np.column_stack([P[:, 0], P[:, 1] * u])
            s['p'] = P if e == 1 else P[::-1]
    ends = {}                                           # each join side: the stroke end nearest the join point
    for side in sides:
        gx = 0.0 if side == 'left' else right
        best = None
        for si, s in enumerate(strokes):
            if s['closed']: continue
            for e in (0, 1):
                x, y = s['p'][0 if e == 0 else -1]
                dd = np.hypot(x - gx, 1.6 * y)
                if dd < 3.4 and (best is None or dd < best[0]): best = (dd, si, e)
        if best: ends[(best[1], best[2])] = side
    for si, s in enumerate(strokes):                    # ends at a join edge: laid onto the baseline, run into the edge
        for e in (0, 1):
            P = s['p'] if e == 1 else s['p'][::-1]
            side = ends.get((si, e))
            if not side: continue
            s['free'][e] = False
            d = np.r_[0, np.cumsum(np.hypot(*np.diff(P[::-1], axis=0).T))][::-1]      # distance from this end
            u = np.clip(d / 1.8, 0, 1); u = u * u * (3 - 2 * u)
            P = np.column_stack([P[:, 0], P[:, 1] * u])
            ex = (left_e - 0.5) if side == 'left' else (right_e + 0.5)
            P = np.vstack([P, [[ex, 0.0]]])
            s['p'] = P if e == 1 else P[::-1]
        s['q'] = fit(s['p'], s['closed'])
        if sides: s['q'] = rail(s['q'], s['closed'])
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
                ink=(xs.min(), ys.min(), xs.max(), ys.max()), scale=1.0, entry_y=G.get('entry_y', 0.0))


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

# سـ ـسـ : the flat Ruqʿah seen, a short start tick then one run on the line
CUSTOM['seen.init'] = dict(form='init', strokes=[
    ([(4.0, 1.0), (3.75, 0.45), (3.45, 0.08), (2.9, 0.0), (1.6, 0.0), (0.0, 0.0)], False, [True, False])])
CUSTOM['seen.medi'] = dict(form='medi', right=3.6, strokes=[
    ([(3.6, 0.0), (2.6, 0.0), (1.2, 0.0), (0.0, 0.0)], False, [False, False])])


# ـد ـذ : from the notebook sheet, the run on the line, a short upright, and a light flick away down-left
DAL_FINA = [([(4.4, 0.0), (3.6, 0.0), (2.9, 0.02), (2.45, 0.1)], False, [False, False]),
            ([(2.4, 0.12), (2.38, 1.0), (2.5, 2.0), (2.85, 2.8)], False, [False, True]),
            ([(2.45, 0.1), (1.9, -0.12), (1.0, -0.42), (0.0, -0.72)], False, [False, True])]
CUSTOM['dal.fina'] = dict(form='fina', right=4.4, strokes=DAL_FINA)
CUSTOM['thal.fina'] = dict(form='fina', right=4.4, strokes=DAL_FINA, dots=[(2.3, 4.2)])

# ح ج خ joined: the stacked Ruqʿah form from the notebook (تحول, المرابحة). The letter before sits up on the head:
# the pen enters at the top (STK), runs left-down to the vertex, flicks back right, then one long diagonal to the line.
STK = 5.6                                          # entry height (pen widths): the shaping engine lifts the letters before
HAH_STK_MEDI = [(6.75, STK), (6.0, STK - 0.08), (5.0, STK - 0.6), (3.9, STK - 1.45), (3.0, STK - 2.3)]
# the deep "<" of the notebook: the flick runs back almost under the entry, then turns round into the diagonal
HAH_STK_TURN = [(3.0, STK - 2.3), (4.0, STK - 2.5), (4.85, STK - 2.68), (5.3, STK - 2.85)]
HAH_STK_DIAG = [(5.3, STK - 2.85), (5.5, STK - 3.1), (5.3, STK - 3.45), (4.7, 1.75), (3.7, 1.1), (2.6, 0.5), (1.5, 0.12),
                (0.5, 0.0), (-0.5, 0.0)]
CUSTOM['hah.medi'] = dict(form='medi', right=6.0, entry_y=STK, strokes=[
    (HAH_STK_MEDI, False, [False, False]), (HAH_STK_TURN[:-1] + HAH_STK_DIAG, False, [False, False])])
CUSTOM['jeem.medi'] = dict(CUSTOM['hah.medi'], dots=[(4.2, 0.55)])
CUSTOM['khah.medi'] = dict(CUSTOM['hah.medi'], dots=[(3.3, STK + 1.35)])


def _hah_fina_stk():
    from redraw import tr, H_DESC, KH
    W = np.array(HAH_STK_TURN[-1]); ay = 3.5
    bowl = np.array(tr(H_DESC, KH, (262, 342), ay)) + [W[0], W[1] - ay]
    dot = np.array(tr([(271, 462)], KH, (262, 342), ay))[0] + [W[0], W[1] - ay]
    return bowl, dot


_B, _D = _hah_fina_stk()
CUSTOM['hah.fina'] = dict(form='fina', right=6.0, entry_y=STK, strokes=[
    (HAH_STK_MEDI, False, [False, False]), (HAH_STK_TURN, False, [False, False]), (_B.tolist(), False, [False, True])])
CUSTOM['jeem.fina'] = dict(CUSTOM['hah.fina'], dots=[tuple(_D)])
CUSTOM['khah.fina'] = dict(CUSTOM['hah.fina'], dots=[(3.3, STK + 1.35)])



def _meem_head(cx=1.95, cy=0.78, rx=1.2, ry=0.78, tilt=18):
    t = np.linspace(0, 2 * np.pi, 64, endpoint=False); a = np.radians(tilt)
    x, y = rx * np.cos(t), ry * np.sin(t)
    return np.column_stack([cx + x * np.cos(a) - y * np.sin(a), cy + x * np.sin(a) + y * np.cos(a)]).tolist()


# مـ ـمـ : the Ruqʿah meem, a small filled head sitting on the line; the pen leaves from its foot
CUSTOM['meem.init'] = dict(form='init', heads=[_meem_head()], strokes=[
    ([(1.55, 0.18), (1.0, 0.03), (0.4, 0.0), (0.0, 0.0)], False, [False, False])])
# ـمـ ـم stacked, as in the notebook (عملية، العميل): the letter before sits up, one diagonal brings the pen down
# onto the head, and the pen leaves along the line (medial) or drops into the tail (final).
MSTK = 3.6
MEEM_IN = [(5.6, MSTK), (5.0, MSTK - 0.08), (4.45, MSTK - 0.45), (3.75, MSTK - 1.25), (3.15, 1.75), (2.75, 1.35)]
CUSTOM['meem.medi'] = dict(form='medi', right=4.85, entry_y=MSTK, heads=[_meem_head()], strokes=[
    ([(1.55, 0.18), (1.0, 0.03), (0.4, 0.0), (0.0, 0.0)], False, [False, False]),
    (MEEM_IN, False, [False, False])])
_MF = 2.6                                          # final: the same meem moved right to make room for the tail
CUSTOM['meem.fina'] = dict(form='fina', right=4.85 + _MF, entry_y=MSTK, heads=[_meem_head(cx=1.95 + _MF)], strokes=[
    ([(x + _MF, y) for x, y in MEEM_IN], False, [False, False]),
    ([(1.4 + _MF, 0.2), (0.75 + _MF, -0.55), (1.6, -1.9), (0.95, -3.3), (0.7, -4.4), (1.0, -5.1), (1.75, -5.35), (2.55, -5.2)],
     False, [False, True])])


def _from_redraw(fn, k, stem=None, form='medi'):
    from redraw import sad_init, sad_medi
    g = {'init': sad_init, 'medi': sad_medi}[fn]()
    st = []
    for pts, m0, m1 in g['strokes']:
        P = np.array(pts, float) * k
        st.append((P.tolist(), False, [m0 == 'land', m1 == 'land']))
    if stem: st.append((stem, False, [True, False]))
    out = dict(form=form, strokes=st)
    if 'right' in g['cuts']: out['right'] = g['cuts']['right'] * k
    return out


TAH_K = 0.82
TAH_STEM = [(2.35, 10.2), (2.2, 7.0), (2.05, 4.5), (1.98, 2.7)]
CUSTOM['tah.medi'] = _from_redraw('medi', TAH_K, TAH_STEM)
CUSTOM['tah.init'] = _from_redraw('init', TAH_K, TAH_STEM, form='init')
CUSTOM['zah.medi'] = dict(CUSTOM['tah.medi'], dots=[(3.4, 5.6)])
CUSTOM['zah.init'] = dict(CUSTOM['tah.init'], dots=[(3.4, 5.6)])


def custom_glyph(name):
    c = CUSTOM[name]
    st = [dict(p=np.array(p, float) * [WX, 1], closed=cl, free=list(fr)) for p, cl, fr in c['strokes']]
    for s in st: s['q'] = rail(fit(s['p'], s['closed'], eps=0.05), s['closed'])
    sides = SIDES.get(c['form'], ())
    return dict(strokes=st, heads=[np.array(h, float) * [WX, 1] for h in c.get('heads', [])],
                dots=[np.array(d) * [WX, 1] for d in c.get('dots', [])], left=-EXT if 'left' in sides else None,
                right=c['right'] * WX + EXT if 'right' in sides else None, form=c['form'], side=None,
                entry_y=c.get('entry_y', 0.0))


TOOTH = ('teh', 'theh', 'noon', 'yeh')                # Ruqʿah: these share one tooth with ب, only the dots differ


SHARE = {'sheen.init': 'seen.init', 'sheen.medi': 'seen.medi'}


def shared_tooth(D, name, base_name=None):
    fam, form = name.split('.')
    base_name = base_name or 'beh.' + form
    base = custom_glyph(base_name) if base_name in CUSTOM else rebuild_glyph(D['glyphs'][base_name], base_name)
    own = rebuild_glyph(D['glyphs'][name], name)
    is_mark = lambda p: p[:, 1].min() > 1.3 or p[:, 1].max() < -0.45
    body = [s for s in base['strokes'] if not is_mark(s['q'])]
    marks = [s for s in own['strokes'] if is_mark(s['q'])]
    for s in marks:                                # dots below hang at one depth under every tooth
        if s['q'][:, 1].max() < 0: s['q'] = s['q'] + [0, -1.35 - s['q'][:, 1].mean()]
    B = np.vstack([s['q'] for s in body])
    tx = B[:, 0][B[:, 1] > 0.45].mean() if (B[:, 1] > 0.45).any() else B[:, 0].mean()
    pts = [s['q'] for s in marks] + [np.array(own['dots']).reshape(-1, 2)]
    allm = np.vstack(pts) if any(len(p) for p in pts) else None
    dx = tx - allm[:, 0].mean() if allm is not None and len(allm) else 0.0
    for s in marks: s['q'] = s['q'] + [dx, 0]
    return dict(base, strokes=body + marks, dots=[d + [dx, 0] for d in own['dots']])


def run(inp='stage2r.pkl', out='stage3.pkl', only=None):
    D = pickle.load(open(inp, 'rb'))
    for name, g in list(D['glyphs'].items()):
        if g['form'] == 'mark' or (only and name not in only): continue
        if name.split('.')[0] in TOOTH and g['form'] in ('init', 'medi'):
            G = shared_tooth(D, name)
        elif name in SHARE:
            G = shared_tooth(D, name, SHARE[name])
        else:
            G = custom_glyph(name) if name in CUSTOM else rebuild_glyph(g, name)
        if name.split('.')[0] in TOOTH + ('beh',) and g['form'] in ('init', 'medi'):
            G['dots'] = [np.array([d[0], -1.35]) if d[1] < 0 else d for d in G['dots']]
        D['glyphs'][name] = render(G)
        print('.', end='', flush=True)
    print()
    pickle.dump(D, open(out, 'wb'))


if __name__ == '__main__':
    run()
