#!/usr/bin/env python

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

"""
 pngmerge -- composing APNG from PNG images
 Copyright (C) 2009 Kengo Ichiki <kichiki@users.sourceforge.net>
 $Id: pngmerge.py,v 1.1 2009/03/25 05:25:59 kengo Exp $
"""

import sys
import binascii
import struct


def PNG_header_read (f):
    header = f.read(8)
    if header != b'\x89PNG\x0d\x0a\x1a\x0a':
        print('%s is not PNG file'%(filename))
        sys.exit()

def PNG_header_write (f):
    head = b'\x89PNG\x0d\x0a\x1a\x0a'
    f.write(head)


def PNG_chunk_read (f):
    length, = struct.unpack(">I", f.read(4))
    name   = f.read(4)
    data   = f.read(length)
    crc, = struct.unpack(">i", f.read(4))
    print('tag',crc)
    crc_ = binascii.crc32(name)
    crc_ = binascii.crc32(data, crc_)
    if crc&0xffffffff != crc_:
        print("corrupt data crc : ", crc, crc_)
        sys.exit()
    return (name, data, crc)

def PNG_chunk_write (f, name, data):
    crc = binascii.crc32(name)
    length = len(data)
    if length > 0:
        crc = binascii.crc32(data, crc)
    print('write',crc)
    #crc=~crc
    #crc=crc&0xffffffff
    #crc=~crc
    print('finish',crc)
    f.write(struct.pack(">I", length))
    f.write(name)
    if length > 0:
        f.write(data)
    f.write(struct.pack(">L", crc))



def PNG_IHDR_write (f, w, h, d, col, comp, filt, intl):
    name = b'IHDR'
    data = struct.pack(">IIbbbbb", w, h, d, col, comp, filt, intl)
    PNG_chunk_write (f, name, data)


def PNG_IHDR_parse (data):
    if len(data) != 13:
        print("IHDR : length %d != 13"%(len(data)))
        sys.exit()

    w, h, d, col, comp, filt, intl = struct.unpack(">IIbbbbb", data)
    return w, h, d, col, comp, filt, intl


def PNG_acTL_write (f, nf, np):
    name = b'acTL'
    data = struct.pack(">II", nf, np)
    PNG_chunk_write (f, name, data)

def PNG_acTL_parse (data):
    if len(data) != 8:
        print("acTL : length %d != 8"%(len(data)))
        sys.exit()

    nf, np = struct.unpack(">II", data)
    return nf, np


def PNG_fcTL_write (f, ns, w, h, x0, y0, dn, dd, dop, bop):
    name = b'fcTL'
    data = struct.pack(">IIIIIHHBB",
                       ns, w, h, x0, y0, dn, dd, dop, bop)
    PNG_chunk_write (f, name, data)

def PNG_fcTL_parse (data):
    if len(data) != 26:
        print("fcTL : length %d != 26"%(len(data)))
        sys.exit()

    ns, w, h, x0, y0, dn, dd, dop, bop = struct.unpack(">IIIIIHHBB", data)
    return ns, w, h, x0, y0, dn, dd, dop, bop


def PNG_fdAT_write (f, ns, data):
    name = b'fdAT'
    data_ = struct.pack(">I", ns) + data
    PNG_chunk_write (f, name, data_)



def usage():
    print('pngmerge -- composing APNG from PNG images')
    print('$Id: pngmerge.py,v 1.1 2009/03/25 05:25:59 kengo Exp $')
    print('USAGE: python pngmerge.py [options] file1 file2 ...')
    print('OPTIONS:')
    print('\t-o  : output file name')
    print('\t-np : number of plays (default: 0 for looping)')
    print('\t-dn : numerator   for delay time (default: 100)')
    print('\t-dd : denominator for delay time (default: 1000)')



def main():
    file_apng = ''
    file_pngs = []
    np = 0    # number of plays
    dn = 100  # numerator of delay 
    dd = 1000 # denominator of delay
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '-o':
            file_apng = sys.argv[i+1]
            i += 2
        elif sys.argv[i] == '-np':
            np = int(sys.argv[i+1])
            i += 2
        elif sys.argv[i] == '-dn':
            dn = int(sys.argv[i+1])
            i += 2
        elif sys.argv[i] == '-dd':
            dd = int(sys.argv[i+1])
            i += 2
        elif sys.argv[i] == '-h' or sys.argv[i] == '--help':
            usage()
            sys.exit()
        else:
            file_pngs.append(sys.argv[i])
            i += 1

    if file_apng == '' or file_pngs == []:
        usage()
        sys.exit()

    f_apng = open(file_apng, 'wb')

    nf = len(file_pngs) # number of frames

    dop = 1 # APNG_DISPOSE_OP_BACKGROUND
    bop = 0 # APNG_BLEND_OP_SOURCE

    PNG_header_write (f_apng)


    ns = 0  # number of sequence

    # first frame
    f_png = open(file_pngs[0], 'rb')
    PNG_header_read (f_png)

    w0 = 0
    h0 = 0
    d0 = 0
    col0 = 0
    comp0 = 0
    filt0 = 0
    intl0 = 0

    while 1:
        name, data, crc = PNG_chunk_read (f_png)
        print(name)
        if name == b'IEND':
            break
        elif name == b'IHDR':
            w0, h0, d0, col0, comp0, filt0, intl0 = PNG_IHDR_parse (data)
            PNG_IHDR_write (f_apng, w0, h0, d0, col0, comp0, filt0, intl0)
            # acTL
            PNG_acTL_write (f_apng, nf, np)
            # fcTL
            PNG_fcTL_write (f_apng, ns, w0, h0, 0, 0, dn, dd, dop, bop)
            ns += 1
        elif name == b'IDAT':
            # IDAT
            PNG_chunk_write (f_apng, name, data)

    f_png.close()


    # the following frames
    for i in range(1,len(file_pngs)):
        f_png = open(file_pngs[i], 'rb')
        PNG_header_read (f_png)

        while 1:
            name, data, crc = PNG_chunk_read (f_png)
            if name == b'IEND':
                break
            elif name == b'IHDR':
                w, h, d, col, comp, filt, intl = PNG_IHDR_parse (data)
                if w != w0 or h != h0 or d != d0 or col != col0 or comp != comp0 or filt != filt0 or intl != intl0:
                    print('something is wrong...')
                # fcTL
                PNG_fcTL_write (f_apng, ns, w0, h0, 0, 0, dn, dd, dop, bop)
                ns += 1
            elif name == b'IDAT':
                # fdAT
                PNG_fdAT_write (f_apng, ns, data)
                ns += 1

        f_png.close()

    # IEND
    name = b'IEND'
    data = b''
    PNG_chunk_write (f_apng, name, data)

    f_apng.close()

    sys.exit()


if __name__ == "__main__":
    main()
