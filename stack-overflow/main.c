#include <stdio.h>
#include <string.h>

int f(char* input) {
	char buf[256];
	strcpy(buf, input);
	printf("%s\n", buf);
	return 0;
}

int main(int argc, char** argv) {
    return f(argv[1]);
}
