"""Punctuation and the connector, drawn as strokes with the same pen as the letters."""
import numpy as np

def arc(cx, cy, r, a0, a1, n=60, ry=None):
    t = np.radians(np.linspace(a0, a1, n)); ry = r if ry is None else ry
    return np.stack([cx + r * np.cos(t), cy - ry * np.sin(t)], 1)

def line(x0, y0, x1, y1, n=30):
    return np.stack([np.linspace(x0, x1, n), np.linspace(y0, y1, n)], 1)

# units: pen widths, y up from the baseline, x right. alef ≈ 9.2 pen widths.
SHAPES = {
    'period':      dict(cp=0x2E,  dots=[(0.6, 0.6)], w=1.6),
    'colon':       dict(cp=0x3A,  dots=[(0.6, 0.6), (0.6, 3.6)], w=1.6),
    'exclam':      dict(cp=0x21,  strokes=[line(0.7, 8.6, 0.6, 2.8)], dots=[(0.6, 0.6)], w=1.7),
    'hyphen':      dict(cp=0x2D,  strokes=[line(0.3, 3.0, 3.1, 3.0)], w=3.6),
    'arabiccomma': dict(cp=0x60C, strokes=[np.vstack([arc(0.9, 1.6, 0.75, 90, 300), line(1.27, 0.95, 0.9, -0.4, 10)[1:]])], w=2.2, flip=True),
    'arabicsemicolon': dict(cp=0x61B, strokes=[np.vstack([arc(0.9, 1.6, 0.75, 90, 300), line(1.27, 0.95, 0.9, -0.4, 10)[1:]])],
                            dots=[(0.95, 4.4)], w=2.2, flip=True),
    'arabicquestion': dict(cp=0x61F, strokes=[np.vstack([arc(2.0, 6.6, 1.8, 0, 200), line(0.3, 6.0, 2.0, 3.2, 20)[1:]])],
                           dots=[(2.0, 0.6)], w=4.2, flip=True),
    'parenleft':   dict(cp=0x28, strokes=[arc(4.2, 3.6, 3.4, 120, 240, ry=6.4)], w=2.6),
    'parenright':  dict(cp=0x29, strokes=[arc(-1.6, 3.6, 3.4, -60, 60, ry=6.4)], w=2.6),
    'guillemetleft':  dict(cp=0xAB, strokes=[line(1.6, 4.4, 0.4, 3.2), line(0.4, 3.2, 1.6, 2.0), line(3.0, 4.4, 1.8, 3.2), line(1.8, 3.2, 3.0, 2.0)], w=3.4),
    'guillemetright': dict(cp=0xBB, strokes=[line(0.4, 4.4, 1.6, 3.2), line(1.6, 3.2, 0.4, 2.0), line(1.8, 4.4, 3.0, 3.2), line(3.0, 3.2, 1.8, 2.0)], w=3.4),
    'shadda':      dict(cp=0x651, strokes=[np.vstack([line(0.0, 1.5, 0.15, 0.4, 8), arc(0.85, 0.4, 0.7, 180, 360, 30)[1:],
                                                     arc(2.25, 0.4, 0.7, 180, 360, 30)[1:], line(2.95, 0.4, 3.1, 1.6, 8)[1:]])],
                        w=3.1, mark=True),
    'seen.medi':   dict(cp=None, strokes=[line(-0.6, 0.0, 4.0, 0.0, 40)], w=3.4, join=True, letter=True),
    'tatweel':     dict(cp=0x640, strokes=[line(-0.3, 0.0, 2.6, 0.0)], w=2.3, join=True),
}
