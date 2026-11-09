"""IMG PNG 모음 시트: python tools/sheet.py start end → work/view/sheet_S.png"""
import sys, os, glob
from PIL import Image, ImageDraw
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
a, b = int(sys.argv[1]), int(sys.argv[2]); C = 8; T = 150
fs = [f for i in range(a, b) for f in sorted(glob.glob(os.path.join(R, 'work/img/%03d_*.png' % i)))[:1]]
rows = (len(fs) + C - 1) // C
sh = Image.new('RGB', (C * T, rows * (T + 14)), (40, 40, 40)); d = ImageDraw.Draw(sh)
for k, f in enumerate(fs):
    im = Image.open(f).convert('RGB'); im.thumbnail((T, T))
    x, y = k % C * T, k // C * (T + 14)
    sh.paste(im, (x, y + 14)); d.text((x + 2, y), os.path.basename(f) + ' %dx%d' % Image.open(f).size, fill=(255, 255, 0))
sh.save(os.path.join(R, 'work/view/sheet.png'))
