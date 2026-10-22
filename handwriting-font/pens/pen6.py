"""Pen model v6: a professional's line.

  - continuation: at every junction, the two branches that carry on from each other
    become one stroke, so the line flows through the join instead of stopping at it
  - reattach: the remaining branch is glued back onto the smoothed line (no pen breaks)
  - twicing: 2·G(p) − G(G(p)) removes tremor without shrinking curves"""
import numpy as np, cv2
from scipy.ndimage import gaussian_filter1d
from pen3 import _resample
from pen4 import _rot, _length
from pen5 import analyse5, words, fit_lines, _ease


def _out_dir(P, at_start, w):
    Q = P if at_start else P[::-1]
    k = min(len(Q) - 1, max(2, int(1.5 * w)))
    v = Q[k] - Q[0]
    return v / (np.linalg.norm(v) + 1e-9)


def continuation(A, w):
    S = A['strokes']
    changed = True
    while changed:
        changed = False
        ends = []
        for i, s in enumerate(S):
            if s['closed'] or s.get('loop') or s.get('stem') or s.get('dot') or len(s['p']) < 4:
                continue
            for e in (0, 1):
                if not s['free'][e]:
                    ends.append((i, e, s['p'][0 if e == 0 else -1]))
        used = set()
        best = []
        for a in range(len(ends)):
            for b in range(a + 1, len(ends)):
                (i, ei, pi), (j, ej, pj) = ends[a], ends[b]
                if i == j or np.hypot(*(pi - pj)) > 3.5:
                    continue
                da = _out_dir(S[i]['p'], ei == 0, w); db = _out_dir(S[j]['p'], ej == 0, w)
                ang = np.degrees(np.arccos(np.clip(np.dot(da, db), -1, 1)))
                if ang >= 145:
                    best.append((-ang, a, b))
        for _, a, b in sorted(best):
            (i, ei, _), (j, ej, _) = ends[a], ends[b]
            if i in used or j in used:
                continue
            A_, B_ = S[i], S[j]
            pa = A_['p'] if ei == 1 else A_['p'][::-1]; ra = A_['r'] if ei == 1 else A_['r'][::-1]
            pb = B_['p'] if ej == 0 else B_['p'][::-1]; rb = B_['r'] if ej == 0 else B_['r'][::-1]
            fa = A_['free'][0] if ei == 1 else A_['free'][1]; fb = B_['free'][1] if ej == 0 else B_['free'][0]
            ba = A_['bridged'][0] if ei == 1 else A_['bridged'][1]; bb = B_['bridged'][1] if ej == 0 else B_['bridged'][0]
            m = dict(A_); m.update(p=np.vstack([pa, pb[1:]]), r=np.r_[ra, rb[1:]], free=[fa, fb], bridged=[ba, bb], hooks=[])
            S[i] = m; S[j] = None; used |= {i, j}; changed = True
        S = [s for s in S if s is not None]
    A['strokes'] = S
    return A


def close_touches(A, w):
    """An end that touches another stroke is a join, not a flick; an end that stops just short
    while pointing at a stroke is extended to meet it."""
    S = [s for s in A['strokes'] if not s.get('dot')]
    added = []
    for s in S:
        for e in (0, 1):
            if not s['free'][e] or len(s['p']) < 3:
                continue
            pe = s['p'][0 if e == 0 else -1]
            best, bp = 1e9, None
            for o in S:
                if o is s: continue
                dd = np.hypot(*(o['p'] - pe).T); k = int(dd.argmin())
                if dd[k] < best: best, bp = dd[k], o['p'][k]
            if bp is None:
                continue
            if best < 0.6 * w:
                s['free'][e] = False; s.setdefault('touch', []).append(e)
            elif best < 1.8 * w:
                t = -_out_dir(s['p'], e == 0, w)               # direction the stroke was heading
                u = (bp - pe) / (best + 1e-9)
                if np.dot(t, u) > np.cos(np.radians(45)):
                    n = max(3, int(best) + 1); tt = np.linspace(0, 1, n)[:, None]
                    seg = pe + (bp - pe) * tt
                    rr = np.full(n, float(s['r'][0 if e == 0 else -1]))
                    added.append(dict(p=seg, r=rr, closed=False, free=[False, False], bridged=[False, False],
                                      bridge=True, line=s.get('line', -1), word=s.get('word', -1)))
                    s['free'][e] = False; s['bridged'][e] = True
    A['bridges'] = A['bridges'] + added
    return A


def analyse6(mask, w):
    A = analyse5(mask, w)                 # words + lines already fitted on the raw strokes
    W, lines = A['words'], A['lines']
    A = continuation(A, w)
    A = close_touches(A, w)
    A['words'], A['lines'] = W, lines
    return A


def _twice(a, sigma, closed):
    mode = 'wrap' if closed else 'nearest'
    g = gaussian_filter1d(a, sigma, axis=0, mode=mode)
    return 2 * g - gaussian_filter1d(g, sigma, axis=0, mode=mode)


def _smooth2(p, sigma, closed, pin=True):
    if sigma <= 0 or len(p) < 5:
        return p
    s = min(sigma, len(p) / 6)
    q = _twice(p, s, closed)
    if pin and not closed:
        n = len(p); k = np.arange(n)
        wa = np.clip(1 - k / (2.5 * s), 0, 1)[:, None]; wb = np.clip(1 - (n - 1 - k) / (2.5 * s), 0, 1)[:, None]
        q = q + wa * (p[0] - q[0]) + wb * (p[-1] - q[-1])
    return q


def render6(A, shape, snap=0.0, fluency=0.0, stems=0.0, level=0.0, contrast=1.0, angle=68, flicks=0.0,
            calm=0.0, weight=1.0):
    w, rmed = A['w'], A['rmed']
    sq = np.sqrt(contrast); heavy = np.array([-1.0, 1.0]) / np.sqrt(2)
    items = A['strokes'] + (A['bridges'] if fluency > 0.5 else [])
    prep = []
    # ---- pass 1: geometry ----
    for s in items:
        P = s['p'].copy()
        P[:, 1] += A['words'].get(s.get('word'), {}).get('delta', 0.0) * snap
        if stems > 0 and s.get('stem'):
            st = s['stem']; piv = P[0] if st['pivot'] == 0 else P[-1]
            P = _rot(P, piv, -(A['stem_target'] - st['angle']) * stems)
        if level > 0 and s.get('line', -1) >= 0:
            L = A['lines'][s['line']]
            if L.get('base'):
                m, b = L['base']; cx = L['cx']; P = _rot(P, np.array([cx, m * cx + b]), L['angle'] * level)
        rm = np.minimum(s['r'], 1.6 * rmed)
        solid = not s.get('loop') and _length(s['p']) < 3 * w
        re = np.where((rm > 1.45 * rmed) & solid, np.minimum(rm, 1.45 * rmed), rmed)
        if fluency > 0 and s.get('loop'):
            lp = s['loop']; need = rmed * 1.15 + 0.42 * w
            if lp['R'] < need:
                k = 1 + (need / max(lp['R'], 1e-3) - 1) * fluency; piv = np.array(lp['pivot']); P = piv + (P - piv) * k
        p, rm_ = _resample(P, rm, s['closed']); _, re_ = _resample(P, re, s['closed'])
        sig = calm * 1.4 * w
        if s.get('loop'):
            piv = np.array(s['loop']['pivot']) if not s['closed'] else p.mean(0)
            R0 = np.hypot(*(p - p.mean(0)).T).mean()
            p = _smooth2(p, min(sig, len(p) / 10), s['closed'])
            R1 = np.hypot(*(p - p.mean(0)).T).mean()
            if R1 > 1e-3: p = piv + (p - piv) * (R0 / R1)
        else:
            p = _smooth2(p, sig, s['closed'])
        rm_ = gaussian_filter1d(rm_, max(0.5, calm * 1.2 * w + 0.15 * w), mode='wrap' if s['closed'] else 'nearest') if len(rm_) > 3 else rm_
        prep.append(dict(s=s, p=p, rm=rm_, re=re_))
    # ---- pass 2: glue junction ends back onto the line they meet (no pen breaks) ----
    if fluency > 0:
        allp = [(i, q['p']) for i, q in enumerate(prep)]
        for i, q in enumerate(prep):
            s = q['s']
            if s['closed'] or len(q['p']) < 3: continue
            for e in (0, 1):
                if s['free'][e]: continue
                end = q['p'][0 if e == 0 else -1]
                bd, bp = 1e9, None
                for j, pj in allp:
                    if j == i or len(pj) == 0: continue
                    dd = np.hypot(*(pj - end).T); k = int(dd.argmin())
                    if dd[k] < bd: bd, bp = dd[k], pj[k]
                if bp is None or bd > 1.5 * w or bd < 0.05: continue
                n = len(q['p']); idx = np.arange(n) if e == 0 else (n - 1 - np.arange(n))
                fall = np.clip(1 - idx / (2.0 * w / 1.0), 0, 1)[:, None]     # samples are 1 px apart
                q['p'] = q['p'] + fall * (bp - end) * fluency
    # ---- pass 3: pressure and ink ----
    canvas = np.zeros(shape, np.uint8)
    for q in prep:
        s, p, rm_, re_ = q['s'], q['p'], q['rm'], q['re']
        n = len(p)
        d = np.r_[0, np.cumsum(np.hypot(*np.diff(p, axis=0).T))] if n > 1 else np.zeros(1); L_ = d[-1]
        free = [f and not (fluency > 0.5 and bb) for f, bb in zip(s['free'], s['bridged'])]
        if fluency <= 0.5:
            free = [f or (e in s.get('touch', [])) for e, f in enumerate(free)]
        ex = 0 if (-p[0, 0] + .8 * p[0, 1]) > (-p[-1, 0] + .8 * p[-1, 1]) else 1
        r_old = rm_.copy()
        travel = np.gradient(p, axis=0) if n > 1 else np.zeros((1, 2))
        if ex == 0: travel = -travel
        travel /= (np.linalg.norm(travel, axis=1, keepdims=True) + 1e-9)
        r_new = re_ * (1 + 0.10 * (travel @ heavy))
        if s.get('dot') or L_ < 2.2 * w:
            if not s.get('loop') and L_ > 0.6 * w:
                r_new = re_ * (0.6 + 0.4 * np.sin(np.pi * np.clip(d / max(L_, 1e-6), 0, 1)))
        else:
            for e, f in enumerate(free):
                if not f: continue
                dist = d if e == 0 else L_ - d
                if e == ex:
                    floor = 1 - 0.78 * flicks
                    r_new = r_new * (floor + (1 - floor) * _ease(dist / (2.8 * w)) ** 0.75)
                    r_old = r_old * ((1 - flicks * 0.7) + flicks * 0.7 * _ease(dist / (2.8 * w)))
                else:
                    r_new = r_new * (0.7 + 0.3 * _ease(dist / (1.1 * w)))
        r = ((1 - fluency) * r_old + fluency * r_new) * weight
        for (x, y), rr in zip(p, r):
            cv2.ellipse(canvas, (int(x * 16), int(y * 16)), (max(1, int(rr * sq * 16)), max(1, int(rr / sq * 16))),
                        -angle, 0, 360, 1, -1, cv2.LINE_8, 4)
    return cv2.GaussianBlur(canvas.astype(np.float32), (0, 0), 3 * .35) > .5
