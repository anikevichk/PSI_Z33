#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/wait.h>
#include <signal.h>

#define HOST_ADDRESS "0.0.0.0"
#define PORT_NUMBER 8000


unsigned long djb2(unsigned char* str){
    unsigned long hash = 5381;
    int c;

    while (c = *str++)
        hash = ((hash << 5) + hash) + c;

    return hash;
}

void KillZombies(){
    while(waitpid(-1, NULL, WNOHANG)>0){}
}

int main(){
    int serverSocket, newSocket;
    pid_t pid;
    struct sockaddr_in serverAddr;


    serverSocket = socket(AF_INET, SOCK_STREAM, 0);
    serverAddr.sin_addr.s_addr = INADDR_ANY;
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(PORT_NUMBER);


    bind(serverSocket,
        (struct sockaddr*)&serverAddr,
        sizeof(serverAddr));

    if (listen(serverSocket, 50) == 0){
        printf("Listening \n");
    }
    else{
        printf("Error\n");
    }

    signal(SIGCHLD, KillZombies);



    while (1) {
        struct sockaddr_in clientAddress;
        socklen_t clientAddressLength = sizeof clientAddress;

        newSocket = accept(serverSocket,
                    (struct sockaddr*)&clientAddress,
                    &clientAddressLength);


        pid = fork();

        if(pid == 0){
            close(serverSocket);
            unsigned char receiveBuffer[1024];
            ssize_t receivedBytes = recv(newSocket, receiveBuffer, sizeof receiveBuffer-1, 0);
            if(receivedBytes > 0){
                receiveBuffer[receivedBytes] = '\0';
            }
            unsigned long hash = djb2(receiveBuffer);
            send(newSocket, receiveBuffer, (size_t)receivedBytes, 0);
            exit(0);
        }
        else{
            close(newSocket);
            KillZombies();
        }
}
}