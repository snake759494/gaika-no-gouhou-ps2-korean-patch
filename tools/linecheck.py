"""번역 후 줄 수가 원문보다 늘어난 항목 집계(그룹별)"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from text import load_ko, wrap, width
import build
from collections import Counter, defaultdict
ko = load_ko(); R = build.R
stat = Counter(); ex = defaultdict(list)
for nm, n in (('MSG', 4), ('SCN', 26)):
    for j in range(n):
        tag = '%s%02d' % (nm, j)
        for s in open(os.path.join(R, 'work/arc/%s/%04d.bin' % (nm, j)), 'rb').read().split(b'\0'):
            if not s: continue
            jp = s.decode('cp932'); t = ko.get(jp)
            if t is None: continue
            W = build.group_w(tag) or max(max(width(l) for l in jp.split('\n')), 24)
            w = wrap(t, W)
            nj = jp.rstrip('\n').count('\n') + 1; nt = w.rstrip('\n').count('\n') + 1
            if nt > nj:
                stat[tag] += 1; ex[tag].append((nj, nt, jp, w))
print(sorted(stat.items()))
for tag in sorted(ex):
    for nj, nt, jp, w in ex[tag][:2]: print(tag, nj, '->', nt, repr(jp[:60]), '|', repr(w[:80]))
