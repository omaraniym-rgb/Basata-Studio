# Omar Hand (خط عمر)

A Ruqʿah font made from one person's handwriting.

- `OmarHand.ttf`: install on Mac (double-click) or Windows (right-click > Install)
- `OmarHand.woff2`: for websites (`@font-face`)
- `omar-hand.html`: type tester with the font embedded

## Rebuild

```
pip install fonttools opencv-python-headless scikit-image scipy potracer pillow numpy brotli
python3 extract.py stage1.pkl   # cut every letter from ../sources, straighten, find its baseline
python3 stage2.py               # pen settings + Ruqʿah proportions + standard joins
python3 build_ttf.py "Omar Hand"
```

- Letter map: `glyphmap.py`
- Pen: `stage2.PEN` (the Pen Lab settings)
- Proportions are measured against Aref Ruqaa (OFL), downloaded to the scratch folder at build time (see `proportions.REF`).
