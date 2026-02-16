import socket
import os
import hashlib
from pathlib import Path


HOST = 'localhost'
PORT = 65432

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind((HOST, PORT))
servidor.listen()

print("Servidor a la espera de conexiones ...")
cliente, addr = servidor.accept()
print(f"Conexión realizada por {addr}")

data = cliente.recv(4026).decode()
# El comando se divide en partes: comando, nombre del archivo, tamaño y checksum
comando = data.split()
print(f"Comando recibido: {comando}")
filename = comando[1] # El nombre del archivo es la primera parte del comando
size = int(comando[2]) # El tamaño del archivo es la segunda parte del comando
checksum = comando[3] # El checksum es la tercera parte del comando

# Recibir el archivo en partes
with open(filename, "wb") as f:
    received = 0
    while received < size:
        chunk = cliente.recv(max(4026, size - received))
        if not chunk:
            break
        f.write(chunk)
        received += len(chunk)
cliente.close()        


