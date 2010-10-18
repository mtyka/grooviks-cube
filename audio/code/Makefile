VERSION = 4.32.03
FMODLIBDIR     = ../fmodapi/lib
FMODINCDIR     = ../fmodapi/inc
CONTENTDIR     = ../../audio/Grooviks Build Directory/

.PHONY: grooviksaudio
grooviksaudio: 
	make -C  grooviksaudio
	cp grooviksaudio/*.so .
	cp -r ../build media/
	
run:
	./grooviksaudio

clean:
	make -C grooviksaudio clean
	rm -f grooviksaudio.so
	rm -fr media
	
