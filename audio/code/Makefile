VERSION = 4.32.03
FMODLIBDIR     = ../fmodapi/lib
FMODINCDIR     = ../fmodapi/inc
CONTENTDIR     = ../../audio/Grooviks Build Directory/

.PHONY: grooviksaudio
grooviksaudio: 
	make -C  grooviksAudioEngine
	cp grooviksAudioEngine/*.so .
	cp -r ../build media/

clean:
	make -C grooviksAudioEngine clean
	rm -f grooviksaudio.so
	rm -fr media
	rm -f libfmodevent64.so
	rm -f libfmod64.so
	
