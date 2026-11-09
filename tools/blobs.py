"""텍스처의 글자 줄 영역 자동 검출(투명 배경 기준) + 번호 붙인 확대 보기.
python tools/blobs.py 206 [gap]"""
import sys, os, numpy as np
from PIL import Image, ImageDraw
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def fgmask(a, mode='key', thr=90):
    rgb = a[..., :3].astype(int)
    if mode == 'bright':
        return rgb.max(2) > thr
    mag = (rgb[..., 0] > 200) & (rgb[..., 1] < 40) & (rgb[..., 2] > 200)
    chk = (abs(rgb[..., 0] - 148) < 12) & (abs(rgb[..., 1] - 136) < 12) & (abs(rgb[..., 2] - 121) < 12)
    return ~mag & ~chk


def lines(a, gap=6, mode='key', thr=90):
    m = fgmask(a, mode, thr)
    rows = np.where(m.any(1))[0]; out = []
    if not len(rows): return out
    groups = []; s = rows[0]; p = rows[0]
    for r in rows[1:]:
        if r > p + 1: groups.append((s, p)); s = r
        p = r
    groups.append((s, p))
    for y0, y1 in groups:
        cols = np.where(m[y0:y1 + 1].any(0))[0]
        s = cols[0]; p = cols[0]
        for c in cols[1:]:
            if c > p + gap: out.append((s, y0, p + 1, y1 + 1)); s = c
            p = c
        out.append((s, y0, p + 1, y1 + 1))
    return out


if __name__ == '__main__':
    i = int(sys.argv[1]); gap = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    mode = sys.argv[3] if len(sys.argv) > 3 else 'key'; thr = int(sys.argv[4]) if len(sys.argv) > 4 else 90
    im = Image.open(os.path.join(R, 'work/img/%03d_0.png' % i)); a = np.asarray(im)
    bs = lines(a, gap, mode, thr)
    bg = Image.new('RGBA', im.size, (255, 0, 255, 255)); bg.alpha_composite(im)
    S = 3; v = bg.convert('RGB').resize((im.width * S, im.height * S), Image.NEAREST); d = ImageDraw.Draw(v)
    for k, (x0, y0, x1, y1) in enumerate(bs):
        d.rectangle((x0 * S, y0 * S, x1 * S - 1, y1 * S - 1), outline=(0, 255, 0))
        d.text((x0 * S + 1, y0 * S + 1), str(k), fill=(0, 255, 255))
        print(k, (x0, y0, x1, y1))
    v.save(os.path.join(R, 'work/view/b%d.png' % i))
