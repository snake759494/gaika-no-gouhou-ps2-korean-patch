import struct,os
NAMES=['IMG','MAPDATA','MSG','RFIGHT','SCN','SE','SYS']
def read_inf(p):
    d=open(p,'rb').read(); r={}
    for k,nm in enumerate(NAMES):
        n,o=struct.unpack_from('<II',d,0x10+8*k)
        r[nm]=[list(struct.unpack_from('<4HII',d,o+16*j)) for j in range(n)]
    return d,r
def unpack(inf,arcdir,out,names):
    _,r=read_inf(inf)
    for nm in names:
        a=open(os.path.join(arcdir,nm+'.ARC'),'rb').read(); os.makedirs(os.path.join(out,nm),exist_ok=True)
        for j,e in enumerate(r[nm]):
            open(os.path.join(out,nm,'%04d.bin'%j),'wb').write(a[e[5]:e[5]+e[4]])
if __name__=='__main__':
    unpack('work/ext/ARC.INF','work/ext','work/arc',['MSG','SCN','SYS','MAPDATA'])
