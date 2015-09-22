CC = clang
CXX = clang++
CFLAGS = -Wall -std=c99 -ggdb -O0 -pipe
CXXFLAGS = -Wall -std=c++11 -ggdb -O0 -pipe
LDFLAGS = -Wl,-z,execstack

.PHONY: all

all: vuln

vuln: vuln.o malloc.o payload.asm
	$(CXX) $(CXXFLAGS) -o vuln vuln.o malloc.o $(LDFLAGS)
	yasm -f bin -o payload.bin payload.asm

clean:
	rm -f *.o vuln payload.bin
