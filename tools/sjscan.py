import sys,re
def scan(d,minc=2):
    out=[];i=0;n=len(d)
    while i<n:
        j=i;c=0
        while j<n:
            b=d[j]
            if 0x81<=b<=0x9f or 0xe0<=b<=0xfc:
                if j+1<n and 0x40<=d[j+1]<=0xfc and d[j+1]!=0x7f: j+=2;c+=1;continue
                break
            elif b in (0x0a,) or 0x20<=b<0x7f: j+=1;continue
            break
        if c>=minc: out.append((i,d[i:j]));i=j
        else: i=max(j,i+1) if c==0 else i+1
    return out
if __name__=='__main__':
    for f in sys.argv[1:]:
        r=scan(open(f,'rb').read())
        print(f,len(r),sum(len(x) for _,x in r))
