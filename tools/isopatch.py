"""ISO9660 제자리 패치: 파일 데이터 덮어쓰기/재배치(디렉터리 레코드 LBA·크기 갱신)."""
import struct
SEC = 2048


class Iso:
    def __init__(self, path):
        self.f = open(path, 'r+b')
        pvd = self.read(16, 1)
        assert pvd[1:6] == b'CD001'
        self.root = struct.unpack_from('<I', pvd, 156 + 2)[0], struct.unpack_from('<I', pvd, 156 + 10)[0]

    def read(self, lba, n):
        self.f.seek(lba * SEC); return self.f.read(n * SEC)

    def _dir(self, lba, size):
        d = self.read(lba, (size + SEC - 1) // SEC); o = 0; out = []
        while o < len(d):
            l = d[o]
            if l == 0: o = (o // SEC + 1) * SEC; continue
            nl = d[o + 32]; name = d[o + 33:o + 33 + nl]
            ext, sz = struct.unpack_from('<I', d, o + 2)[0], struct.unpack_from('<I', d, o + 10)[0]
            out.append((name, lba * SEC + o, ext, sz, d[o + 25]))
            o += l
        return out

    def find(self, path):
        lba, size = self.root
        parts = path.strip('/').split('/')
        for k, p in enumerate(parts):
            for name, pos, ext, sz, fl in self._dir(lba, size):
                n = name.decode('latin1').split(';')[0]
                if n.upper() == p.upper():
                    if k == len(parts) - 1: return pos, ext, sz
                    lba, size = ext, sz; break
            else: raise KeyError(path)

    def set_record(self, pos, lba, size):
        self.f.seek(pos + 2); self.f.write(struct.pack('<I', lba) + struct.pack('>I', lba) + struct.pack('<I', size) + struct.pack('>I', size))

    def write_at(self, lba, data):
        self.f.seek(lba * SEC); self.f.write(data)
        pad = (-len(data)) % SEC
        if pad: self.f.write(b'\0' * pad)

    def put(self, path, data, alloc):
        """같은 자리에 들어가면 제자리, 아니면 alloc()에서 받은 LBA로 옮김."""
        pos, ext, sz = self.find(path)
        if (len(data) + SEC - 1) // SEC <= (sz + SEC - 1) // SEC: lba = ext
        else: lba = alloc((len(data) + SEC - 1) // SEC)
        self.write_at(lba, data); self.set_record(pos, lba, len(data))
        return lba

    def close(self): self.f.close()
