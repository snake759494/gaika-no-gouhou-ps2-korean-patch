"""동영상 자막(흰 글자) 검출/교체 공용 함수"""
import numpy as np, cv2, subprocess, imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H = 640, 448


def frames(path):
    p = subprocess.Popen([FF, '-v', 'error', '-i', path, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    while True:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3)


def textmask(f, d=28, smax=90):
    hsv = cv2.cvtColor(f, cv2.COLOR_RGB2HSV)
    v = hsv[..., 2].astype(np.int16); s = hsv[..., 1]
    bg = cv2.medianBlur(hsv[..., 2], 21).astype(np.int16)
    return ((v - bg) > d) & (s < smax) & (v > 90)
