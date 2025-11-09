#ifndef SERVER_UDP_H
#define SERVER_UDP_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netinet/in.h>

#define MAX_BUFFER 1024
#define DEFAULT_PORT 8000
#define DEFAULT_ADDR "127.0.0.1"

int  createServerSocket();
void bindSocket(int serverSocket, struct sockaddr_in *serverAddress);
void processReceivedData(int serverSocket, struct sockaddr_in *clientAddress);

#endif

