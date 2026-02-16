import socket
import threading
import json
from pathlib import Path

HOST = "localhost"
PORT = 9004
BUFFER_SIZE = 1024
ROOMS_FILE = Path("rooms.json")

clients = {}       # {username: socket}
rooms = {}         # {room_name: [username, username]}
lock = threading.Lock()

def load_rooms():#carga salas desde un archivo json
    global rooms
    if ROOMS_FILE.exists():
        with open(ROOMS_FILE, "r") as f:
            rooms = json.load(f)
    else:
        rooms = {"general": []}

def save_rooms(): #guarda salas en un archivo json
    with open(ROOMS_FILE, "w") as f:
        json.dump(rooms, f)
#FUNCIONES PARA MANEJAR CLIENTES Y SALAS
def broadcast_room(message, room):
    with lock:
        if room in rooms:
            for username in rooms[room]:
                if username in clients:
                    clients[username].send(message.encode())

def private_message(message, sender, recipient):
    with lock:
        if recipient in clients:
            clients[recipient].send(f"Private from {sender}: {message}".encode())

#MANEJO DE CLIENTE
def handle_client(conn, addr):
    print(f"Conectado con {addr}")
    
    conn.send("Bienvenido al chat! Ingresa tu nombre de usuario: ".encode())    
    username = conn.recv(BUFFER_SIZE).decode().strip()
    
    with lock:
        clients[username] = conn
    
    current_room = "general"
    with lock:
        rooms.setdefault(current_room, []).append(username)
    
    broadcast_room(f"{username} se ha unido a la sala {current_room}", current_room)
        
    while True:
        message = conn.recv(BUFFER_SIZE).decode().strip()
        
        if not message:
            break
        
        #PROCESANDO COMANDOS
        if message.startswith("/"):
            parts =message.split()
            command = parts[0]
            
            if command == "/create" and len(parts) > 1: #create
                name_room = parts[1]
                with lock:
                    if name_room not in rooms:
                        rooms[name_room] = []
                        save_rooms()
                        conn.send(f"Sala {name_room} creada\n.".encode())
                    else:
                        conn.send(f"Sala {name_room} ya existe.".encode())
                        
            elif command == "/join" and len(parts) > 1: #join
                name_room = parts[1]
                with lock:
                    if name_room in rooms:
                        rooms[current_room].remove(username)
                        current_room = name_room
                        rooms[name_room].append(username)
                        conn.send(f"Te has unido a la sala {name_room}.".encode())
                    else:
                        conn.send(f"Sala {name_room} no existe.".encode())
            
            elif command == "/leave": #leave
                with lock:
                    rooms[current_room].remove(username)
                    current_room = "general"
                    rooms[current_room].append(username)
                    conn.send("Has vuelto a la sala general.".encode())
            
            elif command == "/users": #list
                with lock:
                    users_in_room = ", ".join(rooms[current_room])
                    conn.send(f"Usuarios en {current_room}: {users_in_room}".encode())
            
            elif command == "/msg" and len(parts) > 2: #private message
                recipient = parts[1]
                private_message(" ".join(parts[2:]), username, recipient)                
            else:
                conn.send("Comando no reconocido.".encode())    
        else:
            #MENSAJE NORMAL
            broadcast_room(f"{username}: {message}", current_room)
    
    #DESCONEXION
    
    with lock:
        if username in clients:
            del clients[username]
        if username in rooms[current_room]:
            rooms[current_room].remove(username)
    
    conn.close()
    print(f"{username} se ha desconectado.")
#SERVIDOR PRINCIPAL
def main():
    load_rooms()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Servidor escuchando en {HOST}:{PORT}")
    
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()    
        broadcast_room(f"Nuevo usuario conectado: {addr}", "general")
             
if __name__ == "__main__":
    main()   