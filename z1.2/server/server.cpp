
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>

#include <cstdint>
#include <cstdio>
#include <cstring>
#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <chrono>
#include <iomanip>
#include <openssl/sha.h>
#include <sstream>

int main(int argc, char** argv){
    if (argc < 2){
        std::cerr<<"Usage: "<<argv[0]<<" <port>\n";
        return 1;
    }
    int port = atoi(argv[1]);

    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0){ perror("socket"); return 1; }

    sockaddr_in serv{};
    serv.sin_family = AF_INET;
    serv.sin_port = htons(port);
    serv.sin_addr.s_addr = INADDR_ANY;

    if (bind(sock, (sockaddr*)&serv, sizeof(serv))<0){
        perror("bind");
        return 1;
    }

    std::cout<<"Server listening on UDP port "<<port<<"...\n";

    uint32_t total_packets = 0;
    uint32_t file_size = 0;
    bool have_control = false;
    std::vector<std::vector<uint8_t>> parts;
    std::vector<char> received_flag;
    uint32_t packets_received = 0;

    const size_t MAX_PACKET = 1500;
    std::vector<uint8_t> buf(MAX_PACKET);

    sockaddr_in cli{};
    socklen_t cli_len = sizeof(cli);

    timeval tv;
    tv.tv_sec = 5;
    tv.tv_usec = 0;
    setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));

    while (true){
        ssize_t n = recvfrom(sock, buf.data(), buf.size(), 0, (sockaddr*)&cli, &cli_len);

        if (n < 0){
            if (errno == EAGAIN || errno == EWOULDBLOCK){
                if (have_control && packets_received == total_packets && total_packets > 0){
                    std::cout<<"All packets received.\n";

                    std::ofstream of("received.bin", std::ios::binary);

                    SHA256_CTX ctx;
                    SHA256_Init(&ctx);

                    for (uint32_t i = 0; i < total_packets; i++){
                        of.write((char*)parts[i].data(), parts[i].size());
                        SHA256_Update(&ctx, parts[i].data(), parts[i].size());
                    }
                    of.close();

                    unsigned char digest[SHA256_DIGEST_LENGTH];
                    SHA256_Final(digest, &ctx);

                    std::ostringstream oss;
                    oss << std::hex << std::setfill('0');
                    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++){
                        oss << std::setw(2) << (int)digest[i];
                    }

                    std::cout<<"Server SHA-256: "<<oss.str()<<"\n";

                    uint8_t fend[2] = {3, 1};
                    sendto(sock, fend, 2, 0, (sockaddr*)&cli, cli_len);

                    have_control = false;
                    total_packets = 0;
                    file_size = 0;
                    packets_received = 0;
                    parts.clear();
                    received_flag.clear();

                    continue;
                }
                continue;
            } else {
                perror("recvfrom");
                break;
            }
        }

        if (n < 1) continue;

        uint8_t type = buf[0];


        if (type == 0){
            if (n < 1 + 8){
                std::cerr<<"Bad control packet\n";
                continue;
            }

            uint32_t tp, fs;
            memcpy(&tp, buf.data()+1, 4);
            memcpy(&fs, buf.data()+5, 4);

            tp = ntohl(tp);
            fs = ntohl(fs);

            total_packets = tp;
            file_size = fs;

            std::cout<<"CONTROL received: total_packets="<<total_packets
                     <<", file_size="<<file_size<<"\n";

            parts.assign(total_packets, std::vector<uint8_t>());
            received_flag.assign(total_packets, 0);
            packets_received = 0;
            have_control = true;

            uint8_t reply[2] = {0,1};
            sendto(sock, reply, 2, 0, (sockaddr*)&cli, cli_len);
            continue;
        }


        if (type == 1){
            if (!have_control) continue;
            if (n < 1 + 4 + 2) continue;

            uint32_t seq;
            uint16_t plen;

            memcpy(&seq, buf.data()+1, 4);
            memcpy(&plen, buf.data()+5, 2);

            seq = ntohl(seq);
            plen = ntohs(plen);

            if (seq >= total_packets) continue;

            if (plen > 100) plen = 100;

            if (!received_flag[seq]){
                parts[seq].assign(buf.begin() + 7, buf.begin() + 7 + plen);
                received_flag[seq] = 1;
                packets_received++;

                if (packets_received % 50 == 0 ||
                    packets_received == total_packets)
                {
                    std::cout<<"Received packets: " << packets_received
                             << "/" << total_packets << "\n";
                }
            }

            uint8_t ack[5];
            ack[0] = 2;
            uint32_t seqn = htonl(seq);
            memcpy(ack+1, &seqn, 4);
            sendto(sock, ack, 5, 0, (sockaddr*)&cli, cli_len);
            continue;
        }
    }

    close(sock);
    return 0;
}
