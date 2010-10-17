VERSION = 4.32.03
FMODLIBDIR     = ../fmodapi/lib
FMODINCDIR     = ../fmodapi/inc
CONTENTDIR     = ../../audio/Grooviks Build Directory/

grooviksaudio: grooviksaudio.o
	gcc -o grooviksaudio grooviksaudio.o ${FMODLIBDIR}/libfmodevent64.so ${FMODLIBDIR}/libfmodex64.so -pthread -Wl,-rpath ${FMODLIBDIR}
	
grooviksaudio.o:
	gcc -O3 -fPIC -c grooviksaudio.c 
run:
	./grooviksaudio

clean:
	rm *.o
	rm grooviksaudio
