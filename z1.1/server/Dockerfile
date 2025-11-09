FROM gcc:4.9
WORKDIR /server
COPY . /server
RUN gcc -o server server.c server.h
CMD ["./server"]