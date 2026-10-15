# name -> spec for lib3d.html. Subjects sit in the upper-middle; the lower third stays calm for text.
LOW = {'x': -7, 'y': 3.2, 'z': 2}       # low raking sun, long shadows
HIGH = {'x': -3, 'y': 10, 'z': 6}
J = []
def j(name, kind, pal, cam=None, light=None, **opt):
    J.append((name, {'kind': kind, 'pal': pal, 'cam': cam or {}, 'light': light or {}, 'opt': opt}))

# architecture
j('arches-paper', 'arches', 'paper', {'x': -4.5, 'y': 2.4, 'z': 9, 'tx': 1, 'ty': 1.6, 'tz': -5}, {'x': 7, 'y': 3.2, 'z': 2}, x=1.2)
j('arches-orange', 'arches', 'orange', {'x': -4.5, 'y': 2.4, 'z': 9, 'tx': 1, 'ty': 1.6, 'tz': -5}, {'x': 7, 'y': 3.2, 'z': 2}, accent=0, x=1.2)
j('arches-night', 'arches', 'night', {'x': -4.5, 'y': 2.4, 'z': 9, 'tx': 1, 'ty': 1.6, 'tz': -5}, {'x': -6, 'y': 4, 'z': -8, 'i': 2.2}, x=1.2)
j('arch-glow-paper', 'arch', 'paper', {'y': 2.6, 'z': 14, 'ty': 2.6}, HIGH, glow=True)
j('arch-sand', 'arch', 'sand', {'y': 2.4, 'z': 15, 'ty': 1.6}, LOW)
j('arch-night-glow', 'arch', 'night', {'y': 2.6, 'z': 17, 'ty': 1.4}, None, glow=True)
j('columns-stone', 'columns', 'stone', {'x': 0, 'y': 2.6, 'z': 15, 'ty': 1.8, 'tz': -5}, LOW)
j('columns-sand', 'columns', 'sand', {'x': 0, 'y': 2.6, 'z': 15, 'ty': 1.8, 'tz': -5}, LOW, accent=2)
j('window-paper', 'window', 'paper', {'x': 2, 'y': 3, 'z': 9, 'ty': 2.2, 'tz': -2}, {'x': -2, 'y': 4, 'z': -9, 'i': 3.4})
j('window3-white', 'window', 'white', {'x': 0, 'y': 3, 'z': 10, 'ty': 2.4, 'tz': -2}, {'x': 1, 'y': 4.5, 'z': -9, 'i': 3.4}, cols=3)
j('window-orange-obj', 'window', 'orange', {'x': 2, 'y': 3, 'z': 9, 'ty': 2, 'tz': -2}, {'x': -2, 'y': 4, 'z': -9, 'i': 3.0}, obj=True, ox=1.4)
j('door-glow-white', 'door', 'white', {'y': 2.0, 'z': 12, 'ty': 2.0}, LOW, glow=True)
j('door-sand', 'door', 'sand', {'x': -3, 'y': 1.8, 'z': 11, 'ty': 1.9}, LOW)
j('door-night-glow', 'door', 'night', {'y': 2.0, 'z': 12, 'ty': 2.0}, None, glow=True)
j('stairs-paper', 'stairs', 'paper', {'x': -6, 'y': 2.8, 'z': 6, 'tx': 0, 'ty': 1.0, 'tz': -2.4}, LOW, top=True)
j('stairs-orange', 'stairs', 'orange', {'x': -6, 'y': 2.8, 'z': 6, 'tx': 0, 'ty': 1.0, 'tz': -2.4}, LOW, obj=True)
j('stairs-stone', 'stairs', 'stone', {'x': -6, 'y': 2.8, 'z': 6, 'tx': 0, 'ty': 1.0, 'tz': -2.4}, HIGH)
j('bridge-paper', 'bridge', 'paper', {'y': 2.4, 'z': 15, 'ty': 1.8}, HIGH)
j('bridge-night', 'bridge', 'night', {'y': 2.4, 'z': 15, 'ty': 1.8})
# objects
j('monolith-sand', 'monolith', 'sand', {'y': 1.4, 'z': 13, 'ty': 2.0}, LOW, small=True)
j('monolith-white', 'monolith', 'white', {'y': 1.4, 'z': 13, 'ty': 2.0}, LOW, k='a')
j('monolith-night', 'monolith', 'night', {'y': 1.4, 'z': 15, 'ty': 1.4}, {'x': -6, 'y': 3, 'z': 3, 'i': 2.4}, k='b', x=1.4)
j('bars-paper', 'bars', 'paper', {'y': 2.2, 'z': 13, 'ty': 1.9}, HIGH)
j('bars-night', 'bars', 'night', {'y': 2.2, 'z': 13, 'ty': 1.9})
j('bars-orange', 'bars', 'orange', {'y': 2.2, 'z': 13, 'ty': 1.9}, HIGH, hs=[1.6, 1.6, 1.6, 2.8, 1.6, 1.6], accent=3)
j('cairn-stone', 'cairn', 'stone', {'y': 1.6, 'z': 11, 'ty': 1.7}, HIGH, topb=True)
j('cairn-sand', 'cairn', 'sand', {'y': 1.6, 'z': 11, 'ty': 1.7}, LOW)
j('cairn-night', 'cairn', 'night', {'y': 1.6, 'z': 11, 'ty': 1.7}, None, k='c', topb=True)
j('grid-white', 'grid', 'white', {'y': 7.2, 'z': 9.5, 'ty': 0, 'tz': -1.5, 'fov': 32}, HIGH)
j('grid-missing-paper', 'grid', 'paper', {'y': 7.2, 'z': 9.5, 'ty': 0, 'tz': -1.5, 'fov': 32}, HIGH, missing=True)
j('grid-night', 'grid', 'night', {'y': 7.2, 'z': 9.5, 'ty': -1.2, 'tz': -1.5, 'fov': 32})
j('ring-white', 'ring', 'white', {'y': 1.8, 'z': 12, 'ty': 1.8}, LOW, obj=True)
j('ring-orange', 'ring', 'orange', {'y': 1.8, 'z': 13, 'ty': 1.4}, LOW, rx=.6)
j('balance-paper', 'balance', 'paper', {'y': 1.6, 'z': 11, 'ty': 1.3}, HIGH)
j('balance-night', 'balance', 'night', {'y': 1.6, 'z': 12, 'ty': .5})
j('maze-paper', 'maze', 'paper', {'y': 11, 'z': 8, 'ty': 0, 'tz': 0}, HIGH)
j('maze-sand', 'maze', 'sand', {'y': 11, 'z': 8, 'ty': 0, 'tz': 0}, LOW)
j('prism-white', 'prism', 'white', {'y': 2.4, 'z': 11, 'ty': 1.6}, HIGH)
j('prism-night', 'prism', 'night', {'y': 2.4, 'z': 11, 'ty': 1.6})
j('trio-paper', 'trio', 'paper', {'y': 2.0, 'z': 12, 'ty': 1.6}, HIGH)
j('trio-stone', 'trio', 'stone', {'y': 2.0, 'z': 12, 'ty': 1.6}, LOW)
j('ribbon-white', 'ribbon', 'white', {'y': 1.8, 'z': 11, 'ty': 1.6}, HIGH)
j('ribbon-night', 'ribbon', 'night', {'y': 1.8, 'z': 11, 'ty': 1.6}, None)
j('ribbon-orange', 'ribbon', 'orange', {'y': 1.8, 'z': 11, 'ty': 1.6}, HIGH, k='a')
j('slabs-paper', 'slabs', 'paper', {'y': 2.0, 'z': 13, 'ty': 1.8}, LOW, accent=2)
j('slabs-sand', 'slabs', 'sand', {'y': 2.0, 'z': 13, 'ty': 1.8}, LOW)
j('path-sand', 'path', 'sand', {'y': 1.5, 'z': 8, 'ty': 1.0, 'tz': -10}, LOW, px=1.6)
j('path-white', 'path', 'white', {'y': 1.5, 'z': 8, 'ty': 1.0, 'tz': -10}, LOW, k='b', px=1.6)
j('seed-paper', 'seed', 'paper', {'y': 2.2, 'z': 12, 'ty': 1.4}, LOW)
j('seed-night', 'seed', 'night', {'y': 2.2, 'z': 12, 'ty': 1.4}, {'x': -6, 'y': 3, 'z': 3, 'i': 2.4})
JOBS = J

# batch 2: every scene in the palettes it doesn't have yet
_have = {n for n, _ in J}
_base = {}
for n, s in J:
    _base.setdefault(s['kind'], (s['cam'], s['light'], {k: v for k, v in s['opt'].items() if k not in ('accent',)}))
for kind, (cam, light, opt) in _base.items():
    for pal in ('paper', 'white', 'orange', 'night', 'sand', 'stone'):
        nm = f'{kind}-{pal}'
        if nm in _have or any(x.startswith(kind + '-') and x.endswith('-' + pal) for x in _have): continue
        J.append((nm, {'kind': kind, 'pal': pal, 'cam': cam, 'light': light, 'opt': opt}))
JOBS = J
