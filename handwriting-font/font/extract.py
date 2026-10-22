"""Stage 1: cut each glyph out of its sheet, straighten its row, find its baseline.

Output per glyph (all in 3x sheet pixels, glyph-local): mask, baseline y, row slope,
stroke width of its sheet."""
import sys, pickle, numpy as np, cv2
sys.path.insert(0, '../pens')
from repen import ink_mask, stroke_width, UP
from glyphmap import G, JOINS

SRC = '../sources/'
M = 60          # crop margin (1x px) so the background estimate is sound


def crop_mask(src_img, box, hard):
    x0, y0, x1, y1 = box
    H, W = src_img.shape[:2]
    X0, Y0 = max(0, x0 - M), max(0, y0 - M)
    X1, Y1 = min(W, x1 + M), min(H, y1 + M)
    m = ink_mask(src_img[Y0:Y1, X0:X1])
    bx0, by0, bx1, by1 = (x0 - X0) * UP, (y0 - Y0) * UP, (x1 - X0) * UP, (y1 - Y0) * UP
    inside = np.zeros_like(m); inside[by0:by1, bx0:bx1] = True
    if hard:
        m = m & inside
        n, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), connectivity=8)
        if n > 2:                                   # specks the box edge sliced off a neighbour
            big = st[1:, 4].max()
            for i in range(1, n):
                if st[i, 4] < 0.06 * big: m = m & (lab != i)
    else:
        n, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), connectivity=8)
        keep = np.zeros(n, bool)
        for i in range(1, n):
            comp = lab == i
            keep[i] = (comp & inside).sum() >= 0.5 * st[i, 4]
        m = keep[lab]
    ys, xs = np.where(m)
    pad = 12 * UP
    cx0, cy0 = max(0, xs.min() - pad), max(0, ys.min() - pad)
    cx1, cy1 = min(m.shape[1], xs.max() + pad), min(m.shape[0], ys.max() + pad)
    m = m[cy0:cy1, cx0:cx1]
    # origin of this glyph-local frame in sheet 1x coords
    return m, (X0 + cx0 / UP, Y0 + cy0 / UP)


def drop_marks(m, where):
    n, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), connectivity=8)
    if n <= 2: return m
    big = int(np.argmax(st[1:, 4])) + 1
    by0, bh = st[big, 1], st[big, 3]
    for i in range(1, n):
        if i == big or st[i, 4] > 0.35 * st[big, 4]: continue
        cy = st[i, 1] + st[i, 3] / 2
        if (where == 'above' and cy < by0 + 0.35 * bh) or (where == 'below' and cy > by0 + 0.6 * bh):
            m = m & (lab != i)
    return m


def marks_of(m, where):
    """The small components above/below the main body."""
    n, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), connectivity=8)
    big = int(np.argmax(st[1:, 4])) + 1
    out = np.zeros_like(m)
    by0, bh = st[big, 1], st[big, 3]
    for i in range(1, n):
        if i == big: continue
        cy = st[i, 1] + st[i, 3] / 2
        if (where == 'above' and cy < by0 + 0.5 * bh) or (where == 'below' and cy > by0 + 0.5 * bh):
            out |= lab == i
    return out


def main_body(m):
    n, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), connectivity=8)
    return lab == (int(np.argmax(st[1:, 4])) + 1)


def join_point(m, side, w):
    """Where the connection runs: the most-inked row near that edge (a flick or a hook
    spreads its ink over many rows, the connecting stroke piles it on one)."""
    n, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), connectivity=8)
    big = st[1:, 4].max()
    b = np.isin(lab, [i for i in range(1, n) if st[i, 4] >= 0.25 * big])     # every real stroke, not the dots
    ys, xs = np.where(b)
    band = (xs <= xs.min() + 3 * w) if side == 'left' else (xs >= xs.max() - 3 * w)
    yb = ys[band]
    bins = np.arange(yb.min(), yb.max() + w, max(2.0, w / 2))
    h, edges = np.histogram(yb, bins=bins)
    k = int(np.argmax(h))
    y = float(np.median(yb[(yb >= edges[k]) & (yb < edges[k + 1] + w / 2)]))
    x = float(xs.min() if side == 'left' else xs.max())
    return x, y


def run(out_path):
    imgs = {}
    raw = {}
    for name, s in G.items():
        if s['src'] not in imgs: imgs[s['src']] = cv2.imread(SRC + s['src'])
        m, org = crop_mask(imgs[s['src']], s['box'], s.get('hard', False))
        if s.get('drop_above'): m = drop_marks(m, 'above')
        if s.get('drop_below'): m = drop_marks(m, 'below')
        if s.get('drop_dots'):
            n_, lab_, st_, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), connectivity=8)
            big = st_[1:, 4].max()
            for i in range(1, n_):
                if st_[i, 4] < 0.12 * big: m = m & (lab_ != i)
        raw[name] = dict(mask=m, org=org)
    # pen width per sheet
    widths = {}
    for name, s in G.items():
        widths.setdefault(s['src'], []).append(stroke_width(raw[name]['mask']))
    W = {k: float(np.median(v)) for k, v in widths.items()}
    # marks borrowed from another glyph (ت dots on ب's end form, ج's dot)
    for name, s in G.items():
        if not s.get('add_mark'): continue
        donor, where, fx = s['add_mark']
        dm = marks_of(raw[donor]['mask'], where)
        ys, xs = np.where(dm)
        dm = dm[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        m = raw[name]['mask']; b = main_body(m)
        bys, bxs = np.where(b)
        w = W[s['src']]
        cx = bxs.min() + fx * (bxs.max() - bxs.min())
        cy = (bys.min() - 1.4 * w - dm.shape[0] / 2) if where == 'above' else (bys.max() + 1.2 * w + dm.shape[0] / 2)
        if where == 'below':
            # under the head: just below the body at that x
            col = np.where(b[:, int(cx)])[0]
            cy = (col.max() if len(col) else bys.max()) + 1.0 * w + dm.shape[0] / 2
        y0 = int(cy - dm.shape[0] / 2); x0 = int(cx - dm.shape[1] / 2)
        padt = max(0, -y0); padb = max(0, y0 + dm.shape[0] - m.shape[0])
        if padt or padb:
            m = np.pad(m, ((padt, padb), (0, 0))); y0 += padt
            raw[name]['org'] = (raw[name]['org'][0], raw[name]['org'][1] - padt / UP)
        m[y0:y0 + dm.shape[0], x0:x0 + dm.shape[1]] |= dm
        raw[name]['mask'] = m
    # baselines: each row's line through its joins (sheet 1x coords)
    rows = {}
    for name, s in G.items():
        if s['form'] in ('mark',): continue
        jl, jr = JOINS[s['form']]
        w = W[s['src']]; org = raw[name]['org']
        for side, on in (('left', jl), ('right', jr)):
            if on:
                x, y = join_point(raw[name]['mask'], side, w)
                rows.setdefault(s['row'], []).append((org[0] + x / UP, org[1] + y / UP))
    lines = {}
    for row, pts in rows.items():
        P = np.array(pts)
        if len(P) >= 2:
            sl = [(P[j, 1] - P[i, 1]) / (P[j, 0] - P[i, 0]) for i in range(len(P)) for j in range(i + 1, len(P)) if abs(P[j, 0] - P[i, 0]) > 20]
            m_ = float(np.clip(np.median(sl), -0.12, 0.12)) if sl else 0.0
        else:
            m_ = 0.0
        b_ = float(np.median(P[:, 1] - m_ * P[:, 0]))
        lines[row] = (m_, b_)
    # digits: they stand on the line
    dig = [n for n in G if G[n]['form'] == 'digit']
    bott = []
    for n in dig:
        m = raw[n]['mask']; ys, xs = np.where(m); org = raw[n]['org']
        bott.append((org[0] + xs.mean() / UP, org[1] + ys.max() / UP))
    P = np.array(bott); lines['dg5'] = (0.0, float(np.median(P[:, 1])))
    out = {}
    for name, s in G.items():
        m = raw[name]['mask']; org = raw[name]['org']; w = W[s['src']]
        if s['form'] == 'mark':
            out[name] = dict(mask=m, base=None, slope=0.0, w=w, src=s['src'], form='mark', side=s['side'])
            continue
        m_, b_ = lines.get(s['row'], (0.0, None))
        if b_ is None:   # a row without joins (shouldn't happen): use the body bottom
            ys, xs = np.where(m); b_ = org[1] + ys.max() / UP
        jl, jr = JOINS[s['form']]
        if jl or jr:     # a joining letter sits exactly where its own connections are
            pts = [join_point(m, side, w) for side, on in (('left', jl), ('right', jr)) if on]
            pts = [(org[0] + x / UP, org[1] + y / UP) for x, y in pts]
            if len(pts) == 2 and abs(pts[1][0] - pts[0][0]) > 8:
                m_ = float(np.clip((pts[1][1] - pts[0][1]) / (pts[1][0] - pts[0][0]), -0.15, 0.15))
            b_ = float(np.mean([y - m_ * x for x, y in pts]))
        # straighten: vertical shear by the row slope around the glyph centre
        xc = m.shape[1] / 2
        A = np.float32([[1, 0, 0], [-m_, 1, m_ * xc]])
        m2 = cv2.warpAffine(m.astype(np.uint8), A, (m.shape[1], m.shape[0]), flags=cv2.INTER_NEAREST) > 0
        xs_sheet = org[0] + xc / UP
        base_sheet = m_ * xs_sheet + b_
        base = (base_sheet - org[1]) * UP
        out[name] = dict(mask=m2, base=float(base), slope=m_, w=w, src=s['src'], form=s['form'])
    pickle.dump(dict(glyphs=out, widths=W, lines=lines), open(out_path, 'wb'))
    print('sheets pen width (3x px):', {k: round(v, 1) for k, v in W.items()})
    print('row slopes:', {k: round(v[0], 3) for k, v in lines.items()})


if __name__ == '__main__':
    run(sys.argv[1] if len(sys.argv) > 1 else 'stage1.pkl')
