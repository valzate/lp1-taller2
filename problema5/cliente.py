import socket
import hashlib
from pathlib import Path

HOST = 'localhost'
PORT = 65432

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect((HOST, PORT))
filename = input("Ingrese el nombre del archivo a enviar: ")
if not Path(filename).is_file(): # Verificar si el archivo existe
    print("Archivo no encontrado.")
    cliente.close()
else:
    print(f"Enviando {filename} al servidor ...")
    size = Path(filename).stat().st_size
    checksum = hashlib.md5(Path(filename).read_bytes()).hexdigest()
    # Enviar el comando con el formato: "comando nombre_archivo tamaño checksum"
    with open(filename, "rb") as f:
        data = f.read(4026)   
    command = f"upload {filename} {size} {checksum}"
    cliente.sendall(command.encode())
    cliente.sendall(data)
    cliente.close()
