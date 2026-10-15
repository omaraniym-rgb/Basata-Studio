"""Render engine-v2 scenes straight to final 4:5 frames. usage: python3 r3d2.py OUTDIR W H DPR name... (specs from libspecs2)"""
import json, sys, os, time
from playwright.sync_api import sync_playwright
def run(jobs, out, w=540, h=675, dpr=1):
    os.makedirs(out, exist_ok=True)
    with sync_playwright() as p:
        b=p.chromium.launch(args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--no-proxy-server'])
        for name,spec in jobs:
            path=f'{out}/{name}.png'
            if os.path.exists(path) and '-f' not in sys.argv: continue
            t=time.time(); spec={**spec,'w':w,'h':h,'dpr':dpr}
            pg=b.new_page(viewport={'width':w,'height':h},device_scale_factor=dpr); pg.set_default_timeout(600000)
            errs=[]; pg.on('console', lambda m: errs.append(m.text) if m.type=='error' else None); pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.add_init_script('window.SPEC='+json.dumps(spec))
            pg.goto('http://127.0.0.1:8765/lib3d2.html')
            try: pg.wait_for_function('window.DONE===true',timeout=580000)
            except Exception as e: print('FAIL',name,errs[:3],flush=True); pg.close(); continue
            pg.screenshot(path=path,clip={'x':0,'y':0,'width':w,'height':h},timeout=600000)
            pg.close(); print('ok',name,round(time.time()-t,1),errs[:2],flush=True)
        b.close()
if __name__=='__main__':
    from libspecs2 import JOBS2
    out,w,h,dpr=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),float(sys.argv[4]); names=[a for a in sys.argv[5:] if a!='-f']
    D=dict(JOBS2); run([(n,D[n]) for n in (names or D)], out, w, h, dpr)
