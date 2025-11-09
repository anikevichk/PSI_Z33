#!/bin/bash
set -e

#budowanie obrazu serwera
docker build -q -t server ./server

#uruchomienie serwera w tle
docker run -d --rm --replace -p 8000:8000/udp --name udp-server server

sleep 1

#uruchomienie klienta
cd client
python3 client.py 127.0.0.1 8000

#tworzenie wykresu
python3 plot_rezult.py rezult.txt

#zatrzymanie serwera
docker stop udp-server

