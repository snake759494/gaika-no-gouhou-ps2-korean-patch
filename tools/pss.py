"""PSS(MPEG-PS) 비디오 ES 추출/교체. 팩·PES 구조와 PTS는 원본 그대로 두고 비디오 페이로드만 바꾼다."""
import struct, sys


def pes_list(d):
    """[(payload_start, payload_len, sid)] 순서대로"""
    out = []; i = 0
    while i < len(d) - 4:
        if d[i:i + 4] == b'\x00\x00\x01\xba':
            st = d[i + 13] & 7; i += 14 + st; continue
        if d[i:i + 3] == b'\x00\x00\x01':
            sid = d[i + 3]
            if sid == 0xb9: break
            L = struct.unpack('>H', d[i + 4:i + 6])[0]
            if sid in (0xe0, 0xbd):
                hl = d[i + 8]; ps = i + 9 + hl
                out.append((ps, i + 6 + L - ps, sid))
            i += 6 + L; continue
        i += 1
    return out


def video_es(d):
    return b''.join(d[s:s + n] for s, n, sid in pes_list(d) if sid == 0xe0)


def put_video_es(d, es):
    d = bytearray(d); k = 0
    for s, n, sid in pes_list(d):
        if sid != 0xe0: continue
        d[s:s + n] = es[k:k + n]; k += n
    assert k == len(es), (k, len(es))
    return bytes(d)


def pictures(es):
    """[(offset, type)] — picture start code 위치와 I/P/B, 그리고 GOP 헤더 위치"""
    out = []; i = 0
    while True:
        i = es.find(b'\x00\x00\x01', i)
        if i < 0 or i + 5 >= len(es): break
        c = es[i + 3]
        if c == 0x00: out.append((i, 'IPB'[((es[i + 5] >> 3) & 7) - 1]))
        elif c == 0xb8: out.append((i, 'G'))
        elif c == 0xb3: out.append((i, 'S'))
        i += 3
    return out


def zero_to_padding(d):
    """페이로드가 전부 0인 비디오 PES를 같은 길이의 패딩 패킷(0xBE, 0xFF 채움)으로 바꾼다."""
    d = bytearray(d); n = 0
    for s, L, sid in pes_list(d):
        if sid != 0xe0 or any(d[s:s + L]): continue
        i = d.rfind(b'\x00\x00\x01\xe0', 0, s)
        tot = struct.unpack('>H', d[i + 4:i + 6])[0]
        d[i + 3] = 0xbe; d[i + 6:i + 6 + tot] = b'\xff' * tot; n += 1
    return bytes(d), n
