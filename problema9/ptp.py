"""
p2p_node.py

Nodo peer-to-peer simple.
Cada nodo:
- Escucha conexiones entrantes
- Se conecta a otros nodos
- Envía y recibe mensajes JSON
- Sincroniza un contador compartido
"""

import socket
import threading
import json
import sys
import time

# ========= CONFIGURACIÓN =========

HOST = "localhost"
PORT = int(sys.argv[1])  # Puerto propio

MAX_COUNTER = 25

# Lista de peers conocidos (todos menos él mismo)
PEERS = [
    ("localhost", 5001),
    ("localhost", 5002),
    ("localhost", 5003),
    ("localhost", 5004),
]

# Remover el propio puerto
PEERS = [peer for peer in PEERS if peer[1] != PORT]

# Estado compartido
shared_state = {
    "counter": 0
}

# Lista de conexiones activas
connections = []
stop_event = threading.Event()

# ==================================


def handle_connection(conn, addr):
    """
    Maneja mensajes entrantes de otros nodos.
    """
    print(f"[{PORT}] Conectado con {addr}")

    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break

            message = json.loads(data.decode())

            # Procesar mensaje
            if message["type"] == "update":
                shared_state["counter"] = message["counter"]
                print(f"[{PORT}] Estado actualizado a {shared_state['counter']}")

        except:
            break

    conn.close()


def start_server():
    """
    Inicia el servidor para aceptar conexiones entrantes.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"[{PORT}] Nodo escuchando...")

    while True:
        conn, addr = server.accept()
        connections.append(conn)
        threading.Thread(target=handle_connection, args=(conn, addr), daemon=True).start()


def connect_to_peers():
    """
    Conecta este nodo a los otros nodos.
    """
    for peer in PEERS:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(peer)
            connections.append(s)
            threading.Thread(target=handle_connection, args=(s, peer), daemon=True).start()
            print(f"[{PORT}] Conectado a peer {peer}")
        except:
            pass


def broadcast_update():
    """
    Envía el estado actual a todos los peers conectados.
    """
    message = json.dumps({
        "type": "update",
        "counter": shared_state["counter"]
    }).encode()

    for conn in connections:
        try:
            conn.sendall(message)
        except:
            pass


def auto_increment():
    """
    Incrementa el contador cada 10 segundos
    y sincroniza con los peers.
    """
    while True:
        time.sleep(10)
        if shared_state["counter"] >= MAX_COUNTER:
            print(f"[{PORT}] ✅ Contador detenido en {shared_state['counter']}")
            stop_event.set()
            break

        shared_state["counter"] += 1
        print(f"[{PORT}] Incrementando contador a {shared_state['counter']}")

        broadcast_update()


# ========= MAIN =========

if __name__ == "__main__":
    # Iniciar servidor en hilo
    threading.Thread(target=start_server, daemon=True).start()

    # Esperar un poco antes de conectar
    time.sleep(2)

    # Conectarse a peers
    connect_to_peers()

    # Empezar incremento automático
    auto_increment()
