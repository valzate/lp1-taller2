import socket
import threading

BUFFER_SIZE = 4096
LISTEN_PORT = 8080

def handle_client(client_socket):
    try:
        # ==============================
        # 1️⃣ Recibir petición del cliente
        # ==============================
        request = client_socket.recv(BUFFER_SIZE)
        first_line = request.split(b'\n')[0]

        print("Petición recibida:")
        print(first_line.decode())

        # ==============================
        # 2️⃣ Manejo de HTTPS (CONNECT)
        # ==============================
        if b"CONNECT" in first_line:
            address = first_line.split()[1].decode()
            host, port = address.split(":")
            port = int(port)

            print(f"[HTTPS] Conectando a {host}:{port}")

            # Conectar al servidor destino
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((host, port))

            # Responder al cliente que el túnel está listo
            client_socket.send(b"HTTP/1.1 200 Connection established\r\n\r\n")

            # Reenvío bidireccional
            forward_data(client_socket, server_socket)

        else:
            # ==============================
            # 3️⃣ Manejo HTTP normal
            # ==============================
            host = None
            for line in request.split(b"\r\n"):
                if b"Host:" in line:
                    host = line.split(b":")[1].strip().decode()
                    break

            if host:
                print(f"[HTTP] Conectando a {host}:80")

                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.connect((host, 80))

                server_socket.send(request)

                forward_data(client_socket, server_socket)

    except Exception as e:
        print("Error:", e)

    finally:
        client_socket.close()


def forward_data(client_socket, server_socket):
    """
    Reenvío bidireccional entre cliente y servidor destino
    """

    def forward(source, destination):
        try:
            while True:
                data = source.recv(BUFFER_SIZE)
                if not data:
                    break
                destination.sendall(data)
        except:
            pass

    # Crear dos hilos para comunicación bidireccional
    thread1 = threading.Thread(target=forward, args=(client_socket, server_socket))
    thread2 = threading.Thread(target=forward, args=(server_socket, client_socket))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    server_socket.close()


def start_proxy():
    proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy.bind(("0.0.0.0", LISTEN_PORT))
    proxy.listen(100)

    print(f"Proxy escuchando en puerto {LISTEN_PORT}...")

    while True:
        client_socket, addr = proxy.accept()
        print(f"Cliente conectado: {addr}")

        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()


if __name__ == "__main__":
    start_proxy()
