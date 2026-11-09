"""번역 템플릿 생성: translation/ko/<그룹>_NN.tsv (id \t 원문 \t 번역 \t [용량]) — 이미 있는 번역은 유지."""
import os, sys, re, collections
sys.path.insert(0, os.path.dirname(__file__))
from extract import unesc, esc
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST = re.compile(r'^イベント番号([０-９]+)のテストメッセージ\n$')
Z2A = str.maketrans('０１２３４５６７８９', '0123456789')


def uniq(path, col):
    u = collections.OrderedDict()
    for line in open(path, encoding='utf-8'):
        p = line.rstrip('\n').split('\t')
        s = unesc(p[col])
        if col == 3:
            cap = int(p[2]); u[s] = min(u.get(s, 9999), cap)
        else: u.setdefault(s, None)
    return u


def write_chunks(name, items, nchunk):
    total = sum(len(s) for s, _ in items); per = total / nchunk
    chunks = [[]]; acc = 0
    for it in items:
        if acc > per * len(chunks) and len(chunks) < nchunk: chunks.append([])
        chunks[-1].append(it); acc += len(it[0])
    for k, ch in enumerate(chunks):
        p = os.path.join(R, 'translation/ko/%s_%02d.tsv' % (name, k + 1))
        if os.path.exists(p): continue
        with open(p, 'w', encoding='utf-8', newline='\n') as f:
            for j, (s, cap) in enumerate(ch):
                f.write('%s%02d-%04d\t%s\t\t%s\n' % (name, k + 1, j, esc(s), '' if cap is None else cap))


if __name__ == '__main__':
    src = os.path.join(R, 'translation/src')
    tests = []
    plan = {'tutmsg': [('scn_tutorial', 2), ('msg', 2)], 'event': [('scn_event', 2)], 'brief': [('scn_brief', 2)]}
    n = {'tutmsg': 2, 'event': 3, 'brief': 4}
    for name, srcs in plan.items():
        items = []
        for g, col in srcs:
            for s, cap in uniq(os.path.join(src, g + '.tsv'), col).items():
                if TEST.match(s): tests.append(s); continue
                items.append((s, cap))
        write_chunks(name, items, n[name])
    write_chunks('fixed', list(uniq(os.path.join(src, 'fixed.tsv'), 3).items()), 1)
    with open(os.path.join(R, 'translation/ko/auto_test.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        for k, s in enumerate(sorted(set(tests))):
            num = TEST.match(s).group(1).translate(Z2A)
            f.write('test-%04d\t%s\t%s\n' % (k, esc(s), esc('이벤트 번호 %s 테스트 메시지\n' % num)))
