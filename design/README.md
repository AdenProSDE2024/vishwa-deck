# Vishwa pitch — body slides, for design

`vishwa-deck-body.html` is the 11 presented slides (正文 only, no appendix), self-contained:
fonts and images are embedded as data URIs, so it opens and renders with no build step and
no network. Regenerate it after any content change with:

    python3 design/export_for_design.py

## What to send back

One `.html` per slide you changed, the way `设计优化改版请求-2.zip` did it. A whole-file
replacement is fine too. Either way the round trip is: you change the look, we re-port it
into `deck/pages/`, because the deck has build rules that a standalone file cannot carry.

## The five rules that broke last time

These are not style preferences. Each one has already cost a rebuild.

1. **The stage is 1440 × 810.** The last export was authored at 1920 × 1080 and every value
   had to be scaled by 0.75. Author at 1440 × 810 and nothing needs touching.

2. **Fonts are Archivo (variable) + IBM Plex Mono, and nothing else.** They are embedded in
   this file. Do not add a Google Fonts link and do not introduce a third family — the deck
   renders to PDF through headless Chrome with no network, so a linked font silently falls
   back and the build's font-fallback gate rejects it. Manrope had to be swapped out of the
   last export for exactly this reason.

3. **Use the CSS variables, not raw hex.** `--bg #0D1117`, `--green #2FBF74`,
   `--green-br #4FD894`, `--green-dk #147E4A`, `--ink #F4F2ED`, `--ink2 #D3D2CC`,
   `--muted #8B95A3`, `--faint #69737F`, `--line #2E3846`, `--panel #171D26`,
   `--amber #E7B45A`. A page with its own black and its own green reads as a different deck
   the moment you page past it.

4. **Never write a page number.** The deck numbers pages at build time from filename order.
   In the real page the footer is `{{NUM}}`; this export has real numbers baked in so it is
   readable, but any page you send back should carry `{{NUM}}`. Same for appendix
   cross-references: write `{{REF:a6-selective-disclosure}}`, never "appendix A6".

5. **No speaker notes in the page.** The last export carried a `data-speaker-notes`
   attribute on the `<section>`. Notes live in `deck/notes.py` and are stripped from the
   public build; a copy inside the markup defeats that. Notes leaked to the public web page
   once already.

## Two more things worth knowing

- **Decorative glyphs fall back.** `▸ ▲ ■ ✓ ←` are not in Archivo and render in Menlo or
  Lucida, which is what made the first deck look broken. Use inline SVG for arrows and
  marks. `→` (`&#8594;`) and `≥` (`&#8805;`) are safe and already in use.
- **Text is being cut, not added.** The standing direction is fewer words, bigger type, no
  dense grey small copy, and a diagram wherever a diagram will do. If a page needs a
  sentence to work, it usually belongs in the spoken script instead.

## Where things stand

Slides 06, 08, 09 and 11 were rewritten most recently. 09 is the ported compute-market page
from the last design round. 01–05, 07 and 10 have not had a design pass.
