#!/usr/bin/env python3
"""Build, publish and commit — one command, from inside the repo.

    python3 publish.py "what changed"

Order matters and each step gates the next:
  1. deck/build.py            slides -> deck.html -> PDF -> pptx, with its own gates
  2. web/build_web.py --public rebuilds the public page WITHOUT speaker notes
  3. verify                    refuses to continue if notes or internal phrases are present
  4. git commit + push         GitHub Pages picks it up (CDN caches ~10 min)

Run with --dry to do everything except commit.
"""
import json, os, re, subprocess, sys, shutil

R = os.path.dirname(os.path.abspath(__file__))
SLUG = 'ef5aabaf9c89'                      # unguessable publish path
DECK, WEB = os.path.join(R, 'deck'), os.path.join(R, 'web')
INTERNAL = ('Open cold', 'Slow down', 'Volunteer the', 'terms are not signed',
            'If asked', 'Do not read', 'Do not narrate')

def run(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if p.returncode: sys.exit(f'FAILED: {" ".join(cmd)}\n{p.stdout}\n{p.stderr}')
    return p.stdout

def main():
    msg = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
    dry = '--dry' in sys.argv
    if not msg and not dry: sys.exit('need a commit message: python3 publish.py "what changed"')

    print(run([sys.executable, 'build.py'], cwd=DECK).strip())

    run([sys.executable, os.path.join(WEB, 'build_web.py'), '--public'], cwd=DECK)

    body = open(os.path.join(DECK, 'public.html'), encoding='utf8').read()
    page = ('<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<meta name="robots" content="noindex, nofollow, noarchive, nosnippet, noimageindex">\n'
            '<meta name="referrer" content="no-referrer">\n'
            '<style>*{box-sizing:border-box}html,body{margin:0}img{max-width:100%}'
            '[hidden]{display:none!important}</style>\n' + body + '</html>')
    out = os.path.join(R, SLUG); os.makedirs(out, exist_ok=True)
    open(os.path.join(out, 'index.html'), 'w', encoding='utf8').write(page)

    for f in os.listdir(DECK):
        if f.endswith('.pptx') and 'presenter' not in f:
            for old in os.listdir(out):
                if old.endswith('.pptx'): os.remove(os.path.join(out, old))
            shutil.copy2(os.path.join(DECK, f), os.path.join(out, f))

    leaked = sum(1 for x in json.loads(re.search(r'const META = (\[.*?\]);', page, re.S).group(1))
                 if x.get('notes'))
    phrases = [p for p in INTERNAL if p in page]
    print(f'public page: notes={leaked}  internal phrases={phrases or "none"}')
    if leaked or phrases: sys.exit('REFUSING TO PUBLISH — speaker notes reached the public page')

    if dry: return print('--dry: built and verified, nothing committed')
    run(['git', 'add', '-A'], cwd=R)
    if not run(['git', 'status', '--porcelain'], cwd=R).strip():
        return print('nothing to commit')
    run(['git', '-c', 'user.email=aden.yu@vishwalab.com', '-c', 'user.name=Aden',
         'commit', '-q', '-m', msg], cwd=R)
    run(['git', '-c', 'http.postBuffer=524288000', 'push', '-q', 'origin', 'main'], cwd=R)
    print(f'pushed. live in ~10 min: https://adenprosde2024.github.io/vishwa-deck/{SLUG}/')

if __name__ == '__main__':
    main()
