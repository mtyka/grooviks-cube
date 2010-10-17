VERSION = 4.32.03
FMODLIBDIR     = ../fmodapi/lib
FMODINCDIR     = ../fmodapi/inc
CONTENTDIR     = ../../audio/Grooviks Build Directory/

test_app: test.o
	gcc -o test_app test.o ${FMODLIBDIR}/libfmodevent64.so ${FMODLIBDIR}/libfmodex64.so -pthread -Wl,-rpath ${FMODLIBDIR}
	
test.o:
	gcc -O3 -c test.c 
run:
	./test_app

clean:
	rm *.o
	rm test_app
