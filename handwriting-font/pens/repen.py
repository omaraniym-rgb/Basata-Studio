"""Re-ink handwriting with a different pen.

Ink -> centre-line skeleton -> stamp a pen shape along the skeleton.
A round pen stamps a disc; a qalam (broad nib) stamps a thin slanted line,
so stroke thickness changes with direction, like Ruqʿah calligraphy."""
import numpy as np, cv2
from skimage.morphology import skeletonize

UP = 3  # work at 3x for smooth edges


def ink_mask(bgr, k=61, t=0.70, min_area=25):
    g = bgr[:, :, 2].astype(np.float32)  # red channel: blue and black ink are both dark
    bg = cv2.morphologyEx(g, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    bg = cv2.GaussianBlur(bg, (0, 0), k / 4)
    n = np.clip(g / np.maximum(bg, 1), 0, 1.2)
    n = cv2.resize(n, None, fx=UP, fy=UP, interpolation=cv2.INTER_CUBIC)
    n = cv2.GaussianBlur(n, (0, 0), UP * 0.6)
    m = (n < t).astype(np.uint8)
    cnt, lab, st, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
    keep = np.zeros(cnt, bool); keep[1:] = st[1:, 4] >= min_area * UP * UP
    return keep[lab]


def stroke_width(mask):
    dt = cv2.distanceTransform(mask.astype(np.uint8), cv2.DIST_L2, 5)
    sk = skeletonize(mask)
    return 2 * float(np.median(dt[sk])) if sk.any() else 1.0


def _neighbours(sk):
    k = np.ones((3, 3), np.uint8); k[1, 1] = 0
    return cv2.filter2D(sk.astype(np.uint8), -1, k, borderType=cv2.BORDER_CONSTANT)


def prune(sk, max_len):
    """Remove short side-branches (spurs) that skeletons grow at stroke corners."""
    sk = sk.copy()
    H, W = sk.shape
    for _ in range(2):
        nb = _neighbours(sk) * sk
        for y, x in zip(*np.where(nb == 1)):
            path, seen = [(y, x)], {(y, x)}
            py, px = y, x
            while len(path) <= max_len:
                nxt = [(py + a, px + b) for a in (-1, 0, 1) for b in (-1, 0, 1)
                       if (a or b) and 0 <= py + a < H and 0 <= px + b < W
                       and sk[py + a, px + b] and (py + a, px + b) not in seen]
                if len(nxt) != 1:
                    if len(nxt) > 1:          # walked into a junction: this was a spur
                        for q in path: sk[q] = False
                    break
                py, px = nxt[0]; path.append((py, px)); seen.add((py, px))
    return sk


def skeleton(mask, w):
    return prune(skeletonize(mask), int(w * 1.2))


def nib_kernel(width, angle_deg, thin):
    r = int(np.ceil(width / 2)) + thin + 2
    k = np.zeros((2 * r + 1, 2 * r + 1), np.uint8)
    a = np.deg2rad(angle_deg)
    dx, dy = np.cos(a) * width / 2, -np.sin(a) * width / 2
    cv2.line(k, (int(round(r - dx)), int(round(r - dy))), (int(round(r + dx)), int(round(r + dy))), 1, thin)
    return k


def disc(d):
    d = max(1, int(round(d)))
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (d, d))


def repen(mask, pen, w):
    """pen = ('original',) | ('round', diameter) | ('nib', width, angle, thin)"""
    if pen[0] == 'original':
        out = mask.astype(np.uint8)
    else:
        sk = skeleton(mask, w).astype(np.uint8)
        if pen[0] == 'round':
            out = cv2.dilate(sk, disc(pen[1]))
        else:
            _, width, ang, thin = pen
            out = cv2.dilate(sk, nib_kernel(width, ang, thin))
            # dots: a qalam dot is a small rhombus, not a hairline
            cnt, lab, st, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8))
            for i in range(1, cnt):
                x, y, ww, hh, a = st[i]
                if max(ww, hh) < 2.2 * w:
                    cy, cx = y + hh // 2, x + ww // 2
                    dot = np.zeros_like(out); dot[cy, cx] = 1
                    dot = cv2.dilate(dot, nib_kernel(width, ang, thin))
                    dot = cv2.dilate(dot, nib_kernel(width * 0.75, ang - 75, thin))
                    out[y:y+hh, x:x+ww] = 0 if False else out[y:y+hh, x:x+ww]
                    out |= dot
    out = cv2.GaussianBlur(out.astype(np.float32), (0, 0), UP * 0.7)
    return out > 0.5


def render(mask, ink=(30, 32, 45), paper=(244, 240, 232)):
    """Mask at UP scale -> antialiased RGB at 1x."""
    a = cv2.resize(mask.astype(np.float32), (mask.shape[1] // UP, mask.shape[0] // UP), interpolation=cv2.INTER_AREA)
    a = a[..., None]
    return (np.array(paper) * (1 - a) + np.array(ink) * a).astype(np.uint8)
