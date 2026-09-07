# Editing this deck in a fresh session

Point a new session at this file. Everything it needs is here.

## Where things are

    ~/Documents/Dev/vishwa-deck/          the git repo — edit, commit and publish here
      deck/                               slides, build, assets, fonts
      web/                                public web page builder
      publish.py                          build + verify + commit + push, one command
      ef5aabaf9c89/                       the published page (generated, do not hand-edit)
    ~/Documents/Dev/whoIs/vishwa-pitch/   mirror of the deliverables, rewritten each build

The repo is the only source of truth. `~/Documents/ChatGPT/Investor Rel/deck-rewrite/v2/`
is a pre-repo snapshot and must not be edited — two copies is how `notes.py` and
`deck.html` silently diverged during the original build.

The deck is 11 presented slides plus a 9-page appendix, one slide per file:

    pages/01-cover.html      pages/05-govern.html    pages/09-ant.html
    pages/02-market.html     pages/06-privacy.html   pages/10-team.html
    pages/03-category.html   pages/07-loop.html      pages/11-ask.html
    pages/04-mandate.html    pages/08-rings.html
    appendix/a1-appendix-divider.html … a9-security.html

## Edit one page

1. Open the one file. Each is a complete `<section class="slide">`; shared styles live in
   `head.html` and `deck.css`, so a page file rarely needs anything else.
2. `python3 build.py`
3. Look at the rendered page before believing it worked:

       python3 -c "import pymupdf; d=pymupdf.open('Vishwa_Pitch_2026-09-09.pdf'); \
       d[5].get_pixmap(matrix=pymupdf.Matrix(1.3,1.3)).save('/tmp/p6.png')"

   Index is 0-based: `d[5]` is slide 06. **Do this.** A patch that reports success can still
   produce a broken page — that happened repeatedly while building this deck.

## Rules that are not obvious

**Never write a page number.** Footers carry `{{NUM}}`; the build assigns 01..11 and A1..A9
from filename order. Reorder or insert by renaming files.

**Never write `appendix A6`.** Write `{{REF:a6-selective-disclosure}}`. The build resolves it,
so moving an appendix page cannot leave a dangling reference.

**Chrome is verbose.** Always redirect its output or the command looks hung:
`... > /dev/null 2>&1`. And `timeout` does not exist on macOS — do not use it.

**Use balanced-tag extraction, not regex, to replace a block.** Non-greedy `.*?</div>` stops
at the first close tag and silently eats the rest of the slide. This broke two pages here.

## Publish

    cd ~/Documents/Dev/vishwa-deck
    python3 publish.py "raised the privacy headline"     # build, verify, commit, push
    python3 publish.py --dry                             # everything except the commit

`publish.py` builds the deck, rebuilds the public page **without** speaker notes, then
refuses to commit if any note text or internal phrase reached that page. GitHub Pages
caches about 10 minutes — `curl` the URL before telling anyone it is live.

## Version history and rollback

    git log --oneline -- deck/pages/06-privacy.html   # what changed on one page
    git diff HEAD~1 -- deck/pages/06-privacy.html     # what the last change did
    git checkout <sha> -- deck/pages/06-privacy.html  # restore just that page
    python3 publish.py "revert privacy page"

Because each slide is its own file, history and rollback are per-slide. Reverting one page
never touches another.

## What must never be committed or published

`notes.py`, `SCRIPT.md`, `*_presenter.pptx`, `*_speaker-notes.pdf`, `presenter-inline.html`.
They hardcode speaker notes and internal positioning ("terms are not signed", stage
directions). `.gitignore` covers them; the build gates also fail on NEED / CONFIDENTIAL /
TODO / TBD / DRAFT / placeholder appearing on any slide.

`build_web.py --public` strips notes from the web build. Never publish the non-public build.

## Claim discipline

These caveats are load-bearing and appear as small chips on the slides, not as sentences.
Do not remove them:

- 86% privacy figure: **simulated mechanism**, not client data (figures only in appendix A6)
- 41–86.7%: **published MAST/NeurIPS data**, not ours
- SMM: **terms not signed**
- traction figures: **company-reported**, four different bases, not additive
- team stats: **prior operating history**, logos are prior affiliations
- market figures: **market context**, not Vishwa revenue

Do not state what competitors do not do. Say what Vishwa does and let the gap be inferred.

## Chrome does not exit after --print-to-pdf

Chrome 152 writes the PDF in a few seconds and then keeps running (GCM, updater).
`subprocess.run` on it waits forever, which looks exactly like a slow render — it is
not. `build.py` now launches Chrome with Popen, waits for the PDF to stop growing,
then kills it. A full 20-slide build takes about 9 seconds.

If a build is ever killed mid-render, its Chrome child survives and keeps writing the
same PDF path. Two Chromes on one `--print-to-pdf` target corrupt it silently. Clean up
with `pkill -f "print-to-pdf=Vishwa_Pitch"`; renders go to a per-pid temp file and are
moved into place only after a size check.
