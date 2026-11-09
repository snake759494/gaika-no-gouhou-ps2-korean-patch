"""원문 추출: strlist(SCN 0~25, MSG 0~3) + 고정칸(SYS 9/11/14, MAPDATA, GAIKA.BIN) → translation/src/*.tsv"""
import os, sys, glob
sys.path.insert(0, os.path.dirname(__file__))
from sjscan import scan
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def esc(s): return s.replace('\\', '\\\\').replace('\n', '\\n').replace('\t', '\\t')


def unesc(s):
    out = []; i = 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            out.append({'n': '\n', 't': '\t', '\\': '\\'}.get(s[i + 1], s[i + 1])); i += 2
        else:
            out.append(s[i]); i += 1
    return ''.join(out)


def jpish(s):
    k = sum(1 for c in s if '\u3040' <= c <= '\u30ff' or '\u4e00' <= c <= '\u9fff' or '\uff00' <= c <= '\uffef'
            or c in '、。・ー「」『』【】（）？！～…')
    return k >= 1 and k >= len(s.replace(' ', '')) * 0.4


def strlist(arc, idxs):
    rows = []
    for i in idxs:
        d = open(os.path.join(R, 'work/arc/%s/%04d.bin' % (arc, i)), 'rb').read().split(b'\0')
        for k, s in enumerate(d):
            if s: rows.append(('%s%02d' % (arc, i), k, s.decode('cp932')))
    return rows


def fixed(path, tag, loose=False):
    d = open(path, 'rb').read(); rows = []
    for o, x in scan(d, 1):
        try: s = x.decode('cp932')
        except UnicodeDecodeError: continue
        if not jpish(s): continue
        if o > 0 and d[o - 1] != 0 and not loose: continue
        e = o + len(x)
        if e < len(d) and d[e] != 0: continue
        cap = e
        while cap < len(d) and d[cap] == 0: cap += 1
        rows.append((tag, o, s, cap - o - 1))
    return rows


GROUPS = {'scn_tutorial': ('SCN', [0]), 'scn_event': ('SCN', range(1, 13)),
          'scn_brief': ('SCN', range(13, 26)), 'msg': ('MSG', range(4))}

if __name__ == '__main__':
    out = os.path.join(R, 'translation/src'); os.makedirs(out, exist_ok=True)
    for g, (arc, idxs) in GROUPS.items():
        with open(os.path.join(out, g + '.tsv'), 'w', encoding='utf-8', newline='\n') as f:
            for a, k, s in strlist(arc, idxs): f.write('%s\t%d\t%s\n' % (a, k, esc(s)))
    fx = []
    for i in (9, 11, 14): fx += fixed(os.path.join(R, 'work/arc/SYS/%04d.bin' % i), 'SYS%02d' % i, loose=(i == 11))
    for p in sorted(glob.glob(os.path.join(R, 'work/arc/MAPDATA/*.bin'))):
        fx += fixed(p, 'MAP%03d' % int(os.path.basename(p)[:4]))
    g = fixed(os.path.join(R, 'work/ext/GAIKA.BIN'), 'GAIKA')
    fx += [r for r in g if r[1] >= 0x97c00]
    with open(os.path.join(out, 'fixed.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        for a, o, s, cap in fx: f.write('%s\t%x\t%d\t%s\n' % (a, o, cap, esc(s)))
