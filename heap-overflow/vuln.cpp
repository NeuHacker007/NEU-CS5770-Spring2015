#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <iostream>

struct MsgHdr {
    size_t len_;
    size_t opts_len_;
};

int RecvMsg(int sk) {
    MsgHdr hdr;
    memset(&hdr, 0, sizeof(hdr));
    read(sk, &hdr.len_, 2);
    read(sk, &hdr.opts_len_, 2);
    char* msg = reinterpret_cast<char*>(malloc(hdr.len_));
    char* msg_opts = reinterpret_cast<char*>(malloc(hdr.opts_len_));

    char* ptr = msg;
    while (1) {
        char c;
        auto n = read(sk, &c, 1);
        if (n < 1 || c == '\n')
            break;
        *ptr++ = c;
    }

    free(msg);

    return 0;
}

int main(int argc, char** argv) {
    return RecvMsg(0);
}
