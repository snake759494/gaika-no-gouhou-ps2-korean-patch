"""원문 중 번역 누락 목록 → work/missing.tsv"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from text import load_ko
from extract import unesc, jpish
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ko = load_ko(); miss = []
for g in ('msg', 'scn_tutorial', 'scn_event', 'scn_brief', 'fixed'):
    for line in open(os.path.join(R, 'translation/src/%s.tsv' % g), encoding='utf-8'):
        p = line.rstrip('\n').split('\t'); s = unesc(p[-1])
        if jpish(s) and s not in ko: miss.append((g, p[0], p[1], p[-1]))
with open(os.path.join(R, 'work/missing.tsv'), 'w', encoding='utf-8') as f:
    for m in miss: f.write('\t'.join(m) + '\n')
from collections import Counter
print(len(miss), Counter((m[0], m[1][:3]) for m in miss))
