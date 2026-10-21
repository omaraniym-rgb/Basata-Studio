# Handwriting → Arabic font
1. Print `template/template.pdf` (3 pages, A4, 100% scale). Write each letter with a dark pen.
2. Photograph/scan each page flat, all 4 black corner squares visible.
3. `pip install fonttools opencv-python-headless potracer pillow numpy`
4. `python3 build_font.py MyHand.ttf "My Hand" page1.jpg page2.jpg page3.jpg`
Regenerate the template with `python3 make_template.py template`.
