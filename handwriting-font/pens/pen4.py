"""Pen model v4: consistency.

On top of v3 (your ink as centre-line + own width), the strokes are analysed once:
  - blob spurs from redrawn letters are pruned (so overdrawn ink becomes one stroke)
  - strokes are split at sharp corners (Ruqaa corners stay crisp; stems become separable)
  - breaks: free ends that point at each other across a small gap get a bridge
  - stems: straight near-vertical strokes, with the pivot they hang from
  - lines: each line of writing and its tilt
Rendering then applies dials: even weight, mend, straighten stems, level lines,
plus the v3 dials (contrast, flicks, calm, weight, angle)."""
import numpy as np, cv2
from scipy.ndimage import gaussian_filter1d
from skimage.morphology import skeletonize
from repen import prune, UP
from pen2 import trace
from pen3 import _resample, _smooth

RING = [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]
SPUR = (1.35, 0.3)      # a spur shorter than this (x ink radius at its root, + x pen width) is a blob, not a stroke


def _ends(sk):
    def is_end(x, y):
        v = [0 <= y + a < sk.shape[0] and 0 <= x + b < sk.shape[1] and sk[y + a, x + b] for a, b in RING]
        return sum(1 for i in range(8) if v[i] and not v[(i + 1) % 8]) == 1
    return is_end


def _length(P):
    return float(np.hypot(*np.diff(P, axis=0).T).sum()) if len(P) > 1 else 0.0


def clean_skeleton(mask, w, dt):
    """Skeleton with blob spurs removed: a spur shorter than the ink radius it grows from is not a stroke."""
    sk = prune(skeletonize(mask), int(0.6 * w))
    for _ in range(3):
        is_end = _ends(sk); changed = False
        for P, closed in trace(sk):
            if closed or len(P) < 2:
                continue
            P = P.astype(int)
            f0, f1 = is_end(*P[0]), is_end(*P[-1])
            if f0 == f1:
                continue
            j = P[-1] if f0 else P[0]
            if _length(P) < SPUR[0] * dt[j[1], j[0]] + SPUR[1] * w:
                body = P[:-1] if f0 else P[1:]
                sk[body[:, 1], body[:, 0]] = False; changed = True
        if not changed:
            break
    return sk


def split_corners(P, w, closed):
    """Split a stroke where it turns sharply (> 60° over ~1.2 pen widths)."""
    if closed or len(P) < 8:
        return [P]
    Q, _ = _resample(P, np.zeros(len(P)), False)
    k = max(2, int(1.2 * w))
    if len(Q) < 2 * k + 3:
        return [P]
    turn = np.zeros(len(Q))
    for i in range(k, len(Q) - k):
        a, b = Q[i] - Q[i - k], Q[i + k] - Q[i]
        c = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9)
        turn[i] = np.degrees(np.arccos(np.clip(c, -1, 1)))
    cuts, i = [], k
    while i < len(Q) - k:
        if turn[i] > 60 and turn[i] == turn[max(0, i - k):i + k + 1].max():
            cuts.append(i); i += 2 * k
        else:
            i += 1
    if not cuts:
        return [P]
    # map cut points on Q back to nearest P index
    idx = [int(np.argmin(np.hypot(*(P - Q[c]).T))) for c in cuts]
    pieces, s = [], 0
    for c in idx:
        if c - s >= 2:
            pieces.append(P[s:c + 1]); s = c
    pieces.append(P[s:])
    return [q for q in pieces if len(q) >= 2]


def carve(mask, w):
    """Redrawn loops: open every hole whose wall is thicker than a normal stroke."""
    m = mask.copy()
    dt = cv2.distanceTransform(m.astype(np.uint8), cv2.DIST_L2, 5)
    rmed = float(np.median(dt[skeletonize(m)]))
    n, lab, st, _ = cv2.connectedComponentsWithStats((~m).astype(np.uint8), connectivity=4)
    H, W = m.shape
    for i in range(1, n):
        x, y, ww, hh, area = st[i]
        if x == 0 or y == 0 or x + ww >= W or y + hh >= H or area > 6 * w * w:
            continue
        hole = (lab == i).astype(np.uint8)
        x0, y0, x1, y1 = max(0, x - 3 * int(w)), max(0, y - 3 * int(w)), min(W, x + ww + 3 * int(w)), min(H, y + hh + 3 * int(w))
        hz = hole[y0:y1, x0:x1]
        near = cv2.dilate(hz, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(1.2 * w) | 1,) * 2)) & m[y0:y1, x0:x1]
        if not near.any():
            continue
        wall = float(np.percentile(dt[y0:y1, x0:x1][near > 0], 90))   # how thick the ink around the hole gets
        extra = wall - 1.1 * rmed
        if extra <= 0.15 * rmed:
            continue
        k = int(2 * extra * 1.6) | 1
        grow = cv2.dilate(hz, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
        m[y0:y1, x0:x1] &= ~(grow > 0)
    return m


def analyse(mask, w):
    dt = cv2.distanceTransform(mask.astype(np.uint8), cv2.DIST_L2, 5)
    sk = clean_skeleton(mask, w, dt)
    is_end = _ends(sk)
    strokes = []
    for P, closed in trace(sk):
        P = P.astype(int)
        loop = closed or (len(P) > 2 and (P[0] == P[-1]).all())
        f0 = not loop and is_end(*P[0]); f1 = not loop and is_end(*P[-1])
        pieces = [P] if loop else split_corners(P, w, loop)
        for i, q in enumerate(pieces):
            st = dict(p=q.astype(float), r=dt[q[:, 1], q[:, 0]].astype(float), closed=loop and len(pieces) == 1,
                      free=[f0 and i == 0, f1 and i == len(pieces) - 1], bridged=[False, False], loop=None)
            if loop and len(q) > 4:
                c = q.mean(0); attached = not closed      # traced from a junction: grow away from it
                st['loop'] = dict(pivot=(q[0] if attached else c).astype(float).tolist(),
                                  R=float(np.hypot(*(q - c).T).mean()))
            strokes.append(st)
    rmed = float(np.median(np.concatenate([s['r'] for s in strokes])))
    # ---- breaks ----
    ends = []
    for si, s in enumerate(strokes):
        if _length(s['p']) < 3 * w:
            continue
        for e in (0, 1):
            if not s['free'][e]:
                continue
            P = s['p'] if e == 1 else s['p'][::-1]
            k = min(len(P) - 1, max(2, int(1.5 * w)))
            t = P[-1] - P[-1 - k]; t = t / (np.linalg.norm(t) + 1e-9)
            ends.append((si, e, P[-1], t, s['r'][-1 if e == 1 else 0]))
    pairs = []
    for i in range(len(ends)):
        for j in range(i + 1, len(ends)):
            (si, ei, pi, ti, ri), (sj, ej, pj, tj, rj) = ends[i], ends[j]
            if si == sj:
                continue
            g = pj - pi; d = np.linalg.norm(g)
            if d < 1 or d > 1.7 * w:
                continue
            u = g / d
            if np.dot(ti, u) > np.cos(np.radians(40)) and np.dot(tj, -u) > np.cos(np.radians(40)):
                pairs.append((d, i, j))
    used, bridges = set(), []
    for d, i, j in sorted(pairs):
        if i in used or j in used:
            continue
        used |= {i, j}
        (si, ei, pi, ti, ri), (sj, ej, pj, tj, rj) = ends[i], ends[j]
        t = np.linspace(0, 1, max(3, int(d) + 1))[:, None]
        h00, h10, h01, h11 = 2*t**3 - 3*t**2 + 1, t**3 - 2*t**2 + t, -2*t**3 + 3*t**2, t**3 - t**2
        curve = h00 * pi + h10 * ti * d + h01 * pj + h11 * (-tj) * d
        bridges.append(dict(p=curve, r=np.linspace(ri, rj, len(curve)), closed=False, free=[False, False],
                            bridged=[False, False], bridge=True))
        strokes[si]['bridged'][ei] = True; strokes[sj]['bridged'][ej] = True
    # ---- stems ----
    for s in strokes:
        P = s['p']; L = _length(P); s['stem'] = None
        if L < 4 * w or not (s['free'][0] or s['free'][1]):
            continue
        a, b = P[0], P[-1]; ch = b - a
        dev = np.abs(ch[0] * (P[:, 1] - a[1]) - ch[1] * (P[:, 0] - a[0])) / (np.linalg.norm(ch) + 1e-9)
        if dev.max() > 0.12 * L:
            continue
        if ch[1] < 0: ch = -ch                          # point downward
        ang = np.degrees(np.arctan2(-ch[0], ch[1]))     # 0 = upright, + = top leans right
        if abs(ang) > 30:
            continue
        if not s['free'][0]: piv = 0
        elif not s['free'][1]: piv = 1
        else: piv = 0 if P[0][1] > P[-1][1] else 1
        s['stem'] = dict(pivot=piv, angle=ang)
    angs = [s['stem']['angle'] for s in strokes if s['stem']]
    target = float(np.median(angs)) if angs else 0.0
    # ---- lines ----
    rows = mask.any(1).astype(np.uint8)
    bands, y = [], 0
    rows = cv2.dilate(rows[:, None], np.ones((int(1.5 * w) | 1, 1), np.uint8))[:, 0]
    while y < len(rows):
        if rows[y]:
            y0 = y
            while y < len(rows) and rows[y]: y += 1
            if y - y0 > 3 * w: bands.append((y0, y))
        y += 1
    lines = []
    for y0, y1 in bands:
        pts = []
        for st in strokes:
            q, _ = _resample(st['p'], np.zeros(len(st['p'])), False, 2.0)
            if len(q) < 4 or not (y0 <= q[:, 1].mean() < y1): continue
            t = np.gradient(q, axis=0); ang = np.degrees(np.arctan2(t[:, 1], t[:, 0]))
            flat = (np.abs(ang) < 18) | (np.abs(ang) > 162)
            pts.append(q[flat])
        pts = np.vstack(pts) if pts else np.zeros((0, 2))
        if len(pts) < 20:
            continue
        c = np.array([(pts[:, 0].min() + pts[:, 0].max()) / 2, np.median(pts[:, 1])])
        rng = np.random.default_rng(0); span = pts[:, 0].max() - pts[:, 0].min()
        best, ba = 0, 0.0
        for _ in range(1500):
            i, j = rng.integers(0, len(pts), 2)
            dx = pts[j, 0] - pts[i, 0]
            if abs(dx) < span / 3: continue
            ang = np.degrees(np.arctan2(pts[j, 1] - pts[i, 1], dx))
            if abs(ang) > 5: continue
            yl = pts[i, 1] + (pts[:, 0] - pts[i, 0]) * np.tan(np.radians(ang))
            inl = int((np.abs(pts[:, 1] - yl) < 0.3 * w).sum())
            if inl > best: best, ba = inl, ang
        support = best / len(pts)
        if support < 0.35: ba = 0.0                   # not sure: leave the line alone
        ba = -ba                                       # rotate by the opposite of the tilt
        lines.append(dict(cx=float(c[0]), cy=float(c[1]), y0=y0, y1=y1, angle=float(ba)))
    for s in strokes + bridges:
        c = s['p'].mean(0)[1]
        s['line'] = int(np.argmin([abs(c - (l['y0'] + l['y1']) / 2) for l in lines])) if lines else -1
    return dict(strokes=strokes, bridges=bridges, stem_target=target, lines=lines, rmed=rmed, w=w)


def _rot(P, c, deg):
    a = np.radians(deg); R = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
    return (P - c) @ R.T + c


def render(A, shape, even=0.0, mend=0.0, stems=0.0, level=0.0, counters=0.0,
           contrast=1.0, angle=68, taper=0.0, calm=0.0, weight=1.0):
    w, rmed = A['w'], A['rmed']
    canvas = np.zeros(shape, np.uint8)
    sq = np.sqrt(contrast)
    items = A['strokes'] + (A['bridges'] if mend > 0.5 else [])
    for s in items:
        P = s['p'].copy()
        if stems > 0 and s.get('stem'):
            st = s['stem']; piv = P[0] if st['pivot'] == 0 else P[-1]
            # image y is down: positive angle (top leans right) = clockwise; rotate toward target
            P = _rot(P, piv, -(A['stem_target'] - st['angle']) * stems)
        if level > 0 and s['line'] >= 0:
            L = A['lines'][s['line']]
            P = _rot(P, np.array([L['cx'], L['cy']]), L['angle'] * level)
        r = np.minimum(s['r'], 1.6 * rmed)
        if even > 0:
            head = r > 1.45 * rmed                       # solid heads (ف ق م و filled in): keep them, capped
            r = np.where(head, np.minimum(r, (1.6 - 0.15 * even) * rmed),
                         rmed * (np.maximum(r, 1e-3) / rmed) ** (1 - even))
        if counters > 0 and s.get('loop'):
            lp = s['loop']; rr_ = float(np.median(r)) * weight * max(sq, 1 / sq)
            need = rr_ + 0.42 * w                      # loop radius that leaves a clear opening
            if lp['R'] < need:
                k = 1 + (need / max(lp['R'], 1e-3) - 1) * counters
                piv = np.array(lp['pivot']); P = piv + (P - piv) * k
        p, r = _resample(P, r, s['closed'])
        if s.get('loop'):                                   # smooth loops gently and keep their size
            piv = np.array(s['loop']['pivot']) if not s['closed'] else p.mean(0)
            R0 = np.hypot(*(p - p.mean(0)).T).mean()
            p = _smooth(p, min(calm * 0.6 * w, len(p) / 14), s['closed'], pin=True)
            R1 = np.hypot(*(p - p.mean(0)).T).mean()
            if R1 > 1e-3: p = piv + (p - piv) * (R0 / R1)
        else:
            p = _smooth(p, calm * 0.6 * w, s['closed'], pin=True)
        r = _smooth(r, calm * 1.2 * w + 0.15 * w, s['closed'], pin=False)
        free = [f and not (mend > 0.5 and b) for f, b in zip(s['free'], s['bridged'])]
        n = len(p)
        if taper > 0 and n > 3:
            d = np.r_[0, np.cumsum(np.hypot(*np.diff(p, axis=0).T))]; L = d[-1]
            ex = 0 if (-p[0, 0] + .8 * p[0, 1]) > (-p[-1, 0] + .8 * p[-1, 1]) else 1
            for e, f in enumerate(free):
                if not f: continue
                dist = d if e == 0 else L - d
                span = (2.8 if e == ex else 1.2) * w; floor = 1 - taper * (0.7 if e == ex else 0.3)
                u = np.clip(dist / span, 0, 1); r = r * (floor + (1 - floor) * u * u * (3 - 2 * u))
        for (x, y), rr in zip(p, r * weight):
            cv2.ellipse(canvas, (int(x * 16), int(y * 16)), (max(1, int(rr * sq * 16)), max(1, int(rr / sq * 16))),
                        -angle, 0, 360, 1, -1, cv2.LINE_8, 4)
    return cv2.GaussianBlur(canvas.astype(np.float32), (0, 0), UP * .35) > .5
