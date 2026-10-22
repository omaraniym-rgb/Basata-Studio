"""Your original ink (blue) + current render (dark) on a pen-width grid. Origin = left edge, baseline; y up."""
import sys, pickle, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
from stage2 import R_W
S1 = pickle.load(open('stage1.pkl', 'rb'))['glyphs']
S2 = pickle.load(open('stage2.pkl', 'rb'))['glyphs']
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
fb = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 18)
tiles = []
SC = 0.6
for n in sys.argv[2].split(','):
    g1, g2 = S1[n], S2[n]; s = g2['scale']; k = R_W / g1['w']; pad = int(3 * R_W)
    m = cv2.resize(g1['mask'].astype(np.float32), None, fx=s * k, fy=s * k, interpolation=cv2.INTER_LINEAR) > 0.5
    img = g2['img']; H, W = img.shape
    ov = np.zeros((H, W), bool); hh, ww = min(H - pad, m.shape[0]), min(W - pad, m.shape[1])
    ov[pad:pad + hh, pad:pad + ww] = m[:hh, :ww]
    L, B = g2['left'], g2['base']
    ys, xs = np.where(img | ov)
    x0 = int(min(xs.min(), L) - R_W); x1 = int(max(xs.max(), g2['right']) + R_W)
    y0 = int(min(ys.min(), B - 2 * R_W) - R_W); y1 = int(max(ys.max(), B) + R_W)
    im = np.full((y1 - y0, x1 - x0, 3), 250, np.uint8)
    for gx in np.arange(np.floor((x0 - L) / R_W), np.ceil((x1 - L) / R_W) + 1):
        X = int(L + gx * R_W - x0); im[:, max(0, X):X + 1] = (205, 205, 205) if gx % 2 else (170, 170, 170)
    for gy in np.arange(np.floor((B - y1) / R_W), np.ceil((B - y0) / R_W) + 1):
        Y = int(B - gy * R_W - y0); im[max(0, Y):Y + 1, :] = (205, 205, 205) if gy % 2 else (170, 170, 170)
    im[ov[y0:y1, x0:x1]] = (150, 185, 245)
    im[img[y0:y1, x0:x1]] = (im[img[y0:y1, x0:x1]] * 0.35 + np.array([20, 20, 30]) * 0.65).astype(np.uint8)
    cv2.line(im, (0, int(B - y0)), (im.shape[1], int(B - y0)), (0, 150, 0), 2)
    for X in (L, g2['right']): cv2.line(im, (int(X - x0), 0), (int(X - x0), im.shape[0]), (220, 60, 60), 2)
    pim = Image.fromarray(im).resize((int(im.shape[1] * SC), int(im.shape[0] * SC)), Image.LANCZOS)
    d = ImageDraw.Draw(pim)
    for gx in np.arange(np.floor((x0 - L) / R_W), np.ceil((x1 - L) / R_W) + 1):
        if gx % 2 == 0: d.text(((L + gx * R_W - x0) * SC + 2, 2), str(int(gx)), fill=(200, 0, 0), font=f)
    for gy in np.arange(np.floor((B - y1) / R_W), np.ceil((B - y0) / R_W) + 1):
        if gy % 2 == 0: d.text((2, (B - gy * R_W - y0) * SC - 14), str(int(gy)), fill=(0, 120, 0), font=f)
    d.text((pim.width - 140, pim.height - 22), n, fill=(60, 60, 150), font=fb)
    tiles.append(pim)
Wt = sum(t.width for t in tiles) + 10 * len(tiles); Ht = max(t.height for t in tiles)
out = Image.new('RGB', (Wt, Ht), 'white'); x = 0
for t in tiles[::-1]: out.paste(t, (x, 0)); x += t.width + 10
out.save(sys.argv[1]); print(out.size)
