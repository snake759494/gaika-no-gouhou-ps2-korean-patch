"""한글패치 빌드: 번역 삽입 → ARC/ARC.INF 재구성 → GAIKA.BIN → ISO 패치.
사용: python tools/build.py [출력ISO]   (출력 ISO가 없으면 원본을 복사해 만든다)"""
import os, sys, struct, shutil, glob
sys.path.insert(0, os.path.dirname(__file__))
from arc import read_inf, NAMES
from text import load_ko, encode, wrap, width
from extract import unesc, GROUPS
from isopatch import Iso
import kfont
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIG = os.path.join(R, 'Gaika no Gouhou - Air Land Force (Japan).iso')
OUT = os.path.join(R, 'Gaika no Gouhou - Air Land Force (Korean).iso')
ARCLBA = {}
WARN = []
DUMMY0 = 353          # PADDING/DUMMY00.DAT 시작 LBA(268MB) — 커진 파일을 옮겨 둘 곳
PAG0 = True
MAXLINES = {'SCN': 13}   # 브리핑 창 최대 줄 수
WRAPW = {'MSG01': 56, 'MSG02': 36, 'MSG03': 36}   # 한 줄 패널: 원문 최대 줄 폭까지 허용


def group_w(tag):
    i = int(tag[3:])
    if tag.startswith('SCN'): return 54 if i <= 12 else 50
    return WRAPW.get(tag)


def paginate(t, n):
    """창이 n줄씩 넘어가므로, 문단(빈 줄 구분)마다 n줄 배수로 채워 문단이 페이지 중간에서 갈리지 않게 한다."""
    paras = [p for p in t.rstrip('\n').split('\n\n')]
    paras = [p.strip('\n') for p in paras if p.strip('\n')]
    pages = []
    for p in paras:
        # 문장 단위 묶음(줄 끝이 문장부호) → 페이지(n줄)에 넘치지 않게 채워 넣기
        groups, cur = [], []
        for l in p.split('\n'):
            cur.append(l)
            if l.rstrip().endswith(('.', '!', '?', '」', '」')): groups.append(cur); cur = []
        if cur: groups.append(cur)
        pg = []
        for g in groups:
            if pg and len(pg) + len(g) > n: pages.append(pg); pg = []
            while len(g) > n: pages.append(g[:n]); g = g[n:]
            pg += g
        if pg: pages.append(pg)
    out = []
    for k, pg in enumerate(pages):
        out += pg
        if k < len(pages) - 1: out += [''] * ((-len(pg)) % n)
    return '\n'.join(out) + '\n'


def strlist_file(tag, raw, ko):
    parts = raw.split(b'\0'); out = []
    for k, s in enumerate(parts):
        if not s: out.append(s); continue
        jp = s.decode('cp932')
        if jp in ko:
            t = ko[jp]
            W = group_w(tag)
            if W is None:   # MSG: 원문 최대 줄 폭 이상
                W = max(max(width(l) for l in jp.split('\n')), 24)
            t = wrap(t, W)
            lim = MAXLINES.get(tag[:3]) if tag.startswith('SCN') and int(tag[3:]) >= 13 else None
            if (tag == 'SCN00' and PAG0) or (PAG0 and tag.startswith('SCN') and 1 <= int(tag[3:]) <= 12 and '「' in t): t = paginate(t, 3)
            while lim and t.rstrip('\n').count('\n') + 1 > lim and '\n\n' in t:
                k = t.rstrip('\n').rfind('\n\n'); t = t[:k] + t[k + 1:]   # 빈 줄을 뒤에서부터 제거
            if jp.endswith('\n') and not t.endswith('\n'): t += '\n'
            out.append(encode(t))
        else:
            out.append(s)
    return b'\0'.join(out)


def fixed_rows():
    rows = []
    for line in open(os.path.join(R, 'translation/src/fixed.tsv'), encoding='utf-8'):
        a, o, cap, s = line.rstrip('\n').split('\t')
        rows.append((a, int(o, 16), int(cap), unesc(s)))
    return rows


def apply_fixed(buf, tag, rows, ko):
    for a, o, cap, jp in rows:
        if a != tag or jp not in ko: continue
        b = encode(ko[jp])
        if len(b) > cap:
            WARN.append('넘침 %s@%x cap=%d len=%d %s' % (a, o, cap, len(b), ko[jp])); continue
        old = len(jp.encode('cp932'))
        buf[o:o + max(old, len(b)) + 1] = b + b'\0' * (max(old, len(b)) + 1 - len(b))


def repack(name, entries, files):
    """entries: INF 항목 목록, files: 바뀐 내용 리스트 → (ARC bytes, 새 entries)"""
    out = bytearray(); new = []
    for e, d in zip(entries, files):
        o = len(out); out += d; out += b'\0' * ((-len(out)) % 2048)
        e2 = list(e); e2[4] = len(d); e2[5] = o; new.append(e2)
    return bytes(out), new


def write_inf(inf, tables):
    d = bytearray(inf)
    for k, nm in enumerate(NAMES):
        n, o = struct.unpack_from('<II', d, 0x10 + 8 * k)
        for j, e in enumerate(tables[nm]): struct.pack_into('<4HII', d, o + 16 * j, *e)
    return bytes(d)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else OUT
    ko = load_ko(); rows = fixed_rows()
    inf, tab = read_inf(os.path.join(R, 'work/ext/ARC.INF'))
    newarc = {}
    # MSG / SCN
    for nm in ('MSG', 'SCN'):
        files = []
        for j, e in enumerate(tab[nm]):
            raw = open(os.path.join(R, 'work/arc/%s/%04d.bin' % (nm, j)), 'rb').read()
            tag = '%s%02d' % (nm, j)
            if (nm == 'MSG') or j <= 25: raw = strlist_file(tag, raw, ko)
            files.append(raw)
        newarc[nm] = repack(nm, tab[nm], files)
    # SYS: 9/11/14 고정칸, 13 글꼴
    files = []
    for j, e in enumerate(tab['SYS']):
        raw = bytearray(open(os.path.join(R, 'work/arc/SYS/%04d.bin' % j), 'rb').read())
        if j in (9, 11, 14): apply_fixed(raw, 'SYS%02d' % j, rows, ko)
        if j == 13:
            for ch, (idx, _) in kfont.charmap().items():
                raw[idx * 242:(idx + 1) * 242] = kfont.pack(kfont.render(ch))
        files.append(bytes(raw))
    newarc['SYS'] = repack('SYS', tab['SYS'], files)
    # MAPDATA
    files = []
    for j, e in enumerate(tab['MAPDATA']):
        raw = bytearray(open(os.path.join(R, 'work/arc/MAPDATA/%04d.bin' % j), 'rb').read())
        apply_fixed(raw, 'MAP%03d' % j, rows, ko); files.append(bytes(raw))
    newarc['MAPDATA'] = repack('MAPDATA', tab['MAPDATA'], files)
    for nm, (_, t) in newarc.items(): tab[nm] = t
    # GAIKA.BIN
    gaika = bytearray(open(os.path.join(R, 'work/ext/GAIKA.BIN'), 'rb').read())
    apply_fixed(gaika, 'GAIKA', rows, ko)
    import patch_code
    patch_code.apply(gaika, ko)
    # ISO
    if not os.path.exists(out) or os.path.getsize(out) != os.path.getsize(ORIG):
        print('ISO 복사...'); shutil.copyfile(ORIG, out)
    iso = Iso(out)
    # 이전 빌드에서 옮겨진 레코드를 원본 위치·크기로 되돌린 뒤 배치(제자리 판정이 원본 기준이 되도록)
    orig = Iso.__new__(Iso); orig.f = open(ORIG, 'rb')
    pvd = orig.read(16, 1); import struct as _st
    orig.root = _st.unpack_from('<I', pvd, 158)[0], _st.unpack_from('<I', pvd, 166)[0]
    for p in ['/DATA/ARC.INF'] + ['/DATA/%s.ARC' % nm for nm in newarc] + ['/GAIKA.BIN']:
        _, oe, osz = orig.find(p); pos, _, _ = iso.find(p); iso.set_record(pos, oe, osz)
    orig.f.close()
    nxt = [DUMMY0]
    def alloc(n):
        l = nxt[0]; nxt[0] += n; return l
    iso.put('/DATA/ARC.INF', write_inf(inf, tab), alloc)
    for nm, (data, _) in newarc.items():
        lba = iso.put('/DATA/%s.ARC' % nm, data, alloc); print(nm, len(data), 'LBA', lba)
    iso.put('/GAIKA.BIN', bytes(gaika), alloc)
    import images
    images.apply(iso)
    # 동영상 자막(work/mov/*_ko.PSS, tools/movsub.py로 생성 — 원본과 같은 크기)
    for mv in ('OP', 'ED'):
        p = os.path.join(R, 'work/mov/%s_ko.PSS' % mv)
        if os.path.exists(p):
            pos, ext, sz = iso.find('/MOV/%s.PSS' % mv); d = open(p, 'rb').read()
            assert len(d) == sz; iso.write_at(ext, d); print('동영상', mv)
    iso.close()
    for w in WARN: print('경고:', w)
    print('완료', out)


if __name__ == '__main__':
    main()
