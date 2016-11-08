CC=gcc
CFLAGS=-O2 -g
zqqlib.so: zqqlib.c zqqlib.h
	${CC} ${CFLAGS} -shared -fPIC zqqlib.c -I/usr/include/python2.6 -I./ -o zqqlib.so
clean:
	rm zqqlib.so 
