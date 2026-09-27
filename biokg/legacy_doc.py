import olefile,struct,sys
def extract(path):
    ole=olefile.OleFileIO(path)
    wd=ole.openstream('WordDocument').read()
    flags=struct.unpack_from('<H',wd,0xA)[0]
    tbl=ole.openstream('1Table' if flags&0x200 else '0Table').read()
    # FibRgFcLcb97: fcClx at index 33 (fc,lcb pairs) starting after csw/rgW/cslw/rgLw/cbRgFcLcb
    pos=32; csw=struct.unpack_from('<H',wd,pos)[0]; pos+=2+csw*2
    cslw=struct.unpack_from('<H',wd,pos)[0]; pos+=2+cslw*4
    pos+=2
    fcClx,lcbClx=struct.unpack_from('<II',wd,pos+33*8)
    clx=tbl[fcClx:fcClx+lcbClx]; i=0
    while clx[i]==1:
        cb=struct.unpack_from('<H',clx,i+1)[0]; i+=3+cb
    assert clx[i]==2; lcb=struct.unpack_from('<I',clx,i+1)[0]; plc=clx[i+5:i+5+lcb]
    n=(lcb-4)//12; cps=struct.unpack_from('<%dI'%(n+1),plc,0); out=[]
    for k in range(n):
        pcd=plc[(n+1)*4+k*8:(n+1)*4+k*8+8]; fc=struct.unpack_from('<I',pcd,2)[0]
        ln=cps[k+1]-cps[k]
        if fc&0x40000000:
            off=(fc&0x3FFFFFFF)//2; out.append(wd[off:off+ln].decode('cp1252',errors='replace'))
        else: out.append(wd[fc:fc+2*ln].decode('utf-16le',errors='replace'))
    return ''.join(out)
t=extract(sys.argv[1]).replace('\r','\n').replace('\x07','\t|')
open(sys.argv[2],'w').write(t)
