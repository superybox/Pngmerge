#!/usr/bin/env python3.2

import sys
import binascii
import struct
import io
import zlib

def png_header(fpng):
	header=fpng.read(8)
	print("png_header end")
def png_chunck(fpng):
	length,=struct.unpack(">I",fpng.read(4))
	name=fpng.read(4)
	data=fpng.read(length)
	if(name!=b'IEND'):
		crc,=struct.unpack(">i",fpng.read(4))
		crcc=crc&0xffffffff
		crcd=crcc&0xffffffff
		print('crc32={:#10x}'.format(crc))

		crc_=binascii.crc32(name)
		crc_=binascii.crc32(data,crc_)

		crc_z=zlib.crc32(name)
		crc_z=zlib.crc32(data,crc_z)

		print(crc,crcd,crcc,crc_,crc_z)

		if crcc!=crc_ or crcc!=crc_z:
			print("corrupt data crc:",crc,crc_,crc_z)
	else:
		crcc=0
	return name,data,crcc
def main():
	fpng=open("01.png","rb")
	png_header(fpng)
	while(1):
		name,data,crcc=png_chunck(fpng)
		print('name',name)
		if(name==b'IEND'):
			break

if __name__=="__main__":
	main()
