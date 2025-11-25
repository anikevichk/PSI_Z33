## Opis projektu

Repozytorium zawiera implementację komunikacji typu **TCP klient–serwer** w konfiguracji:

- **klient:** Python
- **serwer:** C

Klient nawiązuje połączenie TCP z serwerem, wysyła wiadomość tekstową, a serwer odsyła jej **hash** (funkcja `djb2`). Klient generuje kilka żądań **równolegle** z użyciem `ThreadPoolExecutor`, natomiast serwer obsługuje każde połączenie współbieżnie w osobnym procesie (`fork()`), sprzątając procesy potomne przy pomocy `waitpid(..., WNOHANG)` (obsługa `SIGCHLD`).

---

### 1. Utworzenie sieci Docker

Skrypt zakłada istnienie sieci o nazwie:

```
z33_network
```

---

### 2. Automatyczne uruchomienie klienta i serwera

W głównym katalogu repozytorium:

```bash
chmod +x run.sh
./run.sh
```

Skrypt wykonuje kolejno:

1. Budowanie obrazu serwera i uruchomienie go w tle.
2. Krótkie oczekiwanie, aby serwer zdążył wystartować.
3. Budowanie obrazu klienta i uruchomienie go (wysłanie kilku wiadomości).
4. Zatrzymanie kontenera serwera po zakończeniu działania klienta.

---

### Komunikaty serwera

Komunikaty serwera można podejrzeć poleceniem:

```bash
docker logs z33_server
```

---

## Wymagania

- Docker
- Python 3
