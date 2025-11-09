FROM docker.io/library/gcc:13
WORKDIR /app
COPY server.c server.h ./
RUN gcc -O2 -Wall -Wextra -o server server.c
EXPOSE 8000/udp
ENTRYPOINT ["./server"]
CMD ["0.0.0.0","8000"]
