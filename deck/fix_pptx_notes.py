#!/usr/bin/env python3
"""Repair a pptx that python-pptx wrote with notes slides.

python-pptx adds the notesMaster relationship to ppt/_rels/presentation.xml.rels but
does NOT add the matching <p:notesMasterIdLst> to ppt/presentation.xml. The file is a
valid zip and python-pptx reads it back happily, so nothing local complains — but
PowerPoint and Keynote treat the dangling relationship as a broken package and refuse
to open it, or offer to "repair" it. That is why a deck with speaker notes would not
open while the same deck built with --no-notes would.

CT_Presentation's element order is fixed, so the list has to go immediately after
</p:sldMasterIdLst>.

    python3 fix_pptx_notes.py file.pptx [more.pptx ...]
"""
import re
import shutil
import sys
import zipfile

PRES = 'ppt/presentation.xml'
RELS = 'ppt/_rels/presentation.xml.rels'


def repair(path):
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        if PRES not in names or RELS not in names:
            return 'not a presentation'
        pres = z.read(PRES).decode('utf8')
        rels = z.read(RELS).decode('utf8')
        blobs = {n: z.read(n) for n in names}

    m = re.search(r'<Relationship Id="([^"]+)"[^>]*?/notesMaster"', rels)
    if not m:
        return 'no notesMaster relationship — nothing to fix'
    rid = m.group(1)
    if '<p:notesMasterIdLst' in pres:
        return 'already declared'
    if '</p:sldMasterIdLst>' not in pres:
        return 'no sldMasterIdLst — unexpected shape, left alone'

    pres = pres.replace(
        '</p:sldMasterIdLst>',
        f'</p:sldMasterIdLst><p:notesMasterIdLst><p:notesMasterId r:id="{rid}"/>'
        '</p:notesMasterIdLst>', 1)
    blobs[PRES] = pres.encode('utf8')

    shutil.copy2(path, path + '.bak')
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as out:
        for n in names:
            out.writestr(n, blobs[n])
    return f'declared notesMaster {rid}'


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for p in sys.argv[1:]:
        print(f'{p}: {repair(p)}')


if __name__ == '__main__':
    main()
