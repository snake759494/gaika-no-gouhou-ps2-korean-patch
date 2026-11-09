"""번역 병합: python tools/merge_ko.py translation/ko/event_01.tsv 번역파일.txt
번역파일: 한 줄에 `id<TAB>번역`(줄바꿈은 \\n 으로 표기). 같은 id가 다시 나오면 나중 것 우선."""
import sys, os
tsv, src = sys.argv[1], sys.argv[2]
tr = {}
for line in open(src, encoding='utf-8'):
    line = line.rstrip('\r\n')
    if not line or '\t' not in line: continue
    i, t = line.split('\t', 1)
    tr[i.strip()] = t
rows = []; hit = 0
for line in open(tsv, encoding='utf-8'):
    p = line.rstrip('\n').split('\t')
    while len(p) < 4: p.append('')
    if p[0] in tr: p[2] = tr[p[0]]; hit += 1
    rows.append('\t'.join(p))
open(tsv, 'w', encoding='utf-8', newline='\n').write('\n'.join(rows) + '\n')
miss = [r.split('\t')[0] for r in rows if not r.split('\t')[2]]
print('병합 %d건, 빈 칸 %d건' % (hit, len(miss)), miss[:20])
