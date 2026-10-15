"""Engine v2: render an animated scene as frames, composed in-camera (no wide crop). Same call shape as anim3d.render_frames."""
import sys, json, os, time
from playwright.sync_api import sync_playwright
from libspecs2 import JOBS2
D2 = dict(JOBS2)
def render_frames2(name, n, out, w=720, h=900, dpr=1.0):
    os.makedirs(out, exist_ok=True)
    if len([f for f in os.listdir(out) if f.endswith('.png')]) >= n: return
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--no-proxy-server'])
        spec = {**D2[name], 'w': w, 'h': h, 'dpr': dpr, 'anim': True, 't': 0}
        pg = b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=dpr); pg.set_default_timeout(600000)
        pg.add_init_script('window.SPEC=' + json.dumps(spec))
        pg.goto('http://127.0.0.1:8765/lib3d2.html'); pg.wait_for_function('window.DONE===true', timeout=580000)
        for i in range(n):
            f = f'{out}/{i:03d}.png'
            if os.path.exists(f): continue
            pg.evaluate(f'window.frame({i/(n-1)})')
            pg.screenshot(path=f, clip={'x': 0, 'y': 0, 'width': w, 'height': h})
        b.close()
if __name__ == '__main__':
    t = time.time(); render_frames2(sys.argv[1], int(sys.argv[2]), f'lib/anim/{sys.argv[1]}'); print('secs', time.time() - t)
