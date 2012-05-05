#!/usr/bin/env python3.2
f=open('01.png','rb')
def rf(f):
	fr=f.read(4)
	return fr 
i=10
while(i):
	print(rf(f))
	i=i-1
print("first end")
i=10
while(i):
	print("sec:",rf(f))
	i=i-1
