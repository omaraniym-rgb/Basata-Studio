"""Pen model v3: start from YOUR ink, only add.

The ink is stored as its medial axis: a centre-line plus the ink's own
half-width at every point. Re-stamping round discs of those widths rebuilds
the original exactly. Each dial then adds one calligraphic quality:
  contrast  discs become ovals at the nib angle (same ink area)
  taper     free stroke ends thin out into a flick, mostly on the exit
  calm      light smoothing of the centre-line and of the width (loops kept)
  weight    overall ink weight"""
import numpy as np, cv2
from scipy.ndimage import gaussian_filter1d
from skimage.morphology import skeletonize
from repen import prune, UP
from pen2 import trace

RING = [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]


def medial(mask, w):
    """-> list of strokes: dict(p=(N,2) xy, r=(N,) half-width, closed, free=(start_free, end_free))"""
    dt = cv2.distanceTransform(mask.astype(np.uint8), cv2.DIST_L2, 5)
    sk = prune(skeletonize(mask), int(0.6 * w))
    on = lambda y, x: 0 <= y < sk.shape[0] and 0 <= x < sk.shape[1] and sk[y, x]
    def is_end(x, y):
        v = [on(y + a, x + b) for a, b in RING]
        return sum(1 for i in range(8) if v[i] and not v[(i + 1) % 8]) == 1
    out = []
    for P, closed in trace(sk):
        if len(P) < 1:
            continue
        P = P.astype(int)
        r = dt[P[:, 1], P[:, 0]]
        loop = closed or (len(P) > 2 and (P[0] == P[-1]).all())
        out.append(dict(p=P.astype(float), r=r.astype(float), closed=loop,
                        free=(not loop and is_end(*P[0]), not loop and is_end(*P[-1]))))
    return out


def _resample(p, r, closed, step=1.0):
    if closed and len(p) > 2:
        p = np.vstack([p, p[:1]]); r = np.r_[r, r[:1]]
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(p, axis=0).T))]
    if len(p) < 2 or d[-1] < step:
        return p, r
    t = np.arange(0, d[-1] + 1e-6, step)
    return (np.stack([np.interp(t, d, p[:, 0]), np.interp(t, d, p[:, 1])], 1), np.interp(t, d, r))


def _smooth(a, sigma, closed, pin):
    if sigma <= 0 or len(a) < 5:
        return a
    s = min(sigma, len(a) / 6)                       # never smooth a short stroke or small loop away
    b = gaussian_filter1d(a, s, axis=0, mode='wrap' if closed else 'nearest')
    if pin and not closed:
        n = len(a); k = np.arange(n)
        wa = np.clip(1 - k / (2.5 * s), 0, 1); wb = np.clip(1 - (n - 1 - k) / (2.5 * s), 0, 1)
        if a.ndim == 2: wa, wb = wa[:, None], wb[:, None]
        b = b + wa * (a[0] - b[0]) + wb * (a[-1] - b[-1])
    return b


def exit_index(p):
    """Which end the pen most likely left from: Arabic moves right-to-left and down."""
    s0, s1 = -p[0, 0] + 0.8 * p[0, 1], -p[-1, 0] + 0.8 * p[-1, 1]
    return 0 if s0 > s1 else 1


def render(strokes, w, shape, contrast=1.0, angle=68, taper=0.0, calm=0.0, weight=1.0):
    canvas = np.zeros(shape, np.uint8)
    rmed = np.median(np.concatenate([s['r'] for s in strokes])) if strokes else w / 2
    sq = np.sqrt(contrast)
    for s in strokes:
        p, r = _resample(s['p'], np.minimum(s['r'], 1.6 * rmed), s['closed'])
        p = _smooth(p, calm * 0.6 * w, s['closed'], pin=True)
        r = _smooth(r, calm * 1.2 * w + 0.15 * w, s['closed'], pin=False)
        n = len(p)
        if taper > 0 and n > 3:
            d = np.r_[0, np.cumsum(np.hypot(*np.diff(p, axis=0).T))]
            L = d[-1]
            ex = exit_index(p)
            for end, free in enumerate(s['free']):
                if not free:
                    continue
                dist = d if end == 0 else L - d
                span = (2.8 if end == ex else 1.2) * w
                floor = 1 - taper * (0.7 if end == ex else 0.3)
                u = np.clip(dist / span, 0, 1)
                r = r * (floor + (1 - floor) * (u * u * (3 - 2 * u)))
        A, B = r * weight * sq, r * weight / sq
        for (x, y), a, b in zip(p, A, B):
            cv2.ellipse(canvas, (int(x * 16), int(y * 16)), (max(1, int(a * 16)), max(1, int(b * 16))),
                        -angle, 0, 360, 1, -1, cv2.LINE_8, 4)
    return cv2.GaussianBlur(canvas.astype(np.float32), (0, 0), UP * .35) > .5
