import numpy as np
from PIL import Image
G=22; GB=242
def glyph(d,i):
    b=np.frombuffer(d[i*GB:(i+1)*GB],np.uint8)
    px=np.empty(GB*2,np.uint8); px[0::2]=b&15; px[1::2]=b>>4
    return px.reshape(G,G)
def sheet(d,start,n,cols=32,path='x.png'):
    rows=(n+cols-1)//cols; im=np.zeros((rows*(G+2),cols*(G+2)),np.uint8)
    for k in range(n):
        r,c=divmod(k,cols); im[r*(G+2):r*(G+2)+G,c*(G+2):c*(G+2)+G]=glyph(d,start+k)*17
    Image.fromarray(im).resize((im.shape[1]*2,im.shape[0]*2),Image.NEAREST).save(path)
