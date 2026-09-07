#!/usr/bin/env python3
"""Build the deck from per-page files.

    python3 build.py            # deck.html -> PDF -> pptx (+ presenter set)
    python3 build.py --no-notes # skip the internal presenter/notes outputs
    python3 build.py --presenter # also inline the ?presenter=1 overlay (internal only)

Pages live one to a file:
    pages/NN-name.html      presented slides, numbered 01..N in filename order
    appendix/aN-name.html   appendix slides, numbered A1..AM in filename order

Numbering is assigned HERE, not written in the files. Each file carries {{NUM}} in its
footer span (and, for appendix files, in its "Appendix {{NUM}}" eyebrow). Reorder or insert
a page by renaming files — page numbers, appendix labels and their eyebrows stay in sync.
That is the whole point: hand-numbering broke three times before this existed.

Cross-references to appendix pages are written as {{REF:a2-business-model}} and resolved to
the label that file ends up with, so moving an appendix page cannot leave a dangling "A5".
"""
import glob, os, re, subprocess, sys, shutil

DATE   = '2026-09-09'
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
MIRROR = '/Users/aden/Documents/Dev/whoIs/vishwa-pitch'
WPM, SLIDE_CHANGE = 100.0, 2.0
SYSFONTS = ('Lucida','Menlo','Helvetica','Arial','Times','Courier')
BANNED   = re.compile(r'\[NEED|CONFIDENTIAL|TODO|TBD|DRAFT\b|placeholder', re.I)
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)


def collect():
    pages = sorted(glob.glob('pages/*.html'))
    apx   = sorted(glob.glob('appendix/*.html'), key=lambda p: int(re.search(r'/a(\d+)', p).group(1)))
    labels = {}
    for i, f in enumerate(pages, start=1): labels[f] = f'{i:02d}'
    for i, f in enumerate(apx,   start=1): labels[f] = f'A{i}'
    ref = {os.path.splitext(os.path.basename(f))[0]: labels[f] for f in apx}
    return pages, apx, labels, ref


def assemble():
    pages, apx, labels, ref = collect()
    out = [open('head.html', encoding='utf8').read()]
    for f in pages + apx:
        s = open(f, encoding='utf8').read().replace('{{NUM}}', labels[f])
        s = re.sub(r'\{\{REF:([a-z0-9\-]+)\}\}',
                   lambda m: ref.get(m.group(1), 'A?'), s)
        out.append(s)
    if '--presenter' in sys.argv and os.path.exists('presenter-inline.html'):
        out.append('\n' + open('presenter-inline.html', encoding='utf8').read())
    out.append('\n</body></html>')
    html = ''.join(out)
    open('deck.html', 'w', encoding='utf8').write(html)
    return html, pages, apx, ref


def render(html):
    pdf = f'Vishwa_Pitch_{DATE}.pdf'
    prof = '/tmp/cr_build'
    shutil.rmtree(prof, ignore_errors=True)
    subprocess.run([CHROME, '--headless', '--disable-gpu', f'--user-data-dir={prof}',
                    '--no-first-run', '--no-default-browser-check', '--no-pdf-header-footer',
                    f'--print-to-pdf={pdf}', f'file://{HERE}/deck.html'], capture_output=True)
    return pdf


def main():
    html, pages, apx, ref = assemble()
    pdf = render(html)
    import pymupdf
    d = pymupdf.open(pdf)

    bad = {sp['font'] for i in range(d.page_count)
           for b in d[i].get_text('dict')['blocks'] for l in b.get('lines', [])
           for sp in l['spans'] if any(x in sp['font'] for x in SYSFONTS)}
    leaks = [(i+1, ln.strip()[:60]) for i in range(d.page_count)
             for ln in d[i].get_text().split('\n') if BANNED.search(ln)]
    dangling = sorted(set(re.findall(r'\{\{REF:[a-z0-9\-]+\}\}|appendix A\?', html)))
    balance = None if html.count('<div') == html.count('</div>') else \
              f"<div>={html.count('<div')} </div>={html.count('</div>')}"

    os.makedirs('slides_png', exist_ok=True)
    for f in glob.glob('slides_png/*.png'): os.remove(f)
    pngs = []
    for i in range(d.page_count):
        p = f'slides_png/slide_{i+1:02d}.png'
        d[i].get_pixmap(matrix=pymupdf.Matrix(2.0, 2.0)).save(p); pngs.append(p)

    from pptx import Presentation
    from pptx.util import Inches
    want_notes = '--no-notes' not in sys.argv
    notes = {}
    if want_notes:
        try:
            sys.path.insert(0, HERE); from notes import SLIDE_NOTES; notes = SLIDE_NOTES
        except Exception as e:
            print('note: notes.py unavailable —', e)

    made = []
    for with_notes, name in ((False, f'Vishwa_Pitch_{DATE}.pptx'),
                             (True,  f'Vishwa_Pitch_{DATE}_presenter.pptx')):
        if with_notes and not notes: continue
        prs = Presentation(); prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
        for i, p in enumerate(pngs, start=1):
            sl = prs.slides.add_slide(prs.slide_layouts[6])
            sl.shapes.add_picture(p, 0, 0, width=prs.slide_width, height=prs.slide_height)
            if with_notes and notes.get(i):
                sl.notes_slide.notes_text_frame.text = notes[i].strip()
        prs.save(name); made.append(name)

    os.makedirs(MIRROR, exist_ok=True)
    for f in [pdf] + made:
        shutil.copy2(f, os.path.join(MIRROR, f))

    print(f'{len(pages)} pages + {len(apx)} appendix = {d.page_count} slides -> {pdf}')
    for m in made: print(f'  {m}')
    print(f'appendix labels : {", ".join(f"{k}={v}" for k, v in ref.items())}')
    print(f'font fallbacks  : {bad or "clean"}')
    print(f'text leaks      : {leaks or "clean"}')
    print(f'dangling refs   : {dangling or "clean"}')
    print(f'div balance     : {balance or "clean"}')
    if bad or leaks or dangling or balance:
        sys.exit('BUILD GATE FAILED')

if __name__ == '__main__':
    main()
