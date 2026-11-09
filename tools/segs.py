"""행 범위 안의 글자 조각(가로 간격 gap 이상으로 구분) x 범위 출력: python tools/segs.py 156 y0 y1 [gap]"""
import sys, os, numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from blobs import fgmask
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
i, y0, y1 = map(int, sys.argv[1:4]); gap = int(sys.argv[4]) if len(sys.argv) > 4 else 5
a = np.asarray(Image.open(os.path.join(R, 'work/img/%03d_0.png' % i)))
m = fgmask(a)[y0:y1]
cols = np.where(m.any(0))[0]
if len(cols):
    s = p = cols[0]; out = []
    for c in cols[1:]:
        if c > p + gap: out.append((s, p + 1)); s = c
        p = c
    out.append((s, p + 1))
    rows = np.where(m.any(1))[0]
    print('y', y0 + rows[0], y0 + rows[-1] + 1, 'segs', [(int(a), int(b)) for a, b in out])
