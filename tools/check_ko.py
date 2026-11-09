"""번역 검사: python tools/check_ko.py [파일...]  (기본: translation/ko/*.tsv)
- 빈 번역, $코드 불일치, 인코딩 불가 문자(완성형 2350 외 한글 등), 끝 \\n 불일치, 고정칸 용량 초과, 남은 가나·한자"""
import sys, os, re, glob
sys.path.insert(0, os.path.dirname(__file__))
from extract import unesc
from kfont import charmap
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CM = charmap()


def enc_len(s):
    n = 0
    for ch in s:
        if ch in CM: n += 2
        else: n += len(ch.encode('cp932'))
    return n


def check(path):
    errs = []
    for line in open(path, encoding='utf-8'):
        p = line.rstrip('\n').split('\t')
        if len(p) < 3: errs.append((p[0], '칸 부족')); continue
        i, jp, ko = p[0], unesc(p[1]), unesc(p[2])
        cap = p[3] if len(p) > 3 else ''
        if ko == '=': continue
        if not ko: errs.append((i, '빈 번역')); continue
        if sorted(re.findall(r'\$\d\d', jp)) != sorted(re.findall(r'\$\d\d', ko)): errs.append((i, '$코드 불일치'))
        if jp.endswith('\n') != ko.endswith('\n'): errs.append((i, '끝 \\n 불일치'))
        bad = []
        for ch in ko:
            if ch in CM: continue
            if '가' <= ch <= '힣': bad.append(ch); continue
            try: ch.encode('cp932')
            except UnicodeEncodeError: bad.append(ch)
        if bad: errs.append((i, '인코딩 불가 %s' % ''.join(bad)))
        kana = [c for c in ko if '぀' <= c <= 'ヿ' and c not in '・ー' or '一' <= c <= '鿿']
        if kana: errs.append((i, '가나/한자 남음 %s' % ''.join(kana)))
        if cap and not bad and enc_len(ko) > int(cap): errs.append((i, '용량 초과 %d>%s' % (enc_len(ko), cap)))
    return errs


if __name__ == '__main__':
    fs = sys.argv[1:] or sorted(glob.glob(os.path.join(R, 'translation/ko/*.tsv')))
    tot = 0
    for f in fs:
        e = check(f); tot += len(e)
        for i, m in e[:40]: print(os.path.basename(f), i, m)
        if len(e) > 40: print(os.path.basename(f), '... 외 %d건' % (len(e) - 40))
    print('오류 %d건' % tot)
