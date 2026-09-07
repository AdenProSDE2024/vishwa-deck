#!/usr/bin/env python3
"""Export the 11 presented slides as one self-contained HTML for a design session.

Fonts and images are embedded as data URIs, so the file renders identically with
no build step and no network. Appendix pages are excluded — this is 正文 only.

    python3 design/export_for_design.py
"""
import base64, glob, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.join(os.path.dirname(HERE), 'deck')
OUT  = os.path.join(HERE, 'vishwa-deck-body.html')


def datauri(path, mime):
    with open(path, 'rb') as f:
        return f'data:{mime};base64,' + base64.b64encode(f.read()).decode()


def main():
    os.chdir(DECK)
    css = open('deck.css', encoding='utf8').read()
    for name in os.listdir('fonts'):
        if name.endswith('.ttf'):
            css = css.replace(f"url('fonts/{name}')", f"url('{datauri('fonts/'+name,'font/ttf')}')")

    head = open('head.html', encoding='utf8').read()
    inline = re.search(r'<style>(.*?)</style>', head, re.S)
    inline = inline.group(1) if inline else ''

    pages = sorted(glob.glob('pages/*.html'))
    body, missing = [], []
    for i, f in enumerate(pages, start=1):
        s = open(f, encoding='utf8').read()
        s = s.replace('{{NUM}}', f'{i:02d}')
        for ref in re.findall(r'\{\{REF:([a-z0-9-]+)\}\}', s):
            missing.append((f, ref))
            s = s.replace(f'{{{{REF:{ref}}}}}', 'A?')
        for img in sorted(set(re.findall(r'src="(assets/[^"]+)"', s))):
            s = s.replace(f'src="{img}"', f'src="{datauri(img,"image/png")}"')
        body.append(f'<!-- ===== {os.path.basename(f)} ===== -->\n{s}')

    open(OUT, 'w', encoding='utf8').write(
        '<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8">\n'
        f'<title>Vishwa pitch — body slides ({len(pages)})</title>\n'
        '<style>\n' + css + '\n' + inline + '\n'
        'body{background:#000;display:flex;flex-direction:column;align-items:center;gap:26px;padding:26px 0}\n'
        '</style></head>\n<body>\n' + '\n'.join(body) + '\n</body></html>\n')

    print(f'{len(pages)} slides -> {os.path.relpath(OUT)}  ({os.path.getsize(OUT)/1e6:.1f} MB)')
    for f, ref in missing:
        print(f'  note: {f} points at appendix {ref}, which is not in this export')


if __name__ == '__main__':
    sys.exit(main())
