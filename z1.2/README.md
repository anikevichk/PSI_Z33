## Opis projektu

Repozytorium zawiera implementację komunikacji typu **UDP klient–serwer** w konfiguracji:

- **klient:** Python
- **serwer:** C

Klient wysyła datagramy UDP o rosnącej wielkości (2, 4, 8, …, 65507 B), mierzy czas RTT,binarnie szuka wartość granicy oraz zapisuje wyniki do pliku CSV. Serwer pełni rolę **echo servera**, zwracając dokładnie tę samą treść, którą otrzymał.

Dodatkowo projekt zawiera skrypt ułatwiający automatyczne uruchomienie obu kontenerów.

Projekt można uruchomić jednym poleceniem dzięki skryptowi `run.sh`.

### 1. Utworzenie sieci Docker

Skrypt zakłada istnienie sieci o nazwie:

```
z33_network
```

### 2. Automatyczne uruchomienie klienta i serwera

W głównym katalogu repozytorium:

```bash
chmod +x run.sh
./run.sh
```

Skrypt wykonuje kolejno:

1. Budowanie obrazu serwera i uruchomienie go w tle.
2. Krótkie oczekiwanie, aby serwer zdążył wystartować.
3. Budowanie obrazu klienta i uruchomienie go w trybie interaktywnym.
4. Zatrzymanie kontenera serwera po zakończeniu testów.

Wyniki zapisywane są w katalogu `client` jako:

`rezults.csv` — surowe pomiary RTT

### Komunikaty serwera

Komunikaty serwera można zobaczyć za pomocą polecenia:

```
docker logs z33_server
```

## Wymagania

- Docker
- Python
