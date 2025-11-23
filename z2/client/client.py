import socket
import threading
from concurrent.futures import ThreadPoolExecutor

HOST = "172.21.33.2"
PORT = 8000
messages = ["PSI", "Anikevich", "Katsyaryna", "Yedzeika", "Sofiya", "Ivashchenko", "Matvii"]

def send_request(message):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(message.encode('ascii'))
            data = s.recv(1024)
            print(f"Message: {message:<15} : Hash: {data.decode()}")
    except socket.timeout:
        print(f"Timeout occurred while trying to send message: '{message}'")

        

def main():
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(send_request, messages)

if __name__ == "__main__":
    print(f"Client will send to {HOST}:{PORT}")
    main()


