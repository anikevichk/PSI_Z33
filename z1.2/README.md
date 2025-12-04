## Opis projektu

Repozytorium zawiera implementację niezawodnej transmisji pliku przez UDP w konfiguracji:

- **klient:** Python
- **serwer:** C

Klient dzieli plik 10 000 B na fragmenty po 100 B, wysyła je do serwera, a serwer potwierdza każdy fragment, odbudowuje cały plik i oblicza jego hash SHA-256. Mechanizm ACK i retransmisji kompensuje utratę pakietów. Po zakończeniu transmisji hashe klienta i serwera są porównywane.

### Jak uruchomić projekt

W głównym katalogu repozytorium:

```bash
chmod +x run.sh
./run.sh
```

Skrypt automatycznie:

1. Buduje obrazy Dockera (klienta i serwera)
2. Uruchamia kontenery
3. Wykonuje transmisję pliku.
4. Pobiera z logów oba hashe i wyświetla wynik:
```bash
RESULT: MATCH / NO MATCH
```

## Wymagania

- Docker
- Python
