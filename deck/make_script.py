#!/usr/bin/env python3
"""Render the speaker script for either cut, as plain text.

    python3 make_script.py          -> SCRIPT.md      (4-minute deck)
    python3 make_script.py --vc     -> SCRIPT_VC.md   (longer VC cut)

Two things this has to get right, and both have bitten:
  - appendix labels differ between the cuts (the VC cut promotes two appendix pages
    into the body and renumbers the rest), so "appendix A6" written in notes.py is
    translated to whatever that page is called in the cut being rendered;
  - drafting chatter aimed at the agent, not the speaker, is dropped.
"""
import re, os, sys, types

VC = '--vc' in sys.argv
DROP = ('你说得对',)          # conversation artifacts, not stage directions


def collect(vc):
    argv = sys.argv
    sys.argv = ['b', '--vc'] if vc else ['b']
    try:
        src = open('build.py').read().split('if __name__')[0]
        m = types.ModuleType('b'); m.__file__ = 'build.py'
        exec(compile(src, 'build.py', 'exec'), m.__dict__)
        return m.collect()
    finally:
        sys.argv = argv


def clean(x):
    x = re.sub(r'<[^>]+>', '', x)
    for a, b in (('&#183;', '·'), ('&#8212;', '—'), ('&#8217;', "'"), ('&#8594;', '→'),
                 ('&amp;', '&'), ('&nbsp;', ' '), ('&#8805;', '≥'), ('{{NUM}}', '')):
        x = x.replace(a, b)
    x = re.sub(r'^\s*Appendix\s*·\s*', '', x)
    return re.sub(r'\s+', ' ', x).strip()


def headings(f):
    s = open(f, encoding='utf8').read()
    e = re.search(r'<div class="eyebrow">(.*?)</div>', s, re.S)
    h = re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S)
    return (clean(e.group(1)) if e else ''), (clean(h.group(1)) if h else '')


def main():
    import notes
    sp, sa, slab, _, _ = collect(False)
    pages, apx, labels, _, _ = collect(VC)
    xlate = {}
    if VC:
        for f in sa:
            xlate[slab[f]] = (f'slide {labels[f]}' if f in pages else
                              f'appendix {labels[f]}' if f in apx else f'appendix {slab[f]}')

    def fix(t):
        if not VC:
            return t
        return re.sub(r'appendix (A\d+)',
                      lambda m: xlate.get(m.group(1), m.group(0)), t)

    out = [f"Vishwa — {'VC pitch' if VC else '4-minute pitch'} script",
           f"{len(pages)} body + {len(apx)} appendix. 100 wpm + 2s per slide change.",
           "Indented plain lines are spoken. [ bracketed ] blocks are not spoken and are not timed.", '']
    run = 0
    for f in pages:
        stem = os.path.splitext(os.path.basename(f))[0]
        raw = fix(notes.NOTES_BY_FILE.get(stem, '').strip())
        if not raw:
            out += ['=' * 72, f'SLIDE {labels[f]}   (no script yet)', '']
            continue
        blocks = re.split(r'\n\s*\[', '\n' + raw)
        spoken = blocks[0].strip()
        asides = [b for b in blocks[1:] if not any(d in b for d in DROP)]
        words = len(re.sub(r'^->.*$', '', spoken, flags=re.M).split())
        secs = words / 100 * 60 + 2
        run += secs
        eb, h1 = headings(f)
        out += ['=' * 72,
                f'SLIDE {labels[f]}   {secs:.0f}s   (running {int(run)//60}:{int(run)%60:02d})'
                + (f'   ·   {eb}' if eb else ''),
                f'   {h1}', '']
        out += ['  ' + l.strip() for l in spoken.split('\n')]
        for a in asides:
            title, _, rest = a.partition(']')
            out += ['', f'  [ {title.strip()} ]']
            out += ['    ' + l.strip() for l in rest.strip().split('\n') if l.strip()]
        out += ['']
    out += ['=' * 72, f'TOTAL {int(run)//60}:{int(run)%60:02d}']
    name = 'SCRIPT_VC.md' if VC else 'SCRIPT.md'
    open(name, 'w', encoding='utf8').write('\n'.join(out) + '\n')
    print(f'{name}  {len(pages)} slides  {int(run)//60}:{int(run)%60:02d}')


if __name__ == '__main__':
    main()
