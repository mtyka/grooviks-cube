VERSION = 4.32.03
FMODLIBDIR     = fmodapi/lib/
FMODINCDIR     = fmodapi/inc/
CONTENTDIR     = ../../audio/Grooviks Build Directory/

grooviksaudio: grooviksaudio.o
	gcc -o grooviksaudio.so grooviksaudio.o -L../fmodapi/lib -lfmodevent64  -lfmodex64 -pthread -shared
	
grooviksaudio.o: grooviksaudio.c
	gcc -O3 -fPIC -c grooviksaudio.c 
run:
	./grooviksaudio

clean:
	@rm -f *.o
	@rm -f grooviksaudio.so
	@rm -f libfmodevent64.so
	@rm -f libfmodex64.so
