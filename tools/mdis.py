import capstone,struct,sys
md=capstone.Cs(capstone.CS_ARCH_MIPS,capstone.CS_MODE_MIPS64|capstone.CS_MODE_LITTLE_ENDIAN); md.skipdata=True
def load(which):
    if which=='elf': return open('work/ext/SLPM_652.60','rb').read()[0x100:0x100+0x63980],0x100000
    return open('work/ext/GAIKA.BIN','rb').read(),0x22a100
def dis(which,a,n):
    d,b=load(which)
    for i in md.disasm(d[a-b:a-b+4*n],a): print('%x: %08x  %s %s'%(i.address,struct.unpack_from('<I',d,i.address-b)[0],i.mnemonic,i.op_str))
def xref(which,target):
    d,b=load(which); w=struct.unpack('<%dI'%(len(d)//4),d[:len(d)//4*4]); out=[]
    for k,x in enumerate(w):
        if x>>26 in (2,3) and ((x&0x3ffffff)<<2)==target: out.append(b+4*k)
    return out
if __name__=='__main__':
    if sys.argv[1]=='x': print([hex(x) for x in xref(sys.argv[2],int(sys.argv[3],16))])
    else: dis(sys.argv[1],int(sys.argv[2],16),int(sys.argv[3]))
