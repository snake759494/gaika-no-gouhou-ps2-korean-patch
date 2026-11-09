"""TIM2(8bpp) 텍스처 글자 교체.
항목: (box, 한글, 옵션) — box 안의 원래 글자를 지우고 같은 스타일(세로 그라데이션 채움+테두리)로 한글을 그린 뒤
기존 CLUT로 양자화한다(팔레트 불변 → 파일 크기 불변)."""
import os, sys, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
import tim2
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = {'serif': 'SeoulHangangB.ttf', 'serifeb': 'SeoulHangangEB.ttf', 'serifm': 'SeoulHangangM.ttf',
         'gothic': 'NanumSquareNeo-dEb.ttf', 'gothicb': 'NanumSquareNeo-cBd.ttf', 'gothicr': 'NanumSquareNeo-bRg.ttf',
         'pixel': 'Galmuri11-Bold.ttf'}


def font(name, size):
    return ImageFont.truetype(os.path.join(R, FONTS[name]), size)


class Tex:
    def __init__(self, data):
        self.d = bytearray(data); self.p = tim2.parse(self.d)[0]
        assert self.p['itype'] == 5, 'only 8bpp'
        rgba = tim2.decode(self.d, self.p)          # 표시용 RGBA(알파 0..255)
        self.rgb = rgba[..., :3].astype(np.float32)
        self.w, self.h = self.p['w'], self.p['h']
        o = self.p['img_off']
        self.idx = np.frombuffer(bytes(self.d[o:o + self.w * self.h]), np.uint8).reshape(self.h, self.w).copy()
        # 팔레트(표시 순서): 인덱스 → RGB
        cl = self.d[self.p['clut_off']:self.p['clut_off'] + self.p['clut']]
        ct = self.p['ctype'] & 0x3f
        if ct == 3: pal = np.frombuffer(bytes(cl), np.uint8).reshape(-1, 4)[:, :3].astype(np.float32)
        else:
            v = np.frombuffer(bytes(cl), '<u2').astype(np.uint32)
            pal = np.stack([(v & 31) << 3, ((v >> 5) & 31) << 3, ((v >> 10) & 31) << 3], 1).astype(np.float32)
        if not (self.p['ctype'] & 0x80) and len(pal) >= 256:
            pal = tim2._clut_unswz(np.concatenate([pal, np.zeros((len(pal), 1), np.float32)], 1)[:256])[:, :3]
        self.pal = pal[:256]

    def bytes(self):
        o = self.p['img_off']; self.d[o:o + self.w * self.h] = self.idx.tobytes(); return bytes(self.d)

    def color_of(self, i): return self.pal[i]

    def nearest(self, rgb, allowed=None):
        pal = self.pal if allowed is None else self.pal[allowed]
        dd = ((rgb[:, None, :] - pal[None, :, :]) ** 2).sum(2)
        k = dd.argmin(1)
        return (k if allowed is None else np.asarray(allowed)[k]).astype(np.uint8)


def is_key(rgb):
    return (rgb[..., 0] > 200) & (rgb[..., 1] < 40) & (rgb[..., 2] > 200)


def retext(t, box, text, font_name='serif', size=None, fg_mode='auto', erase='auto', align='center',
           fill=None, outline=None, out_w=1, squeeze=0.75, dy=0, bright_thr=None, keyidx=None, ref=None, tracking=0, height=None):
    x0, y0, x1, y1 = box
    sub = t.rgb[y0:y1, x0:x1]; key = is_key(sub)
    lum = sub.max(2)
    # 원래 글자 마스크
    if erase == 'auto': erase = 'key' if key.mean() > 0.3 else 'inpaint'
    if erase == 'diff':
        # 줄 중앙값과 크게 다른 픽셀(밝은 글자+어두운 테두리) → inpaint
        med = np.median(lum, 1, keepdims=True)
        fgm = np.abs(lum - med) > (bright_thr or 18)
        fgm = cv2.dilate(fgm.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        erase = 'inpaint'
    elif erase == 'key':
        fgm = ~key
    else:
        thr = bright_thr if bright_thr is not None else np.percentile(lum, 55) + 25
        fgm = lum > thr
        fgm = cv2.dilate(fgm.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    # 스타일 추출(ref 영역 지정 시 거기서)
    rx0, ry0, rx1, ry1 = ref or box
    rs = t.rgb[ry0:ry1, rx0:rx1]; rl = rs.max(2)
    rm = ~is_key(rs) if erase == 'key' else fgm if ref is None and erase == 'inpaint' and bright_thr is not None and bright_thr < 40 else rl > (bright_thr if bright_thr is not None else np.percentile(rl, 55) + 25)
    ys, xs = np.where(rm)
    rows = np.where(rm.any(1))[0]
    if not len(rows): rows = np.array([0, ry1 - ry0 - 1])
    if fill is None and len(ys):
        lv = rl[ys, xs]; hi = lv >= np.percentile(lv, 60)
        H = ry1 - ry0; grad = []
        for k in range(H):
            sel = hi & (ys == k)
            grad.append(np.median(rs[ys[sel], xs[sel]], 0) if sel.sum() >= 2 else None)
        last = None
        for k in range(H):
            if grad[k] is None: grad[k] = last
            else: last = grad[k]
        last = None
        for k in range(H - 1, -1, -1):
            if grad[k] is None: grad[k] = last
            else: last = grad[k]
        if grad[0] is None: grad = [np.array([255, 255, 255], np.float32)] * H
        fillg = np.array(grad, np.float32)
        # 그라데이션 행 범위를 글자 실제 높이로 정규화
        rows = np.where(rm.any(1))[0]; fillg = fillg[rows[0]:rows[-1] + 1]
    else:
        fillg = np.array([fill or (255, 255, 255)], np.float32)
    if outline is None and len(ys):
        lv = rl[ys, xs]; lo = lv <= np.percentile(lv, 15)
        outline = tuple(np.median(rs[ys[lo], xs[lo]], 0)) if lo.sum() else (0, 0, 0)
    # 지우기
    if erase == 'key':
        if keyidx is None:
            kk = np.argwhere(is_key(t.rgb))
            keyidx = t.idx[kk[0][0], kk[0][1]]
        t.idx[y0:y1, x0:x1][fgm] = keyidx; t.rgb[y0:y1, x0:x1][fgm] = t.pal[keyidx]
    elif erase == 'inpaint':
        img = np.clip(t.rgb[y0:y1, x0:x1], 0, 255).astype(np.uint8)
        pad = 6
        X0, Y0, X1, Y1 = max(0, x0 - pad), max(0, y0 - pad), min(t.w, x1 + pad), min(t.h, y1 + pad)
        big = np.clip(t.rgb[Y0:Y1, X0:X1], 0, 255).astype(np.uint8).copy()
        mk = np.zeros(big.shape[:2], np.uint8); mk[y0 - Y0:y1 - Y0, x0 - X0:x1 - X0] = fgm.astype(np.uint8) * 255
        res = cv2.inpaint(big, mk, 4, cv2.INPAINT_TELEA).astype(np.float32)
        t.rgb[Y0:Y1, X0:X1][mk > 0] = res[mk > 0]
        q = t.nearest(res[mk > 0].reshape(-1, 3))
        t.idx[Y0:Y1, X0:X1][mk > 0] = q
    elif erase == 'rowfill':
        # 상자 전체를 줄별 중앙값(글자 제외)으로 채움 — 어두운 테두리 잔상까지 제거
        for r in range(y0, y1):
            row = t.rgb[r, x0:x1]; m = fgm[r - y0]
            c = np.median(row[~m], 0) if (~m).sum() else np.median(row, 0)
            row[:] = c; t.idx[r, x0:x1] = t.nearest(c[None])[0]
    elif erase == 'rowmed':
        for r in range(y0, y1):
            row = t.rgb[r, x0:x1]; m = fgm[r - y0]
            if (~m).sum():
                c = np.median(row[~m], 0); row[m] = c
                t.idx[r, x0:x1][m] = t.nearest(c[None])[0]
    # 그리기
    if not text: return
    gh = (rows[-1] - rows[0] + 1) if len(ys) else (y1 - y0)
    top = rows[0] if (len(ys) and ref is None) else 0
    if height: gh = height; top = (y1 - y0 - height) // 2
    S = 4
    sz = size or gh
    f = font(font_name, sz * S)
    im = Image.new('L', ((x1 - x0) * S * 3, (y1 - y0) * S * 3), 0); dr = ImageDraw.Draw(im)
    if tracking:
        xx = 0
        for ch in text:
            dr.text((xx, 0), ch, font=f, fill=255); xx += dr.textlength(ch, font=f) + tracking * S
    else:
        dr.text((0, 0), text, font=f, fill=255)
    bb = im.getbbox()
    if not bb: return
    im = im.crop(bb)
    tw, th = im.size
    W = (x1 - x0 - 2 * out_w) * S; Hh = gh * S
    sc = min(1.0, Hh / th)
    nw, nh = tw * sc, th * sc
    sx = 1.0
    if nw > W: sx = max(W / nw, squeeze)
    if nw * sx > W: sc2 = W / (nw * sx); nw *= sc2; nh *= sc2
    nw = int(nw * sx)
    im = im.resize((max(1, int(round(nw / S))) * S, max(1, int(round(nh / S))) * S), Image.LANCZOS)
    m = np.asarray(im.resize((im.width // S, im.height // S), Image.LANCZOS)).astype(np.float32) / 255
    mh, mw = m.shape
    ty = y0 + top + (gh - mh) // 2 + dy
    if align == 'center': tx = x0 + (x1 - x0 - mw) // 2
    elif align == 'left': tx = x0 + out_w
    else: tx = x1 - out_w - mw
    full = np.zeros((t.h + 8, t.w + 8), np.float32); full[ty + 4:ty + 4 + mh, tx + 4:tx + 4 + mw] = m
    full = full[4:-4, 4:-4]
    ol = cv2.dilate(full, np.ones((2 * out_w + 1, 2 * out_w + 1), np.float32)) if out_w else full * 0
    reg = (slice(max(0, ty - out_w - 1), min(t.h, ty + mh + out_w + 1)), slice(max(0, tx - out_w - 1), min(t.w, tx + mw + out_w + 1)))
    base = t.rgb[reg]; fm = full[reg]; om = ol[reg]
    gy = np.clip(((np.arange(base.shape[0]) + reg[0].start - ty) / max(1, mh - 1) * (len(fillg) - 1)).round().astype(int), 0, len(fillg) - 1)
    fc = fillg[gy][:, None, :]
    oc = np.array(outline, np.float32)
    newc = base * (1 - om[..., None]) + oc * om[..., None]
    newc = newc * (1 - fm[..., None]) + fc * fm[..., None]
    ch = (om > 0.25) | (fm > 0.1)
    t.rgb[reg][ch] = newc[ch]
    t.idx[reg][ch] = t.nearest(newc[ch].reshape(-1, 3))


class _Pad:
    """텍스처 가장자리를 넘는 박스용: 32px 여백을 붙인 임시 텍스처"""
    P = 32

    def __init__(self, t):
        P = self.P; self.t = t; self.pal = t.pal; self.w, self.h = t.w + 2 * P, t.h + 2 * P
        # 여백은 가장자리 복제(inpaint가 엉뚱한 색을 끌어오지 않도록)
        self.rgb = np.pad(t.rgb, ((P, P), (P, P), (0, 0)), mode='edge')
        self.idx = np.pad(t.idx, ((P, P), (P, P)), mode='edge')

    nearest = Tex.nearest

    def done(self):
        P = self.P; self.t.rgb[:] = self.rgb[P:-P, P:-P]; self.t.idx[:] = self.idx[P:-P, P:-P]


def chars(t, items, h=18, w=16, keep_key=True, **opt):
    """한 글자씩 제자리 교체. items: [(x, y, 글자), ...] — x,y는 원래 글자 칸 좌상단(텍스처 밖이어도 됨)"""
    keym = is_key(t.rgb); kidx = t.idx[keym].copy(); krgb = t.rgb[keym].copy()
    for x, y, ch in items:
        p = _Pad(t); P = p.P
        x0, y0, x1, y1 = x + P, y + P, x + w + P, y + h + P
        ix0, iy0, ix1, iy1 = max(x0, P), max(y0, P), min(x1, P + t.w), min(y1, P + t.h)
        if ix0 >= ix1 or iy0 >= iy1: continue
        o = dict(opt); o.setdefault('height', h - 2)
        # 지우기는 텍스처 안쪽만, 그리기는 전체 칸 기준
        retext(p, (ix0, iy0, ix1, iy1), '', **{k: v for k, v in o.items() if k in ('erase', 'bright_thr', 'fill', 'outline')})
        o['erase'] = 'none'
        retext(p, (x0, y0, x1, y1), ch, **o)
        # 칸 밖으로 번진 부분 제거: 텍스처 안쪽만 반영
        p.done()
    if keep_key: t.idx[keym] = kidx; t.rgb[keym] = krgb
