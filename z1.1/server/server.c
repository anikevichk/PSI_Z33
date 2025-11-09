#include "server.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netinet/in.h>

int main(int argc, char **argv){
    setbuf(stdout, NULL);
    const char *host = (argc > 1 ? argv[1] : "127.0.0.1");
    int          port = (argc > 2 ? atoi(argv[2]) : 8000);

    int s = socket(AF_INET, SOCK_DGRAM, 0);
    if (s < 0) { perror("socket"); return 1; }

    struct sockaddr_in sa;
    memset(&sa, 0, sizeof sa);
    sa.sin_family = AF_INET;
    sa.sin_port   = htons(port);
    if (inet_pton(AF_INET, host, &sa.sin_addr) != 1) {
        fprintf(stderr, "Bad host: %s\n", host); return 1;
    }
    if (bind(s, (struct sockaddr*)&sa, sizeof sa) < 0) {
        perror("bind"); return 1;
    }
    printf("UDP echo listening on %s:%d\n", host, port);

    unsigned char buf[MAX_DGRAM];
    while (Work()) {
        struct sockaddr_in cli; socklen_t clen = sizeof cli;
        ssize_t n = recvfrom(s, buf, sizeof buf, 0, (struct sockaddr*)&cli, &clen);
        if (n < 0) { perror("recvfrom"); continue; }
        if (sendto(s, buf, (size_t)n, 0, (struct sockaddr*)&cli, clen) < 0)
            perror("sendto");
    }
    close(s);
    return 0;
}
