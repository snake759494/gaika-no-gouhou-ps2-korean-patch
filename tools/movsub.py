"""PSS 동영상 자막 한글화: 일본어 흰 글자를 지우고(inpaint) 같은 위치·속도·투명도로 한글을 그린 뒤
같은 GOP 구조로 재인코딩하고, GOP별로 원본 바이트 범위에 맞춰 0 채움 → 원본 PSS 팩/PTS/오디오는 그대로.
python tools/movsub.py OP|ED"""
import os, sys, subprocess, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
import movtext, pss, movsub_cfg
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 640, 448
S = 4


def render_line(text, size, font='SeoulHangangM.ttf'):
    f = ImageFont.truetype(os.path.join(R, font), size * S)
    im = Image.new('L', (W * S * 2, size * S * 2), 0)
    d = ImageDraw.Draw(im); d.text((0, 0), text, font=f, fill=255)
    bb = im.getbbox()
    if not bb: return np.zeros((1, 1), np.float32), 0
    im = im.crop((0, 0, bb[2] + S, size * S * 2))
    im = im.resize((im.width // S, im.height // S), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32) / 255
    # 글자 위쪽 기준선: 렌더 박스 맨 위가 글꼴 ascent 기준이므로 실제 잉크 상단 오프셋 반환
    rows = np.where(a.max(1) > 0.2)[0]
    return a, int(rows[0]) if len(rows) else 0


def measure(f, y0, y1, x0, x1):
    """띠 안 원래 글자의 대비(0~): 밝은 글자 픽셀이 주변보다 얼마나 밝은지"""
    y0, y1 = max(0, y0), min(H, y1)
    if y1 - y0 < 4: return 0.0, None
    hsv = cv2.cvtColor(f[y0:y1, x0:x1], cv2.COLOR_RGB2HSV)
    v = hsv[..., 2].astype(np.int16)
    bg = cv2.medianBlur(hsv[..., 2], 21).astype(np.int16)
    dif = (v - bg) * (hsv[..., 1] < 100)
    return float(np.percentile(dif, 99.3)), (dif, bg)


def erase(f, bands, mode='inpaint'):
    m = np.zeros((H, W), np.uint8)
    hsv = cv2.cvtColor(f, cv2.COLOR_RGB2HSV)
    v = hsv[..., 2].astype(np.int16); bg = cv2.medianBlur(hsv[..., 2], 21).astype(np.int16)
    t = np.abs(v - bg) > 8 if mode == 'inpaint' else (v - bg) > 14
    for y0, y1, x0, x1 in bands:
        y0, y1 = max(0, y0), min(H, y1)
        if y1 <= y0: continue
        m[y0:y1, x0:x1] = t[y0:y1, x0:x1]
    if not m.any(): return f
    m = cv2.dilate(m, np.ones((3, 3), np.uint8))
    if mode == 'inpaint': return cv2.inpaint(f, m * 255, 3, cv2.INPAINT_TELEA)
    # 글자 픽셀만 주변 배경(글자 제외 정규화 블러)으로 채움 — 질감이 남도록 원래 픽셀을 일부 섞음
    ff = f.astype(np.float32); w = (1 - m).astype(np.float32)
    num = cv2.GaussianBlur(ff * w[..., None], (0, 0), 3); den = cv2.GaussianBlur(w, (0, 0), 3)[..., None] + 1e-3
    fill = num / den
    mm = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.8)[..., None]
    return np.clip(ff * (1 - mm) + fill * mm, 0, 255).astype(np.uint8)


def draw(f, a, x, y, alpha, color=(208, 208, 204)):
    if alpha <= 0.01: return f
    h, w = a.shape
    out = f.astype(np.float32)
    # 그림자(오른쪽 아래, 흐리게)
    sh = cv2.GaussianBlur(a, (0, 0), 1.0)
    for img, dx, dy, col, k in ((sh, 1, 1, (0, 0, 0), 0.7), (a, 0, 0, color, 1.0)):
        X0, Y0 = x + dx, y + dy
        xs0, ys0 = max(0, -X0), max(0, -Y0)
        xs1, ys1 = min(w, W - X0), min(h, H - Y0)
        if xs1 <= xs0 or ys1 <= ys0: continue
        m = img[ys0:ys1, xs0:xs1, None] * alpha * k
        reg = out[Y0 + ys0:Y0 + ys1, X0 + xs0:X0 + xs1]
        reg[:] = reg * (1 - m) + np.array(col, np.float32) * m
    return np.clip(out, 0, 255).astype(np.uint8)


def keyframes(name):
    es = pss.video_es(open(os.path.join(R, 'work/mov/%s.PSS' % name), 'rb').read())
    seq = [t for o, t in pss.pictures(es) if t in 'IPBG']
    ks = []; c = 0
    for k, t in enumerate(seq):
        if t == 'I':
            nb = 0
            for u in seq[k + 1:]:
                if u == 'B': nb += 1
                else: break
            ks.append(c + nb if ks else 0)
        if t in 'IPB': c += 1
    return ks


def process(name):
    cfg = movsub_cfg.CFG[name]
    kf = ','.join('%.4f' % (k / 30) for k in keyframes(name))
    src = os.path.join(R, 'work/mov/%s.PSS' % name)
    # 각 항목: 줄 목록 (frame_t → (y_top, x_left 또는 중앙정렬)), 프레임 범위
    items = []
    for b in cfg:
        lines = []
        for k, (idx, txt) in enumerate(b['lines']):
            a, top = render_line(txt, b.get('size', 20))
            lines.append((idx, a, top))
        items.append((b, lines))
    enc = subprocess.Popen([movtext.FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', '30',
                            '-i', '-', '-c:v', 'mpeg2video', '-pix_fmt', 'yuv420p', '-g', '20', '-bf', '2', '-sc_threshold', '1000000000', '-force_key_frames', kf,
                            '-b:v', cfg_rate(name), '-maxrate', '4500k', '-bufsize', '1441792', '-aspect', '4:3',
                            '-f', 'mpeg2video', os.path.join(R, 'work/mov/%s_new.m2v' % name)], stdin=subprocess.PIPE)
    prev = {}
    for t, f in enumerate(movtext.frames(src)):
        f = f.copy(); bands = []; draws = []
        for b, lines in items:
            if not (b['t0'] <= t <= b['t1']): continue
            for idx, a, top in lines:
                if 'ys' in b: y = b['ys'][idx]
                elif 'v' in b: y = int(round(b['Y0'] + b['pitch'] * idx - b['v'] * (t - b['t0'])))
                else: y = int(round(b['Y0'] + b['pitch'] * idx))
                if y > H + 2 or y < -24: continue
                if b.get('center'): x = (W - a.shape[1]) // 2 + b.get('cx', 0); xa, xb = b['xr']
                else: x = b['x']; xa, xb = b['x'] - 6, min(W, b['x'] + 600)
                if 'v' in b or 'ys' in b: c, _ = measure(f, y - 3, y + 19, xa, xb); key = (id(b), idx)
                else:
                    ys = [int(round(b['Y0'] + b['pitch'] * i)) for i, _, _ in lines]
                    c, _ = measure(f, min(ys) - 3, max(ys) + 19, xa, xb); key = (id(b), -1)
                al = min(1.0, max(0.0, (c - b.get('c0', 12)) / (b['cfull'] - b.get('c0', 12))))
                al = 0.6 * al + 0.4 * prev.get(key, al)
                if 'v' in b or 'ys' in b or idx == lines[-1][0]: prev[key] = al
                bands.append((y - 4, y + 21, xa, xb))
                if al > 0.02: draws.append((a, x, y - top + b.get('dy', -1), al))
        if bands: f = erase(f, bands, movsub_cfg.ERASE.get(name, 'inpaint'))
        for a, x, y, al in draws: f = draw(f, a, x, y, al)
        enc.stdin.write(f.tobytes())
        if t in movsub_cfg.SNAP.get(name, ()):
            Image.fromarray(f).save(os.path.join(R, 'work/mov/s_%s_%04d.png' % (name, t)))
    enc.stdin.close(); enc.wait()


def cfg_rate(name): return movsub_cfg.RATE.get(name, '3800k')


def gops(es):
    p = pss.pictures(es)
    st = [o for o, t in p if t == 'G']
    if p[0][1] == 'S': st[0] = p[0][0]
    return st + [len(es)]


def ptypes(b): return ''.join(t for o, t in pss.pictures(b) if t in 'IPB')


def splice(name):
    d = open(os.path.join(R, 'work/mov/%s.PSS' % name), 'rb').read()
    es = pss.video_es(d)
    new = open(os.path.join(R, 'work/mov/%s_new.m2v' % name), 'rb').read()
    go, gn = gops(es), gops(new)
    assert len(go) == len(gn), (len(go), len(gn))
    out = bytearray(); over = []
    kf = keyframes(name) + [10 ** 9]
    rng = [(b['t0'] - 3, b['t1'] + 3) for b in movsub_cfg.CFG[name]]
    for i in range(len(go) - 1):
        a = new[gn[i]:gn[i + 1]]; L = go[i + 1] - go[i]
        if not any(kf[i] <= t1 and kf[i + 1] > t0 for t0, t1 in rng) or ptypes(a) != ptypes(es[go[i]:go[i + 1]]): a = es[go[i]:go[i + 1]]
        if i == len(go) - 2:   # 마지막: 시퀀스 끝 코드 유지
            pass
        if len(a) > L: over.append((i, len(a) - L)); a = es[go[i]:go[i + 1]]   # 넘치면 원본 GOP 유지
        out += a + b'\0' * (L - len(a))
    out = bytes(out)
    print(name, 'GOP', len(go) - 1, '넘침(원본 유지)', over)
    fin, npad = pss.zero_to_padding(pss.put_video_es(d, out)); print('패딩 패킷', npad)
    open(os.path.join(R, 'work/mov/%s_ko.PSS' % name), 'wb').write(fin)
    return over


if __name__ == '__main__':
    n = sys.argv[1]
    if len(sys.argv) < 3 or sys.argv[2] != 'splice': process(n)
    splice(n)
