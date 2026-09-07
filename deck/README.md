# Vishwa — seed pitch deck

Source for the 4-minute pitch. Plug and Play, New York, 9 September 2026.

    python3 build.py

Produces `deck.html`, `Vishwa_Pitch_<date>.pdf` and a `.pptx` (one full-bleed image per
slide, so Google Slides and PowerPoint cannot substitute fonts or reflow the layout).

## Layout

    head.html            <head>, design tokens, shared component CSS
    deck.css             typography and colour tokens
    pages/NN-name.html   presented slides, numbered 01..N in filename order
    appendix/aN-name.html appendix slides, numbered A1..AM in filename order
    assets/  fonts/      images, and Archivo + IBM Plex Mono (both OFL)

**One page per file, and page numbers are assigned by the build, not written in the files.**
Each file carries `{{NUM}}` in its footer; appendix files also carry it in their
`Appendix {{NUM}}` eyebrow. Reorder or insert a page by renaming files and the numbers,
appendix labels and eyebrows all stay in sync.

Reference an appendix page as `{{REF:a6-selective-disclosure}}` rather than writing `A6`.
The build resolves it to whatever label that file ends up with, so moving a page cannot
leave a dangling reference.

## Build gates

The build refuses to finish on any of:

- a glyph that fell back to a system font (Archivo appears unnamed/Type3 — that is normal)
- NEED / CONFIDENTIAL / TODO / TBD / DRAFT / placeholder anywhere on a slide
- an unresolved `{{REF:...}}`
- unbalanced `<div>` tags

## Editing one page at a time

Each page is self-contained: edit `pages/06-privacy.html`, run `python3 build.py`, done.
Nothing else needs to change.

## Not in this repo

Speaker notes and the presenter builds are internal — they contain stage directions and
internal positioning. They stay out of version control by `.gitignore`.
