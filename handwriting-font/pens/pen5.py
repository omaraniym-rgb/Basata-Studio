"""Pen model v5: on the line, one steady pen.

Adds to v4:
  - words (pieces of connected ink + their dots) and each word's own baseline
  - each line's true baseline: a robust fit through the word baselines
  - snap: move every word onto its line
  - hooks: the little tick a pen makes when it lands or lifts is trimmed"""
import numpy as np, cv2
from pen3 import _resample, _smooth
from pen4 import analyse, carve, _rot, _length


def _turn_hook(P, w):
    """If the last ~w of a stroke snaps back sharply, return how many points to cut."""
    if len(P) < 6:
        return 0
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(P[::-1], axis=0).T))]   # distance from the end
    i1 = int(np.searchsorted(d, 0.9 * w)); i2 = int(np.searchsorted(d, 2.6 * w))
    if i2 >= len(P) or i1 < 2:
        return 0
    Q = P[::-1]
    a = Q[0] - Q[i1]; b = Q[i1] - Q[i2]
    c = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9)
    return i1 if c < np.cos(np.radians(65)) else 0


def words(mask, A, w):
    n, lab, st, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), connectivity=8)
    big = [i for i in range(1, n) if st[i, 4] >= 6 * w * w]
    def is_mark(i):            # sits over/under a much bigger piece of ink: a dot, dash, shadda or hamza
        x0, x1 = st[i, 0], st[i, 0] + st[i, 2]
        for j in big:
            if j == i or st[j, 4] < 3 * st[i, 4]: continue
            ov = min(x1, st[j, 0] + st[j, 2]) - max(x0, st[j, 0])
            if ov > 0.5 * st[i, 2] and abs((st[i, 1] + st[i, 3] / 2) - (st[j, 1] + st[j, 3] / 2)) < 8 * w:
                return True
        return False
    big = [i for i in big if not is_mark(i)]
    owner = {i: i for i in big}
    for i in range(1, n):                                     # dots ride with the word above/below them
        if i in owner:
            continue
        cx = st[i, 0] + st[i, 2] / 2; cy = st[i, 1] + st[i, 3] / 2
        best, bd = None, 1e18
        for j in big:
            x0, y0, ww, hh = st[j, :4]
            dx = max(0, x0 - cx, cx - (x0 + ww)); dy = max(0, y0 - cy, cy - (y0 + hh))
            dd = dx * 3 + dy
            if dd < bd: best, bd = j, dd
        owner[i] = best if best is not None else i
    for s in A['strokes'] + A['bridges']:
        q = np.round(s['p']).astype(int)
        q[:, 0] = np.clip(q[:, 0], 0, lab.shape[1] - 1); q[:, 1] = np.clip(q[:, 1], 0, lab.shape[0] - 1)
        labs = lab[q[:, 1], q[:, 0]]; labs = labs[labs > 0]
        s['word'] = owner.get(int(np.bincount(labs).argmax()), -1) if len(labs) else -1
    W = {}
    for s in A['strokes']:
        if s['word'] < 0 or s.get('dot'):
            continue
        q, _ = _resample(s['p'], np.zeros(len(s['p'])), False, 2.0)
        if len(q) < 3:
            continue
        t = np.gradient(q, axis=0); ang = np.degrees(np.arctan2(t[:, 1], t[:, 0]))
        flat = (np.abs(ang) < 15) | (np.abs(ang) > 165)
        e = W.setdefault(s['word'], dict(flat=[], all=[]))
        e['flat'].append(q[flat]); e['all'].append(q)
    out = {}
    for k, e in W.items():
        allp = np.vstack(e['all']); flat = np.vstack(e['flat']) if e['flat'] else np.zeros((0, 2))
        x0, x1, y0, y1 = allp[:, 0].min(), allp[:, 0].max(), allp[:, 1].min(), allp[:, 1].max()
        if len(flat) * 2.0 >= 1.5 * w:
            base = float(np.median(flat[:, 1]))
        elif (y1 - y0) > 2.2 * (x1 - x0):                     # a lone alef: it stands on the line
            base = float(y1 - 0.5 * w)
        else:
            base = None
        out[k] = dict(x=float((x0 + x1) / 2), base=base, top=float(y0), bottom=float(y1))
    return out


def fit_lines(A, W, w):
    """Line baseline = straight line through the most horizontal ink (connections sit on it).
    Each word's baseline = its own horizontal ink near that line."""
    for li, L in enumerate(A['lines']):
        pts = []
        for s in A['strokes']:
            if s.get('line') != li or s.get('word', -1) not in W or s.get('dot'): continue
            q, _ = _resample(s['p'], np.zeros(len(s['p'])), False, 2.0)
            if len(q) < 3: continue
            t = np.gradient(q, axis=0); ang = np.degrees(np.arctan2(t[:, 1], t[:, 0]))
            flat = (np.abs(ang) < 15) | (np.abs(ang) > 165)
            for p in q[flat]: pts.append((p[0], p[1], s['word']))
        L['base'] = None
        if len(pts) < 20: continue
        P = np.array([(x, y) for x, y, _ in pts]); wid = np.array([k for _, _, k in pts])
        rng = np.random.default_rng(1); span = np.ptp(P[:, 0]); best, bm, bb = -1, 0.0, 0.0
        for _ in range(2000):
            i, j = rng.integers(0, len(P), 2)
            dx = P[j, 0] - P[i, 0]
            if abs(dx) < span / 4: continue
            m = (P[j, 1] - P[i, 1]) / dx
            if abs(m) > 0.08: continue
            b = P[i, 1] - m * P[i, 0]
            inl = np.abs(P[:, 1] - (m * P[:, 0] + b)) < 0.35 * w
            score = len(set(wid[inl]))*1000 + int(inl.sum())     # agree with as many words as possible
            if score > best: best, bm, bb = score, m, b
        L['base'] = (float(bm), float(bb))
        for k in set(wid):
            sel = wid == k
            near = sel & (np.abs(P[:, 1] - (bm * P[:, 0] + bb)) < 2.2 * w)
            if near.sum() * 2.0 >= 1.2 * w:
                W[k]['base_near'] = float(np.median(P[near, 1]))
                W[k]['x_near'] = float(np.median(P[near, 0]))


def analyse5(mask, w):
    mc = carve(mask, w)
    A = analyse(mc, w)
    for s in A['strokes']:
        s['dot'] = _length(s['p']) < 2.2 * w and s['r'].max() > 0
        for e in (0, 1):
            if not s['free'][e] or s['dot']:
                continue
            P = s['p'] if e == 1 else s['p'][::-1]
            cut = _turn_hook(P, w)
            if cut:
                P = P[:len(P) - cut]; R = (s['r'] if e == 1 else s['r'][::-1])[:len(P)]
                s['p'] = P if e == 1 else P[::-1]; s['r'] = R if e == 1 else R[::-1]
                s.setdefault('hooks', []).append(e)
    W = words(mc, A, w)
    # one line per word: where most of its ink is
    votes = {}
    for st in A['strokes'] + A['bridges']:
        k = st.get('word', -1)
        if k < 0 or st.get('line', -1) < 0: continue
        votes.setdefault(k, {}); votes[k][st['line']] = votes[k].get(st['line'], 0) + _length(st['p']) + 1
    for st in A['strokes'] + A['bridges']:
        k = st.get('word', -1)
        if k in votes: st['line'] = max(votes[k], key=votes[k].get)
    fit_lines(A, W, w)
    for k, v in W.items():
        v['delta'] = 0.0
        li = next((s['line'] for s in A['strokes'] if s.get('word') == k), -1)
        L = A['lines'][li] if li >= 0 else None
        if L and L.get('base') and 'base_near' in v:
            m, b = L['base']; v['delta'] = float(np.clip(m * v['x_near'] + b - v['base_near'], -2.2 * w, 2.2 * w))
    for L in A['lines']:                     # level = undo the fitted slope
        L['angle'] = float(-np.degrees(np.arctan(L['base'][0]))) if L.get('base') else 0.0
    A['words'] = W
    A['mask'] = mc
    return A


def _ease(u):
    u = np.clip(u, 0, 1); return u * u * (3 - 2 * u)


def render5(A, shape, snap=0.0, fluency=0.0, stems=0.0, level=0.0, contrast=1.0, angle=68, flicks=0.0,
            calm=0.0, weight=1.0):
    """fluency 0 = your pressure as written today; 1 = steady pressure, soft landings, clean lift-off flicks."""
    w, rmed = A['w'], A['rmed']
    canvas = np.zeros(shape, np.uint8); sq = np.sqrt(contrast)
    heavy = np.array([-1.0, 1.0]) / np.sqrt(2)              # Arabic hands press harder moving left and down
    items = A['strokes'] + (A['bridges'] if fluency > 0.5 else [])
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
        solid = not s.get('loop') and _length(s['p']) < 3 * w      # a filled-in head is a short fat stroke
        head = (rm > 1.45 * rmed) & solid
        r_even = np.where(head, np.minimum(rm, 1.45 * rmed), rmed)
        if fluency > 0 and s.get('loop'):
            lp = s['loop']; need = rmed * 1.15 + 0.42 * w
            if lp['R'] < need:
                k = 1 + (need / max(lp['R'], 1e-3) - 1) * fluency; piv = np.array(lp['pivot']); P = piv + (P - piv) * k
        p, rm_ = _resample(P, rm, s['closed']); _, re_ = _resample(P, r_even, s['closed'])
        if s.get('loop'):
            piv = np.array(s['loop']['pivot']) if not s['closed'] else p.mean(0)
            R0 = np.hypot(*(p - p.mean(0)).T).mean()
            p = _smooth(p, min(calm * 0.6 * w, len(p) / 14), s['closed'], pin=True)
            R1 = np.hypot(*(p - p.mean(0)).T).mean()
            if R1 > 1e-3: p = piv + (p - piv) * (R0 / R1)
        else:
            p = _smooth(p, calm * 0.6 * w, s['closed'], pin=True)
        rm_ = _smooth(rm_, calm * 1.2 * w + 0.15 * w, s['closed'], pin=False)
        n = len(p)
        d = np.r_[0, np.cumsum(np.hypot(*np.diff(p, axis=0).T))] if n > 1 else np.zeros(1); L_ = d[-1]
        free = [f and not (fluency > 0.5 and bb) for f, bb in zip(s['free'], s['bridged'])]
        ex = 0 if (-p[0, 0] + .8 * p[0, 1]) > (-p[-1, 0] + .8 * p[-1, 1]) else 1
        # as written: measured pressure, old-style taper
        r_old = rm_.copy()
        # fluent: steady pressure along the travel direction, soft landing, long lift-off
        travel = np.gradient(p, axis=0) if n > 1 else np.zeros((1, 2))
        if ex == 0: travel = -travel
        travel /= (np.linalg.norm(travel, axis=1, keepdims=True) + 1e-9)
        r_new = re_ * (1 + 0.10 * (travel @ heavy))
        if s.get('dot') or L_ < 2.2 * w:
            if not s.get('loop') and L_ > 0.6 * w:           # a dash: pressed in the middle
                r_new = re_ * (0.6 + 0.4 * np.sin(np.pi * np.clip(d / max(L_, 1e-6), 0, 1)))
        else:
            ent = 1 - ex
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
