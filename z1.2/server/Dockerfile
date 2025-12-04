FROM gcc:12
RUN apt-get update && apt-get install -y openssl libssl-dev
COPY . /server
WORKDIR /server
RUN g++ -std=c++11 -O2 -o server server.cpp -lssl -lcrypto
CMD ["./server", "8888"]
