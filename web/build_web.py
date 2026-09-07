import re, base64, json, sys, os

# Run this from deck/ — deck.html, deck.css, fonts/ and assets/ are resolved
# relative to the cwd. shell.html is the one file that lives beside the script.
HERE = os.path.dirname(os.path.abspath(__file__))
PUBLIC = '--public' in sys.argv   # public build ships no speaker notes
sys.path.insert(0, '.')
try:
    from notes import SLIDE_NOTES, BUDGET
except ModuleNotFoundError:
    # public builds strip notes anyway; notes.py is internal and not shipped here
    if not PUBLIC: raise
    SLIDE_NOTES, BUDGET = {}, {}

def datauri(path, mime):
    return f"data:{mime};base64," + base64.b64encode(open(path,'rb').read()).decode()

html = open('deck.html', encoding='utf8').read()
css  = open('deck.css',  encoding='utf8').read()

# ---- fonts + images -> data URIs (the artifact CSP blocks every external asset) ----
for f, name in [('Archivo-Variable.ttf','Archivo-Variable.ttf'),
                ('IBMPlexMono-Regular.ttf','IBMPlexMono-Regular.ttf'),
                ('IBMPlexMono-SemiBold.ttf','IBMPlexMono-SemiBold.ttf'),
                ('IBMPlexMono-Bold.ttf','IBMPlexMono-Bold.ttf')]:
    css = css.replace(f"url('fonts/{name}')", f"url('{datauri('fonts/'+f,'font/ttf')}')")

inline = re.search(r'<style>(.*?)</style>', html, re.S).group(1)
inline = re.sub(r'@page\{[^}]*\}', '', inline)

body = html.split('</style>',1)[1].split('</body>')[0]
for m in sorted(set(re.findall(r'src="(assets/[^"]+)"', body))):
    body = body.replace(f'src="{m}"', f'src="{datauri(m,"image/png")}"')

# ---- deck CSS: strip page/print rules, keep the design tokens ----
css = css.replace('html,body{background:#000;}', '')
css = re.sub(r"body\{font-family:'Archivo'[^}]*\}", '', css)
css = css.replace('page-break-after:always;break-after:page;', '')

sections = re.findall(r'<section class="slide[^"]*"[^>]*>.*?</section>', body, re.S)
labels = [ (re.findall(r'<span>(0\d|1\d|A\d{1,2})</span></div>\s*</section>', s) or ['?'])[-1] for s in sections ]
TITLES = {1:'Cover',2:'The intelligent economy',3:'Category',4:'Govern',5:'Protect',6:'Improve',
          7:'Compute expansion',8:'Production proof',9:'Team',10:'The ask'}
notes = {i: re.sub(r'\n{3,}','\n\n', t.strip()) for i,t in SLIDE_NOTES.items()}
meta = [{'label': labels[i], 'title': TITLES.get(i+1, 'Appendix ' + labels[i]),
         'notes': '' if PUBLIC else notes.get(i+1,''),
         'budget': 0 if PUBLIC else BUDGET.get(i+1,0)} for i in range(len(sections))]

open('artifact.html','w',encoding='utf8').write(
    open(os.path.join(HERE,'shell.html'),encoding='utf8').read()
      .replace('/*DECKCSS*/', css)
      .replace('/*INLINECSS*/', inline)
      .replace('<!--SLIDES-->', '\n'.join(f'<div class="vw-frame" data-i="{i}">{s}</div>'
                                          for i,s in enumerate(sections)))
      .replace('/*META*/', json.dumps(meta, ensure_ascii=False))
      .replace('/*PUBLIC*/', 'true' if PUBLIC else 'false'))
out = 'public.html' if PUBLIC else 'artifact.html'
os.rename('artifact.html', out)
print(f'{len(sections)} slides -> {out} ({os.path.getsize(out)//1024}KB) '
      f'notes={"STRIPPED" if PUBLIC else "included"}')
