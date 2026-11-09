import struct, numpy as np
def _clut_unswz(c):
    # CSM1 8bpp: 32-entry blocks swap middle 8s
    c=c.copy().reshape(-1,32,4)
    t=c[:,8:16].copy(); c[:,8:16]=c[:,16:24]; c[:,16:24]=t
    return c.reshape(-1,4)
def parse(d):
    assert d[:4]==b'TIM2'
    n=struct.unpack_from('<H',d,6)[0]; o=0x80 if d[5]&1 else 16; pics=[]
    for k in range(n):
        tot,cl,im,hs,cc,fmt,mip,ctype,itype,w,h=struct.unpack_from('<IIIHHBBBBHH',d,o)
        p=dict(off=o,tot=tot,clut=cl,img=im,hs=hs,cc=cc,ctype=ctype,itype=itype,w=w,h=h,mip=mip)
        p['gs']=d[o+0x18:o+0x30]
        p['img_off']=o+hs; p['clut_off']=o+hs+im
        pics.append(p); o+=tot
    return pics
def decode(d,p):
    w,h=p['w'],p['h']; it=p['itype']; raw=d[p['img_off']:p['img_off']+p['img']]
    def col(cl):
        ct=p['ctype']&0x3f
        if ct==3: a=np.frombuffer(cl,np.uint8).reshape(-1,4).copy()
        elif ct==2: a=np.frombuffer(cl,np.uint8).reshape(-1,3); a=np.concatenate([a,np.full((len(a),1),0x80,np.uint8)],1)
        else:
            v=np.frombuffer(cl,'<u2').astype(np.uint32)
            a=np.stack([(v&31)<<3,((v>>5)&31)<<3,((v>>10)&31)<<3,np.where(v&0x8000,0x80,0)],1).astype(np.uint8)
        return a
    if it==5:
        idx=np.frombuffer(raw,np.uint8)[:w*h]
        cl=col(d[p['clut_off']:p['clut_off']+p['clut']])
        if not (p['ctype']&0x80) and len(cl)>=256: cl=_clut_unswz(cl[:256])
        rgba=cl[idx].reshape(h,w,4)
    elif it==4:
        b=np.frombuffer(raw,np.uint8)[:w*h//2]; idx=np.empty(len(b)*2,np.uint8); idx[0::2]=b&15; idx[1::2]=b>>4
        cl=col(d[p['clut_off']:p['clut_off']+p['clut']]); rgba=cl[idx].reshape(h,w,4)
    elif it==3: rgba=np.frombuffer(raw,np.uint8)[:w*h*4].reshape(h,w,4).copy()
    elif it==2:
        a=np.frombuffer(raw,np.uint8)[:w*h*3].reshape(h,w,3); rgba=np.concatenate([a,np.full((h,w,1),0x80,np.uint8)],2)
    elif it==1:
        v=np.frombuffer(raw,'<u2')[:w*h].astype(np.uint32)
        rgba=np.stack([(v&31)<<3,((v>>5)&31)<<3,((v>>10)&31)<<3,np.where(v&0x8000,0x80,0)],1).astype(np.uint8).reshape(h,w,4)
    else: raise ValueError(it)
    out=rgba.astype(np.uint16); out[...,3]=np.minimum(out[...,3]*2,255)
    return out.astype(np.uint8)
