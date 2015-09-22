CC = clang
CFLAGS = -Wall -ggdb -O0 -std=c99 -fno-stack-protector -Wl,-z,execstack

.PHONY: all clean

all: main payload.bin

main: main.c
	$(CC) $(CFLAGS) -o main main.c

payload.bin: payload.asm
	yasm -f bin -o payload.bin payload.asm

clean:
	rm -f main payload.bin
