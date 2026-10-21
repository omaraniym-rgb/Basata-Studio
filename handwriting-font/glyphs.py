"""Glyph slot definitions shared by the template maker and the font builder."""

# (base codepoint, joining type, first presentation-form codepoint)
# D = dual joining (isol, fina, init, medi), R = right joining (isol, fina), S = non-joining
LETTERS = [
    (0x0621, 'S', 0xFE80), (0x0622, 'R', 0xFE81), (0x0623, 'R', 0xFE83),
    (0x0624, 'R', 0xFE85), (0x0625, 'R', 0xFE87), (0x0626, 'D', 0xFE89),
    (0x0627, 'R', 0xFE8D), (0x0628, 'D', 0xFE8F), (0x0629, 'R', 0xFE93),
    (0x062A, 'D', 0xFE95), (0x062B, 'D', 0xFE99), (0x062C, 'D', 0xFE9D),
    (0x062D, 'D', 0xFEA1), (0x062E, 'D', 0xFEA5), (0x062F, 'R', 0xFEA9),
    (0x0630, 'R', 0xFEAB), (0x0631, 'R', 0xFEAD), (0x0632, 'R', 0xFEAF),
    (0x0633, 'D', 0xFEB1), (0x0634, 'D', 0xFEB5), (0x0635, 'D', 0xFEB9),
    (0x0636, 'D', 0xFEBD), (0x0637, 'D', 0xFEC1), (0x0638, 'D', 0xFEC5),
    (0x0639, 'D', 0xFEC9), (0x063A, 'D', 0xFECD), (0x0641, 'D', 0xFED1),
    (0x0642, 'D', 0xFED5), (0x0643, 'D', 0xFED9), (0x0644, 'D', 0xFEDD),
    (0x0645, 'D', 0xFEE1), (0x0646, 'D', 0xFEE5), (0x0647, 'D', 0xFEE9),
    (0x0648, 'R', 0xFEED), (0x0649, 'R', 0xFEEF), (0x064A, 'D', 0xFEF1),
]
FORM_ORDER = ['isol', 'fina', 'init', 'medi']
SUFFIX = {'isol': '', 'fina': '.fina', 'init': '.init', 'medi': '.medi'}
# (joins on visual LEFT, joins on visual RIGHT)  -- Arabic is right-to-left
JOINS = {'isol': (False, False), 'fina': (False, True),
         'init': (True, False), 'medi': (True, True)}
FORM_HINT = {'isol': 'ALONE', 'fina': 'END  → joins RIGHT',
             'init': 'START  ← joins LEFT', 'medi': 'MIDDLE  ← → joins both'}

PUNCT = [0x060C, 0x061B, 0x061F, 0x002E, 0x0021, 0x003A, 0x002D, 0x0028, 0x0029]


def gname(cp, form='isol'):
    return 'uni%04X' % cp + SUFFIX[form]


def slots():
    out = []
    for cp, kind, pres in LETTERS:
        forms = {'D': FORM_ORDER, 'R': FORM_ORDER[:2], 'S': FORM_ORDER[:1]}[kind]
        for i, f in enumerate(forms):
            out.append(dict(name=gname(cp, f), form=f, ghost=pres + i, cmap=cp if f == 'isol' else None,
                            joins=JOINS[f], label=chr(cp) + '  ' + FORM_HINT[f]))
    out.append(dict(name='lamalef', form='isol', ghost=0xFEFB, cmap=0xFEFB, joins=(False, False),
                    label='لا  LAM-ALEF  ALONE'))
    out.append(dict(name='lamalef.fina', form='fina', ghost=0xFEFC, cmap=0xFEFC, joins=(False, True),
                    label='لا  LAM-ALEF  END → joins RIGHT'))
    out.append(dict(name='uni0640', form='tatweel', ghost=0x0640, cmap=0x0640, joins=(True, True),
                    label='ـ  CONNECTOR  (plain joining stroke)'))
    for i in range(10):
        cp = 0x0660 + i
        out.append(dict(name=gname(cp), form='isol', ghost=cp, cmap=cp, joins=(False, False),
                        label=chr(cp) + '  DIGIT'))
    for cp in PUNCT:
        out.append(dict(name=gname(cp), form='isol', ghost=cp, cmap=cp, joins=(False, False),
                        label=chr(cp) + '  SYMBOL'))
    return out


# --- page geometry (pixels @ 300 dpi, A4 portrait) ---
PAGE_W, PAGE_H = 2480, 3508
COLS, ROWS = 7, 8
CELL_W, CELL_H, LABEL_H = 300, 340, 40
PITCH_X, PITCH_Y = 320, CELL_H + LABEL_H + 0
X0, Y0 = 130, 260
BASE_Y = 211            # baseline, measured from the top of a cell
MARKER = 80
MARKER_CENTERS = [(120, 120), (PAGE_W - 120, 120), (120, PAGE_H - 120), (PAGE_W - 120, PAGE_H - 120)]
PER_PAGE = COLS * ROWS


def cell_rect(i):
    """Pixel rect (x, y, w, h) of slot i *within its page*."""
    c, r = i % COLS, (i // COLS) % ROWS
    return X0 + c * PITCH_X, Y0 + r * PITCH_Y + LABEL_H, CELL_W, CELL_H
