#include "server.h"

int createServerSocket() {
    int serverSocket = socket(AF_INET, SOCK_DGRAM, 0);
    if (serverSocket < 0) {
        perror("Socket creation failed");
        exit(EXIT_FAILURE);
    }
    return serverSocket;
}

void bindSocket(int serverSocket, struct sockaddr_in *serverAddress) {
    if (bind(serverSocket, (const struct sockaddr *)serverAddress, sizeof(*serverAddress)) < 0) {
        perror("Error while binding socket");
        exit(EXIT_FAILURE);
    }
    printf("Server is listening on port %d\n", ntohs(serverAddress->sin_port));
}

void processReceivedData(int serverSocket, struct sockaddr_in *clientAddress) {
    int clientAddressLen = sizeof(*clientAddress);
    char buffer[MAX_BUFFER];
    const char *responseMessage = "Message received\n";
    int receivedBytes;

    while (1) {
        receivedBytes = recvfrom(serverSocket, (char *)buffer, MAX_BUFFER, MSG_WAITALL,
                                 (struct sockaddr *)clientAddress, &clientAddressLen);
        buffer[receivedBytes] = '\0';
        printf("Packet received: %s\n", buffer);

        sendto(serverSocket, responseMessage, strlen(responseMessage), MSG_CONFIRM,
               (const struct sockaddr *)clientAddress, clientAddressLen);
    }
}

int main() {
    const char *serverAddress = DEFAULT_ADDR;
    int serverPort = DEFAULT_PORT;

    printf("Server IP: %s:%d\n", serverAddress, serverPort);

    int serverSocket;
    struct sockaddr_in serverAddressStruct, clientAddressStruct;

    serverSocket = createServerSocket();

    memset(&serverAddressStruct, 0, sizeof(serverAddressStruct));
    memset(&clientAddressStruct, 0, sizeof(clientAddressStruct));

    serverAddressStruct.sin_family = AF_INET;
    serverAddressStruct.sin_addr.s_addr = inet_addr(serverAddress);
    serverAddressStruct.sin_port = htons(serverPort);

    bindSocket(serverSocket, &serverAddressStruct);

    processReceivedData(serverSocket, &clientAddressStruct);

    return 0;
}
