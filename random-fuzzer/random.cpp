#include <iostream>
#include <memory>
#include <random>
#include <string.h>

static int test_prog_main(int argc, char** argv) {
    if (argc < 2)
        return 1;

    char buf[65536];
    strcpy(buf, argv[1]);

    printf("DEBUG: argv[1]=\"%s\"\n", argv[1]);

    char* resp = (char*) malloc(*((size_t*) buf + 48));
    if (!memcmp(buf + 44, "asd", 3)) {
        free(resp);
    }

    printf("DEBUG: resp=\"%s\"\n", resp);
    free(resp);

    return 0;
}

int main(int argc, char** argv) {
    std::random_device dev;
    std::mt19937 rng(dev());
    std::uniform_int_distribution<> len_dist(0, 65535);
    std::uniform_int_distribution<> char_dist(1, 255);
    char data[65536];

    while (true) {
        auto len = len_dist(rng);
        for (auto i = 0u; i < len; i++) {
            data[i] = char_dist(rng);
        }

        data[len] = '\0';

        char *test_argv[] = {
            argv[0],
            data,
            nullptr,
        };

        fprintf(stderr, "# len=%u\n", len);
        test_prog_main(2, test_argv);
    }

    return 0;
}
