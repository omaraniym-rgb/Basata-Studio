# Engine v2 scene specs. Subjects sit in the upper ~60%; the lower third stays calm for text.
# set: cyc (seamless studio sweep) | room (wall + floor, window light) | sky (open air, dunes) | open (old horizon look)
# gobo: window light pattern thrown by the key: blinds | window | arch | leaves | slit
J=[]
def j(name, kind, pal, cam=None, light=None, **kw):
    opt=kw.pop('opt',{}); J.append((name, {'kind':kind,'pal':pal,'cam':cam or {},'light':light or {},'opt':opt, **kw}))
TOP=lambda h=12, tz=-1.2, ty=0, fov=30: {'x':0,'y':h,'z':h*.32,'tx':0,'ty':ty,'tz':tz,'fov':fov}     # near top-down
WIN_L={'x':-9,'y':8,'z':5,'tx':0,'ty':0,'tz':-2}       # window light from left
WIN_R={'x':9,'y':8,'z':4,'tx':0,'ty':0,'tz':-2}

# ---- build what lasts ----
j('keystone-bone', 'keystone', 'bone', {'y':2.2,'z':19,'ty':.2}, {'x':-6,'y':7,'z':6}, set='cyc', mat='travertine')
j('keystone-room-sand', 'keystone', 'sand', {'x':-5,'y':2.8,'z':15,'ty':.5,'tz':-.5}, WIN_R, set='room', gobo='window', mat='clay', back=-1.6)
j('ziggurat-sky', 'ziggurat', 'sky', {'x':5,'y':3.4,'z':11,'ty':.2}, {'x':-8,'y':8,'z':4}, set='sky', dunes=True, mat='travertine', opt=dict(topb=True))
j('pillars-room-stone', 'pillars', 'stone', {'x':2.5,'y':2.2,'z':10,'ty':1.0}, WIN_L, set='room', gobo='blinds', mat='plaster', back=-1.8)
j('monument-sky', 'monument', 'sky', {'x':-2,'y':1.6,'z':14,'ty':2.2}, {'x':-9,'y':6,'z':-1}, set='sky', dunes=True, mat='basalt', aCol=0x3a332d, opt=dict(k='a',ball=True))
j('bricks-room-sand', 'bricks', 'sand', {'x':-2.4,'y':2.2,'z':8,'ty':1.3}, {'x':-9,'y':6,'z':4}, set='room', gobo='leaves', mat='clay', aCol=0xd9b796, back=-1.0)
# ---- simplicity / removing ----
j('sculpt-stone', 'sculpt', 'stone', {'x':3.5,'y':4,'z':8,'ty':.6}, {'x':-6,'y':9,'z':5}, set='cyc', mat='plaster', opt=dict(state=.62))
j('sculpt-orange', 'sculpt', 'orange', {'x':-3.5,'y':3.4,'z':8.5,'ty':.6}, {'x':6,'y':9,'z':5}, set='cyc', mat='matte', accCol=0x2b2926, accMat='basalt', opt=dict(state=.48))
j('untangle-bone', 'untangle', 'bone', {'y':5.5,'z':10,'ty':.4}, {'x':-5,'y':9,'z':4}, set='cyc', accMat='gloss', opt=dict(state=.38))
j('untangle-charcoal', 'untangle', 'charcoal', {'y':3.6,'z':9,'ty':.7}, {'x':-6,'y':8,'z':4}, set='cyc', accMat='ceramic', opt=dict(state=.45))
j('sort-stone', 'sort', 'stone', {'x':0,'y':8.5,'z':12.5,'tx':0,'ty':-1.4,'tz':0}, {'x':-6,'y':9,'z':3}, set='cyc', mat='matte')
j('vase-room-bone', 'vase', 'bone', {'x':1.5,'y':2.2,'z':9,'ty':1.7}, WIN_L, set='room', gobo='arch', mat='ceramic', back=-1.8, opt=dict(plinth=1.0))
j('vase-charcoal', 'vase', 'charcoal', {'y':2.0,'z':10,'ty':1.7}, {'x':-5,'y':6,'z':3}, set='cyc', mat='clay', aCol=0xb9a48e, opt=dict(plinth=.8))
j('bowl-clay', 'bowl', 'clay', {'y':5.2,'z':5.2,'ty':-.2,'tz':-.6}, {'x':-4,'y':9,'z':3}, set='cyc', mat='ceramic', aCol=0xf1e6da)
j('shelf-room-stone', 'shelf', 'stone', {'x':-1,'y':1.8,'z':8,'ty':1.5}, WIN_R, set='room', gobo='window', back=-1.6, opt=dict(objs=['vase','ball','book'], y=1.7))
j('frame-room-sand', 'frame', 'sand', {'x':1.2,'y':1.8,'z':8,'ty':1.6}, WIN_L, set='room', gobo='arch', back=-1.4, opt=dict(y=1.0, x=-.3, obj=True), arches=1)
# ---- focus / choice ----
j('lens-bone', 'lens', 'bone', {'y':6.5,'z':6.5,'ty':-.4,'tz':-.4}, {'x':-5,'y':9,'z':4}, set='cyc', mat='matte')
j('spotlight-charcoal', 'spotlight', 'charcoal', {'y':5,'z':10,'ty':-.4,'tz':-1}, {'x':-6,'y':8,'z':4,'i':.5}, set='cyc', mat='matte', fill=.5)
j('target-clay', 'target', 'clay', TOP(11,-1.6,0,30), {'x':-6,'y':9,'z':2}, set='cyc', mat='plaster', aCol=0xf0dfd0)
j('fork-sand', 'fork', 'sand', {'x':0,'y':10,'z':7,'ty':0,'tz':-2.4}, {'x':-6,'y':9,'z':3}, set='cyc', mat='plaster', opt=dict(pick='R', state=.5))
j('compass-bone', 'compass', 'bone', TOP(9,-1.4,0,30), {'x':-6,'y':8,'z':2}, set='cyc', mat='travertine')
j('orbit-charcoal', 'orbit', 'charcoal', {'y':3.2,'z':12,'ty':1.0}, {'x':-6,'y':8,'z':5}, set='cyc', accMat='gloss')
j('tunnel-mist', 'tunnel', 'mist', {'x':.6,'y':1.6,'z':6,'ty':1.0,'tz':-6}, {'x':-6,'y':9,'z':2}, set='cyc', mat='plaster', back=-30)
j('keyhole-stone', 'keyhole', 'stone', {'x':1.8,'y':2.6,'z':7,'ty':1.6}, {'x':-7,'y':6,'z':6}, set='cyc', back=-24, mat='plaster', gobo='window')
# ---- process / momentum ----
j('domino-room-paper', 'domino', 'paper', {'x':-1.2,'y':3.2,'z':12,'tx':0,'ty':.2,'tz':-.4}, WIN_R, set='room', gobo='blinds', mat='matte', back=-1.6, opt=dict(state=.55))
j('domino-stone-top', 'domino', 'stone', {'x':0,'y':17,'z':9,'tx':0,'ty':0,'tz':-2.6,'fov':28}, {'x':-5,'y':9,'z':4}, set='cyc', mat='plaster', opt=dict(state=.7, n=11))
j('cradle-charcoal', 'cradle', 'charcoal', {'x':2,'y':2.2,'z':9,'ty':1.5}, {'x':-6,'y':7,'z':4}, set='cyc', opt=dict(lift=.6))
j('cradle-mist', 'cradle', 'mist', {'x':-3,'y':2.4,'z':8,'ty':1.5}, WIN_R, set='room', gobo='window', back=-1.5, opt=dict(lift=.55))
j('growth-paper', 'growth', 'paper', {'x':1.2,'y':1.2,'z':11,'tx':1.1,'ty':.5}, {'x':-6,'y':6,'z':4}, set='cyc', mat='ceramic', dof={'ap':.0016,'max':.008})
j('stepping-mist', 'stepping', 'mist', {'x':-2,'y':6,'z':7,'ty':0,'tz':-.4}, {'x':-7,'y':6,'z':3}, set='open', fogNear=14, fogFar=40)
j('tightrope-sky', 'tightrope', 'sky', {'y':2.6,'z':11,'ty':2.0}, {'x':-6,'y':8,'z':5}, set='sky', dunes=True)
j('cord-stone', 'cord', 'stone', {'x':1,'y':2.8,'z':14,'ty':.6}, {'x':-5,'y':8,'z':5}, set='cyc', mat='matte')
j('ladder-room-sand', 'ladder', 'sand', {'x':2.6,'y':2.2,'z':8,'ty':2.0}, {'x':-9,'y':10,'z':4}, set='room', gobo='window', back=-1.8)
j('unfold-bone', 'unfold', 'bone', {'x':2,'y':4.4,'z':5,'ty':0,'tz':-.4}, {'x':-5,'y':8,'z':3}, set='cyc', mat='paper', opt=dict(state=.42))
j('plane-mist', 'plane', 'mist', {'y':2.8,'z':8,'ty':1.5}, {'x':-5,'y':8,'z':4}, set='cyc', opt=dict(y=2.5, sc=.75, rx=-.55, ry=.5, rz=.3, k='b'))
# ---- time / patience / calm ----
j('hourglass-room-sand', 'hourglass', 'sand', {'x':2,'y':2.0,'z':10,'ty':2.0}, WIN_L, set='room', gobo='arch', back=-1.8, opt=dict(wood=True, state=.45))
j('hourglass-charcoal', 'hourglass', 'charcoal', {'y':2.2,'z':11,'ty':2.0}, {'x':-6,'y':7,'z':4}, set='cyc', accCol=0xe8743a, opt=dict(state=.62))
j('sundial-sky', 'sundial', 'sky', {'x':2,'y':4.2,'z':7,'ty':-.2}, {'x':-8,'y':4.5,'z':2}, set='sky', dunes=True, mat='travertine')
j('chair-room-bone', 'chair', 'bone', {'x':-2,'y':2.0,'z':9,'ty':1.3}, WIN_R, set='room', gobo='window', back=-1.8, opt=dict(ball=True))
j('chair-room-mist', 'chair', 'mist', {'x':2,'y':2.0,'z':9,'ty':1.3}, WIN_L, set='room', gobo='blinds', back=-1.8, opt=dict(ck='a', ry=.6, x=-.2))
j('dune-sky', 'dune', 'sky', {'x':0,'y':1.4,'z':10,'ty':1.6}, {'x':-9,'y':6,'z':-2}, set='sky', dunes=True, opt=dict(ball=True))
j('beacon-night', 'beacon', 'night', {'x':-2,'y':2.4,'z':13,'ty':2.6}, {'x':-6,'y':6,'z':4,'i':.9}, set='open')
j('ripple-mist', 'ripple', 'mist', {'y':6,'z':9,'ty':-.6,'tz':-1}, {'x':-6,'y':8,'z':3}, set='open', fogNear=16, fogFar=40)
j('ripple-charcoal', 'ripple', 'charcoal', {'y':5,'z':10,'ty':-.4,'tz':-1}, {'x':-6,'y':8,'z':3}, set='open', fogNear=14, fogFar=36, stars=False, opt=dict(wcol=0x2a2724, state=.5))
j('glasscube-orange', 'glasscube', 'orange', {'x':2,'y':2.6,'z':9,'ty':.9}, {'x':-6,'y':8,'z':4}, set='cyc', accCol=0x2b2926, accMat='ceramic', frostCol=0xfbefe4)
j('spiral-paper', 'spiral', 'paper', TOP(9,-1.4,0,32), {'x':-6,'y':9,'z':2}, set='cyc')
j('precarious-bone', 'precarious', 'bone', {'x':1,'y':2.2,'z':9,'ty':1.0}, {'x':-6,'y':8,'z':4}, set='cyc', mat='plaster')
j('pages-room-paper', 'pages', 'paper', {'x':.2,'y':8.5,'z':9,'tx':.2,'ty':-.8,'tz':.3}, WIN_L, set='room', gobo='blinds', back=-3.4, opt=dict(mark=True, state=.42))
DROP={'pages-room-paper'}
NEW=[n for n,_ in J if n not in DROP]

# ---- the original 41, upgraded: same subject, new set, light and material ----
from libspecs import JOBS as OLD
_old=dict(OLD)
UP={ # name: overrides
 'arches-paper':dict(set='room',gobo='blinds',mat='travertine',back=-14), 'arches-orange':dict(set='cyc',mat='plaster',back=-30), 'arches-night':dict(set='open'),
 'arch-sand':dict(set='room',gobo='arch',mat='clay',back=-2.0), 'arch-night-glow':dict(set='cyc',mat='plaster'),
 'columns-stone':dict(set='cyc',mat='travertine',back=-30), 'columns-sand':dict(set='room',gobo='blinds',mat='plaster',back=-16),
 'window-paper':dict(set='open',mat='plaster'), 'window3-white':dict(set='open',mat='plaster'), 'window-orange-obj':dict(set='open',mat='plaster'),
 'door-sand':dict(set='room',gobo='leaves',mat='plaster',back=-2.4), 'door-night-glow':dict(set='cyc',mat='plaster'),
 'stairs-paper':dict(set='room',gobo='window',mat='travertine',back=-6.5), 'stairs-orange':dict(set='cyc',mat='plaster'), 'stairs-stone':dict(set='cyc',mat='plaster'),
 'bridge-paper':dict(set='cyc',mat='travertine'), 'bridge-night':dict(set='open'),
 'monolith-sand':dict(set='sky',dunes=True,mat='basalt'), 'monolith-night':dict(set='open'),
 'bars-paper':dict(set='room',gobo='blinds',mat='plaster',back=-2.0), 'bars-orange':dict(set='cyc',mat='matte'),
 'cairn-stone':dict(set='cyc',mat='travertine'), 'cairn-night':dict(set='cyc'),
 'grid-white':dict(set='cyc',mat='plaster'), 'grid-night':dict(set='cyc'),
 'ring-white':dict(set='room',gobo='window',mat='ceramic',back=-2.2), 'ring-orange':dict(set='cyc',mat='plaster'),
 'balance-paper':dict(set='room',gobo='blinds',mat='plaster',back=-2.4,darkMat='metal'), 'balance-night':dict(set='cyc'),
 'maze-paper':dict(set='cyc',mat='plaster'), 'maze-sand':dict(set='cyc',mat='travertine'),
 'prism-white':dict(set='room',gobo='slit',mat='travertine',back=-2.2),
 'trio-paper':dict(set='room',gobo='window',mat='plaster',back=-2.2),
 'ribbon-white':dict(set='cyc',mat='plaster'), 'ribbon-orange':dict(set='cyc'),
 'slabs-paper':dict(set='room',gobo='blinds',mat='plaster',back=-3.0), 'slabs-sand':dict(set='cyc',mat='travertine'),
 'path-sand':dict(set='sky',dunes=True), 'path-white':dict(set='open'),
 'seed-paper':dict(set='cyc',mat='plaster'), 'seed-night':dict(set='open'),
}
for n,ov in UP.items():
    if n not in _old: continue
    s={**_old[n], **ov}
    if ov.get('gobo'): s['light']={**{'x':-9,'y':8,'z':5,'tx':0,'ty':0,'tz':-2}, **{k:v for k,v in s.get('light',{}).items() if k in ('i',)}}
    s['fovMul']=ov.get('fovMul',1.3)
    J.append((n+'-v2', s))
UPG=[n+'-v2' for n in UP if n in _old]
JOBS2=J

# ---- week 2 remake: orange family (article language: orange wall or sky, white object, one dark accent) ----
_D=dict(J)
def ov(src, name, **kw):
    s={**_D[src]}; o=dict(s.get('opt',{})); o.update(kw.pop('opt',{})); s['opt']=o
    s.update({'pal':'orange','accCol':kw.pop('accCol',0x2b2926),'accMat':kw.pop('accMat','ceramic')}); s.update(kw)
    s.pop('aCol',None); J.append((name,s)); return name
ORANGE=[
 ov('keystone-room-sand','keystone-room-orange', mat='plaster'),
 ov('fork-sand','fork-orange'),
 ov('compass-bone','compass-orange', mat='plaster'),
 ov('lens-bone','lens-orange'),
 ov('tunnel-mist','tunnel-orange'),
 ov('vase-room-bone','vase-room-orange', mat='ceramic'),
 ov('chair-room-mist','chair-room-orange'),
 ov('frame-room-sand','frame-room-orange'),
 ov('ladder-room-sand','ladder-room-orange'),
 ov('cradle-mist','cradle-room-orange'),
 ov('hourglass-room-sand','hourglass-room-orange'),
 ov('unfold-bone','unfold-orange', mat='plaster'),
 ov('precarious-bone','precarious-orange'),
 ov('growth-paper','growth-orange', mat='ceramic'),
 ov('spiral-paper','spiral-orange', opt=dict(k='a')),
 ov('domino-room-paper','domino-room-orange'),
 ov('tightrope-sky','tightrope-orange', set='cyc', dunes=False),
 ov('cord-stone','cord-orange'),
 ov('plane-mist','plane-orange', opt=dict(k='p')),
 ov('monument-sky','monument-orange', set='cyc', dunes=False, mat='plaster', opt=dict(k='a',ball=True)),
 ov('pillars-room-stone','pillars-room-orange'),
 ov('bowl-clay','bowl-orange'),
]
# ---- Journal figures, wide 2:1 (rendered at 1600x800) ----
def art(src, name, cam=None, **kw):
    s={**dict(J)[src]}; s.update(kw)
    if cam: s['cam']={**s['cam'], **cam}
    J.append((name,s)); return name
ART=[
 art('fork-orange','art-fork', cam={'y':12,'z':6,'tz':-2.6,'ty':0}),
 art('keystone-room-orange','art-keystone', cam={'x':-5,'y':2.6,'z':13,'ty':1.4}),
 art('compass-orange','art-compass', cam={'y':8,'z':3.2,'tz':-.6,'ty':0}),
 art('sculpt-orange','art-sculpt', cam={'x':-3.5,'y':3.2,'z':8.5,'ty':1.2}),
 art('frame-room-orange','art-frame', cam={'x':1.2,'y':1.8,'z':7.5,'ty':1.9}),
 art('plane-orange','art-plane', cam={'y':2.6,'z':8,'ty':2.4}),
]
JOBS2=J

# ---- framing fixes for week 2 posts (text corner must stay clear) ----
def _fix(name, cam=None, opt=None):
    for i,(n,s) in enumerate(J):
        if n==name:
            s={**s}
            if cam: s['cam']={**s['cam'],**cam}
            if opt: s['opt']={**s.get('opt',{}),**opt}
            J[i]=(n,s)
_fix('vase-room-orange', cam={'z':12,'ty':2.3})
_fix('keyhole-stone', cam={'ty':2.4})
_fix('ladder-room-orange', opt={'x':1.5})
_fix('fork-orange', cam={'tx':-1.5})
_fix('compass-orange', cam={'y':12.5,'z':4,'tz':-1.4})
JOBS2=J
_fix('vase-room-orange', opt={'x':1.1})
_fix('hourglass-room-orange', cam={'z':14,'ty':2.7})
_fix('ladder-room-orange', opt={'x':1.1})
_fix('compass-orange', cam={'y':13,'z':4.2,'tz':1.7})
JOBS2=J
_fix('vase-room-orange', cam={'z':13,'ty':0.9})
_fix('hourglass-room-orange', cam={'z':15,'ty':0.5})
JOBS2=J

# ---- week 2 v3 (8 Oct night): reused shapes get a new style, never the week 1 look ----
ov('door-sand-v2','door-orange', set='cyc', mat='plaster', gobo=None)
_s={**dict(J)['stairs-paper-v2'], 'pal':'sky', 'set':'sky', 'dunes':True, 'gobo':None, 'mat':'plaster'}; J.append(('stairs-sky',_s))
JOBS2=J
_s={**dict(J)['cradle-mist']}; _s['cam']={**_s['cam'],'z':11.5,'tx':-1.8,'ty':2.2,'y':3.4}; J.append(('cradle-mist-w2',_s))
JOBS2=J
