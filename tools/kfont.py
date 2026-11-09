"""한글 글리프 생성 → SYS 13(22x22 4bpp, JIS 94x94 순) 한자 칸(16구~)에 KS X 1001 한글 2350자를 배치.
원본 글자: 바깥 1px 테두리(값 4, 가장자리 1~3) + 흰 채움(8~15, 중심 15). 둥근 고딕 → 나눔스퀘어네오."""
import os, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G = 22; GB = 242; KU0 = 16
FONT = os.path.join(R, 'NanumSquareNeo-dEb.ttf')


def hangul():
    out = []
    for b1 in range(0xB0, 0xC9):
        for b2 in range(0xA1, 0xFF):
            out.append(bytes([b1, b2]).decode('euc-kr'))
    return out


def jis_to_sjis(ku, ten):
    j1, j2 = ku + 0x20, ten + 0x20
    s1 = (j1 + 1) // 2 + (0x70 if j1 <= 0x5e else 0xb0)
    if j1 & 1: s2 = j2 + (0x1f if j2 <= 0x5f else 0x20)
    else: s2 = j2 + 0x7e
    return bytes([s1, s2])


def charmap():
    """한글 → (글리프 인덱스, SJIS 2바이트)"""
    m = {}
    for k, ch in enumerate(hangul()):
        idx = (KU0 - 1) * 94 + k
        ku, ten = divmod(idx, 94)
        m[ch] = (idx, jis_to_sjis(ku + 1, ten + 1))
    return m


def render(ch, size=19, dy=0):
    S = 4
    f = ImageFont.truetype(FONT, size * S)
    im = Image.new('L', (G * S, G * S), 0); dr = ImageDraw.Draw(im)
    bb = dr.textbbox((0, 0), ch, font=f)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    x = (G * S - w) // 2 - bb[0]
    y = (G * S - h) // 2 - bb[1] + dy * S
    dr.text((x, y), ch, font=f, fill=255)
    fill = np.asarray(im.resize((G, G), Image.LANCZOS)).astype(np.float32) / 255
    big = np.asarray(im.filter(ImageFilter.MaxFilter(9))).astype(np.float32)   # 약 1px 확장(4배 해상도)
    out = np.asarray(Image.fromarray(big.astype(np.uint8)).resize((G, G), Image.LANCZOS)).astype(np.float32) / 255
    fill = np.clip((fill - 0.08) / 0.84, 0, 1)
    v = np.where(fill > 0.02, 4 + 11 * fill, 4 * out)
    return np.clip(np.rint(v), 0, 15).astype(np.uint8)


def pack(g):
    f = g.reshape(-1)
    return bytes((f[0::2] | (f[1::2] << 4)).astype(np.uint8))


def build(src, dst):
    d = bytearray(open(src, 'rb').read())
    for ch, (idx, _) in charmap().items():
        d[idx * GB:(idx + 1) * GB] = pack(render(ch))
    open(dst, 'wb').write(d)


if __name__ == '__main__':
    build(os.path.join(R, 'work/arc/SYS/0013.bin'), sys.argv[1] if len(sys.argv) > 1 else os.path.join(R, 'work/font_ko.bin'))
