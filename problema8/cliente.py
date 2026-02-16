import socket
import threading

HOST = "localhost"
PORT = 7000
BUFFER = 1024


def receive(sock):
    while True:
        try:
            msg = sock.recv(BUFFER).decode()
            if not msg:
                break
            print(msg)
        except:
            break


def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    threading.Thread(target=receive, args=(client,), daemon=True).start()

    while True:
        msg = input()
        client.send(msg.encode())


if __name__ == "__main__":
    start_client()
