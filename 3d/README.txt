Basata 3D · working files

Engine v2 (current): lib3d2.html + scenes_v1.js (the original 41 shapes) + scenes_v2.js (the 47 new shapes).
Every scene is a recipe in libspecs2.py: shape, background colour, set (studio sweep, room, open air), window light, material, camera.

Render a still:       python3 r3d2.py OUT 1080 1350 1.6 keystone-bone
Render motion frames: python3 anim3d2.py keystone-bone 56
Needs: Python 3 + playwright, Node with three@0.169 (npm i three@0.169.0), and a local server in this folder:
    python3 -m http.server 8765 --bind 127.0.0.1

Backgrounds: paper, white, bone, sand, stone, mist, orange, clay, night, charcoal, sky.
Materials: plaster, travertine, clay, ceramic, gloss, matte, metal, chrome, oak, basalt, frost, glass, paper, velvet.
Window light: blinds, window, arch, leaves, slit.

Naked renders have no text and no mark. Set 2 renders are 1728 x 2160 (4:5).
