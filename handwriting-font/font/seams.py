"""Seamless joins: every connector ends in the same standard piece of line.

At each joining edge the glyph's own connector is eased, over the last ~0.9 pen widths,
into one standard stroke: centred exactly on the baseline, one thickness for the whole
font, cut flat just past the advance edge. Neighbours overlap inside that standard piece,
so a word reads as one unbroken line on a ruler-straight baseline."""
import numpy as np, cv2

def _runs(col, lo, hi):
    out, y = [], max(0, lo); hi = min(hi, len(col))
    while y < hi:
        if col[y]:
            a = y
            while y < hi and col[y]: y += 1
            out.append((a, y - 1))
        y += 1
    return out

def _ease(u):
    u = np.clip(u, 0, 1); return u * u * (3 - 2 * u)

def seam(img, edge, side, base, T, RW, over=0.38, Z=0.9):
    """side: 'left' (joins toward smaller x) or 'right'. Works in place."""
    H, W = img.shape
    sgn = -1 if side == 'left' else 1
    e = edge + sgn * over * RW                       # where the ink must end
    x_std = edge - sgn * 0.25 * RW                   # standard from here outward
    lo, hi = max(0, int(base - 3 * RW)), min(H, int(base + 3 * RW))
    lab = cv2.connectedComponents(img.astype(np.uint8), connectivity=8)[1]
    # find this glyph's own connector, walking inward from Z
    x_in, run = None, None
    for step in range(0, int(3.0 * RW)):
        x = int(round(edge - sgn * (Z * RW + step)))
        if not (0 <= x < W): break
        rs = [r for r in _runs(img[:, x], lo, hi) if abs((r[0] + r[1]) / 2 - base) < 2.2 * T]
        if rs:
            run = min(rs, key=lambda r: abs((r[0] + r[1]) / 2 - base)); x_in = x; break
    t_std, b_std = base - T / 2, base + T / 2
    if run is None:
        x_in = int(round(edge - sgn * Z * RW)); t0, b0, comp = t_std, b_std, -1
    else:
        t0, b0 = run
        if b0 - t0 > 2.2 * T:                         # the connector merges with a stem or bowl here
            c = min(max(base, t0 + T / 2), b0 - T / 2); t0, b0 = c - T / 2, c + T / 2
        comp = lab[int((run[0] + run[1]) / 2), x_in]
    xs = range(x_in, int(round(e)) + sgn, sgn)
    span = abs(x_std - x_in) or 1
    for x in xs:
        if not (0 <= x < W): continue
        u = _ease(abs(x - x_in) / span)
        top, bot = t0 + (t_std - t0) * u, b0 + (b_std - b0) * u
        ti, bi = int(round(top)), int(round(bot))
        for a, b in _runs(img[:, x], lo, hi):        # trim the old connector to the standard, never a head or stem
            if comp >= 0 and not (lab[a:b + 1, x] == comp).any(): continue      # dots and other strokes stay
            if b < ti - 0.6 * T or a > bi + 0.6 * T: continue                     # clear of the connector band
            if a < ti and ti - a <= 0.6 * T: img[a:ti, x] = False                 # a sliver above: trim
            if b > bi and b - bi <= 0.6 * T: img[bi + 1:b + 1, x] = False         # a sliver below: trim
        img[ti:bi + 1, x] = True
    # nothing may stick out past the edge in the connector band
    band = slice(max(0, int(base - 1.7 * RW)), int(base + 1.7 * RW))
    if side == 'left': img[band, :max(0, int(round(e)))] = False
    else: img[band, int(round(e)) + 1:] = False
    return img
