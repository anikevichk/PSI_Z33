#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netinet/in.h>

#define MAX_DGRAM 65536
#define HOST_ADDRESS "0.0.0.0"
#define PORT_NUMBER 8000

int main(int argc, char **argv) {
    setbuf(stdout, NULL);

    unsigned char receiveBuffer[MAX_DGRAM];

    const char *hostAddress = HOST_ADDRESS;
    int portNumber = PORT_NUMBER;

    int serverSocket = socket(AF_INET, SOCK_DGRAM, 0);
    if (serverSocket < 0) { perror("socket"); return 1; }

    struct sockaddr_in serverAddress;

    memset(&serverAddress, 0, sizeof serverAddress);
    serverAddress.sin_family = AF_INET;
    serverAddress.sin_port   = htons(portNumber);

    if (inet_pton(AF_INET, hostAddress, &serverAddress.sin_addr) != 1) {
        fprintf(stderr, "Bad host: %s\n", hostAddress); return 1;
    }

    if (bind(serverSocket, (struct sockaddr*)&serverAddress, sizeof serverAddress) < 0) {
        perror("bind"); return 1;
    }

    printf("UDP echo listening on %s:%d\n", hostAddress, portNumber);


    while (1) {
        struct sockaddr_in clientAddress;
        socklen_t clientAddressLength = sizeof clientAddress;

        ssize_t receivedBytes = recvfrom(serverSocket, receiveBuffer, sizeof receiveBuffer, 0, (struct sockaddr*)&clientAddress, &clientAddressLength);
        if (receivedBytes < 0) {
            perror("recvfrom");
            continue;
        }

        printf("Received %zd bytes from client\n", receivedBytes);

        if (sendto(serverSocket, receiveBuffer, (size_t)receivedBytes, 0, (struct sockaddr*)&clientAddress, clientAddressLength) < 0) {
            perror("sendto");
        } else {
            printf("Sent %zd bytes back to client\n", receivedBytes);
        }
    }

    close(serverSocket);
    return 0;
}
