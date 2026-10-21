"""Pen model v2: smoothed centre-lines + oval nib.

The skeleton is split into strokes, each stroke is smoothed along its length
(removes hand tremor, keeps the shape), then swept with an oval nib.
contrast = long axis / short axis of the oval: 1.0 is a round pen, ~3 is a reed qalam."""
import numpy as np, cv2
from scipy.ndimage import gaussian_filter1d
from repen import ink_mask, stroke_width, skeleton, UP

N8 = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]   # orthogonal first


def trace(sk):
    """Skeleton pixels -> list of ordered strokes [(N,2) float arrays of (x, y)], closed flag."""
    pts = set(zip(*np.nonzero(sk)))
    def nb(p):
        return [(p[0] + a, p[1] + b) for a, b in N8 if (p[0] + a, p[1] + b) in pts]
    def crossings(p):
        ring = [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]
        v = [((p[0] + a, p[1] + b) in pts) for a, b in ring]
        return sum(1 for i in range(8) if not v[i] and v[(i + 1) % 8])
    nodes = {p for p in pts if crossings(p) != 2}
    seen, strokes = set(), []
    def walk(start, first):
        path, prev, cur = [start, first], start, first
        while cur not in nodes:
            seen.add(cur)
            nxt = [r for r in nb(cur) if r != prev and r not in seen and (r in nodes or r not in seen)]
            nxt = [r for r in nxt if r not in path[-3:]]
            if not nxt:
                break
            prev, cur = cur, nxt[0]
            path.append(cur)
            if cur == start:
                break
        return path
    for n in nodes:
        for q in nb(n):
            if q in seen or (q in nodes and q < n):
                continue
            p = walk(n, q)
            strokes.append((np.array([(x, y) for y, x in p], float), False))
    for p0 in pts:                     # closed loops with no junction
        if p0 in seen or p0 in nodes:
            continue
        seen.add(p0)
        q = [r for r in nb(p0) if r not in seen]
        if not q:
            continue
        p = walk(p0, q[0])
        strokes.append((np.array([(x, y) for y, x in p], float), True))
    return strokes


def resample(P, step=1.0, closed=False):
    if closed:
        P = np.vstack([P, P[:1]])
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))]
    if d[-1] < step:
        return P
    t = np.arange(0, d[-1], step)
    return np.stack([np.interp(t, d, P[:, 0]), np.interp(t, d, P[:, 1])], 1)


def smooth(P, sigma, closed=False):
    if len(P) < 4 or sigma <= 0:
        return P
    Q = resample(P, 1.0, closed)
    if closed:
        return np.stack([gaussian_filter1d(Q[:, i], sigma, mode='wrap') for i in (0, 1)], 1)
    S = np.stack([gaussian_filter1d(Q[:, i], sigma, mode='nearest') for i in (0, 1)], 1)
    n = len(Q); k = np.arange(n)
    wa = np.clip(1 - k / (2.5 * sigma), 0, 1)[:, None]          # pin both ends so strokes still meet
    wb = np.clip(1 - (n - 1 - k) / (2.5 * sigma), 0, 1)[:, None]
    S = S + wa * (Q[0] - S[0]) + wb * (Q[-1] - S[-1])
    return S


def oval_kernel(diam, contrast, angle):
    a = diam / 2 * np.sqrt(contrast)       # same ink area at any contrast
    b = diam / 2 / np.sqrt(contrast)
    r = int(np.ceil(a)) + 2
    k = np.zeros((2 * r + 1, 2 * r + 1), np.uint8)
    cv2.ellipse(k, ((r, r), (2 * b, 2 * a), -(90 - angle)), 1, -1)   # long axis at `angle` from horizontal
    return k


def ink(mask, diam, contrast, angle, sigma, w):
    sk = skeleton(mask, w)
    canvas = np.zeros(mask.shape, np.uint8)
    for P, closed in trace(sk):
        S = smooth(P, sigma, closed)
        pts = np.round(S * 16).astype(np.int32).reshape(-1, 1, 2)
        cv2.polylines(canvas, [pts], closed, 1, 1, cv2.LINE_8, shift=4)
    out = cv2.dilate(canvas, oval_kernel(diam, contrast, angle))
    out = cv2.GaussianBlur(out.astype(np.float32), (0, 0), UP * .5) > .5
    return out
