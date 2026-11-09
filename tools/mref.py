import struct
def refs(code, base, targets):
    """lui/addiu(ori) 쌍으로 만든 주소 참조 찾기. returns {target:[(lui_idx_off, lo_off)]}"""
    n=len(code)//4; w=struct.unpack('<%dI'%n,code[:n*4]); ts=set(targets); out={}
    hi={}
    for i,x in enumerate(w):
        op=x>>26
        if op==0x0f: hi[(x>>16)&31]=(i,(x&0xffff)<<16)
        elif op in (0x09,0x0d,0x23,0x21,0x25,0x20,0x24,0x2b,0x29,0x28) :
            rs=(x>>21)&31
            if rs in hi:
                li,h=hi[rs]
                if i-li>64: continue
                imm=x&0xffff
                a=(h+ (imm-0x10000 if imm>=0x8000 and op!=0x0d else imm))&0xffffffff
                if a in ts: out.setdefault(a,[]).append((li*4,i*4))
    return out
