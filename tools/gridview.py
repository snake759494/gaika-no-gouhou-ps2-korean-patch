"""좌표 격자 확대 보기: python tools/gridview.py 이미지번호 [x0 y0 x1 y1] [배율]"""
import sys, os
from PIL import Image, ImageDraw
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
i = int(sys.argv[1])
p = sys.argv[1] if not sys.argv[1].isdigit() else os.path.join(R, 'work/img/%03d_0.png' % i)
im = Image.open(p).convert('RGB')
box = tuple(map(int, sys.argv[2:6])) if len(sys.argv) >= 6 else (0, 0, im.width, im.height)
S = int(sys.argv[6]) if len(sys.argv) > 6 else max(1, min(4, 1000 // max(box[2] - box[0], box[3] - box[1])))
c = im.crop(box).resize(((box[2] - box[0]) * S, (box[3] - box[1]) * S), Image.NEAREST)
d = ImageDraw.Draw(c)
step = 8 if S >= 3 else 16
for x in range((box[0] // step + 1) * step, box[2], step):
    col = (0, 255, 0) if x % 32 == 0 else (0, 110, 0)
    d.line(((x - box[0]) * S, 0, (x - box[0]) * S, c.height), fill=col)
    if x % 32 == 0: d.text(((x - box[0]) * S + 2, 2), str(x), fill=(255, 255, 0))
for y in range((box[1] // step + 1) * step, box[3], step):
    col = (0, 255, 0) if y % 32 == 0 else (0, 110, 0)
    d.line((0, (y - box[1]) * S, c.width, (y - box[1]) * S), fill=col)
    if y % 32 == 0: d.text((2, (y - box[1]) * S + 2), str(y), fill=(255, 255, 0))
c.save(os.path.join(R, 'work/view/grid.png'))
print(c.size)
