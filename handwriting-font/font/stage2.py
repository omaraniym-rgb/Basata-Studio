"""Stage 2: your pen on every glyph, perfect joins, outlines in font units."""
import sys, copy, pickle, numpy as np, cv2, potrace
sys.path.insert(0, '../pens')
from repen import UP
from pen6 import analyse6, render6
import pen4
pen4.SPUR = (0.8, 0.0)      # the letter sheets were written with care: keep short legs (the ج's crossing dot)
from glyphmap import JOINS, G as GM

PEN = dict(fluency=1.0, stems=0.8, contrast=1.3, flicks=0.95, calm=0.9, weight=1.05, angle=46)
TALL = {'alef', 'lam', 'kaf', 'tah', 'zah', 'lamalef', 'alefHamzaAbove', 'alefHamzaBelow', 'alefMadda'}
R_W = 44.0          # render resolution: pixels per pen width
TAIL = 0.9          # connector kept beyond the letter body, in pen widths
OVER = 0.10         # ink overlap past the join edge so joins never show a seam
SIDE = 0.55         # side bearing on non-joining sides, in pen widths


def _smoothstep(u):
    u = np.clip(u, 0, 1); return u * u * (3 - 2 * u)


def fix_join(A, side, base, w, extent, wt=None, span=None):
    """Make the connector on `side` a standard horizontal stroke on the baseline. Returns the cut x."""
    wt = wt or w
    best = None
    for si, s in enumerate(A['strokes']):
        if s.get('dot') or s['closed'] or len(s['p']) < 2: continue
        for e in (0, 1):
            pt = s['p'][0 if e == 0 else -1]
            if abs(pt[1] - base) > 1.8 * w: continue
            if side == 'left' and pt[0] > extent + 1.5 * w: continue
            if side == 'right' and pt[0] < extent - 1.5 * w: continue
            key = pt[0] if side == 'left' else -pt[0]
            if best is None or key < best[0]: best = (key, si, e)
    sgn = -1 if side == 'left' else 1
    if best is None:     # no connector drawn: grow one from the body point nearest the baseline edge
        allp = np.vstack([s['p'] for s in A['strokes']])
        tgt = np.array([extent, base]); k = int(np.argmin(np.hypot(*(allp - tgt).T)))
        B = allp[k]; Q_rest = np.zeros((0, 2)); r_rest = np.zeros(0); s = None
    else:
        _, si, e = best; s = A['strokes'][si]
        Q = s['p'] if e == 0 else s['p'][::-1]; R = s['r'] if e == 0 else s['r'][::-1]
        k = max(2, int(w)); i = 0
        while i < len(Q) - 1:
            j = min(len(Q) - 1, i + k); d = Q[j] - Q[i]
            if abs(Q[i][1] - base) > 0.75 * w or abs(d[1]) > 0.7 * abs(d[0]) + 1e-6: break
            if span and abs(Q[i][0] - extent) > 0.4 * span: break      # never eat the letter itself
            i += 1
        B = Q[i]; Q_rest = Q[i + 1:]; r_rest = R[i + 1:]
    cut = B[0] + sgn * TAIL * wt
    xs = np.arange(cut + sgn * 0.6 * wt, B[0], -sgn * 1.0)            # from beyond the edge back to the body
    ease = 1 - _smoothstep(np.abs(xs - B[0]) / (1.2 * wt))
    tail = np.stack([xs, base + (B[1] - base) * ease], 1)
    rmed = A['rmed']
    if s is None:
        A['strokes'].append(dict(p=np.vstack([tail, B[None]]), r=np.full(len(tail) + 1, rmed), closed=False,
                                 free=[False, False], bridged=[False, False], loop=None, stem=None, joined=[0]))
    else:
        newQ = np.vstack([tail, B[None], Q_rest]); newR = np.r_[np.full(len(tail) + 1, rmed), r_rest]
        if e == 1: newQ, newR = newQ[::-1], newR[::-1]
        s['p'], s['r'] = newQ, newR
        s['free'][e] = False; s['bridged'][e] = False
        s.setdefault('joined', []).append(e)
    return float(cut)


def scale_A(A, k, off):
    B = copy.deepcopy(A)
    for s in B['strokes'] + B['bridges']:
        s['p'] = s['p'] * k + off; s['r'] = s['r'] * k
        if s.get('loop'):
            s['loop']['pivot'] = (np.array(s['loop']['pivot']) * k + off).tolist(); s['loop']['R'] *= k
    B['w'] *= k; B['rmed'] *= k
    B['words'] = {}; B['lines'] = []
    for s in B['strokes'] + B['bridges']: s['line'] = -1
    return B


def trace(img):
    bm = potrace.Bitmap(~img)
    return bm.trace(turdsize=12, alphamax=1.0, opticurve=True, opttolerance=0.25)


def pull_ascender(A, base, w, want_up, body=1.2):
    """Stretch everything above the letter's body zone so the ascender reaches the standard height."""
    allp = np.vstack([s['p'] for s in A['strokes'] + A['bridges']])
    top = allp[:, 1].min(); y_cut = base - body * w
    have = y_cut - top; want = want_up - body * w
    if have <= 0.3 * w or want <= 0: return
    f = float(np.clip(want / have, 0.75, 4.0))
    for s in A['strokes'] + A['bridges']:
        P = s['p'].copy(); hi = P[:, 1] < y_cut
        P[hi, 1] = y_cut - (y_cut - P[hi, 1]) * f
        s['p'] = P
        if s.get('loop'):
            lp = s['loop']; py = lp['pivot'][1]
            if py < y_cut: lp['pivot'][1] = y_cut - (y_cut - py) * f


def X_(x, k, pad):
    return x * k + pad


def body_box(A, cuts, m):
    """Ink extent between the join cuts (what the eye reads as the letter)."""
    ys, xs = np.where(m)
    x0 = cuts.get('left', xs.min()); x1 = cuts.get('right', xs.max())
    sel = (xs >= x0) & (xs <= x1)
    return x1 - x0, ys[sel].max() - ys[sel].min()


def analyse_joined(m, base, form, wa, wt, keep=False):
    A = analyse6(m, wa, extend=False)
    cuts = {}
    if form not in ('mark', 'digit'):
        jl, jr = JOINS[form]
        ys, xs = np.where(m); span = xs.max() - xs.min()
        if keep or (ys.max() - ys.min()) < 2.4 * wa: span = 1e-6     # written flat (Ruqʿah س) or marked: the whole ink is the letter
        if jl: cuts['left'] = fix_join(A, 'left', base, wa, xs.min(), wt, span)
        if jr: cuts['right'] = fix_join(A, 'right', base, wa, xs.max(), wt, span)
    return A, cuts


def run(inp, out, ref_scale=True):
    from proportions import ref_metrics
    D = pickle.load(open(inp, 'rb'))
    G = D['glyphs']
    REF = ref_metrics(list(G))
    # pass 1: body sizes in pen widths
    first = {}
    for name, g in G.items():
        A, cuts = analyse_joined(g['mask'], g['base'] if g['base'] is not None else 0, g['form'], g['w'], g['w'], GM[name].get('keep', False))
        bw, bh = body_box(A, cuts, g['mask'])
        first[name] = (bw / g['w'], bh / g['w'])
    alef_u = float(np.median([first[n][1] for n in ('alef', 'alef.fina', 'alefHamzaBelow', 'lam')]))
    scales = {}
    for name, g in G.items():
        r = REF.get(name)
        if not ref_scale or r is None:
            scales[name] = 1.0; continue
        bw, bh = first[name]
        sw, sh = r['w'] * alef_u / bw, r['h'] * alef_u / bh
        fam = name.split('.')[0]
        lo = 0.7
        if fam in TALL:                                  # ascenders: size by width, the stem is pulled to height later
            scales[name] = 1.0 if r['w'] < 0.4 * r['h'] else float(np.clip(sw, 0.75, 1.35)); continue
        if r['w'] < 0.4 * r['h']: a = 0.0
        elif bh < 1.6 or GM[name].get('keep_flat'): a, lo = 1.0, 0.3   # written flat (Ruqʿah س, م): width decides
        else: a = 0.5
        s = sw ** a * sh ** (1 - a)
        scales[name] = float(np.clip(s, lo, 1.6)) * GM[name].get('grow', 1.0)
    # pass 2: rescale each glyph to the standard, analyse again, standard joins
    res, ana = {}, {}
    for name, g in G.items():
        s = scales[name]; m = g['mask']
        if abs(s - 1) > 0.02:
            m = cv2.resize(m.astype(np.float32), None, fx=s, fy=s, interpolation=cv2.INTER_LINEAR) > 0.5
        base = g['base'] * s if g['base'] is not None else None
        r_ = REF.get(name)
        if base is not None and r_ is not None and g['form'] in ('isol', 'digit') and not name.startswith('lamalef'):
            ys_, xs_ = np.where(m)                                  # seat it on the line like the reference first
            base = float(ys_.max() - max(r_['down'], 0.0) * alef_u * g['w'])   # never float above the line
        A, cuts = analyse_joined(m, base if base is not None else 0, g['form'], g['w'] * s, g['w'], GM[name].get('keep', False))
        if name.split('.')[0] in TALL and base is not None and name in REF:
            fam = name.split('.')[0]
            pull_ascender(A, base, g['w'], REF[name]['up'] * alef_u * g['w'], 2.8 if fam in ('tah', 'zah') else 1.3)
        ana[name] = (A, cuts, m, base, s)
    angs = [st['stem']['angle'] for A, *_ in ana.values() for st in A['strokes'] if st.get('stem')]
    lean = float(np.median(angs)) if angs else 0.0
    for name, g in G.items():
        A, cuts, m, base_s, s = ana[name]; A['stem_target'] = lean
        if GM[name].get('blind'):
            for st in A['strokes']: st['blind'] = True
        w = g['w']; k = R_W / w; pad = int(3 * R_W)
        Ak = scale_A(A, k, np.array([pad, pad]))
        Ak['w'] = R_W; Ak['rmed'] = A['rmed'] * k / s          # one physical pen for every glyph
        for st in Ak['strokes'] + Ak['bridges']: st['r'] = st['r'] / s   # thickness is the pen's, not the letter's size
        H, W = int(m.shape[0] * k) + 2 * pad, int(m.shape[1] * k) + 2 * pad
        top = min(float(st['p'][:, 1].min()) for st in Ak['strokes'] + Ak['bridges'] if len(st['p']))
        lift = max(0, int(2 * R_W - top))          # stretched ascenders must stay on the canvas
        if lift:
            for st in Ak['strokes'] + Ak['bridges']:
                st['p'] = st['p'] + np.array([0, lift])
                if st.get('loop'): st['loop']['pivot'][1] += lift
            H += lift
        if name == 'digit0':
            img = np.zeros((H, W), bool); cy, cx = int(X_(m.shape[0] / 2, k, pad)), int(X_(m.shape[1] / 2, k, pad))
            cv2.ellipse(img.view(np.uint8), (cx, cy), (int(0.95 * R_W), int(0.7 * R_W)), -40, 0, 360, 1, -1)
            img = img.astype(bool)
        else:
            img = render6(Ak, (H, W), snap=0, level=0, heads=not GM[name].get('thin'), **PEN)
        X = lambda x: x * k + pad
        if GM[name].get('counters'):           # tiny counters the pen would swallow: punch your original back out
            k4, lab4, st4, _ = cv2.connectedComponentsWithStats((~m).astype(np.uint8), connectivity=4)
            hole = np.zeros(m.shape, np.uint8)
            for i in range(1, k4):
                x_, y_, w_, h_, a_ = st4[i]
                if x_ > 0 and y_ > 0 and x_ + w_ < m.shape[1] and y_ + h_ < m.shape[0]: hole[lab4 == i] = 1
            if hole.any():
                hk = cv2.resize(hole, (int(m.shape[1] * k), int(m.shape[0] * k)), interpolation=cv2.INTER_NEAREST)
                hk = cv2.dilate(hk, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(0.25 * R_W) | 1,) * 2))
                full = np.zeros_like(img); full[pad:pad + hk.shape[0], pad:pad + hk.shape[1]] = hk[:H - pad, :W - pad] > 0
                img &= ~full
        if base_s is not None:                 # clear beyond the joins, but only in the connector band:
            y0b, y1b = max(0, int(X(base_s) + lift - 1.7 * R_W)), int(X(base_s) + lift + 1.7 * R_W)   # stems and tails may overhang
            if 'left' in cuts: img[y0b:y1b, :max(0, int(X(cuts['left'] - OVER * w)))] = False
            if 'right' in cuts: img[y0b:y1b, int(X(cuts['right'] + OVER * w)):] = False
        ys, xs = np.where(img)
        if not len(xs):
            print('empty', name); continue
        left = X(cuts['left']) if 'left' in cuts else xs.min() - SIDE * R_W
        right = X(cuts['right']) if 'right' in cuts else xs.max() + SIDE * R_W
        base = X(base_s) + lift if base_s is not None else None
        res[name] = dict(img=img, left=left, right=right, base=base, form=g['form'], side=g.get('side'),
                         rw=R_W, ink=(xs.min(), ys.min(), xs.max(), ys.max()), scale=s)
        print('.', end='', flush=True)
    print()
    pickle.dump(dict(glyphs=res, lean=lean, alef_u=alef_u), open(out, 'wb'))
    print('glyphs', len(res), 'shared lean', round(lean, 1), 'alef', round(alef_u, 1), 'pen widths')
    sc = sorted(scales.items(), key=lambda kv: kv[1])
    print('most shrunk', [(k, round(v, 2)) for k, v in sc[:6]], 'most grown', [(k, round(v, 2)) for k, v in sc[-6:]])


if __name__ == '__main__':
    run('stage1.pkl', 'stage2.pkl')
