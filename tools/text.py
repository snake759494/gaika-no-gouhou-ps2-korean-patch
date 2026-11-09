"""번역 로드·인코딩·줄바꿈."""
import os, sys, glob, re
sys.path.insert(0, os.path.dirname(__file__))
from extract import unesc, esc
from kfont import charmap
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CM = charmap()
# 반각 → 전각 대체(게임 폰트에 반각 글리프가 없으므로 필요 시)
HALF2FULL = {}


def load_ko():
    """translation/ko/*.tsv: id \t 원문 \t 번역 → {원문: 번역}"""
    m = {}
    for p in sorted(glob.glob(os.path.join(R, 'translation/ko/*.tsv'))):
        for ln, line in enumerate(open(p, encoding='utf-8'), 1):
            line = line.rstrip('\n')
            if not line or line.startswith('#'): continue
            parts = line.split('\t')
            if len(parts) < 3 or not parts[2] or parts[2] == '=': continue
            m[unesc(parts[1])] = unesc(parts[2])
    return m


def encode(s):
    out = bytearray()
    for ch in s:
        if ch in CM: out += CM[ch][1]
        else:
            ch = HALF2FULL.get(ch, ch)
            out += ch.encode('cp932')
    return bytes(out)


def width(s):
    return sum(1 if ord(c) < 0x80 else 2 for c in s)


def wrap_line(line, W):
    """W: 반각 단위 폭. 공백 기준 단어 줄바꿈, 단어가 너무 길면 글자 단위."""
    if width(line) <= W: return [line]
    out = []; cur = ''
    for tok in re.split(r'(\s+)', line):
        if not tok: continue
        if width(cur + tok) <= W: cur += tok; continue
        if tok.isspace():
            out.append(cur.rstrip()); cur = ''; continue
        if cur.strip(): out.append(cur.rstrip()); cur = ''
        while width(tok) > W:
            k = 0; w = 0
            while k < len(tok) and w + width(tok[k]) <= W: w += width(tok[k]); k += 1
            out.append(tok[:k]); tok = tok[k:]
        cur = tok
    if cur.strip() or not out: out.append(cur.rstrip())
    return out


def wrap(s, W):
    out = []
    for l in s.split('\n'):
        if l.startswith('「') and width(l) > W:
            parts = wrap_line(l, W)
            first = parts[0]; rest = ' '.join(parts[1:])
            out.append(first)
            out += ['　' + x for x in wrap_line(rest, W - 2)]
        else:
            out += wrap_line(l, W)
    return '\n'.join(out)
