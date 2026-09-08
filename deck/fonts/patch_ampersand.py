#!/usr/bin/env python3
"""Point U+0026 at Archivo's alternate ampersand.

Archivo's default ampersand is the flat-topped "Ɛ"-like form. At projection size
it reads as a different letter, so the deck uses `ampersand.alt`, the
conventional form, which ships in the same font but is not reachable through any
OpenType feature in this build — so the cmap is repointed instead.

Re-run this after replacing Archivo-Variable.ttf with a fresh upstream copy:

    python3 fonts/patch_ampersand.py
"""
import sys
from fontTools.ttLib import TTFont

PATH, ALT = 'fonts/Archivo-Variable.ttf', 'ampersand.alt'
f = TTFont(PATH)
if ALT not in f.getGlyphOrder():
    sys.exit(f'{PATH} has no {ALT} glyph — upstream Archivo may have changed')
n = 0
for t in f['cmap'].tables:
    if t.cmap.get(ord('&')) not in (None, ALT):
        t.cmap[ord('&')] = ALT
        n += 1
if not n:
    print('already patched')
else:
    f.save(PATH)
    print(f'{PATH}: & -> {ALT} in {n} cmap subtable(s)')
