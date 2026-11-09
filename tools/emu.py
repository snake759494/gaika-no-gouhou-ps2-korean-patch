"""검증 전용: 휴대용 PCSX2(work/emu/pcsx2-gaika.exe)를 최소화·비활성으로 실행, PINE(28431)으로 가상 패드·상태저장 스크린샷.
가상 패드: scePadRead 호출(0x136650)을 코드케이브로 돌려, 읽은 버튼(+2, active low)에서 VPAD 비트를 끈다.
버튼: SELECT=1 L3=2 R3=4 START=8 U=0x10 R=0x20 D=0x40 L=0x80 L2=0x100 R2=0x200 L1=0x400 R1=0x800 T=0x1000 O=0x2000 X=0x4000 S=0x8000"""
import subprocess, sys, os, time, glob, zipfile, struct, ctypes, socket
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMU = os.path.join(R, 'work', 'emu'); EXE = os.path.join(EMU, 'pcsx2-gaika.exe'); PORT = 28431
VPAD = 0x000ff000; DBG = 0x000ff008; CAVE = 0x000ff100; CALL = 0x136650; PADREAD = 0x124b90
BTN = dict(SELECT=1, L3=2, R3=4, START=8, U=0x10, R=0x20, D=0x40, L=0x80, L2=0x100, R2=0x200, L1=0x400, R1=0x800,
           T=0x1000, O=0x2000, X=0x4000, S=0x8000)
def j(a, link=False): return ((3 if link else 2) << 26) | ((a >> 2) & 0x3ffffff)
def section():
    hi = lambda a: (a + 0x8000) >> 16
    lo = lambda a: a & 0xffff
    code = [0x27bdfff0, 0xffbf0000,
            0x3c010000 | hi(DBG), 0xac260000 | lo(DBG),            # sw a2,DBG
            j(PADREAD, True), 0,
            0x3c010000 | hi(VPAD), 0x8c210000 | lo(VPAD),          # lw at,VPAD
            0x3c090000 | hi(DBG), 0x8d290000 | lo(DBG),            # lw t1,DBG
            0x95280002,                                            # lhu t0,2(t1)
            0x00200827, 0x01014024, 0xa5280002,                    # nor at; and t0; sh t0,2(t1)
            0xdfbf0000, 0x03e00008, 0x27bd0010]
    out = ['gametitle=GAIKA (QA vpad)']
    out += ['patch=1,EE,%08x,word,%08x' % (CAVE + 4 * i, c) for i, c in enumerate(code)]
    out += ['patch=1,EE,%08x,word,%08x' % (CALL, j(CAVE, True))]
    return '\n'.join(out) + '\n'
def elf_crc(iso):
    import pycdlib
    i = pycdlib.PyCdlib(); i.open(iso); r = i.get_record(iso_path='/SLPM_652.60;1')
    with open(iso, 'rb') as f: f.seek(r.extent_location() * 2048); d = f.read(r.data_length)
    i.close(); c = 0
    for (x,) in struct.iter_unpack('<I', d[:len(d) // 4 * 4]): c ^= x
    return c
def launch(iso, state=None):
    stop(); crc = elf_crc(iso)
    for f in glob.glob(os.path.join(EMU, 'cheats', '*.pnach')): os.remove(f)
    open(os.path.join(EMU, 'cheats', '%08X.pnach' % crc), 'w').write(section())
    si = subprocess.STARTUPINFO(); si.dwFlags = 1; si.wShowWindow = 7   # SW_SHOWMINNOACTIVE
    args = [EXE, '-batch', '-nogui']
    if state: args += ['-statefile', state]
    p = subprocess.Popen(args + ['--', os.path.abspath(iso)], cwd=EMU, startupinfo=si)
    print('pid', p.pid, 'crc %08X' % crc); hide(p.pid)
def hide(pid):
    u = ctypes.windll.user32
    for _ in range(150):
        hs = []
        @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        def cb(h, l):
            pp = ctypes.c_ulong(); u.GetWindowThreadProcessId(ctypes.c_void_p(h), ctypes.byref(pp))
            if pp.value == pid and u.IsWindowVisible(ctypes.c_void_p(h)): hs.append(h)
            return True
        u.EnumWindows(cb, 0)
        if hs:
            time.sleep(1.0)
            for h in hs: u.ShowWindow(ctypes.c_void_p(h), 7)
            return
        time.sleep(0.2)
def stop():
    subprocess.run(['taskkill', '/F', '/IM', 'pcsx2-gaika.exe'], capture_output=True)
def pine(payload):
    s = socket.create_connection(('127.0.0.1', PORT), timeout=10)
    s.sendall(struct.pack('<I', len(payload) + 4) + payload)
    def rv(n):
        b = b''
        while len(b) < n:
            c = s.recv(n - len(b))
            if not c: raise EOFError
            b += c
        return b
    n = struct.unpack('<I', rv(4))[0]; body = rv(n - 4); s.close(); return body
def w32(a, v): return pine(struct.pack('<BII', 6, a, v))
def r32(a): return struct.unpack_from('<I', pine(struct.pack('<BI', 2, a)), 1)[0]
def press(names, ms=250):
    m = 0
    for n in names.split('+'): m |= BTN[n]
    w32(VPAD, m); time.sleep(ms / 1000); w32(VPAD, 0); time.sleep(0.2)
def member(p, name):
    import zstandard
    with zipfile.ZipFile(p) as z: i = z.getinfo(name)
    with open(p, 'rb') as f:
        f.seek(i.header_offset); h = f.read(30); n, e = struct.unpack_from('<HH', h, 26); f.seek(n + e, 1)
        raw = f.read(i.compress_size)
    if i.compress_type == 0: return raw
    if i.compress_type == 93: return zstandard.ZstdDecompressor().decompress(raw, max_output_size=i.file_size)
    with zipfile.ZipFile(p) as z: return z.read(name)
def latest():
    ps = glob.glob(os.path.join(EMU, 'sstates', '*.p2s'))
    return max(ps, key=os.path.getmtime) if ps else None
def snap(tag, slot=9):
    old = latest(); t = os.path.getmtime(old) if old else 0
    pine(struct.pack('<BB', 9, slot))
    for _ in range(300):
        p = latest()
        if p and os.path.getmtime(p) > t: time.sleep(1.0); break
        time.sleep(0.1)
    os.makedirs(os.path.join(R, 'work', 'shots'), exist_ok=True)
    out = os.path.join(R, 'work', 'shots', '%s.png' % tag)
    open(out, 'wb').write(member(p, 'Screenshot.png')); print(out)
if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'launch': launch(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif c == 'stop': stop()
    elif c == 'snap': snap(sys.argv[2])
    elif c == 'press':
        for k in sys.argv[2:]:
            try: time.sleep(float(k))
            except ValueError: press(k)
    elif c == 'save': print(pine(struct.pack('<BB', 9, int(sys.argv[2]))))
    elif c == 'load': print(pine(struct.pack('<BB', 0xa, int(sys.argv[2]))))
    elif c == 'r32': print(hex(r32(int(sys.argv[2], 16))))
    elif c == 'rd':
        a = int(sys.argv[2], 16); print(' '.join('%08x' % r32(a + 4 * k) for k in range(int(sys.argv[3]))))
