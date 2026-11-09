"""IMG.ARC 텍스처 한글화: 사양(img_specs.SPECS) 적용 → ISO의 IMG.ARC 안 같은 자리에 덮어쓰기(크기 불변).
python tools/images.py preview 206   → work/view/p206.png (원본|결과)"""
import os, sys, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from arc import read_inf
import retext, tim2
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIG = os.path.join(R, 'Gaika no Gouhou - Air Land Force (Japan).iso')
IMG_LBA = 1804498


def entry(i):
    _, r = read_inf(os.path.join(R, 'work/ext/ARC.INF'))
    return r['IMG'][i]


def load(i):
    e = entry(i)
    with open(ORIG, 'rb') as f:
        f.seek(IMG_LBA * 2048 + e[5]); return f.read(e[4])


def make(i):
    import img_specs
    spec = img_specs.SPECS[i]
    t = retext.Tex(load(i))
    for it in spec:
        if callable(it): it(t); continue
        box, text = it[0], it[1]; opt = it[2] if len(it) > 2 else {}
        retext.retext(t, box, text, **opt)
    return t


def apply(iso):
    import img_specs
    pos, ext, sz = iso.find('/DATA/IMG.ARC')
    for i in sorted(img_specs.SPECS):
        t = make(i); data = t.bytes(); e = entry(i)
        assert len(data) == e[4]
        iso.f.seek(ext * 2048 + e[5]); iso.f.write(data)
    print('이미지 %d장' % len(img_specs.SPECS))


def preview(i, scale=2):
    from PIL import Image
    t = make(i)
    a = tim2.decode(t.bytes(), tim2.parse(t.bytes())[0])
    o = tim2.decode(load(i), tim2.parse(load(i))[0])
    im = Image.fromarray(np.concatenate([o, a], 1)[..., :3])
    im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    im.save(os.path.join(R, 'work/view/p%d.png' % i))


if __name__ == '__main__':
    if sys.argv[1] == 'preview':
        for x in sys.argv[2:]: preview(int(x), 2 if int(x) in range(150, 300) else 1)
